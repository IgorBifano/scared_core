from __future__ import annotations

import json
import logging
import re
import socket
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


LOGGER = logging.getLogger("iptv")

M3U_ATTRIBUTE_RE = re.compile(r'([\w-]+)="([^"]*)"')

ALLOWED_SCHEMES = {"http", "https", "rtmp", "rtsp", "rtp", "udp", "mms"}

CATEGORY_KEYWORDS = {
    "sports": ["sport", "sports", "premiere", "espn", "fox sports", "sportv", "combate", "ufc", "nba", "nfl"],
    "movies": ["movie", "movies", "filme", "filmes", "cinema", "telecine", "cine", "max", "paramount"],
    "series": ["series", "séries", "drama", "novela", "shows", "seriados"],
    "kids": ["kids", "children", "infantil", "cartoon", "disney", "nick", "boomerang", "junior"],
    "news": ["news", "noticias", "notícias", "jornal", "cnn", "bbc news", "record news", "globonews"],
    "vod": ["vod", "on demand", "filmes e series", "movie club"],
    "live": ["ao vivo", "live", "eventos", "event"]
}

LIVE_GROUP_TITLES = {
    "sports": "Sports",
    "news": "News",
    "kids": "Kids",
    "entertainment": "Entertainment",
    "documentary": "Documentary",
    "regional": "Regional",
}

MOVIE_GROUP_TITLES = {
    "action": "Action",
    "comedy": "Comedy",
    "drama": "Drama",
    "horror": "Horror",
    "thriller": "Thriller",
    "romance": "Romance",
    "documentary": "Documentary",
    "animation": "Anime",
    "family": "Family",
    "crime": "Crime",
    "scifi": "Sci-Fi",
    "general": "Movies",
}

SERIES_GROUP_TITLES = {
    "netflix": "Netflix",
    "hbo": "HBO",
    "anime": "Anime",
    "sitcom": "Sitcom",
    "drama": "Drama",
    "documentary": "Documentary",
    "crime": "Crime",
    "general": "Series",
}

LIVE_CATEGORY_KEYWORDS = {
    "sports": ["sport", "sports", "premiere", "espn", "fox sports", "sportv", "combate", "ufc", "nba", "nfl"],
    "news": ["news", "noticias", "notícias", "jornal", "cnn", "bbc news", "record news", "globonews", "band news"],
    "kids": ["kids", "children", "infantil", "cartoon", "disney channel", "disney junior", "nick", "nick jr", "boomerang", "gloob"],
    "documentary": ["documentario", "documentários", "documentaries", "discovery", "animal planet", "history", "nat geo", "investigation", "tlc"],
    "regional": ["regional", "regionais", "globo regionais", "tv local", "rede amazonica", "capital", "interior"],
    "entertainment": ["entertainment", "entretenimento", "variedades", "show", "canais", "globo", "sbt", "record", "band", "warner", "sony", "universal"],
}

MOVIE_GENRE_KEYWORDS = {
    "action": ["acao", "ação", "action", "aventura", "adventure", "super-heroi", "super hero"],
    "comedy": ["comedia", "comédia", "comedy", "humor", "sitcom"],
    "drama": ["drama"],
    "horror": ["terror", "horror", "slasher", "sobrenatural"],
    "thriller": ["thriller", "suspense", "misterio", "mistério"],
    "romance": ["romance", "romantica", "romântica"],
    "documentary": ["documentario", "documentário", "documentary", "doc"],
    "animation": ["animacao", "animação", "animation", "anime", "desenho"],
    "family": ["family", "familia", "família", "infantil", "kids"],
    "crime": ["crime", "policial", "investigacao", "investigação"],
    "scifi": ["ficcao", "ficção", "scifi", "sci-fi", "fantasia", "fantasy"],
    "general": [],
}

