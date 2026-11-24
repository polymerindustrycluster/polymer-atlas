"""Map-listing street fills (SCHEMA §4.13, v1.20.0): judge every blank-street PIC-18 site, then apply the fills.

Inputs outside the repo are the controller's measurement packets (read only) and the shared store's Overture release.
Usage: python3 -I build.py [--apply]   (without --apply it only writes the BASIS/FILLS/CLAIMS tables)
"""
import argparse
import collections
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
import check_evidence_binding as b  # noqa: E402
from regions import PIC18  # noqa: E402

BASE = (HERE / "BASE").read_text().strip()
SITES, EVIDENCE = "data/sites_OH.csv", "data/evidence_sites_OH.csv"
LABEL = f"claude-code {HERE.name}"
PACKETS = Path("/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist")
STORE = Path("/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store")
OV_PARQUET = PACKETS / "overture-pic18-2026-11-24/places_pic18_bbox.parquet"
GOOGLE_RAW = PACKETS / "google-places-pic18-2026-11-24/raw.jsonl"
CANDIDATES = PACKETS / "street-gaps-2026-11-24/candidates.csv"
DUCKDB = "/opt/homebrew/bin/duckdb"
OVERTURE_RELEASE = "raw/overture/2026-11-23-places/type=place"
OV_CLOSED = {"permanently_closed", "temporarily_closed", "closed"}
G_CLOSED = {"CLOSED_PERMANENTLY", "CLOSED_TEMPORARILY"}
# Judgment hold (not mechanical): the site's own note about this address is cut mid-sentence ("a different Olm...").
MANUAL_HOLDS = {"SITE-001824": "STILL_UNCERTAIN: the held note on the street is truncated ('a different Olm...'); "
                               "settled by the full text of verification wave 5 verdict W5-0064"}
ZIP5 = re.compile(r"\d{5}")


def zip5(value):
    m = ZIP5.match((value or "").strip())
    return m.group(0) if m else ""


def google_parts(formatted):
    """Parse 'street, City, ST 44092, USA' from the right, so a comma inside the street is kept."""
    parts = [p.strip() for p in formatted.split(",")]
    if len(parts) < 4 or parts[-1] != "USA":
        return None
    m = re.fullmatch(r"([A-Z]{2}) (\d{5})(?:-\d{4})?", parts[-2])
    return (", ".join(parts[:-3]), parts[-3], m[1], m[2]) if m else None


def load_listings():
    csv_text = subprocess.check_output([DUCKDB, "-csv", "-c",
        f"select id,name,street,city,zip,region,src,operating_status,confidence,lon,lat from '{OV_PARQUET}' "
        "where street is not null and region in ('OH','US-OH')"], text=True)
    overture = list(csv.DictReader(io.StringIO(csv_text)))
    google = {}
    for line in GOOGLE_RAW.read_text().splitlines():
        d = json.loads(line)
        google[d["site_id"]] = d["response"].get("places", [])
    return overture, google


def lead_clauses(site):
    notes = site.get("notes") or ""
    clauses = ["lead: " + c.strip() for c in re.split(r"[;\n]", notes)
               if re.fullmatch(r"Street \(per ([^()]+)\): (.+)", c.strip())]
    clauses += ["lead: " + m.group(0).rstrip() for m in b.HELD_FRS_LEAD.finditer(notes)]
    return clauses


def listing_row(site, listing, second):
    """The evidence row the route needs; the digest is filled in once the capture exists."""
    prov, pid, name, street, city, state = (listing[k] for k in ("provider", "id", "name", "street", "city", "state"))
    return dict(record_table="sites", record_id=site["site_id"], claim_type="address",
                claim_detail=f"{street}; quote: name: {name}; street: {street}; city: {city}; state: {state}",
                source_class="platform_category", source_ref=f"{prov} {pid}", tier_effect="supports_C",
                created_by=LABEL, address_role="", notes=f"capture_sha256: {{digest}}; second_source: {second}")


def listings_for(site, keys, parents, overture_by_city, google_places):
    out = []
    for r in overture_by_city.get(b.squash(site["city"]), []):
        k = b.name_key(r["name"] or "")
        if k in keys and k not in parents:
            out.append(dict(provider="overture-maps-places", id=r["id"], name=r["name"], street=r["street"], city=r["city"],
                            state=r["region"].removeprefix("US-"), zip=r["zip"], closed=r["operating_status"] in OV_CLOSED,
                            status=r["operating_status"] or "unstated", src=r["src"],
                            lon=float(r["lon"]), lat=float(r["lat"])))
    for p in google_places:
        parsed = google_parts(p.get("formattedAddress", ""))
        k = b.name_key(p["displayName"]["text"])
        if parsed and k in keys and k not in parents and b.squash(parsed[1]) == b.squash(site["city"]):
            out.append(dict(provider="google-places", id=p["id"], name=p["displayName"]["text"], street=parsed[0],
                            city=parsed[1], state=parsed[2], zip=parsed[3], closed=p.get("businessStatus") in G_CLOSED,
                            status=p.get("businessStatus", "unstated"), src="google"))
    return out


