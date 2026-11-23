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
        for name, version, files, dirs in vendor_libs.LIBS:
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
                self.assertEqual(set(listed), on_disk)                       # nothing unlisted, nothing missing
                for rel, digest in listed.items():
                    self.assertEqual(hashlib.sha256((folder / rel).read_bytes()).hexdigest(), digest, rel)
                self.assertIn("LICENSE", listed)
                for rel in files:
                    self.assertIn(Path(rel).name, listed)

    def test_no_folder_is_vendored_without_a_pin(self):
        folders = {p.name for p in VENDOR.iterdir() if p.is_dir() and not p.name.startswith("__")}
        self.assertEqual(folders, {name for name, *_ in vendor_libs.LIBS})


if __name__ == "__main__":
    unittest.main()
