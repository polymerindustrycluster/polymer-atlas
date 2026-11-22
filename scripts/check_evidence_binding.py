#!/usr/bin/env python3
"""Evidence binding gate: is an evidence row's quote about the record it is filed on?

validate.py checks an evidence row's form, never whether its quote witnesses that record. On 2026-11-22 two join
batches (about 34,000 rows) passed every check while a first-cut test found 28% did not bind: the quote named another
operator, another street, or claimed a headquarters from a plant permit (tasks/evidence-binding-gate-2026-11-22/).

Every evidence row gets exactly one verdict:
  PASS            structured sources only. The quoted operator is a name the record holds (exact name_key of the whole
                  field, never a comma part); for a site row matching.same_street(site street, quoted street) holds
                  (the repo's one street test, shared with derive_last_activity.py) and a quoted state equals the
                  site's; for an organization `address` row the source states the entity's own address and the quoted
                  city and state are the record's HQ. A web (free-text) quote is never PASS.
  FAIL            name_not_held, street_differs, unit_differs, record_no_street, quote_no_street, state_differs,
                  hq_city_state_differs, hq_from_facility_or_permit, hq_from_s5_identity_source (SCHEMA §4.8 S-5);
                  web quotes: street_absent_from_quote (no civic number directly followed by the record's street
                  word), unit_differs (every occurrence states another suite), not_own_site (an own_site URL off the
                  record's website; on a platform host, host and path must both match).
  READ_REQUIRED   a web quote the mechanics did not fail. Admitted only by its own proof line with a reading.
  UNINSPECTABLE   no_quote, other_table, record_not_found, unknown_source_family, parse_failed, operator_not_a_name,
                  no_civic_number. Admitted only by its own proof line, as READ_REQUIRED.

Strict reading (owner questions, measured in the name_alt column, never passing): a parent's name, a name found only
in the record's notes, a permit's facility label, a quoted name that merely starts with a held name, one comma part
of an operator field.

Usage:
  python3 scripts/check_evidence_binding.py --all [--head REF | --tree DIR] [--out verdicts.csv]
  python3 scripts/check_evidence_binding.py --new-since origin/main [--tree DIR]   # PR gate: rows added or changed
  python3 scripts/check_evidence_binding.py --verify-proofs origin/main [--tree DIR]  # and fetch archive captures
  python3 scripts/check_evidence_binding.py --provenance-since origin/main [--tree DIR]  # run tasks/<folder>/check.py
  python3 scripts/check_evidence_binding.py --sample 20 --seed 7 [--since origin/main]  # audit only, admits nothing
--new-since exits 1 on any FAIL row (no waiver exists) and on any READ_REQUIRED or UNINSPECTABLE row without a valid
line in tasks/<the folder its created_by names>/BINDING_PROOF.csv (columns: PROOF_COLS; see check_proofs). Exit 2 =
could not check (including a capture --verify-proofs could not fetch).

--tree DIR reads data/ and tasks/ from DIR, an untrusted checkout of the PR; the rules and this code come from the
trusted checkout that runs it. Nothing from DIR is executed except tasks/<folder>/check.py under --provenance-since,
which runs on a copy, with a stripped environment (no token), and without network only where `unshare` exists.
"""
import argparse
import csv
import hashlib
import io
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TREE = ROOT  # where data/ and tasks/ are read when no git ref is given; --tree moves it, ROOT stays the trusted code
sys.path.insert(0, str(ROOT / "scripts"))
from atlas import (LOCALITY_SEP_RE, PLATFORM_HOSTS, SUFFIX, UNIT_ONLY_RE, name_key, org_name_fields,  # noqa: E402
                   site_name_key, squash, street_key)
from build_echo_spine import STATE_NAMES  # noqa: E402
from matching import corporate_form_extension, has_civic_number, same_street, units  # noqa: E402  (PR #463)

csv.field_size_limit(10**9)
ARCHIVE_RE = re.compile(r"https://web\.archive\.org/web/\d{14}/\S+")
PROOF_COLS = ("evidence_id", "capture", "capture_sha256", "quote_offset", "quote_length", "verdict", "reader_family",
              "reader_model", "tie")
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


# ---------------------------------------------------------------- loading

def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout


def data_files(ref, pattern):
    """[(path, text)] for data/<pattern> at a git ref, or the working tree when ref is None. Merged exports skipped."""
    if ref is None:
        paths = sorted((TREE / "data").glob(pattern))
        if any(p.is_symlink() or not p.resolve().is_relative_to(TREE.resolve()) for p in paths):
            raise subprocess.CalledProcessError(2, "data_files", stderr=f"a data/{pattern} file is a symlink")
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


