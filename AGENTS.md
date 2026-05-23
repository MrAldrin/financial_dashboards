# Agent Instructions for Invest Calculator Marimo

Welcome, autonomous agent! This repository is for interactive notebooks and dashboards using marimo. The project is automatically exported to WebAssembly (WASM) and deployed to GitHub Pages via GitHub Actions.

The user uses this project for learning, so **you must explain complex architectural and coding choices well during the planning phase and at the end of the build**. 

## General:

**Never**:
- write code unless told so explicitly!
- use @app.cell(hide_code=True)

Special repo folder:
- plans/: 
    - A special folder that you should use if you make longer plans.
    - We will often iterate on a .md file together before implementing the plan. 
    - The bottom of the files should contain tracking of progress for that plan.


## 1. Workflows & Commands

We use `uv` for fast, reproducible dependency management and execution.

### Local WASM Testing (Critical Before Pushing)
Because GitHub Actions automatically deploys the main branch, and because some Python packages are not WASM-compatible, you should often test the app locally before committing changes.
- **Export Notebooks to WebAssembly:** 
  ```bash
  uv run .github/scripts/build.py
  ```
- **Serve Local Site:**
  ```bash
  python -m http.server -d _site
  ```
  *(Preview changes at `http://localhost:8000` to verify WASM compatibility in the browser)*

### Linting & Formatting
- **Check Linting Errors:** `uv run ruff check .`
- **Apply Formatting:** `uv run ruff check --fix .` and `uv run ruff format .`

### Testing
There is no formal test suite yet. Ad-hoc testing is done in the `local_testing/` folder.
If `pytest` is introduced in the future:
- **Run All Tests:** `uv run pytest`
- **Run a Single Test Function:** `uv run pytest path/to/test_file.py::test_function_name`

## 2. Agent Skills
There are several marimo-specific skills available in the environment. Whenever you are performing tasks related to marimo notebooks, you MUST check for and load relevant skills using your `skill` tool.
- Use the `wasm-compatibility` skill to check if packages are compatible with WebAssembly.
- Use the `marimo-notebook` skill for guidance on writing marimo notebooks in the correct Python format.

## 3. Code Style & Architecture Guidelines

### Core Principles
- **Readability & Modularity:** Emphasize readable, reusable, and modular code. Break down large complex cells into smaller helper functions when possible.
- **Commenting:** Provide high-quality, explanatory comments for complex or verbose logic (e.g., financial math or data transformations).

### Frameworks & Libraries
- Notebook: **Marimo:**
- Dataframe library: **Polars**
- Plotting library: **Altair:** 

### Current projects
- Stock investments 
- Builing taxation

### Typing & Naming
- Always use Python type hints for function signatures (e.g., `def calculate(amount: float) -> pl.DataFrame:`).
- **Variables & Functions:** Use `snake_case`.
- **Constants:** Use `UPPER_CASE` for global constants.