SERIES_GENRE_KEYWORDS = {
    "netflix": ["netflix"],
    "hbo": ["hbo", "max"],
    "anime": ["anime", "animacao", "animação"],
    "sitcom": ["sitcom", "comedia", "comédia", "comedy"],
    "drama": ["drama", "novela", "seriado", "globoplay"],
    "documentary": ["documentario", "documentário", "docuseries", "documentary"],
    "crime": ["crime", "policial", "investigacao", "investigação"],
    "general": [],
}

COUNTRY_KEYWORDS = {
    "br": [
        "brasil",
        "brazil",
        "sportv",
        "premiere",
        "globo",
        "sbt",
        "record",
        "band",
        "telecine",
        "multishow",
        "gnt",
        "megapix",
        "canal brasil",
        "espn br",
        "fox sports br",
    ],
    "us": [
        "usa",
        "united states",
        "fox usa",
        "abc",
        "nbc",
        "cbs",
        "pbs",
        "cw",
        "msnbc",
        "bloomberg",
        "weather channel",
    ],
    "uk": ["uk", "united kingdom", "bbc", "itv", "sky news", "channel 4", "british"],
    "es": ["spain", "españa", "espana", "antena 3", "telecinco", "movistar plus", "la 1"],
    "pt": ["portugal", "sic", "tvi", "rtp", "benfica tv", "sport tv portugal"],
    "jp": ["japan", "nhk", "tokyo mx", "fuji tv", "tv tokyo"],
    "kr": ["korea", "south korea", "kbs", "mbc", "sbs", "arirang"],
    "fr": ["france", "francais", "français", "tf1", "france 2", "bfm"],
    "de": ["germany", "deutsch", "zdf", "ard", "rtl deutschland", "prosieben"],
    "latam": ["latam", "latin", "latino", "latina", "américa latina", "america latina"],
}

CHANNEL_KEYWORDS = {
    "espn": ["espn"],
    "sportv": ["sportv"],
    "disney": ["disney", "disney junior", "disney xd"],
    "telecine": ["telecine"],
    "hbo": ["hbo", "hbo2", "hbo plus", "hbo family", "hbo xtreme"],
    "premiere": ["premiere"],
    "discovery": ["discovery", "tlc", "animal planet", "investigation discovery", "id "],
    "cartoon": ["cartoon", "tooncast", "boomerang"],
    "fox": ["fox", "fx", "fxx"],
    "cnn": ["cnn"],
    "globo": ["globo"],
    "nick": ["nick", "nickelodeon", "nick jr"],
    "warner": ["warner", "warner channel", "space", "tnt"],
}

CHANNEL_OUTPUT_NAMES = {
    "espn": ["espn"],
    "sportv": ["sportv"],
    "disney": ["disney", "disney_channel"],
    "telecine": ["telecine"],
    "hbo": ["hbo"],
    "premiere": ["premiere"],
    "discovery": ["discovery"],
    "cartoon": ["cartoon"],
    "fox": ["fox"],
    "cnn": ["cnn"],
    "globo": ["globo"],
    "nick": ["nick"],
    "warner": ["warner"],
}

MEDIA_FILE_EXTENSIONS = (".mp4", ".mkv", ".avi", ".mov", ".m4v", ".ts", ".m2ts", ".wmv")
SERIES_EPISODE_RE = re.compile(r"\bs\d{1,2}(?:\s*e\d{1,3})?\b", re.IGNORECASE)
PUBLIC_BASE_URL = "https://igorbifano.github.io/scared_core/output"
PLAYLIST_BRAND = "Family Media"

QUALITY_TOKENS = [
    "fhd",
    "uhd",
    "fullhd",
    "hd",
    "sd",
    "4k",
    "1080p",
    "720p",
    "480p",
    "cam",
]


