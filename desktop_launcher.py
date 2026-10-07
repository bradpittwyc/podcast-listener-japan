"""
Desktop App Entry Point for Podcast Learner Japan (Native Windows Desktop App)
"""
import sys
import os
import time
import socket
import threading
import urllib.request

# Fix PyInstaller --windowed mode stdout/stderr stream wrappers
class NullStream:
    def write(self, data):
        pass
    def flush(self):
        pass
    def isatty(self):
        return False

for stream_name in ('stdout', 'stderr', '__stdout__', '__stderr__'):
    if getattr(sys, stream_name, None) is None:
        setattr(sys, stream_name, NullStream())

import uvicorn
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView

# Ensure working directory is set to the directory containing the executable / script
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(os.path.abspath(sys.executable)))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app import app

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def is_our_app_running(port):
    try:
        url = f"http://127.0.0.1:{port}/api/version"
        req = urllib.request.Request(url, headers={"User-Agent": "PodcastLearnerJapan-Launcher"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            return resp.status == 200
    except Exception:
        return False

def start_server(port):
    custom_log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s] %(message)s",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.NullHandler",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": "ERROR"},
            "uvicorn.error": {"level": "ERROR"},
            "uvicorn.access": {"handlers": ["default"], "level": "ERROR"},
        },
    }
    uvicorn.run(app, host="127.0.0.1", port=port, log_config=custom_log_config)

def main():
    default_port = 8557
    port = default_port
    
    # 1. Start uvicorn server in a daemon thread if not already running
    if not is_our_app_running(default_port):
        while is_port_in_use(port):
            port += 1
            if port > default_port + 10:
                break
        t = threading.Thread(target=start_server, args=(port,), daemon=True)
        t.start()
        time.sleep(0.6)

    # 2. Launch Native Windows Desktop Window using PyQt5 QWebEngineView
    q_app = QApplication(sys.argv)
    q_app.setApplicationName("Podcast Learner Japan")
    
    view = QWebEngineView()
    view.setWindowTitle("Podcast Learner Japan")
    view.resize(1280, 820)
    view.load(QUrl(f"http://127.0.0.1:{port}"))
    view.show()
    
    sys.exit(q_app.exec_())

if __name__ == "__main__":
    main()
