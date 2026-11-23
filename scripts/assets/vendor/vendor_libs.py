#!/usr/bin/env python3
"""Vendor the public site's JavaScript libraries from the npm registry, at the exact pinned versions.

    python3 scripts/assets/vendor/vendor_libs.py            # download, verify, write scripts/assets/vendor/<lib>/
    python3 scripts/assets/vendor/vendor_libs.py --check    # re-hash the vendored files against each SHA256SUMS (offline)

For each library: read the registry's record of name@version, download the tarball, check it against the registry's published
integrity (sha512) and shasum (sha1), unpack it in its own new empty directory (tarfile 'data' filter: no links, no absolute or
parent paths, no special files), and copy only the named dist files and the LICENSE into scripts/assets/vendor/<lib>/. Package
contents are untrusted data: nothing from a package is executed, and this script lives outside every unpacked directory.
SHA256SUMS holds the registry integrity line it was checked against and the sha256 of each vendored file. Stdlib only.
"""
import base64
import hashlib
import json
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
UA = "Mozilla/5.0 (compatible; AtlasSiteCorpus/1.0)"
# name, version, files to copy from the package (dist files only), directories to copy whole (images)
LIBS = [
    ("graphology", "0.25.4", ["dist/graphology.umd.min.js"], []),
    ("graphology-library", "0.8.0", ["dist/graphology-library.min.js"], []),
    ("sigma", "2.4.0", ["build/sigma.min.js"], []),
    ("d3", "7.9.0", ["dist/d3.min.js"], []),
    ("topojson-client", "3.1.0", ["dist/topojson-client.min.js"], []),
    ("3d-force-graph", "1.73.4", ["dist/3d-force-graph.min.js"], []),
    ("leaflet", "1.9.4", ["dist/leaflet.js", "dist/leaflet.css"], ["dist/images"]),
]


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
        return r.read()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def vendor(name, version, files, dirs):
    meta = json.loads(get(f"https://registry.npmjs.org/{name}/{version}"))
    assert meta["name"] == name and meta["version"] == version, (name, version)
    integrity, shasum, tarball = meta["dist"]["integrity"], meta["dist"]["shasum"], meta["dist"]["tarball"]
    blob = get(tarball)
    algo, _, b64 = integrity.partition("-")
    assert algo == "sha512" and base64.b64encode(hashlib.sha512(blob).digest()).decode() == b64, f"{name}: integrity mismatch"
    assert hashlib.sha1(blob).hexdigest() == shasum, f"{name}: shasum mismatch"
    out = HERE / name
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    with tempfile.TemporaryDirectory(prefix=f"vendor-{name}-") as tmp:       # its own new, empty directory
        archive = Path(tmp) / "pkg.tgz"
        archive.write_bytes(blob)
        pkg = Path(tmp) / "unpacked"
        pkg.mkdir()
        with tarfile.open(archive) as t:
            t.extractall(pkg, filter="data")
        root = pkg / "package"
        for rel in files:
            src = root / rel
            assert src.is_file() and not src.is_symlink(), f"{name}: {rel} missing"
            shutil.copyfile(src, out / Path(rel).name)
        for rel in dirs:
            src = root / rel
            assert src.is_dir() and not src.is_symlink(), f"{name}: {rel} missing"
            (out / Path(rel).name).mkdir()
            for f in sorted(src.iterdir()):
                if f.is_file() and not f.is_symlink():
                    shutil.copyfile(f, out / Path(rel).name / f.name)
        lic = sorted(p for p in root.iterdir() if p.is_file() and p.name.upper().startswith(("LICENSE", "LICENCE")))
        assert lic, f"{name}: no LICENSE file in the package"
        shutil.copyfile(lic[0], out / "LICENSE")
    lines = [f"# {name}@{version} registry integrity {integrity} (tarball checked against it before unpacking)"]
    for f in sorted(p for p in out.rglob("*") if p.is_file() and p.name != "SHA256SUMS"):
        lines.append(f"{sha256(f)}  {f.relative_to(out).as_posix()}")
    (out / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{name}@{version}: {len(lines) - 1} files, integrity ok")


def check():
    bad = 0
    for name, *_ in LIBS:
        sums = HERE / name / "SHA256SUMS"
        for line in sums.read_text(encoding="utf-8").splitlines():
            if line.startswith("#") or not line.strip():
                continue
            digest, _, rel = line.partition("  ")
            if sha256(HERE / name / rel) != digest:
                print("MISMATCH", name, rel)
                bad += 1
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    for lib in LIBS:
        vendor(*lib)