def street_part(addr):
    """The street comma-part of a quoted "STREET, CITY, ST ZIP" with any unit-only parts beside it ("Suite 5, 1 Elm St"
    or "1 Elm St, Suite 5"): what matching.same_street compares, so the gate and the derivation agree."""
    parts = (addr or "").split(",")
    lead = []
    while len(parts) > 1 and UNIT_ONLY_RE.match(parts[0].lower()):
        lead.append(parts.pop(0))
    trail = []
    for x in parts[1:]:
        if not UNIT_ONLY_RE.match(x.lower()):
            break
        trail.append(x)
    return ",".join(lead + parts[:1] + trail)


def quote_street(addr):
    """street_key of the quoted street line (leading unit-only parts skipped)."""
    return street_key(street_part(addr))


def street_reason(rec_street, addr):
    """"" exactly when matching.same_street holds; otherwise why not (a FAIL reason, or no_civic_number)."""
    if same_street(rec_street, street_part(addr)):
        return ""
    rk, qk = street_key(rec_street), quote_street(addr)
    if not rk:
        return "record_no_street"
    if not qk or not has_civic_number(qk) and rk != qk:
        return "quote_no_street"
    if rk != qk:
        return "street_differs"
    if not has_civic_number(qk) or len(qk.split()) < 2:
        return "no_civic_number"  # equal keys but a bare number, a PO box or no civic number: cannot tell places apart
    return "unit_differs"


def hq_in_quote(addr, org):
    city, st = squash(org.get("hq_city")), (org.get("hq_state") or "").strip().lower()
    a = " " + squash(addr) + " "
    return bool(city and st) and any(f" {city} {s} " in a for s in (st, STATE_KEYS.get(st, st)))


# ---------------------------------------------------------------- verdict

def name_keys(names):
    """name_keys of each quoted name as a whole: an operator field is one name, never split on commas."""
    return {k for n in names for k in (name_key(n), name_key(PAREN_RE.sub(" ", n))) if k}


def comma_part_keys(names):
    """Measured only (owner question): the comma parts of a quoted name ("ACME, ACME CO" in OSHA ITA)."""
    return {k for n in names for part in n.split(",")[1:] + n.split(",")[:1] if "," in n
            for k in (name_key(part),) if k}


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
    if not qkeys & held and table == "sites" and not street_reason(rec.get("street_address"), p["addr"]) and any(
            corporate_form_extension(h, q) for h in held for q in qkeys):
        info["name_basis"] = "corporate_form"  # owner ruling 2026-11-22: held name + corporate-form words, street passes
        if qkeys & idx.parent_keys(table, rid):
            info["name_alt"] = "parent"  # measured: the extended name is also a parent's name (flagged to the owner)
    elif not qkeys & held:
        reasons.append("name_not_held")
        alts = name_alternatives(idx, table, rid, qkeys, alt_keys, held)
        if comma_part_keys(p["names"]) & held:
            alts.append("comma_part")  # "ACME, ACME CO": one comma part is a held name (an owner question, never PASS)
        info["name_alt"] = ";".join(alts)
    else:  # measured: which held name matched (audits the false-PASS side)
        org = idx.org_keys(rec.get("org_id") if table == "sites" else rid)
        lead = name_key(LOCALITY_SEP_RE.split(PAREN_RE.sub(" ", rec.get("site_name") or ""))[0])
        info["name_basis"] = "org" if qkeys & org else "site_name_lead" if lead in qkeys else "site_name_other"
    if table == "sites":
        why = street_reason(rec.get("street_address"), p["addr"])
        st = re.search(r",\s*([A-Za-z][A-Za-z ]*?)\s*,?\s+\d[\dE-]{3,9}\s*$", p["addr"] or "")
        q_st = st and (st[1].upper() if len(st[1]) == 2 else STATE_NAMES.get(st[1].title(), ""))
        if q_st in STATE_NAMES.values() and rec.get("state") and q_st != rec["state"].strip().upper():
            reasons.append("state_differs")  # an explicit other state is contrary evidence (Codex review, PR #467)
        if why == "no_civic_number" and not reasons:
            return "UNINSPECTABLE", why, info
        if why and why != "no_civic_number":
            reasons.append(why)
        city = squash(rec.get("city"))
        if not why and city and f" {city} " not in f" {squash(p['addr'])} ":
            info["city_not_in_quote"] = "1"  # measured only: the gate binds the street, not the city
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


