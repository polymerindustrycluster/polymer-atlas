#!/usr/bin/env python3
"""Evidence binding gate: is an evidence row's quote about the record it is filed on?

validate.py checks an evidence row's form, never whether its quote witnesses that record. On 2026-11-22 two join
batches (about 34,000 rows) passed every check while a first-cut test found 28% did not bind: the quote named another
operator, another street, or claimed a headquarters from a plant permit (tasks/evidence-binding-gate-2026-11-22/).

Every evidence row gets exactly one verdict:
  PASS            the quoted operator is a name the record holds (exact name_key, scripts/atlas.py); for a site row the
                  quoted street equals the site's street_address under street_key; for an organization `address` row
                  the source states the entity's own address and the quoted city and state are the record's HQ.
  FAIL            with reasons: name_not_held, street_differs, unit_differs (both state a suite or unit and they
                  differ; street_key drops units), record_no_street, quote_no_street, hq_city_state_differs,
                  hq_from_facility_or_permit, hq_from_s5_identity_source (FMCSA filed address or a state filing,
                  SCHEMA §4.8 S-5).
  UNINSPECTABLE   with a reason: no_quote, free_text_web_quote, other_table, record_not_found, unknown_source_family,
                  parse_failed, operator_not_a_name (shifted columns such as "permittee: 3"), no_civic_number (equal
                  street keys with no civic number, such as a bare road or park name). Never a pass.

Strict reading (owner questions, measured in the name_alt column, never passing): a parent's name, a name found only
in the record's notes, a permit's facility label, a quoted name that merely starts with a held name.

Usage:
  python3 scripts/check_evidence_binding.py --all [--head REF] [--out verdicts.csv]
  python3 scripts/check_evidence_binding.py --new-since origin/main      # PR gate: rows added or re-pointed since
  python3 scripts/check_evidence_binding.py --provenance-since origin/main  # tasks/<created_by>/check.py required
--new-since exits 1 on any FAIL or UNINSPECTABLE row without a waiver in a tasks/**/BINDING_WAIVERS.csv file
(columns: evidence_id,reason,reviewer; one line per row; both reason and reviewer required). Exit 2 = could not check.
"""
import argparse
import csv
import io
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from atlas import (LOCALITY_SEP_RE, UNIT_ONLY_RE, UNIT_RE, name_key, org_name_fields, site_name_key, squash,  # noqa: E402
                   street_key)
from build_echo_spine import STATE_NAMES  # noqa: E402

csv.field_size_limit(10**9)
BINDING_FIELDS = ("record_table", "record_id", "claim_type", "claim_detail", "source_ref")
WAIVER_COLS = ("evidence_id", "reason", "reviewer")

# Source families whose quote format is known. Deny by default: any other non-URL source is unknown_source_family.
# (source_ref prefix, quote format, operator fields, address field, HQ basis for an organization `address` row)
# HQ basis: "entity" = the source states the entity's own address; "s5" = an identity-only source under SCHEMA §4.8 S-5
# (FMCSA filed carrier address; a state filing's address may be an agent's); "facility" = a facility or permit record.
PERMIT = (("permittee",), "address", "facility")
FAMILIES = [
    ("EPA ECHO ", "echo", (), "", "facility"),
    ("OSHA ", "osha", (), "", "facility"),
    ("FMCSA Company Census", "labelled", ("legal_name", "dba_name"), "physical_address", "s5"),
    ("state-entity-files-bulk", "labelled", ("legal_name",), "principal_address", "s5"),
    ("USAspending bulk", "labelled", ("recipient_name",), "recipient_address", "entity"),
    ("SBIR/STTR bulk", "labelled", ("firm_name",), "address", "entity"),
] + [(p, "labelled") + PERMIT for p in (
    "TCEQ Central Registry", "PA DEP ", "NC DEQ ArcGIS", "Ohio EPA ", "CA DTSC ", "CA SWRCB ", "IN IGMAP ", "NJDEP ",
    "GA EPD ")]
LABEL_RE = re.compile(r"(?:^|;\s*)([A-Za-z][A-Za-z_ ()/]{0,30}?):\s")
PAREN_RE = re.compile(r"\([^()]*\)")
STATE_KEYS = {v.lower(): squash(k) for k, v in STATE_NAMES.items()}
NUMBER_WORDS = dict(zip("one two three four five six seven eight nine ten".split(), map(str, range(1, 11))))
NUMBER_WORDS.update(zip("first second third fourth fifth sixth seventh eighth ninth tenth".split(), map(str, range(1, 11))))
UNIT_ID_RE = re.compile(r"(?:suite|ste|unit|apt|apartment|bldg|building|floor|fl|room|rm|dept|department|#)\W*([a-z0-9-]+)")


