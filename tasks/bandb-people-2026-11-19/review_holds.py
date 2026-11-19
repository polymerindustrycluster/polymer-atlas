"""review_holds.csv from the full-set two-family review: a raw-check-passing row is kept only when BOTH families judged it
SOUND. A row a family did not mention, or a review file that did not finish (last line not "exit 0"), holds (fail closed).
    python review_holds.py codex gemini"""
import csv, re, sys
from pathlib import Path

C = Path(__file__).resolve().parent
fams = sys.argv[1:] or ["codex", "gemini"]
rc = [r["lead_id"] for r in csv.DictReader(open(C / "rawcheck.csv", encoding="utf-8"))
      if r["gate_a"] == r["gate_b"] == r["gate_a_surname"] == "yes"]


def verdicts(fam):
    out = {}
    for p in (1, 2):
        lines = (C / f"review_{fam}_part{p}.txt").read_text(encoding="utf-8").splitlines()
        assert lines and lines[-1].strip() == "exit 0", f"{fam} part {p} did not finish: {lines[-1:]}"
        for line in lines:
            m, v = re.search(r"BB-\d{4}", line), re.search(r"\b(SOUND|WRONG|DOUBT)\b", line)
            if m and v:
                out.setdefault(m.group(0), (v.group(1), " ".join(line.split())[:300]))
    return out


V = {f: verdicts(f) for f in fams}
holds = []
for lid in rc:
    bad = [(f, V[f].get(lid, ("MISSING", "row not reviewed"))) for f in fams]
    bad = [(f, v) for f, v in bad if v[0] != "SOUND"]
    if bad:
        holds.append({"lead_id": lid, "reason": " | ".join(f"{f}: {v[0]}: {v[1]}" for f, v in bad)})
with open(C / "review_holds.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["lead_id", "reason"], lineterminator="\n"); w.writeheader(); w.writerows(holds)
for f in fams:
    print(f, sum(1 for lid in rc if V[f].get(lid, ("MISSING",))[0] == "SOUND"), "SOUND of", len(rc))
print("both SOUND", len(rc) - len(holds), "; held", len(holds))
