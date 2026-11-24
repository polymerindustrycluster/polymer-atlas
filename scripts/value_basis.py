#!/usr/bin/env python3
"""Generate data/value_basis.csv, the per-value basis table of SCHEMA §4.24. Stdlib only.

One row per (record_table, record_id, field, value) for every processes / markets_served value an organization or
site row holds that a bound evidence row names. The table is derived, never authored: validator V-69 fails when it
differs from a fresh generation. Run `python3 scripts/value_basis.py` to rewrite it, `--check` to compare,
`--summary` for the PIC-18 counts by basis.

Precedence (SCHEMA §4.24, v1.20.1). The first line that holds for a key decides its basis (an own-record row is preferred to an organization row when
a row must stand for the value):
  1. stated   a verified quote: an own_site row on the SAME record, naming exactly this value, quoting the page, with a
              VERIFIED line in its folder's BINDING_PROOF.csv whose claim_sha256 still matches the row (the gate
              replayed the capture when the row merged), OR the latest reader verdict for the key is STATED and
              replays against its stored page.
  2. filing   a government_filing row on the SAME record naming exactly this value and carrying the filing's words.
  3. latest reader verdict: IMPLIED -> implied; NOT_STATED -> not_found_pending_refetch. The latest read_date wins;
              two verdict classes on one latest date is an error, never a silent pick.
  4. not_yet_checked   any other bound row (a row on the organization counts for its sites) that names the value; a value
              no bound row names also gets this basis, with an empty evidence_id (owner-controller ruling 2026-11-24).
A `contradicts` row and a harvest_roster or platform_category row are never a source. A row on another record settles
no `stated` or `filing`: a corporate statement does not settle a plant claim.
"""
import argparse
import csv
import hashlib
import io
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_evidence_binding as gate  # noqa: E402  (reused for proof checks; its TREE is never read here)

FIELDS = ("processes", "markets_served")
COLS = ["record_table", "record_id", "field", "value", "basis", "evidence_id", "basis_date"]
BASIS = ("stated", "filing", "implied", "not_yet_checked", "not_found_pending_refetch")
WITHHELD = "not_found_pending_refetch"
LABELS = {"stated": "stated", "filing": "from a filing", "implied": "implied", "not_yet_checked": "not yet checked"}
# The re-read lane's values.csv format, used as is. NO_PAGE lines carry no verdict and are skipped.
VERDICT_COLS = ("owner", "record_table", "record_id", "field", "value", "class", "quote", "page_path", "page_sha256",
                "offset", "grain", "note")
VERDICT_CLASS = {"STATED": "stated", "IMPLIED": "implied", "NOT_STATED": WITHHELD}
CITING_CLASSES = {"own_site", "government_filing", "registry", "press", "directory"}
CITING_CLAIMS = {"activity", "scope"}
ISO = re.compile(r"\d{4}-\d{2}-\d{2}")
SHA = re.compile(r"[0-9a-f]{64}")
QUOTE_MIN, QUOTE_MAX = 20, 200  # characters: the gate's floor and the re-read lane's cap


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def table_rows(data, prefix):
    return [r for p in sorted(data.glob(f"{prefix}_*.csv")) for r in read_csv(p)]


def toks(value):
    return [t.strip() for t in (value or "").split(";") if t.strip() and t.strip() != "unknown"]


def names(text, token):
    return re.search(r"(?<![a-z0-9_])" + re.escape(token) + r"(?![a-z0-9_])", text) is not None


def head_and_quote(detail):
    """(assertion, quote): the quote is everything after the first 'quote:', as the gate splits a proof; the assertion is
    what comes before the first 'quote:' or 'process excerpt:', so the witness's own words never decide which value a row asserts."""
    _, _, quote = detail.partition("quote:")
    return re.split(r"quote:|process excerpt:", detail, maxsplit=1)[0], gate.norm_space(quote)


def replay(v, pages):
    """'' when the quote sits at its offset in the stored page's capture text; else the reason it does not."""
    path = Path(pages) / v["page_path"]
    try:
        data = path.resolve().read_bytes() if path.resolve().is_relative_to(Path(pages).resolve()) else None
    except OSError:
        data = None
    if data is None or hashlib.sha256(data).hexdigest() != v["page_sha256"]:
        return "stored page missing from the store or its sha256 differs"
    try:
        text = gate.capture_text(data)
    except UnicodeDecodeError:
        return "stored page is not UTF-8"
    start = int(v["offset"])
    return "" if text[start:start + len(v["quote"])] == v["quote"] else "quote is not at that offset in the stored page"