def judge_site(site, listings, base_idx, base_sites, orgs, evid_by_id, evid_by_site):
    """Return (disposition, reason, chosen listing, second source, detail) for one frame site."""
    sid = site["site_id"]
    if sid in MANUAL_HOLDS:
        return "HELD", "manual_hold", None, "", MANUAL_HOLDS[sid]
    if not listings:
        return "HELD", "no_listing_match", None, "", "no Overture or Google place with a held name in the site city"
    closed = [x for x in listings if x["closed"]]
    if closed:
        return "STATUS_LEAD", "listing_shows_closed", closed[0], "", \
            "; ".join(f"{x['provider']} {x['id']} {x['status']}" for x in closed) + " (status needs dated evidence, AGENTS §3)"
    first = listings[0]
    for x in listings[1:]:
        if not (b.same_street(first["street"], x["street"]) and b.designators_compare(first["street"], x["street"]) == "equal"):
            return "HELD", "listings_disagree", None, "", " | ".join(sorted({f"{x['provider']}: {x['street']}" for x in listings}))
    seconds = lead_clauses(site) + [e["evidence_id"] for e in evid_by_site[sid]
                                    if e["claim_type"] in ("address", "existence")]
    reasons = collections.Counter()
    for listing in sorted(listings, key=lambda x: (x["provider"] != "overture-maps-places", -len(x["id"]), x["id"])):
        head_sites = [dict(s, street_address=listing["street"]) if s["site_id"] == sid else s for s in base_sites]
        head = b.Index(head_sites, orgs)
        for second in seconds:
            row = listing_row(site, listing, second) | dict(evidence_id="EVD-999999", observed_date="2026-11-24")
            row["notes"] = row["notes"].format(digest="0" * 64)
            verdict, why = b.map_listing_result(row, base_idx, head, evid_by_id, None)
            ev = evid_by_id.get(second)
            if verdict == "PASS" and ev is not None and ev["tier_effect"] == "contradicts":
                verdict, why = "HELD", "second_source_is_contradicts_row"  # the gate does not check this
            if verdict == "PASS" and site["zip"].strip() and zip5(listing["zip"]) and zip5(site["zip"]) != zip5(listing["zip"]):
                verdict, why = "HELD", "listing_zip_differs_from_held_zip"  # stricter than the gate, which ignores ZIP
            if verdict == "PASS":
                return "FILLED", "listing_and_second_source_agree", listing, second, \
                    f"{listing['provider']} {listing['status']}, listing ZIP {listing['zip'] or 'none'}, held ZIP {site['zip'] or 'blank'}"
            reasons[why] += 1
    if not seconds:
        return "HELD", "no_second_source_held", None, "", "no 'Street (per <origin>)' clause, strong FRS note or own-site/filing evidence row on the site"
    top = reasons.most_common(1)[0][0] if reasons else "no_second_source_held"
    return "HELD", top, None, "", f"{sum(reasons.values())} listing/second-source pairs tried; reasons {dict(reasons)}"


def evaluate():
    base_idx = b.Index.load(BASE)
    evidence = b.rows(BASE, "evidence_*.csv")
    evid_by_id = {e["evidence_id"]: e for e in evidence}
    evid_by_site = collections.defaultdict(list)
    for e in evidence:
        if e["record_table"] == "sites":
            evid_by_site[e["record_id"]].append(e)
    base_sites, orgs = list(base_idx.sites.values()), list(base_idx.tables["organizations"].values())
    frame = {s["site_id"]: s for s in base_sites if s["state"] == "OH" and s["county"] in PIC18
             and s["operating_status"] == "active" and s["verification_tier"] in {"A", "B", "C"}
             and not (s["street_address"] or "").strip()}
    overture, google = load_listings()
    by_city = collections.defaultdict(list)
    for r in overture:
        by_city[b.squash(r["city"] or "")].append(r)
    cand_notes = collections.defaultdict(set)
    for r in csv.DictReader(open(CANDIDATES)):
        if r["source_family"] == "site notes":
            cand_notes[r["site_id"]].add(r["street"])
    results = {}
    for sid, site in sorted(frame.items()):
        keys, parents = base_idx.held_keys("sites", sid), base_idx.parent_keys("sites", sid)
        listings = listings_for(site, keys, parents, by_city, google.get(sid, []))
        res = judge_site(site, listings, base_idx, base_sites, orgs, evid_by_id, evid_by_site)
        note_agrees = bool(listings) and any(b.same_street(listings[0]["street"], s) for s in cand_notes[sid])
        results[sid] = res + (listings, note_agrees)
    return base_idx, evid_by_id, frame, results, overture


def tables(frame, results):
    basis, fills = [], []
    for sid, site in frame.items():
        disp, reason, listing, second, detail, listings, note_agrees = results[sid]
        if disp == "HELD" and reason in ("no_second_source_held", "map_second_source_unbound") and note_agrees:
            detail += "; a free-text note street agrees with the listing but is not a gate-accepted lead form"
        basis.append(dict(site_id=sid, tier=site["verification_tier"], city=site["city"], disposition=disp, reason=reason,
                          listings=" | ".join(f"{x['provider']} {x['id']} {x['street']} ({x['status']})" for x in listings),
                          second_source=second[:120], detail=detail))
        if disp == "FILLED":
            fills.append(dict(site_id=sid, provider=listing["provider"], place_id=listing["id"], name=listing["name"],
                              street=listing["street"], city=listing["city"], state=listing["state"], zip=listing["zip"],
                              lon=listing.get("lon", ""), lat=listing.get("lat", ""), second_source=second))
    return basis, fills


