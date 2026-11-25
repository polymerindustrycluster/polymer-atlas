#!/usr/bin/env python3
"""Evidence binding gate: is an evidence row's quote about the record it is filed on?

validate.py checks an evidence row's form, never whether its quote witnesses that record. On 2026-11-22 two join
batches (about 34,000 rows) passed every check while a first-cut test found 28% did not bind: the quote named another
operator, another street, or claimed a headquarters from a plant permit (tasks/evidence-binding-gate-2026-11-22/).

Owner ruling 2026-11-22, "strict floor, then merge": the gate is a FLOOR, not proof. PASS means every mechanical leg
matched; admitting a data PR still needs two model families reading rows.

Every evidence row gets exactly one verdict:
  PASS            a web quote with a replayed proof, or a structured quote with EVERY leg matched positively and
                  nothing left unexplained. Name: the whole quoted operator field (never a comma part, nothing in parentheses
                  dropped) is a name the record holds, or a held name plus corporate-form words only on a site row
                  whose street passes; not a recorded parent's name, nor a key shared with one unless the text is the
                  record's own; a site-name part made only of generic labels (matching.generic_label, either part of a
                  parenthetical city included) is not a name. Site rows also need: street, matching.same_street;
                  designators, matching.designators_compare "equal" (any suite, unit, room, floor or building on either
                  side stated and equal on both); locality, every comma part after the street read as city, state or
                  ZIP and matching.same_locality true (state on both sides and equal; city equal, either part of a
                  parenthetical city, or ZIP5 equal); and the same quote not passing on another site record.
                  Organization `address` rows: the source states the entity's own address and the quoted city and state
                  are the record's HQ.
  FAIL            a demonstrated conflict: name_not_held, parent_name_lead (the filing names only a recorded parent: a
                  lead to be read), street_differs, unit_differs, record_no_street, quote_no_street, state_differs,
                  city_differs, hq_city_state_differs, hq_from_facility_or_permit, hq_from_s5_identity_source (SCHEMA
                  §4.8 S-5); web quotes: street_absent_from_quote (no civic number directly followed by the record's
                  street word), unit_differs (every occurrence states another suite), not_own_site (an own_site URL off
                  the record's website; on a platform host, host and path must both match).
  HELD            a structured row with no demonstrated conflict where a leg did not match positively:
                  held_for_reading:<legs> (name_with_parenthetical, name_equals_parent_key, address_with_parenthetical,
                  designator_not_on_both_sides, street_suffix_unexplained, locality_not_read, locality_not_matched, passes_on_two_records).
                  Web proofs are HELD for records absent from the base or observations outside the merge commit date window.
  READ_REQUIRED   a web quote awaiting a valid, replayed per-row proof in tasks/<folder>/BINDING_PROOF.csv.
                  Programs and ecosystem records use their own names and published city/state where an address is quoted.
                  For program and office web proofs the source must match the record's own page.
  UNINSPECTABLE   no_quote, other_table, record_not_found, unknown_source_family, parse_failed, operator_not_a_name,
                  no_civic_number. No admission path here either.
Every verdict other than PASS fails the PR; FAIL, HELD and the rest differ only for the reader's queue.

Strict reading (owner questions, measured in the name_alt column, never passing): a name found only in the record's
notes, a permit's facility label, a quoted name that merely starts with a held name, one comma part of an operator
field. A recorded parent's name never binds, on any path (DECISIONS.md, 2026-11-22).

Usage:
  python3 scripts/check_evidence_binding.py --all [--head REF | --tree DIR] [--out verdicts.csv]
  python3 scripts/check_evidence_binding.py --new-since origin/main [--tree DIR]   # PR gate: rows added or changed
  python3 scripts/check_evidence_binding.py --verify-proofs origin/main [--tree DIR --pr-head SHA]  # same gate with capture replay
  python3 scripts/check_evidence_binding.py --provenance-since origin/main [--tree DIR]  # tasks/<folder>/check.py exists
  python3 scripts/check_evidence_binding.py --sample 20 --seed 7 [--since origin/main]  # audit only, admits nothing
--new-since and --verify-proofs both replay captures and exit 1 on any non-PASS. Exit 2 = could not check.
--all and --sample report the mechanical verdicts without fetching captures.

--tree DIR reads data/ and tasks/ from DIR, an untrusted checkout of the PR; the rules and this code come from the
trusted checkout that runs it. Web proof replay uses the GitHub merge commit in the checkout and checks its
second parent against --pr-head when a pinned PR head is supplied.
Nothing from DIR is executed: --provenance-since checks that check.py is present; the
replay it performs is run by the lane and by the reviewing family.
"""
import argparse
import contextlib
import csv
import gzip
import hashlib
import http.client
import io
import ipaddress
import json
import re
import socket
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
TREE = ROOT  # where data/ and tasks/ are read when no git ref is given; --tree moves it, ROOT stays the trusted code
sys.path.insert(0, str(ROOT / "scripts"))
from atlas import (LOCALITY_SEP_RE, PLATFORM_HOSTS, SUFFIX, name_key, org_name_fields,  # noqa: E402
                   site_name_key, squash, street_key, tokens_semicolon)
from build_echo_spine import STATE_NAMES  # noqa: E402
from site_corpus import linkedin_url  # noqa: E402
from matching import (DESIGNATOR_ONLY_RE, city_differs, corporate_form_extension, designators_compare,  # noqa: E402
                      generic_label, has_civic_number, route_street_key, same_locality, same_street, units)  # (PR #463)

csv.field_size_limit(10**9)
ARCHIVE_RE = re.compile(r"https://web\.archive\.org/web/([0-9]{14})(id_)?/(https?://[^\s]+)")
PROOF_COLS = ("evidence_id", "record_id", "claim_sha256", "capture", "capture_date", "capture_sha256", "quote_offset",
              "verdict", "reader_family", "reader_date")
MAX_CAPTURE_BYTES = 8 * 1024 * 1024

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

def git(*args, worktree=None):
    cmd = ["git", "-C", str(worktree or ROOT)]
    if worktree is not None:
        cmd.append("--git-dir=.git")
    return subprocess.run([*cmd, *args], capture_output=True, text=True, check=True).stdout


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


def record_names(rec):
    if "program_id" in rec:
        return [rec.get("program_name") or ""]
    names = [v for _, v in org_name_fields(rec)] if "trade_names" in rec else [rec.get("legal_name") or ""]
    if rec.get("record_grain") == "office" and rec.get("office_name"):
        names.append(rec["office_name"])
    return names


PROGRAM_ECOSYSTEM_TABLES = {"ecosystem", "programs"}
PROGRAM_ECOSYSTEM_CLAIMS = {"existence", "scope", "address"}


class Index:
    """Index records by their declared table, with a shared organization index for foreign keys."""

    def __init__(self, sites, orgs, ecosystem=(), programs=(), links=()):
        self.sites = {s["site_id"]: s for s in sites}
        self.tables = {"sites": self.sites, "organizations": {o["org_id"]: o for o in orgs},
                       "ecosystem": {o["org_id"]: o for o in ecosystem},
                       "programs": {p["program_id"]: p for p in programs}}
        self.orgs = self.tables["organizations"] | self.tables["ecosystem"]
        self._notes = {}
        self.sec_ciks = defaultdict(set)
        for link in links:
            if link["registry"] == "SEC_CIK" and not link.get("site_id"):
                self.sec_ciks[link["org_id"]].add(link["registry_id"])

    @classmethod
    def load(cls, ref=None):
        return cls(rows(ref, "sites_*.csv"), rows(ref, "organizations_*.csv"),
                   rows(ref, "ecosystem.csv"), rows(ref, "programs.csv"), rows(ref, "registry_links.csv"))

    def record(self, table, rid):
        return self.tables.get(table, {}).get(rid)

    def org_keys(self, oid):
        return {k for v in record_names(self.orgs.get(oid, {}))
                for k in (name_key(v), name_key(PAREN_RE.sub(" ", v))) if k}

    def held_keys(self, table, rid):
        """name_keys of every name the record itself holds (strict reading: no parent, no notes, no generic site label)."""
        if table in PROGRAM_ECOSYSTEM_TABLES:
            return {k for v in record_names(self.record(table, rid)) for k in
                    (name_key(v), name_key(PAREN_RE.sub(" ", v))) if k}
        if table == "organizations":
            return self.org_keys(rid)
        s = self.sites[rid]
        # A site-name part made only of generic labels ("Plant 2", "North Warehouse", the site's city) is not a name;
        # a brand, division or trading name is (owner ruling 2026-11-22, "drop generic labels only"; Codex r2 finding 3).
        return ({k for k in self.site_keys(rid) if not generic_label(k, s.get("city") or "", s.get("county") or "")}
                | self.org_keys(s.get("org_id")))

    def site_keys(self, rid):
        """Every key a site name yields: the whole name, the name less its trailing locality, each " - " part that is not
        the city."""
        s = self.sites[rid]
        name, city = s.get("site_name") or "", squash(s.get("city"))
        keys = {name_key(name), site_name_key(name, s.get("city") or "")}
        for part in LOCALITY_SEP_RE.split(PAREN_RE.sub(" ", name)):
            if squash(part) and not (city and squash(part).startswith(city)):
                keys.add(name_key(part))
        return {k for k in keys if k}

    def parent_names(self, table, rid):
        """Every recorded parent and ultimate-parent name up the chain, as written. An ultimate_parent_name written
        exactly as one of the organization's own names is a self-reference, not a parent (43 organizations at 17834918
        give their own name; 29 in identical text)."""
        o = self.orgs.get(self.sites[rid].get("org_id")) if table == "sites" else self.orgs.get(rid)
        names, seen = set(), set()
        if table in PROGRAM_ECOSYSTEM_TABLES:
            rec = self.record(table, rid)
            institution = rec.get("institution_org_id") or rec.get("parent_institution_org_id")
            if institution and institution != rid:
                parent = self.orgs.get(institution, {})
                names.update(record_names(parent))
                if table == "programs":
                    o = parent or None
        while o and o["org_id"] not in seen:
            seen.add(o["org_id"])
            up = (o.get("ultimate_parent_name") or "").strip()
            if up and squash(up) not in self.own_texts(o["org_id"]):
                names.add(up)
            o = self.orgs.get(o.get("parent_org_id") or "")
            if o:
                names.update(record_names(o))
        return {n for n in names if n}

    def parent_keys(self, table, rid):
        return {k for n in self.parent_names(table, rid) for k in (name_key(n), name_key(PAREN_RE.sub(" ", n))) if k}

    def own_texts(self, oid):
        """An organization's own names as written (squash only, corporate-form words kept)."""
        return {squash(v) for v in record_names(self.orgs.get(oid, {})) if squash(v)}

    def street_sites(self, key):
        """site_ids whose street_key is key (for the two-records rule)."""
        if not hasattr(self, "_by_street"):
            self._by_street = defaultdict(set)
            for sid, s in self.sites.items():
                self._by_street[route_street_key(street_key(s.get("street_address")))].add(sid)
        return self._by_street.get(route_street_key(key), set())

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
        a = [x.strip() for x in re.split(r";(?![^()]*\))", q)]  # "(ABC; FORMERLY ...)" is not a field break
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
    """The street comma-part of a quoted "STREET, CITY, ST ZIP" with any designator-only parts beside it ("Suite 5, 1 Elm
    St", "1 Elm St, Ste. 5", "1 Elm St, Building B"), street first: what matching.same_street compares, so the gate and
    the derivation agree and a stated suite or building reaches the designator test (Codex r2 finding 2)."""
    parts = (addr or "").split(",")
    lead = []
    while len(parts) > 1 and designator_part(parts[0]):
        lead.append(parts.pop(0))
    trail = []
    for x in parts[1:]:
        if not designator_part(x):
            break
        trail.append(x)
    return ",".join(parts[:1] + lead + trail)


def designator_part(x):
    """A comma part that is only a suite, unit, floor or building, and not a state: "FL 33101" is Florida, not a floor."""
    m = re.fullmatch(r"\s*([A-Za-z]{2})\.?\s*(\d[\dE-]{3,9})?\s*", x)
    return bool(DESIGNATOR_ONLY_RE.match(x)) and not (m and state_code(m[1]))


ZIP_TAIL_RE = re.compile(r"(?:^|\s+)(\d{5}[-\s]\d{4}|\d{5}-?|\d{9}|\d{4}|\d[\dE]{2,8})$")  # ZIP, ZIP+4, "317E6"


