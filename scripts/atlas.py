#!/usr/bin/env python3
"""atlas.py - read-only command-line helper that EXECUTES the repo's mechanical
rules (AGENTS.md §3, docs/SCHEMA.md §5.6, Appendix C §2/§6.1/§6.4) so agents do
not have to interpret the prose.  Stdlib only.  It never writes under data/.

Usage (run from the repo root; add --data-dir PATH to point at another tree):

  python3 scripts/atlas.py next-id ORG            # tree-wide max + next free id
  python3 scripts/atlas.py next-id --all          # table for every XXX-###### prefix
  python3 scripts/atlas.py next-id --all --audit  # ...plus dangling-reference audit
  python3 scripts/atlas.py dedupe-check --domain avient.com --name "Avient Corp"
  python3 scripts/atlas.py dedupe-check --street "554 Moore Road" --city "Avon Lake" --state OH --zip 44012
  python3 scripts/atlas.py dedupe-check --name "PolyOne" --json
  python3 scripts/atlas.py show ORG-000010        # record + evidence + relationships + sites
  python3 scripts/atlas.py show SITE-000001 --json
  python3 scripts/atlas.py shard-of --hq-state TX             # organizations_TX.csv
  python3 scripts/atlas.py shard-of --site-state OH           # sites_OH.csv
  python3 scripts/atlas.py shard-of --hq-state QC --hq-country CA   # organizations_INTL.csv

Exit codes: next-id 0 ok / 2 unknown prefix; dedupe-check 0 no hits / 1 hits;
show 0 found / 1 not found; shard-of 0 resolved / 3 needs more facts /
4 unplaceable site.  Every command accepts --json (shard-of and next-id too).

ID rule (SCHEMA Appendix C §6.1): scan EVERY shard of the table, take the
max numeric suffix + 1; gaps are permanent and are never filled.  Only a
table's own primary-key column counts toward the max (the first column of each
table file; registry_links has none; sites.site_group_id defines GRP-).  IDs that
appear only in foreign-key columns are tracked separately and reported when they
exceed the primary-key max.
"""
import argparse
import csv
import glob
import json
import os
import re
import sys
from collections import defaultdict

csv.field_size_limit(10 ** 8)
DEFAULT_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data")
ID_RE = re.compile(r"^([A-Z][A-Z0-9]*)-(\d+)$")
SHARD_RE = re.compile(r"^(.+)_([A-Z]{2,4})$")  # organizations_OH, sites_INTL
NO_PK_TABLES = {"registry_links"}              # first column is a foreign key
EXTRA_PK = {("sites", "site_group_id")}        # GRP- ids are defined here ...
NONUNIQUE_PK = {"sites.site_group_id"}         # ... and are shared by design (a group = several sites)
# SCHEMA Appendix C §2: USPS codes incl. DC + territories (same set as validate.py USPS_ALL)
USPS = set("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ "
           "NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC AS GU MP PR VI".split())
US_COUNTRIES = {"", "US", "USA", "UNITED STATES"}

# ---------------------------------------------------------------- loading

class Table:
    def __init__(self, name):
        self.name, self.columns, self.rows = name, [], []   # rows: dicts with '__file__', '__line__'


def load_tables(data_dir):
    """Return {table_name: Table}; shards (organizations_OH...) merge into one table."""
    tables = {}
    for path in sorted(glob.glob(os.path.join(data_dir, "*.csv"))):
        stem = os.path.basename(path)[:-4]
        m = SHARD_RE.match(stem)
        name = m.group(1) if m else stem
        if stem == "evidence" or stem.startswith("evidence_"):
            name = "evidence"  # [v1.8] evidence shards union into one table
        t = tables.setdefault(name, Table(name))
        with open(path, newline="", encoding="utf-8-sig") as fh:
            rd = csv.DictReader(fh)
            if not t.columns:
                t.columns = list(rd.fieldnames or [])
            for r in rd:
                r["__file__"], r["__line__"] = os.path.basename(path), rd.line_num
                t.rows.append(r)
    return tables


def pk_columns(t):
    cols = [] if t.name in NO_PK_TABLES or not t.columns or not t.columns[0].endswith("_id") else [t.columns[0]]
    return cols + [c for (tn, c) in EXTRA_PK if tn == t.name and c in t.columns]