def capture_body(listing):
    """Project the cited Overture release record into the gate's capture shape (bytes)."""
    if listing["provider"] != "overture-maps-places":
        raise NotImplementedError("this packet cites no Google record")
    lon, lat = listing["lon"], listing["lat"]
    box = f"bbox.xmin between {lon - 0.001} and {lon + 0.001} and bbox.ymin between {lat - 0.001} and {lat + 0.001}"
    rec, = json.loads(subprocess.check_output([DUCKDB, "-json", "-c",
        f"select id, names.primary as name, addresses, operating_status, confidence, sources "
        f"from read_parquet('{STORE}/{OVERTURE_RELEASE}/*.parquet') where {box} and id='{listing['id']}'"]))
    addr, = rec["addresses"]
    return json.dumps({"type": "Feature", "id": rec["id"], "properties": {
        "theme": "places", "type": "place", "names": {"primary": rec["name"]}, "addresses": [addr],
        "operating_status": rec["operating_status"], "confidence": rec["confidence"], "sources": rec["sources"]}},
        separators=(",", ":"), sort_keys=True).encode()


def store_capture(listing):
    """Store the capture by SHA-256 under the brief's path and under the gate's --map-store path."""
    body = capture_body(listing)
    digest = hashlib.sha256(body).hexdigest()
    for rel in (f"raw/overture/2026-11-18.0/{digest}.json", f"raw/map-listings/overture-maps-places/{digest}.json"):
        path = STORE / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            assert path.read_bytes() == body, f"{rel} exists with other bytes"
        else:
            path.write_bytes(body)
    return digest


def write_csv(path, rows, fields=None):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fields or list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def encode(rows, header, ending):
    stream = io.StringIO(newline="")
    w = csv.DictWriter(stream, list(rows[0]), lineterminator=ending)
    if header:
        w.writeheader()
    w.writerows(rows)
    return stream.getvalue().encode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    _, _, frame, results, _ = evaluate()
    basis, fills = tables(frame, results)
    write_csv(HERE / "BASIS.csv", basis)
    print(collections.Counter((r["disposition"], r["reason"]) for r in basis))
    if not args.apply:
        return
    old_sites, old_ev = git("show", f"{BASE}:{SITES}"), git("show", f"{BASE}:{EVIDENCE}")
    ending = "\r\n" if b"\r\n" in old_sites else "\n"
    sites = list(csv.DictReader(io.StringIO(old_sites.decode(), newline="")))
    assert encode(sites, True, ending) == old_sites, "base site CSV does not round-trip"
    by_id = {s["site_id"]: s for s in sites}
    greatest = max(int(e["evidence_id"].split("-")[1]) for e in b.rows(BASE, "evidence_*.csv"))
    ev_rows, fill_out, claims = [], [], []
    for n, fill in enumerate(fills, start=1):
        listing = next(x for x in results[fill["site_id"]][5] if x["id"] == fill["place_id"])
        digest = store_capture(listing)
        row = listing_row(frame[fill["site_id"]], listing, fill["second_source"])
        row.update(evidence_id=f"EVD-{greatest + n:06d}", observed_date="2026-11-24",
                   notes=row["notes"].format(digest=digest))
        assert not by_id[fill["site_id"]]["street_address"].strip()
        by_id[fill["site_id"]]["street_address"] = fill["street"]
        ev_rows.append(row)
        fill_out.append(fill | dict(evidence_id=row["evidence_id"], capture_sha256=digest))
        claims.append(dict(table="sites", record_id=fill["site_id"], field="street_address", verdict="corrected",
                           evidence_id=row["evidence_id"]))
    claims += [dict(table="sites", record_id=sid, field="street_address", verdict="held", evidence_id="")
               for sid in frame if sid not in {f["site_id"] for f in fills}]
    write_csv(HERE / "CLAIMS_CHECKED.csv", sorted(claims, key=lambda r: (r["verdict"] != "corrected", r["record_id"])),
              ["table", "record_id", "field", "verdict", "evidence_id"])
    write_csv(HERE / "FILLS.csv", fill_out)
    header = old_ev.splitlines()[0].decode().split(",")
    ev_rows = [{k: r.get(k, "") for k in header} for r in ev_rows]
    ev_ending = "\r\n" if old_ev.endswith(b"\r\n") else "\n"
    assert old_ev.endswith(b"\n")
    (ROOT / SITES).write_bytes(encode(sites, True, ending))
    (ROOT / EVIDENCE).write_bytes(old_ev + encode(ev_rows, False, ev_ending))
    print(f"applied {len(fills)} fill(s)")


if __name__ == "__main__":
    main()
