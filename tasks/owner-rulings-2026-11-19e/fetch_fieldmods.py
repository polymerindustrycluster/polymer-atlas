#!/usr/bin/env python3
"""Fetch GLEIF field-modification history for the six LEIs in this ruling (raw/<LEI>.field-modifications.json).
A creationDate that GLEIF later edited (e.g. a placeholder replaced, as with Struktol in #406) is a reason to hold.
The history starts when the LEI was issued; it cannot see corporate history before that. GLEIF data is CC0.
    python3 -I tasks/owner-rulings-2026-11-19e/fetch_fieldmods.py"""
import json, urllib.request
from pathlib import Path

T = Path(__file__).resolve().parent
LEIS = ["549300GL8XWPNYKSXX74", "549300RM25BXTF73R043", "549300UCYIXHJ7CBMB49",   # ALPLA, Molten, Storopack
        "Q0M0CZB4YN6JZ65WXI09", "549300FTOLN3EVCFSS85", "254900HX50E22OG6NT36"]   # Sealed Air, Ridge, MSI Express
(T / "raw").mkdir(exist_ok=True)
for lei in LEIS:
    url = f"https://api.gleif.org/api/v1/lei-records/{lei}/field-modifications?page[size]=200"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.api+json", "User-Agent": "polymer-atlas-research"})
    body = urllib.request.urlopen(req, timeout=60).read()
    (T / "raw" / f"{lei}.field-modifications.json").write_bytes(body)
    mods = json.loads(body)["data"]
    created = [m["attributes"] for m in mods if "creationdate" in m["attributes"].get("field", "").lower()]
    print(lei, len(mods), "modifications;", "creationDate edits:", created or "none")
