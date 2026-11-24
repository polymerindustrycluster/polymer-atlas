"""Check the map-listing street fills: every leg of the route, the cell delta, the ledger, and fifteen planted defects.

Run from the repository root with the Atlas shared store mounted: python3 -I tasks/pic18-map-streets-2026-11-24/check.py
The hold reasons in BASIS.csv are replayed only when the controller's measurement packets are present (see build.py).
"""
import copy
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(HERE))
import build  # noqa: E402  (its listing and capture helpers; this check re-derives every leg itself)
import check_evidence_binding as b  # noqa: E402
from regions import PIC18  # noqa: E402

BASE, SITES, EVIDENCE, STORE = build.BASE, build.SITES, build.EVIDENCE, build.STORE
CLAIM_FIELDS = ("table", "record_id", "field", "verdict", "evidence_id")
NOTES = re.compile(r"capture_sha256: ([0-9a-f]{64}); second_source: (EVD-\d+|lead: .+)")
REF = re.compile(r"overture-maps-places ([A-Za-z0-9_-]+)")
ALLOWED_DISPOSITIONS = {"FILLED", "HELD", "STATUS_LEAD"}


def csv_rows(text, header=None):
    reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
    if header:
        assert tuple(reader.fieldnames) == tuple(header), "wrong CSV header"
    data = list(reader)
    assert all(None not in r and None not in r.values() for r in data), "truncated or wide CSV row"
    return data


def keyed(rows, field):
    out = {r[field]: r for r in rows}
    assert len(out) == len(rows), f"duplicate {field}"
    return out


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def verify_fill(ev, capture, base_idx, evidence, store=None):
    """Assert every leg of the map-listing route for one evidence row; the gate's own verdict comes last."""
    site = base_idx.sites[ev["record_id"]]
    m = NOTES.fullmatch(ev["notes"])
    ref = REF.fullmatch(ev["source_ref"])
    assert m and ref, "row cites no capture digest, second source or Overture place"
    digest, second = m.groups()
    assert hashlib.sha256(capture).hexdigest() == digest, "capture sha256 does not match the cited digest"
    cap = json.loads(capture)
    props = cap["properties"]
    (addr,) = props["addresses"]
    assert cap["id"] == ref[1] and (cap["type"], props["theme"], props["type"]) == ("Feature", "places", "place")
    name, street, city = props["names"]["primary"], addr["freeform"], addr["locality"]
    state, zip_ = addr["region"].removeprefix("US-"), addr["postcode"]
    assert addr["country"] == "US" and state == "OH"
    assert props["operating_status"] not in build.OV_CLOSED, "listing shows closed: a status lead, never a fill"
    assert not any(s["dataset"].lower().startswith("google") for s in props["sources"]), "Google-derived Overture place"
    assert ev["claim_detail"] == f"{street}; quote: name: {name}; street: {street}; city: {city}; state: {state}"
    assert (ev["record_table"], ev["claim_type"], ev["source_class"]) == ("sites", "address", "platform_category")
    assert ev["tier_effect"] in {"supports_C", "supports_U"} and ev["address_role"] == "", "tier ceiling or address role"
    # operator and place
    keys = b.name_key(name)
    assert keys and keys in base_idx.held_keys("sites", site["site_id"]), "listing name is not a held name of the site"
    assert keys not in base_idx.parent_keys("sites", site["site_id"]), "listing names the parent, not the operator"
    assert b.squash(city) == b.squash(site["city"]) and site["state"] == "OH" and site["county"] in PIC18, "listing city or state differs from the site"
    assert site["operating_status"] == "active" and site["verification_tier"] in {"A", "B", "C"}
    # the cell and the street
    assert not (site["street_address"] or "").strip(), "base street is not blank: a fill never overwrites"
    assert b.physical_street(street) and not b.ADDRESS_RISK.search(street + " " + name), "not a physical street"
    assert not site["zip"].strip() or build.zip5(site["zip"]) == build.zip5(zip_), "listing ZIP differs from the held ZIP"
    # second source: independent origin, never a contradicts row, same street by script
    held = evidence.get(second)
    assert not (held and held["tier_effect"] == "contradicts"), "second source is a contradicts row"
    other, why = b.map_second_source(second, site, base_idx, evidence, "overture-maps-places")
    assert not why, f"second source rejected: {why}"
    assert b.physical_street(other) and b.same_street(street, other) and b.designators_compare(street, other) == "equal", \
        "listing street differs from the second source"
    # the gate, on the exact row (and its capture replay when the store is given)
    head = b.Index([dict(s, street_address=street) if s is site else s for s in base_idx.sites.values()],
                   base_idx.tables["organizations"].values())
    verdict, reason = b.map_listing_result(ev, base_idx, head, evidence, store)
    assert verdict == "PASS", f"binding gate: {reason}"


