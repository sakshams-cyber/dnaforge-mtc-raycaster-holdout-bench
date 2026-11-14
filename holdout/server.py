"""Zero-dependency web server for the Holdout UI (standard library only).

  python -m holdout serve --port 8000   ->  http://127.0.0.1:8000

GET  /                      the single-page UI (web/index.html)
GET  /web/<file>            static assets
GET  /api/health
GET  /api/demo?which=demo   analyze a bundled synthetic filing (demo | clean)
POST /api/analyze           body = raw file bytes (PDF or page-marked text); header X-Filename
GET  /api/report/<id>       a report analyzed earlier in this process
GET  /api/bench             bench_out/results.json, if `bench score` has been run
GET  /bench/results.png     the benchmark chart
"""
from __future__ import annotations

import json
import mimetypes
import os
import tempfile
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .pipeline import analyze_path

ROOT = Path(__file__).resolve().parent.parent
WEB = Path(os.environ.get("HOLDOUT_WEB_DIR", ROOT / "web"))
FIXTURES = Path(os.environ.get("HOLDOUT_FIXTURES_DIR", ROOT / "fixtures"))
BENCH = Path(os.environ.get("HOLDOUT_BENCH_DIR", "bench_out"))
MAX_UPLOAD = 200 * 1024 * 1024
REPORTS: dict[str, dict] = {}


class Handler(BaseHTTPRequestHandler):
    server_version = "Holdout/0.1"

    def log_message(self, fmt, *args):  # quieter logs
        if "/api/" in (args[0] if args else ""):
            super().log_message(fmt, *args)

    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code: int = 200):
        self._send(code, json.dumps(obj, default=str).encode(), "application/json")

    def _file(self, path: Path):
        if not path.exists() or not path.is_file():
            return self._json({"error": "not found"}, 404)
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        self._send(200, path.read_bytes(), ctype)

    def do_GET(self):
        u = urlparse(self.path)
        try:
            if u.path in ("/", "/index.html"):
                return self._file(WEB / "index.html")
            if u.path.startswith("/web/"):
                target = (WEB / u.path[5:]).resolve()
                if WEB.resolve() not in target.parents:
                    return self._json({"error": "bad path"}, 400)
                return self._file(target)
            if u.path == "/api/health":
                return self._json({"ok": True, "extractor": os.environ.get("HOLDOUT_LLM", "heuristic")})
            if u.path == "/api/demo":
                which = parse_qs(u.query).get("which", ["demo"])[0]
                name = {"demo": "synthetic_ind_demo.md", "clean": "synthetic_ind_clean.md"}.get(which)
                if not name:
                    return self._json({"error": "which must be demo or clean"}, 400)
                return self._report(analyze_path(FIXTURES / name))
            if u.path.startswith("/api/report/"):
                rid = u.path.rsplit("/", 1)[-1]
                return self._json(REPORTS[rid]) if rid in REPORTS else self._json({"error": "unknown id"}, 404)
            if u.path == "/api/bench":
                f = BENCH / "results.json"
                if not f.exists():
                    return self._json({"available": False})
                return self._json({"available": True, **json.loads(f.read_text())})
            if u.path == "/bench/results.png":
                return self._file(BENCH / "results.png")
            return self._json({"error": "not found"}, 404)
        except Exception as exc:
            traceback.print_exc()
            return self._json({"error": repr(exc)}, 500)

    def do_POST(self):
        u = urlparse(self.path)
        if u.path != "/api/analyze":
            return self._json({"error": "not found"}, 404)
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0 or n > MAX_UPLOAD:
            return self._json({"error": "empty or too large"}, 400)
        data = self.rfile.read(n)
        name = Path(self.headers.get("X-Filename") or "upload").name
        suffix = ".pdf" if data[:5] == b"%PDF-" else ".md"
        try:
            with tempfile.TemporaryDirectory() as tmp:
                p = Path(tmp) / (Path(name).stem + suffix)
                p.write_bytes(data)
                rep = analyze_path(p)
                rep.filename = name
            return self._report(rep)
        except Exception as exc:
            traceback.print_exc()
            return self._json({"error": repr(exc)}, 500)

    def _report(self, rep):
        d = rep.to_dict()
        REPORTS[rep.id] = d
        return self._json(d)


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"Holdout UI on http://{host}:{port}  (extractor: {os.environ.get('HOLDOUT_LLM', 'heuristic')})")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args()
    serve(a.host, a.port)