# ---------------------------------------------------------------- loading

def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout


def data_files(ref, pattern):
    """[(path, text)] for data/<pattern> at a git ref, or the working tree when ref is None. Merged exports skipped."""
    if ref is None:
        paths = sorted((ROOT / "data").glob(pattern))
        return [(f"data/{p.name}", p.read_text(encoding="utf-8")) for p in paths if not p.name.endswith("_all.csv")]
    names = [n for n in git("ls-tree", "--name-only", f"{ref}:data/").split()
             if Path(n).match(pattern) and not n.endswith("_all.csv")]
    return [(f"data/{n}", git("show", f"{ref}:data/{n}")) for n in sorted(names)]


def rows(ref, pattern):
    out = []
    for path, text in data_files(ref, pattern):
        reader = csv.DictReader(io.StringIO(text))
        for r in reader:
            r["_at"] = f"{path}:{reader.line_num}"
            out.append(r)
    return out


class Index:
    """The records a quote can be about: sites, organizations (shards + ecosystem) by id."""

    def __init__(self, sites, orgs):
        self.sites = {s["site_id"]: s for s in sites}
        self.orgs = {o["org_id"]: o for o in orgs}
        self._notes = {}

    @classmethod
    def load(cls, ref=None):
        return cls(rows(ref, "sites_*.csv"), rows(ref, "organizations_*.csv") + rows(ref, "ecosystem.csv"))

    def record(self, table, rid):
        return self.sites.get(rid) if table == "sites" else self.orgs.get(rid)

    def org_keys(self, oid):
        o = self.orgs.get(oid)
        if not o:
            return set()
        names = [v for _, v in org_name_fields(o)] if "trade_names" in o else [o.get("legal_name", "")]
        return {k for v in names for k in (name_key(v), name_key(PAREN_RE.sub(" ", v))) if k}

    def held_keys(self, table, rid):
        """name_keys of every name the record itself holds (strict reading: no parent, no notes)."""
        if table != "sites":
            return self.org_keys(rid)
        s = self.sites[rid]
        name, city = s.get("site_name") or "", squash(s.get("city"))
        keys = {name_key(name), site_name_key(name, s.get("city") or "")}
        for part in LOCALITY_SEP_RE.split(PAREN_RE.sub(" ", name)):
            if squash(part) and not (city and squash(part).startswith(city)):
                keys.add(name_key(part))
        return {k for k in keys if k} | self.org_keys(s.get("org_id"))

    def parent_keys(self, table, rid):
        o = self.orgs.get(self.sites[rid].get("org_id")) if table == "sites" else self.orgs.get(rid)
        keys, seen = set(), set()
        while o and o["org_id"] not in seen:
            seen.add(o["org_id"])
            keys |= {k for k in (name_key(o.get("ultimate_parent_name")),) if k}
            o = self.orgs.get(o.get("parent_org_id") or "")
            if o:
                keys |= self.org_keys(o["org_id"])
        return keys

    def notes_text(self, table, rid):
        if (table, rid) not in self._notes:
            rec = self.record(table, rid)
            texts = [rec.get("notes")]
            if table == "sites":
                texts.append((self.orgs.get(rec.get("org_id")) or {}).get("notes"))
            self._notes[(table, rid)] = " " + " ".join(squash(t) for t in texts if t) + " "
        return self._notes[(table, rid)]


# ---------------------------------------------------------------- quote parsing

def family_of(source_ref):
    for fam in FAMILIES:
        if source_ref.startswith(fam[0]):
            return fam
    return None


def labelled_fields(q):
    parts = LABEL_RE.split(q)
    if len(parts) < 3 or parts[0].strip():
        return None
    out = {}
    for k, v in zip(parts[1::2], parts[2::2]):
        out.setdefault(k.strip().lower().replace(" ", "_"), v.strip().rstrip(";").strip())
    return out


def present(v):
    return v if v and v.strip() not in ("—", "-", "–") else ""