@dataclass(slots=True)
class PlaylistEntry:
    name: str
    url: str
    attributes: dict[str, str] = field(default_factory=dict)
    directives: list[str] = field(default_factory=list)
    source: str = ""
    source_priority: int = 0
    country: str = "others"
    category: str = "general"
    content_type: str = "live"
    live_category: str = "entertainment"
    vod_genre: str = "general"
    series_genre: str = "general"
    channel_group: str | None = None

    @property
    def tvg_id(self) -> str:
        return self.attributes.get("tvg-id", "")

    @property
    def group_title(self) -> str:
        return self.attributes.get("group-title", "")

    def canonical_name(self) -> str:
        return normalize_channel_name(self.name)

    def quality_score(self) -> int:
        haystack = normalized_text(" ".join([self.name, self.attributes.get("tvg-name", "")]))
        for index, token in enumerate(QUALITY_TOKENS):
            if token in haystack:
                return len(QUALITY_TOKENS) - index
        return 0


def configure_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")


def normalized_text(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value or "")
    ascii_value = "".join(char for char in ascii_value if not unicodedata.combining(char))
    ascii_value = ascii_value.lower()
    ascii_value = re.sub(r"\s+", " ", ascii_value)
    return ascii_value.strip()


def normalize_channel_name(value: str) -> str:
    normalized = normalized_text(value)
    normalized = normalized.replace("|", " ")
    normalized = re.sub(r"[¹²³⁴⁵⁶⁷⁸⁹⁰]", "", normalized)
    normalized = re.sub(r"\b(sp|rj|mg|df|fhd|uhd|hd|sd)\b", " ", normalized)
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def parse_attributes(raw_attributes: str) -> dict[str, str]:
    return {key: value for key, value in M3U_ATTRIBUTE_RE.findall(raw_attributes)}


def parse_m3u_text(content: str, source: str, source_priority: int) -> list[PlaylistEntry]:
    entries: list[PlaylistEntry] = []
    extinf_line: str | None = None
    directives: list[str] = []

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("#EXTINF:"):
            extinf_line = line
            directives = []
            continue

        if line.startswith("#"):
            if extinf_line:
                directives.append(line)
            continue

        if not extinf_line:
            continue

        parsed = parse_extinf(extinf_line)
        entry = PlaylistEntry(
            name=parsed["name"],
            url=line,
            attributes=parsed["attributes"],
            directives=directives.copy(),
            source=source,
            source_priority=source_priority,
        )
        entries.append(entry)
        extinf_line = None
        directives = []

    return entries


def parse_extinf(line: str) -> dict[str, object]:
    raw_body = line.replace("#EXTINF:", "", 1).strip()
    comma_index = find_unquoted_comma(raw_body)
    if comma_index == -1:
        return {"name": line.replace("#EXTINF:", "").strip(), "attributes": {}}

    metadata = raw_body[:comma_index].strip()
    name = raw_body[comma_index + 1 :].strip()

    if " " in metadata:
        _, raw_attributes = metadata.split(" ", 1)
    else:
        raw_attributes = ""

    attributes = parse_attributes(raw_attributes)
    name = name or attributes.get("tvg-name", "Unnamed Channel")
    return {"name": name, "attributes": attributes}


def find_unquoted_comma(value: str) -> int:
    in_quotes = False
    for index, char in enumerate(value):
        if char == '"':
            in_quotes = not in_quotes
            continue
        if char == "," and not in_quotes:
            return index
    return -1


def collect_local_playlists(project_root: Path) -> list[Path]:
    playlists_dir = project_root / "playlists"
    return sorted(path for path in playlists_dir.rglob("*.m3u") if path.is_file())


def resolve_plus_playlist(project_root: Path) -> Path | None:
    candidates = [project_root / "plus.m3u", project_root.parent / "plus.m3u"]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def load_remote_sources(config_path: Path) -> list[str]:
    if not config_path.exists():
        return []

    sources: list[str] = []
    for line in config_path.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        sources.append(value)
    return sources


def read_entries_from_file(path: Path, source_priority: int) -> list[PlaylistEntry]:
    LOGGER.info("Loading playlist: %s", path)
    content = path.read_text(encoding="utf-8", errors="ignore")
    return parse_m3u_text(content, source=str(path), source_priority=source_priority)


