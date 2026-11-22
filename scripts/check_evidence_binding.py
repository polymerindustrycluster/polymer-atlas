#!/usr/bin/env python3
"""Evidence binding gate: is an evidence row's quote about the record it is filed on?

validate.py checks an evidence row's form, never whether its quote witnesses that record. On 2026-11-22 two join
batches (about 34,000 rows) passed every check while a first-cut test found 28% did not bind: the quote named another
operator, another street, or claimed a headquarters from a plant permit (tasks/evidence-binding-gate-2026-11-22/).

Every evidence row gets exactly one verdict:
  PASS            the quoted operator is a name the record holds (exact name_key, scripts/atlas.py); for a site row the
                  quoted street equals the site's street_address under street_key; for an organization `address` row
                  the source states the entity's own address and the quoted city and state are the record's HQ.
                  A web (free-text) quote passes when it is bound by its source: an own_site URL on the record's own
                  website domain, or a directory/press quote that contains a held name; a site address/existence
                  row also needs the street's civic number and first street word in the quote, and an organization
                  address row its HQ city and state. Any other site row stays UNINSPECTABLE.
  FAIL            with reasons: name_not_held, street_differs, unit_differs (both state a suite or unit and they
                  differ; street_key drops units), record_no_street, quote_no_street, hq_city_state_differs,
                  hq_from_facility_or_permit, hq_from_s5_identity_source (FMCSA filed address or a state filing,
                  SCHEMA §4.8 S-5); web quotes: not_own_site (own_site URL off the record's website domain),
                  street_absent_from_quote.
  UNINSPECTABLE   with a reason: no_quote, other_table, record_not_found, unknown_source_family, parse_failed,
                  operator_not_a_name (shifted columns such as "permittee: 3"), no_civic_number (equal street keys with
                  no civic number, such as a bare road or park name); web quotes: no_record_website,
                  name_absent_from_quote, web_record_no_street, record_street_no_civic_number, web_class_untested
                  (registry, government_filing), web_site_row_no_street_claim, hq_absent_from_quote. Never a pass.

Strict reading (owner questions, measured in the name_alt column, never passing): a parent's name, a name found only
in the record's notes, a permit's facility label, a quoted name that merely starts with a held name.

Usage:
  python3 scripts/check_evidence_binding.py --all [--head REF] [--out verdicts.csv]
  python3 scripts/check_evidence_binding.py --new-since origin/main      # PR gate: rows added or re-pointed since
  python3 scripts/check_evidence_binding.py --provenance-since origin/main  # tasks/<created_by>/check.py required
  python3 scripts/check_evidence_binding.py --sample 20 --seed 7 [--since origin/main]  # audit only, admits nothing
--new-since exits 1 on any FAIL row (no waiver exists: fix the row or make it a lead), and on any UNINSPECTABLE row
without a per-row proof line in tasks/<folder named by a created_by word>/BINDING_PROOF.csv
(evidence_id,capture,capture_sha256,quote_offset,quote_length; see check_proofs). Exit 2 = could not check.
"""
import argparse
import csv
import hashlib
import io
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from atlas import (LOCALITY_SEP_RE, SUFFIX, UNIT_ONLY_RE, UNIT_RE, domain_key, name_key,  # noqa: E402
                   org_name_fields, site_name_key, squash, street_key)
from build_echo_spine import STATE_NAMES  # noqa: E402

csv.field_size_limit(10**9)
BINDING_FIELDS = ("record_table", "record_id", "claim_type", "claim_detail", "source_ref")
PROOF_COLS = ("evidence_id", "capture", "capture_sha256", "quote_offset", "quote_length")
ARCHIVE_RE = re.compile(r"https://web\.archive\.org/web/\d{14}/\S+$")
DIRECTIONS = {"n", "s", "e", "w", "ne", "nw", "se", "sw"}

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
        return judge_web(ev, rec, idx, detail[i + 6:].strip())
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


def record_websites(idx, table, rec):
    """domain_keys of the record's own website: a site's organization website, else the organization's own."""
    o = idx.orgs.get(rec.get("org_id")) if table == "sites" else rec
    keys = (domain_key(w) for w in re.split(r"[;,\s]+", (o or {}).get("website") or ""))
    return [k for k in keys if re.match(r"[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}(/|$)", k)]  # notes in the field are not hosts


SECOND_LEVEL = {"co", "com", "ac", "gov", "org", "net", "edu", "ne", "or"}  # "acme.co.uk", "acme.com.au"