def parse_quote(q, fam):
    """{"names": [...], "alt_names": [...], "addr": str} or {"bad": reason}. alt_names = a permit's facility label."""
    _, fmt, op_fields, addr_field, _ = fam
    if fmt == "echo":  # NAME; STREET, CITY, ST ZIP; FRS registry ...
        a = [x.strip() for x in PAREN_RE.sub(" ", q).split(";")]  # "(ABC; FORMERLY ...)" is not a field break
        if len(a) < 3 or not re.search(r",\s*[A-Z]{2}\s+\d{4,5}", a[1]):
            return {"bad": "parse_failed"}
        return {"names": [a[0]], "alt_names": [], "addr": a[1]}
    if fmt == "osha":  # NAME, STREET, CITY, ST ZIP; the name may hold commas, the street is the first numbered part
        a = [x.strip() for x in q.split(",")]
        if len(a) < 3 or not re.match(r"^[A-Z]{2}\s+\d[\dE-]{3,9}$", a[-1]):  # ZIPs arrive as 4, 5, 9 digits or "317E6"
            return {"bad": "parse_failed"}
        i = next((i for i in range(1, len(a) - 2) if re.match(r"\d", a[i])), None)
        if i is None and len(a) >= 4:  # no numbered part: the street sits before CITY, ST ZIP ("One Innovation Dr")
            i = len(a) - 3
        if i is None:
            return {"names": [a[0]], "alt_names": [], "addr": ""}
        return {"names": [", ".join(a[:i])], "alt_names": [], "addr": ", ".join(a[i:])}
    d = labelled_fields(q)
    if d is None:
        return {"bad": "parse_failed"}
    names = [present(d.get(f)) for f in op_fields if present(d.get(f))]
    if not names:
        return {"bad": "parse_failed"}
    if not any(re.search(r"[A-Za-z]", n) for n in names):
        return {"bad": "operator_not_a_name", "facility": present(d.get("facility")), "addr": present(d.get(addr_field))}
    return {"names": names, "alt_names": [present(d.get("facility"))] if present(d.get("facility")) else [],
            "addr": present(d.get(addr_field))}


def quote_street(addr):
    """street_key of the first comma part of a quoted "STREET, CITY, ST ZIP" (leading unit-only parts skipped)."""
    parts = (addr or "").split(",")
    while len(parts) > 1 and UNIT_ONLY_RE.match(parts[0].lower()):
        parts = parts[1:]
    return street_key(parts[0])


def has_civic_number(key):
    """A token holding a digit ("198a", "n44") or a leading number word ("one innovation dr")."""
    t = key.split()
    return bool(t) and (any(re.search(r"\d", x) for x in t) or t[0] in NUMBER_WORDS)


def unit_ids(s):
    """Suite/unit identifiers a street string states ("100" from "191 American Blvd, Suite 100"); street_key drops them."""
    found, street_seen = [], False
    for part in (s or "").lower().split(","):
        if UNIT_ONLY_RE.match(part):
            found.append(part)
            continue
        if street_seen:
            break
        street_seen = True
        m = UNIT_RE.search(part)
        if m:
            found.append(m.group(0))
    return {m.group(1) for m in (UNIT_ID_RE.search(x) for x in found) if m}


def street_reason(rec_street, addr):
    """"" when the quoted street binds to the record's street, else a FAIL or UNINSPECTABLE reason."""
    rk, qk = street_key(rec_street), quote_street(addr)
    if not rk:
        return "record_no_street"
    if not qk or re.match(r"p ?o box\b", qk) or (rk != qk and not has_civic_number(qk)):
        return "quote_no_street"
    if rk != qk:
        return "street_differs"
    if not has_civic_number(qk):
        return "no_civic_number"  # equal keys with no civic number cannot tell two places apart: UNINSPECTABLE
    ru, qu = unit_ids(rec_street), unit_ids(addr)
    return "unit_differs" if ru and qu and not ru & qu else ""


def hq_in_quote(addr, org):
    city, st = squash(org.get("hq_city")), (org.get("hq_state") or "").strip().lower()
    a = " " + squash(addr) + " "
    return bool(city and st) and any(f" {city} {s} " in a for s in (st, STATE_KEYS.get(st, st)))


# ---------------------------------------------------------------- verdict

def name_keys(names):
    """name_keys of each quoted name and of each comma part ("ACME, ACME CO" is establishment, company in OSHA ITA)."""
    cands = [n for name in names for n in [name] + name.split(",")]
    return {k for n in cands for k in (name_key(n), name_key(PAREN_RE.sub(" ", n))) if k}