# Shared hosting where one host carries many unrelated tenants: the record's own site there is its host AND path.
# shortcut: a fixed list can never be complete; an unlisted shared host is compared by registrable domain, and every
# web row is READ_REQUIRED anyway, so a miss here costs a FAIL, never a PASS.
PLATFORMS = set(PLATFORM_HOSTS) | {
    "pages.dev", "netlify.app", "vercel.app", "herokuapp.com", "blogspot.com", "myshopify.com", "webflow.io",
    "carrd.co", "wix.com", "editorx.io", "azurewebsites.net", "cloudfront.net", "amazonaws.com", "firebaseapp.com",
    "web.app", "glitch.me", "000webhostapp.com", "jimdosite.com", "site123.me", "strikingly.com", "mystrikingly.com",
    "tumblr.com", "medium.com", "substack.com", "hs-sites.com", "ueniweb.com", "wpengine.com", "wpcomstaging.com"}
WEB_UNIT_RE = re.compile(r"^(?:suite|ste|unit|apt|apartment|room|rm)$")


def host_path(url):
    """(host, path) of a URL or bare domain: lowercase, no scheme, port, www., query or trailing slash."""
    s = re.sub(r"^[a-z][a-z0-9+.-]*://", "", (url or "").strip().lower())
    host, _, path = s.partition("/")
    host = re.sub(r":\d+$", "", host.rsplit("@", 1)[-1]).rstrip(".")
    host = host[4:] if host.startswith("www.") else host
    return host, path.split("?")[0].split("#")[0].strip("/")


def on_platform(host):
    return any(host == h or host.endswith("." + h) for h in PLATFORMS)


def record_websites(idx, table, rec):
    """(host, path) of the record's own website: a site's organization website, else the organization's own."""
    o = idx.orgs.get(rec.get("org_id")) if table == "sites" else rec
    hps = (host_path(w) for w in re.split(r"[;,\s]+", (o or {}).get("website") or ""))
    return [hp for hp in hps if re.fullmatch(r"[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}", hp[0])]  # notes are not hosts


SECOND_LEVEL = {"co", "com", "ac", "gov", "org", "net", "edu", "ne", "or"}  # "acme.co.uk", "acme.com.au"


def registrable(host):
    """Last two host labels, three under a country second-level label. shortcut: no public-suffix list; add one if
    a country code outside SECOND_LEVEL shows up among not_own_site rows."""
    t = host.split(".")
    return ".".join(t[-3:] if len(t) > 2 and len(t[-1]) == 2 and t[-2] in SECOND_LEVEL else t[-2:])


def own_domain(src, site):
    """Is the source URL on the record's own website? Registrable domain, www-insensitive; on a shared platform host
    the same host, and a path under the website's path (a bare platform root such as sites.google.com never matches)."""
    (sh, sp), (wh, wp) = src, site
    if on_platform(sh) or on_platform(wh):
        if sh != wh or (wh in PLATFORMS and not wp):
            return False
        return not wp or sp == wp or sp.startswith(wp + "/")
    return registrable(sh) == registrable(wh)


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
    if not words:
        return "record_street_no_civic_number"
    return t[0], words[0]


def web_street_reason(rec_street, quote):
    """FAIL unless the quote prints the record's civic number immediately before its first street word (a direction or
    one letter may sit between), and FAIL when every such occurrence states a suite or unit the record contradicts."""
    parts = web_street_parts(rec_street)
    if isinstance(parts, str):
        return parts
    num, word = parts
    q = street_tokens(quote)
    hits = [i for i, x in enumerate(q) if x == num and (q[i + 1:i + 2] == [word] or (
        q[i + 1:i + 2] and (q[i + 1] in DIRECTIONS or len(q[i + 1]) == 1) and q[i + 2:i + 3] == [word]))]
    if not hits:
        return "street_absent_from_quote"
    rec_units = units(rec_street)
    if not rec_units:
        return ""

    def conflicts(i):
        window = q[i + 2:i + 12]
        stated = {window[k + 1] for k in range(len(window) - 1)
                  if WEB_UNIT_RE.match(window[k]) and re.fullmatch(r"\d+[a-z]?|[a-z]", window[k + 1])}
        return bool(stated) and not stated & rec_units
    return "unit_differs" if all(conflicts(i) for i in hits) else ""


def web_street_alt(rec_street, quote):
    """Measured, never passing: the street is in the quote once spacing is ignored ("Bragg Ridge" / "Braggridge")."""
    t = [w for w in street_tokens(street_key(rec_street)) if w not in DIRECTIONS]
    q = "".join(w for w in street_tokens(quote) if w not in DIRECTIONS)
    return "spacing" if len(t) > 1 and "".join(t[:3]) in q else ""