def ref_columns(t):
    pks = set(pk_columns(t))
    return [c for c in t.columns if c not in pks and (c.endswith("_id") or c.endswith("_ids"))]


def tokens(cell):
    return [x.strip() for x in re.split(r"[;,]", cell or "") if x.strip()]

# ---------------------------------------------------------------- next-id

def scan_ids(tables):
    """prefix -> {ids:{id:[files]}, pk_cols:set, refs:{id:[(table,col,file)]}, width}"""
    info = defaultdict(lambda: {"ids": defaultdict(list), "pk_cols": set(), "refs": defaultdict(list), "unique": False})
    for t in tables.values():
        for col in pk_columns(t):
            for r in t.rows:
                v = (r[col] or "").strip()
                if not v:
                    continue
                m = ID_RE.match(v)
                if not m:
                    continue  # not an XXX-###### id (cannot be attributed to a prefix)
                d = info[m.group(1)]
                d["ids"][v].append(r["__file__"])
                d["pk_cols"].add(f"{t.name}.{col}")
                d["unique"] |= f"{t.name}.{col}" not in NONUNIQUE_PK
        for col in ref_columns(t):
            for r in t.rows:
                for tok in tokens(r[col]):
                    m = ID_RE.match(tok)
                    if m:
                        info[m.group(1)]["refs"][tok].append((t.name, col, r["__file__"]))
    return info


def num(i):
    return int(ID_RE.match(i).group(2))


def next_id_report(prefix, d):
    ids = d["ids"]
    rep = {"prefix": prefix, "pk_columns": sorted(d["pk_cols"]), "count": len(ids),
           "files": sorted({f for fl in ids.values() for f in fl}), "warnings": []}
    top_ref = max(d["refs"], key=num, default=None)
    if ids:
        mx = max(ids, key=num)
        width = len(ID_RE.match(mx).group(2))
    else:
        mx, width = None, len(ID_RE.match(top_ref).group(2)) if top_ref else 6
    rep["max_id"] = mx
    rep["next_id"] = f"{prefix}-{(num(mx) if mx else 0) + 1:0{width}d}" if mx else None
    rep["duplicates"] = {i: fl for i, fl in ids.items() if len(fl) > 1 and d["unique"]}
    if rep["duplicates"]:
        rep["warnings"].append(f"{len(rep['duplicates'])} duplicate primary key(s): " +
                               ", ".join(f"{i} in {'+'.join(fl)}" for i, fl in list(rep["duplicates"].items())[:5]))
    base = num(mx) if mx else 0
    above = sorted((i for i in d["refs"] if num(i) > base), key=num)
    rep["referenced_above_max"] = above
    rep["max_referenced"] = top_ref
    if above:
        safe = f"{prefix}-{num(above[-1]) + 1:0{width}d}"
        rep["next_id_avoiding_refs"] = safe
        rep["warnings"].append(
            f"{len(above)} referenced id(s) exceed the primary-key max (first: {above[0]}, last: {above[-1]}); "
            f"{'no primary table holds this prefix' if not ids else 'dangling or reserved'}. "
            f"Strict rule next = {rep['next_id']}; next avoiding those references = {safe}. Flag this to the integrator.")
    return rep


def dangling_refs(info):
    """Every FK-column token whose id is not a primary key anywhere (any prefix)."""
    out = defaultdict(list)
    for prefix, d in info.items():
        for tok, places in d["refs"].items():
            if tok not in d["ids"]:
                for (t, c, f) in places:
                    out[f"{t}.{c}"].append(tok)
    return out


