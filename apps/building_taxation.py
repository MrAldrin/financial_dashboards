import marimo

__generated_with = "0.23.8"
app = marimo.App(width="full", sql_output="polars")

with app.setup:
    import marimo as mo


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
