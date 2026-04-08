#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any
from zipfile import BadZipFile, ZipFile
import xml.etree.ElementTree as ET

from legacy_asset_paths import notes_dir


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC_NS = "http://purl.org/dc/elements/1.1/"

NS = {
    "w": W_NS,
    "m": M_NS,
    "cp": CP_NS,
    "dc": DC_NS,
}

HEADING_PATTERNS = [
    re.compile(r"^heading([1-9])$"),
    re.compile(r"^heading([1-9])char$"),
    re.compile(r"^标题([1-9])$"),
    re.compile(r"^标题([1-9])字符$"),
]

FIGURE_CAPTION_RE = re.compile(
    r"^(?:图|figure)\s*([A-Za-z0-9]+(?:[-.][A-Za-z0-9]+)*)",
    flags=re.IGNORECASE,
)
TABLE_CAPTION_RE = re.compile(
    r"^(?:表|table)\s*([A-Za-z0-9]+(?:[-.][A-Za-z0-9]+)*)",
    flags=re.IGNORECASE,
)
EQUATION_NO_RE = re.compile(
    r"(?:式\s*)?[（(]([A-Za-z0-9]+(?:[-.][A-Za-z0-9]+)*)[）)]\s*$"
)

FIELD_ERROR_TERMS = [
    "Error! Bookmark not defined.",
    "错误!未定义书签。",
    "错误！未定义书签。",
]

SECTION_EQUIVALENTS = {
    "abstract_zh": {"摘要", "中文摘要"},
    "abstract_en": {"abstract"},
    "references": {"参考文献", "references", "bibliography"},
    "acknowledgements": {"致谢", "acknowledgements", "acknowledgments"},
    "appendix": {"附录", "appendix", "appendices"},
}

DECLARATION_TERMS = [
    "原创性声明",
    "独创性声明",
    "学位论文原创性声明",
    "授权声明",
    "使用授权声明",
]

FOOTNOTE_SKIP_TYPES = {"separator", "continuationSeparator", "continuationNotice"}


def fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 1


def normalize_text(text: str) -> str:
    return re.sub(r"[\s:：\-_.]+", "", text).lower()


