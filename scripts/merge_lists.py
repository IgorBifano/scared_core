from __future__ import annotations

import argparse
import sys
from pathlib import Path
from urllib.error import URLError

from iptv_core import (
    LOGGER,
    check_stream_availability,
    collect_local_playlists,
    configure_logging,
    deduplicate_entries,
    enrich_entries,
    ensure_directories,
    load_remote_sources,
    read_entries_from_file,
    read_entries_from_url,
    resolve_plus_playlist,
    write_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge IPTV playlists and generate organized outputs.")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--check-streams", action="store_true", help="Check stream connectivity before writing output.")
    parser.add_argument("--timeout", type=float, default=3.0, help="Timeout for remote fetch and availability checks.")
    parser.add_argument("--limit", type=int, default=None, help="Limit the number of entries checked for availability.")
    parser.add_argument(
        "--base-url",
        default="https://igorbifano.github.io/scared_core/output",
        help="Public base URL used to build index.m3u for GitHub Pages.",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    configure_logging(verbose=args.verbose)
    ensure_directories(project_root)

    source_counts = {"local_files": 0, "plus_entries": 0, "remote_entries": 0}
    all_entries = []

    local_playlists = collect_local_playlists(project_root)
    for playlist_path in local_playlists:
        entries = read_entries_from_file(playlist_path, source_priority=2)
        source_counts["local_files"] += len(entries)
        all_entries.extend(entries)

    plus_playlist = resolve_plus_playlist(project_root)
    if plus_playlist:
        plus_entries = read_entries_from_file(plus_playlist, source_priority=3)
        source_counts["plus_entries"] = len(plus_entries)
        all_entries.extend(plus_entries)
    else:
        LOGGER.warning("plus.m3u was not found in %s or %s", project_root, project_root.parent)

    remote_sources = load_remote_sources(project_root / "config" / "sources.txt")
    for remote_source in remote_sources:
        try:
            remote_entries = read_entries_from_url(remote_source, source_priority=1, timeout=args.timeout)
        except (URLError, OSError, ValueError) as exc:
            LOGGER.warning("Skipping remote source %s: %s", remote_source, exc)
            continue
        source_counts["remote_entries"] += len(remote_entries)
        all_entries.extend(remote_entries)

    LOGGER.info("Collected %s raw entries", len(all_entries))

    entries = enrich_entries(all_entries)
    deduped_entries, cleanup_stats = deduplicate_entries(entries)
    LOGGER.info("Remaining entries after cleanup: %s", len(deduped_entries))

    if args.check_streams:
        deduped_entries, removed = check_stream_availability(
            deduped_entries,
            timeout=args.timeout,
            limit=args.limit,
        )
        cleanup_stats["offline_removed"] = removed
        LOGGER.info("Remaining entries after availability check: %s", len(deduped_entries))
    else:
        cleanup_stats["offline_removed"] = 0

    write_outputs(project_root, deduped_entries, cleanup_stats, source_counts, base_url=args.base_url)
    LOGGER.info("Output written to %s", project_root / "output")
    return 0


if __name__ == "__main__":
    sys.exit(main())
