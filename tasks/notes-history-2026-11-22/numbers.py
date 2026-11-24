"""Prints every number DESIGN.md quotes in §0 (count reconciliation), §1 (taxonomy), §5 (what a script can do alone). Reads data/ only."""
import re, collections, json
from corpus import run
from load import load
from sample200 import sample
from notes_split import kind_of
import check
orgs, sites = run()
by = {r["_id"]: r for r in orgs + sites}
print("== §0 count reconciliation (rows with a hit; organizations / sites)")
for label, rx in {"my agent|pass regex": r"Grok|spaghetti|Muse|Codex|Claude|[Pp]ass[- ]\d+|PASS \d+|integration pass",
                  "wide pipeline vocabulary": r"[Pp]ass[- ]\d+|PASS \d+|integration pass|wave|verdict|staging|packet|lane|burn-down|integrator|Grok|spaghetti",
                  "controller-style (stats.py)": r"Grok|spaghetti|PASS \d|verdicts\.csv|staging|working/|burn-down|integrator assert"}.items():
    c = re.compile(rx); print(f"  {label}: {sum(1 for r in orgs if c.search(r['notes']))} / {sum(1 for r in sites if c.search(r['notes']))}")
print("  this lane's word list (notes_split.hits):", sum(1 for r in orgs if check.NS.hits(r['notes'])), "/", sum(1 for r in sites if check.NS.hits(r['notes'])))
print("  empty notes:", sum(1 for r in orgs if not r["notes"].strip()), "/", sum(1 for r in sites if not r["notes"].strip()))
print("== §1 taxonomy: pieces / notes (200-note sample), pieces / rows (all)")
s = sample(); cp, cn, ca, cr = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
for x in s:
    seen = set()
    for p in by[x["id"]]["_parts"]: k = kind_of(p["text"]); cp[k] += 1; seen.add(k)
    for k in seen: cn[k] += 1
for r in orgs + sites:
    seen = set()
    for p in r["_parts"]: k = kind_of(p["text"]); ca[k] += 1; seen.add(k)
    for k in seen: cr[k] += 1
for k in sorted(ca): print(f"  {k}: sample {cp[k]}/{cn[k]}  all {ca[k]}/{cr[k]}")
print("== §5 dispositions (pieces) and reader kinds")
for name, rows in (("organizations", orgs), ("sites", sites)):
    d = collections.Counter(p["disp"] for r in rows for p in r["_parts"]); rk = collections.Counter(p["kind"] for r in rows for p in r["_parts"] if p["disp"] == "READER")
    nr = sum(1 for r in rows if any(p["disp"] == "READER" for p in r["_parts"]))
    rx = re.compile(r"Grok|spaghetti|Muse|Codex|Claude|[Pp]ass[- ]\d+|PASS \d+|integration pass")
    b = sum(1 for r in rows if rx.search(r["notes"])); a1 = sum(1 for r in rows if rx.search(check.group_after(r["_parts"], "script-only"))); a2 = sum(1 for r in rows if rx.search(check.group_after(r["_parts"], "worst-case")))
    r1 = sum(1 for r in rows if check.residue(check.group_after(r["_parts"], "script-only"))); r2 = sum(1 for r in rows if check.residue(check.group_after(r["_parts"], "worst-case")))
    print(f" {name} rows {len(rows)}: {dict(d)} | reader kinds {dict(rk)} | rows needing a reader {nr} | agent|pass regex before {b} after script-only {a1} worst {a2} | independent residue rows script-only {r1} worst {r2}")
print(" script-alone:", json.load(open("script_alone.json")) if __import__("os").path.exists("script_alone.json") else "run check.py first")