def packet_meta(folder):
    """(read date, reader family, checker family) from the packet README, or None. A packet counts only when a second,
    different family has checked it (controller ruling 2026-11-24: labels publish only after the second-family check)."""
    path = folder / "README.md"
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    field = lambda name: (re.search(rf"^\W*{name}:\s*(.+)$", text, re.M | re.I) or [None, ""])[1].strip()
    date = ISO.search(field("Read on"))
    reader, checker = gate.family_of_text(field("Read by")), gate.family_of_text(field("Checked by"))
    return (date[0], reader, checker) if date and reader and checker and reader != checker else None


PAGE_COLS = ("page_sha256", "page_url")  # optional third column `requested_url`: the URL a redirected capture was requested as


def site_of(url):
    host, _ = gate.host_path(url)
    return gate.registrable(host) if host else ""


def page_key(url):
    """Normalized (host, path) of a URL: the gate's own normalization (no scheme, www, query, fragment or trailing slash)."""
    return gate.host_path(url) if url else ("", "")


def load_page_urls(folder, problems):
    """tasks/<folder>/VALUE_PAGES.csv: {page sha256: (page_url, requested_url)} from the lane's corpus manifest."""
    path = folder / "VALUE_PAGES.csv"
    if not path.exists():
        return {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if tuple(reader.fieldnames or ()) not in (PAGE_COLS, PAGE_COLS + ("requested_url",)):
            problems.append(f"{path}: header must be {','.join(PAGE_COLS)}[,requested_url]")
            return {}
        return {r["page_sha256"]: (r["page_url"], r.get("requested_url") or "") for r in reader}


def load_verdicts(tasks, problems, held):
    """tasks/<folder>/VALUE_VERDICTS.csv lines (values.csv format), shape-checked. -> [(line dict, read date)]."""
    out = []
    for path in sorted(tasks.glob("*/VALUE_VERDICTS.csv")):
        rel = path.relative_to(tasks.parent)
        meta = packet_meta(path.parent)
        if meta is None:
            problems.append(f"{rel}: README.md needs 'Read on: <date>', 'Read by: <family>' and 'Checked by: <a different family>'; "
                            f"until then the packet publishes no label")
            continue
        urls = load_page_urls(path.parent, problems)
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, strict=True)
            if tuple(next(reader, [])) != VERDICT_COLS:
                problems.append(f"{rel}: header must be {','.join(VERDICT_COLS)}")
                continue
            for cells in reader:
                at = f"{rel}:{reader.line_num}"
                v = dict(zip(VERDICT_COLS, cells))
                v["_at"] = at
                v["_url"], v["_requested"] = urls.get(v.get("page_sha256"), ("", ""))
                why = verdict_shape(v) if len(cells) == len(VERDICT_COLS) else f"{len(cells)} cells, the header has {len(VERDICT_COLS)}"
                key = (v.get("record_table"), v.get("record_id"), v.get("field"), v.get("value"))
                if not why and v["class"] != "NO_PAGE" and key not in held:
                    why = f"the record does not hold {v['value']!r} in {v['field']}"
                if why:
                    problems.append(f"{at}: {why}")
                elif v["class"] != "NO_PAGE":
                    out.append((v, meta[0]))
    return out


def verdict_shape(v):
    if v["class"] == "NO_PAGE":
        return "" if not (v["quote"] or v["page_sha256"] or v["offset"]) else "a NO_PAGE line carries no quote, page or offset"
    if v["class"] not in VERDICT_CLASS or v["field"] not in FIELDS or v["record_table"] not in ("organizations", "sites"):
        return "class, field or record_table is outside the closed vocabulary"
    if not (SHA.fullmatch(v["page_sha256"]) and v["page_path"]):
        return "a read needs page_path and a 64-hex page_sha256"
    if v["class"] != "STATED":
        return "" if not (v["quote"] or v["offset"]) else "only a STATED verdict carries a quote and offset"
    if not re.fullmatch(r"[0-9]{1,8}", v["offset"]) or not QUOTE_MIN <= len(v["quote"]) <= QUOTE_MAX:
        return f"a STATED verdict needs an integer offset and a quote of {QUOTE_MIN}-{QUOTE_MAX} characters"
    return ""


