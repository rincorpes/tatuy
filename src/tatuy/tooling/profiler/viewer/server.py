from __future__ import annotations

import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def serve(
    profile_path: str | Path,
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
) -> None:
    profile_path = Path(profile_path).resolve()

    if not profile_path.exists():
        raise FileNotFoundError(profile_path)

    static_dir = Path(__file__).parent / "static"

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path == "/profile.json":
                self.send_response(200)
                self.send_header(
                    "Content-Type",
                    "application/json",
                )
                self.end_headers()

                self.wfile.write(profile_path.read_bytes())
                return

            super().do_GET()

    handler = functools.partial(
        Handler,
        directory=str(static_dir),
    )

    server = ThreadingHTTPServer(
        (host, port),
        handler,
    )

    print(f"Tatuy profiler viewer: " f"http://{host}:{port}")

    server.serve_forever()
