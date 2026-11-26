"""Build VALUE_VERDICTS.csv, VALUE_PAGES.csv and HOLDS.csv in this folder from the 2026-11-24 re-read pack (outside the repo).
Usage: python3 -I tasks/reread-labels-2026-11-26/build.py PERSIST_DIR [--pilot]
PERSIST_DIR holds requote-all-2026-11-24/ (values.csv, second-family/adjudicated.csv), the page store and value-pages-builder/.
Scope: STATED and IMPLIED lines only. Lines are copied verbatim, except that a second-family adjudication replaces the class
(an IMPLIED line carries no quote or offset, SCHEMA §4.24). A line the generator would stop on is left out and listed in HOLDS.csv
with the generator's own reason; an adjudication to NOT_STATED, or a NOT_STATED line adjudicated up, is listed too (never labelled
here, never withheld here). --pilot writes only a seeded draw of 25 STATED + 5 IMPLIED lines (AGENTS §2a rule 8b)."""
import ast, csv, hashlib, re, subprocess, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import value_basis as vb  # noqa: E402

csv.field_size_limit(10**9)
SEED = "20261126-labels"
REL = f"tasks/{HERE.name}/VALUE_VERDICTS.csv"


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


key = lambda r: (r["record_table"], r["record_id"], r["field"], r["value"])
rank = lambda r: hashlib.sha256((SEED + "|" + "|".join(key(r))).encode()).hexdigest()


def candidates(pack, census=True):
    """-> (lines to try, holds): the pack's STATED and IMPLIED lines with the 2026-11-24 adjudications applied and, unless census=False,
    the 2026-11-26 Gemini census adjudication (second-family/ADJUDICATION-census.csv): `implied` sets the class (and clears the quote and offset an
    IMPLIED line may not carry); `hold` removes the line, listed in HOLDS.csv with the census reason."""
    lines, holds = read(pack / "values.csv"), []
    by_key = {(r["owner"],) + key(r)[1:]: r for r in lines}
    for a in read(pack / "second-family/adjudicated.csv"):
        r = by_key[(a["owner"], a["record_id"], a["field"], a["value"])]
        assert r["class"] == a["reader_class"], f"adjudication {a['record_id']} {a['value']}: pack class is {r['class']}"
        new = a["adjudicated_class"]
        if r["class"] == "STATED" and new == "IMPLIED":
            r.update({"class": "IMPLIED", "quote": "", "offset": ""})  # a stricter label: the quote no longer stands
        else:  # NOT_STATED adjudicated or adjudicated up from NOT_STATED: no label and no withholding here
            reason = ("adjudicated to NOT_STATED: for the hiding PR" if new == "NOT_STATED" else
                      f"pack NOT_STATED adjudicated to {new}: a label needs {'a quote and offset' if new == 'STATED' else 'its witness page, which is not the cited page'}")
            holds.append({"record_table": r["record_table"], "record_id": r["record_id"], "field": r["field"], "value": r["value"],
                          "pack_class": r["class"], "adjudicated_class": new, "reason": reason})
            r["class"] = "HELD"
    for a in read(HERE / "second-family/ADJUDICATION-census.csv") if census else []:
        (r,) = [r for r in lines if key(r) == key(a)]
        assert (r["class"], a["pack_class"]) == ("STATED", "STATED"), f"census line {key(a)}: the line is {r['class']}"
        if a["action"] == "implied":
            r.update({"class": "IMPLIED", "quote": "", "offset": ""})
        else:
            assert a["action"] == "hold", a
            holds.append({"record_table": r["record_table"], "record_id": r["record_id"], "field": r["field"], "value": r["value"],
                          "pack_class": "STATED", "adjudicated_class": a["census_class"], "reason": a["reason"]})
            r["class"] = "HELD"
    return [r for r in lines if r["class"] in ("STATED", "IMPLIED")], holds


def run(pack, pages, lines):
    """Write the candidate files, run the generator, return its problems."""
    write(HERE / "VALUE_VERDICTS.csv", vb.VERDICT_COLS, lines)
    subprocess.run([sys.executable, "-I", str(pages / "requote-all-2026-11-24/value-pages-builder/build_value_pages.py"), str(pages),
                    str(HERE / "VALUE_VERDICTS.csv"), str(HERE / "VALUE_PAGES.csv")], check=True)
    _, problems, info = vb.generate(ROOT / "data", ROOT / "tasks", pages)
    return problems, info


def unbound(lines, keys):
    """UNBOUND.csv: the lines whose read page is another page of the cited site (no label here), for the follow-up PR that adds own-site rows."""
    urls = {r["page_sha256"]: r["page_url"] for r in read(HERE / "VALUE_PAGES.csv")}
    cited = {}
    for e in vb.table_rows(ROOT / "data", "evidence"):
        cited.setdefault((e["record_table"], e["record_id"]), []).append(e)
    out = []
    for r in lines:
        if key(r) in set(keys):
            rows = [e for e in cited.get(key(r)[:2], []) if e["claim_type"] in vb.CITING_CLAIMS and vb.names(e["claim_detail"], r["value"])]
            out.append({"record_table": r["record_table"], "record_id": r["record_id"], "field": r["field"], "value": r["value"], "class": r["class"],
                        "read_page_url": urls[r["page_sha256"]], "cited_source_refs": " | ".join(sorted({e["source_ref"] for e in rows}))})
    write(HERE / "UNBOUND.csv", ["record_table", "record_id", "field", "value", "class", "read_page_url", "cited_source_refs"], out)


def main():
    pages, pilot = Path(sys.argv[1]), "--pilot" in sys.argv
    pack = pages / "requote-all-2026-11-24"
    lines, holds = candidates(pack)
    if pilot:
        lines = sorted((r for r in lines if r["class"] == "STATED"), key=rank)[:25] + sorted((r for r in lines if r["class"] == "IMPLIED"), key=rank)[:5]
        holds = []
    drop = {}
    while (problems_info := run(pack, pages, lines))[0]:
        problems = problems_info[0]
        for p in problems:
            if m := re.match(rf"{re.escape(REL)}:(\d+): ", p):
                k, why = key(lines[int(m[1]) - 2]), p[m.end():]  # file line 1 is the header
            elif p.startswith("("):
                k, why = ast.literal_eval(p.split("): ", 1)[0] + ")"), p.split("): ", 1)[1]
            else:
                sys.exit(f"unplaceable problem, stopping: {p}")
            drop[k] = why
        if pilot:
            print("PILOT problems:", *problems, sep="\n  ")
            break
        before = len(lines)
        lines = [r for r in lines if key(r) not in drop]
        assert len(lines) < before, "no progress"
    unbound(lines, problems_info[1]["verdict_unbound"])
    holds += [{"record_table": k[0], "record_id": k[1], "field": k[2], "value": k[3], "pack_class": "", "adjudicated_class": "", "reason": why}
              for k, why in sorted(drop.items())]
    write(HERE / "HOLDS.csv", ["record_table", "record_id", "field", "value", "pack_class", "adjudicated_class", "reason"], holds)
    print(f"{len(lines)} lines {dict(Counter(r['class'] for r in lines))}; holds {len(holds)}")


if __name__ == "__main__":
    main()
