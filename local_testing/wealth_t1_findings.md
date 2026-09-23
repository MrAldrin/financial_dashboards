# T1 — Objective wealth-dashboard usability and interaction check

Measured 23 September 2026 against the exported WASM app at 1400×1000 and 390×844 in headless local Chrome. Run `uv run .github/scripts/build.py` followed by `uv run scripts/check_wealth_browser.py`. The test starts its own HTTP server; it does **not** restart the watched Marimo session. Screenshots are browser artifacts from the default policy: [desktop controls](wealth_t1_desktop.png), [mobile controls](wealth_t1_mobile.png), [mobile selected-point/curves](wealth_t1_mobile_curves.png).

## Findings and fixes

- At 390 px the original horizontal economy/policy input rows were clipped within a container without causing page-level horizontal overflow. Set control rows, tier rows and preset rows to wrap; the test now checks the visible bounds of key controls as well as document width on desktop/mobile. Charts retain their existing contained horizontal scrolling and their order.
- Policy customization was not obvious: the 14m preset resets housing tiers **only**, not allowance/rates. Added an explicit reference/custom policy status and preset-scope text. The status compares the sandbox policy controls against the fixed reference, not the user's economy; it returns to reference only when all policy controls match. Browser checks verify non-housing edits survive preset switching and tier add/remove returns to the baseline policy.
- Tier deletion used an unlabeled cross. It now has a visible, specific name (`Fjern trinn N`); keyboard Enter on the add button and named remove buttons are exercised. Existing ownership, reference-table and composition-chart regression checks remain in the browser script.
- No new notebook packages, runtime I/O or calculations were introduced. The original full-owner outputs and public-reference data are unchanged.

## Verification

- `uv run python -m unittest discover -s tests`: **29 passed**.
- `uv run ruff check .` and `uv run ruff format --check apps/building_taxation.py scripts/check_wealth_browser.py`: pass.
- `uv run marimo check apps/building_taxation.py` and `uv run scripts/build_wealth_reference.py --check`: pass.
- `uv run .github/scripts/build.py`: all three notebooks exported successfully; wealth HTML **225,916 bytes**, versus T0's **212,373 bytes** before the intervening ownership implementation (not an isolated T1 size delta). Browser smoke after the build: desktop/mobile interactions, policy status, tier add/remove, fixed references, no captured page/console errors; no document-level overflow at the tested widths. Two final runs passed.
- Illustrative initial-render times on the two final runs: **18.68 / 20.78 s** from navigation setup to source-composition canvas attached. First desktop preset-result times **0.96 / 0.95 s**; warmed mobile preset-result times **1.02 / 1.44 s**. Headless Chrome, local server, no CPU/network throttling or cache clearing. These are different operations from T0's whole-process wall times (14.19/15.49/14.33 s), not evidence of a comparable slowdown or a performance threshold. No demonstrated bottleneck was optimized.

## Limits for final human review

- The Marimo numeric control's DOM `aria-label` contains HTML markup (a framework rendering issue); locator tests search label substrings, not a screen-reader audit. Full keyboard navigation, automated WCAG audit, screen-reader usability, very small (<390 px) screens and other browsers remain untested. The slider's compact number field truncates its formatted large value on mobile until focused; its value is editable and the control itself remains within the viewport. The dense chart axes need human assessment; charts deliberately scroll inside their container.
- Screenshots and automated geometry checks do not replace human acceptance of mobile layout or density. Browser test was run with network access; disconnected *cold* startup and all special-case legal combinations remain outside this task. No bookmarks were moved or deployment attempted by this task.