def registrable(host):
    """Last two host labels, three under a country second-level label. shortcut: no public-suffix list; add one if
    a country code outside SECOND_LEVEL shows up among not_own_site rows."""
    t = host.split(".")
    return ".".join(t[-3:] if len(t) > 2 and len(t[-1]) == 2 and t[-2] in SECOND_LEVEL else t[-2:])


def own_domain(src, site):
    """Does the source URL (domain_key) sit on the record's website (domain_key)? Registrable domain, www-insensitive;
    on a shared platform host (atlas.PLATFORM_HOSTS: wixsite, LinkedIn ...) the same host and a path under the site's."""
    (sh, _, sp), (wh, _, wp) = src.partition("/"), site.partition("/")
    if "/" in site:
        return sh == wh and (sp + "/").startswith(wp.rstrip("/") + "/" if wp.strip("/") else "")
    return "/" not in src and registrable(sh) == registrable(wh)


def street_tokens(s):
    """Tokens normalised as street_key normalises a street line, number words as digits."""
    s = re.sub(r"\b(\d+)(st|nd|rd|th)\b", r"\1", (s or "").lower())
    return [NUMBER_WORDS.get(t, SUFFIX.get(t, t)) for t in squash(s).split()]


def web_street_parts(rec_street):
    """(civic number, first street word) of a record street, or a reason it has none."""
    t = street_tokens(street_key(rec_street))
    if not t:
        return "web_record_no_street"
    if not has_civic_number(" ".join(t[:1])):
        return "record_street_no_civic_number"
    words = [w for w in t[1:] if w not in DIRECTIONS]
    if len(words) > 2 and len(words[0]) == 1:
        words = words[1:]  # "2210 C Larkspur Rd": the letter belongs to the civic number
    return t[0], words[0] if words else ""


def web_street_reason(rec_street, quote):
    """A free-text quote must show the record street's civic number and first street word (ruling 2026-11-22)."""
    parts = web_street_parts(rec_street)
    if isinstance(parts, str):
        return parts
    q = set(street_tokens(quote))
    return "" if parts[0] in q and (not parts[1] or parts[1] in q) else "street_absent_from_quote"


def street_gap(rec_street, quote):
    """Measured on PASS rows: the civic number and first street word are not within two tokens of each other."""
    num, word = web_street_parts(rec_street)
    q = street_tokens(quote)
    return bool(word) and not any(x == num and word in q[i + 1:i + 3] for i, x in enumerate(q))


def web_street_alt(rec_street, quote):
    """Measured, never passing: the street is in the quote once spacing is ignored ("Bragg Ridge" / "Braggridge")."""
    t = [w for w in street_tokens(street_key(rec_street)) if w not in DIRECTIONS]
    q = "".join(w for w in street_tokens(quote) if w not in DIRECTIONS)
    return "spacing" if len(t) > 1 and "".join(t[:3]) in q else ""


def judge_web(ev, rec, idx, quote):
    """A web quote is free text: bind it by the source domain, the quoted street and the quoted name."""
    table, cls, ct = ev["record_table"], ev["source_class"], ev["claim_type"]
    fails, unins, info = [], "", {}
    site_street = table == "sites" and ct in ("address", "existence")
    if site_street:
        why = web_street_reason(rec.get("street_address"), quote)
        if why == "street_absent_from_quote":
            fails.append(why)
            if web_street_alt(rec.get("street_address"), quote):
                info["street_limit"] = "spacing"
        elif why:
            unins = why
    if cls == "own_site":
        sites = record_websites(idx, table, rec)
        src = domain_key(ev["source_ref"])
        if not sites:
            unins = unins or "no_record_website"
        elif not any(own_domain(src, w) for w in sites):
            fails.append("not_own_site")
            host = re.sub(r"[^a-z0-9]", "", src.split("/")[0])
            if any(len(k.split()[0]) >= 4 and k.split()[0] in host for k in idx.held_keys(table, ev["record_id"])):
                info["name_alt"] = "name_in_host"  # measured: a sister or regional domain carrying a held name
    elif cls in ("directory", "press"):
        q = f" {name_key(quote)} "
        hits = [k for k in idx.held_keys(table, ev["record_id"]) if f" {k} " in q]
        if not hits:
            unins = unins or "name_absent_from_quote"
        info["web_bound"] = f"name_{min(len(k.split()) for k in hits)}w" if hits else ""
    else:
        unins = unins or "web_class_untested"  # registry, government_filing: no mechanical test in the ruling
    if fails:
        return "FAIL", "+".join(fails), info
    if unins:
        return "UNINSPECTABLE", unins, info
    if table == "sites" and not site_street:
        return "UNINSPECTABLE", "web_site_row_no_street_claim", info  # own domain or name binds the company, not the plant
    if table != "sites" and ct == "address" and not hq_in_quote(quote, rec):
        return "UNINSPECTABLE", "hq_absent_from_quote", info
    info["web_bound"] = (info.get("web_bound") or "domain") + (
        "+street_gap" if site_street and street_gap(rec.get("street_address"), quote) else "")
    return "PASS", "", info


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
                    "name_basis": info.get("name_basis", ""), "web_bound": info.get("web_bound", "")})
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


