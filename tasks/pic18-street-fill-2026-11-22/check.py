#!/usr/bin/env python3
"""Replay the dated witnesses and verify the complete applied delta."""
import argparse
import csv
import hashlib
import io
import os
import subprocess
import zipfile
from collections import defaultdict
from pathlib import Path

import build as W
from matching import same_street, zip5
from atlas import street_key


def require(value, message):
    if not value:
        raise SystemExit(message)


def raw_rows(store, locators):
    files = defaultdict(set)
    for ref in locators:
        path, ordinal = ref.rsplit("@", 1)
        file, _, member = path.partition("!")
        files[(file, member)].add(int(ordinal))
    result = {}
    for (file, member), ordinals in files.items():
        path = store / file

        def scan(records):
            last = max(ordinals)
            for i, r in enumerate(records, 1):
                if i in ordinals:
                    ref = file + ("!" + member if member else "") + "@" + str(i)
                    result[ref] = r
                if i >= last:
                    break

        if "/sam/" in file:
            with path.open(encoding="utf-8-sig", newline="") as stream:
                scan((r for r in csv.reader(stream, delimiter="|", quoting=csv.QUOTE_NONE) if not r[0].startswith(("BOF ", "EOF "))))
        elif member:
            with zipfile.ZipFile(path) as archive, io.TextIOWrapper(
                archive.open(member), encoding="utf-8-sig", errors="replace", newline=""
            ) as stream:
                scan(({k.lower(): v for k, v in row.items()} for row in csv.DictReader(stream)))
        else:
            with path.open(encoding="utf-8-sig", errors="replace", newline="") as stream:
                scan(({k.lower(): v for k, v in row.items()} for row in csv.DictReader(stream)))
    missing = set(locators) - result.keys()
    require(not missing, "raw row locators did not resolve: " + ", ".join(sorted(missing)))
    return result


def replay(store, facts):
    locators = {r["ref"] for r in facts if r["kind"] != "permit"}
    locators.update(r["event_ref"] for r in facts if r["event_ref"])
    raw = raw_rows(store, locators)
    pdf_files = {W.ref_file(r["ref"]) for r in facts if r["kind"] == "permit"}
    pdf = {w["ref"]: w for w in W.permit_rows(store, pdf_files)} if pdf_files else {}
    witnesses, bands = {}, {}
    for f in facts:
        ref, kind = f["ref"], f["kind"]
        if kind in ("ita", "insp"):
            r = raw[ref]
            require(r["state" if kind == "ita" else "site_state"].strip().upper() == "OH", f"{ref}: OSHA state")
            entry, = W.B.unify([r], kind)
            w = W.witness(kind, ref, entry["names"], entry["st"], entry["city"], entry["zip"], W.B.source_date(entry))
            bands[ref] = W.B.band_of(W.B.count_of(entry))
        elif kind in W.EPA:
            r = raw[ref]
            key, name, street, city, zp, date_key = W.EPA[kind]
            state = {"frs": "fac_state", "rcra": "state_code", "air": "state", "npdes": "state_code"}[kind]
            require(r[state].strip().upper() == "OH", f"{ref}: EPA facility state")
            event_ref = f["event_ref"]
            event = raw[event_ref] if event_ref else {}
            require(event and event[key].strip() == r[key].strip(), f"{ref}: EPA event is for a different facility")
            w = W.witness(kind, ref, [r[name]], r[street], r[city], r[zp], W.dmy(event[date_key]), event_ref)
        elif kind == "sam":
            r = raw[ref]
            require(r[18].strip().upper() == "OH" and r[23].strip() != "Y" and r[121].strip() != "D&B", f"{ref}: SAM role/policy")
            street = " ".join(x.strip() for x in (r[15], r[16]) if x.strip())
            w = W.witness(kind, ref, [r[11], r[12]], street, r[17], zip5(r[19]), W.dmy(r[9]))
        elif kind in ("form5500", "form5500_sf"):
            r = raw[ref]
            _, _, name, alt, first, second, city, zp, d, _ = W.LAKE[kind]
            fields = [r[k.lower()] for k in (name, alt, first, second, city, zp, d)]
            n, a, st, line2, mun, z, dt = fields
            require(r[first.lower().replace("address1", "state")].strip().upper() == "OH", f"{ref}: Form 5500 location state")
            w = W.witness(kind, ref, [n, a], " ".join(x.strip() for x in (st, line2) if x.strip()),
                          mun, z, W.dmy(dt))
        else:
            w = pdf[ref]
        require(W.fact(w) == f, f"{ref}: raw data, source role or date differs from packet")
        witnesses[ref] = w
    return witnesses, bands


