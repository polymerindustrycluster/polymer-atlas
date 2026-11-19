"""review_holds.csv from the full-set two-family review: a raw-check-passing row is kept only when BOTH families judged it
SOUND. Fails closed:
  - codex plus at least one other distinct family are required;
  - a review file that did not finish (last line not "exit 0") stops the run, and the old holds file is deleted first, so
    a stale one cannot survive;
  - a row a family did not mention holds;
  - a row holds if ANY line naming it carries WRONG, DOUBT, "not SOUND" or "unsound" (all lines, not the first).
    python review_holds.py codex gemini"""
import csv, re, sys
from pathlib import Path

C = Path(__file__).resolve().parent
OUT = C / "review_holds.csv"
OUT.unlink(missing_ok=True)
fams = sys.argv[1:]
assert "codex" in fams and len(set(fams)) >= 2, "need codex plus at least one other distinct family"
rc = [r["lead_id"] for r in csv.DictReader(open(C / "rawcheck.csv", encoding="utf-8"))
      if r["gate_a"] == r["gate_b"] == r["gate_a_surname"] == "yes"]
WORD = re.compile(r"(?i)\b(not\s+sound|unsound|sound|wrong|doubt)\b")


def verdicts(fam):
    words, lines_for = {}, {}
    for p in (1, 2):
        lines = (C / f"review_{fam}_part{p}.txt").read_text(encoding="utf-8").splitlines()
        assert lines and lines[-1].strip() == "exit 0", f"{fam} part {p} did not finish: {lines[-1:]}"
        for line in lines:
            ws = {" ".join(w.lower().split()) for w in WORD.findall(line)}
            for lid in set(re.findall(r"BB-\d{4}", line)):
                words.setdefault(lid, set()).update(ws)
                if lid not in lines_for or ws - {"sound"}:  # quote the line that carries the objection
                    lines_for[lid] = " ".join(line.split())[:300]
    return {lid: ("SOUND" if ws == {"sound"} else "/".join(sorted(ws - {"sound"})).upper() or "NO VERDICT", lines_for[lid])
            for lid, ws in words.items()}


V = {f: verdicts(f) for f in dict.fromkeys(fams)}
holds = []
for lid in rc:
    bad = [(f, V[f].get(lid, ("MISSING", "row not reviewed"))) for f in V]
    bad = [(f, v) for f, v in bad if v[0] != "SOUND"]
    if bad:
        holds.append({"lead_id": lid, "reason": " | ".join(f"{f}: {v[0]}: {v[1]}" for f, v in bad)})
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["lead_id", "reason"], lineterminator="\n"); w.writeheader(); w.writerows(holds)
for f in V:
    print(f, sum(1 for lid in rc if V[f].get(lid, ("MISSING",))[0] == "SOUND"), "SOUND of", len(rc))
print("both SOUND", len(rc) - len(holds), "; held", len(holds))
