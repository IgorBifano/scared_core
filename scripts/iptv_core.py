from __future__ import annotations

import logging
import re
import shutil
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


LOGGER = logging.getLogger("iptv")

M3U_ATTRIBUTE_RE = re.compile(r'([\w-]+)="([^"]*)"')
SERIES_EPISODE_RE = re.compile(r"\bS\d{1,2}\s*E\d{1,3}\b", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
MEDIA_EXTENSIONS = (".mp4", ".mkv", ".avi", ".mov", ".m4v", ".wmv", ".m2ts")
LIVE_STREAM_EXTENSIONS = (".m3u8", ".ts", ".mpd")

LIVE_CATEGORIES = [
    "TV AO VIVO | Todos",
    "TV AO VIVO | Canais Abertos",
    "TV AO VIVO | Canais Internacionais",
    "TV AO VIVO | Canais Documentarios",
    "TV AO VIVO | Canais Filmes e Series",
    "TV AO VIVO | Canais HBO",
    "TV AO VIVO | Canais Telecine",
    "TV AO VIVO | Canais Infantis",
    "TV AO VIVO | Canais Noticias",
    "TV AO VIVO | Canais Variedades",
    "TV AO VIVO | Canais Religiosos",
    "TV AO VIVO | Canais Premiere Clubes",
    "TV AO VIVO | Canais Sportv",
    "TV AO VIVO | Canais ESPN",
    "TV AO VIVO | Canais Amazon Prime",
    "TV AO VIVO | Canais Disney",
    "TV AO VIVO | Canais Paramount",
    "TV AO VIVO | Canais HBO MAX",
    "TV AO VIVO | Canais TNT",
    "TV AO VIVO | Canais Combate/UFC Fight",
    "TV AO VIVO | Canais Nba League Pass",
    "TV AO VIVO | Canais Apple TV",
    "TV AO VIVO | Canais Cazé TV",
    "TV AO VIVO | Canais DAZN",
    "TV AO VIVO | Canais GE TV",
    "TV AO VIVO | Canais GOAT",
    "TV AO VIVO | Canais Nosso Futebol",
    "TV AO VIVO | Canais NSPORTS",
    "TV AO VIVO | Canais XSPORTS",
    "TV AO VIVO | Canais 24h Animes",
    "TV AO VIVO | Canais 24h Discovery",
    "TV AO VIVO | Canais 24h Novelas",
    "TV AO VIVO | Canais 24h Infantis",
    "TV AO VIVO | Canais 24h Series de TV",
    "TV AO VIVO | Canais Adultos",
]

SERIES_CATEGORIES = [
    "SERIES | Todos",
    "SERIES | ABC",
    "SERIES | AMC+",
    "SERIES | Apple TV",
    "SERIES | BBC ONE",
    "SERIES | Brasil Paralelo",
    "SERIES | CW",
    "SERIES | Discovery +",
    "SERIES | Disney +",
    "SERIES | GloboPlay",
    "SERIES | HBO Max",
    "SERIES | Hulu",
    "SERIES | Lionsgate +",
    "SERIES | Looke",
    "SERIES | Netflix",
    "SERIES | Paramount +",
    "SERIES | PlayPlus",
    "SERIES | Amazon Prime Video",
    "SERIES | Starz",
    "SERIES | Via Play",
    "SERIES | Ação",
    "SERIES | Animação/Infantil",
    "SERIES | Animes",
    "SERIES | Aventura",
    "SERIES | Chicago Universe",
    "SERIES | Comedia",
    "SERIES | Crime",
    "SERIES | Documentários",
    "SERIES | Dorama",
    "SERIES | Drama",
    "SERIES | Ficção e Fantasia",
    "SERIES | Faroeste",
    "SERIES | Guerra",
    "SERIES | Marvel",
    "SERIES | Mini Séries",
    "SERIES | Nacional",
    "SERIES | Novelas",
    "SERIES | Reality Shows",
    "SERIES | Romance",
    "SERIES | Suspense",
    "SERIES | Terror",
    "SERIES | Turcas",
    "SERIES | Tv Show",
]

MOVIE_CATEGORIES = [
    "FILMES | Todos",
    "FILMES | Cinema",
    "FILMES | Lançamentos",
    "FILMES | 4K",
    "FILMES | Ação",
    "FILMES | Animação",
    "FILMES | Animes Filmes",
    "FILMES | Aventura",
    "FILMES | Clássicos",
    "FILMES | Coletânea 007",
    "FILMES | Coletânea Batman",
    "FILMES | Coletânea Bourne",
    "FILMES | Coletânea Jornada nas Estrelas",
    "FILMES | Coletânea Os Trapalhões",
    "FILMES | Coletânea Resident Evil",
    "FILMES | Coletânea Rocky",
    "FILMES | Coletânea Star Wars",
    "FILMES | Comédia Stand-up",
    "FILMES | Comédia",
    "FILMES | Comédia Romântica",
    "FILMES | Crime",
    "FILMES | Drama",
    "FILMES | Documentários Filmes",
    "FILMES | Faroeste",
    "FILMES | Ficção",
    "FILMES | Guerra",
    "FILMES | Infantil",
    "FILMES | Karaoke",
    "FILMES | Legendados",
    "FILMES | Musical",
    "FILMES | Nacional",
    "FILMES | Religiosos",
    "FILMES | Romance",
    "FILMES | Suspense",
    "FILMES | Terror",
    "FILMES | Especiais de Natal",
]

ALLOWED_CATEGORIES = set(LIVE_CATEGORIES + SERIES_CATEGORIES + MOVIE_CATEGORIES)

LIVE_KEYWORDS = [
    ("Canais Abertos", [" globo ", " sbt ", " record ", " band ", " redetv ", " rede tv "]),
    ("Canais Documentarios", [" discovery ", "history", " animal planet ", " nat geo ", "document"]),
    ("Canais Filmes e Series", [" cinema ", " filmes ", " series ", " movie channel ", " film "]),
    ("Canais HBO", [" hbo "]),
    ("Canais Telecine", [" telecine "]),
    ("Canais Infantis", [" cartoon ", "nick", " disney junior ", " boomerang ", " gloob ", " discovery kids "]),
    ("Canais Noticias", [" news ", " cnn ", " bbc news ", "globonews", " jornal ", "noticias"]),
    ("Canais Religiosos", [" jesus ", " gospel ", " igreja ", " church ", " biblia ", " catolica ", " religioso "]),
    ("Canais Premiere Clubes", [" premiere "]),
    ("Canais Sportv", [" sportv ", " sport tv "]),
    ("Canais ESPN", [" espn "]),
    ("Canais Amazon Prime", [" amazon prime ", " prime video sports "]),
    ("Canais Disney", [" disney channel ", " disney xd ", " disney jr ", " disney + ", " disney+ "]),
    ("Canais Paramount", [" paramount "]),
    ("Canais HBO MAX", [" hbo max ", " max channels "]),
    ("Canais TNT", [" tnt "]),
    ("Canais Combate/UFC Fight", [" combate ", " ufc ", " fight "]),
    ("Canais Nba League Pass", [" nba league pass ", " nba tv "]),
    ("Canais Apple TV", [" apple tv "]),
    ("Canais Cazé TV", [" caze tv ", " cazé tv "]),
    ("Canais DAZN", [" dazn "]),
    ("Canais GE TV", [" ge tv ", " esporte globo "]),
    ("Canais GOAT", [" goat "]),
    ("Canais Nosso Futebol", [" nosso futebol "]),
    ("Canais NSPORTS", [" nsports "]),
    ("Canais XSPORTS", [" xsports "]),
    ("Canais 24h Animes", [" anime ", " animex ", " anime vision "]),
    ("Canais 24h Discovery", [" discovery world ", " discovery turbo ", " discovery theater "]),
    ("Canais 24h Novelas", [" novela ", " telenovela "]),
    ("Canais 24h Infantis", [" baby shark ", " kids ", " kids tv ", " baby tv "]),
    ("Canais 24h Series de TV", [" tv series ", " series channel ", " sitcom "]),
    ("Canais Adultos", [" adult ", " porno ", " xxx "]),
]

SERIES_KEYWORDS = [
    ("ABC", [" abc "]),
    ("AMC+", [" amc+ ", " amc plus "]),
    ("Apple TV", [" apple tv "]),
    ("BBC ONE", [" bbc one "]),
    ("Brasil Paralelo", [" brasil paralelo "]),
    ("CW", [" cw "]),
    ("Discovery +", [" discovery+ ", " discovery plus "]),
    ("Disney +", [" disney+ ", " disney + "]),
    ("GloboPlay", [" globoplay "]),
    ("HBO Max", [" hbo max ", " max original "]),
    ("Hulu", [" hulu "]),
    ("Lionsgate +", [" lionsgate+ ", " lionsgate plus "]),
    ("Looke", [" looke "]),
    ("Netflix", [" netflix "]),
    ("Paramount +", [" paramount+ ", " paramount plus "]),
    ("PlayPlus", [" playplus "]),
    ("Amazon Prime Video", [" amazon prime video ", " prime video "]),
    ("Starz", [" starz "]),
    ("Via Play", [" via play ", " viaplay "]),
    ("Ação", [" action ", " acao ", " ação "]),
    ("Animação/Infantil", [" animation ", " animacao ", " animação ", " infantil "]),
    ("Animes", [" anime ", " naruto ", " one piece ", " dragon ball ", " demon slayer ", " bleach "]),
    ("Aventura", [" aventura ", " adventure "]),
    ("Chicago Universe", [" chicago fire ", " chicago pd ", " chicago med "]),
    ("Comedia", [" comedy ", " comedia ", " sitcom "]),
    ("Crime", [" crime ", " policial "]),
    ("Documentários", [" documentario ", " documentary "]),
    ("Dorama", [" dorama ", " k-drama ", " korean drama "]),
    ("Drama", [" drama "]),
    ("Ficção e Fantasia", [" sci-fi ", " ficcao ", " ficção ", " fantasy ", " fantasia "]),
    ("Faroeste", [" western ", " faroeste "]),
    ("Guerra", [" guerra ", " war "]),
    ("Marvel", [" marvel "]),
    ("Mini Séries", [" miniserie ", " mini serie ", " mini-series "]),
    ("Nacional", [" brasil ", " brasileiro ", " nacional "]),
    ("Novelas", [" novela ", " telenovela "]),
    ("Reality Shows", [" reality ", " reality show "]),
    ("Romance", [" romance "]),
    ("Suspense", [" suspense ", " thriller "]),
    ("Terror", [" horror ", " terror "]),
    ("Turcas", [" turca ", " turkish "]),
    ("Tv Show", [" tv show ", " talk show ", " variety show "]),
]

MOVIE_KEYWORDS = [
    ("Lançamentos", [" lançamento ", " lancamento ", "new release"]),
    ("4K", [" 4k ", " ultra hd "]),
    ("Ação", [" action ", " acao ", " ação "]),
    ("Animação", [" animation ", " animacao ", " animação "]),
    ("Animes Filmes", [" anime movie ", " anime film ", " anime "]),
    ("Aventura", [" aventura ", " adventure "]),
    ("Clássicos", [" classicos ", " clássicos ", " classic "]),
    ("Coletânea 007", [" 007 ", " james bond "]),
    ("Coletânea Batman", [" batman "]),
    ("Coletânea Bourne", [" bourne "]),
    ("Coletânea Jornada nas Estrelas", [" star trek ", " jornada nas estrelas "]),
    ("Coletânea Os Trapalhões", [" trapalhoes ", " trapalhões "]),
    ("Coletânea Resident Evil", [" resident evil "]),
    ("Coletânea Rocky", [" rocky "]),
    ("Coletânea Star Wars", [" star wars "]),
    ("Comédia Stand-up", [" stand-up ", " stand up "]),
    ("Comédia", [" comedy ", " comedia ", " comédia "]),
    ("Comédia Romântica", [" romantic comedy ", " comedia romantica ", " comédia romântica "]),
    ("Crime", [" crime ", " policial "]),
    ("Drama", [" drama "]),
    ("Documentários Filmes", [" documentario ", " documentary "]),
    ("Faroeste", [" western ", " faroeste "]),
    ("Ficção", [" sci-fi ", " ficcao ", " ficção ", " fantasy ", " fantasia "]),
    ("Guerra", [" guerra ", " war "]),
    ("Infantil", [" infantil ", " kids ", " children "]),
    ("Karaoke", [" karaoke "]),
    ("Legendados", [" legendado ", " subtitled "]),
    ("Musical", [" musical "]),
    ("Nacional", [" brasil ", " brasileiro ", " nacional "]),
    ("Religiosos", [" religioso ", " faith ", " gospel ", " biblia "]),
    ("Romance", [" romance "]),
    ("Suspense", [" suspense ", " thriller "]),
    ("Terror", [" horror ", " terror "]),
    ("Especiais de Natal", [" natal ", " christmas "]),
]

VOD_URL_HINTS = ("/movie/", "/movies/", "/film/", "/films/", "/vod/", "/series/", "/serie/", "/episode/", "/episodes/")
SERIES_TEXT_HINTS = (" temporada ", " episodio ", " episode ", " season ")
MOVIE_TEXT_HINTS = ()
LIVE_TEXT_HINTS = (" ao vivo ", " live ", " channel ", " canal ", " tv ")


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

    def clone(self) -> "PlaylistEntry":
        return PlaylistEntry(
            name=self.name,
            url=self.url,
            attributes=self.attributes.copy(),
            directives=self.directives.copy(),
            source=self.source,
            content_type=self.content_type,
            group_title=self.group_title,
        )


def configure_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")


def ensure_directories(project_root: Path) -> None:
    for path in [
        project_root / "scripts",
        project_root / "config",
        project_root / "playlists" / "source",
        project_root / "output" / "live",
        project_root / "output" / "series",
        project_root / "output" / "movies",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def clean_generated_outputs(project_root: Path) -> None:
    output_dir = project_root / "output"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    ensure_directories(project_root)


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


def slugify(value: str) -> str:
    value = normalized_text(value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


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


def normalize_category(category: str, allowed_categories: list[str], fallback: str) -> str:
    normalized = normalized_text(category)
    for allowed in allowed_categories:
        if normalized_text(allowed) == normalized:
            return allowed
    return fallback


def safe_name(entry: PlaylistEntry) -> str:
    return squeeze_spaces(entry.attributes.get("tvg-name", "") or entry.name or "Sem Nome")


def existing_group_title(entry: PlaylistEntry) -> str:
    return squeeze_spaces(entry.attributes.get("group-title", ""))


def text_haystack(entry: PlaylistEntry) -> str:
    return f" {normalized_text(' '.join([entry.name, entry.tvg_id, existing_group_title(entry), entry.url]))} "


def detection_haystack(entry: PlaylistEntry) -> str:
    return f" {normalized_text(' '.join([entry.name, entry.tvg_id, entry.url]))} "


def url_has_extension(url: str, extensions: tuple[str, ...]) -> bool:
    lowered = url.lower()
    return any(lowered.endswith(extension) for extension in extensions)


def detect_content_type(entry: PlaylistEntry) -> str:
    attrs = {key.lower(): value for key, value in entry.attributes.items()}
    type_attr = normalized_text(attrs.get("type", ""))
    haystack = detection_haystack(entry)
    group_title = normalized_text(existing_group_title(entry))
    url_lower = entry.url.lower()

    if type_attr == "series":
        return "series"
    if type_attr == "movie":
        return "movies"

    strong_series = bool(SERIES_EPISODE_RE.search(entry.name)) or any(token in haystack for token in SERIES_TEXT_HINTS) or "/series/" in url_lower or "/serie/" in url_lower
    strong_movie = url_has_extension(url_lower, MEDIA_EXTENSIONS) or any(token in url_lower for token in VOD_URL_HINTS if "series" not in token)
    obvious_live = group_title.startswith("tv ao vivo |") or any(token in haystack for token in LIVE_TEXT_HINTS) or "/live/" in url_lower or url_has_extension(url_lower, LIVE_STREAM_EXTENSIONS)

    if strong_series and not obvious_live:
        return "series"
    if strong_movie and not obvious_live:
        return "movies"

    if group_title.startswith("series |") and strong_series:
        return "series"
    if group_title.startswith("filmes |") and strong_movie:
        return "movies"

    return "live"


def match_keyword_category(haystack: str, mappings: list[tuple[str, list[str]]], fallback: str) -> str:
    for category, keywords in mappings:
        if any(keyword in haystack for keyword in keywords):
            return category
    return fallback


def detect_live_group(entry: PlaylistEntry) -> str:
    haystack = text_haystack(entry)
    category = match_keyword_category(haystack, LIVE_KEYWORDS, "Canais Variedades")

    if category == "Canais Variedades":
        if any(token in haystack for token in [" bbc ", " france ", " rai ", " dw ", "rtve", " telemundo ", " univision "]):
            category = "Canais Internacionais"

    normalized_existing = normalized_text(existing_group_title(entry))
    if normalized_existing.startswith("tv ao vivo | "):
        existing_suffix = existing_group_title(entry).split("|", 1)[1].strip()
        candidate = normalize_category(f"TV AO VIVO | {existing_suffix}", LIVE_CATEGORIES, "")
        if candidate and candidate != "TV AO VIVO | Todos":
            return candidate.replace("TV AO VIVO | ", "", 1)
    return category


def detect_series_group(entry: PlaylistEntry) -> str:
    haystack = text_haystack(entry)
    category = match_keyword_category(haystack, SERIES_KEYWORDS, "Drama")
    normalized_existing = normalized_text(existing_group_title(entry))
    if normalized_existing.startswith("series | "):
        existing_suffix = existing_group_title(entry).split("|", 1)[1].strip()
        candidate = normalize_category(f"SERIES | {existing_suffix}", SERIES_CATEGORIES, "")
        if candidate and candidate != "SERIES | Todos":
            return candidate.replace("SERIES | ", "", 1)
    return category


def detect_movie_group(entry: PlaylistEntry) -> str:
    haystack = text_haystack(entry)
    year_match = YEAR_RE.search(entry.name)
    if year_match and int(year_match.group(1)) >= 2024:
        return "Lançamentos"

    category = match_keyword_category(haystack, MOVIE_KEYWORDS, "Cinema")
    normalized_existing = normalized_text(existing_group_title(entry))
    if normalized_existing.startswith("filmes | "):
        existing_suffix = existing_group_title(entry).split("|", 1)[1].strip()
        candidate = normalize_category(f"FILMES | {existing_suffix}", MOVIE_CATEGORIES, "")
        if candidate and candidate != "FILMES | Todos":
            return candidate.replace("FILMES | ", "", 1)
    return category


def prepare_entry(entry: PlaylistEntry) -> PlaylistEntry | None:
    if not entry.name.strip() or not entry.url.strip():
        return None

    prepared = entry.clone()
    prepared.name = safe_name(entry)
    prepared.content_type = detect_content_type(entry)

    if prepared.content_type == "live":
        prepared.group_title = f"TV AO VIVO | {detect_live_group(entry)}"
    elif prepared.content_type == "series":
        prepared.group_title = f"SERIES | {detect_series_group(entry)}"
    else:
        prepared.group_title = f"FILMES | {detect_movie_group(entry)}"

    if prepared.group_title not in ALLOWED_CATEGORIES:
        LOGGER.debug("Falling back to default category for %s", prepared.name)
        prepared.group_title = {
            "live": "TV AO VIVO | Canais Variedades",
            "series": "SERIES | Drama",
            "movies": "FILMES | Cinema",
        }[prepared.content_type]

    prepared.attributes["group-title"] = prepared.group_title
    prepared.attributes["tvg-name"] = prepared.name
    prepared.attributes["tvg-id"] = squeeze_spaces(prepared.attributes.get("tvg-id", ""))
    prepared.attributes["tvg-logo"] = squeeze_spaces(prepared.attributes.get("tvg-logo", ""))

    if prepared.content_type == "series":
        prepared.attributes["type"] = "series"
    elif prepared.content_type == "movies":
        prepared.attributes["type"] = "movie"
    else:
        prepared.attributes.pop("type", None)

    return prepared


def serialize_playlist(entries: Iterable[PlaylistEntry]) -> str:
    lines = ["#EXTM3U"]
    for entry in entries:
        attributes = " ".join(
            f'{key}="{value}"'
            for key, value in sorted(entry.attributes.items())
            if value is not None and value != ""
        )
        lines.append(f"#EXTINF:-1 {attributes},{entry.name}".strip())
        lines.extend(entry.directives)
        lines.append(entry.url)
    return "\n".join(lines) + "\n"


def build_catalog(project_root: Path) -> tuple[list[PlaylistEntry], list[PlaylistEntry]]:
    source_entries: list[PlaylistEntry] = []
    prepared_entries: list[PlaylistEntry] = []

    for playlist in source_playlists(project_root):
        for entry in read_entries_from_file(playlist):
            source_entries.append(entry)
            prepared = prepare_entry(entry)
            if prepared is not None:
                prepared_entries.append(prepared)

    prepared_entries.sort(
        key=lambda item: (
            {"live": 0, "series": 1, "movies": 2}.get(item.content_type, 9),
            item.group_title,
            normalize_name(item.name),
            item.url,
        )
    )
    return source_entries, prepared_entries


def build_category_playlists(entries: list[PlaylistEntry], content_type: str, all_category: str) -> dict[str, list[PlaylistEntry]]:
    scoped_entries = [entry for entry in entries if entry.content_type == content_type]
    categories: dict[str, list[PlaylistEntry]] = {all_category: scoped_entries}
    for entry in scoped_entries:
        categories.setdefault(entry.group_title, []).append(entry)
    return categories


def validate_entries(source_entries: list[PlaylistEntry], entries: list[PlaylistEntry]) -> dict[str, object]:
    output_url_counter = Counter(entry.url for entry in entries)
    source_url_counter = Counter(entry.url for entry in source_entries if entry.name.strip() and entry.url.strip())
    category_counts = Counter(entry.group_title for entry in entries)

    empty_categories = {
        "live": [category for category in LIVE_CATEGORIES if category != "TV AO VIVO | Todos" and category_counts.get(category, 0) == 0],
        "series": [category for category in SERIES_CATEGORIES if category != "SERIES | Todos" and category_counts.get(category, 0) == 0],
        "movies": [category for category in MOVIE_CATEGORIES if category != "FILMES | Todos" and category_counts.get(category, 0) == 0],
    }

    invalid_categories = sorted(category for category in category_counts if category not in ALLOWED_CATEGORIES)
    live_with_media_prefix = sorted(entry.name for entry in entries if entry.content_type == "live" and ("SERIES" in entry.group_title or "FILMES" in entry.group_title))

    return {
        "source_entries": len(source_entries),
        "output_entries": len(entries),
        "content_counts": Counter(entry.content_type for entry in entries),
        "categories": dict(sorted(category_counts.items())),
        "empty_categories": empty_categories,
        "invalid_categories": invalid_categories,
        "live_with_media_prefix": live_with_media_prefix,
        "urls_preserved": source_url_counter == output_url_counter,
        "source_url_count": sum(source_url_counter.values()),
        "output_url_count": sum(output_url_counter.values()),
    }


def print_validation_report(report: dict[str, object]) -> None:
    LOGGER.info("Validation summary")
    LOGGER.info("Source entries: %s", report["source_entries"])
    LOGGER.info("Output entries: %s", report["output_entries"])
    LOGGER.info("Content counts: %s", dict(report["content_counts"]))
    LOGGER.info("URLs preserved: %s", report["urls_preserved"])
    LOGGER.info("Invalid categories: %s", len(report["invalid_categories"]))
    LOGGER.info(
        "Empty categories -> live: %s, series: %s, movies: %s",
        len(report["empty_categories"]["live"]),
        len(report["empty_categories"]["series"]),
        len(report["empty_categories"]["movies"]),
    )
    LOGGER.info("Live entries misfiled as series/movies: %s", len(report["live_with_media_prefix"]))


def write_outputs(project_root: Path, entries: list[PlaylistEntry]) -> None:
    ensure_directories(project_root)
    (project_root / "output" / "index.m3u").write_text(serialize_playlist(entries), encoding="utf-8")

    playlist_groups = [
        ("live", "TV AO VIVO | Todos", project_root / "output" / "live"),
        ("series", "SERIES | Todos", project_root / "output" / "series"),
        ("movies", "FILMES | Todos", project_root / "output" / "movies"),
    ]

    for content_type, all_category, target_dir in playlist_groups:
        category_playlists = build_category_playlists(entries, content_type, all_category)
        for category, category_entries in sorted(category_playlists.items()):
            filename = f"{slugify(category)}.m3u"
            (target_dir / filename).write_text(serialize_playlist(category_entries), encoding="utf-8")
