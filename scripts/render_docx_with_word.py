#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORD_EXPORT_SCRIPT = ROOT / "scripts" / "export_docx_to_pdf_word.jxa"
WORD_EXPORT_DAEMON = ROOT / "scripts" / "word_export_daemon.py"
DEFAULT_DAEMON_SOCKET = Path.home() / "Library" / "Caches" / "graduate-thesis-review" / "word-export.sock"


def require_command(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise RuntimeError(f"Missing required command: {name}")
    return path


def run_word_export_direct(docx_path: Path, pdf_path: Path, keep_word_active: bool) -> dict:
    if sys.platform != "darwin":
        raise RuntimeError("Word-native export is currently supported only on macOS")
    if not Path("/Applications/Microsoft Word.app").exists():
        raise RuntimeError("Microsoft Word.app is not installed in /Applications")

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            "/usr/bin/osascript",
            "-l",
            "JavaScript",
            str(WORD_EXPORT_SCRIPT),
            str(docx_path),
            str(pdf_path),
            str(keep_word_active).lower(),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    lines = [
        line.strip()
        for line in (result.stdout.splitlines() + result.stderr.splitlines())
        if line.strip()
    ]
    payload: dict | None = None
    for line in reversed(lines):
        try:
            candidate = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict) and "result" in candidate:
            payload = candidate
            break

    if result.returncode != 0 or payload is None or payload.get("result") != "success":
        detail = payload.get("error") if isinstance(payload, dict) else "\n".join(lines)
        raise RuntimeError(f"Word export failed: {detail}")

    if not pdf_path.exists():
        raise RuntimeError(f"Word export reported success but PDF was not created: {pdf_path}")

    return payload


