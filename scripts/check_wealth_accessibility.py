# /// script
# requires-python = ">=3.13"
# dependencies = ["playwright>=1.58"]
# ///
"""Run a scoped DOM/keyboard audit and a genuinely isolated cold-offline probe.

Build the exports first with ``uv run .github/scripts/build.py``. This checks
visible control names and a real Tab/Enter sequence; it is not a WCAG or
screen-reader certification. The offline probe uses a brand-new browser context,
blocks service workers and every off-origin request before navigation, while
allowing only the local static server needed to serve the exported files.
"""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
from threading import Thread
from urllib.parse import urlparse

from playwright.sync_api import Browser, Locator, Page, Route, expect, sync_playwright

from wealth_offline_runtime import failed_required_runtime_requests


class QuietStaticHandler(SimpleHTTPRequestHandler):
    """Serve the export without flooding test output with routine requests."""

    def log_message(self, format: str, *args: object) -> None:
        pass


ACCESSIBLE_NAME_AUDIT = r"""() => {
  const selector = [
    "button", "input", "select", "textarea", "summary", "[role=button]",
    "[role=switch]", "[role=combobox]", "[role=slider]", "[role=checkbox]",
    "[role=radio]", "[role=tab]"
  ].join(",");
  const controls = [];
  const isHidden = (element) => {
    for (let current = element; current;) {
      if (current.nodeType === Node.ELEMENT_NODE) {
        const style = getComputedStyle(current);
        if (current.hidden || current.getAttribute("aria-hidden") === "true" ||
            style.display === "none" || style.visibility === "hidden") return true;
        current = current.parentElement || current.getRootNode().host || null;
      } else {
        current = current.host || null;
      }
    }
    return false;
  };
  const text = (element) => (element?.innerText || element?.textContent || "").trim();
  const walk = (root) => {
    for (const element of root.children || []) {
      if (element.matches?.(selector)) {
        const rect = element.getBoundingClientRect();
        const style = getComputedStyle(element);
        if (!isHidden(element) && rect.width > 0 && rect.height > 0 &&
            style.opacity !== "0" && !element.disabled) {
          const tree = element.getRootNode();
          const ariaLabel = element.getAttribute("aria-label") || "";
          const labelledBy = (element.getAttribute("aria-labelledby") || "")
            .split(/\s+/).filter(Boolean).map((id) => {
              const referenced = [...tree.querySelectorAll("[id]")]
                .find((candidate) => candidate.id === id);
              return text(referenced);
            }).filter(Boolean).join(" ");
          const nativeLabels = element.labels
            ? [...element.labels].map(text).filter(Boolean).join(" ") : "";
          const linkedLabel = element.id
            ? [...tree.querySelectorAll("label[for]")]
                .find((label) => label.htmlFor === element.id) : null;
          const buttonText = /^(BUTTON|SUMMARY)$/.test(element.tagName)
            ? text(element) : "";
          const name = ariaLabel || labelledBy || nativeLabels ||
            text(linkedLabel) || buttonText || element.getAttribute("title") || "";
          controls.push({
            tag: element.tagName,
            role: element.getAttribute("role") || "",
            id: element.id,
            className: typeof element.className === "string" ? element.className : "",
            outerHTML: element.outerHTML.slice(0, 500),
            name: name.trim(),
            ariaLabel,
            literalMarkupInAriaLabel: /<[^>]+>/.test(ariaLabel)
          });
        }
      }
      walk(element);
      if (element.shadowRoot) walk(element.shadowRoot);
    }
  };
  walk(document);
  return {
    language: document.documentElement.lang,
    controls,
    missingNames: controls.filter((control) => !control.name),
    markupLabels: controls.filter((control) => control.literalMarkupInAriaLabel)
  };
}"""


def is_focused_in_its_tree(locator: Locator) -> bool:
    """Check focus through the control's own open shadow root."""
    return locator.evaluate(
        "element => element === element.getRootNode().activeElement"
    )


def assert_tab_reaches(page: Page, locator: Locator, max_tabs: int = 100) -> int:
    """Prove that sequential keyboard navigation can reach a specific control."""
    for count in range(1, max_tabs + 1):
        page.keyboard.press("Tab")
        if is_focused_in_its_tree(locator):
            return count
    raise AssertionError(f"Tab did not reach {locator} in {max_tabs} presses")


