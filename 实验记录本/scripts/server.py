import http.server
import socketserver

PORT = 8765
PROJECT_DIR = r"D:\Users\ao\Documents\电致变色\实验记录本"

class NotebookHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PROJECT_DIR, **kwargs)

    def log_message(self, format, *args):
        print(f"[{self.client_address[0]}] {format % args}")

if __name__ == '__main__':
    with socketserver.TCPServer(("0.0.0.0", PORT), NotebookHandler) as httpd:
        print(f"实验记录本服务器已启动")
        print(f"本地访问: http://localhost:{PORT}/实验记录本.html")
        print("按 Ctrl+C 停止")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")