def twips_to_mm(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return round(int(value) * 25.4 / 1440, 2)
    except ValueError:
        return None


def read_xml(archive: ZipFile, member: str) -> ET.Element | None:
    try:
        payload = archive.read(member)
    except KeyError:
        return None
    return ET.fromstring(payload)


def read_story_roots(archive: ZipFile) -> list[tuple[str, ET.Element]]:
    roots: list[tuple[str, ET.Element]] = []
    for name in sorted(archive.namelist()):
        if not name.startswith("word/"):
            continue
        if not name.endswith(".xml"):
            continue
        if not (
            name == "word/document.xml"
            or re.match(r"word/header\d+\.xml", name)
            or re.match(r"word/footer\d+\.xml", name)
        ):
            continue
        root = read_xml(archive, name)
        if root is not None:
            roots.append((name, root))
    return roots


def paragraph_text(node: ET.Element) -> str:
    return "".join(text_node.text or "" for text_node in node.iterfind(".//w:t", NS)).strip()


def parse_styles(archive: ZipFile) -> dict[str, str]:
    root = read_xml(archive, "word/styles.xml")
    if root is None:
        return {}
    styles: dict[str, str] = {}
    for style in root.findall(".//w:style", NS):
        style_id = style.attrib.get(f"{{{W_NS}}}styleId")
        if not style_id:
            continue
        name_node = style.find("w:name", NS)
        style_name = (
            name_node.attrib.get(f"{{{W_NS}}}val", "").strip() if name_node is not None else ""
        )
        styles[style_id] = style_name
    return styles


def detect_heading_level(style_id: str | None, style_name: str | None) -> int | None:
    for raw in [style_id or "", style_name or ""]:
        normalized = normalize_text(raw)
        for pattern in HEADING_PATTERNS:
            match = pattern.match(normalized)
            if match:
                return int(match.group(1))
    return None


def iter_paragraphs(document_root: ET.Element, style_map: dict[str, str]) -> list[dict[str, Any]]:
    body = document_root.find("w:body", NS)
    if body is None:
        return []

    paragraphs: list[dict[str, Any]] = []
    for paragraph_index, node in enumerate(body.iterfind(".//w:p", NS), start=1):
        style_node = node.find("w:pPr/w:pStyle", NS)
        style_id = (
            style_node.attrib.get(f"{{{W_NS}}}val", "").strip() if style_node is not None else ""
        )
        style_name = style_map.get(style_id, "")
        text = paragraph_text(node)
        paragraphs.append(
            {
                "paragraph_index": paragraph_index,
                "text": text,
                "normalized_text": normalize_text(text),
                "style_id": style_id,
                "style_name": style_name,
                "heading_level": detect_heading_level(style_id, style_name),
                "has_math": node.find(".//m:oMath", NS) is not None
                or node.find(".//m:oMathPara", NS) is not None,
            }
        )
    return paragraphs


def collect_field_instructions(roots: list[tuple[str, ET.Element]]) -> list[str]:
    instructions: list[str] = []
    for _, root in roots:
        for node in root.findall(".//w:instrText", NS):
            if node.text and node.text.strip():
                instructions.append(node.text.strip())
        for node in root.findall(".//w:fldSimple", NS):
            value = node.attrib.get(f"{{{W_NS}}}instr", "").strip()
            if value:
                instructions.append(value)
    return instructions


def collect_section_properties(document_root: ET.Element) -> list[dict[str, Any]]:
    body = document_root.find("w:body", NS)
    if body is None:
        return []

    sections: list[dict[str, Any]] = []
    for index, sect in enumerate(body.findall(".//w:sectPr", NS), start=1):
        margin_node = sect.find("w:pgMar", NS)
        size_node = sect.find("w:pgSz", NS)
        header_refs = sect.findall("w:headerReference", NS)
        footer_refs = sect.findall("w:footerReference", NS)
        sections.append(
            {
                "section_index": index,
                "orientation": size_node.attrib.get(f"{{{W_NS}}}orient", "portrait")
                if size_node is not None
                else None,
                "page_size": {
                    "width_twips": size_node.attrib.get(f"{{{W_NS}}}w") if size_node is not None else None,
                    "height_twips": size_node.attrib.get(f"{{{W_NS}}}h") if size_node is not None else None,
                },
                "margins": {
                    "top_twips": margin_node.attrib.get(f"{{{W_NS}}}top") if margin_node is not None else None,
                    "bottom_twips": margin_node.attrib.get(f"{{{W_NS}}}bottom") if margin_node is not None else None,
                    "left_twips": margin_node.attrib.get(f"{{{W_NS}}}left") if margin_node is not None else None,
                    "right_twips": margin_node.attrib.get(f"{{{W_NS}}}right") if margin_node is not None else None,
                    "header_twips": margin_node.attrib.get(f"{{{W_NS}}}header") if margin_node is not None else None,
                    "footer_twips": margin_node.attrib.get(f"{{{W_NS}}}footer") if margin_node is not None else None,
                    "gutter_twips": margin_node.attrib.get(f"{{{W_NS}}}gutter") if margin_node is not None else None,
                },
                "header_ref_count": len(header_refs),
                "footer_ref_count": len(footer_refs),
            }
        )
    return sections


def summarize_sections(sections: list[dict[str, Any]]) -> dict[str, Any]:
    signatures = set()
    for section in sections:
        margins = section["margins"]
        signatures.add(
            (
                section["orientation"],
                margins.get("top_twips"),
                margins.get("bottom_twips"),
                margins.get("left_twips"),
                margins.get("right_twips"),
                margins.get("gutter_twips"),
            )
        )
    return {
        "section_count": len(sections),
        "unique_margin_signature_count": len(signatures),
        "sections": [
            {
                "section_index": section["section_index"],
                "orientation": section["orientation"],
                "header_ref_count": section["header_ref_count"],
                "footer_ref_count": section["footer_ref_count"],
                "margins_mm": {
                    key.replace("_twips", "_mm"): twips_to_mm(value)
                    for key, value in section["margins"].items()
                },
            }
            for section in sections
        ],
    }


def detect_sections(paragraphs: list[dict[str, Any]]) -> dict[str, list[int]]:
    found: dict[str, list[int]] = {key: [] for key in SECTION_EQUIVALENTS}
    for paragraph in paragraphs:
        normalized = paragraph["normalized_text"]
        if not normalized:
            continue
        for key, aliases in SECTION_EQUIVALENTS.items():
            if normalized in aliases:
                found[key].append(paragraph["paragraph_index"])
    return found


def detect_declarations(paragraphs: list[dict[str, Any]]) -> list[int]:
    matches: list[int] = []
    for paragraph in paragraphs:
        text = paragraph["text"]
        if any(term in text for term in DECLARATION_TERMS):
            matches.append(paragraph["paragraph_index"])
    return matches


def detect_keywords(paragraphs: list[dict[str, Any]]) -> dict[str, list[int]]:
    result = {"zh": [], "en": []}
    for paragraph in paragraphs:
        text = paragraph["text"]
        if "关键词" in text:
            result["zh"].append(paragraph["paragraph_index"])
        if re.search(r"\bkey\s*words?\b", text, flags=re.IGNORECASE):
            result["en"].append(paragraph["paragraph_index"])
    return result


def detect_heading_skips(paragraphs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    headings = [paragraph for paragraph in paragraphs if paragraph["heading_level"] is not None]
    skips: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None
    for paragraph in headings:
        if previous and paragraph["heading_level"] > previous["heading_level"] + 1:
            skips.append(
                {
                    "from_level": previous["heading_level"],
                    "to_level": paragraph["heading_level"],
                    "from_paragraph": previous["paragraph_index"],
                    "to_paragraph": paragraph["paragraph_index"],
                    "to_text": paragraph["text"],
                }
            )
        previous = paragraph
    return skips


def detect_captions(
    paragraphs: list[dict[str, Any]],
    pattern: re.Pattern[str],
    kind: str,
) -> tuple[list[dict[str, Any]], dict[str, list[int]]]:
    items: list[dict[str, Any]] = []
    duplicates: dict[str, list[int]] = {}
    by_number: dict[str, list[int]] = {}
    for paragraph in paragraphs:
        text = paragraph["text"]
        match = pattern.match(text)
        if not match:
            continue
        number = match.group(1)
        items.append(
            {
                "kind": kind,
                "number": number,
                "paragraph_index": paragraph["paragraph_index"],
                "text": text,
            }
        )
        by_number.setdefault(number, []).append(paragraph["paragraph_index"])
    for number, indexes in by_number.items():
        if len(indexes) > 1:
            duplicates[number] = indexes
    return items, duplicates


def detect_equation_numbers(paragraphs: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, list[int]]]:
    items: list[dict[str, Any]] = []
    duplicates: dict[str, list[int]] = {}
    by_number: dict[str, list[int]] = {}
    for paragraph in paragraphs:
        text = paragraph["text"]
        match = EQUATION_NO_RE.search(text)
        if not match:
            continue
        number = match.group(1)
        items.append(
            {
                "number": number,
                "paragraph_index": paragraph["paragraph_index"],
                "text": text,
            }
        )
        by_number.setdefault(number, []).append(paragraph["paragraph_index"])
    for number, indexes in by_number.items():
        if len(indexes) > 1:
            duplicates[number] = indexes
    return items, duplicates


def count_revisions(roots: list[tuple[str, ET.Element]]) -> int:
    total = 0
    for _, root in roots:
        total += len(root.findall(".//w:ins", NS))
        total += len(root.findall(".//w:del", NS))
        total += len(root.findall(".//w:moveFrom", NS))
        total += len(root.findall(".//w:moveTo", NS))
    return total


def count_hidden_runs(roots: list[tuple[str, ET.Element]]) -> int:
    total = 0
    for _, root in roots:
        total += len(root.findall(".//w:vanish", NS))
    return total


def parse_comments(archive: ZipFile) -> int:
    root = read_xml(archive, "word/comments.xml")
    if root is None:
        return 0
    return len(root.findall(".//w:comment", NS))


def parse_notes(archive: ZipFile, member: str, note_tag: str) -> int:
    root = read_xml(archive, member)
    if root is None:
        return 0
    count = 0
    for node in root.findall(f".//w:{note_tag}", NS):
        note_type = node.attrib.get(f"{{{W_NS}}}type")
        if note_type in FOOTNOTE_SKIP_TYPES:
            continue
        count += 1
    return count


def parse_core_properties(archive: ZipFile) -> dict[str, str | None]:
    root = read_xml(archive, "docProps/core.xml")
    if root is None:
        return {"creator": None, "last_modified_by": None}
    creator = root.findtext("dc:creator", default=None, namespaces=NS)
    last_modified_by = root.findtext("cp:lastModifiedBy", default=None, namespaces=NS)
    return {
        "creator": creator.strip() if creator else None,
        "last_modified_by": last_modified_by.strip() if last_modified_by else None,
    }


def has_track_revisions(archive: ZipFile) -> bool:
    root = read_xml(archive, "word/settings.xml")
    if root is None:
        return False
    return root.find("w:trackRevisions", NS) is not None


def count_field_matches(instructions: list[str], pattern: str) -> int:
    regex = re.compile(pattern, flags=re.IGNORECASE)
    return sum(1 for instruction in instructions if regex.search(instruction))


def add_check(
    checks: list[dict[str, Any]],
    findings: list[dict[str, Any]],
    *,
    check_id: str,
    category: str,
    status: str,
    severity: str,
    note: str,
    source_file: str,
    template_source: str | None,
    evidence: dict[str, Any] | None = None,
    needs_manual_confirmation: bool = False,
) -> None:
    item = {
        "source_file": source_file,
        "template_source": template_source,
        "scope": "formal_review",
        "category": category,
        "check_id": check_id,
        "severity": severity,
        "status": status,
        "automation": "automatic",
        "evidence": evidence or {},
        "note": note,
        "needs_manual_confirmation": needs_manual_confirmation,
    }
    checks.append(item)
    if status in {"warn", "fail"}:
        findings.append(item)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check a DOCX for thesis formal-review mechanics and emit structured findings."
    )
    parser.add_argument("--docx", required=True, help="Path to source DOCX")
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument("--output-dir", help="Directory for manifest and findings output")
    target_group.add_argument("--paper-dir", help="Paper workspace root")
    parser.add_argument(
        "--manifest",
        help="Optional manifest path. Defaults to <output-dir>/manifest.json or <paper-dir>/notes/formal_review_manifest.json",
    )
    parser.add_argument(
        "--objects-path",
        help="Optional objects/formal_findings.json path to overwrite with extracted findings",
    )
    parser.add_argument(
        "--template-source",
        help="Optional school template or guideline source identifier for this run",
    )
    parser.add_argument(
        "--blind-review",
        action="store_true",
        help="Treat anonymity-sensitive findings as warnings for blind-review export",
    )
    args = parser.parse_args()

    docx_path = Path(args.docx).expanduser().resolve()
    if not docx_path.exists():
        return fail(f"Missing DOCX: {docx_path}")

    paper_dir = Path(args.paper_dir).expanduser().resolve() if args.paper_dir else None
    if paper_dir is not None:
        output_dir = notes_dir(paper_dir)
        default_manifest = notes_dir(paper_dir) / "formal_review_manifest.json"
        default_objects = paper_dir / "objects" / "formal_findings.json"
        paper_id = paper_dir.name
    else:
        output_dir = Path(args.output_dir).expanduser().resolve()
        default_manifest = output_dir / "manifest.json"
        default_objects = output_dir / "formal_findings.json"
        paper_id = ""

    manifest_path = (
        Path(args.manifest).expanduser().resolve() if args.manifest else default_manifest
    )
    objects_path = (
        Path(args.objects_path).expanduser().resolve() if args.objects_path else default_objects
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    objects_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        archive = ZipFile(docx_path)
    except BadZipFile:
        return fail(f"Invalid DOCX/ZIP archive: {docx_path}")

    with archive:
        document_root = read_xml(archive, "word/document.xml")
        if document_root is None:
            return fail(f"Missing word/document.xml in {docx_path}")

        story_roots = read_story_roots(archive)
        styles = parse_styles(archive)
        paragraphs = iter_paragraphs(document_root, styles)
        field_instructions = collect_field_instructions(story_roots)
        sections = collect_section_properties(document_root)
        section_summary = summarize_sections(sections)
        detected_sections = detect_sections(paragraphs)
        declaration_hits = detect_declarations(paragraphs)
        keyword_hits = detect_keywords(paragraphs)
        heading_skips = detect_heading_skips(paragraphs)
        figure_captions, duplicate_figures = detect_captions(paragraphs, FIGURE_CAPTION_RE, "figure")
        table_captions, duplicate_tables = detect_captions(paragraphs, TABLE_CAPTION_RE, "table")
        equation_numbers, duplicate_equations = detect_equation_numbers(paragraphs)
        revisions_count = count_revisions(story_roots)
        hidden_count = count_hidden_runs(story_roots)
        comments_count = parse_comments(archive)
        footnotes_count = parse_notes(archive, "word/footnotes.xml", "footnote")
        endnotes_count = parse_notes(archive, "word/endnotes.xml", "endnote")
        metadata = parse_core_properties(archive)
        track_revisions_enabled = has_track_revisions(archive)

    toc_field_count = count_field_matches(field_instructions, r"\bTOC\b")
    page_field_count = count_field_matches(field_instructions, r"\bPAGE\b")
    cross_ref_error_hits = [
        {
            "paragraph_index": paragraph["paragraph_index"],
            "text": paragraph["text"],
        }
        for paragraph in paragraphs
        if any(term in paragraph["text"] for term in FIELD_ERROR_TERMS)
    ]
    math_paragraph_count = sum(1 for paragraph in paragraphs if paragraph["has_math"])

    checks: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    source_file = str(docx_path)
    template_source = args.template_source

    add_check(
        checks,
        findings,
        check_id="sections.abstracts_present",
        category="document_parts",
        status="pass"
        if detected_sections["abstract_zh"] and detected_sections["abstract_en"]
        else "warn",
        severity="info"
        if detected_sections["abstract_zh"] and detected_sections["abstract_en"]
        else "P1",
        note="已检测到中英文摘要标题。"
        if detected_sections["abstract_zh"] and detected_sections["abstract_en"]
        else "未同时检测到中英文摘要标题；如当前稿件已到送审 / 答辩前，需人工回查摘要页完整性。",
        source_file=source_file,
        template_source=template_source,
        evidence={
            "abstract_zh": detected_sections["abstract_zh"],
            "abstract_en": detected_sections["abstract_en"],
        },
        needs_manual_confirmation=not (
            detected_sections["abstract_zh"] and detected_sections["abstract_en"]
        ),
    )

    add_check(
        checks,
        findings,
        check_id="sections.references_present",
        category="document_parts",
        status="pass" if detected_sections["references"] else "warn",
        severity="info" if detected_sections["references"] else "P1",
        note="已检测到参考文献标题。"
        if detected_sections["references"]
        else "未检测到参考文献标题；如果这不是中期稿，应优先人工确认参考文献页是否缺失或标题样式异常。",
        source_file=source_file,
        template_source=template_source,
        evidence={"references": detected_sections["references"]},
        needs_manual_confirmation=not bool(detected_sections["references"]),
    )

    add_check(
        checks,
        findings,
        check_id="sections.keyword_markers_present",
        category="document_parts",
        status="pass" if keyword_hits["zh"] or keyword_hits["en"] else "warn",
        severity="info" if keyword_hits["zh"] or keyword_hits["en"] else "P2",
        note="已检测到关键词标记。"
        if keyword_hits["zh"] or keyword_hits["en"]
        else "未检测到“关键词 / Key words”标记；需人工确认摘要页是否漏了关键词块或使用了异常写法。",
        source_file=source_file,
        template_source=template_source,
        evidence=keyword_hits,
        needs_manual_confirmation=not (keyword_hits["zh"] or keyword_hits["en"]),
    )

    add_check(
        checks,
        findings,
        check_id="sections.declaration_markers_present",
        category="document_parts",
        status="pass" if declaration_hits else "warn",
        severity="info" if declaration_hits else "P1",
        note="已检测到声明 / 授权相关文字。"
        if declaration_hits
        else "未检测到原创性声明或授权声明关键词；需结合学校模板人工确认是否应单独成页。",
        source_file=source_file,
        template_source=template_source,
        evidence={"declaration_paragraphs": declaration_hits},
        needs_manual_confirmation=True,
    )

    add_check(
        checks,
        findings,
        check_id="word.toc_field_present",
        category="word_mechanics",
        status="pass" if toc_field_count else "warn",
        severity="info" if toc_field_count else "P1",
        note="检测到目录域。"
        if toc_field_count
        else "未检测到 TOC 域；目录可能是手打文本，或正文尚未建立自动目录。",
        source_file=source_file,
        template_source=template_source,
        evidence={"toc_field_count": toc_field_count},
        needs_manual_confirmation=not bool(toc_field_count),
    )

    add_check(
        checks,
        findings,
        check_id="word.page_number_field_present",
        category="word_mechanics",
        status="pass" if page_field_count else "warn",
        severity="info" if page_field_count else "P1",
        note="检测到页码域。"
        if page_field_count
        else "未检测到 PAGE 页码域；需人工确认页码是否丢失，或页码被转成了纯文本。",
        source_file=source_file,
        template_source=template_source,
        evidence={"page_field_count": page_field_count},
        needs_manual_confirmation=not bool(page_field_count),
    )

    heading_count = sum(1 for paragraph in paragraphs if paragraph["heading_level"] is not None)
    add_check(
        checks,
        findings,
        check_id="word.heading_styles_detected",
        category="structure",
        status="pass" if heading_count else "warn",
        severity="info" if heading_count else "P1",
        note=f"检测到 {heading_count} 个带标题样式的段落。"
        if heading_count
        else "未检测到稳定的标题样式；目录、章节编号与样式回归风险较高。",
        source_file=source_file,
        template_source=template_source,
        evidence={"heading_count": heading_count},
        needs_manual_confirmation=not bool(heading_count),
    )

    add_check(
        checks,
        findings,
        check_id="word.heading_level_skips",
        category="structure",
        status="pass" if not heading_skips else "warn",
        severity="info" if not heading_skips else "P2",
        note="未检测到明显的标题层级跳级。"
        if not heading_skips
        else "检测到标题层级跳级；需人工确认章节结构是否正确。",
        source_file=source_file,
        template_source=template_source,
        evidence={"skips": heading_skips[:20], "skip_count": len(heading_skips)},
        needs_manual_confirmation=bool(heading_skips),
    )

    add_check(
        checks,
        findings,
        check_id="word.cross_reference_errors",
        category="word_mechanics",
        status="pass" if not cross_ref_error_hits else "fail",
        severity="info" if not cross_ref_error_hits else "P0",
        note="未检测到书签 / 交叉引用错误提示。"
        if not cross_ref_error_hits
        else "检测到交叉引用错误提示，需优先修复书签或域错误。",
        source_file=source_file,
        template_source=template_source,
        evidence={
            "error_count": len(cross_ref_error_hits),
            "examples": cross_ref_error_hits[:10],
        },
        needs_manual_confirmation=bool(cross_ref_error_hits),
    )

    add_check(
        checks,
        findings,
        check_id="word.revisions_remaining",
        category="word_mechanics",
        status="pass" if revisions_count == 0 else "fail",
        severity="info" if revisions_count == 0 else "P0",
        note="未检测到修订记录。"
        if revisions_count == 0
        else "检测到未清理的修订记录；送审或提交前应先接受 / 拒绝修订。",
        source_file=source_file,
        template_source=template_source,
        evidence={
            "revision_count": revisions_count,
            "track_revisions_enabled": track_revisions_enabled,
        },
        needs_manual_confirmation=bool(revisions_count),
    )

    add_check(
        checks,
        findings,
        check_id="word.comments_remaining",
        category="word_mechanics",
        status="pass" if comments_count == 0 else "fail",
        severity="info" if comments_count == 0 else "P0",
        note="未检测到批注。"
        if comments_count == 0
        else "检测到未清理的批注；正式提交前应删除或解决所有批注。",
        source_file=source_file,
        template_source=template_source,
        evidence={"comments_count": comments_count},
        needs_manual_confirmation=bool(comments_count),
    )

    add_check(
        checks,
        findings,
        check_id="word.hidden_text_present",
        category="word_mechanics",
        status="pass" if hidden_count == 0 else "warn",
        severity="info" if hidden_count == 0 else "P1",
        note="未检测到隐藏文本。"
        if hidden_count == 0
        else "检测到隐藏文本或隐藏格式；需人工确认是否存在模板残留或送审风险。",
        source_file=source_file,
        template_source=template_source,
        evidence={"hidden_run_count": hidden_count},
        needs_manual_confirmation=bool(hidden_count),
    )

    add_check(
        checks,
        findings,
        check_id="layout.section_margins_consistency",
        category="layout",
        status="pass" if section_summary["unique_margin_signature_count"] <= 1 else "warn",
        severity="info" if section_summary["unique_margin_signature_count"] <= 1 else "P2",
        note="分节页边距签名一致。"
        if section_summary["unique_margin_signature_count"] <= 1
        else "检测到多个页边距 / 方向签名；需结合模板人工确认是否为合理分节。",
        source_file=source_file,
        template_source=template_source,
        evidence=section_summary,
        needs_manual_confirmation=True,
    )

    add_check(
        checks,
        findings,
        check_id="layout.header_footer_refs_present",
        category="layout",
        status="info",
        severity="info",
        note="已统计各节页眉页脚引用数量，供后续核查页码和盲审版本使用。",
        source_file=source_file,
        template_source=template_source,
        evidence={
            "section_count": section_summary["section_count"],
            "sections": section_summary["sections"],
        },
        needs_manual_confirmation=True,
    )

    add_check(
        checks,
        findings,
        check_id="captions.figure_numbering",
        category="captions",
        status="pass" if not duplicate_figures else "fail",
        severity="info" if not duplicate_figures else "P0",
        note="未检测到重复图号。"
        if not duplicate_figures
        else "检测到重复图号；需立即修复 caption 编号与正文互引。",
        source_file=source_file,
        template_source=template_source,
        evidence={
            "figure_caption_count": len(figure_captions),
            "duplicates": duplicate_figures,
        },
        needs_manual_confirmation=bool(duplicate_figures),
    )

    add_check(
        checks,
        findings,
        check_id="captions.table_numbering",
        category="captions",
        status="pass" if not duplicate_tables else "fail",
        severity="info" if not duplicate_tables else "P0",
        note="未检测到重复表号。"
        if not duplicate_tables
        else "检测到重复表号；需立即修复 caption 编号与正文互引。",
        source_file=source_file,
        template_source=template_source,
        evidence={
            "table_caption_count": len(table_captions),
            "duplicates": duplicate_tables,
        },
        needs_manual_confirmation=bool(duplicate_tables),
    )

    equation_status = "pass"
    equation_severity = "info"
    equation_note = "已检测到公式编号，且未发现重复。"
    if duplicate_equations:
        equation_status = "fail"
        equation_severity = "P0"
        equation_note = "检测到重复公式编号；需优先修复公式编号与互引。"
    elif math_paragraph_count > 0 and not equation_numbers:
        equation_status = "warn"
        equation_severity = "P1"
        equation_note = "检测到公式对象，但未识别到公式编号；需人工确认是否漏编号或编号格式异常。"
    elif math_paragraph_count == 0 and not equation_numbers:
        equation_status = "info"
        equation_severity = "info"
        equation_note = "未检测到公式对象或公式编号。"

    add_check(
        checks,
        findings,
        check_id="equations.numbering",
        category="equations",
        status=equation_status,
        severity=equation_severity,
        note=equation_note,
        source_file=source_file,
        template_source=template_source,
        evidence={
            "math_paragraph_count": math_paragraph_count,
            "equation_number_count": len(equation_numbers),
            "duplicates": duplicate_equations,
        },
        needs_manual_confirmation=equation_status in {"warn", "fail"},
    )

    add_check(
        checks,
        findings,
        check_id="notes.footnotes_endnotes_usage",
        category="references",
        status="info",
        severity="info",
        note="已统计脚注 / 尾注数量；如学校限制注释体例，需结合模板人工判断。",
        source_file=source_file,
        template_source=template_source,
        evidence={
            "footnotes_count": footnotes_count,
            "endnotes_count": endnotes_count,
        },
        needs_manual_confirmation=(footnotes_count + endnotes_count) > 0,
    )

    metadata_note = "已提取文档元数据。"
    metadata_status = "info"
    metadata_severity = "info"
    if args.blind_review and any(metadata.values()):
        metadata_note = "盲审模式下检测到作者或最后修改者元数据；导出提交前需人工确认是否需要清理。"
        metadata_status = "warn"
        metadata_severity = "P1"

    add_check(
        checks,
        findings,
        check_id="metadata.author_fields",
        category="metadata",
        status=metadata_status,
        severity=metadata_severity,
        note=metadata_note,
        source_file=source_file,
        template_source=template_source,
        evidence=metadata,
        needs_manual_confirmation=args.blind_review and any(metadata.values()),
    )

    if args.blind_review:
        add_check(
            checks,
            findings,
            check_id="blind_review.acknowledgements_present",
            category="submission",
            status="warn" if detected_sections["acknowledgements"] else "pass",
            severity="P1" if detected_sections["acknowledgements"] else "info",
            note="盲审模式下检测到致谢标题；需确认盲审版是否应移除或替换。"
            if detected_sections["acknowledgements"]
            else "盲审模式下未检测到致谢标题。",
            source_file=source_file,
            template_source=template_source,
            evidence={"acknowledgements": detected_sections["acknowledgements"]},
            needs_manual_confirmation=True,
        )

    findings_counter = Counter(item["status"] for item in findings)
    payload = {
        "paper_id": paper_id,
        "kind": "formal_findings",
        "source_docx": source_file,
        "template_source": template_source,
        "blind_review": args.blind_review,
        "summary": {
            "check_count": len(checks),
            "finding_count": len(findings),
            "fail_count": findings_counter.get("fail", 0),
            "warn_count": findings_counter.get("warn", 0),
            "info_count": sum(1 for item in checks if item["status"] == "info"),
            "pass_count": sum(1 for item in checks if item["status"] == "pass"),
        },
        "items": findings,
        "checks": checks,
    }

    manifest = {
        "source_docx": source_file,
        "paper_id": paper_id,
        "template_source": template_source,
        "blind_review": args.blind_review,
        "detected_sections": detected_sections,
        "declaration_hits": declaration_hits,
        "keyword_hits": keyword_hits,
        "field_code_summary": {
            "toc_field_count": toc_field_count,
            "page_field_count": page_field_count,
            "field_instruction_count": len(field_instructions),
        },
        "document_metrics": {
            "paragraph_count": len(paragraphs),
            "heading_count": heading_count,
            "math_paragraph_count": math_paragraph_count,
            "figure_caption_count": len(figure_captions),
            "table_caption_count": len(table_captions),
            "equation_number_count": len(equation_numbers),
            "comments_count": comments_count,
            "revisions_count": revisions_count,
            "hidden_run_count": hidden_count,
            "footnotes_count": footnotes_count,
            "endnotes_count": endnotes_count,
            "track_revisions_enabled": track_revisions_enabled,
        },
        "layout": section_summary,
        "metadata": metadata,
        "checks": checks,
        "findings": findings,
    }

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    objects_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Checked DOCX formal rules for {docx_path}")
    print(f"Checks: {len(checks)} | warnings: {findings_counter.get('warn', 0)} | failures: {findings_counter.get('fail', 0)}")
    print(f"Manifest: {manifest_path}")
    print(f"Findings: {objects_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
