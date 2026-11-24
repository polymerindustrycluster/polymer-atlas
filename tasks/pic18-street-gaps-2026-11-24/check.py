"""Check the canonical cell delta against the raw physical establishment filings."""
import csv
import hashlib
import io
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = (HERE / "BASE").read_text().strip()
SITES = "data/sites_OH.csv"
EVIDENCE = "data/evidence_sites_OH.csv"
CLAIM_FIELDS = ("table", "record_id", "field", "verdict", "evidence_id")
sys.path.insert(0, str(HERE.parent / "pic18-street-fill-2026-11-22"))
from check import raw_rows, W as earlier
from check_evidence_binding import Index, judge, rows as git_rows
from regions import PIC18

STORE = earlier.STORE
RISK = re.compile(r"\b(?:p\.?\s*o\.?\s*box|mail(?:ing)?|(?:registered|statutory) agent|registered office|"
                  r"apartment|apt|residence|home address)\b|@", re.I)


def csv_rows(text, header=None):
    reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
    if header:
        assert tuple(reader.fieldnames) == tuple(header), "wrong CSV header"
    data = list(reader)
    assert all(None not in row and None not in row.values() for row in data), "truncated or wide CSV row"
    return data


def keyed(rows, field):
    result = {r[field]: r for r in rows}
    assert len(result) == len(rows), f"duplicate {field}"
    return result


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def verify_addresses(fills, raw, rows, frame, head):
    idx = Index.load()
    evidence = keyed(rows, "record_id")
    assert set(evidence) == set(fills), "one address observation per filled site"
    expected = {}
    for sid, f in fills.items():
        e = evidence[sid]
        data = raw[f["ref"]]
        kind = f["kind"]
        if kind == "ita":
            assert f["operator_field"] in ("company_name", "establishment_name")
            keys = ("establishment_id", "street_address", "city", "state", "zip_code")
            day = f"{int(float(data['year_filing_for']))}-12-31"
            label = f"OSHA ITA Form 300A CY{day[:4]} establishment"
        else:
            assert kind == "inspection" and f["operator_field"] == "estab_name"
            keys = ("activity_nr", "site_address", "site_city", "site_state", "site_zip")
            day = data["open_date"][:10]
            label = "OSHA inspection"
        source_id, st, city, state, zp = (data[key].strip() for key in keys)
        name = data[f["operator_field"]].strip()
        assert state == "OH" and day and not RISK.search(st) and not RISK.search(name)
        assert (source_id, st, city, state, zp, day, name) == tuple(
            f[key] for key in ("source_id", "street", "city", "state", "zip", "date", "operator")
        ), f"{sid}: packet fields differ from raw witness"
        site = frame[sid]
        assert head[sid]["street_address"] == st, f"{sid}: street differs from the raw physical address"
        normalized_zip = zp[:5] if re.fullmatch(r"\d{5}(-?\d{4})?", zp) else ""
        expected_zip = site["zip"] or normalized_zip
        assert head[sid]["zip"] == expected_zip and f["zip_fill"] == ("" if site["zip"] else normalized_zip)
        expected[sid, "street_address"] = e["evidence_id"]
        if not site["zip"] and normalized_zip:
            expected[sid, "zip"] = e["evidence_id"]
        addr = f"{st}, {city}, OH {zp}"
        assert e["evidence_id"] == f["evidence_id"]
        assert (e["record_table"], e["claim_type"], e["address_role"]) == ("sites", "address", "physical")
        assert (e["source_class"], e["tier_effect"], e["observed_date"]) == ("government_filing", "supports_A", day)
        assert e["claim_detail"] == f"physical site street; quote: {name}, {addr}"
        assert e["source_ref"] == f"{label} {source_id}; {f['ref']}"
        assert e["created_by"] == "codex " + HERE.name and f"Filed operator field: {f['operator_field']}." in e["notes"]
        assert judge(e, idx)[0] == "PASS", f"{sid}: binding gate rejected the replay"
    return expected


def check_cells(base, head, expected):
    assert list(base) == list(head), "site row count/ID/order changed"
    assert list(next(iter(base.values()))) == list(next(iter(head.values()))), "site columns changed"
    changed = sorted((sid, cell) for sid, before in base.items()
                     for cell, value in before.items() if head[sid][cell] != value)
    assert changed == sorted(expected), "canonical changed cells differ from raw replay"
    return changed