def judge_web(ev, rec, idx, quote):
    """A web quote is free text. Code can show it is NOT about the record (FAIL) but never that it is: a quote with
    the right street and name can still describe a sibling plant, a former operator or a satellite office. So a web row
    is FAIL or READ_REQUIRED, never PASS (controller ruling 2026-11-22 after the Codex review of PR #467)."""
    table, cls, ct = ev["record_table"], ev["source_class"], ev["claim_type"]
    fails, why, info = [], "", {}
    if table == "sites" and ct in ("address", "existence"):
        w = web_street_reason(rec.get("street_address"), quote)
        if w in ("street_absent_from_quote", "unit_differs"):
            fails.append(w)
            if w == "street_absent_from_quote" and web_street_alt(rec.get("street_address"), quote):
                info["street_limit"] = "spacing"
        elif w:
            why = w
    if cls == "own_site":
        sites = record_websites(idx, table, rec)
        src = host_path(ev["source_ref"])
        if not sites:
            why = why or "no_record_website"
        elif not any(own_domain(src, w) for w in sites):
            fails.append("not_own_site")
            host = re.sub(r"[^a-z0-9]", "", src[0])
            if any(len(k.split()[0]) >= 4 and k.split()[0] in host for k in idx.held_keys(table, ev["record_id"])):
                info["name_alt"] = "name_in_host"  # measured: a sister or regional domain carrying a held name
    elif cls in ("directory", "press"):
        q = f" {name_key(quote)} "
        if not any(f" {k} " in q for k in idx.held_keys(table, ev["record_id"])):
            why = why or "name_absent_from_quote"
    else:
        why = why or "web_class_untested"  # registry, government_filing: no mechanical test in the ruling
    if fails:
        return "FAIL", "+".join(fails), info
    return "READ_REQUIRED", why or "mechanics_clear", info


# ---------------------------------------------------------------- modes

def source_family(src):
    if src.startswith("http"):
        return "url"
    fam = family_of(src)
    return fam[0].strip() if fam else "other:" + re.split(r"[(,:;]", src)[0].strip()[:30]


VERDICTS = ("PASS", "FAIL", "READ_REQUIRED", "UNINSPECTABLE")


def judge_all(evs, idx):
    out = []
    for ev in evs:
        v, reason, info = judge(ev, idx)
        assert v in VERDICTS, v
        out.append({"evidence_id": ev["evidence_id"], "at": ev["_at"], "record_table": ev["record_table"],
                    "record_id": ev["record_id"], "claim_type": ev["claim_type"], "created_by": ev["created_by"],
                    "source_family": source_family(ev["source_ref"]), "verdict": v, "reason": reason,
                    "name_alt": info.get("name_alt", ""), "street_limit": info.get("street_limit", ""),
                    "hq_basis": info.get("hq_basis", ""), "if_facility_operator": info.get("if_facility_operator", ""),
                    "city_not_in_quote": info.get("city_not_in_quote", ""), "name_basis": info.get("name_basis", "")})
    return out


def raw_evidence_count(ref):
    """Rows counted without the csv module: lines that open with an evidence id (an independent yield check)."""
    return sum(len(re.findall(r"^EVD-\d+,", text, re.M)) for _, text in data_files(ref, "evidence_*.csv"))


def report(results, total):
    by_v = Counter(r["verdict"] for r in results)
    assert len(results) == total == sum(by_v[v] for v in VERDICTS), f"judged {len(results)} of {total} rows"
    print(f"evidence rows read: {total}; judged: {len(results)}; " + ", ".join(f"{k}={by_v[k]}" for k in VERDICTS))
    print("\nby verdict and reason:")
    for (v, why), n in sorted(Counter((r["verdict"], r["reason"]) for r in results).items(), key=lambda kv: -kv[1]):
        print(f"  {n:7d}  {v:13s} {why}")
    for col in ("created_by", "source_family"):
        print(f"\nby {col} (rows: " + " / ".join(VERDICTS) + "):")
        tab = defaultdict(Counter)
        for r in results:
            tab[r[col]][r["verdict"]] += 1
        for k, c in sorted(tab.items(), key=lambda kv: -sum(kv[1].values())):
            print(f"  {sum(c.values()):7d}  " + " / ".join(f"{c[v]:6d}" for v in VERDICTS) + f"  {k}")


def write_csv(results, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0]) if results else ["evidence_id"])
        w.writeheader()
        w.writerows(results)


def changed_rows(base_evs, head_evs):
    """Head rows that are new, or differ from the base row with the same id in ANY column: every edit re-gates the row
    (Codex review of PR #467: an edit to source_class or created_by changes the verdict or the proof it needs).
    A column absent on one side counts as empty, so a migration that adds an empty column edits no row."""
    def strip(e):
        return {k: v for k, v in e.items() if k != "_at" and v}
    base = {e["evidence_id"]: strip(e) for e in base_evs}
    return [e for e in head_evs if base.get(e["evidence_id"]) != strip(e)]


