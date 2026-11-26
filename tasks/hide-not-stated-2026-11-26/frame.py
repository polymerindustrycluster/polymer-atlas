"""Stage 1 of the NOT_STATED hiding PR (owner ruling 2026-11-24 10:29, item 3): build the candidate list, run the repo's own generator
(scripts/value_basis.py) on a scratch copy, and write FRAME.csv, REJECTED.csv, counts.json. No page is opened to judge it, no network, no repo file written.
Usage: python3 -I frame.py REPO PERSIST OUTDIR
  REPO     a polymer-atlas checkout at origin/main (data/, tasks/, scripts/); read only
  PERSIST  the controller persist dir (requote-all-2026-11-24/, pic18-corpus-2026-11-16/ ...): the page store
  OUTDIR   where the outputs go (this folder)
Scratch: $TMPDIR/hide-scratch-*/tasks/ = symlinks to every REPO/tasks folder plus one new folder holding the candidate lines; data/ is read in place."""
import csv, hashlib, json, os, re, shutil, subprocess, sys, tempfile
from collections import Counter, defaultdict
from pathlib import Path

REPO, PERSIST, OUT = (Path(a).resolve() for a in sys.argv[1:4])
PACK = PERSIST / "requote-all-2026-11-24"
SEED = "20261126-hide"
csv.field_size_limit(10**9)
sys.path.insert(0, str(REPO / "scripts"))
import value_basis as vb  # noqa: E402
from regions import PIC18  # noqa: E402

KEYCOLS = ("record_table", "record_id", "field", "value")
key = lambda r: tuple(r[c] for c in KEYCOLS)
rank = lambda r: hashlib.sha256((SEED + "|" + "|".join(key(r))).encode()).hexdigest()
read = lambda p: list(csv.DictReader(open(p, newline="", encoding="utf-8")))