def bounded_diagnostic(values: list[str], limit: int = 3) -> str:
    """Keep unexpected-startup diagnostics useful without dumping full stacks."""
    unique = list(dict.fromkeys(values))
    details = [value[:240] for value in unique[:limit]]
    if len(unique) > limit:
        details.append(f"... and {len(unique) - limit} more")
    return "; ".join(details) if details else "(none)"


def check_accessibility_and_keyboard(page: Page) -> None:
    preset = page.get_by_role("button", name="Boligtrinn: 10 mill.", exact=True)
    expect(preset).to_be_visible(timeout=180_000)
    expect(
        page.get_by_role(
            "heading", name="Offisielle scenarioer — faste, daterte referanser"
        )
    ).to_be_visible(timeout=180_000)

    audit = page.evaluate(ACCESSIBLE_NAME_AUDIT)
    controls = audit["controls"]
    assert controls, "No visible, enabled interactive controls were audited"
    missing_names = audit["missingNames"]
    print(
        "Scoped DOM accessibility audit: "
        f"{len(controls)} visible/enabled controls; "
        f"{len(missing_names)} have no detectable accessible name."
    )
    for item in missing_names:
        print(
            "UNNAMED CONTROL: "
            f"tag={item['tag']} role={item['role']!r} id={item['id']!r} "
            f"class={item['className'][:100]!r}"
        )
    if audit["markupLabels"]:
        examples = sorted({item["ariaLabel"] for item in audit["markupLabels"]})[:3]
        print(
            "KNOWN FRAMEWORK LIMITATION: "
            f"{len(audit['markupLabels'])} control names contain literal HTML markup; "
            f"examples: {examples}"
        )
    if audit["language"] != "nb":
        print(
            "KNOWN DOCUMENT-LANGUAGE FINDING: "
            f"export root has lang={audit['language']!r}; dashboard text is Norwegian."
        )

    add = page.get_by_role("button", name="Legg til verdsettelsesgrense")
    tabs_to_add = assert_tab_reaches(page, add)
    page.keyboard.press("Enter")
    remove = page.get_by_role("button", name="Fjern trinn 2")
    expect(remove).to_be_visible(timeout=60_000)
    page.keyboard.press("Shift+Tab")
    assert is_focused_in_its_tree(remove), (
        "Shift+Tab did not focus the new remove button"
    )
    page.keyboard.press("Enter")
    expect(remove).to_have_count(0, timeout=60_000)
    expect(
        page.get_by_text("Status: samme politikk som 2026-referansen")
    ).to_be_visible()
    print(
        "Keyboard interaction passed: Tab reached tier-add in "
        f"{tabs_to_add} presses; Enter added a tier; Shift+Tab/Enter removed it."
    )
    print(
        "Audit limits: no axe-core/WCAG conformance run, color-contrast assessment, "
        "screen-reader test, chart-semantic review, or cross-browser review."
    )


