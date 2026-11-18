#!/usr/bin/env python3
"""Fetch a URL, store raw bytes by sha256 under PERSIST, append manifest.csv.
Usage: fetch.py URL PROVENANCE   (PROVENANCE = which rule-14 route made the URL fetchable)."""
import csv, hashlib, os, subprocess, sys, datetime, tempfile
PERSIST = "/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/people-rulings-2026-11-18b"
UA = "Mozilla/5.0 (compatible; PolymerAtlasBot/1.0; public-page verification)"

def fetch(url, prov):
    os.makedirs(PERSIST, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False) as t:
        tmp = t.name
    r = subprocess.run(["curl", "-sL", "--max-time", "45", "-A", UA, "-o", tmp, "-w", "%{http_code}", url],
                       capture_output=True, text=True)
    code = r.stdout.strip()
    data = open(tmp, "rb").read(); os.unlink(tmp)
    if code != "200" or not data:
        print(f"FAIL {code} {url}"); return None
    h = hashlib.sha256(data).hexdigest()
    open(os.path.join(PERSIST, h), "wb").write(data)
    mp = os.path.join(PERSIST, "manifest.csv")
    new = not os.path.exists(mp)
    with open(mp, "a", newline="") as f:
        w = csv.writer(f)
        if new: w.writerow(["url", "fetched_at", "sha256", "url_provenance"])
        w.writerow([url, datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), h, prov])
    print(f"OK {len(data)} {h[:12]} {url}")
    return h

if __name__ == "__main__":
    fetch(sys.argv[1], sys.argv[2])