def write(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


# ---------------------------------------------------------------- repo facts
EVID = {e["evidence_id"]: e for e in vb.table_rows(REPO / "data", "evidence")}
SITE_ORG = {s["site_id"]: s["org_id"] for s in vb.table_rows(REPO / "data", "sites")}
CITED = defaultdict(list)
for e in EVID.values():
    CITED[(e["record_table"], e["record_id"])].append(e)


# ---------------------------------------------------------------- 1. candidates (unit: value keys)
def candidates():
    pack = read(PACK / "values.csv")
    by_key = {key(r): r for r in pack}
    assert len(by_key) == len(pack), "values.csv has a duplicate key"
    adj = read(PACK / "second-family/adjudicated.csv")
    holds = read(REPO / "tasks/reread-labels-2026-11-26/HOLDS.csv")
    second = {}  # second-family class per (record, field, value), wherever a second family read it
    for p in (PACK / "second-family/verdicts.csv", PACK / "second-family/round2/verdicts.csv"):
        for v in read(p):
            second[(v["record_id"], v["field"], v["value"])] = v["your_class"]
    adj_by = {(a["record_id"], a["field"], a["value"]): a["adjudicated_class"] for a in adj}
    cand = {}

    def add(r, source, reader_class, second_class):
        k = key(r)
        assert k not in cand, f"duplicate candidate key {k}: {source} and {cand[k]['source']}"
        cand[k] = {**r, "source": source, "reader_class": reader_class, "second_family_class": second_class, "class": "NOT_STATED", "quote": "", "offset": ""}

    for r in pack:
        if r["class"] == "NOT_STATED":
            i = (r["record_id"], r["field"], r["value"])
            add(r, "values", "NOT_STATED", adj_by.get(i) or second.get(i, ""))
    for a in adj:
        if a["adjudicated_class"] == "NOT_STATED":
            (r,) = [x for x in pack if (x["record_id"], x["field"], x["value"]) == (a["record_id"], a["field"], a["value"])]
            assert r["class"] == a["reader_class"] == "IMPLIED", a
            add(r, "adjudicated", "IMPLIED", "NOT_STATED")
    for h in holds:
        if h["reason"].startswith("Gemini 4 Hydrogen census NOT_STATED"):
            r = by_key[key(h)]
            assert r["class"] == "STATED" and h["pack_class"] == "STATED", h
            add(r, "census", "STATED", h["adjudicated_class"])  # verbatim: SITE-001891 reads "NOT_STATED COMPANY_WIDE"
    return cand


# ---------------------------------------------------------------- 2. the generator on a scratch copy
class Scratch:
    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix="hide-scratch-", dir=os.environ.get("TMPDIR")))
        (self.root / "tasks").mkdir()
        for d in sorted((REPO / "tasks").iterdir()):
            if d.is_dir():
                (self.root / "tasks" / d.name).symlink_to(d)
        self.folder = self.root / "tasks" / "hide-not-stated-scratch"
        self.folder.mkdir()
        # The generator loads a packet only when its README names a reader and a different checking family. This stand-in lets it run; it claims no check.
        (self.folder / "README.md").write_text("Read on: 2026-11-24\nRead by: Codex (OpenAI GPT-6.2 Sol)\nChecked by: Gemini (Google Gemini 4 Hydrogen)\n"
                                               "Scratch folder of the stage-1 frame run: lets the generator load the lines; claims no second-family check.\n")

    def run(self, lines):
        """-> (rows, problems, info, why): the generator on these NOT_STATED lines on top of the repo's own tasks; why = {key: the generator's problem}."""
        verdicts = self.folder / "VALUE_VERDICTS.csv"
        write(verdicts, vb.VERDICT_COLS, lines)
        subprocess.run([sys.executable, "-I", str(PACK / "value-pages-builder/build_value_pages.py"), str(PERSIST), str(verdicts), str(self.folder / "VALUE_PAGES.csv")],
                       check=True, capture_output=True)
        rows, problems, info = vb.generate(REPO / "data", self.root / "tasks", PERSIST)
        line_of = {}  # file line number of each record, counted as the generator's csv.reader counts it
        with open(verdicts, newline="", encoding="utf-8") as f:
            rd = csv.reader(f, strict=True)
            next(rd)
            for cells in rd:
                line_of[rd.line_num] = dict(zip(vb.VERDICT_COLS, cells))
        why = {}
        for p in problems:
            if m := re.match(r"tasks/hide-not-stated-scratch/VALUE_VERDICTS\.csv:(\d+): (.*)", p):
                why[key(line_of[int(m[1])])] = m[2]
            elif p.startswith("("):
                k, _, reason = p.partition("): ")
                why[eval(k + ")")] = reason  # the generator prints the key as a Python tuple of strings
            else:
                sys.exit(f"unplaceable problem, stopping: {p}")
        return rows, problems, info, why

    def urls(self):
        return {r["page_sha256"]: (r["page_url"], r.get("requested_url") or "") for r in read(self.folder / "VALUE_PAGES.csv")}

    def close(self):
        shutil.rmtree(self.root, ignore_errors=True)


# ---------------------------------------------------------------- 3. owners known to unknown, the controller harness's definition (harness/pic18_unknown.py)
ORGS = {o["org_id"]: o for o in vb.table_rows(REPO / "data", "organizations")}
ECO = {o["org_id"]: o for o in read(REPO / "data/ecosystem.csv")}
GT = defaultdict(list)
for s in vb.table_rows(REPO / "data", "sites"):
    if s["state"] == "OH" and s["county"] in PIC18 and s["operating_status"] == "active" and s["verification_tier"] in ("A", "B", "C"):
        GT[s["org_id"]].append(s)
R124 = [o for o in GT if (ORGS.get(o) or {}).get("ring_primary") in ("1", "2", "4")]


def known(oid, field, w):
    """The harness's pick(): the union of the owner's PIC-18 site tokens, else its own row's, less the withheld keys."""
    rec = ORGS.get(oid) or ECO.get(oid) or {}
    drop = lambda table, rid: {k[3] for k in w if k[:3] == (table, rid, field)}
    site_t = set().union(*(set(vb.toks(s[field])) - drop("sites", s["site_id"]) for s in GT[oid]))
    return bool(site_t or (set(vb.toks(rec.get(field))) - drop("organizations", oid)))