def daemon_request(socket_path: Path, payload: dict) -> dict:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.connect(str(socket_path))
        client.sendall((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
        chunks: list[bytes] = []
        while True:
            data = client.recv(4096)
            if not data:
                break
            chunks.append(data)
            if b"\n" in data:
                break

    if not chunks:
        raise RuntimeError("Word export daemon returned no response")
    line = b"".join(chunks).split(b"\n", 1)[0].decode("utf-8")
    return json.loads(line)


def ensure_word_export_daemon(socket_path: Path) -> None:
    socket_path.parent.mkdir(parents=True, exist_ok=True)

    if socket_path.exists():
        try:
            response = daemon_request(socket_path, {"command": "ping"})
        except Exception:
            try:
                socket_path.unlink()
            except FileNotFoundError:
                pass
        else:
            if response.get("result") == "success":
                return
            try:
                socket_path.unlink()
            except FileNotFoundError:
                pass

    log_path = socket_path.with_suffix(".log")
    with log_path.open("a", encoding="utf-8") as handle:
        subprocess.Popen(
            [
                sys.executable,
                str(WORD_EXPORT_DAEMON),
                "--socket",
                str(socket_path),
            ],
            stdout=handle,
            stderr=handle,
            start_new_session=True,
        )

    deadline = time.time() + 20
    while time.time() < deadline:
        if socket_path.exists():
            try:
                response = daemon_request(socket_path, {"command": "ping"})
            except Exception:
                time.sleep(0.2)
                continue
            if response.get("result") == "success":
                return
        time.sleep(0.2)

    raise RuntimeError(
        f"Timed out waiting for word export daemon to start. See log: {log_path}"
    )


def run_word_export(
    docx_path: Path,
    pdf_path: Path,
    keep_word_active: bool,
    use_daemon: bool,
    daemon_socket: Path,
) -> dict:
    if use_daemon:
        ensure_word_export_daemon(daemon_socket)
        payload = daemon_request(
            daemon_socket,
            {
                "command": "export",
                "input_path": str(docx_path),
                "output_path": str(pdf_path),
            },
        )
        if payload.get("result") != "success":
            raise RuntimeError(f"Word export daemon failed: {payload.get('error')}")
        if not pdf_path.exists():
            raise RuntimeError(
                f"Word export daemon reported success but PDF was not created: {pdf_path}"
            )
        return payload

    return run_word_export_direct(
        docx_path=docx_path,
        pdf_path=pdf_path,
        keep_word_active=keep_word_active,
    )


def rasterize_pdf(pdf_path: Path, output_dir: Path, dpi: int) -> list[Path]:
    gs = require_command("gs")
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = pdf_path.stem
    for existing in output_dir.glob(f"{stem}-page-*.png"):
        existing.unlink()

    output_pattern = output_dir / f"{stem}-page-%03d.png"
    result = subprocess.run(
        [
            gs,
            "-q",
            "-dSAFER",
            "-dBATCH",
            "-dNOPAUSE",
            "-sDEVICE=png16m",
            f"-r{dpi}",
            "-dTextAlphaBits=4",
            "-dGraphicsAlphaBits=4",
            f"-sOutputFile={output_pattern}",
            str(pdf_path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "Ghostscript rasterization failed: "
            + (result.stderr.strip() or result.stdout.strip() or "unknown error")
        )

    page_files = sorted(output_dir.glob(f"{stem}-page-*.png"))
    if not page_files:
        raise RuntimeError(f"No page renders were generated for {pdf_path}")
    return page_files


def update_review_manifest(
    review_manifest_path: Path,
    docx_path: Path,
    pdf_path: Path,
    page_renders_dir: Path,
    dpi: int,
) -> None:
    if not review_manifest_path.exists():
        return

    payload = json.loads(review_manifest_path.read_text(encoding="utf-8"))
    review_object = payload.setdefault("review_object", {})
    visual_truth_source = review_object.setdefault("visual_truth_source", {})
    visual_truth_source.update(
        {
            "path": str(pdf_path),
            "authority_type": "word_native_pdf_export",
            "renderer": "word_native",
            "page_renders_dir": str(page_renders_dir),
            "fallback_pdf": str(pdf_path),
            "source_docx": str(docx_path),
            "dpi": dpi,
        }
    )
    review_object["derived_pdf_source"] = str(pdf_path)
    review_manifest_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_manifest(
    manifest_path: Path,
    docx_path: Path,
    pdf_path: Path,
    page_renders_dir: Path,
    dpi: int,
    page_files: list[Path],
) -> None:
    manifest = {
        "kind": "page_renders",
        "source_docx": str(docx_path),
        "output_pdf": str(pdf_path),
        "render_engine": "word_native",
        "render_authority": "word_native_pdf_export",
        "dpi": dpi,
        "page_renders_dir": str(page_renders_dir),
        "page_count": len(page_files),
        "pages": [
            {
                "page": index,
                "asset_type": "page_render_capture",
                "output_path": str(path),
                "filename": path.name,
            }
            for index, path in enumerate(page_files, start=1)
        ],
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Render a DOCX through Microsoft Word's native PDF export, then "
            "rasterize the resulting PDF into page images."
        )
    )
    parser.add_argument("--docx", required=True, help="Path to source DOCX")
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument(
        "--paper-dir",
        help=(
            "Paper workspace root. Outputs PDF and page renders to "
            "assets/page_renders/ and updates reviews/review_version_manifest.json"
        ),
    )
    target_group.add_argument(
        "--output-dir",
        help="Directory where the PDF snapshot, page renders, and manifest will be written",
    )
    parser.add_argument("--pdf-path", help="Optional explicit output PDF path")
    parser.add_argument("--manifest", help="Optional manifest path")
    parser.add_argument("--dpi", type=int, default=144, help="Rasterization DPI for PNG pages")
    parser.add_argument(
        "--keep-word-active",
        action="store_true",
        help="Do not quit Microsoft Word after export when using direct mode",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting an existing PDF snapshot",
    )
    parser.add_argument(
        "--direct",
        action="store_true",
        help="Bypass the persistent daemon and export through a one-shot osascript call",
    )
    parser.add_argument(
        "--daemon-socket",
        default=str(DEFAULT_DAEMON_SOCKET),
        help="Unix socket path for the persistent Word export daemon",
    )
    args = parser.parse_args()

    docx_path = Path(args.docx).expanduser().resolve()
    if not docx_path.exists():
        print(f"Missing DOCX: {docx_path}", file=sys.stderr)
        return 1
    if docx_path.suffix.lower() != ".docx":
        print(f"Expected a .docx file: {docx_path}", file=sys.stderr)
        return 1
    if args.dpi < 72:
        print("DPI must be at least 72", file=sys.stderr)
        return 1

    paper_dir = Path(args.paper_dir).expanduser().resolve() if args.paper_dir else None
    if paper_dir is not None:
        output_dir = paper_dir / "assets" / "page_renders"
        default_pdf = output_dir / f"{docx_path.stem}.word-native.pdf"
        default_manifest = output_dir / "manifest.json"
        review_manifest_path = paper_dir / "reviews" / "review_version_manifest.json"
    else:
        output_dir = Path(args.output_dir).expanduser().resolve()
        default_pdf = output_dir / f"{docx_path.stem}.word-native.pdf"
        default_manifest = output_dir / "manifest.json"
        review_manifest_path = None

    pdf_path = Path(args.pdf_path).expanduser().resolve() if args.pdf_path else default_pdf
    manifest_path = (
        Path(args.manifest).expanduser().resolve() if args.manifest else default_manifest
    )
    daemon_socket = Path(args.daemon_socket).expanduser().resolve()

    output_dir.mkdir(parents=True, exist_ok=True)
    if pdf_path.exists() and not args.overwrite:
        print(
            f"Refusing to overwrite existing PDF without --overwrite: {pdf_path}",
            file=sys.stderr,
        )
        return 1

    export_payload = run_word_export(
        docx_path=docx_path,
        pdf_path=pdf_path,
        keep_word_active=args.keep_word_active,
        use_daemon=not args.direct,
        daemon_socket=daemon_socket,
    )
    page_files = rasterize_pdf(pdf_path=pdf_path, output_dir=output_dir, dpi=args.dpi)
    write_manifest(
        manifest_path=manifest_path,
        docx_path=docx_path,
        pdf_path=pdf_path,
        page_renders_dir=output_dir,
        dpi=args.dpi,
        page_files=page_files,
    )
    if review_manifest_path is not None:
        update_review_manifest(
            review_manifest_path=review_manifest_path,
            docx_path=docx_path,
            pdf_path=pdf_path,
            page_renders_dir=output_dir,
            dpi=args.dpi,
        )

    print(f"Rendered via Microsoft Word: {docx_path}")
    print(f"PDF snapshot: {pdf_path}")
    print(f"Page renders: {output_dir}")
    print(f"Manifest: {manifest_path}")
    print(f"Pages: {len(page_files)}")
    print(f"Renderer: {export_payload.get('renderer', 'word_native')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
