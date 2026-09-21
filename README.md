# Financial dashboards

Interactive [marimo](https://marimo.io) notebooks, exported to WebAssembly and deployed to GitHub Pages.

## Dashboards

- `apps/building_taxation.py`: Norwegian primary-residence wealth-tax sandbox, policy curves and sourced wealth/population context. Population illustrations are assumption-dependent, not validated national revenue predictions.
- `apps/dashboard_stock_investment.py`: stock-investment dashboard.
- `notebooks/penguins.py`: example data-analysis notebook.

## Plans and evidence

- [Plan index](plans/README.md)
- [Current autonomous execution queue](plans/wealth_tax_autonomous_followthrough.md)
- [Wealth-tax research and implementation record](plans/wealth_tax_evidence_and_dashboard_research.md)
- [Public data, provenance and model limitations](data/wealth/README.md)

Read [AGENTS.md](AGENTS.md) for repository instructions. The wealth-tax app is an educational model with explicit legal and data exclusions, not a complete tax-return calculator.

## Local development

Dependencies and commands use `uv`. To open the wealth-tax notebook for editing:

```bash
uv run marimo edit apps/building_taxation.py
```

If a Marimo session is already running, edit the file without restarting it; Marimo watches for changes.

## Validation

```bash
uv run python -m unittest discover -s tests
uv run ruff check .
uv run marimo check apps/building_taxation.py
uv run scripts/build_wealth_reference.py --check
```

## WebAssembly preview

```bash
uv run .github/scripts/build.py
python -m http.server -d _site
```

Open `http://localhost:8000`. The build exports `apps/` in run mode and `notebooks/` in edit mode. After building, the automated wealth-tax browser check is:

```bash
uv run scripts/check_wealth_browser.py
```

See [template documentation](templates/README.md) for generated-site styling. For example:

```bash
uv run .github/scripts/build.py --template templates/tailwind.html.j2
```

## Deployment

GitHub Actions exports the notebooks and deploys GitHub Pages on updates to `main`. Browser/WASM verification should precede integration. Pushing, bookmark movement and integration remain user-controlled; writing a plan or completing checks does not authorise deployment.
