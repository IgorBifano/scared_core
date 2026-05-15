from __future__ import annotations

import argparse
import sys
from pathlib import Path

from iptv_core import (
    LOGGER,
    build_catalog,
    configure_logging,
    ensure_directories,
    migrate_legacy_sources,
    print_validation_report,
    validate_entries,
    write_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a single clean IPTV playlist.")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    configure_logging(verbose=args.verbose)
    ensure_directories(project_root)
    migrate_legacy_sources(project_root)

    entries = build_catalog(project_root)
    if not entries:
        LOGGER.error("No public entries found in playlists/source")
        return 1

    report = validate_entries(entries)
    write_outputs(project_root, entries, report)
    print_validation_report(report)
    LOGGER.info("Generated output/index.m3u with %s entries", len(entries))
    return 0


if __name__ == "__main__":
    sys.exit(main())