def city_is_plain(city):
    """False when a quoted city holds a digit (a ZIP), a trailing state ("DAYTON TX"), or is itself a two-letter state
    code: a second state or ZIP inside the locality is unexplained and is never completed from the tail (Codex r4)."""
    cw = city.split()
    return not (re.search(r"\d", city) or any(state_code(" ".join(cw[k:])) for k in range(1, len(cw)))
                or (len(cw) == 1 and len(city) == 2 and state_code(city)))


def quoted_place(addr):
    """(city, state code, ZIP as printed, complete) for the locality a quoted address states after its street: "STREET,
    CITY, ST ZIP", "STREET, CITY, ST", "STREET, CITY ST ZIP", "STREET, CITY, State", "STREET, CITY, ST ZIP 1234",
    "STREET, CITY, State -" (an empty ZIP). A lone trailing word part with no state is the city ("1 Elm St, Dover").
    complete is True only when every comma part after the street was read as city, state or ZIP: anything left over is
    unexplained, and the gate does not PASS it (owner ruling 2026-11-22, "strict floor"; Codex r3 finding 1)."""
    parts = [x.strip() for x in (addr or "").split(",")]
    rest = [x for x in parts[len(street_part(addr).split(",")):] if x and x != "-"]
    if not rest:
        return "", "", "", False
    last = re.sub(r"\s+-$", "", rest[-1]).strip()
    m = ZIP_TAIL_RE.search(last)
    z = m[1] if m else ""
    if m and not last[:m.start()].strip() and len(rest) > 1:  # the ZIP is its own comma part: "Dover, OH, 44699"
        rest, last = rest[:-1], rest[-2]
    elif m:
        last = last[:m.start()].strip()
    st = state_code(last)
    if st:
        used, city = 1, rest[-2] if len(rest) > 1 else ""
        used += bool(city)
        if len(rest) > 2 and re.fullmatch(r"(?i)(?:city|town|township|borough|village) of", city):
            city, used = rest[-3], 3  # ECHO prints "SPRINGFIELD, TOWNSHIP OF, OH"
        # "Dayton TX 75001, OH 44699": a second state or ZIP inside the final city is unexplained (Codex r4, r5)
        return city, st, z, used == len(rest) and city_is_plain(city)
    words = last.split()
    for k in range(1, len(words)):  # "DOVER OH 44101" or "DOVER OHIO" in one comma part
        if state_code(" ".join(words[k:])):
            c = " ".join(words[:k])
            return c, state_code(" ".join(words[k:])), z, len(rest) == 1 and city_is_plain(c)
    if len(rest) == 1 and not z and not re.search(r"\d", last):
        return last, "", "", True
    return "", "", z, False


def state_code(s):
    s = (s or "").strip().rstrip(".")
    if len(s) == 2:
        return s.upper() if s.upper() in STATE_NAMES.values() else ""
    return STATE_NAMES.get(s.title(), "")


def street_suffix_unexplained(rec_street):
    """True when the record's street line carries a comma part beyond the street and its designators ("321 Oak St,
    Basement Level"): street_key drops it, so a quote naming only the street may name the building while the record
    names a floor or wing. Never PASS (Codex r4, owner floor ruling); a quote repeating it is held by the locality leg."""
    return len([x for x in (rec_street or "").split(",") if x.strip()]) > len(street_part(rec_street).split(","))


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
    """name_keys of each quoted name as a whole: an operator field is one name, never split on commas, and nothing in it
    is dropped: "Acme Polymer (operated by Quill Resins)" is not "Acme Polymer" (owner ruling 2026-11-22, "strict
    floor"; Codex r3 finding 6)."""
    return {k for n in names for k in (name_key(n),) if k}


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


def record_locality(rec, addr):
    """Check a quoted address against the city and state a program or ecosystem record holds."""
    city, state = rec.get("city"), state_code(rec.get("state"))
    q_city, q_state, _, complete = quoted_place(addr)
    if complete:
        if (state and q_state and state != q_state) or city_differs(city, "", q_city, ""):
            return "FAIL", "locality_differs"
        if same_locality(city, state, "", q_city, q_state, ""):
            return "", ""
    return "UNINSPECTABLE", "locality_not_matched"


# Reviewed postal aliases, scoped to the exact state, county and ZIP.
POSTAL_CITIES = {
    ("OH", "cuyahoga", "44125"): {"cleveland", "garfield heights", "valley view"},
    ("OH", "cuyahoga", "44117"): {"cleveland", "euclid"},
}
PRESS_HOSTS = {"rubberworld.com", "www.rubberworld.com", "houlihancapital.com", "www.houlihancapital.com"}
ITA_2021 = "OSHA ITA CY2021 "
ITA_COMPANY_WIDTH = 43  # CY2021 raw public CSV; adjacent years use different widths.


def registry_name(name):
    return name_key(name.replace("+", " and "))


def registry_place(rec, addr, county):
    """Return the qualifying place rule, or an empty string for an incomplete or conflicting place."""
    city, state, zip_code, complete = quoted_place(addr)
    actual = squash(rec.get("city"))
    expected_zip = (rec.get("zip") or "").strip()
    if not (complete and actual and city and state == rec.get("state") and zip_code == expected_zip
            and re.fullmatch(r"\d{5}(?:-\d{4})?", zip_code) and county and county == squash(rec.get("county"))):
        return ""
    street = rec.get("street_address") or ""
    if not street.strip():
        return "blank_street_registry" if actual == squash(city) else ""
    if (PAREN_RE.search(addr) or street_suffix_unexplained(street) or street_reason(street, addr)
            or designators_compare(street, street_part(addr)) != "equal"):
        return ""
    if actual == squash(city):
        return "registry_street"
    aliases = POSTAL_CITIES.get((state, county, zip_code), set())
    return "mailing_city" if "cleveland" in (actual, squash(city)) and {actual, squash(city)} <= aliases else ""


def route_registry(ev, idx, rec, fam, quote):
    """County-bearing registry witness or explicitly quoted 2021 ITA company and establishment fields."""
    src, table, rid, claim = (ev[k] for k in ("source_ref", "record_table", "record_id", "claim_type"))
    fields = labelled_fields(quote)
    ita = src.startswith(ITA_2021) and quote.startswith("company_name:")
    if ita:
        columns = {"company_name", "establishment_name", "address"}
    elif (table == "sites" and (fam[1] in ("echo", "osha") or fam[2] == ("permittee",))
          and quote.startswith("facility_name:")):
        columns = {"facility_name", "address", "county"}
    else:
        return None
    if (ev["source_class"] not in ("registry", "government_filing") or claim not in ("address", "existence")
            or not fields or set(fields) != columns or len(LABEL_RE.findall(quote)) != len(columns)):
        return "HELD", "registry_fields_or_claim", {}
    addr, county = fields["address"], squash(fields.get("county"))
    org_id = rec.get("org_id") if table == "sites" else rid
    operator = idx.orgs.get(org_id, {})
    if ita:
        if table not in ("organizations", "sites") or (table == "organizations" and claim != "existence"):
            return "HELD", "ita_company_claim", {}
        company = fields["company_name"]
        if len(company) != ITA_COMPANY_WIDTH or not squash(company):
            return "HELD", "ita_company_width", {}
        # A prefix is insufficient by itself: require a unique held organization and a held physical establishment.
        prefix = squash(company)
        matches = {oid for oid, org in idx.tables["organizations"].items() if any(
            len(squash(n)) > len(prefix) and squash(n).startswith(prefix)
            for n in record_names(org))}
        sites = [idx.sites[sid] for sid in idx.street_sites(quote_street(addr))
                 if idx.sites[sid].get("org_id") == org_id]
        bound = [site for site in sites if registry_place(site, addr, squash(site.get("county"))) == "registry_street"]
        estab = registry_name(fields["establishment_name"])
        if (matches == {org_id} and len(bound) == 1 and estab
                and not ({registry_name(n) for n in idx.parent_names(table, rid)}
                         & {registry_name(company), estab})
                and (bound[0]["site_id"] == rid if table == "sites" else
                     (squash(bound[0]["city"]) == squash(operator.get("hq_city"))
                      and bound[0]["state"] == operator.get("hq_state")))):
            return "PASS", "ita_cy2021_unique_prefix_and_establishment", {}
        return "HELD", "ita_company_or_establishment_not_bound", {}
    key = registry_name(fields["facility_name"])
    site_label = LOCALITY_SEP_RE.split(rec.get("site_name") or "", maxsplit=1)[0]
    held = {registry_name(n) for n in [*record_names(operator), site_label]}
    parents = {registry_name(n) for n in idx.parent_names(table, rid)}
    place = registry_place(rec, addr, county)
    if not key or key not in held or key in parents or generic_label(key, rec.get("city") or "", county):
        return "FAIL", "registry_operator_not_held", {}
    if not place:
        return "FAIL", "registry_place_not_bound", {}
    if place == "blank_street_registry" and claim == "address" and not ev["claim_detail"].startswith("place only; quote:"):
        return "HELD", "blank_street_requires_place_only_claim", {}
    held_keys = idx.held_keys(table, rid)
    basis = [] if name_keys([fields["facility_name"]]) & held_keys else ["registry_variant"]
    return "PASS", "+".join([*basis, place]), {}