def load_proofs(tasks, evidence, problems):
    """evidence_id -> (date, reader_family) for every proof line that passes the gate's offline checks."""
    out = {}
    for path in sorted(tasks.glob("*/BINDING_PROOF.csv")):
        folder = path.parent.name
        proofs, shape = gate.load_proof_file(str(path.relative_to(tasks.parent)), path.read_bytes())
        if shape:
            problems.extend(shape)
            continue
        readme = path.parent / "README.md"
        builder = gate.builder_family(readme.read_bytes() if readme.exists() else None)
        for eid, (at, p) in proofs.items():
            ev = evidence.get(eid)
            if ev is None or gate.label_folder(ev["created_by"]) != folder or ev["source_class"] != "own_site":
                continue  # not a row this route can admit; it still counts as a naming row (not_yet_checked)
            _, quote = head_and_quote(ev["claim_detail"])
            rf = gate.family_of_text(p["reader_family"])
            if (p["record_id"] == ev["record_id"] and p["claim_sha256"] == gate.claim_sha256(ev)
                    and p["verdict"] == "VERIFIED" and rf and builder and rf != builder
                    and SHA.fullmatch(p["capture_sha256"]) and re.fullmatch(r"[0-9]{1,8}", p["quote_offset"])
                    and len(quote) >= QUOTE_MIN and ISO.fullmatch(p["reader_date"])):
                out[eid] = p["reader_date"]
    return out


def evidence_pick(e):
    """The bound row that stands for a value: one that cites a page, then the lowest evidence id."""
    return (not e["source_ref"].startswith("http"), e["evidence_id"])


