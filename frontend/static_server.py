from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path


class SpaHandler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        path = Path(self.translate_path(self.path))
        if not path.exists() or path.is_dir():
            self.path = "/index.html"
        super().do_GET()


if __name__ == "__main__":
    os.chdir("/srv/dist")
    ThreadingHTTPServer(("0.0.0.0", 80), SpaHandler).serve_forever()