def judge(ev, idx, _alone=False):
    """(verdict, reason, detail dict) for one evidence row. _alone skips the two-records rule (used by that rule)."""
    table, rid, detail, src = ev["record_table"], ev["record_id"], ev["claim_detail"], ev["source_ref"]
    if table not in idx.tables:
        return "UNINSPECTABLE", "other_table", {}
    rec = idx.record(table, rid)
    if rec is None:
        return "UNINSPECTABLE", "record_not_found", {}
    if ev["source_class"] == "linkedin_company":
        return judge_linkedin(ev, table, claim_detail=detail, src=src)
    if src.split(" ", 1)[0] in MAP_PROVIDERS:
        return "HELD", "map_listing_needs_base", {}
    if detail.startswith("trade_names +"):
        return "HELD", "filing_variant_needs_base", {}
    i = detail.find("quote:")
    if i < 0 or not detail[i + 6:].strip():
        return "UNINSPECTABLE", "no_quote", {}
    if src.startswith("http") or (ev["source_class"] == "government_filing" and edgar_ref(src)):
        return judge_web(ev, rec, idx, detail[i + 6:].strip())
    claim = ev["claim_type"]
    if table in PROGRAM_ECOSYSTEM_TABLES and claim not in PROGRAM_ECOSYSTEM_CLAIMS:
        return "UNINSPECTABLE", "claim_untested", {}
    fam = family_of(src)
    if fam is None:
        return "UNINSPECTABLE", "unknown_source_family", {}
    quote = detail[i + 6:].strip()
    route = route_registry(ev, idx, rec, fam, quote)
    if route is not None:
        if route[0] == "PASS" and table == "sites" and not _alone:
            addr = labelled_fields(quote)["address"]
            candidates = idx.street_sites(quote_street(addr)) | idx.street_sites("")
            if any(judge(dict(ev, record_id=sid), idx, _alone=True)[0] == "PASS"
                   for sid in candidates - {rid}):
                return "HELD", "held_for_reading:passes_on_two_records", {}
        return route
    p = parse_quote(quote, fam)
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
    own_org = rec.get("org_id") if table == "sites" else rid
    if table in PROGRAM_ECOSYSTEM_TABLES:
        own, own_texts = held, {squash(v) for v in record_names(rec) if squash(v)}
    else:
        own, own_texts = idx.org_keys(own_org), idx.own_texts(own_org)
    parents = idx.parent_keys(table, rid)
    parent_texts = {squash(n) for n in idx.parent_names(table, rid)}
    qtexts = {squash(n) for n in p["names"]}
    stripped = {k for n in p["names"] for k in (name_key(PAREN_RE.sub(" ", n)),) if k}  # for the parent rule only
    reasons, holds, info = [], [], {}  # reasons: demonstrated conflicts (FAIL); holds: a leg that did not match (HELD)

    def is_parent(q):
        return q in parents or any(corporate_form_extension(k, q) for k in parents)
    on_parent = [q for q in qkeys if is_parent(q)]
    if any(is_parent(q) for q in qkeys | stripped) and not (qkeys | stripped) & own:
        # A filing naming only a recorded parent (or parent + corporate-form words) never binds by machine, on any path,
        # even when the parent's name is part of the site name: a lead to be read (owner ruling 2026-11-22, "fail
        # everywhere"; Codex r2 finding 4).
        reasons.append("parent_name_lead")
    elif on_parent and not qtexts & own_texts - parent_texts:
        # The key is both the record's and a recorded parent's, and the text is not the record's own alone ("Acme Polymer
        # Inc" for subsidiary "Acme Polymer LLC"): never PASS (Codex r3 finding 5), but no demonstrated conflict either,
        # because most such parents are the organization itself spelled another way ("... Co" against "... Company").
        holds.append("name_equals_parent_key")
    elif not qkeys & held and table == "sites" and not street_reason(rec.get("street_address"), p["addr"]) and any(
            corporate_form_extension(h, q) for h in held for q in qkeys):
        info["name_basis"] = "corporate_form"  # owner ruling 2026-11-22: held name + corporate-form words, street passes
    elif not qkeys & held:
        if any(PAREN_RE.search(n) for n in p["names"]) and (stripped & held or table == "sites" and any(
                corporate_form_extension(h, q) for h in held for q in stripped)):
            holds.append("name_with_parenthetical")  # held only once text in parentheses is dropped (Codex r3 finding 6)
        else:
            reasons.append("name_not_held")
            alts = name_alternatives(idx, table, rid, qkeys, alt_keys, held)
            if comma_part_keys(p["names"]) & held:
                alts.append("comma_part")  # "ACME, ACME CO": one comma part is a held name (an owner question, never PASS)
            info["name_alt"] = ";".join(alts)
    else:  # measured: which held name matched (audits the false-PASS side)
        lead = name_key(LOCALITY_SEP_RE.split(PAREN_RE.sub(" ", rec.get("site_name") or ""))[0])
        info["name_basis"] = "org" if qkeys & own else "site_name_lead" if lead in qkeys else "site_name_other"
    if table == "sites":
        if PAREN_RE.search(p["addr"]):  # judged without the parenthetical, and never PASS with it unexplained
            holds.append("address_with_parenthetical")
            p = dict(p, addr=re.sub(r"\s+", " ", PAREN_RE.sub(" ", p["addr"])).strip())
            rec = dict(rec, street_address=re.sub(r"\s+", " ", PAREN_RE.sub(" ", rec.get("street_address") or "")).strip())
        why = street_reason(rec.get("street_address"), p["addr"])
        q_city, q_st, q_zip, complete = quoted_place(p["addr"])
        if q_st and rec.get("state") and q_st != rec["state"].strip().upper():
            reasons.append("state_differs")  # an explicit other state is contrary evidence (Codex review, PR #467)
        if city_differs(rec.get("city"), rec.get("zip"), q_city, q_zip):
            reasons.append("city_differs")  # an explicit other city and ZIP too (controller rulings 2026-11-22, Codex r2 finding 2)
        if why == "no_civic_number" and not reasons:
            return "UNINSPECTABLE", why, info
        if why and why != "no_civic_number":
            reasons.append(why)
        if why == "street_differs":
            info["street_limit"] = street_limit(street_key(rec.get("street_address")), quote_street(p["addr"]))
        # Owner ruling 2026-11-22, "strict floor, then merge": PASS only when every leg matches positively.
        units_seen = designators_compare(rec.get("street_address"), street_part(p["addr"]))
        if units_seen == "conflict" and "unit_differs" not in reasons:
            reasons.append("unit_differs")  # one designator kind on both sides with different values (Codex r3 finding 3)
        elif units_seen == "unequal":
            holds.append("designator_not_on_both_sides")
        if street_suffix_unexplained(rec.get("street_address")):
            holds.append("street_suffix_unexplained")
        if not complete:
            holds.append("locality_not_read")  # no locality, or comma parts the parser could not read (finding 1)
        elif not same_locality(rec.get("city"), rec.get("state"), rec.get("zip"), q_city, q_st, q_zip):
            holds.append("locality_not_matched")  # state missing, or neither the city nor the ZIP5 matches (finding 1)
    elif table in PROGRAM_ECOSYSTEM_TABLES:
        if claim == "address" and fam[4] != "entity":
            reasons.append("address_not_from_entity_source")
        if p["addr"] or claim == "address":
            verdict, reason = record_locality(rec, p["addr"])
            if verdict == "FAIL":
                reasons.append(reason)
            elif verdict and not reasons:
                return verdict, reason, info
    elif claim == "address":
        basis = fam[4]
        info["hq_basis"] = basis
        if basis == "facility":
            reasons.append("hq_from_facility_or_permit")
        elif basis == "s5":
            reasons.append("hq_from_s5_identity_source")
        if not hq_in_quote(p["addr"], rec):
            reasons.append("hq_city_state_differs")
    if reasons:
        return "FAIL", "+".join(reasons), info
    if holds:
        return "HELD", "held_for_reading:" + "+".join(holds), info
    if table == "sites" and not _alone:
        # Two records: the same quote passing on another site record passes on neither (Codex r3 finding 2).
        others = sorted(sid for sid in idx.street_sites(quote_street(p["addr"])) - {rid}
                        if judge(dict(ev, record_id=sid), idx, _alone=True)[0] == "PASS")
        if others:
            info["also_passes_on"] = ";".join(others)
            return "HELD", "held_for_reading:passes_on_two_records", info
    return "PASS", "", info


# Shared hosting where one host carries many unrelated tenants: the record's own site there is its host AND path.
# shortcut: a fixed list can never be complete; add shared hosts as they are identified.
PLATFORMS = set(PLATFORM_HOSTS) | {
    "pages.dev", "netlify.app", "vercel.app", "herokuapp.com", "blogspot.com", "myshopify.com", "webflow.io",
    "carrd.co", "wix.com", "editorx.io", "azurewebsites.net", "cloudfront.net", "amazonaws.com", "firebaseapp.com",
    "web.app", "glitch.me", "000webhostapp.com", "jimdosite.com", "site123.me", "strikingly.com", "mystrikingly.com",
    "tumblr.com", "medium.com", "substack.com", "hs-sites.com", "ueniweb.com", "wpengine.com", "wpcomstaging.com"}
WEB_UNIT_RE = re.compile(r"^(?:suite|ste|unit|apt|apartment|room|rm)$")


def host_path(url, *, preserve_path=False):
    """(host, path) of a URL or bare domain, with optional case preservation for proof paths."""
    s = re.sub(r"^[a-z][a-z0-9+.-]*://", "", (url or "").strip(), flags=re.I)
    if not preserve_path:
        s = s.lower()
    host, _, path = s.partition("/")
    host = re.sub(r":\d+$", "", host.rsplit("@", 1)[-1]).lower().rstrip(".")
    host = host[4:] if host.startswith("www.") else host
    return host, path.split("?")[0].split("#")[0].strip("/")


def on_platform(host):
    return any(host == h or host.endswith("." + h) for h in PLATFORMS)


def record_website(idx, table, rec):
    """A site's website is held on its organization."""
    if table == "programs":
        return rec.get("url") or ""
    if table == "ecosystem" and rec.get("record_grain") == "office":
        return rec.get("tto_url") or ""
    org = idx.orgs.get(rec.get("org_id")) if table == "sites" else rec
    return (org or {}).get("website") or ""


def record_websites(idx, table, rec, *, preserve_path=False):
    """Held website host/path pairs."""
    hps = (host_path(w, preserve_path=preserve_path)
           for w in re.split(r"[;,\s]+", record_website(idx, table, rec)))
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


def matches_record_page(idx, table, rec, url):
    """Programs and offices must bind to their own page on a shared campus website."""
    if table != "programs" and (table != "ecosystem" or rec.get("record_grain") != "office"):
        return True
    try:
        return same_page(url, record_website(idx, table, rec))
    except ValueError:
        return False


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


def press_binding(quote, idx, rid, rec, claim):
    city, state = squash(rec.get("hq_city")), state_code(rec.get("hq_state"))
    if not city or not state:
        return ""
    names = {registry_name(n) for n in record_names(rec)} - {
        registry_name(n) for n in idx.parent_names("organizations", rid)}
    place = rf"([A-Za-z .'-]+),\s*{state}\b"
    lead = re.match(place + r"\s*[–—-]\s*(.+)", quote, re.I | re.S)
    if claim == "existence" and lead and squash(lead[1]) == city:
        if any(n and f" {n} " in f" {registry_name(lead[2])} " for n in names):
            return "press_dateline"
    for hq in re.finditer(r"\bheadquartered in " + place + r"\s*,\s*([^.;]+)", quote, re.I):
        subject = re.split(r"\b(?:is|was|has|operates|announced)\b", hq[2], maxsplit=1, flags=re.I)[0]
        if squash(hq[1]) == city and registry_name(subject) in names:
            return "press_explicit_hq"
    return ""


def edgar_ref(source):
    source = source.removeprefix("SEC EDGAR ")
    try:
        u = capture_url(source)
    except ValueError:
        return None
    if u.scheme != "https" or u.query:
        return None
    if u.hostname == "data.sec.gov":
        m = re.fullmatch(r"/submissions/CIK(\d{10})\.json", u.path)
        if m:
            return source, m[1], "submissions"
    if u.hostname == "www.sec.gov":
        m = re.fullmatch(r"/Archives/edgar/data/([1-9]\d{0,9})/(\d{18})/(\d{10}-\d{2}-\d{6})\.txt", u.path)
        if m and m[2] == m[3].replace("-", ""):
            return source, m[1].zfill(10), "filing"
    return None


def judge_web(ev, rec, idx, quote):
    """Apply the existing mechanical floor. A separate proof supplies the independent reading and source replay."""
    table, cls, ct = ev["record_table"], ev["source_class"], ev["claim_type"]
    if cls == "government_filing" and table in ("sites", "organizations") and ct in ("existence", "address"):
        if edgar_ref(ev["source_ref"]):
            return "READ_REQUIRED", "sec_edgar", {}
    if cls == "press" and table == "organizations" and ct in ("existence", "address"):
        if host_path(ev["source_ref"])[0] in PRESS_HOSTS:
            route = press_binding(quote, idx, ev["record_id"], rec, ct)
            if route:
                return "READ_REQUIRED", route, {}
    fails, why, info = [], "", {}
    if table in PROGRAM_ECOSYSTEM_TABLES:
        if ct not in PROGRAM_ECOSYSTEM_CLAIMS and not (ct == "activity" and cls == "own_site"):
            return "UNINSPECTABLE", "claim_untested", {}
        if ct == "address":
            verdict, reason = record_locality(rec, quote)
            if verdict:
                return verdict, reason, {}
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
        elif not matches_record_page(idx, table, rec, ev["source_ref"]):
            fails.append("not_own_site")
    elif cls in ("directory", "press"):
        q = f" {name_key(quote)} "
        if not any(f" {k} " in q for k in idx.held_keys(table, ev["record_id"])):
            why = why or "name_absent_from_quote"
    else:
        why = why or "web_class_untested"  # registry, government_filing: no mechanical test in the ruling
    if fails:
        return "FAIL", "+".join(fails), info
    return "READ_REQUIRED", why or "mechanics_clear", info


# ---------------------------------------------------------------- LinkedIn company pages (SCHEMA §4.13, source_class linkedin_company)
# A row binds ONE labelled field of the subject company's own "About us" section to its value, in a capture the row names by sha256. Free-text
# description claims are never passed by machine; a quote is only ever a labelled field, so no person, phone or street can ride in on it.

LINKEDIN_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
LINKEDIN_PHONE = re.compile(r"(?<![\d])(?:\+\d{1,3}[ .-]?)?(?:\(\d{3}\)|\d{3})[ .-]?\d{3}[ .-]?\d{4}(?![\d])|\+\d[\d ().-]{8,}\d")
LINKEDIN_ROLE = re.compile(r"(?<!\w)(?:ceo|coo|cfo|cto|cmo|president|vice[ -]president|vp|founded by|founder|co-?founder|owner|proprietor|chairman|chair|principal|"
                           r"contact|managing director|(?:general |plant |sales |operations |regional |branch )?manager|director|chief [a-z]+ officer)(?!\w)", re.I)
LINKEDIN_NOT_NAMES = frozenset("us today team operations manager director sales marketing customer customers service services support information info page "
                               "company corporation inc llc ltd our your the and for of to at in on with details form".split())
