"""
Desktop App Entry Point for Podcast Learner Japan
"""
import sys
import os
import time
import socket
import threading
import urllib.request
import webbrowser

# Fix PyInstaller --windowed mode where sys.stdout/stderr and sys.__stdout__/__stderr__ are None
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

def open_browser(port):
    time.sleep(1.0)
    webbrowser.open(f"http://127.0.0.1:{port}")

def main():
    default_port = 8557
    
    # 1. If app is already running on default_port, open browser and exit gracefully
    if is_our_app_running(default_port):
        webbrowser.open(f"http://127.0.0.1:{default_port}")
        sys.exit(0)
        
    # 2. Find an available port starting from default_port
    port = default_port
    while is_port_in_use(port):
        port += 1
        if port > default_port + 10:
            break
            
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    # Custom log config that uses standard logging.Formatter to avoid uvicorn.logging.DefaultFormatter sys.stdout.isatty() crash in PyInstaller --windowed
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

if __name__ == "__main__":
    main()
