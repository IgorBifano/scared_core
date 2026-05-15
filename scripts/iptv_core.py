from __future__ import annotations

import json
import logging
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs, urlparse


LOGGER = logging.getLogger("iptv")

M3U_ATTRIBUTE_RE = re.compile(r'([\w-]+)="([^"]*)"')
SERIES_EPISODE_RE = re.compile(r"\bS\d{1,2}\s*E\d{1,3}\b", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
MEDIA_EXTENSIONS = (".mp4", ".mkv", ".avi", ".mov", ".m4v", ".wmv", ".m2ts")
PRIVATE_MARKERS = (
    "igorbifano",
    "bng6vizn",
    "username=",
    "password=",
    "token=",
    "auth=",
    "tyzic.xyz",
)

LIVE_SUFFIX_MAP = {
    "canais espn": "Canais ESPN",
    "espn": "Canais ESPN",
    "canais premiere clubes": "Canais Premiere Clubes",
    "premiere": "Canais Premiere Clubes",
    "sportv": "Canais Sportv",
    "canais sportv": "Canais Sportv",
    "canais abertos": "Canais Abertos",
    "abertos": "Canais Abertos",
    "canais noticias": "Canais Noticias",
    "noticias": "Canais Noticias",
    "canais infantis": "Canais Infantis",
    "infantis": "Canais Infantis",
    "canais documentarios": "Canais Documentarios",
    "documentarios": "Canais Documentarios",
    "canais 24h animes": "Canais 24h Animes",
    "canais 24h novelas": "Canais 24h Novelas",
    "variedades": "Canais Variedades",
}

SERIES_SUFFIX_MAP = {
    "animes": "Animes",
    "netflix": "Netflix",
    "drama": "Drama",
    "acao": "Ação",
    "ação": "Ação",
    "comedia": "Comedia",
    "comédia": "Comedia",
    "crime": "Crime",
    "documentarios": "Documentários",
    "documentários": "Documentários",
    "hbo max": "HBO Max",
    "amazon prime video": "Amazon Prime Video",
    "prime video": "Amazon Prime Video",
    "disney +": "Disney +",
    "disney+": "Disney +",
    "globoplay": "Globoplay",
    "novelas": "Novelas",
    "romance": "Romance",
    "suspense": "Suspense",
    "terror": "Terror",
}

MOVIE_SUFFIX_MAP = {
    "acao": "Ação",
    "ação": "Ação",
    "cinema": "Cinema",
    "lancamentos": "Lançamentos",
    "lançamentos": "Lançamentos",
    "comedia": "Comédia",
    "comédia": "Comédia",
    "drama": "Drama",
    "terror": "Terror",
    "suspense": "Suspense",
    "romance": "Romance",
    "animacao": "Animação",
    "animação": "Animação",
    "documentarios": "Documentários",
    "documentários": "Documentários",
    "ficcao": "Ficção",
    "ficção": "Ficção",
    "infantil": "Infantil",
}


@dataclass(slots=True)
class PlaylistEntry:
    name: str
    url: str
    attributes: dict[str, str] = field(default_factory=dict)
    directives: list[str] = field(default_factory=list)
    source: str = ""
    content_type: str = ""
    group_title: str = ""

    @property
    def tvg_id(self) -> str:
        return self.attributes.get("tvg-id", "")

    def canonical_name(self) -> str:
        return normalize_name(self.name)


def configure_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")


def ensure_directories(project_root: Path) -> None:
    for path in [
        project_root / "scripts",
        project_root / "config",
        project_root / "playlists" / "source",
        project_root / "output",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def normalized_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    normalized = normalized.lower()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def normalize_name(value: str) -> str:
    normalized = normalized_text(value)
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def squeeze_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def parse_attributes(raw_attributes: str) -> dict[str, str]:
    return {key: value for key, value in M3U_ATTRIBUTE_RE.findall(raw_attributes)}


def find_unquoted_comma(value: str) -> int:
    in_quotes = False
    for index, char in enumerate(value):
        if char == '"':
            in_quotes = not in_quotes
        elif char == "," and not in_quotes:
            return index
    return -1


def parse_extinf(line: str) -> tuple[dict[str, str], str]:
    payload = line.replace("#EXTINF:", "", 1).strip()
    comma_index = find_unquoted_comma(payload)
    if comma_index == -1:
        return {}, squeeze_spaces(payload)
    metadata = payload[:comma_index].strip()
    name = squeeze_spaces(payload[comma_index + 1 :])
    raw_attributes = metadata.split(" ", 1)[1] if " " in metadata else ""
    attributes = parse_attributes(raw_attributes)
    return attributes, name or attributes.get("tvg-name", "Unnamed")


def parse_m3u_text(content: str, source: str) -> list[PlaylistEntry]:
    entries: list[PlaylistEntry] = []
    pending_extinf: str | None = None
    directives: list[str] = []

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#EXTINF:"):
            pending_extinf = line
            directives = []
            continue
        if line.startswith("#"):
            if pending_extinf:
                directives.append(line)
            continue
        if not pending_extinf:
            continue
        attributes, name = parse_extinf(pending_extinf)
        entries.append(
            PlaylistEntry(
                name=name,
                url=line,
                attributes=attributes,
                directives=directives.copy(),
                source=source,
            )
        )
        pending_extinf = None
        directives = []
    return entries


def read_entries_from_file(path: Path) -> list[PlaylistEntry]:
    LOGGER.info("Reading %s", path)
    return parse_m3u_text(path.read_text(encoding="utf-8", errors="ignore"), str(path))


def source_playlists(project_root: Path) -> list[Path]:
    source_dir = project_root / "playlists" / "source"
    return sorted(path for path in source_dir.rglob("*.m3u") if path.is_file())


def migrate_legacy_sources(project_root: Path) -> Path | None:
    current_sources = source_playlists(project_root)
    if current_sources:
        return None

    candidates: list[Path] = []
    direct_candidates = [
        project_root / "plus.m3u",
        project_root / "index.m3u",
        project_root / "output" / "index.m3u",
    ]
    for candidate in direct_candidates:
        if candidate.exists():
            candidates.append(candidate)

    playlists_root = project_root / "playlists"
    if playlists_root.exists():
        for candidate in sorted(playlists_root.rglob("*.m3u")):
            if "source" not in candidate.parts:
                candidates.append(candidate)

    if not candidates:
        return None

    LOGGER.info("Migrating legacy playlists into playlists/source")
    migrated: list[PlaylistEntry] = []
    for candidate in candidates:
        for entry in read_entries_from_file(candidate):
            if is_private_entry(entry):
                continue
            prepared = prepare_entry(entry)
            if prepared is not None:
                migrated.append(prepared)

    migrated = deduplicate_entries(migrated)
    if not migrated:
        return None

    target = project_root / "playlists" / "source" / "public_catalog.m3u"
    target.write_text(serialize_playlist(migrated), encoding="utf-8")
    LOGGER.info("Created %s with %s public entries", target, len(migrated))
    return target


def is_private_entry(entry: PlaylistEntry) -> bool:
    url = normalized_text(entry.url)
    name = normalized_text(entry.name)
    group_title = normalized_text(entry.attributes.get("group-title", ""))
    if any(marker in url for marker in PRIVATE_MARKERS):
        return True
    if "igorbifano" in name or "igorbifano" in group_title:
        return True
    parsed = urlparse(entry.url)
    query = parse_qs(parsed.query)
    sensitive_keys = {"username", "password", "token", "auth"}
    return any(key.lower() in sensitive_keys for key in query)


def detect_content_type(entry: PlaylistEntry) -> str:
    group_title = normalized_text(entry.attributes.get("group-title", ""))
    haystack = normalized_text(" ".join([entry.name, entry.tvg_id, group_title, entry.url]))
    path = urlparse(entry.url).path.lower()

    if group_title.startswith("series |"):
        return "series"
    if group_title.startswith("filmes |"):
        return "movies"
    if group_title.startswith("tv ao vivo |"):
        if SERIES_EPISODE_RE.search(entry.name):
            return "series"
        if any(token in haystack for token in ["/movie/", "/movies/", "/filmes/"]):
            return "movies"
        return "live"

    if SERIES_EPISODE_RE.search(entry.name):
        return "series"
    if any(token in haystack for token in ["/series/", "temporada", "episodio", "episode", "netflix", "globoplay"]):
        return "series"
    if path.endswith(MEDIA_EXTENSIONS) or any(token in haystack for token in ["/movie/", "/movies/", "/vod/", "/filmes/", "filme", "cinema"]):
        return "movies"
    return "live"


def detect_live_group(entry: PlaylistEntry) -> str:
    existing = suffix_from_group(entry.attributes.get("group-title", ""), "TV AO VIVO")
    if existing:
        normalized_existing = normalized_text(existing)
        if normalized_existing in LIVE_SUFFIX_MAP:
            return LIVE_SUFFIX_MAP[normalized_existing]
        return cleanup_label(existing)

    haystack = normalized_text(" ".join([entry.name, entry.tvg_id, entry.url]))
    if "espn" in haystack:
        return "Canais ESPN"
    if "premiere" in haystack:
        return "Canais Premiere Clubes"
    if "sportv" in haystack or "sport tv" in haystack:
        return "Canais Sportv"
    if any(token in haystack for token in ["globo", "sbt", "record", "band", "redetv"]):
        return "Canais Abertos"
    if any(token in haystack for token in ["anime", "animex", "anime vision"]):
        return "Canais 24h Animes"
    if any(token in haystack for token in ["novela", "telenovela"]):
        return "Canais 24h Novelas"
    if any(token in haystack for token in ["cnn", "bbc news", "news", "globonews"]):
        return "Canais Noticias"
    if any(token in haystack for token in ["cartoon", "nick", "disney junior", "boomerang", "gloob"]):
        return "Canais Infantis"
    if any(token in haystack for token in ["discovery", "history", "animal planet", "nat geo", "document"]):
        return "Canais Documentarios"
    return "Canais Variedades"


def detect_series_group(entry: PlaylistEntry) -> str:
    existing = suffix_from_group(entry.attributes.get("group-title", ""), "SERIES")
    if existing:
        normalized_existing = normalized_text(existing)
        if normalized_existing in SERIES_SUFFIX_MAP:
            return SERIES_SUFFIX_MAP[normalized_existing]
        return cleanup_label(existing)

    haystack = normalized_text(" ".join([entry.name, entry.tvg_id, entry.url]))
    anime_titles = ["naruto", "one piece", "dragon ball", "pokemon", "bleach", "jujutsu", "demon slayer"]
    if any(title in haystack for title in anime_titles) or "anime" in haystack:
        return "Animes"
    if "netflix" in haystack:
        return "Netflix"
    if any(token in haystack for token in ["prime video", "amazon prime"]):
        return "Amazon Prime Video"
    if "globoplay" in haystack:
        return "Globoplay"
    if any(token in haystack for token in ["hbo", "hbo max", " max "]):
        return "HBO Max"
    if "disney" in haystack:
        return "Disney +"
    if any(token in haystack for token in ["crime", "policial"]):
        return "Crime"
    if any(token in haystack for token in ["comedia", "comedy", "sitcom"]):
        return "Comedia"
    if any(token in haystack for token in ["terror", "horror"]):
        return "Terror"
    if any(token in haystack for token in ["suspense", "thriller"]):
        return "Suspense"
    if "romance" in haystack:
        return "Romance"
    return "Drama"


def detect_movie_group(entry: PlaylistEntry) -> str:
    existing = suffix_from_group(entry.attributes.get("group-title", ""), "FILMES")
    if existing:
        normalized_existing = normalized_text(existing)
        if normalized_existing in MOVIE_SUFFIX_MAP:
            return MOVIE_SUFFIX_MAP[normalized_existing]
        return cleanup_label(existing)

    haystack = normalized_text(" ".join([entry.name, entry.tvg_id, entry.url]))
    year_match = YEAR_RE.search(entry.name)
    if year_match and int(year_match.group(1)) >= 2024:
        return "Lançamentos"
    if any(token in haystack for token in ["acao", "action", "aventura", "super hero"]):
        return "Ação"
    if any(token in haystack for token in ["comedia", "comedy"]):
        return "Comédia"
    if any(token in haystack for token in ["terror", "horror"]):
        return "Terror"
    if any(token in haystack for token in ["suspense", "thriller"]):
        return "Suspense"
    if any(token in haystack for token in ["animacao", "animation", "anime"]):
        return "Animação"
    if "romance" in haystack:
        return "Romance"
    if any(token in haystack for token in ["documentario", "documentary"]):
        return "Documentários"
    if any(token in haystack for token in ["ficcao", "sci-fi", "fantasia"]):
        return "Ficção"
    if any(token in haystack for token in ["infantil", "kids", "children"]):
        return "Infantil"
    return "Cinema"


def suffix_from_group(group_title: str, prefix: str) -> str:
    if not group_title:
        return ""
    expected = f"{prefix} | "
    if group_title.startswith(expected):
        return group_title[len(expected) :]
    return ""


def cleanup_label(label: str) -> str:
    label = squeeze_spaces(label.replace("•", " ").replace("|", " "))
    return " ".join(part.capitalize() if not part.isupper() else part for part in label.split())


def prepare_entry(entry: PlaylistEntry) -> PlaylistEntry | None:
    if not entry.name.strip() or not entry.url.strip():
        return None
    if is_private_entry(entry):
        return None

    content_type = detect_content_type(entry)
    if content_type == "live":
        suffix = detect_live_group(entry)
        group_title = f"TV AO VIVO | {suffix}"
    elif content_type == "series":
        suffix = detect_series_group(entry)
        group_title = f"SERIES | {suffix}"
    else:
        suffix = detect_movie_group(entry)
        group_title = f"FILMES | {suffix}"

    entry.name = squeeze_spaces(entry.attributes.get("tvg-name", entry.name))
    entry.content_type = content_type
    entry.group_title = group_title
    entry.attributes["group-title"] = group_title
    entry.attributes["tvg-name"] = entry.name
    entry.attributes["tvg-id"] = squeeze_spaces(entry.attributes.get("tvg-id", "")) or entry.canonical_name().replace(" ", ".")
    entry.attributes["tvg-logo"] = squeeze_spaces(entry.attributes.get("tvg-logo", ""))
    return entry


def deduplicate_entries(entries: Iterable[PlaylistEntry]) -> list[PlaylistEntry]:
    winners: dict[str, PlaylistEntry] = {}
    for entry in entries:
        key = f"{entry.content_type}|{entry.group_title}|{entry.tvg_id}|{normalized_text(entry.url)}"
        existing = winners.get(key)
        if existing is None or len(entry.name) < len(existing.name):
            winners[key] = entry
    return sorted(
        winners.values(),
        key=lambda item: (
            {"live": 0, "series": 1, "movies": 2}.get(item.content_type, 9),
            item.group_title,
            item.canonical_name(),
            item.url,
        ),
    )


def serialize_playlist(entries: Iterable[PlaylistEntry]) -> str:
    lines = ["#EXTM3U"]
    for entry in entries:
        attributes = " ".join(
            f'{key}="{value}"'
            for key, value in sorted(entry.attributes.items())
            if value is not None
        )
        lines.append(f"#EXTINF:-1 {attributes},{entry.name}".strip())
        lines.extend(entry.directives)
        lines.append(entry.url)
    return "\n".join(lines) + "\n"


def build_catalog(project_root: Path) -> list[PlaylistEntry]:
    entries: list[PlaylistEntry] = []
    for playlist in source_playlists(project_root):
        for entry in read_entries_from_file(playlist):
            prepared = prepare_entry(entry)
            if prepared is not None:
                entries.append(prepared)
    return deduplicate_entries(entries)


def validate_entries(entries: Iterable[PlaylistEntry]) -> dict[str, object]:
    entry_list = list(entries)
    category_counts = Counter(entry.group_title for entry in entry_list)
    empty_categories = [category for category, count in category_counts.items() if count == 0]
    misclassified: list[str] = []

    for entry in entry_list:
        if entry.content_type == "live" and not entry.group_title.startswith("TV AO VIVO | "):
            misclassified.append(f"LIVE prefix mismatch: {entry.name}")
        if entry.content_type == "series" and not entry.group_title.startswith("SERIES | "):
            misclassified.append(f"SERIES prefix mismatch: {entry.name}")
        if entry.content_type == "movies" and not entry.group_title.startswith("FILMES | "):
            misclassified.append(f"FILMES prefix mismatch: {entry.name}")
        if entry.content_type == "series" and entry.group_title.startswith("TV AO VIVO | "):
            misclassified.append(f"Series inside live: {entry.name}")
        if entry.content_type == "movies" and entry.group_title.startswith("SERIES | "):
            misclassified.append(f"Movie inside series: {entry.name}")

    return {
        "total_entries": len(entry_list),
        "categories": dict(sorted(category_counts.items())),
        "empty_categories": empty_categories,
        "misclassified": misclassified,
    }


def print_validation_report(report: dict[str, object]) -> None:
    LOGGER.info("Validation summary")
    LOGGER.info("Categories: %s", len(report["categories"]))
    for category, count in report["categories"].items():
        LOGGER.info("  %s -> %s", category, count)
    LOGGER.info("Empty categories: %s", len(report["empty_categories"]))
    LOGGER.info("Misclassified items: %s", len(report["misclassified"]))
    for item in report["misclassified"][:20]:
        LOGGER.warning("  %s", item)


def write_outputs(project_root: Path, entries: list[PlaylistEntry], report: dict[str, object]) -> None:
    ensure_directories(project_root)
    (project_root / "output" / "index.m3u").write_text(serialize_playlist(entries), encoding="utf-8")
    (project_root / "output" / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
