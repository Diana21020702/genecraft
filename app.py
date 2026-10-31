"""Dependency-free local web UI for GeneCraft."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from genetics import make_cross

STATIC = Path(__file__).parent / "static"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        files = {"/": ("index.html", "text/html"), "/style.css": ("style.css", "text/css"),
                 "/app.js": ("app.js", "text/javascript")}
        if self.path not in files:
            return self.respond(404, {"error": "Nenalezeno"})
        filename, content_type = files[self.path]
        data = (STATIC / filename).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != "/api/cross":
            return self.respond(404, {"error": "Nenalezeno"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size < 1 or size > 2048:
                return self.respond(413, {"error": "Neplatná velikost požadavku"})
            req = json.loads(self.rfile.read(size))
            result = make_cross(req["parent1"], req["parent2"])
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            return self.respond(400, {"error": str(exc)})
        self.respond(200, result)

    def respond(self, status, body):
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    parser = argparse.ArgumentParser(description="Interaktivní genetický simulátor")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as server:
        print(f"GeneCraft běží na http://127.0.0.1:{args.port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nUkončeno")


if __name__ == "__main__":
    main()
