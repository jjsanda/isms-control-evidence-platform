#!/usr/bin/env python3
"""Capture dashboard screenshots for the README with Playwright (headless Chromium).

Run indirectly via ``make screenshots`` (which seeds data, boots the app, then calls this). The
shots use a fixed viewport and a seeded, date-pinned register, so they are reproducible. Playwright
lives in the optional ``media`` extra; this script is never imported by the app or the test gate.
"""

from __future__ import annotations

import os
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE_URL = os.environ.get("ICEP_BASE_URL", "http://127.0.0.1:8000")
OUT_DIR = Path("docs/screenshots")

# (path, filename, full_page)
SHOTS: list[tuple[str, str, bool]] = [
    ("/", "overview.png", True),
    ("/controls", "controls.png", True),
    ("/controls/A.8.16", "control-detail.png", True),
    ("/risks", "risks.png", True),
    ("/nis2", "nis2.png", True),
    ("/evidence", "evidence.png", True),
    ("/evidence/EV-001", "evidence-detail.png", True),
    ("/training", "training.png", True),
    ("/initiatives", "initiative.png", True),
    ("/soa", "soa.png", False),
]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(args=["--no-sandbox", "--disable-gpu"])
        page = browser.new_page(viewport={"width": 1440, "height": 960}, device_scale_factor=2)
        for path, filename, full_page in SHOTS:
            page.goto(f"{BASE_URL}{path}", wait_until="networkidle")
            page.screenshot(path=str(OUT_DIR / filename), full_page=full_page)
            print(f"captured {filename}")
        browser.close()


if __name__ == "__main__":
    main()
