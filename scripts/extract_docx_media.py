#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZipFile


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract DOCX word/media assets into a stable output directory."
    )
    parser.add_argument("--docx", required=True, help="Path to the source DOCX file")
    parser.add_argument("--output", required=True, help="Directory for extracted media")
    parser.add_argument(
        "--manifest",
        help="Optional JSON manifest path. Defaults to <output>/manifest.json",
    )
    args = parser.parse_args()

    docx_path = Path(args.docx).expanduser().resolve()
    output_dir = Path(args.output).expanduser().resolve()
    manifest_path = (
        Path(args.manifest).expanduser().resolve()
        if args.manifest
        else output_dir / "manifest.json"
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    items = []
    with ZipFile(docx_path) as archive:
        members = [
            member
            for member in archive.infolist()
            if member.filename.startswith("word/media/") and not member.is_dir()
        ]
        for member in members:
            filename = Path(member.filename).name
            destination = output_dir / filename
            data = archive.read(member.filename)
            destination.write_bytes(data)
            items.append(
                {
                    "id": f"docx_media_{filename.replace('.', '_')}",
                    "asset_type": "docx_media_extract",
                    "source_kind": "docx_media",
                    "source_docx": str(docx_path),
                    "source_path": member.filename,
                    "member": member.filename,
                    "filename": filename,
                    "output_path": str(destination),
                    "size": len(data),
                }
            )

    manifest = {
        "kind": "assets_manifest",
        "source_docx": str(docx_path),
        "output_dir": str(output_dir),
        "item_count": len(items),
        "items": items,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        f"Extracted {len(items)} media assets from {docx_path} to {output_dir}"
    )
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