def cmd_next_id(a, tables):
    info = scan_ids(tables)
    if a.all:
        prefixes = sorted(info)
    else:
        if not a.prefix:
            print("next-id: give a PREFIX or --all", file=sys.stderr); return 2
        p = a.prefix.upper().rstrip("-")
        if p not in info:
            print(f"unknown prefix {p!r}; known: {', '.join(sorted(info))}", file=sys.stderr); return 2
        prefixes = [p]
    reps = [next_id_report(p, info[p]) for p in prefixes]
    audit = None
    if a.audit:
        audit = {k: sorted(set(v), key=lambda s: (s.split('-')[0], num(s))) for k, v in sorted(dangling_refs(info).items())}
    if a.json:
        print(json.dumps({"prefixes": reps, "dangling_references": audit}, indent=2)); return 0
    print(f"{'PREFIX':<8}{'MAX':<15}{'NEXT FREE':<15}{'IDS':>6}  PRIMARY KEY COLUMN(S)")
    for r in reps:
        print(f"{r['prefix']:<8}{r['max_id'] or '-':<15}{r['next_id'] or '-':<15}{r['count']:>6}  {', '.join(r['pk_columns']) or '(references only)'}")
    for r in reps:
        for w in r["warnings"]:
            print(f"WARNING {r['prefix']}: {w}")
    if not a.all and reps:
        print(f"scanned {len(reps[0]['files'])} file(s); gaps are permanent, never fill them (SCHEMA App. C §6.1)")
    if audit is not None:
        print(f"\nDangling references (id in an *_id column that is no table's primary key): {sum(len(v) for v in audit.values())} distinct")
        for k, v in audit.items():
            print(f"  {k}: {len(v)}  e.g. {', '.join(v[:6])}")
    return 0

# ---------------------------------------------------------------- normalizers

NAME_STOP = {"inc", "llc", "corp", "co", "the", "ltd", "company", "corporation", "incorporated"}