def verify_applied(site_street, capture):
    """The street written to the site shard equals the street the capture states."""
    (addr,) = json.loads(capture)["properties"]["addresses"]
    assert site_street == addr["freeform"], "applied street differs from the captured listing street"


def verify_inputs(lines, digest, store=STORE):
    """INPUTS.sha256 is exactly the two capture copies and one release part, each present and hashing to its digest."""
    entries = [line.split("  ", 1) for line in lines]
    assert all(len(e) == 2 for e in entries) and len(entries) == 3, "INPUTS.sha256 must hold three entries"
    capture_paths = {f"raw/overture/2026-11-18.0/{digest}.json", f"raw/map-listings/overture-maps-places/{digest}.json"}
    parts = [e for e in entries if e[1] not in capture_paths]
    assert {e[1] for e in entries} >= capture_paths and len(parts) == 1, "INPUTS.sha256 misses a capture or the release part"
    for want, path in entries:
        full = (store / path).resolve()
        assert path.startswith("raw/") and full.is_relative_to(store / "raw") and full.is_file(), f"missing input {path}"
        with full.open("rb") as stream:
            assert hashlib.file_digest(stream, "sha256").hexdigest() == want, f"digest mismatch for {path}"
    part = parts[0][1]
    assert part.startswith(f"{build.OVERTURE_RELEASE}/") and part.endswith(".parquet"), "not a release 2026-11-18.0 part"
    manifest = (store / "raw/MANIFEST.sha256").read_text().splitlines()
    assert f"{parts[0][0]}  ./{part.removeprefix('raw/')}" in manifest, "release part digest is not in the store MANIFEST.sha256"
    return store / part


def verify_ledger(claims, changed, fills, frame):
    """Corrected rows equal the changed cells; held rows are exactly the rest of the frame, full tuples."""
    got = sorted(tuple(r[k] for k in CLAIM_FIELDS) for r in claims)
    want = sorted([("sites", sid, col, "corrected", fills[sid]["evidence_id"]) for sid, col in changed]
                  + [("sites", sid, "street_address", "held", "") for sid in frame.keys() - fills.keys()])
    assert got == want, "claim ledger differs from the changed cells and the held frame"


def rejects(label, plant):
    try:
        plant()
    except (AssertionError, csv.Error) as e:  # a KeyError or ValueError would be a harness bug, not a rejection
        print(f"Rejected plant: {label}: {str(e)[:90]}")
    else:
        raise AssertionError(f"missed plant: {label}")


