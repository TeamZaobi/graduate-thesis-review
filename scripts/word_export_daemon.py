#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import socketserver
import subprocess
import sys
import threading
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKER_SCRIPT = ROOT / "scripts" / "word_export_worker.jxa"
DEFAULT_SOCKET_PATH = Path.home() / "Library" / "Caches" / "graduate-thesis-review" / "word-export.sock"


class WordWorkerBridge:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._proc = subprocess.Popen(
            [
                "/usr/bin/osascript",
                "-l",
                "JavaScript",
                str(WORKER_SCRIPT),
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

    def request(self, payload: dict) -> dict:
        with self._lock:
            if self._proc.stdin is None or self._proc.stdout is None:
                raise RuntimeError("Word export worker pipes are unavailable")
            if self._proc.poll() is not None:
                stderr = self._proc.stderr.read().strip() if self._proc.stderr else ""
                raise RuntimeError(
                    f"Word export worker exited unexpectedly: rc={self._proc.returncode} {stderr}"
                )

            self._proc.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
            self._proc.stdin.flush()
            line = self._proc.stdout.readline()
            if not line:
                stderr = self._proc.stderr.read().strip() if self._proc.stderr else ""
                raise RuntimeError(
                    "Word export worker produced no response. "
                    + (stderr or "worker stdout closed")
                )
            return json.loads(line)

    def close(self) -> None:
        try:
            self.request({"command": "stop"})
        except Exception:
            pass
        finally:
            if self._proc.poll() is None:
                self._proc.terminate()
                try:
                    self._proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self._proc.kill()


class ThreadedUnixStreamServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True


class RequestHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        raw = self.rfile.readline()
        if not raw:
            return
        payload: dict | None = None
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            response = {"result": "error", "error": f"Invalid JSON: {exc}"}
        else:
            try:
                response = self.server.bridge.request(payload)  # type: ignore[attr-defined]
            except Exception as exc:  # noqa: BLE001
                response = {"result": "error", "error": str(exc)}
        self.wfile.write((json.dumps(response, ensure_ascii=False) + "\n").encode("utf-8"))
        if payload and payload.get("command") == "stop" and response.get("result") == "success":
            threading.Thread(target=self.server.shutdown, daemon=True).start()


def cleanup_socket(path: Path) -> None:
    if path.exists():
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Persistent Word-native PDF export daemon for thesis review."
    )
    parser.add_argument(
        "--socket",
        default=str(DEFAULT_SOCKET_PATH),
        help="Unix socket path for client requests",
    )
    args = parser.parse_args()

    socket_path = Path(args.socket).expanduser().resolve()
    socket_path.parent.mkdir(parents=True, exist_ok=True)
    cleanup_socket(socket_path)

    bridge = WordWorkerBridge()
    server = ThreadedUnixStreamServer(str(socket_path), RequestHandler)
    server.bridge = bridge  # type: ignore[attr-defined]

    def shutdown(*_args: object) -> None:
        server.shutdown()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    try:
        server.serve_forever()
    finally:
        server.server_close()
        bridge.close()
        cleanup_socket(socket_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
