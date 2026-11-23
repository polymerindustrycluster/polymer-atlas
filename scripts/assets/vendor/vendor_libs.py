#!/usr/bin/env python3
"""Vendor the public site's JavaScript libraries from the npm registry, at the exact pinned versions.

    python3 scripts/assets/vendor/vendor_libs.py            # download, verify, write scripts/assets/vendor/<lib>/
    python3 scripts/assets/vendor/vendor_libs.py --check    # offline: each folder holds exactly the expected files, and they match SHA256SUMS

For each library: read the registry's record of name@version, download the tarball, check it against the registry's published
integrity (sha512) and shasum (sha1), unpack it in its own new empty directory (tarfile 'data' filter: no links, no absolute or
parent paths, no special files), and copy only the named files and the LICENSE into scripts/assets/vendor/<lib>/. Every check is an
explicit `if ... raise`, never an `assert`, so `python3 -O` cannot skip one. Package
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
# name, version, the package files to keep (all of them, one by one: nothing is copied by directory)
LIBS = [
    ("graphology", "0.25.4", ["dist/graphology.umd.min.js"]),
    ("graphology-library", "0.8.0", ["dist/graphology-library.min.js"]),
    ("sigma", "2.4.0", ["build/sigma.min.js"]),
    ("d3", "7.9.0", ["dist/d3.min.js"]),
    ("topojson-client", "3.1.0", ["dist/topojson-client.min.js"]),
    ("3d-force-graph", "1.73.4", ["dist/3d-force-graph.min.js"]),
    ("leaflet", "1.9.4", ["dist/leaflet.js", "dist/leaflet.css", "dist/images/layers-2x.png", "dist/images/layers.png",
                          "dist/images/marker-icon-2x.png", "dist/images/marker-icon.png", "dist/images/marker-shadow.png"]),
]


class VendorError(RuntimeError):
    pass


def require(ok, message):
    if not ok:
        raise VendorError(message)


def dest(rel):
    """Where a package file lands inside scripts/assets/vendor/<lib>/: its path below the package's dist/ or build/ folder."""
    head, _, tail = rel.partition("/")
    return tail if head in ("dist", "build") else rel


def expected_files(files):
    return {dest(f) for f in files} | {"LICENSE"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
        return r.read()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def vendor(name, version, files):
    meta = json.loads(get(f"https://registry.npmjs.org/{name}/{version}"))
    require(meta.get("name") == name and meta.get("version") == version, f"{name}@{version}: the registry returned another package")
    integrity, shasum, tarball = meta["dist"]["integrity"], meta["dist"]["shasum"], meta["dist"]["tarball"]
    blob = get(tarball)
    algo, _, b64 = integrity.partition("-")
    require(algo == "sha512" and base64.b64encode(hashlib.sha512(blob).digest()).decode() == b64, f"{name}: sha512 integrity mismatch")
    require(hashlib.sha1(blob).hexdigest() == shasum, f"{name}: sha1 shasum mismatch")
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
            require(src.is_file() and not src.is_symlink(), f"{name}: {rel} missing")
            target = out / dest(rel)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, target)
        lic = sorted(p for p in root.iterdir() if p.is_file() and p.name.upper().startswith(("LICENSE", "LICENCE")))
        require(lic, f"{name}: no LICENSE file in the package")
        shutil.copyfile(lic[0], out / "LICENSE")
    lines = [f"# {name}@{version} registry integrity {integrity} (tarball checked against it before unpacking)"]
    for f in sorted(p for p in out.rglob("*") if p.is_file() and p.name != "SHA256SUMS"):
        lines.append(f"{sha256(f)}  {f.relative_to(out).as_posix()}")
    (out / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{name}@{version}: {len(lines) - 1} files, integrity ok")


def check():
    """Offline: every folder holds exactly the files LIBS says (nothing missing, nothing extra) and each matches its SHA256SUMS line."""
    bad = 0
    for name, _version, files in LIBS:
        folder = HERE / name
        on_disk = {p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file() and p.name != "SHA256SUMS"}
        listed = {}
        for line in (folder / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
            if line.startswith("#") or not line.strip():
                continue
            digest, _, rel = line.partition("  ")
            listed[rel] = digest
        if not (on_disk == set(listed) == expected_files(files)):
            print("FILE SET", name, sorted(on_disk ^ expected_files(files)), sorted(set(listed) ^ expected_files(files)))
            bad += 1
            continue
        for rel, digest in listed.items():
            if sha256(folder / rel) != digest:
                print("MISMATCH", name, rel)
                bad += 1
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    for lib in LIBS:
        vendor(*lib)
