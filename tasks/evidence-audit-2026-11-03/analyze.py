"""Evidence audit, step 3: merge judge verdicts, verify every quote word for word against its saved page, and report
support rates (Wilson 95% CI) overall and by claim type / creating harness, plus Sonnet-vs-Codex agreement."""
import csv, math, re, sys, unicodedata
from collections import Counter, defaultdict
from pathlib import Path

D = Path(sys.argv[1])
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8")))
sample = {r["evidence_id"]: r for r in rd(D / "sample.csv")}
words = lambda s: re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower())


def on_page(q, f):
    q = words(q)
    if not q:
        return None
    p = words(Path(f).read_text(encoding="utf-8"))
    return any(p[i:i + len(q)] == q for i in range(len(p) - len(q) + 1))


def wilson(k, n, z=1.96):
    if not n:
        return (0, 0)
    c = (k + z * z / 2) / (n + z * z); h = z * math.sqrt(k * (n - k) / n + z * z / 4) / (n + z * z)
    return (round(100 * (c - h)), round(100 * (c + h)))


son = {}
for k in "ABCD":
    for r in rd(D / f"judge_out_{k}.csv"):
        son[r["evidence_id"]] = r
cod = {r["evidence_id"]: r for r in rd(D / "judge_out_X.csv")} if (D / "judge_out_X.csv").exists() else {}
ok = [e for e, s in sample.items() if s["fetch_status"] == "ok"]
missing = [e for e in ok if e not in son]
print(f"sample {len(sample)}; fetched {len(ok)}; judged {len(son)}; missing verdicts {len(missing)}")

# a SUPPORTED/PARTIAL whose quote is not on the page is downgraded: the judge's support is unverified
final = {}
bad_quote = 0
for e in ok:
    v = son.get(e, {}).get("verdict", "MISSING").strip()
    if v in ("SUPPORTED", "PARTIAL") and on_page(son[e].get("quote", ""), sample[e]["page_file"]) is not True:
        bad_quote += 1
        v = v + "_QUOTE_UNVERIFIED"
    final[e] = v
print("judge quotes not found verbatim:", bad_quote)
print("final verdicts (fetched pages):", Counter(final.values()).most_common())
dead = Counter(s["fetch_status"].split(":")[0] for s in sample.values() if s["fetch_status"] != "ok")
print("not fetchable today:", dict(dead))

judgeable = [e for e in ok if final[e] not in ("CANNOT_JUDGE", "MISSING")]
sup = [e for e in judgeable if final[e] == "SUPPORTED"]
lo, hi = wilson(len(sup), len(judgeable))
print(f"\nSUPPORTED {len(sup)}/{len(judgeable)} judgeable = {100*len(sup)/len(judgeable):.0f}% (95% CI {lo}-{hi}%)")
supp = [e for e in judgeable if final[e] in ("SUPPORTED", "PARTIAL")]
lo2, hi2 = wilson(len(supp), len(judgeable))
print(f"SUPPORTED or PARTIAL {len(supp)}/{len(judgeable)} = {100*len(supp)/len(judgeable):.0f}% (95% CI {lo2}-{hi2}%)")
allrows = len(sample)
print(f"strict, whole sample (unfetchable and cannot-judge count against): {len(sup)}/{allrows} = {100*len(sup)/allrows:.0f}%")

def harness(c):
    c = c.lower()
    for k in ("muse", "spaghetti", "dot", "duet", "claude", "codex", "grok", "pass"):
        if k in c:
            return k
    return c[:20] or "?"

for label, key in (("claim_type", lambda e: sample[e]["claim_type"]), ("created_by", lambda e: harness(sample[e]["created_by"])),
                   ("record_table", lambda e: sample[e]["record_table"]), ("observed year-month", lambda e: sample[e]["observed_date"][:7])):
    g = defaultdict(list)
    for e in judgeable:
        g[key(e)].append(final[e] == "SUPPORTED")
    print(f"\nby {label}:")
    for k, v in sorted(g.items(), key=lambda kv: -len(kv[1])):
        a, b = wilson(sum(v), len(v))
        print(f"  {k:28} {sum(v):3}/{len(v):3} supported ({a}-{b}%)")

if cod:
    both = [e for e in cod if e in son]
    exact = sum(cod[e]["verdict"].strip() == son[e]["verdict"].strip() for e in both)
    binary = sum((cod[e]["verdict"].strip() == "SUPPORTED") == (son[e]["verdict"].strip() == "SUPPORTED") for e in both)
    print(f"\nSonnet vs Codex on {len(both)}: exact verdict agree {exact}, SUPPORTED-vs-not agree {binary}")
    print("disagreements:", [(e, son[e]["verdict"], cod[e]["verdict"]) for e in both if cod[e]["verdict"].strip() != son[e]["verdict"].strip()])

with open(D / "audit_rows.csv", "w", newline="", encoding="utf-8") as fh:
    cols = ["evidence_id", "record_table", "record_id", "record_name", "claim_type", "created_by", "observed_date", "url",
            "fetch_status", "verdict", "quote", "reason", "codex_verdict"]
    w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n"); w.writeheader()
    for e, s in sample.items():
        j = son.get(e, {})
        w.writerow({**{c: s.get(c, "") for c in cols}, "verdict": final.get(e, "UNFETCHABLE"), "quote": j.get("quote", ""),
                    "reason": j.get("reason", ""), "codex_verdict": cod.get(e, {}).get("verdict", "")})
