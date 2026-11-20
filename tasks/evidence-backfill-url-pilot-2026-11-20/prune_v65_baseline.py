#!/usr/bin/env python3
"""Shrink V-65's grandfathered list by the records this lane evidenced (the baseline file's doctrine: an ID leaves the
list when a lane evidences the record). Asks validate.py which baselined V-65 IDs still violate and drops the rest.
The 'amended' note is left alone so this PR does not conflict with others editing it; the README records the shrink.

    python3 tasks/evidence-backfill-url-pilot-2026-11-20/prune_v65_baseline.py     (from the repo root)
"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "scripts" / "validate_debt_baseline.json"
out = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate.py"), "--debt-details"],
                     capture_output=True, text=True, encoding="utf-8", cwd=ROOT).stdout
still = set(re.findall(r"V-65 debt: \w+ (\S+) is tier", out))
doc = json.loads(BASE.read_text(encoding="utf-8"))
old = doc["rules"]["V-65"]
assert still and still <= set(old), "validate.py output not understood; nothing written"
drop = [i for i in old if i not in still]
doc["rules"]["V-65"] = [i for i in old if i in still]
BASE.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print(f"V-65 baseline {len(old)} -> {len(still)}; dropped {len(drop)}: {', '.join(drop)}")