def hashes(store, facts):
    files = {W.ref_file(ref) for f in facts for ref in (f["ref"], f["event_ref"]) if ref}
    if any(f["kind"] == "permit" for f in facts):
        files.add("raw/permits-oh-air/2026-11-22/manifest.csv")
    manifest = W.inputs(store)
    declared = (W.HERE / "INPUTS.sha256").read_text()
    require(declared == "".join(f"{manifest[p[4:]]}  {p}\n" for p in sorted(files)), "input manifest coverage mismatch")
    for p in sorted(files):
        with (store / p).open("rb") as r:
            require(hashlib.file_digest(r, "sha256").hexdigest() == manifest[p[4:]], f"{p}: SHA-256 mismatch")
    return len(files)


def controls(idx, witnesses, occupied, accepted):
    w = witnesses[accepted["address_ref"]]
    require(W.street_decision([w], set())[0] == "eligible", "positive street control failed")
    changed = dict(w, street="99 Example Road")
    if same_street(changed["street"], w["street"]):
        changed["street"] = "98 Example Road"
    require(W.street_decision([w, changed], set())[0] == "dated_witnesses_disagree", "a different physical street passed")
    require(W.street_decision([w, dict(w, street=w["street"] + " Suite 8"),
                              dict(w, street=w["street"] + " Suite 9")], set())[0] == "dated_witnesses_disagree",
            "two competing unit numbers passed with an unspecified third witness")
    require(W.street_decision([dict(w, date="2021-11-21")], set())[0] == "no_current_held_witness", "stale source passed")
    require(W.street_decision([w], {street_key(w["street"])})[0] == "duplicate_site_lead", "occupied street passed")
    require(W.fact(changed) != W.fact(w), "raw-field replay missed the planted street")
    sid, oid = "TEST-SITE", "TEST-ORG"
    site = dict(site_id=sid, org_id=oid, site_name="Example Plastics - Akron", city="Akron", county="Summit")
    i = W.G.Index([site], [dict(org_id=oid, legal_name="Example Plastics", trade_names="", ultimate_parent_name="Parent Polymer")])
    require(not W.held_name(i, site, "Parent Polymer Inc."), "parent-only filing passed")
    print("Planted defects caught: other street, competing suites, stale date, duplicate key, raw street change, parent-only name.")


def expected_data(base, edits, evidence):
    path_sites = "data/sites_OH.csv"
    path_ev = "data/evidence_sites_OH.csv"

    def base_csv(path):
        content = subprocess.check_output(["git", "show", f"{base}:{path}"]).decode()
        return content, list(csv.DictReader(io.StringIO(content, newline="")))

    old_sites, site_rows = base_csv(path_sites)
    old_ev, e_rows = base_csv(path_ev)
    by_site = {r["site_id"]: r for r in site_rows}
    by_evidence = {(r["record_id"], r["claim_type"]): r for r in evidence}
    for edit in edits:
        s = by_site[edit["site_id"]]
        require(not s["street_address"].strip() and s["operating_status"] == "active", "base street changed or target inactive")
        s["street_address"] = edit["street_address"]
        if band := edit["employee_band_site"]:
            require(s["employee_band_site"] in ("", "unknown"), "existing site band would be overwritten")
            ev = by_evidence[(s["site_id"], "size_band")]
            s["employee_band_site"] = band
            note = f"BAND-SOURCE: employee_band_site={band} from {ev['source_ref'].split(';')[0]}, {ev['observed_date']} (government_filing)."
            s["notes"] = (s["notes"].rstrip() + " " if s["notes"].strip() else "") + note

    def render(content, rows, header=True):
        cooked = io.StringIO(newline="")
        nl = "\r\n" if "\r\n" in content else "\n"
        writer = csv.DictWriter(cooked, list(rows[0]), lineterminator=nl)
        if header:
            writer.writeheader()
        writer.writerows(rows)
        return cooked.getvalue().encode()

    previous_sites = list(csv.DictReader(io.StringIO(old_sites, newline="")))
    require(render(old_sites, previous_sites) == old_sites.encode(), "base site shard does not round-trip")
    require(old_ev.endswith("\n"), "evidence shard lacks a terminal line break")
    return {path_sites: (old_sites.encode(), render(old_sites, site_rows)),
            path_ev: (old_ev.encode(), old_ev.encode() + render(old_ev, evidence, header=False))}


