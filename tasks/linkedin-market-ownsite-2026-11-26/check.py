#!/usr/bin/env python3
"""Named check for the own-site market fills of the LinkedIn reading pilot's owners.

    python3 check.py [--captures DIR]    the clean tree must pass and every planted defect must fail

Offline: it fetches nothing. The captures are replayed from DIR or the shared store (provenance/<task>/captures/<sha256>.html);
the hosted binding gate replays every Wayback capture independently. What it asserts, against the merge-base:
  * the only organization cells that changed are markets_served, on exactly the owners with a `corrected` line in
    CLAIMS_CHECKED.csv, and each cell's new values equal that owner's corrected evidence values (so a mismatch either way fails);
  * evidence, archive_links and value_basis.csv are compared as multisets of whole rows against the merge-base: no existing row is
    deleted or edited, and the additions are exactly one evidence, one archive and one `stated` value_basis row per fill;
  * a `held` owner's cell, and any evidence of it, are unchanged;
  * each fill has a VERIFIED reading by a family other than Anthropic, a proof line whose claim digest matches its evidence row,
    and a capture that hashes to its name and holds the quote exactly once at the proof's offset, without an individual's email.
"""
import argparse
from collections import Counter
import copy
import csv
import hashlib
import io
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TASK = HERE.name
LABEL = f"claude-code {TASK}"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(HERE))
import build  # noqa: E402  (shared helpers: vocabulary, mail scan, Wayback pattern)
import check_evidence_binding as gate  # noqa: E402

HEAD = re.compile(r"Markets served: ([a-z0-9_]+) \(Wayback capture\); quote: (.+)", re.S)


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def table(blob):
    return list(csv.DictReader(io.StringIO(blob.decode(), newline="")))


def data_files(pattern):
    return sorted(p for p in git("ls-files", "data/").decode().split() if re.fullmatch(pattern, p))


def load(base, captures):
    s = {"captures": {}}
    for name, pat in (("orgs", r"data/organizations_[A-Z]+\.csv"), ("evidence", r"data/evidence_[A-Za-z_]+\.csv"),
                      ("archive", r"data/archive_links\.csv"), ("basis", r"data/value_basis\.csv")):
        s[name] = {"base": [], "work": []}
        for p in data_files(pat):
            s[name]["work"] += table((ROOT / p).read_bytes())
            s[name]["base"] += table(git("show", f"{base}:{p}"))
    for name in ("CANDIDATES", "READS", "BINDING_PROOF", "CLAIMS_CHECKED", "HELD"):
        s[name] = table((HERE / f"{name}.csv").read_bytes())
    s["INPUTS"] = [l.split("  ", 1) for l in (HERE / "INPUTS.sha256").read_text().splitlines() if l.strip()]
    for row in s["BINDING_PROOF"]:
        try:
            s["captures"][row["capture_sha256"]] = build.pinned(row["capture_sha256"], *captures)
        except FileNotFoundError:
            pass
    return s


def rowkey(r):
    return tuple(sorted(r.items()))


def delta(rows):
    """(removed, added) as multisets of whole rows: a deletion is a removed row alone, an edit a removed row plus an added one."""
    base, work = Counter(map(rowkey, rows["base"])), Counter(map(rowkey, rows["work"]))
    return [dict(k) for k in (base - work).elements()], [dict(k) for k in (work - base).elements()]