def read_entries_from_url(url: str, source_priority: int, timeout: float = 10.0) -> list[PlaylistEntry]:
    LOGGER.info("Downloading source: %s", url)
    request = Request(url, headers={"User-Agent": "iptv-system/1.0"})
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        content = response.read().decode(charset, errors="ignore")
    return parse_m3u_text(content, source=url, source_priority=source_priority)


def is_valid_stream_url(url: str) -> bool:
    parsed = urlparse(url.strip())
    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        return False
    if parsed.scheme.lower() in {"http", "https", "rtmp", "rtsp"} and not parsed.netloc:
        return False
    return True


def choose_better_entry(current: PlaylistEntry, candidate: PlaylistEntry) -> PlaylistEntry:
    current_score = score_entry(current)
    candidate_score = score_entry(candidate)
    if candidate_score > current_score:
        return candidate
    return current


def score_entry(entry: PlaylistEntry) -> tuple[int, int, int, int]:
    return (
        entry.source_priority,
        1 if entry.tvg_id else 0,
        1 if entry.group_title else 0,
        entry.quality_score(),
    )


def deduplicate_entries(entries: Iterable[PlaylistEntry]) -> tuple[list[PlaylistEntry], dict[str, int]]:
    winners_by_semantic: dict[str, PlaylistEntry] = {}
    semantic_key_by_url: dict[str, str] = {}
    duplicates_removed = 0
    invalid_removed = 0
    empty_removed = 0

    for entry in entries:
        if not entry.name.strip() or not entry.url.strip():
            empty_removed += 1
            continue
        if not is_valid_stream_url(entry.url):
            invalid_removed += 1
            continue

        url_key = normalized_url(entry.url)
        semantic_key = build_semantic_key(entry)

        if url_key in semantic_key_by_url:
            previous_semantic_key = semantic_key_by_url[url_key]
            winners_by_semantic[previous_semantic_key] = choose_better_entry(
                winners_by_semantic[previous_semantic_key], entry
            )
            duplicates_removed += 1
            continue

        if semantic_key in winners_by_semantic:
            winners_by_semantic[semantic_key] = choose_better_entry(winners_by_semantic[semantic_key], entry)
            duplicates_removed += 1
            continue

        semantic_key_by_url[url_key] = semantic_key
        winners_by_semantic[semantic_key] = entry

    deduped = list(winners_by_semantic.values())
    deduped.sort(key=lambda item: (item.country, item.category, item.canonical_name(), item.name, item.url))
    return deduped, {
        "duplicates_removed": duplicates_removed,
        "invalid_removed": invalid_removed,
        "empty_removed": empty_removed,
    }


def normalized_url(url: str) -> str:
    parsed = urlparse(url.strip())
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")
    query = f"?{parsed.query}" if parsed.query else ""
    return f"{scheme}://{netloc}{path}{query}"


def build_semantic_key(entry: PlaylistEntry) -> str:
    tvg_id = normalized_text(entry.tvg_id)
    if tvg_id:
        return f"id::{tvg_id}"
    group_title = normalized_text(entry.group_title)
    return f"name::{entry.canonical_name()}::{group_title}"


def enrich_entries(entries: Iterable[PlaylistEntry]) -> list[PlaylistEntry]:
    enriched: list[PlaylistEntry] = []
    for entry in entries:
        entry.content_type = detect_content_type(entry)
        entry.country = detect_country(entry)
        entry.category = detect_category(entry)
        entry.live_category = detect_live_category(entry) if entry.content_type == "live" else ""
        entry.vod_genre = detect_movie_genre(entry) if entry.content_type == "movies" else ""
        entry.series_genre = detect_series_genre(entry) if entry.content_type == "series" else ""
        entry.channel_group = detect_channel_group(entry)
        standardize_entry(entry)
        enriched.append(entry)
    return enriched


