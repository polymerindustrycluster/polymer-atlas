"""Rows whose notes may name an individual. Output is path:line only; no name is copied anywhere (DESIGN.md §8).
The splitter pins such a PIECE to the row (notes_split._PERSON); this script lists the rows for the owner.
Positive control (run in __main__): the pattern must flag data/evidence_organizations_OH.csv:3235, an evidence note that names an individual."""
import re, csv, os
from load import load, DATA
N = r"[A-Z][a-z]+(?:\s[A-Z]\.?)?\s[A-Z][a-z']+(?:-[A-Z][a-z]+)?"
PATS = [r"[\w.+-]+@[\w-]+\.[\w.-]+", r"(?<!\d)(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}(?!\d)",
        r"\b(?:CEO|CFO|COO|CTO|President|Owner|Founder|Founder/CEO|Co-?founder|Vice President|VP|Mr\.|Mrs\.|Ms\.)\s+" + N,
        r"\b(?:signed by|reviewed by|verified by|approved by|contact(?:ed)?:?|reviewer|attn\.?)\s+" + N,
        r"\b[A-Z] [A-Z][a-z]+ [A-Z][a-z]+ (?:Jr|Sr|II|III)\.? (?:Trust|Estate)\b"]
RX = [re.compile(p) for p in PATS]
def scan(text): return any(p.search(text) for p in RX)
if __name__ == "__main__":
    n = 0
    for t in ("organizations", "sites"):
        for r in load(t):
            if scan(r["notes"]): print(f"data/{r['_file']}:{r['_line']}"); n += 1
    ev = os.path.join(DATA, "evidence_organizations_OH.csv")
    rows = list(csv.reader(open(ev, newline="", encoding="utf-8")))
    ctl = scan(" ".join(rows[3234 - 1]))  # file line 3235 = csv.reader row index 3234 only if no multiline fields; fall back below
    if not ctl:
        ctl = any(scan(" ".join(r)) and "B-PPP" in " ".join(r) for r in rows)
    print("flagged note rows:", n, "| positive control on evidence shard (expects True):", ctl)
    assert ctl, "person pattern failed its positive control"