def problems(s):
    out = []
    say = out.append
    base_orgs = {r["org_id"]: r for r in s["orgs"]["base"]}
    work_orgs = {r["org_id"]: r for r in s["orgs"]["work"]}
    if set(base_orgs) != set(work_orgs):
        say("an organization row was added or removed")
    changed = {}
    for oid, w in work_orgs.items():
        cols = [c for c in w if w[c] != base_orgs.get(oid, {}).get(c)]
        if cols:
            changed[oid] = cols
    for oid, cols in changed.items():
        if cols != ["markets_served"]:
            say(f"{oid}: changed columns {cols}, not markets_served alone")
        if base_orgs[oid]["markets_served"].strip():
            say(f"{oid}: a held markets_served value was overwritten")
    ev_gone, ev_new = delta(s["evidence"])
    if ev_gone:
        say(f"{len(ev_gone)} existing evidence row(s) deleted or edited, e.g. {[e['evidence_id'] for e in ev_gone][:3]}")
    ev = {e["evidence_id"]: e for e in ev_new}
    if len(ev) != len(ev_new):
        say("a duplicate evidence_id among the added evidence rows")
    corrected = [c for c in s["CLAIMS_CHECKED"] if c["verdict"] == "corrected"]
    held = [c for c in s["CLAIMS_CHECKED"] if c["verdict"] == "held"]
    if any(c["table"] != "organizations" or c["field"] != "markets_served" for c in s["CLAIMS_CHECKED"]):
        say("a CLAIMS_CHECKED line is not organizations.markets_served")
    # the corrected rows equal the cells the PR changes
    if {c["record_id"] for c in corrected} != set(changed):
        say(f"corrected owners {sorted({c['record_id'] for c in corrected})} != changed cells {sorted(changed)}")
    values = {}
    for c in corrected:
        e = ev.get(c["evidence_id"])
        if not e or e["record_id"] != c["record_id"]:
            say(f"{c['record_id']}: corrected line cites {c['evidence_id']}, which is not an appended evidence row of that owner")
            continue
        m = HEAD.fullmatch(e["claim_detail"])
        if not m:
            say(f"{e['evidence_id']}: claim_detail is not the market grammar")
            continue
        values.setdefault(c["record_id"], set()).add(m[1])
    for oid in changed:
        have = {t for t in work_orgs[oid]["markets_served"].split(";") if t}
        if have != values.get(oid, set()):
            say(f"{oid}: cell {sorted(have)} != corrected evidence values {sorted(values.get(oid, set()))}")
    if len(ev) != len(corrected) or {e["created_by"] for e in ev_new} - {LABEL}:
        say("appended evidence is not one row of this label per corrected line")
    for e in ev_new:
        if (e["source_class"], e["claim_type"], e["tier_effect"], e["record_table"]) != ("own_site", "activity", "supports_B", "organizations"):
            say(f"{e['evidence_id']}: not an own_site activity supports_B organizations row")
    # held owners stay untouched
    for h in held:
        if h["record_id"] in changed or any(e["record_id"] == h["record_id"] for e in ev_new):
            say(f"{h['record_id']}: held owner has a changed cell or an appended evidence row")
    for h in s["HELD"]:
        if h["owner"] in changed:
            say(f"{h['owner']}: NOT_STATED in HELD.csv but its cell changed")
    # archive rows and value_basis: no existing row deleted or edited, and the additions are exactly the expected ones
    a_gone, a_new = delta(s["archive"])
    if a_gone:
        say(f"{len(a_gone)} existing archive_links row(s) deleted or edited, e.g. {[a['evidence_id'] for a in a_gone][:3]}")
    arch = {a["evidence_id"]: a for a in a_new}
    if set(arch) != set(ev) or len(a_new) != len(ev):
        say("archive_links lines are not one per appended evidence row")
    b_gone, b_new = delta(s["basis"])
    if b_gone:
        say(f"{len(b_gone)} existing value_basis row(s) deleted or edited, e.g. {[(b['record_id'], b['value']) for b in b_gone][:3]}")
    read_date = {p["evidence_id"]: p["reader_date"] for p in s["BINDING_PROOF"]}
    expected = []
    for c in corrected:
        e = ev.get(c["evidence_id"])
        m = HEAD.fullmatch(e["claim_detail"]) if e else None
        if m:
            expected.append(dict(record_table="organizations", record_id=c["record_id"], field="markets_served", value=m[1],
                                 basis="stated", evidence_id=c["evidence_id"], basis_date=read_date.get(c["evidence_id"], "")))
    if sorted(map(rowkey, b_new)) != sorted(map(rowkey, expected)):
        say(f"value_basis additions ({len(b_new)}) are not exactly the {len(expected)} `stated` lines for the corrected rows")
    # readings, proofs, captures
    reads = {(r["owner"], r["value"]): r for r in s["READS"]}
    proofs = {p["evidence_id"]: p for p in s["BINDING_PROOF"]}
    if set(proofs) != set(ev):
        say("BINDING_PROOF lines are not one per appended evidence row")
    vocab = build.market_vocabulary()
    for eid, e in ev.items():
        m, p = HEAD.fullmatch(e["claim_detail"]), proofs.get(eid)
        if not m or not p:
            continue
        value, quote = m[1], m[2]
        a, r = arch.get(eid, {}), reads.get((e["record_id"], value), {})
        if value not in vocab:
            say(f"{eid}: {value} is not a markets_served term")
        if r.get("verdict") != "VERIFIED" or p["verdict"] != "VERIFIED":
            say(f"{eid}: no VERIFIED reading in READS.csv and BINDING_PROOF.csv")
        if re.search(r"claude|anthropic", p["reader_family"], re.I) or not p["reader_family"].strip():
            say(f"{eid}: reader family {p['reader_family']!r} is not another family")
        if p["claim_sha256"] != gate.claim_sha256(e):
            say(f"{eid}: proof claim digest does not match the evidence row")
        wb = build.WAYBACK.fullmatch(p["capture"])
        if not wb or not gate.same_page(wb[5], e["source_ref"]) or f"{wb[1]}-{wb[2]}-{wb[3]}" != p["capture_date"]:
            say(f"{eid}: capture {p['capture']} is not a Wayback capture of {e['source_ref']} on its date")
        elif a.get("archive_ref") != p["capture"].replace("id_/", "/", 1) or a.get("captured_at") != p["capture_date"]:
            say(f"{eid}: archive_links line is not this capture")
        if p["reader_date"] < p["capture_date"]:
            say(f"{eid}: reading predates the capture")
        if not any(d == p["capture_sha256"] and path == f"provenance/{TASK}/captures/{d}.html" for d, path in s["INPUTS"]):
            say(f"{eid}: capture digest is not in INPUTS.sha256")
        data = s["captures"].get(p["capture_sha256"])
        if data is None:
            say(f"{eid}: the capture {p['capture_sha256'][:12]} is not in the store or --captures (not inspected)")
            continue
        text = gate.capture_text(data)
        if hashlib.sha256(data).hexdigest() != p["capture_sha256"]:
            say(f"{eid}: capture does not hash to its digest")
        if text.count(quote) != 1 or text.find(quote) != int(p["quote_offset"]):
            say(f"{eid}: quote is not once at offset {p['quote_offset']} in the capture")
        if len(" ".join(quote.split())) < 20:
            say(f"{eid}: quote shorter than 20 characters")
        if build.individual_mail(data):
            say(f"{eid}: capture holds an individual's email {build.individual_mail(data)}")
    if {d for d, _ in s["INPUTS"]} != {p["capture_sha256"] for p in s["BINDING_PROOF"]}:
        say("INPUTS.sha256 is not exactly the proofs' captures")
    return out


