#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any
from zipfile import ZipFile
import xml.etree.ElementTree as ET

from legacy_asset_paths import notes_dir


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
IN_TEXT_NUMERIC_RE = re.compile(r"\[(\d+(?:\s*[-,，、]\s*\d+)*)\]")
REFERENCE_ENTRY_RE = re.compile(r"^\[(\d+)\]\s*(.*)$")
REFERENCE_HEADINGS = {"参考文献", "references", "bibliography"}
REFERENCE_END_HEADINGS = {"附录", "appendix", "supplementarymaterials"}

REFERENCE_TYPE_MAP = {
    "J": "journal_article",
    "M": "monograph",
    "D": "dissertation",
    "R": "report",
    "S": "standard",
    "C": "conference_paper",
    "P": "patent",
}

SECONDARY_SOURCE_TERMS = [
    "review",
    "meta-analysis",
    "systematic review",
    "umbrella review",
    "guideline",
    "guidelines",
    "statement",
    "consensus",
    "tutorial",
]


def paragraph_text(node: ET.Element) -> str:
    return "".join(text_node.text or "" for text_node in node.iterfind(".//w:t", NS)).strip()


def normalize_heading(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def preview(text: str, limit: int = 120) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def iter_paragraphs(docx_path: Path) -> list[dict[str, Any]]:
    with ZipFile(docx_path) as archive:
        document_xml = archive.read("word/document.xml")

    root = ET.fromstring(document_xml)
    body = root.find("w:body", NS)
    if body is None:
        return []

    paragraphs: list[dict[str, Any]] = []
    for child in list(body):
        kind = child.tag.rsplit("}", 1)[-1]
        if kind != "p":
            continue
        text = paragraph_text(child)
        if not text:
            continue
        paragraphs.append(
            {
                "paragraph_index": len(paragraphs) + 1,
                "text": text,
            }
        )
    return paragraphs


def find_references_section(paragraphs: list[dict[str, Any]]) -> tuple[int | None, int | None]:
    start: int | None = None
    for index, paragraph in enumerate(paragraphs):
        if normalize_heading(paragraph["text"]) in REFERENCE_HEADINGS:
            start = index
    if start is None:
        return None, None

    end = len(paragraphs)
    for index in range(start + 1, len(paragraphs)):
        heading = normalize_heading(paragraphs[index]["text"])
        if heading in REFERENCE_END_HEADINGS:
            end = index
            break
    return start, end


def parse_reference_entries(paragraphs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for paragraph in paragraphs:
        text = paragraph["text"].strip()
        match = REFERENCE_ENTRY_RE.match(text)
        if match:
            if current is not None:
                entries.append(current)
            number = int(match.group(1))
            entry_text = match.group(2).strip()
            current = {
                "reference_no": number,
                "reference_anchor": f"reference_{number:03d}",
                "paragraph_index": paragraph["paragraph_index"],
                "citation_text": f"[{number}] {entry_text}" if entry_text else f"[{number}]",
            }
            continue

        if current is not None:
            current["citation_text"] = (current["citation_text"] + " " + text).strip()

    if current is not None:
        entries.append(current)

    return entries


def expand_numeric_citations(body: str) -> list[int]:
    numbers: list[int] = []
    for part in re.split(r"[,，、]", body):
        token = part.strip()
        if not token:
            continue
        if "-" in token:
            start_text, end_text = [value.strip() for value in token.split("-", 1)]
            try:
                start_no = int(start_text)
                end_no = int(end_text)
            except ValueError:
                continue
            if start_no <= end_no:
                numbers.extend(range(start_no, end_no + 1))
            else:
                numbers.extend(range(start_no, end_no - 1, -1))
            continue
        try:
            numbers.append(int(token))
        except ValueError:
            continue
    return numbers


def infer_citation_type(citation_text: str) -> str:
    match = re.search(r"\[([A-Z])\]", citation_text)
    if match:
        return REFERENCE_TYPE_MAP.get(match.group(1), "unknown")

    lowered = citation_text.lower()
    for token in SECONDARY_SOURCE_TERMS:
        if token in lowered:
            return "review_or_guideline"
    return "unknown"


def infer_primary_source(citation_text: str) -> bool:
    lowered = citation_text.lower()
    return not any(token in lowered for token in SECONDARY_SOURCE_TERMS)


def build_items(
    body_paragraphs: list[dict[str, Any]],
    references_by_no: dict[int, dict[str, Any]],
) -> tuple[list[dict[str, Any]], int]:
    items: list[dict[str, Any]] = []
    occurrence_count = 0

    for paragraph in body_paragraphs:
        text = paragraph["text"]
        for match in IN_TEXT_NUMERIC_RE.finditer(text):
            occurrence_count += 1
            marker = match.group(0)
            for number in expand_numeric_citations(match.group(1)):
                reference = references_by_no.get(number)
                citation_text = reference["citation_text"] if reference else marker
                items.append(
                    {
                        "id": f"cit_{len(items) + 1:04d}",
                        "claim_anchor": f"paragraph_{paragraph['paragraph_index']:04d}",
                        "claim_text_preview": preview(text),
                        "paragraph_index": paragraph["paragraph_index"],
                        "citation_marker": marker,
                        "citation_no": number,
                        "citation_text": citation_text,
                        "citation_type": infer_citation_type(citation_text),
                        "is_primary_source": infer_primary_source(citation_text),
                        "reference_anchor": reference["reference_anchor"] if reference else None,
                        "reference_paragraph_index": reference["paragraph_index"] if reference else None,
                        "reference_found": reference is not None,
                    }
                )

    return items, occurrence_count


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract in-text numeric citations and bibliography entries from a DOCX."
    )
    parser.add_argument("--docx", required=True, help="Path to source DOCX")
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument(
        "--output-dir",
        help="Directory for extraction manifest output",
    )
    target_group.add_argument(
        "--paper-dir",
        help="Paper workspace root. Defaults manifest to notes/citation_extraction_manifest.json and objects to objects/citations.json",
    )
    parser.add_argument(
        "--manifest",
        help="Optional manifest path. Defaults to <output-dir>/manifest.json or <paper-dir>/notes/citation_extraction_manifest.json",
    )
    parser.add_argument(
        "--objects-path",
        help="Optional objects/citations.json path to overwrite with extracted metadata",
    )
    args = parser.parse_args()

    docx_path = Path(args.docx).expanduser().resolve()
    paper_dir = Path(args.paper_dir).expanduser().resolve() if args.paper_dir else None

    if paper_dir is not None:
        output_dir = notes_dir(paper_dir)
        default_manifest = notes_dir(paper_dir) / "citation_extraction_manifest.json"
        default_objects = paper_dir / "objects" / "citations.json"
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

    paragraphs = iter_paragraphs(docx_path)
    ref_start, ref_end = find_references_section(paragraphs)

    if ref_start is None:
        body_paragraphs = paragraphs
        reference_entries: list[dict[str, Any]] = []
        references_anchor = None
    else:
        body_paragraphs = paragraphs[:ref_start]
        reference_entries = parse_reference_entries(paragraphs[ref_start + 1 : ref_end])
        references_anchor = f"paragraph_{paragraphs[ref_start]['paragraph_index']:04d}"

    references_by_no = {
        entry["reference_no"]: entry for entry in reference_entries
    }
    items, occurrence_count = build_items(body_paragraphs, references_by_no)

    manifest = {
        "source_docx": str(docx_path),
        "paper_id": paper_id,
        "output_dir": str(output_dir),
        "citation_style": "numeric" if items or reference_entries else "unknown",
        "references_section_anchor": references_anchor,
        "reference_count": len(reference_entries),
        "citation_occurrence_count": occurrence_count,
        "item_count": len(items),
        "unmatched_reference_numbers": sorted(
            {
                item["citation_no"]
                for item in items
                if not item["reference_found"]
            }
        ),
        "references": reference_entries,
        "items": items,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    if objects_path is not None:
        payload = {
            "paper_id": paper_id,
            "kind": "citations",
            "source_docx": str(docx_path),
            "citation_style": manifest["citation_style"],
            "reference_count": len(reference_entries),
            "items": items,
        }
        objects_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print(f"Extracted {len(items)} citation links from {docx_path}")
    print(f"Detected {len(reference_entries)} bibliography entries")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
