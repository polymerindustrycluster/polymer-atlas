#!/usr/bin/env python3
"""The vendored JavaScript libraries (scripts/assets/vendor/) match their SHA256SUMS and the pins in vendor_libs.py.

    python3 -m unittest scripts/test_site_vendor.py

Offline: re-fetching and re-verifying against the npm registry is `python3 scripts/assets/vendor/vendor_libs.py`.
"""
import hashlib
import importlib.util
import re
import unittest
from pathlib import Path

VENDOR = Path(__file__).resolve().parent / "assets" / "vendor"
spec = importlib.util.spec_from_file_location("vendor_libs", VENDOR / "vendor_libs.py")
vendor_libs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vendor_libs)


class VendoredLibraries(unittest.TestCase):
    def test_every_pin_has_a_folder_with_license_and_checksums_that_match(self):
        for name, version, files in vendor_libs.LIBS:
            with self.subTest(lib=name):
                folder = VENDOR / name
                lines = (folder / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
                self.assertRegex(lines[0], rf"^# {re.escape(name)}@{re.escape(version)} registry integrity sha512-[A-Za-z0-9+/=]{{86,}} ")
                listed = {}
                for line in lines[1:]:
                    digest, _, rel = line.partition("  ")
                    self.assertRegex(digest, r"^[0-9a-f]{64}$")
                    listed[rel] = digest
                on_disk = {p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file() and p.name != "SHA256SUMS"}
                self.assertEqual(on_disk, vendor_libs.expected_files(files))   # exactly the pinned files: none deleted, none added
                self.assertEqual(set(listed), on_disk)                       # nothing unlisted, nothing missing
                for rel, digest in listed.items():
                    self.assertEqual(hashlib.sha256((folder / rel).read_bytes()).hexdigest(), digest, rel)
                self.assertIn("LICENSE", listed)

    def test_no_folder_is_vendored_without_a_pin(self):
        folders = {p.name for p in VENDOR.iterdir() if p.is_dir() and not p.name.startswith("__")}
        self.assertEqual(folders, {name for name, *_ in vendor_libs.LIBS})

    def test_a_check_that_could_be_optimised_away_is_not_a_check(self):
        text = (VENDOR / "vendor_libs.py").read_text(encoding="utf-8")
        self.assertNotRegex(text, r"(?m)^\s*assert\b")                         # python3 -O strips assert; verification must raise

    def test_a_wrong_integrity_is_refused_even_under_optimisation(self):
        import base64
        import hashlib
        import subprocess
        import sys
        import textwrap
        probe = textwrap.dedent("""
            import base64, hashlib, importlib.util, sys
            spec = importlib.util.spec_from_file_location("vendor_libs", sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
            blob = b"not the package"
            wrong = "sha512-" + base64.b64encode(hashlib.sha512(b"something else").digest()).decode()
            meta = {"name": "x", "version": "1", "dist": {"integrity": wrong, "shasum": hashlib.sha1(blob).hexdigest(), "tarball": "t"}}
            import json
            m.get = lambda url: json.dumps(meta).encode() if "registry" in url else blob
            try:
                m.vendor("x", "1", ["dist/x.js"])
            except m.VendorError as e:
                print("refused", e)
            else:
                print("VENDORED")
        """)
        for flags in ([], ["-O"], ["-OO"]):
            out = subprocess.run([sys.executable, *flags, "-c", probe, str(VENDOR / "vendor_libs.py")], capture_output=True, text=True, cwd=str(VENDOR.parent))
            self.assertIn("refused", out.stdout, (flags, out.stdout, out.stderr))
            self.assertNotIn("VENDORED", out.stdout)
        self.assertFalse((VENDOR / "x").exists())


if __name__ == "__main__":
    unittest.main()