def tasks_file(ref, path):
    """Bytes of a repository file at ref (None = working tree), or None when it does not exist."""
    if ref is None:
        f = ROOT / path
        return f.read_bytes() if f.is_file() else None
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{ref}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def label_tokens(label):
    """Folder names a created_by label may use: the whole label, then each whitespace word."""
    label = label.strip()
    return [t for t in [label] + label.split() if t and ".." not in t and not t.startswith("/")]


def quote_of(ev):
    return ev["claim_detail"].partition("quote:")[2].strip()


def check_proofs(results, evs, archive, read):
    """Problems with the per-row proof of UNINSPECTABLE rows, one line each (controller ruling 2026-11-22).

    Every UNINSPECTABLE row needs a line in tasks/<folder named by a created_by word>/BINDING_PROOF.csv: the capture it
    was read from (a Wayback archive_ref, which must equal the row's data/archive_links.csv ref where one exists, or a
    repo path to a stored capture), the capture's sha256, and the quote's character offset and length in the capture.
    A repo capture is verified here: its hash, and the row's quote at that offset. An archive capture is not fetched.
    evs: {evidence_id: row}; archive: {evidence_id: archive_ref}; read(path) -> bytes or None.
    """
    need = defaultdict(list)
    for r in results:
        if r["verdict"] == "UNINSPECTABLE":
            need[r["created_by"].strip()].append(r["evidence_id"])
    proofs, problems, files = {}, [], {}
    for label, ids in sorted(need.items()):
        path = next((f"tasks/{t}/BINDING_PROOF.csv" for t in label_tokens(label)
                     if read(f"tasks/{t}/BINDING_PROOF.csv") is not None), None)
        if path is None:
            problems.append(f"created_by '{label}': {len(ids)} UNINSPECTABLE rows and no tasks/<folder>/BINDING_PROOF.csv;"
                            f" each needs a proof line, or is a lead until proved")
            continue
        if path not in files:
            reader = csv.DictReader(io.StringIO(read(path).decode("utf-8")))
            files[path] = []
            if tuple(reader.fieldnames or ()) != PROOF_COLS:
                problems.append(f"{path}: header must be {','.join(PROOF_COLS)}")
            else:
                for row in reader:
                    eid = (row["evidence_id"] or "").strip()
                    if eid in proofs:
                        problems.append(f"{path}:{reader.line_num}: second proof line for {eid}")
                    proofs[eid] = (f"{path}:{reader.line_num}", row)
        for eid in ids:
            if eid not in proofs:
                problems.append(f"{eid} ({label}): no proof line in {path}")
                continue
            at, row = proofs[eid]
            why = proof_problem(row, evs[eid], archive.get(eid), read)
            if why:
                problems.append(f"{at}: {eid}: {why}")
    return problems


def proof_problem(row, ev, archive_ref, read):
    cap, sha, off, n = (row[c].strip() for c in PROOF_COLS[1:])
    if not re.fullmatch(r"[0-9a-f]{64}", sha):
        return "capture_sha256 is not 64 lowercase hex digits"
    if not (off.isdigit() and n.isdigit() and int(n) > 0):
        return "quote_offset and quote_length must be whole numbers, the length above zero"
    if cap.startswith("http"):
        if not ARCHIVE_RE.match(cap):
            return "an http capture must be a Wayback archive ref (https://web.archive.org/web/<14 digits>/<url>)"
        if archive_ref and cap != archive_ref:
            return "capture differs from the row's data/archive_links.csv archive_ref"
        return ""  # shortcut: CI does not fetch the web; the lane's check.py replays the capture, its reviewer re-runs it
    if not cap.startswith("tasks/") or ".." in cap:
        return "capture must be an archive ref or a repo path under tasks/"
    data = read(cap)
    if data is None:
        return f"capture file {cap} is not in the tree"
    if hashlib.sha256(data).hexdigest() != sha:
        return "capture_sha256 does not match the capture file"
    text, off, n = data.decode("utf-8", errors="replace"), int(off), int(n)
    if off + n > len(text):
        return "quote span runs past the end of the capture"
    quote = quote_of(ev)
    if quote and text[off:off + n] != quote:
        return "the row's quote is not at that offset in the capture"
    return ""