def check_claims(claims, changed, expected, frame, filled):
    corrected = sorted(tuple(r[k] for k in CLAIM_FIELDS) for r in claims if r["verdict"] == "corrected")
    held = sorted(tuple(r[k] for k in CLAIM_FIELDS) for r in claims if r["verdict"] == "held")
    assert len(claims) == len(corrected) + len(held)
    assert corrected == sorted(("sites", sid, col, "corrected", expected[sid, col]) for sid, col in changed), (
        "corrected claims differ from actual changed cells, including multiplicity"
    )
    assert held == sorted(("sites", sid, "street_address", "held", "") for sid in frame.keys() - filled.keys())


def rejects(label, plant):
    try:
        plant()
    except (AssertionError, csv.Error):
        print(f"Rejected plant: {label}")
    else:
        raise AssertionError(f"missed plant: {label}")


def main():
    prior = keyed(csv_rows(git("show", f"{BASE}:{SITES}").decode()), "site_id")
    head = keyed(csv_rows((ROOT / SITES).read_text()), "site_id")
    active = [r for r in prior.values() if r["state"] == "OH" and r["county"] in PIC18
              and r["operating_status"] == "active" and r["verification_tier"] in {"A", "B", "C"}]
    frame = {r["site_id"]: r for r in active if not r["street_address"].strip()}
    assert len(active) == 879 and len(frame) == 155
    fills = keyed(csv_rows((HERE / "FILLS.csv").read_text()), "site_id")
    assert fills and fills.keys() <= frame.keys()
    basis = keyed(csv_rows((HERE / "BASIS.csv").read_text()), "site_id")
    assert len(basis) == 18 and basis.keys() <= frame.keys()
    assert {sid for sid, r in basis.items() if r["disposition"] == "PASS"} == fills.keys()
    locators = {f["ref"] for f in fills.values()}
    paths = {ref.split("!")[0].split("@")[0] for ref in locators}
    manifest = [line.split("  ", 1) for line in (HERE / "INPUTS.sha256").read_text().splitlines()]
    assert len(manifest) == len(paths) and {p for _, p in manifest} == paths
    for digest, path in manifest:
        assert path.startswith("raw/") and (STORE / path).resolve().is_relative_to(STORE / "raw")
        with (STORE / path).open("rb") as stream:
            assert hashlib.file_digest(stream, "sha256").hexdigest() == digest, path
    raw = raw_rows(STORE, locators)
    base_ev = git("show", f"{BASE}:{EVIDENCE}")
    new_ev = (ROOT / EVIDENCE).read_bytes()
    assert new_ev.startswith(base_ev), "an existing evidence row or its order changed"
    rows = csv_rows(base_ev.splitlines(keepends=True)[0].decode() + new_ev[len(base_ev):].decode())
    greatest = max(int(r["evidence_id"].split("-")[1]) for r in git_rows(BASE, "evidence_*.csv"))
    assert [int(r["evidence_id"].split("-")[1]) for r in rows] == list(range(greatest + 1, greatest + 1 + len(fills)))
    assert set(git("diff", "--name-only", BASE, "--", "data/").decode().splitlines()) == {SITES, EVIDENCE}
    expected = verify_addresses(fills, raw, rows, frame, head)
    changed = check_cells(prior, head, expected)
    claims_text = (HERE / "CLAIMS_CHECKED.csv").read_text()
    claims = csv_rows(claims_text, CLAIM_FIELDS)
    check_claims(claims, changed, expected, frame, fills)

    sid = next(iter(fills))
    wrong = head | {sid: dict(head[sid], street_address="100 Different Street")}
    rejects("wrong street", lambda: verify_addresses(fills, raw, rows, frame, wrong))
    for role, label in (("mailing", "mailing address"), ("agent", "registered-agent address")):
        rejected = [dict(rows[0], address_role=role), *rows[1:]]
        rejects(label, lambda: verify_addresses(fills, raw, rejected, frame, head))
    corrected = next(r for r in claims if r["verdict"] == "corrected")
    rejects("omission", lambda: check_claims([r for r in claims if r is not corrected], changed, expected, frame, fills))
    rejects("duplicate claim row", lambda: check_claims([*claims, corrected], changed, expected, frame, fills))
    rejects("truncated row", lambda: csv_rows(claims_text + "sites,SITE-000001,street_address,corrected\n", CLAIM_FIELDS))
    print(f"PASS: {len(fills)} raw physical witnesses and binding verdicts, {len(changed)} changed cells, "
          f"{len(frame) - len(fills)} held sites, {len(manifest)} input hashes")


if __name__ == "__main__":
    main()