# ---------------------------------------------------------------- tree, labels, folders

def inside_tree(path):
    """TREE/path when it is a regular file inside TREE (no symlink on the way, no escape), else None."""
    f = TREE / path
    try:
        if ".." in Path(path).parts or any(q.is_symlink() for q in [f, *f.parents] if TREE in q.parents or q == f):
            return None
        return f if f.is_file() and f.resolve().is_relative_to(TREE.resolve()) else None
    except OSError:
        return None


def tasks_file(ref, path):
    """Bytes of a repository file at ref (None = the tree being gated), or None when absent or unsafe."""
    if ref is None:
        f = inside_tree(path)
        return f.read_bytes() if f else None
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{ref}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def label_folder(label):
    """The one tasks/ folder a created_by label names, or "" (controller ruling 2026-11-22, provenance E):
    a one-word label names the folder of that exact name; a two-word label names the folder of its exact second word
    (the first word is the harness: "claude-code lane-a" -> lane-a). Three or more words name no folder. No prefix,
    no other word, no date variant: the name must match the folder exactly."""
    t = label.split()
    f = t[0] if len(t) == 1 else t[1] if len(t) == 2 else ""
    return f if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", f) and ".." not in f else ""


MODEL_FAMILIES = {  # family -> words that name it (product, company or model line)
    "anthropic": {"anthropic", "claude", "opus", "sonnet", "haiku", "fable"},
    "openai": {"openai", "gpt", "codex", "chatgpt"},
    "google": {"google", "gemini", "antigravity", "agy", "deepmind"},
    "xai": {"xai", "grok"},
}


def family_of_text(text):
    """The one model family a text names, or "" when it names none or several."""
    words = set(re.findall(r"[a-z]+", (text or "").lower()))
    fams = {f for f, keys in MODEL_FAMILIES.items() if words & keys}
    return fams.pop() if len(fams) == 1 else ""


def builder_family(readme):
    """The family on the folder README's "Built by:" line, or ""."""
    m = re.search(r"^\W*Built by:\s*(.+)$", (readme or b"").decode("utf-8", "replace"), re.M | re.I)
    return family_of_text(m[1]) if m else ""


# ---------------------------------------------------------------- per-row proof