def owners_to_unknown(w):
    sets = {"proc124": (R124, "processes"), "proc_all": (list(GT), "processes"), "mkt": (list(GT), "markets_served")}
    return {"known_to_unknown": {n: sum(known(o, f, set()) and not known(o, f, w) for o in os_) for n, (os_, f) in sets.items()},
            "unknown_before": {n: sum(not known(o, f, set()) for o in os_) for n, (os_, f) in sets.items()},
            "unknown_after": {n: sum(not known(o, f, w) for o in os_) for n, (os_, f) in sets.items()},
            "universe": {n: len(os_) for n, (os_, f) in sets.items()}}


# ---------------------------------------------------------------- main
def rest_rows(table, rid, token):
    """The rows the generator lets a verdict rest on: the record's own eligible rows naming the value, else (for a site) its organization's."""
    ok = lambda e: (e["claim_type"] in vb.CITING_CLAIMS and e["source_class"] in vb.CITING_CLASSES and e["tier_effect"] != "contradicts"
                    and vb.names(e["claim_detail"], token))
    own = [e for e in CITED[(table, rid)] if ok(e)]
    return own or ([e for t in ("organizations", "ecosystem") for e in CITED[(t, SITE_ORG[rid])] if ok(e)] if table == "sites" else [])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cand = candidates()
    lines = sorted(cand.values(), key=key)
    base = {key(r): r for r in vb.generate(REPO / "data", REPO / "tasks", PERSIST)[0]}  # the repo's own basis table, regenerated (the labels of PR #575 included)
    assert not any(r["basis"] == vb.WITHHELD for r in base.values()), "main already withholds a value"
    for k in cand:
        assert k in base and base[k]["basis"] == "not_yet_checked", f"candidate {k} is {base.get(k, {}).get('basis')} on main, not not_yet_checked"

    sc = Scratch()
    try:
        rows, problems, info, why = sc.run(lines)
        got = {key(r): r for r in rows}
        unbound, urls = set(info["verdict_unbound"]), sc.urls()
        frame, rejected = [], []
        for r in lines:
            k = key(r)
            row = {c: r[c] for c in ("owner", *KEYCOLS, "source", "reader_class", "second_family_class", "page_path", "page_sha256")}
            row["page_url"], row["requested_url"] = urls.get(r["page_sha256"], ("", ""))
            if k in why:
                reason = why[k]
                cause = ("the read page is not on a site any bound row on the record cites" if "is not on a site any bound" in reason else
                         "no bound row to rest on" if "has no bound row" in reason else "other generator problem")
                rejected.append({**row, "cause": cause, "generator_reason": reason})
            elif k in unbound:
                named = [e for e in rest_rows(k[0], k[1], r["value"])]
                rejected.append({**row, "cause": "UNBOUND: the read page is another page of the cited site",
                                 "generator_reason": "value_basis.generate verdict_unbound: same site, another page; no label, the key stays not_yet_checked",
                                 "cited_source_refs": " | ".join(sorted({e["source_ref"] for e in named}))})
            elif got[k]["basis"] == vb.WITHHELD:
                frame.append({**row, "evidence_id": got[k]["evidence_id"],
                              "rests_on": "own record" if EVID[got[k]["evidence_id"]]["record_table"] == k[0] else "organization row"})
            else:
                rejected.append({**row, "cause": f"outranked: basis stays {got[k]['basis']}",
                                 "generator_reason": f"{got[k]['evidence_id']} gives {got[k]['basis']}, which outranks a NOT_STATED verdict"})
        assert len(frame) + len(rejected) == len(lines)
        withheld = {key(r) for r in rows if r["basis"] == vb.WITHHELD}
        assert withheld == {key(r) for r in frame}, "the generator withholds a set the frame does not hold"
        assert len(rejected) == len(lines) - len(frame)

        # convergence: the frame alone runs with no problem, no unbound line, and withholds exactly itself
        frame_lines = [cand[key(r)] for r in frame]
        rows2, problems2, info2, _ = sc.run(frame_lines)
        assert not problems2 and not (set(info2["verdict_unbound"]) & set(cand)) and {key(r) for r in rows2 if r["basis"] == vb.WITHHELD} == withheld, (problems2[:3], set(info2["verdict_unbound"]) & set(cand))

        # independent cross-check (a check, not the definition): every frame line's page is one a bound row on its record cites
        for r in frame:
            cited_pages = {vb.page_key(e["source_ref"]) for e in rest_rows(r["record_table"], r["record_id"], r["value"])}
            assert {vb.page_key(r["page_url"]), vb.page_key(r["requested_url"])} & cited_pages, f"frame line {key(r)}: its page {r['page_url']} is not cited by a bound row"

        # plants (a check must fail on the defect it exists to catch): a wrong owner, and a page of another owner's folder, must each draw a problem
        bad = dict(frame_lines[0], owner="ORG-999999")
        _, p3, _, w3 = sc.run([bad] + frame_lines[1:])
        assert len(p3) == 1 and key(bad) in w3, p3
        other = next(r for r in frame_lines if r["owner"] != frame_lines[0]["owner"])
        bad2 = dict(frame_lines[0], page_path=other["page_path"], page_sha256=other["page_sha256"])
        _, p4, _, w4 = sc.run([bad2] + frame_lines[1:])
        assert key(bad2) in w4, p4

        # pilot (AGENTS 2a rule 8b): 30 frame lines by SHA-256 rank of the seed and the key
        pilot_lines = sorted(frame_lines, key=rank)[:30]
        prow, pprob, pinfo, _ = sc.run(pilot_lines)
        pw = {key(r) for r in prow if r["basis"] == vb.WITHHELD}
        pilot = {"drawn": len(pilot_lines), "withheld": len(pw), "problems": len(pprob), "unbound": len(set(pinfo["verdict_unbound"]) & set(cand)),
                 "by_field": dict(Counter(k[2] for k in pw)), "by_table": dict(Counter(k[0] for k in pw)), "owners": owners_to_unknown(pw),
                 "distinct_owners": len({r["owner"] for r in pilot_lines}), "keys": sorted(map(list, pw)),
                 "rests_on": dict(Counter(r["rests_on"] for r in frame if key(r) in pw))}
    finally:
        sc.close()

    cols = ["record_table", "record_id", "owner", "field", "value", "source", "page_path", "page_sha256", "page_url"]
    write(OUT / "FRAME.csv", cols + ["reader_class", "second_family_class", "rests_on", "evidence_id", "requested_url"], frame)
    write(OUT / "REJECTED.csv", cols + ["reader_class", "second_family_class", "cause", "generator_reason", "cited_source_refs", "requested_url"], rejected)
    own = {key(r) for r in frame if r["rests_on"] == "own record"}  # SCHEMA 4.24 grain: a row on the organization gives a site's value at most not_yet_checked
    firm = {key(r) for r in frame if not r["second_family_class"].startswith(("STATED", "IMPLIED"))}  # drops the line the second family already read STATED
    counts = {"candidates": len(lines), "candidates_by_source": dict(Counter(r["source"] for r in lines)),
              "candidates_by_second_family_class": dict(Counter(f"{r['source']}/{r['second_family_class'] or 'none'}" for r in lines)),
              "frame": len(frame), "frame_by_field": dict(Counter(r["field"] for r in frame)), "frame_by_source": dict(Counter(r["source"] for r in frame)),
              "frame_by_table": dict(Counter(r["record_table"] for r in frame)), "frame_rests_on": dict(Counter(r["rests_on"] for r in frame)),
              "frame_by_second_family_class": dict(Counter(f"{r['source']}/{r['second_family_class'] or 'none'}" for r in frame)),
              "rejected": len(rejected), "rejected_by_cause": dict(Counter(r["cause"] for r in rejected)),
              "rejected_by_source": dict(Counter(r["source"] for r in rejected)),
              "pilot": pilot,
              "full": {"values_withheld_by_field": dict(Counter(k[2] for k in withheld)), "by_table": dict(Counter(k[0] for k in withheld)),
                       "frame_owners": len({r["owner"] for r in frame}), "owners": owners_to_unknown(withheld)},
              "full_without_second_family_up": {"values_withheld_by_field": dict(Counter(k[2] for k in firm)), "owners": owners_to_unknown(firm)},
              "full_own_record_only": {"values_withheld_by_field": dict(Counter(k[2] for k in own)), "owners": owners_to_unknown(own)}}
    json.dump(counts, open(OUT / "counts.json", "w"), indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in counts.items() if k != "pilot"}, indent=1, sort_keys=True))
    print("PILOT", json.dumps({k: v for k, v in pilot.items() if k != "keys"}, sort_keys=True))


if __name__ == "__main__":
    main()
