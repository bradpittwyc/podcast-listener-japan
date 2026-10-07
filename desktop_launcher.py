"""
Desktop App Entry Point for Podcast Learner Japan
"""
import sys
import os
import time
import threading
import webbrowser
import uvicorn
from app import app

def open_browser(port=8557):
    time.sleep(1.2)
    webbrowser.open(f"http://127.0.0.1:{port}")

def main():
    port = 8557
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    print(f"Starting Podcast Learner Japan on http://127.0.0.1:{port} ...")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")

if __name__ == "__main__":
    main()
