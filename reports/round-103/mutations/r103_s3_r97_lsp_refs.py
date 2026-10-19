#!/usr/bin/env python3
"""r103 S3-R97 — LSP references query for `ready_ticks` (semantic dead-field proof).

Starts Godot's built-in GDScript LSP (godot --headless --lsp-port <p>) against a
scratch project carrying the COMMITTED r97 fixture, opens
res://r97_scene_marker.gd, and asks textDocument/references at the declaration
position of `ready_ticks` (line 3, col 5 — 0-based). A dead field returns no
reference outside the file's own decl+increment.

Bounded: 45 s wall clock, no project mutation, read-only w.r.t. the repo.
"""
import hashlib
import json
import socket
import subprocess
import sys
import time
from pathlib import Path

SCRATCH = Path(sys.argv[1] if len(sys.argv) > 1 else "/var/tmp/r103c-S3/s3r97/committed")
FILE = "res://r97_scene_marker.gd"
PORT = int(sys.argv[2] if len(sys.argv) > 2 else 6099)
SYMBOL = sys.argv[3] if len(sys.argv) > 3 else "ready_ticks"
BOUND = 45


class LSP:
    def __init__(self, port):
        self.sock = socket.create_connection(("127.0.0.1", port), timeout=10)
        self.buf = b""
        self.seq = 0

    def send(self, method, params, notify=False):
        msg = {"jsonrpc": "2.0", "method": method, "params": params}
        if not notify:
            self.seq += 1
            msg["id"] = self.seq
        body = json.dumps(msg).encode()
        self.sock.sendall(b"Content-Length: %d\r\n\r\n" % len(body) + body)
        return None if notify else self.seq

    def _read_exact(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise EOFError("lsp closed")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def recv(self):
        header = b""
        while b"\r\n\r\n" not in header:
            header += self._read_exact(1)
        length = int(dict(
            line.split(b": ", 1) for line in header.split(b"\r\n") if b": " in line
        )[b"Content-Length"])
        return json.loads(self._read_exact(length).decode())


def wait_for(port, bound_s):
    deadline = time.time() + bound_s
    while time.time() < deadline:
        try:
            s = socket.create_connection(("127.0.0.1", port), timeout=1)
            s.close()
            return True
        except OSError:
            time.sleep(0.4)
    return False


def main():
    text = (SCRATCH / "r97_scene_marker.gd").read_text()
    lines = text.splitlines()
    decl = next((i for i, l in enumerate(lines)
                 if l.startswith(f"var {SYMBOL}") or l.startswith(f"@export var {SYMBOL}")), None)
    if decl is None:
        print(json.dumps({"error": f"{SYMBOL} declaration not found", "file": str(SCRATCH)}))
        return 1
    col = lines[decl].index(SYMBOL) + 2
    proc = subprocess.Popen(["godot", "--headless", "--editor", "--path", str(SCRATCH),
                             "--lsp-port", str(PORT)],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    result = {"scratch": str(SCRATCH), "port": PORT, "symbol": SYMBOL,
              "decl_line_0based": decl, "decl_col": col,
              "fixture_sha256": hashlib.sha256(text.encode()).hexdigest(),
              "_fixture_source_text": text, "source_bytes": len(text)}
    try:
        if not wait_for(PORT, 20):
            result["error"] = "lsp port never opened"
            print(json.dumps(result, indent=2))
            return 1
        lsp = LSP(PORT)
        lsp.send("initialize", {
            "processId": None,
            "rootUri": SCRATCH.as_uri(),
            "workspaceFolders": [{"uri": SCRATCH.as_uri(), "name": "r103s3r97"}],
            "capabilities": {"textDocument": {"references": {"dynamicRegistration": False}}},
        })
        init = lsp.recv()
        result["server_capabilities"] = sorted((init.get("result") or {}).get("capabilities", {}))
        lsp.send("initialized", {}, notify=True)
        lsp.send("textDocument/didOpen", {"textDocument": {
            "uri": SCRATCH.as_uri() + "/" + FILE.removeprefix("res://"),
            "languageId": "gdscript", "version": 1, "text": text}})
        time.sleep(2.0)
        rid = lsp.send("textDocument/references", {
            "textDocument": {"uri": SCRATCH.as_uri() + "/" + FILE.removeprefix("res://")},
            "position": {"line": decl, "character": col},
            "context": {"includeDeclaration": True}})
        deadline = time.time() + 20
        while time.time() < deadline:
            msg = lsp.recv()
            if msg.get("id") == rid:
                refs = msg.get("result") or []
                result["reference_count"] = len(refs)
                result["references"] = [
                    {k: v for k, v in r.items() if k in ("uri", "range")} for r in refs]
                breaks = [r for r in refs
                          if not r["uri"].endswith("r97_scene_marker.gd")]
                result["references_outside_marker_file"] = len(breaks)
                result["_file_lines"] = len(lines)
                print(json.dumps(result, indent=2))
                return 0
            if msg.get("method") == "window/showMessage":
                result.setdefault("server_messages", []).append(msg.get("params"))
        result["error"] = "no references response inside 20s"
        print(json.dumps(result, indent=2))
        return 1
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    sys.exit(main())
