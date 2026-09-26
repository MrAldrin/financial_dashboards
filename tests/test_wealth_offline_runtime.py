import unittest

from scripts.wealth_offline_runtime import (
    failed_required_runtime_requests,
    is_required_runtime_url,
)


class RequiredRuntimeUrlTests(unittest.TestCase):
    def test_recognizes_boot_assets_without_pinning_runtime_version(self) -> None:
        urls = [
            "https://wasm.marimo.app/pyodide-lock.json?v=0.25.0&pyodide=v314.0.0",
            "https://cdn.jsdelivr.net/pyodide/v314.0.0/full/python_stdlib.zip",
            "https://cdn.jsdelivr.net/pyodide/v314.0.0/full/pyodide.asm.wasm",
            "https://cdn.jsdelivr.net/pyodide/v314.0.0/full/pyodide.asm.mjs",
            "https://cdn.jsdelivr.net/pyodide/v315.1/full/pyodide.mjs",
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertTrue(is_required_runtime_url(url))

    def test_rejects_unrelated_hosts_and_paths(self) -> None:
        urls = [
            "https://example.test/pyodide-lock.json",
            "https://cdn.jsdelivr.net/npm/marimo/index.js",
            "https://cdn.jsdelivr.net/pyodide/v314.0.0/full/unrelated.dat",
            "https://cdn.jsdelivr.net/pyodide/v314.0.0/full/python_stdlib.zip/extra",
            "http://cdn.jsdelivr.net/pyodide/v314.0.0/full/python_stdlib.zip",
            "https://cdn.jsdelivr.net:444/pyodide/v314.0.0/full/python_stdlib.zip",
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertFalse(is_required_runtime_url(url))

    def test_requires_the_request_to_be_both_blocked_and_failed(self) -> None:
        blocked = [
            "https://cdn.jsdelivr.net/pyodide/v314.0.0/full/python_stdlib.zip",
            "https://cdn.jsdelivr.net/npm/marimo/index.js",
        ]
        failed = [
            "https://cdn.jsdelivr.net/pyodide/v314.0.0/full/pyodide.asm.wasm",
            "https://cdn.jsdelivr.net/npm/marimo/index.js",
        ]
        self.assertEqual(failed_required_runtime_requests(blocked, failed), [])

        failed.append(blocked[0])
        self.assertEqual(
            failed_required_runtime_requests(blocked, failed), [blocked[0]]
        )


if __name__ == "__main__":
    unittest.main()