def detect_content_type(entry: PlaylistEntry) -> str:
    if is_probable_series(entry):
        return "series"
    if is_probable_movie(entry):
        return "movies"
    if is_probable_vod(entry):
        group_haystack = normalized_text(entry.group_title)
        if "series" in group_haystack or "temporada" in normalized_text(entry.name):
            return "series"
        return "movies"
    return "live"


def detect_country(entry: PlaylistEntry) -> str:
    haystack = normalized_text(" ".join([entry.name, entry.group_title, entry.tvg_id]))
    for country_code, keywords in COUNTRY_KEYWORDS.items():
        if any(keyword in haystack for keyword in keywords):
            return country_code

    tvg_id_lower = normalized_text(entry.tvg_id)
    for suffix in (".br", ".us", ".uk", ".es", ".pt", ".jp", ".kr", ".fr", ".de"):
        if suffix in tvg_id_lower:
            return suffix.replace(".", "")

    if any(token in haystack for token in ["mexico", "argentina", "colombia", "chile", "peru", "uruguay", "venezuela"]):
        return "latam"

    return "others"


def detect_category(entry: PlaylistEntry) -> str:
    if entry.content_type == "series":
        return "series"
    if entry.content_type == "movies":
        return "movies"

    haystack = normalized_text(" ".join([entry.name, entry.group_title]))
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in haystack for keyword in keywords):
            return category
    return "live"


def detect_channel_group(entry: PlaylistEntry) -> str | None:
    if entry.content_type != "live":
        return None

    haystack = normalized_text(" ".join([entry.name, entry.group_title, entry.tvg_id]))
    for channel_group, keywords in CHANNEL_KEYWORDS.items():
        if any(keyword in haystack for keyword in keywords):
            return channel_group
    return None


def standardize_entry(entry: PlaylistEntry) -> None:
    canonical_name = entry.canonical_name()
    display_name = entry.name.strip() or entry.attributes.get("tvg-name", "Unnamed Channel")
    group_title = canonical_group_title(entry)

    entry.name = squeeze_spaces(display_name)
    entry.attributes["tvg-name"] = entry.name
    entry.attributes["group-title"] = group_title
    if not entry.attributes.get("tvg-id"):
        entry.attributes["tvg-id"] = canonical_name.replace(" ", ".") if canonical_name else ""
    if not entry.attributes.get("tvg-logo"):
        entry.attributes["tvg-logo"] = ""


def squeeze_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def canonical_group_title(entry: PlaylistEntry) -> str:
    if entry.content_type == "live":
        return LIVE_GROUP_TITLES.get(entry.live_category, "Entertainment")
    if entry.content_type == "movies":
        return MOVIE_GROUP_TITLES.get(entry.vod_genre, "Movies")
    return SERIES_GROUP_TITLES.get(entry.series_genre, "Series")


def looks_like_linear_channel(entry: PlaylistEntry) -> bool:
    haystack = normalized_text(" ".join([entry.name, entry.group_title, entry.tvg_id, entry.url]))
    parsed_path = urlparse(entry.url).path.lower()
    if parsed_path.endswith(".m3u8") or parsed_path.endswith(".mpd"):
        return True
    live_tokens = [
        " tv",
        "channel",
        "canal",
        "pluto tv",
        "ao vivo",
        "live",
        "24h",
        "24/7",
        "/live/",
    ]
    return any(token in haystack for token in live_tokens)


def is_probable_vod(entry: PlaylistEntry) -> bool:
    haystack = normalized_text(" ".join([entry.name, entry.group_title, entry.url]))
    if any(token in haystack for token in ["telecine zone", "series •", "filmes •", "movie club", "on demand", "/series/", "/movie/", "/vod/", "/filmes/"]):
        return True
    parsed_path = urlparse(entry.url).path.lower()
    return parsed_path.endswith(MEDIA_FILE_EXTENSIONS)


def is_probable_series(entry: PlaylistEntry) -> bool:
    haystack = " ".join([entry.name, entry.group_title, entry.url])
    normalized = normalized_text(haystack)
    return bool(SERIES_EPISODE_RE.search(haystack)) or any(
        token in normalized for token in [" season ", " episode ", " episodio ", " episódio ", "temporada", "series •", "series |", "/series/"]
    )