LINKEDIN_WORD = re.compile(r"[^\W\d_][\w'’.-]*")
LINKEDIN_LABEL_NAMES = ("Website", "Industry", "Company size", "Headquarters", "Type", "Founded", "Specialties")
LINKEDIN_BRACKETS = frozenset(("0-1", "1", "2-10", "11-50", "51-200", "201-500", "501-1,000", "1,001-5,000", "5,001-10,000", "10,001+"))  # LinkedIn's fixed size brackets
LINKEDIN_INDUSTRY_FILE = ROOT / "docs/schema/linkedin_industry_codes_v2.csv"
LINKEDIN_SIGNED_IN = re.compile(r"\b(?:signed in|sign out|signed out|signout|log ?out|logged in|my network|viewing as)\b", re.I)  # whole words: "designed in" is prose
LINKEDIN_TITLE = re.compile(r"^(?:\[\d+\] )?(.+?)(?: \| LinkedIn)? \((https://[^\s)]+)\)\s*$")
LINKEDIN_CAPTURE = re.compile(r"^([0-9a-f]{64})  (raw/linkedin/([0-9a-f]{64})\.txt)$")
LINKEDIN_NOTES = re.compile(r"capture_sha256: ([0-9a-f]{64}); acquisition: guest(?:, logged out)?")
LINKEDIN_BRACKET = re.compile(r"(\d[\d,]*)(?:-(\d[\d,]*)|(\+))")
# claim_detail heads, one per field: (field, claim types allowed, grammar of the head before "; quote:")
LINKEDIN_HEADS = (
    ("industry", {"activity", "scope"}, re.compile(r"industry: ([^\W\d_][^\d;]{0,80})")),
    ("specialties", {"activity", "scope"}, re.compile(r"specialties: ([^\W\d_][^;]{0,300})")),
    ("founded", {"existence"}, re.compile(r"founded: ((?:1[89]|20)\d{2})")),
    ("hq_city", {"address"}, re.compile(r"hq_city ([^\W\d_][\w .'’-]{0,60})")),
    ("size_band", {"size_band"}, re.compile(r"(?:employee_band_global ([\w+-]+)|linkedin_size_bracket ([\d,+-]+)) \(self-declared\)")),
)
ATLAS_BANDS = (("1-9", 1, 9), ("10-49", 10, 49), ("50-99", 50, 99), ("100-249", 100, 249), ("250-499", 250, 499), ("500-999", 500, 999),
               ("1000-4999", 1000, 4999), ("5000+", 5000, float("inf")))


@lru_cache(maxsize=1)
def linkedin_industries():
    """LinkedIn's published Industry Codes V2 labels (Active), from the repo's reference file; empty if unreadable (then no industry row passes)."""
    try:
        lines = [ln for ln in LINKEDIN_INDUSTRY_FILE.read_text(encoding="utf-8").splitlines() if not ln.startswith("#")]
        return frozenset(r["label"] for r in csv.DictReader(lines))
    except (OSError, KeyError, UnicodeDecodeError):
        return frozenset()


def linkedin_name_tokens(words):
    """Leading run of capitalized name-like tokens (an initial such as M. counts), at least a given name and a surname."""
    run = []
    for w in words:
        if w[0].isupper() and w.lower().strip(".'’-") not in LINKEDIN_NOT_NAMES:
            run.append(w)
        else:
            break
    return len(run) >= 2


def linkedin_personal(text):
    """An email, a phone number, or a person named beside a role (before or after it, any case, initials, apostrophes, hyphens, accents)."""
    if LINKEDIN_EMAIL.search(text) or LINKEDIN_PHONE.search(text):
        return True
    for m in LINKEDIN_ROLE.finditer(text):
        after = LINKEDIN_WORD.findall(text[m.end():m.end() + 80])
        lead = text[max(0, m.start() - 80):m.start()]
        before = LINKEDIN_WORD.findall(lead)[::-1] if re.search(r"[,\-\u2013\u2014(]\s*$", lead) else []  # "Jane Smith, CEO": the role follows the name after a comma or dash
        if linkedin_name_tokens(after) or linkedin_name_tokens(before):
            return True
    return False


def linkedin_url_kind(url):
    """'company' for a logged-out company page, 'profile' for /in/ or /pub/, 'other' for any other URL."""
    p = urlsplit(url or "")
    host, path = (p.hostname or "").lower(), unquote(p.path)
    if host != "linkedin.com" and not host.endswith(".linkedin.com"):
        return "other"
    if re.match(r"/(?:in|pub)/", path, re.I):
        return "profile"
    if p.scheme != "https" or p.query or p.fragment or p.username or p.password or "%" in p.path.replace("%20", ""):
        return "other"  # a logged-out company page is a plain https URL: no query, fragment, userinfo or encoded path
    return "company" if re.fullmatch(r"/company/[^/]+(?:/about)?/?", path) else "other"


def linkedin_bracket_band(bracket):
    """The Atlas band a LinkedIn size bracket nests in, or '' (a bracket sets a band only if every headcount in it falls inside one band; 0 is in none)."""
    m = LINKEDIN_BRACKET.fullmatch((bracket or "").strip())
    if not m:
        return ""
    lo, hi = int(m[1].replace(",", "")), float("inf") if m[3] else int(m[2].replace(",", ""))
    if lo > hi:
        return ""  # an inverted bracket (51-20) is a mis-copy, never a band
    return next((name for name, a, b in ATLAS_BANDS if a <= lo and hi <= b), "")


def linkedin_bracket_valid(bracket):
    """A well-formed, non-inverted LinkedIn size bracket (`51-200`, `10,001+`)."""
    m = LINKEDIN_BRACKET.fullmatch((bracket or "").strip())
    return bool(m) and (bool(m[3]) or int(m[1].replace(",", "")) <= int(m[2].replace(",", "")))


def linkedin_claim(claim_detail, ct):
    """(field, value-or-None, quote) of a claim_detail `<head>; quote: <quote>`; field None for a free description (never passed by machine)."""
    head, sep, quote = claim_detail.partition("; quote:")
    head, quote = head.strip(), quote.strip()
    for field, cts, grammar in LINKEDIN_HEADS:
        m = grammar.fullmatch(head)
        if m and ct in cts:
            return field, [g for g in m.groups() if g is not None][0] if m.groups() else None, quote
    return None, None, (quote if sep else claim_detail.partition("quote:")[2].strip())


def judge_linkedin(ev, table, claim_detail, src):
    """The mechanical floor of a linkedin_company row, before any capture is read: a company page, organization grain, an allowed claim shaped
    as one labelled field, the field's own limits (HQ city and nothing more, an organization-wide self-declared band, a bracket that nests), a
    quote, and no personal data. A row that clears it is HELD until `check_linkedin_routes` replays its capture; a free description is HELD for
    reading and never passed by machine."""
    kind = linkedin_url_kind(src)
    if kind == "profile":
        return "FAIL", "linkedin_profile", {}
    if kind != "company":
        return "FAIL", "linkedin_not_company_page", {}
    if table != "organizations":
        return "FAIL", "linkedin_not_org_grain", {}  # never a site's facts, a street, a county or a child unit
    ct = ev["claim_type"]
    if ct not in ("activity", "scope", "size_band", "existence", "address"):
        return "FAIL", "linkedin_claim_not_allowed", {}
    head = claim_detail.partition("; quote:")[0].strip()
    if re.match(r"employee_band_(?:ohio|site)\b|site_band", head):
        return "FAIL", "linkedin_size_not_organization_wide", {}  # a LinkedIn size is company-wide: never an Ohio or site band
    field, value, quote = linkedin_claim(claim_detail, ct)
    if ct == "address" and field != "hq_city":
        return "FAIL", "linkedin_address_not_hq_city", {}
    if ct == "size_band" and field != "size_band":
        return "FAIL", "linkedin_size_band_not_named_self_declared", {}
    if ct == "existence" and field != "founded":
        return "FAIL", "linkedin_claim_not_a_labelled_field", {}
    if not quote:
        return "UNINSPECTABLE", "no_quote", {}
    if linkedin_personal(claim_detail):
        return "FAIL", "linkedin_personal_data", {}
    if field == "hq_city" and (re.search(r"\bcounty\b|\d", claim_detail, re.I)):
        return "FAIL", "linkedin_address_not_hq_city", {}  # a street, a number, a county or a ZIP is never a LinkedIn fact
    if field == "size_band":
        band, bracket = re.fullmatch(r"(?:employee_band_global ([\w+-]+)|linkedin_size_bracket ([\d,+-]+)) \(self-declared\)", head).groups()
        shown = LINKEDIN_BRACKET.search(quote)
        if not shown:
            return "FAIL", "linkedin_size_quote_has_no_bracket", {}  # "Company size" alone says nothing
        if bracket and (shown.group(0) != bracket or not linkedin_bracket_valid(bracket)):
            return "FAIL", "linkedin_size_bracket_not_in_quote", {}
        if band and linkedin_bracket_band(shown.group(0)) != band:
            return "FAIL", "linkedin_size_bracket_straddles_band", {}  # a band only where the bracket nests in it
    if field is None:
        return "HELD", "linkedin_description_needs_reading", {}
    if field == "specialties":
        return "HELD", "linkedin_specialties_needs_reading", {}  # a free list: read, never passed by machine
    if field == "hq_city":
        return "HELD", "linkedin_hq_city_needs_reading", {}  # whatever the record holds: the record's own city can be set in the same PR
    return "HELD", "linkedin_needs_capture", {}


def read_linkedin_capture(store, digest):
    """The digest-named capture of the shared store, hashed on the way in."""
    root = store.resolve()
    capture = root / f"raw/linkedin/{digest}.txt"
    if not capture.resolve().is_relative_to(root):
        raise ValueError("capture path escapes shared store")
    with capture.open("rb") as stream:
        data = stream.read(MAX_CAPTURE_BYTES + 1)
    if len(data) > MAX_CAPTURE_BYTES or hashlib.sha256(data).hexdigest() != digest:
        raise ValueError("capture size or digest mismatch")
    return data.decode("utf-8")


def linkedin_about(text):
    """(title match or None, the subject's own About-section fields {label: [value or None]}). The layout read is the label-line/value-line one, inside
    the section headed `## About us` only: a label is a whole line equal to one of the labels; its value is exactly the next line of the next paragraph;
    that paragraph must be that one line (so a name or a sentence on the line after the value makes the field ambiguous, None). Paragraphs are
    separated by a blank line or, in the `L<n>:` captures, a gap in the line numbers. A label word inside a value or in prose is never a label, and
    the flattened one-line layout (`Company size, 51-200 employees, Headquarters, ...`) is never parsed."""
    raw = text.split("\n")
    title = LINKEDIN_TITLE.match(raw[0]) if raw else None
    blocks, cur, last, in_about = [], [], None, False
    for ln in raw[1:]:
        m = re.match(r"^L(\d+):\s?(.*)$", ln)
        num, body = (int(m[1]), m[2].rstrip()) if m else (None, ln.rstrip())
        if re.match(r"^#{1,6} ", body.strip()):
            in_about = body.strip() == "## About us"
            if cur:
                blocks.append(cur)
            cur, last = [], None
            if in_about:
                blocks.append(["## About us"])  # a second About section is kept apart, so a repeated label shows
            continue
        if not in_about:
            continue
        gap = num is not None and last is not None and num - last > 1
        if (not body.strip() or gap) and cur:
            blocks.append(cur)
            cur = []
        if body.strip():
            cur.append(body.strip())
        last = num if num is not None else last
    if cur:
        blocks.append(cur)
    fields = {}
    for k, block in enumerate(blocks):
        if len(block) == 1 and block[0] in LINKEDIN_LABEL_NAMES:
            value_block = blocks[k + 1] if k + 1 < len(blocks) else None
            if value_block is None or (len(value_block) == 1 and value_block[0] in LINKEDIN_LABEL_NAMES) or value_block == ["## About us"]:
                value = ""  # a label with nothing after it (the Website link text is not captured)
            else:
                value = norm_space(value_block[0]) if len(value_block) == 1 else None
            fields.setdefault(block[0], []).append(value)
    return title, fields


def linkedin_name_verdict(title_name, idx, rid):
    """The structured path's name and parent rules for a page title: a parent roll-up (even one that normalizes to the child's key) never passes."""
    qkeys = name_keys([title_name])
    held, own = idx.held_keys("organizations", rid), idx.org_keys(rid)
    parents = idx.parent_keys("organizations", rid)
    own_texts, parent_texts = idx.own_texts(rid), {squash(n) for n in idx.parent_names("organizations", rid)}

    def is_parent(q):
        return q in parents or any(corporate_form_extension(k, q) for k in parents)
    if any(is_parent(q) for q in qkeys) and not qkeys & own:
        return "FAIL", "capture_names_parent"
    if any(is_parent(q) for q in qkeys) and not {squash(title_name)} & own_texts - parent_texts:
        return "HELD", "linkedin_name_equals_parent_key"
    if not qkeys & held:
        return "FAIL", "capture_name_not_held"
    return "", ""


