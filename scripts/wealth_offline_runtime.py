"""Recognize the narrowly scoped external requests required for Pyodide boot."""

from collections.abc import Iterable
import re
from urllib.parse import urlparse


_PYODIDE_ASSET_PATH = re.compile(
    r"/pyodide/[^/]+/full/"
    r"(?:pyodide-lock\.json|pyodide\.mjs|pyodide\.asm\.(?:mjs|wasm)|python_stdlib\.zip)"
)


def is_required_runtime_url(url: str) -> bool:
    """Return whether URL matches a known Marimo/Pyodide boot asset endpoint."""
    parsed = urlparse(url)
    if parsed.scheme.lower() != "https" or parsed.username or parsed.password:
        return False
    try:
        if parsed.port not in (None, 443):
            return False
    except ValueError:
        return False

    host = (parsed.hostname or "").lower()
    if host == "wasm.marimo.app":
        return parsed.path == "/pyodide-lock.json"
    return host == "cdn.jsdelivr.net" and bool(
        _PYODIDE_ASSET_PATH.fullmatch(parsed.path)
    )


def failed_required_runtime_requests(
    blocked_urls: Iterable[str], failed_urls: Iterable[str]
) -> list[str]:
    """Return required runtime URLs both intercepted and observed failing."""
    failed = set(failed_urls)
    return [
        url
        for url in dict.fromkeys(blocked_urls)
        if url in failed and is_required_runtime_url(url)
    ]