def name_alternatives(idx, table, rid, qkeys, alt_keys, held):
    """Owner-question bases a strict FAIL would pass under (measured, never passing)."""
    alts = []
    if {q.replace(" ", "") for q in qkeys} & {h.replace(" ", "") for h in held}:
        alts.append("spacing")  # "A.B.C. Co" vs "ABC Co"
    if alt_keys & held:
        alts.append("facility_label")
    if qkeys & idx.parent_keys(table, rid):
        alts.append("parent")
    notes = idx.notes_text(table, rid)
    if any(len(k) >= 5 and f" {k} " in notes for k in qkeys):
        alts.append("notes")
    if any(q.startswith(h + " ") for q in qkeys for h in held):
        alts.append("leading_run")
    if any(set(q.split()) <= set(h.split()) or set(h.split()) <= set(q.split()) for q in qkeys for h in held):
        alts.append("token_subset")
    return alts


def street_limit(rec_key, q_key):
    """Why street_key may reject a true match (measured, never passing)."""
    r, q = rec_key.split(), q_key.split()
    if not r or not q:
        return ""
    m = re.fullmatch(r"(\d+)\s+(\d+)\s+(.*)", rec_key)  # "1201-1205 main st" -> range 1201..1205
    if m and q[0].isdigit() and int(m[1]) <= int(q[0]) <= int(m[2]) and m[3] == " ".join(q[1:]):
        return "number_in_recorded_range"
    if [NUMBER_WORDS.get(t, t) for t in r] == [NUMBER_WORDS.get(t, t) for t in q]:
        return "number_word"
    if r[1:] == q[1:]:  # "734 hollis rd" vs "736 hollis rd": another number on the same street (a campus?)
        return "same_street_other_number"
    if r[0] == q[0]:  # "100 hwy 9 e" vs "100 us hwy 9 e" (subset) or "100 elm ave" vs "100 elm way"
        return "same_number_token_subset" if set(r) <= set(q) or set(q) <= set(r) else "same_number_other"
    return ""


def judge(ev, idx):
    """(verdict, reason, detail dict) for one evidence row."""
    table, rid, detail, src = ev["record_table"], ev["record_id"], ev["claim_detail"], ev["source_ref"]
    if table not in ("sites", "organizations", "ecosystem"):
        return "UNINSPECTABLE", "other_table", {}
    rec = idx.record(table, rid)
    if rec is None:
        return "UNINSPECTABLE", "record_not_found", {}
    i = detail.find("quote:")
    if i < 0 or not detail[i + 6:].strip():
        return "UNINSPECTABLE", "no_quote", {}
    if src.startswith("http"):
        return "UNINSPECTABLE", "free_text_web_quote", {}
    fam = family_of(src)
    if fam is None:
        return "UNINSPECTABLE", "unknown_source_family", {}
    p = parse_quote(detail[i + 6:].strip(), fam)
    if "bad" in p:
        info = {}
        if p.get("facility"):  # measured: the verdict if a shifted-column source's facility label were the operator
            v, why, _ = judge(dict(ev, claim_detail="quote: " + "; ".join(
                f"{k}: {p[k2]}" for k, k2 in (("permittee", "facility"), ("address", "addr")) if p[k2])), idx)
            info["if_facility_operator"] = f"{v} {why}".strip()
        return "UNINSPECTABLE", p["bad"], info
    qkeys = name_keys(p["names"])
    alt_keys = {k for n in p["alt_names"] for k in (name_key(n), site_name_key(n, rec.get("city") or "")) if k}
    held = idx.held_keys(table, rid)
    reasons, info = [], {}
    if not qkeys & held:
        reasons.append("name_not_held")
        info["name_alt"] = ";".join(name_alternatives(idx, table, rid, qkeys, alt_keys, held))
    else:  # measured: which quoted form and which held name matched (audits the false-PASS side)
        whole = {k for n in p["names"] for k in (name_key(n), name_key(PAREN_RE.sub(" ", n))) if k}
        org = idx.org_keys(rec.get("org_id") if table == "sites" else rid)
        lead = name_key(LOCALITY_SEP_RE.split(PAREN_RE.sub(" ", rec.get("site_name") or ""))[0])
        info["name_basis"] = ("whole" if whole & held else "comma_part") + "/" + (
            "org" if qkeys & org else "site_name_lead" if lead in qkeys else "site_name_other")
    if table == "sites":
        why = street_reason(rec.get("street_address"), p["addr"])
        if why == "no_civic_number" and not reasons:
            return "UNINSPECTABLE", why, info
        if why and why != "no_civic_number":
            reasons.append(why)
        city = squash(rec.get("city"))
        if not why and city and f" {city} " not in f" {squash(p['addr'])} ":
            info["city_not_in_quote"] = "1"  # measured only: the gate binds the street, not the city
        st = re.search(r",\s*([A-Za-z][A-Za-z ]*?)\s*,?\s+\d[\dE-]{3,9}\s*$", p["addr"] or "")
        q_st = st and (st[1].upper() if len(st[1]) == 2 else STATE_NAMES.get(st[1].title(), "?"))
        if not why and q_st and q_st != (rec.get("state") or "").upper():
            info["state_differs"] = q_st  # measured only
        if why == "street_differs":
            info["street_limit"] = street_limit(street_key(rec.get("street_address")), quote_street(p["addr"]))
    elif ev["claim_type"] == "address":
        basis = fam[4]
        info["hq_basis"] = basis
        if basis == "facility":
            reasons.append("hq_from_facility_or_permit")
        elif basis == "s5":
            reasons.append("hq_from_s5_identity_source")
        if not hq_in_quote(p["addr"], rec):
            reasons.append("hq_city_state_differs")
    return ("FAIL", "+".join(reasons), info) if reasons else ("PASS", "", info)