def generate(data=ROOT / "data", tasks=ROOT / "tasks", pages=None):
    """-> (rows, problems, info). rows are dicts keyed by COLS, sorted by key; info carries the counts."""
    data, tasks = Path(data), Path(tasks)
    problems = []
    orgs, sites = table_rows(data, "organizations"), table_rows(data, "sites")
    evidence = {r["evidence_id"]: r for r in table_rows(data, "evidence")}
    proofs = load_proofs(tasks, evidence, problems)
    verdicts_by_key, unreplayed = defaultdict(list), 0
    by_record = defaultdict(list)
    for e in evidence.values():
        by_record[(e["record_table"], e["record_id"])].append(e)
    for rows in by_record.values():
        rows.sort(key=lambda e: e["evidence_id"])

    def naming(table, rid, token):
        """Eligible rows naming the token: (own rows, organization-level rows for a site)."""
        ok = lambda e: (e["claim_type"] in CITING_CLAIMS and e["source_class"] in CITING_CLASSES
                        and e["tier_effect"] != "contradicts" and names(e["claim_detail"], token))
        own = [e for e in by_record[(table, rid)] if ok(e)]
        up = []
        if table == "sites":
            oid = site_org[rid]
            up = [e for t in ("organizations", "ecosystem") for e in by_record[(t, oid)] if ok(e)]
        return own, up

    site_org = {s["site_id"]: s["org_id"] for s in sites}
    record_tokens = {(t, r[idc], f): set(toks(r.get(f))) for t, idc, recs in
                     (("organizations", "org_id", orgs), ("sites", "site_id", sites)) for r in recs for f in FIELDS}
    held = {(t, r[idc], f, tok) for t, idc, recs in (("organizations", "org_id", orgs), ("sites", "site_id", sites))
            for r in recs for f in FIELDS for tok in toks(r.get(f))}
    for v, read_date in load_verdicts(tasks, problems, held):
        key = (v["record_table"], v["record_id"], v["field"], v["value"])
        owner, grain = (site_org[key[1]], "plant") if key[0] == "sites" else (key[1], "company")
        page_owner = re.search(r"(ORG-[^/]+)/", v["page_path"])
        if (v["owner"], v["grain"]) != (owner, grain) or (page_owner and page_owner[1] != owner):
            problems.append(f"{v['_at']}: the line's owner, grain or page folder does not match {key[0]} {key[1]} "
                            f"(owner {owner}, grain {grain}); a verdict labels only its own record")
            continue
        if v["class"] == "STATED" and pages and (why := replay(v, pages)):
            problems.append(f"{v['_at']}: STATED quote does not replay: {why}")
            continue
        unreplayed += v["class"] == "STATED" and not pages
        verdicts_by_key[key].append((read_date, v))
    rows, unnamed, unbound = [], Counter(), []
    for key in sorted(held):
        table, rid, field, tok = key
        own, up = naming(table, rid, tok)
        cands = []  # (rank, evidence_id, basis, date)
        for e in own:
            head, quote = head_and_quote(e["claim_detail"])
            # the row asserts exactly this value: it is the one held token its head names
            single = names(head, tok) and sum(names(head, t) for t in record_tokens[(table, rid, field)]) == 1
            excerpt = e["claim_detail"].partition("process excerpt:")[2].partition("quote:")[0].strip(' ";')
            if single and e["evidence_id"] in proofs:
                cands.append((5, e["evidence_id"], "stated", proofs[e["evidence_id"]]))
            elif single and e["source_class"] == "government_filing" and max(len(quote), len(excerpt)) >= QUOTE_MIN:
                cands.append((4, e["evidence_id"], "filing", e["observed_date"]))
        vs = sorted(verdicts_by_key.get(key, []), key=lambda x: x[0])
        pool = own or up  # a row on the value's own record stands for it before any organization row
        if vs:
            last = [v for d, v in vs if d == vs[-1][0]]
            if len({v["class"] for v in last}) > 1:
                problems.append(f"{key}: verdicts of different classes share the latest read date {vs[-1][0]}")
            elif not pool or (last[0]["class"] == "STATED" and not own):
                problems.append(f"{key}: a {last[0]['class']} verdict has no bound row on its own record to rest on"
                                if not pool else
                                f"{key}: a STATED verdict for a site value needs a bound row on the site itself, not only its organization")
            else:
                v = last[0]
                rest = own if v["class"] == "STATED" else pool
                page_sites = {site_of(u) for u in (v["_url"], v["_requested"]) if u} - {""}
                bound = [e for e in rest if page_key(e["source_ref"]) in {page_key(v["_url"]), page_key(v["_requested"])} - {("", "")}]
                if not any(site_of(e["source_ref"]) in page_sites for e in rest):
                    problems.append(f"{key}: the {v['class']} line's page ({v['_url'] or 'no VALUE_PAGES.csv entry'}) is not on a site any bound "
                                    f"row on this record cites")
                elif bound:  # the page is the one the row cites, or a recorded redirect to it
                    cands.append((5 if v["class"] == "STATED" else 3, min(bound, key=evidence_pick)["evidence_id"],
                                  VERDICT_CLASS[v["class"]], vs[-1][0]))
                else:  # same site, another page: no label, as NO_PAGE; the key stays on the cited page's evidence
                    unbound.append(key)
        if pool:
            cands.append((2, min(pool, key=evidence_pick)["evidence_id"], "not_yet_checked", ""))
        if not cands:
            unnamed[(table, field)] += 1
            rows.append(dict(zip(COLS, (table, rid, field, tok, "not_yet_checked", "", ""))))
            continue
        _, eid, basis, date = min(cands, key=lambda c: (-c[0], c[1]))  # highest rank; lowest evidence_id on a tie
        rows.append(dict(zip(COLS, (table, rid, field, tok, basis, eid, date))))
    info = {"unnamed": unnamed, "stated_not_replayed": unreplayed, "held": len(held), "verdict_unbound": unbound}
    return rows, problems, info


