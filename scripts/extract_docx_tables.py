#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any
from zipfile import ZipFile
import xml.etree.ElementTree as ET


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
CAPTION_RE = re.compile(r"^\s*(表|附表|Table)\s*[\dA-Za-z\-\.]*")


def paragraph_text(node: ET.Element) -> str:
    return "".join(text_node.text or "" for text_node in node.iterfind(".//w:t", NS)).strip()


def cell_text(cell: ET.Element) -> str:
    parts = []
    for paragraph in cell.findall("./w:p", NS):
        text = paragraph_text(paragraph)
        if text:
            parts.append(text)
    return "\n".join(parts).strip()


def grid_span(cell: ET.Element) -> int:
    span = cell.find("./w:tcPr/w:gridSpan", NS)
    if span is None:
        return 1
    value = span.attrib.get(f"{{{NS['w']}}}val") or span.attrib.get("val")
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        return 1


def normalize_row(row: list[str], width: int) -> list[str]:
    if len(row) < width:
        return row + [""] * (width - len(row))
    return row


def surrounding_paragraphs(blocks: list[dict[str, Any]], index: int) -> tuple[list[str], list[str]]:
    before: list[str] = []
    after: list[str] = []

    cursor = index - 1
    while cursor >= 0 and len(before) < 3:
        block = blocks[cursor]
        if block["kind"] == "p" and block["text"]:
            before.append(block["text"])
        cursor -= 1

    cursor = index + 1
    while cursor < len(blocks) and len(after) < 3:
        block = blocks[cursor]
        if block["kind"] == "p" and block["text"]:
            after.append(block["text"])
        cursor += 1

    return before, after


def caption_candidate(before: list[str], after: list[str]) -> str:
    for text in before + after:
        if CAPTION_RE.match(text):
            return text
    return before[0] if before else (after[0] if after else "")


def parse_document(docx_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    with ZipFile(docx_path) as archive:
        document_xml = archive.read("word/document.xml")

    root = ET.fromstring(document_xml)
    body = root.find("w:body", NS)
    if body is None:
        return [], []

    blocks: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []

    for child in list(body):
        kind = child.tag.rsplit("}", 1)[-1]
        if kind == "p":
            text = paragraph_text(child)
            blocks.append({"kind": "p", "text": text})
            continue
        if kind != "tbl":
            continue

        rows: list[list[str]] = []
        width = 0
        for row in child.findall("./w:tr", NS):
            values: list[str] = []
            for cell in row.findall("./w:tc", NS):
                text = cell_text(cell)
                values.append(text)
                for _ in range(grid_span(cell) - 1):
                    values.append("")
            width = max(width, len(values))
            rows.append(values)

        rows = [normalize_row(row, width) for row in rows]
        blocks.append({"kind": "tbl", "rows": rows})

    for index, block in enumerate(blocks):
        if block["kind"] != "tbl":
            continue
        before, after = surrounding_paragraphs(blocks, index)
        rows = block["rows"]
        tables.append(
            {
                "table_index": len(tables) + 1,
                "caption_candidate": caption_candidate(before, after),
                "preceding_paragraphs": before,
                "following_paragraphs": after,
                "row_count": len(rows),
                "column_count": max((len(row) for row in rows), default=0),
                "header_preview": rows[0] if rows else [],
                "rows": rows,
            }
        )

    return blocks, tables


def infer_table_no(caption: str, table_index: int) -> str:
    match = re.search(r"(表\s*[\dA-Za-z\-\.]+|Table\s*[\dA-Za-z\-\.]+)", caption)
    if match:
        return match.group(1).replace(" ", "")
    return f"table_{table_index:03d}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract DOCX tables into CSV files and a JSON manifest."
    )
    parser.add_argument("--docx", required=True, help="Path to source DOCX")
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument("--output-dir", help="Directory for CSV output")
    target_group.add_argument(
        "--paper-dir",
        help="Paper workspace root. Defaults output to assets/tables/docx_csv and objects to objects/tables.json",
    )
    parser.add_argument(
        "--manifest",
        help="Optional manifest path. Defaults to <output-dir>/manifest.json",
    )
    parser.add_argument(
        "--objects-path",
        help="Optional objects/tables.json path to overwrite with extracted metadata",
    )
    args = parser.parse_args()

    docx_path = Path(args.docx).expanduser().resolve()
    paper_dir = Path(args.paper_dir).expanduser().resolve() if args.paper_dir else None

    if paper_dir is not None:
        output_dir = paper_dir / "assets" / "tables" / "docx_csv"
        default_manifest = paper_dir / "assets" / "tables" / "manifest.json"
        default_objects = paper_dir / "objects" / "tables.json"
        paper_id = paper_dir.name
    else:
        output_dir = Path(args.output_dir).expanduser().resolve()
        default_manifest = output_dir / "manifest.json"
        default_objects = None
        paper_id = ""

    manifest_path = (
        Path(args.manifest).expanduser().resolve() if args.manifest else default_manifest
    )
    objects_path = (
        Path(args.objects_path).expanduser().resolve()
        if args.objects_path
        else default_objects
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    if objects_path is not None:
        objects_path.parent.mkdir(parents=True, exist_ok=True)

    _, tables = parse_document(docx_path)

    manifest_items: list[dict[str, Any]] = []
    object_items: list[dict[str, Any]] = []

    for table in tables:
        index = table["table_index"]
        caption = table["caption_candidate"]
        table_no = infer_table_no(caption, index)
        csv_name = f"table_{index:03d}.csv"
        csv_path = output_dir / csv_name

        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerows(table["rows"])

        manifest_items.append(
            {
                "table_index": index,
                "table_no": table_no,
                "caption_candidate": caption,
                "row_count": table["row_count"],
                "column_count": table["column_count"],
                "header_preview": table["header_preview"],
                "preceding_paragraphs": table["preceding_paragraphs"],
                "following_paragraphs": table["following_paragraphs"],
                "csv_path": str(csv_path),
            }
        )
        object_items.append(
            {
                "id": f"tbl_{index:03d}",
                "table_no": table_no,
                "caption": caption,
                "source_docx": str(docx_path),
                "csv_path": str(csv_path),
                "row_count": table["row_count"],
                "column_count": table["column_count"],
                "header_preview": table["header_preview"],
                "preceding_paragraphs": table["preceding_paragraphs"],
                "following_paragraphs": table["following_paragraphs"],
            }
        )

    manifest = {
        "source_docx": str(docx_path),
        "output_dir": str(output_dir),
        "table_count": len(manifest_items),
        "items": manifest_items,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    if objects_path is not None:
        payload = {
            "paper_id": paper_id,
            "kind": "tables",
            "source_docx": str(docx_path),
            "items": object_items,
        }
        objects_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print(f"Extracted {len(manifest_items)} tables from {docx_path}")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