# ---------------------------------------------------------------- modes

def source_family(src):
    if src.startswith("http"):
        return "url"
    fam = family_of(src)
    return fam[0].strip() if fam else "other:" + re.split(r"[(,:;]", src)[0].strip()[:30]


def judge_all(evs, idx):
    out = []
    for ev in evs:
        v, reason, info = judge(ev, idx)
        out.append({"evidence_id": ev["evidence_id"], "at": ev["_at"], "record_table": ev["record_table"],
                    "record_id": ev["record_id"], "claim_type": ev["claim_type"], "created_by": ev["created_by"],
                    "source_family": source_family(ev["source_ref"]), "verdict": v, "reason": reason,
                    "name_alt": info.get("name_alt", ""), "street_limit": info.get("street_limit", ""),
                    "hq_basis": info.get("hq_basis", ""), "if_facility_operator": info.get("if_facility_operator", ""),
                    "city_not_in_quote": info.get("city_not_in_quote", ""), "state_differs": info.get("state_differs", ""),
                    "name_basis": info.get("name_basis", "")})
    return out


def raw_evidence_count(ref):
    """Rows counted without the csv module: lines that open with an evidence id (an independent yield check)."""
    return sum(len(re.findall(r"^EVD-\d+,", text, re.M)) for _, text in data_files(ref, "evidence_*.csv"))


def report(results, total):
    assert len(results) == total, f"judged {len(results)} of {total} rows"
    by_v = Counter(r["verdict"] for r in results)
    print(f"evidence rows read: {total}; judged: {len(results)}; " + ", ".join(f"{k}={by_v[k]}" for k in
                                                                              ("PASS", "FAIL", "UNINSPECTABLE")))
    print("\nby verdict and reason:")
    for (v, why), n in sorted(Counter((r["verdict"], r["reason"]) for r in results).items(), key=lambda kv: -kv[1]):
        print(f"  {n:7d}  {v:13s} {why}")
    for col in ("created_by", "source_family"):
        print(f"\nby {col} (rows: PASS / FAIL / UNINSPECTABLE):")
        tab = defaultdict(Counter)
        for r in results:
            tab[r[col]][r["verdict"]] += 1
        for k, c in sorted(tab.items(), key=lambda kv: -sum(kv[1].values())):
            print(f"  {sum(c.values()):7d}  {c['PASS']:6d} / {c['FAIL']:6d} / {c['UNINSPECTABLE']:6d}  {k}")


def write_csv(results, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0]) if results else ["evidence_id"])
        w.writeheader()
        w.writerows(results)


def changed_rows(base_evs, head_evs):
    """Head rows that are new, or whose binding fields differ from the base row with the same id (a re-pointed row)."""
    base = {e["evidence_id"]: tuple(e[f] for f in BINDING_FIELDS) for e in base_evs}
    return [e for e in head_evs if base.get(e["evidence_id"]) != tuple(e[f] for f in BINDING_FIELDS)]


def tasks_files(ref, name):
    if ref is None:
        return [(str(p.relative_to(ROOT)), p.read_text(encoding="utf-8")) for p in sorted((ROOT / "tasks").rglob(name))]
    return [(p, git("show", f"{ref}:{p}")) for p in git("ls-tree", "-r", "--name-only", ref, "tasks/").split()
            if p.endswith("/" + name)]