def linkedin_result(ev, idx, store, read):
    """PASS only if: the row names its capture by sha256 (`notes: capture_sha256: <hex>; acquisition: guest`) and the task's INPUTS.sha256 names it;
    the capture is that page, not signed in; its title carries a name the record holds and is not its parent; the claimed labelled field of the
    About section has the claimed value; and the quote replays on that section and holds the field's label and value. Unreadable is HELD."""
    field, value, quote = linkedin_claim(ev["claim_detail"], ev["claim_type"])
    note = LINKEDIN_NOTES.fullmatch((ev.get("notes") or "").strip())
    if not note:
        return "HELD", "linkedin_capture_not_cited"
    folder = label_folder(ev["created_by"])
    inputs = read(f"tasks/{folder}/INPUTS.sha256") if folder else None
    if inputs is None:
        return "HELD", "linkedin_inputs_missing"
    if store is None:
        return "HELD", "linkedin_store_not_given"
    digest = note[1]
    named = any((m := LINKEDIN_CAPTURE.fullmatch(line.strip())) and m[1] == m[3] == digest for line in inputs.decode("utf-8", "replace").splitlines())
    if not named:
        return "HELD", "linkedin_capture_not_in_inputs"
    try:
        text = read_linkedin_capture(store, digest)
    except (OSError, ValueError):
        return "HELD", "linkedin_capture_unreadable"
    title, fields = linkedin_about(text)
    if not title:
        return "HELD", "linkedin_title_unbound"
    if title[2].rstrip("/").lower() != ev["source_ref"].rstrip("/").lower():
        return "FAIL", "capture_is_another_page"
    if LINKEDIN_SIGNED_IN.search(text):
        return "FAIL", "capture_not_guest"
    verdict, reason = linkedin_name_verdict(title[1], idx, ev["record_id"])
    if reason:
        return verdict, reason
    label = {"industry": "Industry", "founded": "Founded", "size_band": "Company size"}.get(field)
    if label is None:
        return "HELD", "linkedin_hq_city_needs_reading" if field == "hq_city" else "linkedin_specialties_needs_reading"
    values = fields.get(label, [])
    if not values:
        return "HELD", "linkedin_field_not_in_line_layout"  # absent, or only in the flattened one-line layout, which is never parsed
    if len(values) > 1 or values[0] is None:
        return "HELD", "linkedin_field_ambiguous"  # the label appears more than once, or the value line is not alone
    held = values[0]
    if norm_space(quote) != f"{label}, {held}":  # exactly one field as the capture shows it: no prose before or after, no second field, case kept
        return "FAIL", "linkedin_quote_not_exact_field"
    if field == "industry":
        if held not in linkedin_industries():
            return "HELD", "linkedin_industry_not_listed"
        ok = held == norm_space(value)
    elif field == "founded":
        if not re.fullmatch(r"\d{4}", held):
            return "HELD", "linkedin_founded_not_a_year"
        ok = held == value
    else:  # size_band
        found = re.fullmatch(r"(\S+?)(?: employees)?", held)
        shown = found[1] if found else ""
        if shown not in LINKEDIN_BRACKETS:
            return "HELD", "linkedin_size_not_a_linkedin_bracket"
        band, bracket = re.fullmatch(r"(?:employee_band_global ([\w+-]+)|linkedin_size_bracket ([\d,+-]+)) \(self-declared\)",
                                     ev["claim_detail"].partition("; quote:")[0].strip()).groups()
        ok = shown == bracket if bracket else linkedin_bracket_band(shown) == band != ""
    return ("PASS", "linkedin_company_replayed") if ok else ("FAIL", "claim_value_not_in_field")


def check_linkedin_routes(results, evs, idx, store, read):
    for result in results:
        if result["reason"] == "linkedin_needs_capture":
            verdict, reason = linkedin_result(evs[result["evidence_id"]], idx, store, read)
            result.update(verdict=verdict, reason=reason)


# ---------------------------------------------------------------- modes

def source_family(src):
    if src.startswith("http"):
        return "url"
    fam = family_of(src)
    return fam[0].strip() if fam else "other:" + re.split(r"[(,:;]", src)[0].strip()[:30]


VERDICTS = ("PASS", "FAIL", "HELD", "READ_REQUIRED", "UNINSPECTABLE")


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
                    "name_basis": info.get("name_basis", ""), "also_passes_on": info.get("also_passes_on", "")})
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
    SKIP = {"head", "script", "style", "noscript", "template", "nav", "header", "footer", "aside"}
    CHROME = re.compile(r"(?:^|[-_\s])(?:navbar|navigation|header|footer|sidebar)(?:$|[-_\s])", re.I)
    SKIP_ROLES = {"banner", "navigation", "contentinfo", "complementary"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.main, self.skip = [], [], []
        self.main_tag = None
        self.main_depth = 0
        self.publication_dates = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and self.skip == ["head"] and attrs.get("property") == "article:published_time":
            self.publication_dates.add((attrs.get("content") or "")[:10])
        if self.skip:
            if tag == self.skip[0]:
                self.skip.append(tag)
            return
        role = attrs.get("role")
        labels = f"{attrs.get('id', '')} {attrs.get('class', '')}"
        # Divi labels the whole body with its header layout.
        if tag == "div" and attrs.get("id") == "page":
            labels = re.sub(r"(?<!\S)header-util-ct-3(?!\S)", "", labels)
        chrome_label = tag not in ("html", "body") and self.CHROME.search(labels)
        if (tag in self.SKIP or role in self.SKIP_ROLES or chrome_label
                or "hidden" in attrs or attrs.get("aria-hidden") == "true"):
            self.skip.append(tag)
        elif tag == self.main_tag:
            self.main_depth += 1
        elif not self.main_tag and (tag == "main" or role == "main"):
            self.main_tag, self.main_depth = tag, 1

    def handle_endtag(self, tag):
        if self.skip:
            if self.skip[-1] == tag:
                self.skip.pop()
        elif tag == self.main_tag:
            self.main_depth -= 1
            if not self.main_depth:
                self.main_tag = None

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)
            if self.main_tag:
                self.main.append(data)


def norm_space(s):
    return re.sub(r"\s+", " ", s or "").strip()


def capture_text(data):
    """Proof offsets index UTF-8 text with HTML entities decoded and whitespace collapsed, in Unicode characters."""
    parser = _Text()
    parser.feed(data.decode("utf-8"))
    parser.close()
    return norm_space(" ".join(parser.main)) or norm_space(" ".join(parser.parts))


