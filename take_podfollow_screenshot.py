import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = Path(r"C:\Users\Administrator\.gemini\antigravity\brain\d6ed2b18-7017-4428-a3ae-fbdf70a96c48")

def capture():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto("http://127.0.0.1:8557/podfollow")
        page.wait_for_timeout(3500)
        img_path = ARTIFACT_DIR / "podfollow_japan_preview.png"
        page.screenshot(path=str(img_path))
        print(f"Captured screenshot to {img_path}")
        browser.close()

if __name__ == "__main__":
    capture()