def is_probable_movie(entry: PlaylistEntry) -> bool:
    haystack = normalized_text(" ".join([entry.name, entry.group_title, entry.url]))
    parsed_path = urlparse(entry.url).path.lower()
    if parsed_path.endswith(MEDIA_FILE_EXTENSIONS) or any(
        token in parsed_path for token in ["/movie/", "/movies/", "/vod/", "/filmes/"]
    ):
        return True
    if looks_like_linear_channel(entry):
        return False
    vod_tokens = ["filme", "filmes", "cinema", "bluray", "web-dl", "1080p", "2160p", "4k", "movie club"]
    return any(token in haystack for token in vod_tokens)


def detect_live_category(entry: PlaylistEntry) -> str:
    haystack = normalized_text(" ".join([entry.name, entry.group_title, entry.tvg_id]))
    for category, keywords in LIVE_CATEGORY_KEYWORDS.items():
        if any(keyword in haystack for keyword in keywords):
            return category
    return "entertainment"


def detect_movie_genre(entry: PlaylistEntry) -> str:
    haystack = normalized_text(" ".join([entry.name, entry.group_title, entry.url]))
    for genre, keywords in MOVIE_GENRE_KEYWORDS.items():
        if keywords and any(keyword in haystack for keyword in keywords):
            return genre
    return "general"


def detect_series_genre(entry: PlaylistEntry) -> str:
    haystack = normalized_text(" ".join([entry.name, entry.group_title, entry.url]))
    for genre, keywords in SERIES_GENRE_KEYWORDS.items():
        if keywords and any(keyword in haystack for keyword in keywords):
            return genre
    return "general"


def check_stream_availability(entries: list[PlaylistEntry], timeout: float, limit: int | None = None) -> tuple[list[PlaylistEntry], int]:
    checked_entries = entries if limit is None else entries[:limit]
    available: list[PlaylistEntry] = []
    removed = 0

    for index, entry in enumerate(entries):
        if index >= len(checked_entries):
            available.append(entry)
            continue

        if stream_is_available(entry.url, timeout):
            available.append(entry)
        else:
            removed += 1

    return available, removed


def stream_is_available(url: str, timeout: float) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme in {"http", "https"}:
            request = Request(url, method="HEAD", headers={"User-Agent": "iptv-system/1.0"})
            with urlopen(request, timeout=timeout) as response:
                return 200 <= response.status < 400

        if parsed.scheme in {"rtmp", "rtsp", "rtp", "udp", "mms"}:
            host = parsed.hostname
            port = parsed.port or default_port(parsed.scheme)
            if not host or not port:
                return False
            with socket.create_connection((host, port), timeout=timeout):
                return True
    except (OSError, URLError, ValueError):
        return False
    return False


def default_port(scheme: str) -> int:
    return {
        "http": 80,
        "https": 443,
        "rtmp": 1935,
        "rtsp": 554,
        "rtp": 5004,
        "udp": 1234,
        "mms": 1755,
    }.get(scheme, 80)


def serialize_playlist(entries: Iterable[PlaylistEntry], playlist_name: str = PLAYLIST_BRAND) -> str:
    lines = [f'#EXTM3U name="{playlist_name}"']
    for entry in entries:
        attributes = " ".join(
            f'{key}="{value}"'
            for key, value in sorted(entry.attributes.items())
            if value is not None
        ).strip()
        prefix = f"#EXTINF:-1 {attributes},{entry.name}" if attributes else f"#EXTINF:-1,{entry.name}"
        lines.append(prefix)
        lines.extend(entry.directives)
        lines.append(entry.url)
    return "\n".join(lines) + "\n"


