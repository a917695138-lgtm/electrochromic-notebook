import http.server
import json
import socketserver
import subprocess
import threading
from pathlib import Path


PORT = 8765
PROJECT_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = PROJECT_DIR.parent
POWERSHELL = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
SYNC_LOCK = threading.Lock()


class NotebookHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJECT_DIR), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_POST(self):
        if self.path == "/api/save":
            self.save_record()
            return
        if self.path == "/api/delete":
            self.delete_record()
            return
        self.send_error(404, "Not found")

    def save_record(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            folder = self.safe_segment(payload.get("folder", ""))
            name = self.safe_segment(payload.get("name", ""))
            content = payload.get("content", "")
            if not folder or not name.endswith(".md") or not isinstance(content, str):
                raise ValueError("Invalid record payload")

            folder_path = (PROJECT_DIR / folder).resolve()
            target_path = (folder_path / name).resolve()
            if not self.is_inside_project(target_path):
                raise ValueError("Path escapes notebook directory")

            folder_path.mkdir(parents=True, exist_ok=True)
            with target_path.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write(content)

            result = self.sync_notebook()
            self.send_json({"ok": True, "path": f"{folder}/{name}", **result})
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=500)

    def delete_record(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            folder = self.safe_segment(payload.get("folder", ""))
            name = self.safe_segment(payload.get("name", ""))
            if not folder or not name.endswith(".md"):
                raise ValueError("Invalid delete payload")

            target_path = (PROJECT_DIR / folder / name).resolve()
            if not self.is_inside_project(target_path):
                raise ValueError("Path escapes notebook directory")
            if target_path.exists():
                target_path.unlink()

            result = self.sync_notebook()
            self.send_json({"ok": True, "path": f"{folder}/{name}", **result})
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=500)

    def safe_segment(self, value):
        value = str(value).replace("\\", "/").strip("/")
        if not value or "/" in value or ".." in value:
            return ""
        return value

    def is_inside_project(self, path):
        try:
            path.relative_to(PROJECT_DIR)
            return True
        except ValueError:
            return False

    def sync_notebook(self):
        with SYNC_LOCK:
            result = subprocess.run(
                [
                    POWERSHELL,
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(PROJECT_DIR / "scripts" / "push-to-github.ps1"),
                    "-NoPause",
                ],
                cwd=str(ROOT_DIR),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if result.returncode != 0:
                details = (result.stdout + "\n" + result.stderr).strip()
                raise RuntimeError(details or "GitHub Pages sync failed")
            return {"synced": True, "message": "Synced and pushed to GitHub Pages"}

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print(f"[{self.client_address[0]}] {format % args}", flush=True)


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    with ReusableTCPServer(("127.0.0.1", PORT), NotebookHandler) as httpd:
        print("Notebook server started", flush=True)
        print(f"Local URL: http://127.0.0.1:{PORT}/index.html", flush=True)
        print("Save/delete writes Markdown files and syncs to GitHub Pages", flush=True)
        print("Press Ctrl+C to stop", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped", flush=True)