def load_waivers(files):
    """{evidence_id: (path:line, reason, reviewer)}; raises ValueError on a malformed line."""
    out = {}
    for path, text in files:
        reader = csv.DictReader(io.StringIO(text))
        if tuple(reader.fieldnames or ()) != WAIVER_COLS:
            raise ValueError(f"{path}: header must be {','.join(WAIVER_COLS)}")
        for r in reader:
            if not all((r.get(c) or "").strip() for c in WAIVER_COLS):
                raise ValueError(f"{path}:{reader.line_num}: evidence_id, reason and reviewer are all required")
            out[r["evidence_id"].strip()] = (f"{path}:{reader.line_num}", r["reason"].strip(), r["reviewer"].strip())
    return out


def provenance_missing(new_evs, has_check):
    """{created_by: row count} for labels none of whose whitespace tokens names a tasks/<token>/check.py."""
    missing = Counter()
    for e in new_evs:
        label = e["created_by"].strip()
        tokens = [t for t in [label] + label.split() if t and ".." not in t and not t.startswith("/")]
        if not any(has_check(t) for t in tokens):
            missing[label] += 1
    return missing


def resolve_base(ref, head):
    return git("merge-base", ref, head or "HEAD").strip()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true", help="report every evidence row by verdict, created_by and source")
    g.add_argument("--new-since", metavar="REF", help="gate rows added or re-pointed since the merge-base with REF")
    g.add_argument("--provenance-since", metavar="REF", help="require tasks/<created_by>/check.py for new rows")
    ap.add_argument("--head", help="git ref to read instead of the working tree")
    ap.add_argument("--out", help="write per-row verdicts to this CSV")
    a = ap.parse_args(argv)
    try:
        head_evs = rows(a.head, "evidence_*.csv")
        base = resolve_base(a.new_since or a.provenance_since, a.head) if not a.all else None
    except subprocess.CalledProcessError as e:
        print(f"binding gate: cannot read git state ({e.stderr.strip()}); failing closed")
        return 2
    if not head_evs:
        print("binding gate: zero evidence rows read; failing closed")
        return 2
    if len({e["evidence_id"] for e in head_evs}) != len(head_evs):
        print("binding gate: duplicate evidence_id on the head tree; failing closed")
        return 2
    evs = head_evs if a.all else changed_rows(rows(base, "evidence_*.csv"), head_evs)

    if a.provenance_since:
        if a.head is None:
            def has_check(t): return (ROOT / "tasks" / t / "check.py").is_file()
        else:
            paths = set(git("ls-tree", "-r", "--name-only", a.head, "tasks/").split())
            def has_check(t): return f"tasks/{t}/check.py" in paths
        missing = provenance_missing(evs, has_check)
        labels = Counter(e["created_by"].strip() for e in evs)
        print(f"provenance: {len(evs)} evidence rows added or re-pointed since {base[:10]} under {len(labels)} "
              f"created_by label(s)")
        for label, n in sorted(missing.items()):
            print(f"  MISSING tasks/<folder>/check.py for created_by '{label}' ({n} rows): name the folder by one "
                  f"word of created_by")
        return 1 if missing else 0

    idx = Index.load(a.head)
    results = judge_all(evs, idx)
    if a.out:
        write_csv(results, a.out)
    if a.all:
        raw = raw_evidence_count(a.head)
        if raw != len(head_evs):
            print(f"binding gate: csv read {len(head_evs)} evidence rows but {raw} lines open with an evidence id")
            return 2
        report(results, len(head_evs))
        return 0
    try:
        waivers = load_waivers(tasks_files(a.head, "BINDING_WAIVERS.csv"))
    except ValueError as e:
        print(f"binding gate: malformed waiver file: {e}")
        return 2
    report(results, len(evs)) if results else None
    bad = [r for r in results if r["verdict"] != "PASS" and r["evidence_id"] not in waivers]
    waived = sum(r["verdict"] != "PASS" and r["evidence_id"] in waivers for r in results)
    print(f"\nbinding gate: {len(results)} rows added or re-pointed since {base[:10]}; "
          f"{len(results) - len(bad) - waived} PASS, {waived} waived, {len(bad)} blocking")
    for r in bad[:200]:
        print(f"  {r['verdict']:13s} {r['reason'] or '-':40s} {r['evidence_id']} {r['at']}")
    if len(bad) > 200:
        print(f"  ... and {len(bad) - 200} more (use --out for the full list)")
    if bad:
        print("Fix the row, or add it to a tasks/<folder>/BINDING_WAIVERS.csv (evidence_id,reason,reviewer).")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