def data_gate(base, edits, evs, apply, packet_only):
    expected = expected_data(base, edits, evs)
    mode = 0 if apply or packet_only else 1
    changed = set(subprocess.check_output(["git", "diff", "--name-only", base, "--", "data/"], text=True).splitlines())
    require(changed == (set() if mode == 0 else set(expected)), "canonical data scope differs from packet")
    for f, versions in expected.items():
        require(Path(f).read_bytes() == versions[mode], f"{f}: canonical bytes differ from expected")
    if apply:
        staged = []
        try:
            for f, versions in expected.items():
                path = Path(f)
                tmp = path.with_suffix(".street-fill.tmp")
                staged.append((tmp, path))
                with tmp.open("xb") as f:
                    f.write(versions[1])
                    f.flush()
                    os.fsync(f.fileno())
            for tmp, path in staged:
                os.replace(tmp, path)
        finally:
            for tmp, _ in staged:
                tmp.unlink(missing_ok=True)
        print("Applied the hash-replayed street and size packet.")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", required=True)
    ap.add_argument("--store", type=Path, default=W.STORE)
    ap.add_argument("--cache", type=Path, default=W.CACHE)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--packet-only", action="store_true")
    mode.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    files = ("frame.csv", "edits.csv", "evidence_rows.csv", "witnesses.csv")
    frame, edits, evs, facts = saved = tuple(W.B.rd(W.HERE / p) for p in files)
    first = int(evs[0]["evidence_id"].split("-")[1])
    idx = W.snapshot(a.base)
    old = W.G.rows(a.base, "evidence_*.csv")
    require(first > max(int(r["evidence_id"].split("-")[1]) for r in old), "evidence range is below the base maximum")
    actual = W.build(a.base, a.store, a.cache, first)
    for filename, rebuilt, persisted in zip(files, actual, saved):
        require([{k: str(v) for k, v in r.items()} for r in rebuilt] == persisted, filename + " differs from full-frame rebuild")
    by_site = {r["site_id"]: r for r in frame}
    require(len(frame) == len(by_site) == 121, "incorrect or duplicated site grain")
    prior = W.B.rd(W.HERE / "trial_comparison.csv")
    require(len(prior) == len({r["site_id"] for r in prior}) == 25 and
            all(r["current"] == by_site[r["site_id"]]["result"] for r in prior), "legacy sample comparison differs")
    n_hash = hashes(a.store, facts)
    witnesses, bands = replay(a.store, facts)
    accepted = [r for r in frame if r["result"] == "street_fill"]
    occupied = {street_key(s["street_address"]) for s in idx.sites.values() if s["street_address"]}
    controls(idx, witnesses, occupied, accepted[0])
    for row in accepted:
        curr = [witnesses[ref] for ref in row["current_witness_refs"].split("|")]
        require(W.street_decision(curr, occupied)[0] == "eligible", row["site_id"] + ": raw consensus failed")
        cell = next(r for r in edits if r["site_id"] == row["site_id"])
        idx.sites[row["site_id"]]["street_address"] = cell["street_address"]
    lookup = {r["site_id"]: r for r in accepted}
    for ev in evs:
        rid = ev["record_id"]
        row, size = lookup[rid], ev["claim_type"] == "size_band"
        ref = row["band_ref" if size else "address_ref"]
        w = witnesses[ref]
        site = idx.sites[rid]
        band = row["band"] if size else ""
        require(not size or band == bands[ref], f"{rid}: wrong raw band")
        expected = W.evidence(w, W.safe_name(idx, site, w), rid, band)
        expected["evidence_id"] = ev["evidence_id"]
        require(expected == ev and W.G.judge(ev, idx, _alone=True)[0] == "PASS", f"{rid}: raw quote or binding mismatch")
    print(f"Replayed {len(facts)} dated raw witnesses, {n_hash} hashes and {len(evs)} address/size evidence rows across 121 frame sites.")
    data_gate(a.base, edits, evs, a.apply, a.packet_only)


if __name__ == "__main__":
    main()