def plants(clean):
    """name -> mutated state; every one must make problems() non-empty."""
    def make(fn):
        s = copy.deepcopy(clean)
        fn(s)
        return s
    org = lambda s, oid: next(r for r in s["orgs"]["work"] if r["org_id"] == oid)
    first = lambda s: s["CLAIMS_CHECKED"][0]
    held_owner = lambda s: s["HELD"][0]["owner"]
    return {
        "a corrected line for a cell the PR does not change": lambda s: s["CLAIMS_CHECKED"].append(
            dict(table="organizations", record_id=held_owner(s), field="markets_served", verdict="corrected", evidence_id=first(s)["evidence_id"])),
        "a changed cell with no corrected line": lambda s: s["CLAIMS_CHECKED"].remove(next(c for c in s["CLAIMS_CHECKED"] if c["verdict"] == "corrected")),
        "a cell value that no evidence row names": lambda s: org(s, first(s)["record_id"]).update(markets_served=org(s, first(s)["record_id"])["markets_served"] + ";marine"),
        "a held owner's cell filled": lambda s: org(s, held_owner(s)).update(markets_served="plastics_rubber_processors"),
        "another organization column changed": lambda s: org(s, first(s)["record_id"]).update(processes="injection_molding"),
        "a quote that is not in the capture": lambda s: s["BINDING_PROOF"][0].update(quote_offset=str(int(s["BINDING_PROOF"][0]["quote_offset"]) + 1)),
        "a capture whose bytes differ": lambda s: s["captures"].update({s["BINDING_PROOF"][0]["capture_sha256"]: b"<html><p>other page</p></html>"}),
        "a reader of the builder's family": lambda s: s["BINDING_PROOF"][0].update(reader_family="Claude Sonnet 5.5"),
        "a reading that is not VERIFIED": lambda s: s["READS"][0].update(verdict="REJECT"),
        "an evidence claim edited after the reading": lambda s: next(e for e in s["evidence"]["work"] if e["evidence_id"] == s["BINDING_PROOF"][0]["evidence_id"]).update(
            claim_detail=next(e for e in s["evidence"]["work"] if e["evidence_id"] == s["BINDING_PROOF"][0]["evidence_id"])["claim_detail"] + " "),
        "a value outside the vocabulary": lambda s: next(e for e in s["evidence"]["work"] if e["evidence_id"] == s["BINDING_PROOF"][0]["evidence_id"]).update(
            claim_detail=re.sub(r"Markets served: [a-z_]+", "Markets served: made_up_market", next(e for e in s["evidence"]["work"] if e["evidence_id"] == s["BINDING_PROOF"][0]["evidence_id"])["claim_detail"])),
        "a missing archive line": lambda s: s["archive"]["work"].pop(),
        "an existing value_basis row deleted": lambda s: s["basis"]["work"].pop(0),
        "an existing value_basis row edited": lambda s: s["basis"]["work"][0].update(basis_date=s["basis"]["work"][0]["basis_date"] + "x"),
        "an extra value_basis row added": lambda s: s["basis"]["work"].append(dict(s["basis"]["work"][0], record_id=held_owner(s))),
        "an existing evidence row deleted": lambda s: s["evidence"]["work"].pop(0),
        "an existing evidence row edited": lambda s: s["evidence"]["work"][0].update(notes=s["evidence"]["work"][0]["notes"] + " x"),
        "an existing archive_links row deleted": lambda s: s["archive"]["work"].pop(0),
        "an existing archive_links row edited": lambda s: s["archive"]["work"][0].update(captured_at=s["archive"]["work"][0]["captured_at"] + "x"),
    }, make


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--captures", action="append", default=[])
    a = ap.parse_args()
    base = git("merge-base", "HEAD", "origin/main").decode().strip()
    clean = load(base, [*a.captures, build.STORE])
    found = problems(clean)
    print(f"clean tree: {len(found)} problem(s)")
    for p in found:
        print("  -", p)
    table_of_plants, make = plants(clean)
    missed = []
    for name, fn in table_of_plants.items():
        n = len(problems(make(fn)))
        print(f"plant {'caught' if n else 'MISSED'}: {name} ({n} problem(s))")
        if not n:
            missed.append(name)
    ok = not found and not missed
    print("PASS" if ok else "FAIL", f"({len(table_of_plants)} plants)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