def planted_defects(ev, capture, base_idx, evidence):
    sid = ev["record_id"]
    base_sites = list(base_idx.sites.values())
    orgs = list(base_idx.tables["organizations"].values())

    def run(label, cap=None, row=None, site=None, extra_evidence=()):
        c = json.loads(capture)
        if cap:
            cap(c)
        body = json.dumps(c, separators=(",", ":"), sort_keys=True).encode()
        r = dict(ev)
        (a,) = c["properties"]["addresses"]
        quote = f"{a['freeform']}; quote: name: {c['properties']['names']['primary']}; street: {a['freeform']}; city: {a['locality']}; state: OH"
        r.update(claim_detail=quote, notes=f"capture_sha256: {hashlib.sha256(body).hexdigest()}; second_source: " + ev["notes"].partition("second_source: ")[2])
        if row:
            row(r, body)

        sites = [dict(s, **(site or {})) if s["site_id"] == sid else s for s in base_sites]
        evs = evidence | {e["evidence_id"]: e for e in extra_evidence}
        rejects(label, lambda: verify_fill(r, body, b.Index(sites, orgs), evs))

    def addr(**kv):
        return lambda c: c["properties"]["addresses"][0].update(kv)

    run("listing name differs from every held name", cap=lambda c: c["properties"]["names"].update(primary="Other Operator Inc"))
    run("listing in another city", cap=addr(locality="Cleveland"))
    run("listing street differs from the second source", cap=addr(freeform="63 N Summit St"))
    run("listing shows permanently closed", cap=lambda c: c["properties"].update(operating_status="permanently_closed"))
    run("PO box listing street", cap=addr(freeform="PO Box 62"))
    run("address role stated as mailing", row=lambda r, _: r.update(address_role="mailing"))
    run("listing ZIP differs from the held ZIP", site={"zip": "44301"})
    run("base street already held", site={"street_address": "62 N Summit St"})
    clause = "Street (per {}): 62 N Summit St"
    for label, origin in (("second source from the same provider", "Overture Maps"), ("second source of unknown origin", "unknown discovery")):
        second = "lead: " + clause.format(origin)
        run(label, site={"notes": clause.format(origin)},
            row=lambda r, _, s=second: r.update(notes=r["notes"].partition("second_source: ")[0] + "second_source: " + s))
    own = dict(evidence_id="EVD-999991", record_table="sites", record_id=sid, claim_type="address", source_class="own_site",
               claim_detail="site address; quote: Address 62 N Summit St, Akron, OH 44308", source_ref="https://akronpolysys.com/contact",
               observed_date="2026-11-24", tier_effect="supports_C", created_by="plant", notes="", address_role="")
    use = lambda r, _: r.update(notes=r["notes"].partition("second_source: ")[0] + "second_source: EVD-999991")
    # control: the same second source passes unless it contradicts, so the plant fails for the intended reason
    verify_fill(dict(ev, notes=ev["notes"].partition("second_source: ")[0] + "second_source: EVD-999991"), capture,
                base_idx, evidence | {own["evidence_id"]: own})
    run("second source is a contradicts row", row=use, extra_evidence=[dict(own, tier_effect="contradicts")])
    rejects("capture whose sha256 does not match", lambda: verify_fill(ev, capture + b" ", base_idx, evidence))


