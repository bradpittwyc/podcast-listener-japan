"""Capture exact screenshots of the startup screen for tablet and phone viewports."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = Path(r"C:\Users\Administrator\.gemini\antigravity\brain\d6ed2b18-7017-4428-a3ae-fbdf70a96c48")

def capture():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        
        # 1. Tablet Viewport (1024x768)
        page_tablet = browser.new_page(viewport={"width": 1024, "height": 768})
        page_tablet.goto("http://127.0.0.1:8557/")
        page_tablet.wait_for_timeout(2000)
        tablet_path = ARTIFACT_DIR / "tablet_splash.png"
        page_tablet.screenshot(path=str(tablet_path))
        print(f"Saved tablet screenshot to {tablet_path}")
        page_tablet.close()

        # 2. Phone Viewport (390x844)
        page_phone = browser.new_page(viewport={"width": 390, "height": 844}, has_touch=True)
        page_phone.goto("http://127.0.0.1:8557/")
        page_phone.wait_for_timeout(2000)
        phone_path = ARTIFACT_DIR / "phone_splash.png"
        page_phone.screenshot(path=str(phone_path))
        print(f"Saved phone screenshot to {phone_path}")
        page_phone.close()

        browser.close()

if __name__ == "__main__":
    capture()