def claim_sha256(ev):
    """Stable across CSV quoting and line numbering. Any change to the claim text or quote voids the reading."""
    claim = [ev[k] for k in ("record_table", "claim_type", "claim_detail", "observed_date",
                             "source_ref", "source_class", "tier_effect")]
    return hashlib.sha256(json.dumps(claim, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def capture_url(url):
    """A public HTTP(S) URL shape with an unambiguous host and path."""
    if re.search(r"[\x00-\x20\x7f]", url) or "\\" in url:
        raise ValueError("invalid capture URL characters")
    u = urlsplit(url)
    if (u.scheme not in ("https", "http") or not u.hostname or not re.fullmatch(r"[a-z0-9.-]+", u.hostname)
            or u.username is not None or u.port is not None or u.fragment):
        raise ValueError("capture requires an HTTP(S) hostname and default port")
    path = unquote(u.path)
    if re.search(r"%2f|%25", u.path, re.I) or "\\" in path or {".", ".."} & set(path.split("/")):
        raise ValueError("ambiguous capture URL path")
    return u


def decode_capture(data, encoding):
    if len(data) > MAX_CAPTURE_BYTES:
        raise ValueError("capture exceeds byte limit")
    if encoding.strip().lower() == "gzip" or data.startswith(b"\x1f\x8b"):
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as gz:
            data = gz.read(MAX_CAPTURE_BYTES + 1)
    elif encoding.strip().lower() not in ("", "identity"):
        raise ValueError("unsupported capture encoding")
    if len(data) > MAX_CAPTURE_BYTES:
        raise ValueError("decoded capture exceeds byte limit")
    return data


def fetch_url(url):
    """Read from a vetted public destination. The vetted IP is also the connection IP."""
    u = capture_url(url)
    port = 443 if u.scheme == "https" else 80
    addresses = [ipaddress.ip_address(item[4][0])
                 for item in socket.getaddrinfo(u.hostname, port, type=socket.SOCK_STREAM)]
    if not addresses or any(not ip.is_global or ip.is_multicast for ip in addresses):
        raise ValueError("capture host must resolve only to public unicast addresses")
    addresses.sort(key=lambda ip: ip.version)
    connection = http.client.HTTPSConnection if u.scheme == "https" else http.client.HTTPConnection
    with contextlib.closing(connection(u.hostname, timeout=15)) as conn:
        # Retain the URL hostname for the Host header, TLS SNI and certificate validation.
        conn._create_connection = lambda addr, timeout, source: socket.create_connection(
            (str(addresses[0]), addr[1]), timeout, source)
        target = u.path or "/"
        if u.query:
            target += "?" + u.query
        conn.request("GET", target, headers={"Accept-Encoding": "gzip", "User-Agent": "evidence-check/1"})
        with conn.getresponse() as response:
            if response.status != 200:
                # A redirect must be resolved by the lane and cited as its own reviewed URL.
                raise ValueError(f"capture returned HTTP {response.status}")
            return decode_capture(response.read(MAX_CAPTURE_BYTES + 1), response.getheader("Content-Encoding", ""))


def load_proof_file(path, data):
    """Return proof rows keyed by evidence ID and any file-level problems."""
    out, problems = {}, []
    try:
        reader = csv.reader(io.StringIO(data.decode("utf-8")), strict=True)
        if tuple(next(reader, [])) != PROOF_COLS:
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
    except (UnicodeDecodeError, csv.Error) as e:
        return {}, [f"{path}: invalid UTF-8 or CSV: {e}"]
    return out, problems


def archive_index(links):
    out, problems = {}, []
    for link in links:
        eid = link["evidence_id"]
        if eid in out:
            problems.append(f"data/archive_links.csv: duplicate archive evidence_id {eid}")
        out[eid] = link
    return out, problems


def proof_date(value):
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("proof dates must use YYYY-MM-DD")
    return date.fromisoformat(value)


def merge_committer_date(merge, pr_head):
    if TREE != ROOT and not pr_head:
        raise ValueError("--pr-head is required to replay proofs from --tree")
    parents, day = git("show", "--no-patch", "--format=%P%n%cs", "--end-of-options", f"{merge}^{{commit}}",
                       "--", worktree=TREE).splitlines()
    parents = parents.split()
    if len(parents) != 2:
        raise ValueError("web proof replay requires a two-parent merge commit")
    if pr_head and parents[1] != pr_head:
        raise ValueError("merge commit's second parent differs from the pinned PR head")
    return proof_date(day)


def same_page(a, b):
    """Compare original page URLs using §4.22's scheme, www and trailing slash allowances."""
    def page(url):
        u = capture_url(url)
        return u.hostname.removeprefix("www."), u.path.rstrip("/"), u.query
    return page(a) == page(b)


def proof_capture(r, ev, idx, base_idx, archive, observed, *, website_witness=False):
    """Validate the cited page and date before the trusted job makes a request."""
    cap = r["capture"]
    url = capture_url(cap)
    captured = proof_date(r["capture_date"])
    if proof_date(r["reader_date"]) < captured:
        raise ValueError("reading predates the capture")
    m = ARCHIVE_RE.fullmatch(cap)
    original = m[3] if m else cap
    source_ref = ev["source_ref"]
    edgar = edgar_ref(source_ref) if ev["source_class"] == "government_filing" else None
    if edgar:
        source_ref = edgar[0]
    if m:
        if not m[2] or not archive or archive["archive_ref"] != cap.replace(m[1] + "id_/", m[1] + "/", 1):
            raise ValueError("Wayback id_ capture must match the row's archive link")
        if captured != datetime.strptime(m[1], "%Y%m%d%H%M%S").date() or captured != proof_date(archive["captured_at"]):
            raise ValueError("capture date differs from the archive index or timestamp")
        oldest = observed.replace(year=observed.year - 2, day=28 if observed.month == 2 and observed.day == 29
                                  else observed.day)
        if not oldest <= captured <= observed:
            raise ValueError("archive capture is outside the two years ending on observed_date")
    elif url.hostname == "web.archive.org":
        raise ValueError("Wayback capture must use a timestamp and id_")
    table = ev["record_table"]
    if not m and url.scheme != "https":
        raise ValueError("live capture must use HTTPS")
    capture_url(original)
    rid = ev["record_id"]
    base_record = base_idx.record(table, rid)
    cited_page = same_page(original, source_ref) if m and not edgar else original == source_ref
    if (edgar or ev["source_class"] == "press") and not cited_page:
        raise ValueError("capture differs from the row's cited page")
    if edgar:
        if edgar_ref(original) != edgar or not edgar_matches_record(edgar[1], ev, base_idx):
            raise ValueError("EDGAR capture CIK differs from the base record's sole held CIK")
        if not edgar_matches_record(edgar[1], ev, idx):
            raise ValueError("EDGAR capture CIK differs from the current record's sole held CIK")
        return cap
    if ev["source_class"] == "press":
        if capture_url(original).hostname not in PRESS_HOSTS:
            raise ValueError("capture publisher is outside the press route")
        quote = norm_space(ev["claim_detail"].partition("quote:")[2])
        if not press_binding(quote, base_idx, rid, base_record, ev["claim_type"]):
            raise ValueError("press quote does not bind to the base record")
        return cap
    site_idx = idx if website_witness else base_idx
    site_record = site_idx.record(table, rid)
    if not website_witness and record_website(base_idx, table, base_record) != record_website(idx, table, idx.record(table, rid)):
        raise ValueError("record website differs from base")
    websites = record_websites(site_idx, table, site_record, preserve_path=True)
    if (not any(own_domain(host_path(original, preserve_path=True), website) for website in websites)
            or not matches_record_page(site_idx, table, site_record, original)):
        raise ValueError("capture not_own_site")
    if not cited_page:
        raise ValueError("capture differs from the row's cited page")
    return cap


def edgar_matches_record(cik, ev, idx):
    rec = idx.record(ev["record_table"], ev["record_id"])
    oid = (rec or {}).get("org_id")
    return bool(oid and idx.sec_ciks.get(oid) == {cik}
                and sum(cik in codes for codes in idx.sec_ciks.values()) == 1)


def edgar_business(data, route):
    """Identify the filer and its business address in the source's own fields."""
    text = data.decode("utf-8")
    if route == "submissions":
        block = json.loads(text)
        address = block["addresses"]["business"]
        match = re.search(r'"business"\s*:\s*(\{[^{}]*\})', text)
        if not match or json.loads(match[1]) != address:
            raise ValueError("EDGAR business address is missing or ambiguous")
        fields = [address.get(k) for k in ("street1", "street2", "city", "stateOrCountry", "zipCode")]
        return str(block["cik"]).zfill(10), fields, norm_space(match[1]), norm_space(text)
    # Full submission .txt files carry the authoritative filer header ahead of the document bodies.
    header = re.search(r"<SEC-HEADER>(.*?)</SEC-HEADER>", text, re.S)
    if not header:
        raise ValueError("EDGAR full submission header is absent")
    filer = re.findall(r"(?m)^FILER:\s*\n((?:[ \t].*\n|\n)+)", header[1])
    if len(filer) != 1:
        raise ValueError("EDGAR document must have one filer")
    cik = re.findall(r"(?m)^\s*CENTRAL INDEX KEY:\s*(\d{10})\s*$", filer[0])
    addresses = re.findall(r"(?m)^\tBUSINESS ADDRESS:\s*\n((?:\t{2,}[^\n]+\n)+)", filer[0])
    if len(cik) != 1 or len(addresses) != 1:
        raise ValueError("EDGAR filer CIK or business address is missing or ambiguous")
    fields = dict(line.strip().split(":", 1) for line in addresses[0].splitlines())
    return cik[0], [fields.get(k, "").strip() for k in ("STREET 1", "STREET 2", "CITY", "STATE", "ZIP")], (
        norm_space(addresses[0])), norm_space(text)


def edgar_replay(ev, rec, base_record, data, quote, start):
    _, cik, route = edgar_ref(ev["source_ref"])
    actual_cik, fields, business, text = edgar_business(data, route)
    if actual_cik != cik or quote != business or text[start:start + len(quote)] != quote:
        return "EDGAR quote must replay the linked filer's complete business address"
    line1, line2, city, state, zip_code = fields
    if not all(isinstance(x, str) and x for x in (line1, city, state, zip_code)):
        return "EDGAR business address is incomplete"
    street = ", ".join(filter(None, (line1, line2)))
    addr = f"{street}, {city}, {state} {zip_code}"
    for held in (rec, base_record):
        if ev["record_table"] == "sites":
            county = squash(held.get("county"))
            if (held.get("site_type") not in ("hq_only", "hq_and_plant")
                    or registry_place(held, addr, county) not in ("registry_street", "mailing_city")):
                return "EDGAR business address does not bind to the held headquarters site"
        elif ev["claim_type"] != "existence" or not hq_in_quote(addr, held):
            return "EDGAR business address does not bind the claimed organization locality"
    return ""


def proof_problem(r, ev, idx, base_idx, archive, observed, builder, fetch, *, website_witness=False):
    if r["record_id"] != ev["record_id"] or r["claim_sha256"] != claim_sha256(ev):
        return "proof record_id or claim_sha256 differs from the evidence row"
    if r["verdict"] != "VERIFIED":
        return "only a VERIFIED reading admits a row"
    rf = family_of_text(r["reader_family"])
    if not (rf and builder and rf != builder):
        return "builder and reader must name different known model families"
    if not re.fullmatch(r"[0-9a-f]{64}", r["capture_sha256"]):
        return "capture_sha256 must be 64 lowercase hex digits"
    if not re.fullmatch(r"[0-9]{1,8}", r["quote_offset"]):
        return "quote_offset must be a nonnegative integer within the capture byte limit"
    quote = norm_space(ev["claim_detail"].partition("quote:")[2])
    if len(quote) < 20:
        return "quote must contain at least 20 characters"
    try:
        url = proof_capture(r, ev, idx, base_idx, archive, observed, website_witness=website_witness)
    except ValueError as e:
        return str(e)
    try:
        data = fetch(url)
    except Exception as e:  # Any fetch or decoding failure blocks admission.
        return f"could not inspect capture: {e}"
    if hashlib.sha256(data).hexdigest() != r["capture_sha256"]:
        return "capture_sha256 does not match the decoded bytes"
    start = int(r["quote_offset"])
    try:
        table, rid = ev["record_table"], ev["record_id"]
        if ev["source_class"] == "government_filing" and edgar_ref(ev["source_ref"]):
            return edgar_replay(ev, idx.record(table, rid), base_idx.record(table, rid), data, quote, start)
        if ev["source_class"] == "press":
            parser = _Text()
            parser.feed(data.decode("utf-8"))
            if len(parser.publication_dates) != 1:
                return "press capture must contain one publication date"
            if proof_date(next(iter(parser.publication_dates))) > proof_date(r["capture_date"]):
                return "press publication date is after the capture"
        actual = capture_text(data)[start:start + len(quote)]
    except (ValueError, KeyError, TypeError, AttributeError):
        return "capture fields could not be read"
    if actual != quote:
        return "the quote is not at that offset in the capture's main text"
    return ""


def check_proofs(results, evs, idx, load_base, merge, pr_head, archive, read, fetch, *,
                 website_witnesses=(), held_read=None):
    """Replay proofs only for web rows that cleared the existing mechanical floor."""
    need = defaultdict(list)
    for row in results:
        ev = evs[row["evidence_id"]]
        if row["verdict"] == "READ_REQUIRED" and (
            (row["reason"] == "mechanics_clear" and ev["source_class"] == "own_site")
            or row["reason"] in ("press_dateline", "press_explicit_hq", "sec_edgar")
        ):
            need[label_folder(row["created_by"])].append(row)
    if not need:
        return []
    base_idx = load_base()
    merge_date = None
    problems, cache = [], {}

    def cached_fetch(url):
        if url not in cache:
            try:
                cache[url] = fetch(url)
            except Exception as e:
                cache[url] = e
        if isinstance(cache[url], Exception):
            raise cache[url]
        return cache[url]

    for folder, candidates in sorted(need.items()):
        path = f"tasks/{folder}/BINDING_PROOF.csv"
        data = read(path) if folder else None
        if data is None:
            problems.append(f"{len(candidates)} rows need proofs in the folder named by created_by; absent: {path}")
            continue
        proofs, shape = load_proof_file(path, data)
        if shape:
            problems.extend(shape)
            continue
        readme = f"tasks/{folder}/README.md"
        builder = builder_family(read(readme))
        held_proofs = {}
        if held_read and builder == builder_family(held_read(readme)):
            held_data = held_read(path)
            if held_data is not None:
                held_proofs, _ = load_proof_file(path, held_data)
        for result in candidates:
            eid = result["evidence_id"]
            website_witness = eid in website_witnesses
            if not website_witness and base_idx.record(result["record_table"], result["record_id"]) is None:
                result.update(verdict="HELD", reason="record absent from base")
                continue
            if eid not in proofs:
                problems.append(f"{eid}: no proof line in {path}")
                continue
            at, row = proofs[eid]
            held_proof = held_proofs.get(eid)
            previously_held = held_proof and held_proof[1] == row
            if merge_date is None and not previously_held:
                merge_date = merge_committer_date(merge, pr_head)
            ev = evs[eid]
            try:
                observed = proof_date(ev.get("observed_date", ""))
            except ValueError:
                result.update(verdict="HELD", reason="invalid observed_date")
                continue
            if not previously_held and abs((observed - merge_date).days) > 30:
                result.update(verdict="HELD", reason="observed_date more than 30 days from merge commit committer date")
                continue
            why = proof_problem(row, ev, idx, base_idx, archive.get(eid), observed, builder, cached_fetch,
                                website_witness=website_witness)
            if why:
                problems.append(f"{at}: {eid}: {why}")
            else:
                route = result["reason"]
                result.update(verdict="PASS", reason="web_proof_replayed" if route == "mechanics_clear"
                              else f"{route}_proof_replayed")
    return problems


# A state abbreviation by itself is ambiguous. Accept the postal form or a held locality in the quote.
OHIO_POSTAL = re.compile(r"\b(?:OH|Ohio),?\s+4[3-5]\d{3}(?:-\d{4})?\b", re.I)
WEB_STREET_SUFFIX = "|".join(sorted(set(SUFFIX) | set(SUFFIX.values()), key=len, reverse=True))
OHIO_ADDRESS = re.compile(
    rf"\b\d{{1,6}}\s+[^,;]{{2,75}}\s+(?:{WEB_STREET_SUFFIX}|way|pike)\.?,"
    r"\s*[a-z][a-z .'-]{1,45},?\s+(?:OH|Ohio)\b", re.I)
OTHER_STATE = re.compile(
    r"^(?:\s*,\s*(?P<comma>[A-Za-z]{2})\b|\s+(?P<code>[A-Z]{2})\b|"
    r"(?:\s*,\s*|\s+)(?P<name>(?i:" + "|".join(STATE_NAMES) + r"))\b)")


def changed_websites(base_idx, idx):
    base_orgs = base_idx.tables["organizations"]
    return {oid: org for oid, org in idx.tables["organizations"].items()
            if (org.get("website") or "").strip().lower() not in ("", "none_found")
            and org["website"] != base_orgs.get(oid, {}).get("website")}


@lru_cache(maxsize=1)
def public_suffix_rules():
    path = ROOT / "scripts/vendor/public_suffix_list.dat"
    rules = {line for line in path.read_text(encoding="ascii").splitlines() if line and not line.startswith("//")}
    if len(rules) < 9000:
        raise ValueError("public suffix snapshot is incomplete")
    return rules


def website_registrable(host):
    labels = host.rstrip(".").split(".")
    rules = public_suffix_rules()
    suffix_size = 1
    for i in range(len(labels)):
        suffix = ".".join(labels[i:])
        if f"!{suffix}" in rules:
            suffix_size = len(labels) - i - 1
            break
        if suffix in rules:
            suffix_size = max(suffix_size, len(labels) - i)
        if i and f"*.{suffix}" in rules:
            suffix_size = max(suffix_size, len(labels) - i + 1)
    return ".".join(labels[-suffix_size - 1:]) if len(labels) > suffix_size else None


def website_domain_matches(source, website):
    source_domain = website_registrable(capture_url(source).hostname)
    website_domain = website_registrable(capture_url(website).hostname)
    return bool(source_domain and source_domain == website_domain
                and own_domain(host_path(source, preserve_path=True), host_path(website, preserve_path=True)))


def website_witnesses(fills, idx, evidence):
    """Return eligible witness IDs by organization and the reason where no witness reaches replay."""
    public_suffix_rules()
    places = defaultdict(set)
    for oid, org in fills.items():
        if state_code(org.get("hq_state")) == "OH":
            county = org.get("hq_county") or ""
            places[oid].update((org.get("hq_city") or "", f"{county} County" if county else ""))
    for site in idx.sites.values():
        oid = site.get("org_id")
        if oid in fills and state_code(site.get("state")) == "OH":
            county = site.get("county") or ""
            places[oid].update((site.get("city") or "", f"{county} County" if county else ""))

    own = defaultdict(list)
    for ev in evidence:
        if ev["record_table"] == "organizations" and ev["source_class"] == "own_site" and ev["record_id"] in fills:
            own[ev["record_id"]].append(ev)

    candidates, reasons = defaultdict(set), {}
    for oid, org in fills.items():
        if oid not in places:
            reasons[oid] = "no held Ohio headquarters or site"
            continue
        website = org["website"].strip()
        if "://" not in website:
            website = f"https://{website}"
        try:
            host = capture_url(website).hostname
            if not website_registrable(host) or linkedin_url(website):
                raise ValueError("invalid website host")
        except ValueError:
            reasons[oid] = "website must name one own-site domain"
            continue
        stage = 0
        names = idx.held_keys("organizations", oid) | idx.own_texts(oid)
        for ev in own[oid]:
            stage = max(stage, 1)
            source = ev["source_ref"]
            try:
                if linkedin_url(source) or not website_domain_matches(source, website):
                    continue
            except ValueError:
                continue
            stage = max(stage, 2)
            quote = norm_space(ev["claim_detail"].partition("quote:")[2])
            qkey = f" {squash(quote)} "
            if not any(f" {name} " in qkey for name in names):
                continue
            stage = max(stage, 3)
            # A city word inside a company name is not a locality assertion.
            locality_text = quote
            for name in sorted(names, key=len, reverse=True):
                pattern = r"\b" + r"[\W_]+".join(map(re.escape, name.split())) + r"\b"
                locality_text = re.sub(pattern, " ", locality_text, flags=re.I)
            if (OHIO_POSTAL.search(locality_text) or OHIO_ADDRESS.search(locality_text)
                    or any(quoted_ohio_place(place, locality_text) for place in places[oid])):
                candidates[oid].add(ev["evidence_id"])
                stage = 4
        reasons[oid] = ("no own-site evidence", "no same-domain own-site evidence",
                        "no same-domain quote contains a held name", "no held-name quote contains an Ohio locality",
                        "no own-site witness passed capture replay")[stage]
    return candidates, reasons


def quoted_ohio_place(place, quote):
    if not place:
        return False
    pattern = r"\b" + re.escape(place) + r"\b"
    for found in re.finditer(pattern, quote, re.I):
        qualifier = OTHER_STATE.match(quote[found.end():])
        if not qualifier or state_code(qualifier["comma"] or qualifier["code"] or qualifier["name"]) in ("", "OH"):
            return True
    return False


# These routes need the base tree. The head can contain the very street or name being proposed.
MAP_PROVIDERS = ("google-places", "overture-maps-places")
MAP_REF = re.compile(r"(google-places|overture-maps-places) ([A-Za-z0-9_-]{1,256})")
FILING_ALIAS = re.compile(r"([^;()]+) \((OSHA|EPA) filing name\)")
PHYSICAL_ROLES = {"", "physical"}
HELD_FRS_LEAD = re.compile(
    r"Address \d{4}-\d{2}-\d{2} \(gov-data pipeline, EPA FRS facility \d{12}, STRONG match\): ([^;()]+)")
FILING_LOCATOR = re.compile(
    r"\b(?:activity_nr|establishment(?:_id| id)?|inspection|handler|facility|core_place_id|FRS registry)"
    r"[ =]+[A-Z]*\d{5,}(?:\.\d+)?\b|; raw/(?:osha|epa)/[^;\n]+(?:@\d+|\.pdf)(?:$|;)", re.I)
ADDRESS_RISK = re.compile(
    r"@|\d{3}[-. ]\d{3}[-. ]\d{4}|\b(?:p\.?\s*o\.?\s*box|mail(?:ing)?|(?:registered|statutory) agent|"
    r"registered[ _]office|apt|apartment|residence|home address|sole propriet(?:or|orship))\b", re.I)


def physical_street(street):
    head = street_key(street).partition(" ")[0]
    return (has_civic_number(head) and (head[0].isdigit() or head.isalpha())
            and not ADDRESS_RISK.search(street) and not PAREN_RE.search(street)
            and not street_suffix_unexplained(street) and same_street(street, street)
            and designators_compare(street, street) == "equal")


def strict_place(site, city, state):
    return bool(squash(city)) and squash(city) == squash(site.get("city")) and state == site.get("state")


def bound_street(site, addr):
    city, state, _, complete = quoted_place(addr)
    street = street_part(addr).strip()
    return street if complete and not PAREN_RE.search(addr) and strict_place(site, city, state) and physical_street(street) else ""


def filing_agency(source):
    if source.startswith("OSHA "):
        return "OSHA"
    if source.startswith(("EPA ECHO ", "Ohio EPA ")):
        return "EPA"
    return ""


def filing_fields(quote, source):
    fields = labelled_fields(quote)
    if fields:
        operators = {"operator", "permittee", "company_name", "establishment_name", "legal_name", "borrower_name"}
        addresses = {"address", "physical_address"}
        if (len(LABEL_RE.findall(quote)) != len(fields) or len(addresses & fields.keys()) != 1
                or not fields.keys() <= operators | addresses | {"county"}):
            return [], ""
        return [fields[k] for k in operators & fields.keys()], (fields.get("physical_address") or fields.get("address", ""))
    fam = family_of(source)
    parsed = parse_quote(quote, fam) if fam else {}
    return parsed.get("names", []), parsed.get("addr", "")


def read_map_capture(root, provider, digest, place_id):
    """Optional lane replay of the digest-named object in the shared store."""
    root = root.resolve()
    capture = root / f"raw/map-listings/{provider}/{digest}.json"
    if not capture.resolve().is_relative_to(root):
        raise ValueError("capture path escapes shared store")
    with capture.open("rb") as stream:
        data = stream.read(MAX_CAPTURE_BYTES + 1)
    if len(data) > MAX_CAPTURE_BYTES or hashlib.sha256(data).hexdigest() != digest:
        raise ValueError("capture size or digest mismatch")
    row = json.loads(data, object_pairs_hook=unique_capture_fields)
    if row["id"] != place_id:
        raise ValueError("capture id mismatch")
    if provider == "google-places":
        if row.get("pureServiceAreaBusiness"):
            raise ValueError("listing has no physical premises")
        addr = row["postalAddress"]
        street, = addr["addressLines"]
        values = row["displayName"]["text"], street, addr["locality"], addr["administrativeArea"]
        country = addr["regionCode"]
    else:
        properties = row["properties"]
        if (row["type"], properties["theme"], properties["type"]) != ("Feature", "places", "place"):
            raise ValueError("capture is not an Overture place")
        addr, = properties["addresses"]
        values = properties["names"]["primary"], addr["freeform"], addr["locality"], addr["region"].removeprefix("US-")
        country = addr["country"]
    if country != "US" or not all(isinstance(v, str) and v.strip() for v in values):
        raise ValueError("incomplete US listing")
    return values


def unique_capture_fields(pairs):
    fields = dict(pairs)
    if len(fields) != len(pairs):
        raise ValueError("capture contains duplicate fields")
    return fields


def map_second_source(ref, site, base_idx, evidence, provider):
    sid = site["site_id"]
    if ref.startswith("lead: "):
        text = ref.removeprefix("lead: ")
        # Match a complete held clause. Separate provenance in a site's source list does not identify this street.
        held_notes = site.get("notes") or ""
        clauses = re.split(r"[;\n]", held_notes)
        frs = HELD_FRS_LEAD.fullmatch(text)
        if frs and re.search(r"(?:^|[.;] )" + re.escape(text) + r"(?= \(the sites schema|[.;] |$)", held_notes):
            street = bound_street(site, frs[1])
            return (street, "") if street else ("", "map_second_source_unbound")
        m = re.fullmatch(r"Street \(per ([^()]+)\): (.+)", text)
        if not m or text not in {clause.strip() for clause in clauses}:
            return "", "map_second_source_unbound"
        origin, street = m.groups()
        aliases = {"2026-11-14 Google Maps scrape": "google-places", "Google Maps": "google-places",
                   "Google Places": "google-places", "Overture Maps": "overture-maps-places"}
        origin = aliases.get(origin, origin)
        if origin == provider:
            return "", "map_second_source_same_provider"
        if origin not in {*MAP_PROVIDERS, "OSHA", "EPA", "Ohio EPA", "SBA PPP", "SAM.gov"}:
            return "", "map_second_source_unknown_origin"
        return street, ""
    row = evidence.get(ref)
    if (not row or (row["record_table"], row["record_id"]) != ("sites", sid)
            or row["claim_type"] not in ("address", "existence")
            or (row.get("address_role") or "") not in PHYSICAL_ROLES):
        return "", "map_second_source_unbound"
    src, kind = row["source_ref"], row["source_class"]
    quote = row["claim_detail"].partition("quote:")[2].strip()
    if ADDRESS_RISK.search(quote):
        return "", "map_second_source_unbound"
    addr = ""
    if kind == "own_site" and src.startswith(("https://", "http://")) and any(
            own_domain(host_path(src), website) for website in record_websites(base_idx, "sites", site)):
        addr = re.sub(r"(?i)^address:? ", "", quote).removesuffix(", United States")
    elif kind == "government_filing" and (filing_agency(src) or src.startswith(("SBA PPP ", "SAM.gov "))):
        names, reported = filing_fields(quote, src)
        if (name_keys(names) & base_idx.held_keys("sites", sid)
                and not name_keys(names) & base_idx.parent_keys("sites", sid)):
            addr = reported
    street = bound_street(site, addr)
    return (street, "") if street else ("", "map_second_source_unbound")


def map_listing_result(ev, base_idx, idx, evidence, store):
    rid = ev["record_id"]
    src = MAP_REF.fullmatch(ev["source_ref"])
    if (not src or ev["source_class"] != "platform_category"
            or (ev["record_table"], ev["claim_type"]) != ("sites", "address")
            or ev.get("tier_effect") not in {"supports_C", "supports_U"}):
        return "HELD", "map_claim_or_ceiling"
    if ev.get("address_role"):
        return "HELD", "map_address_role"
    site, proposed = base_idx.sites.get(rid), idx.sites[rid]
    if not site or site.get("org_id") != proposed.get("org_id"):
        return "HELD", "map_site_not_held"
    if (site.get("street_address") or "").strip():
        return "HELD", "map_base_street_already_held"
    notes = re.fullmatch(r"capture_sha256: ([0-9a-f]{64}); second_source: (EVD-\d+|lead: .+)", ev.get("notes") or "")
    if not notes:
        return "HELD", "map_capture_or_second_source_not_cited"
    claim, sep, quote = ev["claim_detail"].partition("; quote: ")
    fields = labelled_fields(quote)
    if not sep or not fields or set(fields) != {"name", "street", "city", "state"} or len(LABEL_RE.findall(quote)) != 4:
        return "HELD", "map_listing_quote_incomplete"
    name, street, city, state = (fields[k] for k in ("name", "street", "city", "state"))
    provider, place_id = src.groups()
    if store is not None:
        try:
            if read_map_capture(store, provider, notes[1], place_id) != (name, street, city, state):
                return "HELD", "map_capture_differs_from_quote"
        except (AttributeError, KeyError, OSError, TypeError, ValueError):
            return "HELD", "map_capture_unreplayable"
    keys = name_keys([name])
    if (not keys & base_idx.held_keys("sites", rid) or not keys & idx.held_keys("sites", rid)
            or keys & (base_idx.parent_keys("sites", rid) | idx.parent_keys("sites", rid))):
        return "HELD", "map_operator_not_held"
    if not strict_place(site, city, state) or not strict_place(proposed, city, state):
        return "HELD", "map_city_or_state_differs"
    if not physical_street(street) or ADDRESS_RISK.search(name):
        return "HELD", "map_address_role"
    if norm_space(street) != norm_space(claim) or norm_space(street) != norm_space(
            proposed.get("street_address") or ""):
        return "HELD", "map_street_not_filled_as_listed"
    second, reason = map_second_source(notes[2], site, base_idx, evidence, provider)
    if reason:
        return "HELD", reason
    if not physical_street(second) or not same_street(street, second) or designators_compare(street, second) != "equal":
        return "HELD", "map_second_street_differs"
    return "PASS", "map_listing_street_bound"


# The private-address screen uses the business words and personal-name shape from the PIC-18 street packet.
FILING_BUSINESS_WORDS = frozenset("""inc incorporated llc corp corporation co company companies ltd lp llp plc usa us group holdings holding industries industrial industry plastics plastic rubber polymer polymers chemical chemicals
products product manufacturing mfg machine machines machining tool tooling mold molding foam foams metal metals steel supply services service systems technologies technology tech international american america
center centre hospital hospitals university college school city county church association society institute laboratory laboratories labs lab associates partners enterprises engineering equipment
packaging packaged printing graphics coatings coating paint adhesives composites fiberglass fibre fiber glass wire cable seal seals sealing gasket extrusion extrusions extruded fabricating fabrication
distribution distributors logistics transport trucking freight energy power electric electrical medical dental health care clinic pharmacy foods food farm farms mills mill works plant
division dept department management consulting solutions design designs controls control instruments instrument optical vision labs research development bag bags box boxes container containers
tire tires auto automotive truck trailer trailers marine boat boats pool pools roofing roof building buildings construction contractors contracting concrete cement stone wood lumber furniture
global national united first general universal precision quality superior advanced applied custom premier standard pioneer summit eagle star""".split())
_PERSONAL_NAME = re.compile(r"[A-Za-z][A-Za-z .,'-]*")
_FILING_FORM = re.compile(r"(?: (?:incorporated|inc|l l c|llc|corporation|corp|company|co|limited|ltd|l l p|llp|l p|lp))+$")


def filing_words(name):
    key = _FILING_FORM.sub("", " " + squash(name).removeprefix("the ")).strip()
    return tuple(re.sub(r"(?<=[a-z]) (?=\d)|(?<=\d) (?=[a-z]\b)", "", key).split())


def private_filing_name(name):
    if ADDRESS_RISK.search(name):
        return True
    for value in (name, name_key(name), " ".join(filing_words(name))):
        words = squash(value).split()
        if _PERSONAL_NAME.fullmatch(value) and 2 <= len(words) <= 3 and not FILING_BUSINESS_WORDS.intersection(words):
            return True
    return False


def filing_variant_result(ev, base_idx, idx, base_sites, additions):
    rid = ev["record_id"]
    marker, sep, quote = ev["claim_detail"].removeprefix("trade_names + ").partition("; quote: ")
    name = FILING_ALIAS.fullmatch(marker)
    if (not sep or not name or (rid, marker) not in additions or ev["source_class"] != "government_filing"
            or (ev["record_table"], ev["claim_type"]) != ("organizations", "existence")
            or name[2] != filing_agency(ev["source_ref"]) or not FILING_LOCATOR.search(ev["source_ref"])
            or (ev.get("address_role") or "") not in PHYSICAL_ROLES):
        return "FAIL", "filing_variant_claim_or_agency"
    if not base_idx.record("organizations", rid):
        return "HELD", "filing_variant_org_not_held"
    names, address = filing_fields(quote, ev["source_ref"])
    if name[1] not in names:
        return "FAIL", "filing_variant_not_quoted_operator"
    if private_filing_name(name[1]) or ADDRESS_RISK.search(address):
        return "FAIL", "filing_variant_private_address_screen"
    words = filing_words(name[1])
    parent_names = base_idx.parent_names("organizations", rid) | idx.parent_names("organizations", rid)
    parents = {filing_words(parent) for parent in parent_names}
    if not words or words in parents or any(
            corporate_form_extension(" ".join(parent), " ".join(words)) for parent in parents):
        return "FAIL", "filing_variant_parent_name"
    held_words = [filing_words(PAREN_RE.sub(" ", n)) for n in record_names(base_idx.orgs[rid])]
    if not any(held and not generic_label(" ".join(held)) and set(held) <= set(words) for held in held_words):
        return "FAIL", "filing_variant_distinctive_words_missing"
    matched = []
    for site in base_sites[rid]:
        if street := bound_street(site, address):
            prior = site.get("street_address")
            current = idx.sites.get(site["site_id"], {})
            if (physical_street(prior) and same_street(prior, street) and designators_compare(prior, street) == "equal"
                    and all(current.get(k) == site.get(k) for k in ("org_id", "street_address", "city", "state"))):
                matched.append(site["site_id"])
    if len(matched) != 1:
        return "HELD", "filing_variant_site_not_held"
    return "PASS", "filing_name_variant_bound"


def check_address_routes(results, evs, idx, base_idx, base_evs, store):
    additions = set()
    for oid, org in idx.tables["organizations"].items():
        held = base_idx.orgs.get(oid, {}).get("trade_names")
        additions.update((oid, alias) for alias in set(tokens_semicolon(org.get("trade_names"))) - set(tokens_semicolon(held))
                         if FILING_ALIAS.fullmatch(alias))
    base_sites = defaultdict(list)
    for site in base_idx.sites.values():
        base_sites[site["org_id"]].append(site)
    evidence = {ev["evidence_id"]: ev for ev in base_evs}
    matched = Counter()
    for result in results:
        ev = evs[result["evidence_id"]]
        if result["reason"] == "map_listing_needs_base":
            verdict, reason = map_listing_result(ev, base_idx, idx, evidence, store)
        elif result["reason"] == "filing_variant_needs_base":
            verdict, reason = filing_variant_result(ev, base_idx, idx, base_sites, additions)
            if verdict == "PASS":
                alias = ev["claim_detail"].removeprefix("trade_names + ").partition("; quote: ")[0]
                matched[(ev["record_id"], alias)] += 1
        else:
            continue
        result.update(verdict=verdict, reason=reason)
    return [f"{oid}: filing variant addition has {'no matching' if not matched[oid, alias] else 'more than one'} evidence row"
            for oid, alias in sorted(additions) if matched[oid, alias] != 1]


# ---------------------------------------------------------------- provenance


def provenance_problems(new_evs, base_labels, base_has_folder, head_check_bytes):
    """Problems with the provenance of the rows a PR adds or changes, one line per created_by label: the label names
    exactly one folder; that folder holds a non-empty check.py; a label new to the base adds its folder in this PR.
    Presence only: the gate executes nothing from the tree it gates (owner ruling 2026-11-22, split of PR #467). The
    replay the check.py performs is run by the lane and by the reviewing family."""
    problems = []
    for label, n in sorted(Counter(e["created_by"].strip() for e in new_evs).items()):
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
    return problems


def audit_sample(results, n, seed):
    """Audit of the gate, never admission: N PASS rows per created_by label, chosen by sha256(seed:evidence_id), for a
    reviewer to read; the share found unbound estimates the gate's escape rate."""
    by_label = defaultdict(list)
    for r in results:
        if r["verdict"] == "PASS":
            by_label[r["created_by"].strip()].append(r)
    return {k: sorted(v, key=lambda r: hashlib.sha256(f"{seed}:{r['evidence_id']}".encode()).hexdigest())[:n]
            for k, v in sorted(by_label.items())}


def resolve_base(ref, head, pr_head=None):
    if TREE != ROOT and pr_head:  # The checked-out merge ref pins the base even if main advances.
        return git("rev-parse", "HEAD^1", worktree=TREE).strip()
    if TREE != ROOT:  # A plain directory has no history: compare with REF itself.
        return git("rev-parse", ref).strip()
    return git("merge-base", ref, head or "HEAD").strip()


def main(argv=None):
    global TREE
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true", help="report every evidence row by verdict, created_by and source")
    g.add_argument("--new-since", metavar="REF", help="gate rows added or changed since the merge-base with REF")
    g.add_argument("--verify-proofs", metavar="REF", help="same as --new-since: replay web proofs")
    g.add_argument("--provenance-since", metavar="REF", help="require tasks/<folder>/check.py for new rows")
    g.add_argument("--sample", metavar="N", type=int, help="audit only: list N PASS rows per created_by label to read")
    ap.add_argument("--seed", default="1", help="--sample seed")
    ap.add_argument("--since", metavar="REF", help="--sample: only rows added or changed since REF")
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--head", help="git ref to read instead of the working tree")
    src.add_argument("--tree", metavar="DIR", help="read data/ and tasks/ from DIR (an authoritative run: this "
                                                   "script and its rules come from the trusted checkout)")
    ap.add_argument("--pr-head", help="pinned PR head SHA to verify against the merge commit second parent")
    ap.add_argument("--out", help="write per-row verdicts to this CSV")
    ap.add_argument("--map-store", type=Path, help="the shared store root: also replay map captures (raw/map-listings/) and LinkedIn captures (raw/linkedin/<sha256>.txt) when gating changes")
    a = ap.parse_args(argv)
    if a.map_store is not None and not (a.new_since or a.verify_proofs):
        ap.error("--map-store requires --new-since or --verify-proofs")
    TREE = Path(a.tree).resolve() if a.tree else ROOT
    gate = a.new_since or a.verify_proofs
    try:
        head_evs = rows(a.head, "evidence_*.csv")
        since = gate or a.provenance_since or (a.since if a.sample else None)
        base = resolve_base(since, a.head, a.pr_head) if since else None
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
        problems = provenance_problems(evs, {e["created_by"].strip() for e in base_evs},
                                       lambda f: any(x.startswith(f"tasks/{f}/") for x in base_paths), head_check)
        print(f"provenance: {len(evs)} evidence rows added or changed since {base[:10]} under "
              f"{len({e['created_by'].strip() for e in evs})} created_by label(s); presence checked, nothing executed")
        for line in problems:
            print("  " + line)
        return 1 if problems else 0

    idx = Index.load(a.head)
    results = judge_all(evs, idx)
    problems = []
    if gate:
        try:
            archive, problems = archive_index(rows(a.head, "archive_links.csv"))
            if not problems:
                base_idx = Index.load(base)
                evidence_by_id = {e["evidence_id"]: e for e in evs}
                problems = check_address_routes(results, evidence_by_id, idx, base_idx, base_evs, a.map_store)
                check_linkedin_routes(results, evidence_by_id, idx, a.map_store, lambda path: tasks_file(a.head, path))
                fills = changed_websites(base_idx, idx)
                candidates, reasons = website_witnesses(fills, idx, head_evs) if fills else ({}, {})
                witness_ids = set().union(*candidates.values())
                read = lambda path: tasks_file(a.head, path)
                problems += check_proofs(results, evidence_by_id, idx, lambda: base_idx,
                                         a.head or "HEAD", a.pr_head, archive, read, fetch_url,
                                         website_witnesses=witness_ids)
                if fills:
                    passed = {r["evidence_id"] for r in results if r["verdict"] == "PASS"
                              and r["reason"] == "web_proof_replayed"}
                    pending = set().union(*(ids for ids in candidates.values() if ids.isdisjoint(passed)))
                    pending.difference_update(evidence_by_id)
                    held_evs = [ev for ev in head_evs if ev["evidence_id"] in pending]
                    held_results = judge_all(held_evs, idx)
                    replay_problems = check_proofs(
                        held_results, {ev["evidence_id"]: ev for ev in held_evs}, idx, lambda: base_idx,
                        a.head or "HEAD", a.pr_head, archive, read, fetch_url,
                        website_witnesses=witness_ids, held_read=lambda path: tasks_file(base, path))
                    passed.update(r["evidence_id"] for r in held_results if r["verdict"] == "PASS"
                                  and r["reason"] == "web_proof_replayed")
                    rejected = [f"{oid} website: {reasons[oid]}" for oid in fills
                                if not candidates.get(oid, set()) & passed]
                    print(f"website rule: {len(fills) - len(rejected)}/{len(fills)} website fills passed")
                    if rejected:
                        problems[:0] = rejected + replay_problems
        except (csv.Error, ValueError, OSError, subprocess.CalledProcessError) as e:
            print(f"binding gate: could not inspect proof inputs: {e}")
            return 2
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
    held = [r for r in results if r["verdict"] not in ("PASS", "FAIL")]
    print(f"\nbinding gate: {len(results)} rows added or changed since {base[:10]}; "
          f"{len(results) - len(fails) - len(held)} PASS, {len(fails)} FAIL, {len(held)} HELD, READ_REQUIRED or UNINSPECTABLE")
    for r in fails[:200]:
        print(f"  FAIL {r['reason']:40s} {r['evidence_id']} {r['at']}")
    for r in held[:200]:
        print(f"  {r['verdict']:13s} {r['reason']:31s} {r['evidence_id']} {r['at']}")
    if len(fails) + len(held) > 400:
        print("  ... (use --out for the full list)")
    if fails:
        print("A FAIL row has no waiver: fix the row, or take it out and hold it as a lead.")
    if held:
        print("Held rows require a binding match. Eligible own-site, press and SEC EDGAR rows may supply a proof.")
    for problem in problems[:200]:
        print("  PROOF " + problem)
    if len(problems) > 200:
        print(f"  ... and {len(problems) - 200} more proof problems")
    return 1 if fails or held or problems else 0


if __name__ == "__main__":
    sys.exit(main())
