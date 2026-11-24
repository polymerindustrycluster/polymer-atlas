"""Build canary.csv (before/after per record) and canary_history.csv (the proposed data/record_history.csv shape, one row per piece).
Reads data/ only; writes only inside this folder. Deterministic: re-running gives identical files."""
import csv, json, re
from corpus import run
from notes_split import after_note, kind_of, tidy
import canary_decisions as C

AGENTS = re.compile(r"\b(Grok|spaghetti|Muse|Codex|Gemini|Antigravity|Claude|pass-\d+ integrator|pass \d+ integrator|integrator)\b", re.I)
DATE = re.compile(r"\d{4}-\d\d-\d\d")

def resolve(part, dec):
    d = part["disp"]
    if d != "READER":
        return d, part["restated"], "script"
    x = dec[part["seq"]]
    return x[0], (x[1] if x[0] == "RESTATE" else None), "reader: " + (x[-1] if x[0] != "KEEP" else "kept as written")

def main():
    orgs, sites = run()
    by = {r["_id"]: r for r in orgs + sites}
    lab = json.load(open("canary_ids.json"))
    canary, hist = [], []
    for rid in sorted(lab):
        r = by[rid]; parts = r["_parts"]; dec = C.D.get(rid, {})
        res = [resolve(p, dec) for p in parts]
        row_pieces = []
        for p, (d, rest, who) in zip(parts, res):
            on = {"KEEP": "kept", "MOVE": "moved", "RESTATE": "restated", "PERSON": "person-held"}[d]
            if d == "PERSON": row_pieces.append(p["text"].strip())
            elif d == "KEEP": row_pieces.append(tidy(p["text"]))
            elif d == "RESTATE": row_pieces.append(rest)
            hist.append({"table": r["_table"], "record_id": rid, "seq": p["seq"], "n_pieces": len(parts), "on_row": on,
                         "text": "" if d == "PERSON" else p["text"], "restated_as": rest or "", "kind": kind_of(p["text"]),
                         "first_date": (lambda m: m.group(0) if m else "")(DATE.search(p["text"])), "actor": (lambda m: m.group(0) if m else "")(AGENTS.search(p["text"])),
                         "decided_by": who})
        after = " ".join(row_pieces)
        canary.append({"record_id": rid, "table": r["_table"], "tier": r["verification_tier"], "chosen_as": lab[rid], "source_line": f"data/{r['_file']}:{r['_line']}",
                       "before": r["notes"], "after": after,
                       "pieces": len(parts), "kept": sum(x[0] == "KEEP" for x in res), "moved": sum(x[0] == "MOVE" for x in res),
                       "restated": sum(x[0] == "RESTATE" for x in res), "reader_decisions": sum(p["disp"] == "READER" for p in parts)})
    for n, h in enumerate(hist, 1): h["history_id"] = f"HST-{n:06d}"
    cols = ["history_id", "table", "record_id", "seq", "n_pieces", "on_row", "text", "restated_as", "kind", "first_date", "actor", "decided_by"]
    with open("canary_history.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, cols, lineterminator="\n"); w.writeheader(); w.writerows(hist)
    cc = list(canary[0])
    with open("canary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, cc, lineterminator="\n"); w.writeheader(); w.writerows(canary)
    print(len(canary), "records;", len(hist), "pieces;", {k: sum(c[k] for c in canary) for k in ("kept", "moved", "restated", "reader_decisions")})

if __name__ == "__main__":
    main()
