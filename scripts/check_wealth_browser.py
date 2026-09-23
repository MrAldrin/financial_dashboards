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
import json
import re
import shutil
from threading import Thread
from time import perf_counter

from playwright.sync_api import Page, expect, sync_playwright


def assert_no_page_overflow(page: Page) -> None:
    """Charts can scroll inside their containers; the document must not scroll sideways."""
    dimensions = page.evaluate(
        """() => ({viewport: innerWidth,
                    document: document.documentElement.scrollWidth,
                    body: document.body.scrollWidth})"""
    )
    assert (
        max(dimensions["document"], dimensions["body"]) <= dimensions["viewport"] + 2
    ), dimensions


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
            started = perf_counter()
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
            expect(
                page.get_by_role(
                    "heading",
                    name="Formuens sammensetning etter husholdningstype — 2024",
                )
            ).to_be_visible(timeout=60_000)
            composition = page.locator('marimo-mime-renderer[data-data*="SSB 10316:"]')
            expect(composition.locator("canvas")).to_be_attached(timeout=60_000)
            initial_load = perf_counter() - started
            assert_no_page_overflow(page)
            page.screenshot(path=str(root / "local_testing/wealth_t1_desktop.png"))
            expect(
                page.get_by_text("Status: samme politikk som 2026-referansen")
            ).to_be_visible()
            expect(
                page.get_by_text(
                    "Boligtrinn-knappene endrer bare verdsettelsestrinn", exact=False
                )
            ).to_be_visible()
            advanced = page.get_by_text(
                "Avansert: antatte eiere og gjeld/formue per bolig", exact=True
            )
            expect(advanced).to_be_visible()
            advanced.click()
            scenario_table = page.get_by_role("table").filter(
                has_text="Startmiks: antatt gjeld/eierskap"
            )
            expect(scenario_table).to_be_visible(timeout=120_000)
            expect(scenario_table).to_contain_text("1,712,400")
            expect(scenario_table).to_contain_text("1,887,270")
            page.screenshot(
                path=str(root / "local_testing/wealth_t3c_desktop.png"),
                animations="disabled",
            )
            page.get_by_text(
                "Vis valgt boligs verdsetting, skattebånd og marginal endring",
                exact=True,
            ).click()
            diagnostics = page.get_by_role("table").filter(
                has_text="Grunnlag før nullgulv"
            )
            expect(diagnostics).to_be_visible(timeout=60_000)
            expect(
                diagnostics.get_by_role("row", name=re.compile("Høyre marginal"))
            ).to_contain_text("7,000")
            composition_before = composition.get_attribute("data-data")
            spec = json.loads(json.loads(composition_before))
            bars = spec["datasets"][spec["layer"][0]["data"]["name"]]
            assert len(bars) == 75
            assert sum(row["amount"] < 0 for row in bars) == 15
            assert spec["layer"][1]["encoding"]["y"]["field"] == "net_wealth"
            group_selector = page.get_by_role(
                "combobox", name="Vis formue etter (SSB 2024)"
            )
            group_selector.select_option(label="Alder på hovedinntektstaker")
            age_chart = page.locator('marimo-mime-renderer[data-data*="SSB 10317:"]')
            expect(age_chart.locator("canvas")).to_be_attached(timeout=60_000)
            age_before = age_chart.get_attribute("data-data")
            age_spec = json.loads(json.loads(age_before))
            age_bars = age_spec["datasets"][age_spec["layer"][0]["data"]["name"]]
            assert (
                len(age_bars) == 35 and sum(row["amount"] < 0 for row in age_bars) == 7
            )
            group_selector.select_option(label="Husholdningstype")
            expect(composition.locator("canvas")).to_be_attached(timeout=60_000)
            assert composition.get_attribute("data-data") == composition_before
            update_started = perf_counter()
            preset.click()
            expect(
                page.get_by_text(re.compile(r"Referanse:.*Sandkasse:.*18,000 kr/år"))
            ).to_be_visible(timeout=180_000)
            preset_update = perf_counter() - update_started
            expect(page.get_by_text("Status: egendefinert politikk")).to_be_visible()
            expect(
                page.get_by_text(re.compile(r"Illustrert årlig endring.*\+869\.4"))
            ).to_be_visible(timeout=60_000)
            assert official_table.inner_text() == official_before
            assert composition.get_attribute("data-data") == composition_before
            start_row = scenario_table.get_by_role("row", name=re.compile("Startmiks:"))
            expect(start_row).to_contain_text("761.4", timeout=120_000)
            expect(
                diagnostics.locator("tr").filter(has_text="Skatt (kr/år)")
            ).to_contain_text("18,000", timeout=60_000)
            group_selector.select_option(label="Alder på hovedinntektstaker")
            expect(age_chart.locator("canvas")).to_be_attached(timeout=60_000)
            assert age_chart.get_attribute("data-data") == age_before
            group_selector.select_option(label="Husholdningstype")
            expect(composition.locator("canvas")).to_be_attached(timeout=60_000)
            # Personal share changes housing exposure, never the legacy population.
            # Marimo number fields are text inputs; their aria-label includes markup.
            share = page.locator(
                'input[aria-label*="Skatteenhetens samlede eierandel"]'
            )
            share.fill("50")
            share.press("Tab")
            expect(
                page.get_by_text(
                    re.compile(r"Referanse:.*Sandkasse:.*Endring: \+0 kr/år")
                )
            ).to_be_visible(timeout=60_000)
            expect(
                page.get_by_text(re.compile(r"Skatteenhetens boligandel: 7,000,000 kr"))
            ).to_be_visible()
            expect(
                page.get_by_text(re.compile(r"Illustrert årlig endring.*\+869\.4"))
            ).to_be_visible()
            expect(start_row).to_contain_text("761.4", timeout=60_000)
            share.fill("100")
            share.press("Tab")
            expect(
                page.get_by_text(re.compile(r"Referanse:.*Sandkasse:.*18,000 kr/år"))
            ).to_be_visible(timeout=60_000)
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
            assert composition.get_attribute("data-data") == composition_before
            expect(start_row).to_have_text(
                re.compile(r"1,002\.9.*1,002\.9.*0$"), timeout=120_000
            )
            expect(
                diagnostics.locator("tr").filter(has_text="Skatt (kr/år)")
            ).to_have_text(re.compile(r".*0.*0$"), timeout=60_000)
            expect(composition.locator("canvas")).to_be_attached()
            expect(
                page.get_by_text("Status: samme politikk som 2026-referansen")
            ).to_be_visible()
            # T2a worked example: whole home 16m, half-owner, no debt.
            debt = page.locator('input[aria-label*="Skatteenhetens gjeld"]')
            debt.fill("0")
            debt.press("Tab")
            home = page.locator('input[aria-label*="Hele boligens verdi"]')
            home.fill("16000000")
            home.press("Tab")
            share.fill("50")
            share.press("Tab")
            expect(
                page.get_by_text(
                    re.compile(r"Referanse:.*5,500 kr/år.*Sandkasse:.*5,500 kr/år")
                )
            ).to_be_visible(timeout=60_000)
            joint = page.get_by_role(
                "switch",
                name=re.compile("Fellesfastsetting"),
            )
            joint.click()
            expect(
                page.get_by_text(
                    re.compile(r"Referanse:\s*0 kr/år.*Sandkasse:\s*0 kr/år")
                )
            ).to_be_visible(timeout=60_000)
            share.fill("100")
            share.press("Tab")
            expect(
                page.get_by_text(
                    re.compile(r"Referanse:.*11,000 kr/år.*Sandkasse:.*11,000 kr/år")
                )
            ).to_be_visible(timeout=60_000)
            share.fill("0")
            share.press("Tab")
            expect(
                page.get_by_text(re.compile(r"Skatteenhetens boligandel: 0 kr"))
            ).to_be_visible(timeout=60_000)
            # Restore all controls exercised here to the original full-owner case.
            joint.click()
            share.fill("100")
            share.press("Tab")
            debt.fill("1600000")
            debt.press("Tab")
            home.fill("14000000")
            home.press("Tab")
            expect(
                page.get_by_text(re.compile(r"Økonomisk nettoformue: 12,400,000 kr"))
            ).to_be_visible(timeout=60_000)
            expect(
                page.get_by_text(
                    re.compile(r"Referanse:\s*0 kr/år.*Sandkasse:\s*0 kr/år")
                )
            ).to_be_visible(timeout=60_000)
            assert official_table.inner_text() == official_before
            assert composition.get_attribute("data-data") == composition_before
            # Changing non-housing policy survives a housing preset; the preset is not reset-all.
            allowance = page.locator('input[aria-label*="Bunnfradrag per person"]')
            allowance.fill("2000000")
            allowance.press("Tab")
            expect(page.get_by_text("Status: egendefinert politikk")).to_be_visible()
            page.get_by_role("button", name="Boligtrinn: 10 mill.", exact=True).click()
            page.get_by_role("button", name="Boligtrinn: 14 mill.", exact=True).click()
            expect(allowance).to_have_value("2,000,000")
            expect(page.get_by_text("Status: egendefinert politikk")).to_be_visible()
            allowance.fill("1900000")
            allowance.press("Tab")
            expect(
                page.get_by_text("Status: samme politikk som 2026-referansen")
            ).to_be_visible()
            # Add and remove a valuation tier via named, keyboard-reachable controls.
            add = page.get_by_role("button", name="Legg til verdsettelsesgrense")
            add.focus()
            assert add.evaluate("el => el === el.getRootNode().activeElement")
            add.press("Enter")
            remove = page.get_by_role("button", name="Fjern trinn 2")
            expect(remove).to_be_visible(timeout=60_000)
            expect(page.get_by_text("Status: egendefinert politikk")).to_be_visible()
            remove.click()
            expect(remove).to_have_count(0)
            expect(
                page.get_by_text("Status: samme politikk som 2026-referansen")
            ).to_be_visible()
            assert official_table.inner_text() == official_before
            assert composition.get_attribute("data-data") == composition_before
            # Tail is an explicit assumption; both models respond, references do not.
            tail = page.locator(
                'input[aria-label*="Antatt antall boliger over 30 mill."]'
            )
            tail.fill("0")
            tail.press("Tab")
            expect(scenario_table).to_contain_text("1,711,400", timeout=60_000)
            tail.fill("1000")
            tail.press("Tab")
            expect(scenario_table).to_contain_text("1,712,400", timeout=60_000)
            assert official_table.inner_text() == official_before
            assert composition.get_attribute("data-data") == composition_before
            # Exercise the same exported WASM app at a narrow mobile viewport.
            page.set_viewport_size({"width": 390, "height": 844})
            expect(preset).to_be_visible()
            assert_no_page_overflow(page)
            expect(scenario_table).to_be_visible()
            diagnostics.scroll_into_view_if_needed()
            page.screenshot(
                path=str(root / "local_testing/wealth_t5_mobile.png"),
                animations="disabled",
            )
            scenario_table.scroll_into_view_if_needed()
            page.screenshot(
                path=str(root / "local_testing/wealth_t3c_mobile.png"),
                animations="disabled",
            )
            # A hidden/clipped hstack can leave page width normal while inputs
            # extend beyond the visible viewport. Check actual control bounds.
            for control in (debt, home, share, allowance, add, preset):
                control.scroll_into_view_if_needed()
                bounds = control.bounding_box()
                assert bounds is not None and bounds["x"] >= -2, bounds
                assert bounds["x"] + bounds["width"] <= 392, bounds
            page.get_by_role(
                "heading", name=re.compile("Politisk sandkasse")
            ).scroll_into_view_if_needed()
            page.screenshot(path=str(root / "local_testing/wealth_t1_mobile.png"))
            mobile_started = perf_counter()
            preset.click()
            expect(
                page.get_by_text(re.compile(r"Referanse:.*Sandkasse:.*18,000 kr/år"))
            ).to_be_visible(timeout=60_000)
            mobile_update = perf_counter() - mobile_started
            assert_no_page_overflow(page)
            add.click()
            expect(page.get_by_role("button", name="Fjern trinn 2")).to_be_visible(
                timeout=60_000
            )
            page.get_by_role("button", name="Fjern trinn 2").click()
            expect(page.get_by_role("button", name="Fjern trinn 2")).to_have_count(0)
            page.get_by_role("button", name="Boligtrinn: 14 mill.", exact=True).click()
            expect(
                page.get_by_text("Status: samme politikk som 2026-referansen")
            ).to_be_visible()
            expect(
                page.get_by_text(
                    re.compile(r"Referanse:\s*0 kr/år.*Sandkasse:\s*0 kr/år")
                )
            ).to_be_visible(timeout=60_000)
            assert official_table.inner_text() == official_before
            assert composition.get_attribute("data-data") == composition_before
            # Ensure chart canvases exist; successful HTML alone is not a WASM check.
            expect(page.locator("canvas").first).to_be_attached(timeout=60_000)
            page.get_by_role(
                "heading", name=re.compile("Valgt bolig:")
            ).scroll_into_view_if_needed()
            page.screenshot(
                path=str(root / "local_testing/wealth_t3c_mobile_curves.png")
            )
            if errors:
                raise AssertionError("\n".join(errors))
            browser.close()
            print(
                "WASM browser smoke passed: desktop/mobile layout, labelled keyboard controls, "
                "tier add/remove, policy-status/preset scope, ownership, fixed references, "
                "no browser errors"
            )
            print(
                f"Observed seconds: initial render {initial_load:.2f}; "
                f"desktop preset update {preset_update:.2f}; mobile preset update {mobile_update:.2f} "
                "(warm browser context, not performance thresholds)"
            )
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == "__main__":
    main()
