import http.server
import socketserver
import socket
import os

PORT = 1000

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    local_ip = get_local_ip()

    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print("Сервер запущен")
        print(f"Локально: http://127.0.0.1:{PORT}")
        print(f"По сети:  http://{local_ip}:{PORT}")
        print("Чтобы остановить сервер, нажми Ctrl+C")
        httpd.serve_forever()

if __name__ == "__main__":
    main()
