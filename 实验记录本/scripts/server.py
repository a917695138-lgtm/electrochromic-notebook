import http.server
import json
import os
import socketserver
import subprocess

PORT = 8765
PROJECT_DIR = r"D:\Users\ao\Documents\电致变色\实验记录本"
ROOT_DIR = r"D:\Users\ao\Documents\电致变色"
PYTHON = r"C:\Program Files\Python39\python.exe"
POWERSHELL = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"


class NotebookHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PROJECT_DIR, **kwargs)

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

            folder_path = os.path.realpath(os.path.join(PROJECT_DIR, folder))
            target_path = os.path.realpath(os.path.join(folder_path, name))
            project_path = os.path.realpath(PROJECT_DIR)
            if not target_path.startswith(project_path + os.sep):
                raise ValueError("Path escapes notebook directory")

            os.makedirs(folder_path, exist_ok=True)
            with open(target_path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(content)

            self.sync_notebook()
            self.send_json({"ok": True, "path": f"{folder}/{name}"})
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

            target_path = os.path.realpath(os.path.join(PROJECT_DIR, folder, name))
            project_path = os.path.realpath(PROJECT_DIR)
            if not target_path.startswith(project_path + os.sep):
                raise ValueError("Path escapes notebook directory")
            if os.path.exists(target_path):
                os.remove(target_path)

            self.sync_notebook()
            self.send_json({"ok": True, "path": f"{folder}/{name}"})
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=500)

    def safe_segment(self, value):
        value = str(value).replace("\\", "/").strip("/")
        if not value or "/" in value or ".." in value:
            return ""
        return value

    def sync_notebook(self):
        subprocess.run(
            [PYTHON, os.path.join(PROJECT_DIR, "scripts", "sync-data.py")],
            cwd=PROJECT_DIR,
            check=True,
        )
        src = os.path.join(PROJECT_DIR, "index.html")
        dst = os.path.join(PROJECT_DIR, "实验记录本.html")
        with open(src, "r", encoding="utf-8") as source, open(dst, "w", encoding="utf-8", newline="\n") as target:
            target.write(source.read())

        subprocess.Popen(
            [
                POWERSHELL,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                os.path.join(PROJECT_DIR, "scripts", "push-to-github.ps1"),
                "-NoPause",
            ],
            cwd=ROOT_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print(f"[{self.client_address[0]}] {format % args}")


if __name__ == "__main__":
    with socketserver.TCPServer(("0.0.0.0", PORT), NotebookHandler) as httpd:
        print("实验记录本服务器已启动")
        print(f"本地访问: http://localhost:{PORT}/实验记录本.html")
        print("保存记录后会自动同步并推送到 GitHub Pages")
        print("按 Ctrl+C 停止")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")
