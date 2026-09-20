# /// script
# requires-python = ">=3.13"
# dependencies = ["playwright>=1.58"]
# ///
"""Smoke-test the exported WASM app, not a server-side Marimo session.

First run uv run .github/scripts/build.py, then uv run scripts/check_wealth_browser.py.
Uses local Chrome if available, otherwise a Playwright-installed Chromium.
"""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
import shutil
from threading import Thread

from playwright.sync_api import expect, sync_playwright


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        partial(SimpleHTTPRequestHandler, directory=str(root / "_site")),
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    errors: list[str] = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path=shutil.which("google-chrome"), headless=True
            )
            page = browser.new_page(viewport={"width": 1400, "height": 1000})
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on(
                "console",
                lambda message: (
                    errors.append(message.text) if message.type == "error" else None
                ),
            )
            page.goto(
                f"http://127.0.0.1:{server.server_port}/apps/building_taxation.html"
            )
            # Controls live inside shadow roots; Playwright locators pierce them.
            preset = page.get_by_role("button", name="Boligtrinn: 10 mill.", exact=True)
            expect(preset).to_be_visible(timeout=180_000)
            official_heading = page.get_by_role(
                "heading", name="Offisielle scenarioer — faste, daterte referanser"
            )
            expect(official_heading).to_be_visible(timeout=180_000)
            official_table = page.get_by_role("table").filter(has_text="−1 250")
            expect(official_table).to_be_visible()
            official_before = official_table.inner_text()
            preset.click()
            expect(
                page.get_by_text(re.compile(r"Referanse:.*Sandkasse:.*18,000 kr/år"))
            ).to_be_visible(timeout=180_000)
            expect(
                page.get_by_text(re.compile(r"Illustrert årlig endring.*\+869\.4"))
            ).to_be_visible(timeout=60_000)
            assert official_table.inner_text() == official_before
            page.get_by_role("button", name="Boligtrinn: 14 mill.", exact=True).click()
            expect(
                page.get_by_text(
                    re.compile(r"Referanse:.*Sandkasse:.*Endring: \+0 kr/år")
                )
            ).to_be_visible(timeout=60_000)
            expect(
                page.get_by_text(re.compile(r"Illustrert årlig endring.*\+0\.0"))
            ).to_be_visible(timeout=60_000)
            assert official_table.inner_text() == official_before
            # Ensure chart canvases exist; successful HTML alone is not a WASM check.
            expect(page.locator("canvas").first).to_be_attached(timeout=60_000)
            if errors:
                raise AssertionError("\n".join(errors))
            browser.close()
            print(
                "WASM browser smoke passed: charts, 10m reform, 14m reset, no browser errors"
            )
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == "__main__":
    main()