def main():
    prior = keyed(csv_rows(git("show", f"{BASE}:{SITES}").decode()), "site_id")
    head = keyed(csv_rows((ROOT / SITES).read_text()), "site_id")
    active = [r for r in prior.values() if r["state"] == "OH" and r["county"] in PIC18
              and r["operating_status"] == "active" and r["verification_tier"] in {"A", "B", "C"}]
    frame = {r["site_id"]: r for r in active if not r["street_address"].strip()}
    assert len(active) == 879 and len(frame) == 153, (len(active), len(frame))
    fills = keyed(csv_rows((HERE / "FILLS.csv").read_text()), "site_id")
    basis = keyed(csv_rows((HERE / "BASIS.csv").read_text()), "site_id")
    assert basis.keys() == frame.keys() and {r["disposition"] for r in basis.values()} <= ALLOWED_DISPOSITIONS
    assert {sid for sid, r in basis.items() if r["disposition"] == "FILLED"} == fills.keys() and fills
    assert all(basis[sid]["reason"] and basis[sid]["detail"] for sid in basis), "every frame site needs a reason"
    # cells: exactly the filled streets
    assert list(prior) == list(head), "site row count/ID/order changed"
    changed = sorted((sid, cell) for sid, before in prior.items() for cell, v in before.items() if head[sid][cell] != v)
    assert changed == sorted((sid, "street_address") for sid in fills), "changed cells differ from the fills"
    for sid, f in fills.items():
        assert head[sid]["street_address"] == f["street"] and head[sid]["zip"] == prior[sid]["zip"]
    # evidence rows: appended, sequential, nothing else under data/
    base_ev, new_ev = git("show", f"{BASE}:{EVIDENCE}"), (ROOT / EVIDENCE).read_bytes()
    assert new_ev.startswith(base_ev), "an existing evidence row or its order changed"
    added = csv_rows(base_ev.splitlines(keepends=True)[0].decode() + new_ev[len(base_ev):].decode())
    greatest = max(int(r["evidence_id"].split("-")[1]) for r in b.rows(BASE, "evidence_*.csv"))
    assert [int(r["evidence_id"].split("-")[1]) for r in added] == list(range(greatest + 1, greatest + 1 + len(fills)))
    assert set(git("diff", "--name-only", BASE, "--", "data/").decode().splitlines()) == {SITES, EVIDENCE}
    assert keyed(added, "record_id").keys() == fills.keys()
    # inputs: every cited capture is in the store at its digest, under both paths
    input_lines = (HERE / "INPUTS.sha256").read_text().splitlines()
    base_idx = b.Index.load(BASE)
    evidence = {e["evidence_id"]: e for e in b.rows(BASE, "evidence_*.csv")}
    controls = None
    for ev in added:
        f = fills[ev["record_id"]]
        digest = NOTES.fullmatch(ev["notes"])[1]
        assert digest == f["capture_sha256"] and ev["evidence_id"] == f["evidence_id"]
        capture = (STORE / f"raw/overture/2026-11-18.0/{digest}.json").read_bytes()
        assert capture == (STORE / f"raw/map-listings/overture-maps-places/{digest}.json").read_bytes()
        verify_fill(ev, capture, base_idx, evidence, STORE)
        verify_applied(head[ev["record_id"]]["street_address"], capture)
        part = verify_inputs(input_lines, digest)
        # replay the cited record from the pinned release part, not from the controller's packet
        assert build.capture_body(dict(provider="overture-maps-places", id=f["place_id"], lon=float(f["lon"]),
                                       lat=float(f["lat"])), part) == capture, "release record differs from the stored capture"
        controls = controls or (ev, capture, digest, head[ev["record_id"]]["street_address"])
    claims = csv_rows((HERE / "CLAIMS_CHECKED.csv").read_text(), CLAIM_FIELDS)
    verify_ledger(claims, changed, fills, frame)
    ev, capture, digest, street = controls
    rejects("applied street differs from the capture", lambda: verify_applied("999 Fictional Ave", capture))
    zeros = "0" * 64
    rejects("INPUTS.sha256 names a nonexistent part", lambda: verify_inputs([*input_lines[:2], f"{zeros}  raw/overture/nonexistent.parquet"], digest))
    rejects("INPUTS.sha256 digest wrong", lambda: verify_inputs([l.replace(digest, zeros, 1) if i == 0 else l for i, l in enumerate(input_lines)], digest))
    rejects("INPUTS.sha256 drops the release part", lambda: verify_inputs(input_lines[:2], digest))
    sid0 = sorted(frame.keys() - fills.keys())[0]
    for label, bad in (("held ledger row with the wrong table", ("organizations", sid0, "street_address", "held", "")),
                       ("held ledger row with an evidence ID", ("sites", sid0, "street_address", "held", "EVD-999999"))):
        mutated = [dict(zip(CLAIM_FIELDS, bad)) if r["record_id"] == sid0 else r for r in claims]
        rejects(label, lambda: verify_ledger(mutated, changed, fills, frame))
    planted_defects(ev, capture, base_idx, evidence)
    # hold reasons: replayed only when the packets are there
    if all(p.exists() for p in (build.OV_PARQUET, build.GOOGLE_RAW, build.CANDIDATES)):
        _, _, frame2, results, _ = build.evaluate()
        again, _ = build.tables(frame2, results)
        assert again == [dict(r) for r in csv.DictReader(open(HERE / "BASIS.csv"))], "BASIS.csv differs from a fresh replay"
        replay = "hold reasons replayed from the packets"
    else:
        replay = "NOT RUN: hold reasons not replayed (measurement packets absent)"
    print(f"PASS: {len(fills)} fill(s) through every leg and the binding gate, {len(changed)} changed cell(s), "
          f"{len(frame) - len(fills)} held or status-lead sites, {len(input_lines)} input hash(es); {replay}")


if __name__ == "__main__":
    main()