def squash(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", (s or "").lower().replace("&", " and "))).strip()


def name_key(s):
    toks = squash(s).split()
    kept = [t for t in toks if t not in NAME_STOP]
    return " ".join(kept or toks)


PLATFORM_HOSTS = {"linkedin.com", "facebook.com", "instagram.com", "twitter.com", "x.com", "youtube.com", "google.com",
                  "sites.google.com", "business.site", "wixsite.com", "wordpress.com", "squarespace.com",
                  "godaddysites.com", "weebly.com", "github.io", "bloomberg.com", "crunchbase.com", "zoominfo.com"}


def domain_key(s):
    s = (s or "").strip().lower()
    if not s:
        return ""
    s = re.sub(r"^[a-z][a-z0-9+.-]*://", "", s)
    s = s.split("@")[-1] if "@" in s.split("/")[0] else s
    host, _, path = s.partition("/")
    host = re.sub(r":\d+$", "", host)
    host = host[4:] if host.startswith("www.") else host
    if host in PLATFORM_HOSTS or any(host.endswith("." + h) for h in PLATFORM_HOSTS):
        return host + "/" + path.split("?")[0].split("#")[0].rstrip("/")
    return host


def domain_match(q, c):
    if not q or not c:
        return None
    if q == c:
        return "exact"
    if "/" not in q and "/" not in c and (q.endswith("." + c) or c.endswith("." + q)):
        return "subdomain"
    return None


SUFFIX = {"street": "st", "avenue": "ave", "av": "ave", "road": "rd", "drive": "dr", "boulevard": "blvd", "highway": "hwy",
          "parkway": "pkwy", "lane": "ln", "court": "ct", "circle": "cir", "place": "pl", "terrace": "ter", "route": "rte",
          "square": "sq", "trail": "trl", "center": "ctr", "centre": "ctr", "expressway": "expy", "turnpike": "tpke",
          "north": "n", "south": "s", "east": "e", "west": "w", "northeast": "ne", "northwest": "nw", "southeast": "se",
          "southwest": "sw"}
UNIT_RE = re.compile(r"\b(suite|ste|unit|apt|apartment|bldg|building|floor|fl|room|rm|dept|department)\b.*$|(?<=\S)\s*#.*$")
UNIT_ONLY_RE = re.compile(r"^\s*(?:(?:suite|ste|unit|apt|apartment|bldg|building|floor|fl|room|rm|dept|department)\b|#)\s*[\w-]*\s*$")


def street_key(s):
    """Normalized street line for address-first dedupe (AGENTS §3 step 3); empty only when no street is present."""
    parts = [p for p in (s or "").lower().split(",")]
    # the street is the first comma part with a digit that is not just a unit ("Suite 100, 200 Main St")
    # no comma part with a street number: keep the whole string, as before ("Ironstone House, Ironstone Way")
    street = next((p for p in parts if re.search(r"\d", p) and not UNIT_ONLY_RE.match(p)), (s or "").lower())
    street = re.sub(r"^\s*#\s*(?=\d)", "", street)  # a leading "#6" is a building number, not a unit
    s = UNIT_RE.sub("", street)
    s = re.sub(r"\b(\d+)(st|nd|rd|th)\b", r"\1", s)
    return " ".join(SUFFIX.get(t, t) for t in squash(s).split())

# ---------------------------------------------------------------- dedupe-check

def org_rows(tables):
    for tn in ("organizations", "ecosystem"):
        for r in tables.get(tn, Table(tn)).rows:
            yield tn, r


def brief(table, r):
    if table == "sites":
        return {"id": r["site_id"], "name": r["site_name"], "org_id": r["org_id"], "city": r["city"], "state": r["state"],
                "status": r["operating_status"], "tier": r["verification_tier"], "file": r["__file__"],
                "street": r.get("street_address", "")}
    c, s = ("hq_city", "hq_state") if table == "organizations" else ("city", "state")
    return {"id": r["org_id"], "name": r["legal_name"], "city": r[c], "state": r[s], "status": r["status"],
            "tier": r["verification_tier"], "file": r["__file__"]}


def successor_chain(oid, orgs_by_id):
    chain, seen = [], {oid}
    cur = oid
    while True:
        recs = orgs_by_id.get(cur)
        nxt = (recs[0].get("successor_org_id") or "").strip() if recs else ""
        if not nxt:
            return chain, "terminal"
        chain.append(nxt)
        if nxt in seen:
            return chain, "cycle"
        if nxt not in orgs_by_id:
            return chain, "dangling"
        seen.add(nxt)
        cur = nxt


def dedupe(tables, domain=None, name=None, street=None, city=None, state=None, zip_=None):
    orgs = [(tn, r) for tn, r in org_rows(tables)]
    by_id = defaultdict(list)
    for tn, r in orgs:
        by_id[r["org_id"]].append(r)
    steps = []

    # 1. domain
    s1 = {"step": 1, "name": "website domain (organizations_*.csv + ecosystem.csv)", "skipped": None if domain else "no --domain", "hits": []}
    if domain:
        q = domain_key(domain)
        for tn, r in orgs:
            kind = domain_match(q, domain_key(r.get("website", "")))
            if kind:
                s1["hits"].append({**brief(tn, r), "match": f"domain {kind}: {domain_key(r['website'])}"})
    steps.append(s1)

    # 2. normalized name vs legal_name + trade_names
    s2 = {"step": 2, "name": "normalized name vs legal_name/trade_names", "skipped": None if name else "no --name", "hits": []}
    hit2 = set()
    if name:
        q = name_key(name)
        for tn, r in orgs:
            fields = [("legal_name", r["legal_name"])] + [("trade_names", t) for t in tokens_semicolon(r.get("trade_names"))]
            for fld, val in fields:
                if q and name_key(val) == q:
                    s2["hits"].append({**brief(tn, r), "match": f"name key {q!r} = {fld} {val!r}"})
                    hit2.add(r["org_id"]); break
    steps.append(s2)

    # 3. street address in sites
    s3 = {"step": 3, "name": "street address (sites_*.csv; one address = one site, owned by the operator)",
          "skipped": None if street else "no --street", "hits": [], "other_localities": []}
    if street:
        q = street_key(street)
        sites = tables.get("sites", Table("sites")).rows
        for r in sites:
            if not q or street_key(r.get("street_address", "")) != q:
                continue
            mism = []
            if city and r["city"] and squash(city) != squash(r["city"]): mism.append("city")
            if state and r["state"] and state.upper() != r["state"].upper(): mism.append("state")
            if zip_ and r["zip"] and zip_[:5] != r["zip"][:5]: mism.append("zip")
            op = by_id.get(r["org_id"], [{}])[0].get("legal_name", "(org not found)")
            h = {**brief("sites", r), "operator": op, "match": f"street key {q!r}" + (f"; locality differs: {','.join(mism)}" if mism else "")}
            (s3["other_localities"] if mism else s3["hits"]).append(h)
    steps.append(s3)

    # 4. trade names / notes substring + successor chains
    s4 = {"step": 4, "name": "trade_names/notes/legal_name substring + successor_org_id chain", "skipped": None if name else "no --name", "hits": []}
    if name:
        needles = {n for n in (squash(name), name_key(name)) if len(n) >= 3}
        for tn, r in orgs:
            if r["org_id"] in hit2:
                continue
            for fld in ("trade_names", "notes", "legal_name"):
                hay = " " + squash(r.get(fld, "")) + " "
                if any(f" {n} " in hay for n in needles):
                    s4["hits"].append({**brief(tn, r), "match": f"{fld} contains {name!r}"}); break
    steps.append(s4)

    for s in steps[:2] + steps[3:]:
        for h in s["hits"]:
            ch, end = successor_chain(h["id"], by_id)
            if ch:
                last = by_id.get(ch[-1], [None])[0]
                h["successor_chain"] = ch
                h["successor_end"] = end
                h["successor_terminal"] = (f"{ch[-1]} {last['legal_name']} [{last['status']}]" if last else f"{ch[-1]} (not in tree)")
    stop = next((s["step"] for s in steps if s["hits"]), None)
    return {"query": {"domain": domain, "name": name, "street": street, "city": city, "state": state, "zip": zip_},
            "stop_at_step": stop, "steps": steps}


def tokens_semicolon(cell):
    return [x.strip() for x in (cell or "").split(";") if x.strip()]


def fmt_hit(h, indent="  "):
    loc = ", ".join(x for x in (h["city"], h["state"]) if x)
    s = f"{indent}{h['id']}  {h['name']}  [{loc}]  status={h['status'] or '-'} tier={h['tier'] or '-'}  ({h['file']})"
    if "operator" in h:
        s += f"\n{indent}    operator: {h['org_id']} {h['operator']}; street: {h['street']}"
    s += f"\n{indent}    match: {h['match']}"
    if "successor_chain" in h:
        s += f"\n{indent}    successor chain ({h['successor_end']}): {' -> '.join(h['successor_chain'])}  => {h['successor_terminal']}"
    return s


def cmd_dedupe(a, tables):
    if not (a.domain or a.name or a.street):
        print("dedupe-check: need at least one of --domain, --name, --street", file=sys.stderr); return 2
    res = dedupe(tables, a.domain, a.name, a.street, a.city, a.state, a.zip)
    anyhit = res["stop_at_step"] is not None
    if a.json:
        print(json.dumps(res, indent=2)); return 1 if anyhit else 0
    q = {k: v for k, v in res["query"].items() if v}
    print(f"dedupe-check {q}  (AGENTS.md §3; searches the union of ALL shards)")
    stop = res["stop_at_step"]
    for s in res["steps"]:
        if stop and s["step"] == stop + 1:
            print("\n--- for information (steps after the stop) ---")
        if stop is None and s["step"] == 1:
            print()
        tag = f"skipped ({s['skipped']})" if s["skipped"] else f"{len(s['hits'])} hit(s)"
        print(f"STEP {s['step']} {s['name']}: {tag}")
        for h in s["hits"][:15]:
            print(fmt_hit(h))
        if len(s["hits"]) > 15:
            print(f"  ... {len(s['hits']) - 15} more (use --json)")
        for h in s.get("other_localities", [])[:10]:
            print("  [not counted - same street text, other locality]\n" + fmt_hit(h, "  "))
    if anyhit:
        print(f"\n=> STOP at step {stop}: a hit exists. Use/link the existing record; do not create a duplicate. "
              "When in doubt do NOT merge - create/link and flag (AGENTS.md §3).")
    else:
        print("\n=> No hits at any step run. Create at tier U or C and record which searches you ran (AGENTS.md §3 step 5).")
    return 1 if anyhit else 0

# ---------------------------------------------------------------- show

def find_records(tables, rid):
    out = []
    for t in tables.values():
        for col in pk_columns(t):
            out += [(t.name, col, r) for r in t.rows if (r[col] or "").strip() == rid]
    return out


def clean(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def show(tables, rid):
    recs = find_records(tables, rid)
    res = {"id": rid, "records": [{"table": t, "file": r["__file__"], "line": r["__line__"], "fields": clean(r)} for t, c, r in recs]}
    T = lambda n: tables.get(n, Table(n)).rows
    res["evidence"] = [clean(r) for r in T("evidence") if r["record_id"] == rid]
    res["relationships"] = [clean(r) for r in T("relationships") if rid in (r["from_org_id"], r["to_org_id"])]
    res["registry_links"] = [clean(r) for r in T("registry_links") if r["org_id"] == rid]
    if rid.startswith("ORG-"):
        res["sites"] = [{k: r[k] for k in ("site_id", "site_name", "street_address", "city", "state", "operating_status", "verification_tier", "__file__")} for r in T("sites") if r["org_id"] == rid]
        by_id = defaultdict(list)
        for tn, r in org_rows(tables): by_id[r["org_id"]].append(r)
        ch, end = successor_chain(rid, by_id)
        res["successor_chain"] = {"chain": ch, "end": end} if ch else None
    if rid.startswith("SITE-"):
        res["parent_org"] = [{"id": r["org_id"], "legal_name": r["legal_name"], "status": r["status"], "file": r["__file__"]}
                             for tn, r in org_rows(tables) if r["org_id"] in {x[2]["org_id"] for x in recs}]
        res["capabilities"] = [clean(r) for r in T("site_capabilities") if r["site_id"] == rid]
    refs = defaultdict(list)  # reverse references from other tables
    for t in tables.values():
        for col in ref_columns(t):
            n = [r for r in t.rows if rid in tokens(r[col])]
            if n:
                pk = (pk_columns(t) or [None])[0]
                refs[f"{t.name}.{col}"] = [(r[pk] if pk else "") for r in n]
    res["referenced_by"] = {k: {"rows": len(v), "ids": v[:8]} for k, v in refs.items()}
    return res


def cmd_show(a, tables):
    res = show(tables, a.id.upper())
    if a.json:
        print(json.dumps(res, indent=2)); return 0 if res["records"] else 1
    if not res["records"]:
        print(f"{a.id}: no primary-key match in any table (referenced_by below may still show dangling uses)")
    for rec in res["records"]:
        print(f"== {res['id']}  table={rec['table']}  {rec['file']}:{rec['line']}")
        for k, v in rec["fields"].items():
            if v:
                print(f"  {k}: {v if len(v) <= 400 else v[:400] + ' ...[+%d chars]' % (len(v) - 400)}")
    if res.get("parent_org"):
        for p in res["parent_org"]: print(f"-- parent org: {p['id']} {p['legal_name']} status={p['status']} ({p['file']})")
    if res.get("successor_chain"):
        print(f"-- successor chain ({res['successor_chain']['end']}): {' -> '.join(res['successor_chain']['chain'])}")
    if "sites" in res:
        print(f"-- sites ({len(res['sites'])})")
        for s in res["sites"]:
            print(f"  {s['site_id']}  {s['site_name']}  {s['street_address'] or '-'}, {s['city']}, {s['state']}  {s['operating_status']}/{s['verification_tier']}  ({s['__file__']})")
    if res.get("capabilities"):
        print(f"-- site_capabilities ({len(res['capabilities'])}): " + "; ".join(c["term"] for c in res["capabilities"]))
    print(f"-- evidence rows ({len(res['evidence'])})")
    for e in res["evidence"]:
        print(f"  {e['evidence_id']} {e['claim_type']} {e['source_class']} {e['observed_date']} {e['tier_effect']}  {e['source_ref'][:90]}")
    print(f"-- relationships ({len(res['relationships'])})")
    for r in res["relationships"]:
        print(f"  {r['relationship_id']} {r['from_org_id']} --{r['relationship_type']}--> {r['to_org_id']}  ({r['basis']})")
    print(f"-- registry_links ({len(res['registry_links'])})")
    for r in res["registry_links"]:
        print(f"  {r['registry']}: {r['registry_id']} ({r['match_basis']}, as of {r['as_of']})")
    if res["referenced_by"]:
        print("-- referenced by (other tables)")
        for k, v in res["referenced_by"].items():
            eg = ", ".join(i for i in v["ids"][:5] if i)
            print(f"  {k}: {v['rows']} row(s)" + (f" e.g. {eg}" if eg else ""))
    return 0 if res["records"] else 1

# ---------------------------------------------------------------- shard-of

RULE_TEXT = {
    "org": ("org_shard(org): st=upper(trim(hq_state)); c=upper(trim(hq_country)); if st in USPS (incl. DC + territories): st; "
            "elif c not in {'', US, USA, UNITED STATES}: INTL; else US (residual placement-review queue, SCHEMA App. C §3)."),
    "site": ("site_shard(site): st=upper(trim(state)); c=upper(trim(country)); if st in USPS: st; "
             "elif c not in {'', US, USA, UNITED STATES}: INTL; else UNPLACEABLE (§2.1: hold, validator V-35, owner/schema ruling; "
             "never force into a US shard or the residual - sites have no residual)."),
}


def shard_of(kind, state, country):
    """Returns (tag|None, status, note). status: ok | needs_country | unplaceable."""
    st = (state or "").strip().upper()
    if st in USPS:
        c = (country or "").strip().upper()
        warn = f"; WARNING: country {country!r} is non-US but a USPS state wins by the rule - check for a state/country mix-up" if c not in US_COUNTRIES else ""
        return st, "ok", "USPS state code" + warn
    if country is None:
        return None, "needs_country", f"{state!r} is not a USPS code; the rule then depends on country. " + RULE_TEXT[kind]
    c = country.strip().upper()
    if c not in US_COUNTRIES:
        return "INTL", "ok", f"non-USPS state with stated non-US country {country!r}"
    if kind == "org":
        return "US", "ok", "HQ state unknown and country US/blank: residual shard (placement-review queue; never infer from sites)"
    return None, "unplaceable", RULE_TEXT["site"]


def cmd_shard_of(a, data_dir):
    if (a.hq_state is None) == (a.site_state is None):
        print("shard-of: give exactly one of --hq-state / --site-state", file=sys.stderr); return 2
    kind, state, country = ("org", a.hq_state, a.hq_country) if a.hq_state is not None else ("site", a.site_state, a.country)
    tag, status, note = shard_of(kind, state, country)
    table = "organizations" if kind == "org" else "sites"
    path = f"data/{table}_{tag}.csv" if tag else None
    exists = bool(path) and os.path.exists(os.path.join(data_dir, f"{table}_{tag}.csv"))
    res = {"kind": table, "state": state, "country": country, "shard": tag, "file": path, "status": status, "note": note,
           "file_exists": exists if tag else None}
    if a.json:
        print(json.dumps(res, indent=2))
    elif tag:
        print(f"{path}  ({note})")
        print("file exists" if exists else "file does not exist yet: shards are created lazily when the first row lands (App. C §1)")
        print("Reminder: rows stay ID-sorted within the shard; a placement correction is a MOVE by the integrator of record (§4).")
    else:
        print(("UNPLACEABLE: " if status == "unplaceable" else "UNDECIDED: ") + note)
    return {"ok": 0, "needs_country": 3, "unplaceable": 4}[status]

# ---------------------------------------------------------------- main

def build_parser():
    p = argparse.ArgumentParser(prog="atlas.py", description="Read-only helper for polymer-atlas mechanical rules.")
    p.add_argument("--data-dir", default=DEFAULT_DATA, help="data directory (default: ../data relative to this script)")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("next-id", help="tree-wide max and next free id for a prefix")
    s.add_argument("prefix", nargs="?"); s.add_argument("--all", action="store_true")
    s.add_argument("--audit", action="store_true", help="also list dangling FK references"); s.add_argument("--json", action="store_true")
    s = sub.add_parser("dedupe-check", help="AGENTS.md §3 dedupe searches, in order")
    for o in ("--domain", "--name", "--street", "--city", "--state", "--zip"): s.add_argument(o)
    s.add_argument("--json", action="store_true")
    s = sub.add_parser("show", help="show a record by id with evidence/relationships/sites")
    s.add_argument("id"); s.add_argument("--json", action="store_true")
    s = sub.add_parser("shard-of", help="which shard file a record belongs in (Appendix C §2)")
    s.add_argument("--hq-state"); s.add_argument("--hq-country"); s.add_argument("--site-state"); s.add_argument("--country")
    s.add_argument("--json", action="store_true")
    return p


def main(argv=None):
    a = build_parser().parse_args(argv)
    data_dir = os.path.normpath(a.data_dir)
    if a.cmd == "shard-of":
        return cmd_shard_of(a, data_dir)
    if not os.path.isdir(data_dir):
        print(f"data dir not found: {data_dir}", file=sys.stderr); return 2
    tables = load_tables(data_dir)
    return {"next-id": cmd_next_id, "dedupe-check": cmd_dedupe, "show": cmd_show}[a.cmd](a, tables)


if __name__ == "__main__":
    sys.exit(main())