def cold_offline_probe(browser: Browser, root: Path) -> None:
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        partial(QuietStaticHandler, directory=str(root / "_site")),
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"
    local_requests: list[str] = []
    local_http_errors: list[str] = []
    blocked_urls: list[str] = []
    failed_urls: list[str] = []
    browser_errors: list[str] = []
    offline_started = False
    context = None
    try:
        # This is a fresh incognito profile: no warmed HTTP cache, cookies or
        # persisted application state. Install the block before creating/navigating
        # the page; only localhost is allowed to deliver the already-built export.
        context = browser.new_context(
            viewport={"width": 360, "height": 800}, service_workers="block"
        )

        def isolate_network(route: Route) -> None:
            url = route.request.url
            if urlparse(url).netloc == urlparse(origin).netloc and url.startswith(
                origin + "/"
            ):
                local_requests.append(url)
                route.continue_()
            else:
                blocked_urls.append(url)
                route.abort("internetdisconnected")

        context.route("**/*", isolate_network)
        page = context.new_page()
        page.on(
            "response",
            lambda response: (
                local_http_errors.append(f"{response.status} {response.url}")
                if response.url.startswith(origin + "/") and response.status >= 400
                else None
            ),
        )
        page.on("requestfailed", lambda request: failed_urls.append(request.url))
        page.on("pageerror", lambda error: browser_errors.append(str(error)))
        page.on(
            "console",
            lambda message: (
                browser_errors.append(message.text) if message.type == "error" else None
            ),
        )
        try:
            page.goto(
                origin + "/apps/building_taxation.html",
                wait_until="domcontentloaded",
                timeout=30_000,
            )
        except Exception as error:
            raise AssertionError(
                "Unexpected cold-offline navigation failure: "
                f"{str(error)[:240]}; "
                f"blocked off-origin URLs: {bounded_diagnostic(blocked_urls)}; "
                f"requestfailed URLs: {bounded_diagnostic(failed_urls)}; "
                f"browser errors: {bounded_diagnostic(browser_errors)}"
            ) from error
        try:
            expect(
                page.get_by_role("button", name="Boligtrinn: 10 mill.", exact=True)
            ).to_be_visible(timeout=30_000)
            offline_started = True
        except Exception:
            offline_started = False

        if local_http_errors:
            raise AssertionError(
                "Unexpected cold-offline startup failure from local exported assets: "
                f"{bounded_diagnostic(local_http_errors)}"
            )
        if not local_requests:
            raise AssertionError(
                "Unexpected cold-offline startup failure: no local export request "
                "reached the server; "
                f"blocked off-origin URLs: {bounded_diagnostic(blocked_urls)}; "
                f"requestfailed URLs: {bounded_diagnostic(failed_urls)}; "
                f"browser errors: {bounded_diagnostic(browser_errors)}"
            )

        failed_runtime_urls = failed_required_runtime_requests(
            blocked_urls, failed_urls
        )
        if not offline_started and not failed_runtime_urls:
            raise AssertionError(
                "Unexpected cold-offline startup failure: no blocked required "
                "Pyodide runtime request was also observed failing; "
                f"blocked off-origin URLs: {bounded_diagnostic(blocked_urls)}; "
                f"requestfailed URLs: {bounded_diagnostic(failed_urls)}; "
                f"browser errors: {bounded_diagnostic(browser_errors)}"
            )

        print(
            "Cold-start conditions: fresh browser context, no cache/storage, "
            "service workers blocked; every off-origin request aborted before navigation."
        )
        print(f"Local exported HTML/assets served: {len(local_requests)} requests.")
        print(
            f"Blocked off-origin dependencies: {len(set(blocked_urls))} unique requests."
        )
        for url in dict.fromkeys(blocked_urls):
            print(f"BLOCKED: {url}")
        if offline_started:
            print(
                "Cold offline result: exported WASM started with off-origin access blocked."
            )
        else:
            print(
                "Cold offline result: UNSUPPORTED by current external Pyodide "
                "runtime loading; local HTML loaded but WASM startup could not complete."
            )
            print(f"Failed required runtime requests: {len(failed_runtime_urls)}.")
            for url in failed_runtime_urls:
                print(f"FAILED REQUIRED RUNTIME: {url}")
            for error in list(dict.fromkeys(browser_errors))[:3]:
                print(f"BROWSER ERROR AFTER RUNTIME BLOCK: {error[:240]}")
            if len(set(browser_errors)) > 3:
                print(f"... and {len(set(browser_errors)) - 3} more browser errors")
    finally:
        if context is not None:
            context.close()
        server.shutdown()
        server.server_close()
        thread.join()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        partial(QuietStaticHandler, directory=str(root / "_site")),
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path=shutil.which("google-chrome"), headless=True
            )
            page = browser.new_page(viewport={"width": 360, "height": 844})
            browser_errors: list[str] = []
            page.on("pageerror", lambda error: browser_errors.append(str(error)))
            page.on(
                "console",
                lambda message: (
                    browser_errors.append(message.text)
                    if message.type == "error"
                    else None
                ),
            )
            page.goto(
                f"http://127.0.0.1:{server.server_port}/apps/building_taxation.html"
            )
            check_accessibility_and_keyboard(page)
            if browser_errors:
                raise AssertionError(
                    "Connected browser errors: " + "\n".join(browser_errors)
                )
            browser.close()
        print(
            "Connected exported-WASM accessibility probe completed; "
            "keyboard smoke passed (review the findings above)."
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    # Deliberately separate from the warm online test browser/profile above.
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=shutil.which("google-chrome"), headless=True
        )
        cold_offline_probe(browser, root)
        browser.close()


if __name__ == "__main__":
    main()
