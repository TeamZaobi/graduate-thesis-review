#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_EXTENSIONS = {".md", ".html", ".txt", ".json", ".csv"}


def iter_text_files(root: Path) -> list[Path]:
    return [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in DEFAULT_EXTENSIONS
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scan a thesis-review workspace for stale absolute paths."
    )
    parser.add_argument("--root", required=True, help="Workspace root to scan")
    parser.add_argument(
        "--match-root",
        action="append",
        required=True,
        help="Absolute root prefix that should no longer appear",
    )
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    stale_roots = args.match_root

    matches: list[str] = []
    for path in iter_text_files(root):
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for lineno, line in enumerate(lines, start=1):
            for stale_root in stale_roots:
                if stale_root in line:
                    matches.append(f"{path}:{lineno}: {line.strip()}")

    if matches:
        print(f"Found {len(matches)} stale path reference(s):")
        for match in matches:
            print(match)
        return 1

    print(f"No stale path references found under {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