def render(rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


KEY = lambda r: (r["record_table"], r["record_id"], r["field"], r["value"])


def check(data=ROOT / "data", tasks=ROOT / "tasks", pages=None):
    """Problems with data/value_basis.csv against a fresh generation (validator V-69), one specific line each."""
    fresh, problems, info = generate(data, tasks, pages)
    path = Path(data) / "value_basis.csv"
    if not path.exists():
        return problems + ["data/value_basis.csv is missing; the table is generated, run scripts/value_basis.py"], info
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != COLS:
            return problems + [f"data/value_basis.csv: header must be {','.join(COLS)}"], info
        have = list(reader)
    seen, dup = {}, []
    for r in have:
        (dup.append(KEY(r)) if KEY(r) in seen else seen.__setitem__(KEY(r), r))
    problems += [f"data/value_basis.csv: duplicate key {k}" for k in dup]
    want = {KEY(r): r for r in fresh}
    problems += [f"data/value_basis.csv: a value a bound row names has no basis row: {k}" for k in sorted(want.keys() - seen.keys())]
    for k in sorted(seen.keys() - want.keys()):
        problems.append(f"data/value_basis.csv: row names a value the record does not hold, or no bound row names it: {k}")
    for k in sorted(seen.keys() & want.keys()):
        if seen[k] != want[k]:
            problems.append(f"data/value_basis.csv: {k} is {seen[k]['basis']}/{seen[k]['evidence_id']}/{seen[k]['basis_date']} "
                            f"but generation gives {want[k]['basis']}/{want[k]['evidence_id']}/{want[k]['basis_date']}; the table is never hand-edited")
    if not problems and render(fresh) != path.read_bytes().decode("utf-8"):
        problems.append("data/value_basis.csv differs from a fresh generation in row order or formatting")
    return problems, info


RANK = {"stated": 4, "filing": 3, "implied": 2, "not_yet_checked": 1}  # which label shows when one value has several origins


def withheld_keys(rows):
    """Keys of the values withheld from display: a read found the page neither states nor supports them (§4.24)."""
    return {(r["record_table"], r["record_id"], r["field"], r["value"]) for r in rows if r["basis"] == WITHHELD}


def strip_withheld(rows, table, id_col, withheld):
    """Display copy: remove withheld tokens from processes / markets_served cells, in place. A cell with none withheld
    keeps its exact text; the record CSVs are never rewritten."""
    for r in rows:
        for f in FIELDS:
            parts = [t.strip() for t in (r.get(f) or "").split(";")]
            kept = [t for t in parts if (table, r[id_col], f, t) not in withheld]
            if len(kept) != len(parts):
                r[f] = ";".join(t for t in kept if t)


def pic18_summary(data=ROOT / "data"):
    """Counts by basis for the owners of active tier A-C PIC-18 sites: the values their display rows supply."""
    from regions import PIC18
    data = Path(data)
    orgs = {r["org_id"]: r for r in table_rows(data, "organizations")}
    owners = defaultdict(list)
    for s in table_rows(data, "sites"):
        if (s["state"] == "OH" and s["county"] in PIC18 and s["operating_status"] == "active"
                and s["verification_tier"] in ("A", "B", "C")):
            owners[s["org_id"]].append(s)
    basis = {(r["record_table"], r["record_id"], r["field"], r["value"]):
             r["basis"] + (" (no bound row names it)" if not r["evidence_id"] else "") for r in read_csv(data / "value_basis.csv")}
    out = defaultdict(Counter)
    for oid, ss in owners.items():
        for field in FIELDS:  # site rows first, else the owner's own row: the directory's rule
            recs = [("sites", s["site_id"], toks(s[field])) for s in ss if toks(s[field])]
            if not recs and oid in orgs and toks(orgs[oid][field]):
                recs = [("organizations", oid, toks(orgs[oid][field]))]
            if not recs:
                continue
            out[field]["owners with values"] += 1
            for t, rid, tk in recs:
                for tok in tk:
                    out[field][basis[(t, rid, field, tok)]] += 1
    return len(owners), out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--tree", default=str(ROOT), help="repository root holding data/ and tasks/ (tests use a fixture)")
    ap.add_argument("--pages", help="store root that a verdict line's page_path is relative to: replay every STATED quote")
    ap.add_argument("--check", action="store_true", help="compare data/value_basis.csv with a fresh generation")
    ap.add_argument("--summary", action="store_true", help="print PIC-18 owner counts by basis")
    a = ap.parse_args(argv)
    if a.summary:
        n, out = pic18_summary(Path(a.tree) / "data")
        print(f"PIC-18 owners of active tier A-C sites: {n}")
        for field in FIELDS:
            print(f"{field}: {dict(out[field])}")
        return 0
    if a.check:
        problems, info = check(Path(a.tree) / "data", Path(a.tree) / "tasks", a.pages)
        for p in problems:
            print(p)
        print(f"value basis: {'differs from' if problems else 'matches'} a fresh generation; {info['held']} held values, "
              f"{sum(info['unnamed'].values())} named by no bound row (not_yet_checked, empty evidence_id), "
              f"NOT_INSPECTED: {info['stated_not_replayed']} STATED verdict quotes not replayed (no --pages), "
              f"{len(info['verdict_unbound'])} verdict lines on another page of the cited site give no label")
        return 1 if problems else 0
    rows, problems, info = generate(Path(a.tree) / "data", Path(a.tree) / "tasks", a.pages)
    if problems:
        print("\n".join(problems))
        return 1
    (Path(a.tree) / "data" / "value_basis.csv").write_text(render(rows), encoding="utf-8", newline="")
    print(f"wrote {len(rows)} rows: {dict(Counter(r['basis'] for r in rows))}; unnamed {dict(info['unnamed'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