def group_entries(entries: Iterable[PlaylistEntry], group_by: str) -> dict[str, list[PlaylistEntry]]:
    grouped: dict[str, list[PlaylistEntry]] = {}
    for entry in entries:
        if group_by == "country":
            key = entry.country
        elif group_by == "category":
            key = entry.category
        elif group_by == "channel":
            key = entry.channel_group or "others"
        else:
            raise ValueError(f"Unsupported grouping: {group_by}")
        grouped.setdefault(key, []).append(entry)

    for values in grouped.values():
        values.sort(key=lambda item: (item.canonical_name(), item.name, item.url))
    return grouped


def ensure_directories(project_root: Path) -> None:
    paths = [
        project_root / "playlists",
        project_root / "playlists" / "local",
        project_root / "countries",
        project_root / "categories",
        project_root / "channels",
        project_root / "sports",
        project_root / "movies",
        project_root / "series",
        project_root / "kids",
        project_root / "news",
        project_root / "live",
        project_root / "vod",
        project_root / "logos",
        project_root / "config",
        project_root / "scripts",
        project_root / "output",
        project_root / "output" / "countries",
        project_root / "output" / "categories",
        project_root / "output" / "channels",
        project_root / "output" / "live",
        project_root / "output" / "movies",
        project_root / "output" / "series",
        project_root / "backup",
    ]
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def write_outputs(
    project_root: Path,
    entries: list[PlaylistEntry],
    stats: dict[str, int],
    sources: dict[str, int],
    base_url: str = PUBLIC_BASE_URL,
) -> None:
    ensure_directories(project_root)

    live_entries = [entry for entry in entries if entry.content_type == "live"]
    movie_entries = [entry for entry in entries if entry.content_type == "movies"]
    series_entries = [entry for entry in entries if entry.content_type == "series"]

    (project_root / "output" / "all_channels.m3u").write_text(
        serialize_playlist(live_entries, f"{PLAYLIST_BRAND} Live"),
        encoding="utf-8",
    )

    countries = group_entries(live_entries, "country")
    for code in ["br", "us", "uk", "es", "pt", "jp", "kr", "fr", "de", "latam", "others"]:
        country_entries = countries.get(code, [])
        save_playlist(project_root / "countries" / code / "playlist.m3u", country_entries)
        save_playlist(project_root / "output" / "countries" / f"{code}.m3u", country_entries)

    categories = group_entries(entries, "category")
    for slug, destination in [
        ("sports", project_root / "sports" / "playlist.m3u"),
        ("movies", project_root / "movies" / "playlist.m3u"),
        ("series", project_root / "series" / "playlist.m3u"),
        ("kids", project_root / "kids" / "playlist.m3u"),
        ("news", project_root / "news" / "playlist.m3u"),
        ("live", project_root / "live" / "playlist.m3u"),
        ("vod", project_root / "vod" / "playlist.m3u"),
    ]:
        category_entries = categories.get(slug, [])
        save_playlist(destination, category_entries)
        save_playlist(project_root / "output" / "categories" / f"{slug}.m3u", category_entries)
        save_playlist(project_root / "categories" / f"{slug}.m3u", category_entries)

    channels = group_entries([entry for entry in live_entries if entry.channel_group], "channel")
    for slug in sorted(CHANNEL_KEYWORDS):
        channel_entries = channels.get(slug, [])
        save_playlist(project_root / "channels" / slug / "playlist.m3u", channel_entries)
        save_playlist(project_root / "output" / "channels" / f"{slug}.m3u", channel_entries)
        for alias in CHANNEL_OUTPUT_NAMES.get(slug, []):
            save_playlist(project_root / "output" / "channels" / f"{alias}.m3u", channel_entries)

    live_groups = group_entries_by_attr(live_entries, "live_category")
    for slug in ["sports", "news", "kids", "entertainment", "documentary", "regional"]:
        save_playlist(project_root / "output" / "live" / f"{slug}.m3u", live_groups.get(slug, []))
    save_playlist(project_root / "output" / "live" / "documentaries.m3u", live_groups.get("documentary", []))
    save_playlist(project_root / "output" / "live" / "all.m3u", live_entries)

    movie_groups = group_entries_by_attr(movie_entries, "vod_genre")
    for slug in sorted(MOVIE_GENRE_KEYWORDS):
        save_playlist(project_root / "output" / "movies" / f"{slug}.m3u", movie_groups.get(slug, []))
    save_playlist(project_root / "output" / "movies" / "all.m3u", movie_entries)

    series_groups = group_entries_by_attr(series_entries, "series_genre")
    for slug in sorted(SERIES_GENRE_KEYWORDS):
        save_playlist(project_root / "output" / "series" / f"{slug}.m3u", series_groups.get(slug, []))
    save_playlist(project_root / "output" / "series" / "all.m3u", series_entries)

    (project_root / "output" / "live" / "index.m3u").write_text(
        serialize_playlist(live_entries, f"{PLAYLIST_BRAND} Live"),
        encoding="utf-8",
    )
    (project_root / "output" / "movies" / "index.m3u").write_text(
        serialize_playlist(movie_entries, f"{PLAYLIST_BRAND} Movies"),
        encoding="utf-8",
    )
    (project_root / "output" / "series" / "index.m3u").write_text(
        serialize_playlist(series_entries, f"{PLAYLIST_BRAND} Series"),
        encoding="utf-8",
    )

    catalog_entries = sorted(
        entries,
        key=lambda item: (
            {"live": 0, "movies": 1, "series": 2}.get(item.content_type, 9),
            item.attributes.get("group-title", ""),
            item.canonical_name(),
            item.name,
            item.url,
        ),
    )
    full_catalog = serialize_playlist(catalog_entries, PLAYLIST_BRAND)
    (project_root / "index.m3u").write_text(full_catalog, encoding="utf-8")
    (project_root / "output" / "index.m3u").write_text(full_catalog, encoding="utf-8")

    report = {
        "total_entries": len(entries),
        "content_types": {
            "live": len(live_entries),
            "movies": len(movie_entries),
            "series": len(series_entries),
        },
        "published_outputs": {
            "index_entries": len(catalog_entries),
            "all_channels_entries": len(live_entries),
            "countries_entries": sum(len(value) for value in countries.values()),
            "channels_entries": sum(len(value) for value in channels.values()),
        },
        "countries": {key: len(value) for key, value in countries.items()},
        "categories": {key: len(value) for key, value in categories.items()},
        "channels": {key: len(value) for key, value in channels.items()},
        "live_categories": {key: len(value) for key, value in live_groups.items()},
        "movie_genres": {key: len(value) for key, value in movie_groups.items()},
        "series_genres": {key: len(value) for key, value in series_groups.items()},
        "sources": sources,
        "cleanup": stats,
        "base_url": base_url,
        "parser_notes": {
            "old_main_playlist_problem": "The previous index.m3u files pointed to other playlist files instead of containing playable stream URLs, which modern IPTV apps do not use as navigable folders.",
            "old_mixing_reason": "The previous parser relied too much on raw group-title and loose movie keywords, which allowed linear channels to fall into VOD buckets and episodic content to leak into live/channel playlists.",
            "current_strategy": "The current parser resolves content_type first (live, movies, series), rewrites group-title into IPTV-friendly buckets, and generates main indexes with direct streams instead of nested playlist references.",
        },
    }
    (project_root / "output" / "report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def save_playlist(path: Path, entries: list[PlaylistEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(serialize_playlist(entries, PLAYLIST_BRAND), encoding="utf-8")


def group_entries_by_attr(entries: Iterable[PlaylistEntry], attr_name: str) -> dict[str, list[PlaylistEntry]]:
    grouped: dict[str, list[PlaylistEntry]] = {}
    for entry in entries:
        key = getattr(entry, attr_name, "") or "general"
        grouped.setdefault(key, []).append(entry)
    for values in grouped.values():
        values.sort(key=lambda item: (item.canonical_name(), item.name, item.url))
    return grouped
