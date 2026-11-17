#!/usr/bin/env python3
"""Fetch a URL, store raw bytes under persist/<sha256>, append to manifest.csv (url, fetched_at, sha256, url_provenance).
usage: fetch.py URL PROVENANCE   (prints sha256, http status, bytes)"""
import csv, hashlib, subprocess, sys, datetime, os
P = "/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-faculty-akron-2026-11-17"
def fetch(url, prov):
    os.makedirs(P, exist_ok=True)
    r = subprocess.run(["curl", "-sL", "-m", "60", "-A", "Mozilla/5.0 (PolymerAtlas research)", "-w", "\n%{http_code}", url], capture_output=True)
    body, _, code = r.stdout.rpartition(b"\n")
    code = code.decode()
    if code != "200" or not body:
        return None, code, 0
    sha = hashlib.sha256(body).hexdigest()
    open(f"{P}/{sha}", "wb").write(body)
    m = f"{P}/manifest.csv"
    new = not os.path.exists(m)
    with open(m, "a", newline="") as f:
        w = csv.writer(f)
        if new: w.writerow(["url", "fetched_at", "sha256", "url_provenance"])
        w.writerow([url, datetime.datetime.now().astimezone().isoformat(timespec="seconds"), sha, prov])
    return sha, code, len(body)
if __name__ == "__main__":
    print(*fetch(sys.argv[1], sys.argv[2]))
