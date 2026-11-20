#!/usr/bin/env python3
"""Shrink V-65 (and V-68, where present) by the records this lane evidenced, per the baseline file's shrink-only
doctrine: ask validate.py which baselined entries still violate and drop the rest. Run after a merge from main
(apply.py already shrank V-65 on the original tree). The 'amended' note is left alone to avoid merge conflicts.

    python3 tasks/evidence-tri-filings-2026-11-20/prune_baselines.py     (from the repo root)
"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "scripts" / "validate_debt_baseline.json"
out = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate.py"), "--debt-details"],
                     capture_output=True, text=True, encoding="utf-8", cwd=ROOT).stdout
doc = json.loads(BASE.read_text(encoding="utf-8"))
v65_still = set(re.findall(r"V-65 debt: \w+ (\S+) is tier", out))
assert v65_still and v65_still <= set(doc["rules"]["V-65"]), "validate.py output not understood; nothing written"
before = {"V-65": len(doc["rules"]["V-65"])}
doc["rules"]["V-65"] = [i for i in doc["rules"]["V-65"] if i in v65_still]
if "V-68" in doc["rules"]:
    v68_still = set(re.findall(r"V-68 debt: (\w+) (\S+) is tier", out))  # (table, id); keys add a fingerprint
    assert v68_still, "validate.py output not understood for V-68; nothing written"
    before["V-68"] = len(doc["rules"]["V-68"])
    doc["rules"]["V-68"] = [k for k in doc["rules"]["V-68"] if tuple(k.split(":")[:2]) in v68_still]
BASE.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print("; ".join(f"{r} {n} -> {len(doc['rules'][r])}" for r, n in before.items()))