def audit_sample(results, n, seed):
    """Audit of the gate, never admission: N PASS rows per created_by label, chosen by sha256(seed:evidence_id), for a
    reviewer to read; the share found unbound estimates the gate's escape rate."""
    by_label = defaultdict(list)
    for r in results:
        if r["verdict"] == "PASS":
            by_label[r["created_by"].strip()].append(r)
    return {k: sorted(v, key=lambda r: hashlib.sha256(f"{seed}:{r['evidence_id']}".encode()).hexdigest())[:n]
            for k, v in sorted(by_label.items())}


def provenance_missing(new_evs, has_check):
    """{created_by: row count} for labels none of whose whitespace tokens names a tasks/<token>/check.py."""
    missing = Counter()
    for e in new_evs:
        if not any(has_check(t) for t in label_tokens(e["created_by"])):
            missing[e["created_by"].strip()] += 1
    return missing


def resolve_base(ref, head):
    return git("merge-base", ref, head or "HEAD").strip()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true", help="report every evidence row by verdict, created_by and source")
    g.add_argument("--new-since", metavar="REF", help="gate rows added or re-pointed since the merge-base with REF")
    g.add_argument("--provenance-since", metavar="REF", help="require tasks/<created_by>/check.py for new rows")
    g.add_argument("--sample", metavar="N", type=int, help="audit only: list N PASS rows per created_by label to read")
    ap.add_argument("--seed", default="1", help="--sample seed")
    ap.add_argument("--since", metavar="REF", help="--sample: only rows added or re-pointed since REF")
    ap.add_argument("--head", help="git ref to read instead of the working tree")
    ap.add_argument("--out", help="write per-row verdicts to this CSV")
    a = ap.parse_args(argv)
    try:
        head_evs = rows(a.head, "evidence_*.csv")
        since = a.new_since or a.provenance_since or (a.since if a.sample else None)
        base = resolve_base(since, a.head) if since else None
    except subprocess.CalledProcessError as e:
        print(f"binding gate: cannot read git state ({e.stderr.strip()}); failing closed")
        return 2
    if not head_evs:
        print("binding gate: zero evidence rows read; failing closed")
        return 2
    if len({e["evidence_id"] for e in head_evs}) != len(head_evs):
        print("binding gate: duplicate evidence_id on the head tree; failing closed")
        return 2
    evs = head_evs if base is None else changed_rows(rows(base, "evidence_*.csv"), head_evs)

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
    if a.sample:
        print(f"audit sample (admits nothing): {a.sample} PASS rows per created_by label, seed {a.seed}; read each and "
              f"count the unbound ones to estimate the gate's escape rate")
        for label, picked in audit_sample(results, a.sample, a.seed).items():
            print(f"\n{label}")
            for r in picked:
                print(f"  {r['evidence_id']} {r['at']} {r['record_table']} {r['record_id']} {r['claim_type']}")
        return 0
    report(results, len(evs)) if results else None
    fails = [r for r in results if r["verdict"] == "FAIL"]
    n_unins = sum(r["verdict"] == "UNINSPECTABLE" for r in results)
    archive = {r["evidence_id"]: r["archive_ref"] for r in rows(a.head, "archive_links.csv")}
    problems = check_proofs(results, {e["evidence_id"]: e for e in evs}, archive, lambda path: tasks_file(a.head, path))
    print(f"\nbinding gate: {len(results)} rows added or re-pointed since {base[:10]}; "
          f"{len(results) - len(fails) - n_unins} PASS, {len(fails)} FAIL (blocking), {n_unins} UNINSPECTABLE "
          f"(admitted only by a per-row proof line)")
    for r in fails[:200]:
        print(f"  FAIL {r['reason']:40s} {r['evidence_id']} {r['at']}")
    if len(fails) > 200:
        print(f"  ... and {len(fails) - 200} more (use --out for the full list)")
    if fails:
        print("A FAIL row has no waiver: fix the row, or take it out and hold it as a lead.")
    for line in problems[:200]:
        print("  PROOF " + line)
    if len(problems) > 200:
        print(f"  ... and {len(problems) - 200} more proof problems")
    return 1 if fails or problems else 0

if __name__ == "__main__":
    sys.exit(main())
