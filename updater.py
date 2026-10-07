"""
Automatic GitHub Release Updater for Podcast Learner Japan
"""
import os
import sys
import json
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

APP_VERSION = "1.0.0"
GITHUB_REPO = "bradpittwyc/podcast-listener-japan"
RELEASE_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

def parse_version(v_str: str):
    v = str(v_str or "0.0.0").lstrip("vV").strip()
    parts = []
    for p in v.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)

def check_for_updates():
    try:
        req = urllib.request.Request(
            RELEASE_API_URL,
            headers={"User-Agent": "PodcastLearnerJapan-Updater", "Accept": "application/vnd.github+json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status != 200:
                return {"has_update": False, "current_version": APP_VERSION, "error": f"HTTP {resp.status}"}
            data = json.loads(resp.read().decode("utf-8"))
            
        latest_tag = data.get("tag_name", "v1.0.0")
        latest_version = latest_tag.lstrip("vV")
        body = data.get("body", "")
        assets = data.get("assets", [])
        
        exe_asset = None
        for asset in assets:
            name = asset.get("name", "").lower()
            if name.endswith(".exe"):
                exe_asset = asset
                break
                
        download_url = exe_asset["browser_download_url"] if exe_asset else None
        has_update = parse_version(latest_version) > parse_version(APP_VERSION)
        
        return {
            "has_update": has_update,
            "current_version": APP_VERSION,
            "latest_version": latest_version,
            "tag_name": latest_tag,
            "download_url": download_url,
            "release_notes": body,
            "published_at": data.get("published_at", "")
        }
    except Exception as e:
        return {
            "has_update": False,
            "current_version": APP_VERSION,
            "error": str(e)
        }

def trigger_self_update(download_url: str):
    if not download_url:
        raise ValueError("未找到可供下载的更新文件 (.exe)")
        
    exe_path = Path(sys.executable if getattr(sys, 'frozen', False) else __file__).resolve()
    target_dir = exe_path.parent
    temp_new_exe = target_dir / "PodcastLearnerJapan_new.exe"
    bat_script = target_dir / "apply_update.bat"
    
    # 1. Download new executable
    req = urllib.request.Request(
        download_url,
        headers={"User-Agent": "PodcastLearnerJapan-Updater"}
    )
    with urllib.request.urlopen(req, timeout=120) as resp, open(temp_new_exe, "wb") as f:
        while True:
            chunk = resp.read(65536)
            if not chunk:
                break
            f.write(chunk)
            
    # 2. Write Windows batch updater script
    bat_content = f"""@echo off
timeout /t 2 /nobreak > NUL
copy /y "{temp_new_exe}" "{exe_path}"
del /f /q "{temp_new_exe}"
start "" "{exe_path}" --updated
del /f /q "%~f0"
"""
    bat_script.write_text(bat_content, encoding="gbk")
    
    # 3. Launch batch script asynchronously and exit current process
    subprocess.Popen(["cmd.exe", "/c", str(bat_script)], cwd=str(target_dir), creationflags=subprocess.CREATE_NEW_CONSOLE)
    sys.exit(0)