class _Text(HTMLParser):
    SKIP = {"script", "style", "noscript", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        self.skip += tag in self.SKIP

    def handle_endtag(self, tag):
        self.skip -= tag in self.SKIP and self.skip > 0

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def norm_space(s):
    return re.sub(r"\s+", " ", s or "").strip()


def capture_text(data):
    """The text proof offsets index: an HTML capture's visible text (stdlib html.parser, entities decoded), any other
    capture decoded as UTF-8; whitespace collapsed to single spaces. Lanes import this so offsets agree."""
    s = data.decode("utf-8", errors="replace")
    if re.search(r"<(?:html|body|head|p|div|span|table|br)\b", s[:4096], re.I):
        t = _Text()
        t.feed(s)
        t.close()
        s = " ".join(t.parts)
    return norm_space(s)


def quote_of(ev):
    return norm_space(ev["claim_detail"].partition("quote:")[2])


def raw_capture_url(archive_ref):
    """The Wayback URL that serves the capture's original bytes (the id_ form); the proof digest covers those bytes."""
    return re.sub(r"(/web/\d{14})/", r"\1id_/", archive_ref, count=1)


def fetch_url(url, tries=3):
    req = urllib.request.Request(url, headers={"User-Agent": "evidence-check/1"})
    for k in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except (urllib.error.URLError, TimeoutError, OSError):
            if k == tries - 1:
                raise
            time.sleep(5 * 3 ** k)


def load_proof_file(path, data):
    """{evidence_id: (path:line, row)} and problems with the file's shape (header, widths, duplicate ids)."""
    out, problems = {}, []
    reader = csv.reader(io.StringIO(data.decode("utf-8", errors="replace")))
    header = next(reader, [])
    if tuple(header) != PROOF_COLS:
        return out, [f"{path}: header must be {','.join(PROOF_COLS)}"]
    for row in reader:
        at = f"{path}:{reader.line_num}"
        if len(row) != len(PROOF_COLS):
            problems.append(f"{at}: {len(row)} cells, the header has {len(PROOF_COLS)}")
            continue
        r = dict(zip(PROOF_COLS, (c.strip() for c in row)))
        if r["evidence_id"] in out:
            problems.append(f"{at}: second proof line for {r['evidence_id']}")
        out[r["evidence_id"]] = (at, r)
    return out, problems


def proof_problem(r, ev, archive_ref, read, builder, fetch=None):
    """"" when the proof line admits the row, else why not. With fetch, an archive capture is fetched and checked;
    a fetch failure returns a line starting "could not inspect"."""
    quote = quote_of(ev)
    if not quote:
        return "the row has no quote, so there is nothing to prove: it is a lead"
    if r["verdict"] != "VERIFIED":
        return f"verdict {r['verdict']!r}: only VERIFIED admits a row"
    rf = family_of_text(r["reader_family"])
    if not rf:
        return f"reader_family {r['reader_family']!r} names no known model family"
    if family_of_text(r["reader_model"]) != rf:
        return f"reader_model {r['reader_model']!r} is not a {rf} model"
    if rf == builder:
        return f"the reader ({rf}) is the builder's family; a different family must read the row"
    if len(r["tie"].split()) < 6:
        return "tie must be a sentence saying what in the capture ties the quote to this record"
    sha, off, n = r["capture_sha256"], r["quote_offset"], r["quote_length"]
    if not re.fullmatch(r"[0-9a-f]{64}", sha) or len(set(sha)) == 1:
        return "capture_sha256 must be 64 lowercase hex digits, not one repeated digit"
    if not (off.isdigit() and n.isdigit()):
        return "quote_offset and quote_length must be whole numbers"
    off, n = int(off), int(n)
    if n != len(quote):
        return f"quote_length {n} is not the quote's length ({len(quote)} characters, whitespace collapsed)"
    cap = r["capture"]
    if cap.startswith("http"):
        if not archive_ref:
            return "no data/archive_links.csv line for this row: an archive capture is admitted only through its index line"
        if cap != archive_ref:
            return "capture differs from the row's data/archive_links.csv archive_ref"
        if not ARCHIVE_RE.fullmatch(cap):  # the PR writes its own index line: only a Wayback capture is fetched
            return "capture must be a https://web.archive.org/web/<14 digits>/<url> capture"
        if fetch is None:
            return ""  # form only: --verify-proofs fetches the capture and checks the digest and the quote
        try:
            data = fetch(raw_capture_url(cap))
        except Exception as e:  # noqa: BLE001 - any failure to read the capture is an inspection failure
            return f"could not inspect {cap}: {e}"
    else:
        if archive_ref:
            return "the row has a data/archive_links.csv capture: prove it from that capture"
        if not cap.startswith("tasks/"):
            return "capture must be the row's archive ref or a repo path under tasks/"
        data = read(cap)
        if data is None:
            return f"capture file {cap} is not a regular file in the tree"
    if hashlib.sha256(data).hexdigest() != sha:
        return "capture_sha256 does not match the capture's bytes"
    if capture_text(data)[off:off + n] != quote:
        return "the row's quote is not at that offset in the capture's text"
    return ""


def check_proofs(results, evs, archive, read, fetch=None):
    """Problems with the per-row proof of every row the gate cannot decide (READ_REQUIRED or UNINSPECTABLE), one line
    each. A row is admitted only by its line in tasks/<the folder its created_by names>/BINDING_PROOF.csv; a proof file
    serves only its own folder's rows. evs: {evidence_id: row}; archive: {evidence_id: archive_ref};
    read(path) -> bytes or None; fetch(url) -> bytes, given only by --verify-proofs."""
    need = defaultdict(list)
    for r in results:
        if r["verdict"] not in ("PASS", "FAIL"):  # deny by default: anything undecided needs its proof
            need[label_folder(r["created_by"])].append(r["evidence_id"])
    problems, cache = [], {}

    def cached_fetch(url):
        if url not in cache:
            try:
                cache[url] = fetch(url)
            except Exception as e:  # noqa: BLE001
                cache[url] = e
        if isinstance(cache[url], Exception):
            raise cache[url]
        return cache[url]

    for folder, ids in sorted(need.items()):
        if not folder:
            problems.append(f"{len(ids)} rows whose created_by names no folder (one word, or harness + one word): "
                            f"they cannot be proved, e.g. {ids[0]}")
            continue
        path = f"tasks/{folder}/BINDING_PROOF.csv"
        data = read(path)
        if data is None:
            problems.append(f"{len(ids)} rows need a proof line and {path} is absent: each is a lead until proved, "
                            f"e.g. {ids[0]}")
            continue
        proofs, shape = load_proof_file(path, data)
        problems += shape
        builder = builder_family(read(f"tasks/{folder}/README.md"))
        if not builder:
            problems.append(f"tasks/{folder}/README.md has no 'Built by:' line naming one model family")
        for eid in ids:
            if eid not in proofs:
                problems.append(f"{eid}: no proof line in {path}")
                continue
            at, row = proofs[eid]
            why = proof_problem(row, evs[eid], archive.get(eid), read, builder, fetch and cached_fetch)
            if why:
                problems.append(f"{at}: {eid}: {why}")
    return problems


# ---------------------------------------------------------------- provenance

def isolation_prefix():
    """A no-network wrapper when this host has one; else [] (the caller says so)."""
    try:
        if subprocess.run(["unshare", "-rn", "true"], capture_output=True).returncode == 0:
            return ["unshare", "-rn"]
    except OSError:
        pass
    return []


def tree_git_dir(tree):
    """The git directory of a checkout, read from its .git entry without running git in it (its config is untrusted)."""
    g = tree / ".git"
    if g.is_file():
        m = re.match(r"gitdir:\s*(.+)", g.read_text(encoding="utf-8").strip())
        return str((tree / m[1]).resolve()) if m else ""
    return str(g) if g.is_dir() else ""


def run_folder_checks(folders, head, timeout=900, require_isolation=False):
    """Run tasks/<folder>/check.py for each folder, last, on a COPY of the gated tree; {folder: (exit code, last
    output line)} and the isolation obtained. The environment holds PATH, HOME (a temp dir), LANG and read access to
    the checkout's git history (GIT_DIR, with a throwaway index), and no token; no network only where `unshare -rn`
    works. require_isolation (--tree) refuses to run without it. This is the only code the gate executes from the
    tree it gates."""
    out = {}
    if not folders:
        return out, ""
    wrap = isolation_prefix()
    if require_isolation and not wrap:
        raise RuntimeError("no network isolation on this host (unshare -rn failed): --tree runs no check.py without it")
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / "tree"
        if head is None:
            shutil.copytree(TREE, copy, symlinks=True, ignore=shutil.ignore_patterns(".git"))
            gitdir = tree_git_dir(TREE)
        else:
            copy.mkdir()
            arch = subprocess.run(["git", "-C", str(ROOT), "archive", head], capture_output=True, check=True).stdout
            subprocess.run(["tar", "-x", "-C", str(copy)], input=arch, check=True)
            gitdir = git("rev-parse", "--absolute-git-dir").strip()
        env = {"PATH": f"{Path(sys.executable).parent}:/usr/bin:/bin", "HOME": tmp, "LANG": "C.UTF-8",
               "PYTHONDONTWRITEBYTECODE": "1", "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_NOSYSTEM": "1",
               "GIT_DIR": gitdir, "GIT_WORK_TREE": str(copy), "GIT_INDEX_FILE": str(Path(tmp) / "index")}
        for f in sorted(folders):
            try:
                r = subprocess.run(wrap + [sys.executable, f"tasks/{f}/check.py"], cwd=copy, env=env,
                                   capture_output=True, text=True, timeout=timeout)
                lines = (r.stdout + r.stderr).strip().splitlines()
                out[f] = (r.returncode, lines[-1] if lines else "")
            except subprocess.TimeoutExpired:
                out[f] = (124, f"timed out after {timeout} s")
    return out, "no network (unshare -rn)" if wrap else "network NOT isolated on this host: environment stripped only"


def provenance_problems(new_evs, base_labels, base_has_folder, head_check_bytes, run=run_folder_checks, head=None):
    """Problems with the provenance of the rows a PR adds or changes, one line per created_by label (ruling E):
    the label names exactly one folder; that folder holds a non-empty check.py; a label new to the base adds its folder
    in this PR; and every folder whose label adds rows has its check.py executed, which must exit 0."""
    labels = Counter(e["created_by"].strip() for e in new_evs)
    problems, to_run = [], {}
    for label, n in sorted(labels.items()):
        folder = label_folder(label)
        if not folder:
            problems.append(f"created_by '{label}' ({n} rows) names no folder: use one word, or a harness word and "
                            f"one folder word")
        elif not head_check_bytes(folder):
            problems.append(f"MISSING tasks/{folder}/check.py for created_by '{label}' ({n} rows): it must exist "
                            f"and not be empty")
        elif label not in base_labels and base_has_folder(folder):
            problems.append(f"created_by '{label}' is new, but tasks/{folder}/ already exists on the base: a new "
                            f"label adds its own folder in this PR")
        else:
            to_run[folder] = label
    results, isolation = run(set(to_run), head) if to_run else ({}, "")
    for folder, (code, last) in sorted(results.items()):
        if code != 0:
            problems.append(f"tasks/{folder}/check.py exited {code} for created_by '{to_run[folder]}': {last}")
    return problems, isolation


def audit_sample(results, n, seed):
    """Audit of the gate, never admission: N PASS rows per created_by label, chosen by sha256(seed:evidence_id), for a
    reviewer to read; the share found unbound estimates the gate's escape rate."""
    by_label = defaultdict(list)
    for r in results:
        if r["verdict"] == "PASS":
            by_label[r["created_by"].strip()].append(r)
    return {k: sorted(v, key=lambda r: hashlib.sha256(f"{seed}:{r['evidence_id']}".encode()).hexdigest())[:n]
            for k, v in sorted(by_label.items())}


def resolve_base(ref, head):
    if TREE != ROOT:  # a plain directory has no history: compare with REF itself (check out the PR merge ref)
        return git("rev-parse", ref).strip()
    return git("merge-base", ref, head or "HEAD").strip()


def main(argv=None):
    global TREE
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true", help="report every evidence row by verdict, created_by and source")
    g.add_argument("--new-since", metavar="REF", help="gate rows added or changed since the merge-base with REF")
    g.add_argument("--verify-proofs", metavar="REF", help="as --new-since, and fetch every archive capture a proof cites")
    g.add_argument("--provenance-since", metavar="REF", help="require and run tasks/<folder>/check.py for new rows")
    g.add_argument("--sample", metavar="N", type=int, help="audit only: list N PASS rows per created_by label to read")
    ap.add_argument("--seed", default="1", help="--sample seed")
    ap.add_argument("--since", metavar="REF", help="--sample: only rows added or changed since REF")
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--head", help="git ref to read instead of the working tree")
    src.add_argument("--tree", metavar="DIR", help="read data/ and tasks/ from DIR (an authoritative run: this "
                                                   "script and its rules come from the trusted checkout)")
    ap.add_argument("--out", help="write per-row verdicts to this CSV")
    a = ap.parse_args(argv)
    TREE = Path(a.tree).resolve() if a.tree else ROOT
    gate = a.new_since or a.verify_proofs
    try:
        head_evs = rows(a.head, "evidence_*.csv")
        since = gate or a.provenance_since or (a.since if a.sample else None)
        base = resolve_base(since, a.head) if since else None
        base_evs = rows(base, "evidence_*.csv") if base else []
    except subprocess.CalledProcessError as e:
        print(f"binding gate: cannot read git state ({(e.stderr or '').strip()}); failing closed")
        return 2
    if not head_evs:
        print("binding gate: zero evidence rows read; failing closed")
        return 2
    if len({e["evidence_id"] for e in head_evs}) != len(head_evs):
        print("binding gate: duplicate evidence_id on the head tree; failing closed")
        return 2
    evs = head_evs if base is None else changed_rows(base_evs, head_evs)

    if a.provenance_since:
        base_paths = set(git("ls-tree", "-r", "--name-only", base, "tasks/").split())

        def head_check(f):
            return bool((tasks_file(a.head, f"tasks/{f}/check.py") or b"").strip())
        try:
            problems, isolation = provenance_problems(
                evs, {e["created_by"].strip() for e in base_evs},
                lambda f: any(x.startswith(f"tasks/{f}/") for x in base_paths), head_check, head=a.head,
                run=lambda folders, head: run_folder_checks(folders, head, require_isolation=bool(a.tree)))
        except RuntimeError as e:
            print(f"provenance: {e}; failing closed")
            return 2
        print(f"provenance: {len(evs)} evidence rows added or changed since {base[:10]} under "
              f"{len({e['created_by'].strip() for e in evs})} created_by label(s)" +
              (f"; folder checks ran with {isolation}" if isolation else ""))
        for line in problems:
            print("  " + line)
        return 1 if problems else 0

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
    n_open = sum(r["verdict"] not in ("PASS", "FAIL") for r in results)
    archive = {r["evidence_id"]: r["archive_ref"] for r in rows(a.head, "archive_links.csv")}
    problems = check_proofs(results, {e["evidence_id"]: e for e in evs}, archive,
                            lambda path: tasks_file(a.head, path), fetch_url if a.verify_proofs else None)
    uninspected = [x for x in problems if "could not inspect" in x]
    print(f"\nbinding gate: {len(results)} rows added or changed since {base[:10]}; "
          f"{len(results) - len(fails) - n_open} PASS, {len(fails)} FAIL (blocking, no waiver), {n_open} "
          f"READ_REQUIRED or UNINSPECTABLE (each admitted only by its own proof line)" +
          ("" if a.verify_proofs else "; archive captures checked for form only (--verify-proofs fetches them)"))
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
    if uninspected:
        print(f"{len(uninspected)} captures could not be fetched: an inspection failure, never a pass; re-run")
        return 2
    return 1 if fails or problems else 0


if __name__ == "__main__":
    sys.exit(main())
