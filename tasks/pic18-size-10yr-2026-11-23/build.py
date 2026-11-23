#!/usr/bin/env python3
"""Replay the original PIC-18 matcher with the dated ten-year R13 ruling."""
import argparse
import csv
import importlib.util
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPRINT = HERE.parent / "pic18-size-sprint-2026-11-22"
BASE = "7a9731f2881e8ed5cfc6bfb7b1121167505868d2"
DEFAULT_STORE = Path("/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store")
CUTOFF = "2016-11-23"
FIVE_YEARS = "2021-11-23"
OUTPUTS = ("packet.csv", "holds.csv", "evidence_rows.csv", "counts.json")
HOLD_FACTS = {
    "no_civic_street": "A primary source naming the operating civic street.",
    "no_filing_at_street": "A filing that names the operator and the recorded street.",
    "name_not_held": "Primary evidence connecting the filing establishment name to the operator.",
    "street_near_differs": "Primary evidence settling the differing street or locality.",
    "stale_over_10_years": "A qualifying dated filing on or after 2016-11-23.",
    "later_filing_other_name": "Primary evidence of the operator following the name change.",
    "filing_binds_two_sites": "A physical site identifier or record correction that resolves the shared address.",
    "ita_multiple_establishments_at_street": "A filing identifying which establishment is this site.",
    "newer_contradicting_filing": "The newer filing puts the same establishment in a different band.",
}
SOURCES = {"ita": "OSHA ITA Form 300A", "insp": "OSHA inspection"}

spec = importlib.util.spec_from_file_location("size_sprint", SPRINT / "build.py")
M = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(ROOT / "scripts"))
from check_evidence_binding import Index, judge

spec.loader.exec_module(M)


def filing_band(filing):
    return M.band_of(M.count_of(filing))


def decide(site, matches, active, streets, notes, cutoff=CUTOFF):
    """Keep the matcher, dropping only stale or superseded filings from candidacy."""
    M.CUTOFF = M.WINDOW_LO = cutoff
    qualified = [(e, M.source_date(e), filing_band(e)) for rows in matches.values() for e, rank, _ in rows
                 if M.RANK[rank] >= M.LEVELS["suffix"] and M.fresh(e) and filing_band(e)]
    latest_by_band = {}
    for e, date, band in sorted(qualified, key=lambda x: x[1]):
        latest_by_band[band] = e
    losers = []
    for e, date, band in qualified:
        newer = max((other for b, other in latest_by_band.items() if b != band),
                    key=M.source_date, default=None)
        if newer is not None and M.source_date(newer) > date:
            losers.append((e, newer))
    dropped = {id(e) for e, _ in losers}
    screened = {kind: [row for row in matches[kind] if id(row[0]) not in dropped] for kind in SOURCES}
    screened["f5500"] = []
    near = {kind: band for kind, rows in notes.items() if (band := M.would_be_band(kind, rows))}
    result = M.evaluate(site, "suffix", screened, active, streets, near, notes)
    if result[:2] == ("hold", "stale_over_5_years"):
        result = ("hold", "stale_over_10_years", f"No name-and-street filing on or after {cutoff}.")
    return result, losers


def source_locator(e):
    row = e["r"]
    return f"{row['member']}|row={row['row']}|id={row['rid']}"


def candidate(site, payload, manifest):
    e = payload["e"]
    kind = e["kind"]
    source = SOURCES[kind]
    row = e["r"]
    file = "raw/" + row["file"]
    date = M.source_date(e)
    year = str(payload["year"])
    band = payload["band"]
    quote = f"{e['names'][0]}, {e['st']}, {e['city']}, OH {e['zip']}"
    packet = dict(site_id=site["site_id"], org_id=site["org_id"], source=payload["source"], source_file=file,
                  file_sha256=manifest[file], row_locator=source_locator(e), filing_year=year,
                  source_date=date, band=band, name_match=payload["name_match"],
                  band_source_note=f"BAND-SOURCE: employee_band_site={band} from {source}, {date} (government_filing).")
    ev = dict(evidence_id="", record_table="sites", record_id=site["site_id"], claim_type="size_band",
              claim_detail=f"employee_band_site={band}; {source}, filing year {year}; quote: {quote}",
              source_class="government_filing", source_ref=f"{source}; {file}!{row['member']}@{row['row']}; id={row['rid']}",
              observed_date=date, tier_effect="supports_B", created_by="codex pic18-size-10yr-2026-11-23",
              notes="Retrieved from the 2026-11-22 Atlas raw snapshot.", address_role="")
    return packet, ev


def admit(site, result, manifest, binding):
    if result[0] != "fill":
        return None, result[1] if result[0] == "hold" else "no_eligible_filing"
    e = result[1]["e"]
    if M.personal(e["names"][0]):
        return None, "private_looking_filer"
    packet, ev = candidate(site, result[1], manifest)
    verdict, reason, _ = judge(ev, binding)
    if verdict != "PASS":
        return None, "binding_" + reason
    return (packet, ev), "eligible"


def index_filings(cache):
    indexes = {}
    for kind in SOURCES:
        rows = M.rd(cache / f"{kind}_oh.csv")
        if kind == "ita":
            # Keep company_name available for the sprint's shared-street ambiguity guard.
            # It never supplies the name that binds the filing.
            entries = [e for e in M.unify(rows, kind) if e["r"]["establishment_name"].strip()]
            for e in entries:
                e["names"] = [e["r"]["establishment_name"]]
        else:
            entries = [e for e in M.unify(rows, kind) if e["names"]]
        indexes[kind] = M.index(entries)
    return indexes


def comparison(site, matches, notes, active, streets, manifest, binding, start, stop):
    rows = {k: [t for t in v if start <= M.source_date(t[0]) < stop] for k, v in matches.items()}
    dated_notes = {k: [t for t in v if start <= M.source_date(t[1]) < stop] for k, v in notes.items()}
    result, _ = decide(site, rows, active, streets, dated_notes, start)
    fill, _ = admit(site, result, manifest, binding)
    return fill[0]["band"] if fill else None


def csv_out(path, rows, fields):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build(cache, data, out, manifest):
    orgs, sites = M.load_atlas(data)
    assert len({s["site_id"] for s in sites}) == len(sites), "duplicate Atlas site ID"
    known_org_ids = [r["org_id"] for f in sorted(data.glob("organizations_*.csv")) + [data / "ecosystem.csv"]
                     for r in M.rd(f)]
    assert len(set(known_org_ids)) == len(known_org_ids), "duplicate Atlas owner ID"
    frame, owners, unknown = M.frame(orgs, sites)
    frame_ids = {s["site_id"] for s in frame}
    assert (owners, unknown, len({s["org_id"] for s in frame})) == (794, 392, 392), "outcome frame mismatch"
    age_holds = [h for h in M.rd(SPRINT / "holds.csv") if h["reason"] == "stale_over_5_years"]
    age_ids = {h["site_id"] for h in age_holds}
    assert len(age_ids) == len(age_holds) == 26, "original age-only holds mismatch"
    prior = {r["site_id"] for r in M.rd(SPRINT / "packet.csv")}
    street_sprint = HERE.parent / "pic18-street-fill-2026-11-22"
    prior.update(e["record_id"] for e in M.rd(street_sprint / "evidence_rows.csv") if e["claim_type"] == "size_band")
    assert len(prior) == 55 and prior.isdisjoint(frame_ids), "prior OSHA fills overlap the unknown frame"

    active_sites = [s for s in sites if s["operating_status"] == "active"]
    active = Counter(s["org_id"] for s in active_sites)
    streets = defaultdict(list)
    for s in active_sites:
        if s["street_address"].strip():
            s["_held"] = M.held_names(s, orgs)
            streets[M.street_key(s["street_address"])].append(s)
    binding = Index(sites, orgs.values())
    indexes = index_filings(cache)
    packet, evidence, holds = [], [], []
    era_pairs = defaultdict(list)
    age_results, five, net_window, packet_owner_ids = Counter(), set(), set(), set()

    def hold(site, reason, **filing):
        fact = HOLD_FACTS.get(reason, "A clean, replayable filing that settles the recorded binding or count conflict.")
        holds.append(dict(site_id=site["site_id"], org_id=site["org_id"], reason=reason, settling_fact=fact,
                          scope="filing" if filing else "site", **filing))

    for s in sorted(sites, key=lambda row: row["site_id"]):
        sid, oid = s["site_id"], s["org_id"]
        in_scope = (
            s["state"] == "OH" and s["county"] in M.PIC18 and s["operating_status"] == "active"
            and s["verification_tier"] in ("A", "B", "C"))
        if not in_scope and sid not in age_ids:
            continue
        if not M.same_street(s["street_address"], s["street_address"]):
            disposition = "no_civic_street"
            if sid in frame_ids:
                hold(s, disposition)
            if sid in age_ids:
                age_results[disposition] += 1
            continue
        held = M.held_names(s, orgs)
        matches, notes = {}, {}
        for k, index in indexes.items():
            matches[k], notes[k] = M.classify(s, held, index)
        if sid in frame_ids or sid in age_ids:
            result, losers = decide(s, matches, active, streets, notes)
            fill, disposition = admit(s, result, manifest, binding)
            if disposition == "no_eligible_filing":
                if any(notes.values()):
                    disposition = "street_near_differs"
                else:
                    disposition = "name_not_held" if any(matches.values()) else "no_filing_at_street"
            if sid in age_ids:
                age_results[disposition if sid in frame_ids else "outside_current_frame:" + disposition] += 1
                if sid not in frame_ids:
                    hold(s, "outside_current_frame:" + disposition)
            if sid in frame_ids:
                if fill:
                    p, ev = fill
                    packet.append(p)
                    evidence.append(ev)
                    packet_owner_ids.add(oid)
                    if p["source_date"] < FIVE_YEARS:
                        net_window.add(oid)
                else:
                    hold(s, disposition)
                old_result, _ = decide(s, matches, active, streets, notes, FIVE_YEARS)
                if admit(s, old_result, manifest, binding)[0]:
                    five.add(oid)
                for rows in matches.values():
                    for e, rank, _ in rows:
                        if M.RANK[rank] >= M.LEVELS["suffix"] and M.source_date(e) < CUTOFF and filing_band(e):
                            hold(s, "stale_over_10_years", source_file="raw/" + e["r"]["file"],
                                 row_locator=source_locator(e), source_date=M.source_date(e), band=filing_band(e))
                for e, newer in losers:
                    hold(s, "newer_contradicting_filing", source_file="raw/" + e["r"]["file"],
                         row_locator=source_locator(e), source_date=M.source_date(e), band=filing_band(e),
                         newer_source_file="raw/" + newer["r"]["file"], newer_row_locator=source_locator(newer),
                         newer_source_date=M.source_date(newer), newer_band=filing_band(newer))
        if in_scope:
            old = comparison(s, matches, notes, active, streets, manifest, binding, "2016-01-01", "2021-01-01")
            recent = comparison(s, matches, notes, active, streets, manifest, binding, "2021-01-01", "2027-01-01")
            if old and recent:
                era_pairs[oid].append(M.dist(old, recent))

    assert sum(age_results.values()) == len(age_ids), "age-only holds not all retested"
    packet_ids = {p["site_id"] for p in packet}
    site_holds = {h["site_id"] for h in holds if h["scope"] == "site"}
    assert len(packet_ids) == len(packet) == len({e["record_id"] for e in evidence})
    assert packet_ids.isdisjoint(site_holds) and packet_ids | (site_holds & frame_ids) == frame_ids
    assert len({(p["source_file"], p["row_locator"]) for p in packet}) == len(packet), "filing binds twice"
    out.mkdir(parents=True, exist_ok=True)
    if not packet:
        raise AssertionError("no size candidates were inspected and admitted")
    csv_out(out / "packet.csv", packet, list(packet[0]))
    csv_out(out / "evidence_rows.csv", evidence, list(evidence[0]))
    csv_out(out / "holds.csv", holds, ["site_id", "org_id", "scope", "reason", "settling_fact", "source_file", "row_locator",
                                        "source_date", "band", "newer_source_file", "newer_row_locator", "newer_source_date", "newer_band"])
    counts = dict(base=BASE, pic18_owners=owners, unknown_size_owners=unknown, frame_sites=len(frame),
                  packet_sites=len(packet), packet_owners=len(packet_owner_ids),
                  packet_sites_by_source=dict(Counter(p["source"] for p in packet)),
                  packet_sites_by_filing_year=dict(sorted(Counter(p["filing_year"] for p in packet).items())),
                  current_frame_sites_held=len(site_holds & frame_ids),
                  site_holds_by_reason=dict(Counter(h["reason"] for h in holds if h["scope"] == "site")),
                  filing_holds_by_reason=dict(Counter(h["reason"] for h in holds if h["scope"] == "filing")),
                  age_only_site_retests=dict(age_results),
                  five_year_owners=len(five), added_by_window_owners=len(packet_owner_ids - five),
                  lost_by_window_owners=len(five - packet_owner_ids), pre_five_year_source_owners=len(net_window),
                  paired_owners=len(era_pairs), paired_sites=sum(map(len, era_pairs.values())),
                  agreeing_owners=sum(max(ds) == 0 for ds in era_pairs.values()),
                  within_one_band_owners=sum(max(ds) <= 1 for ds in era_pairs.values()))
    (out / "counts.json").write_text(json.dumps(counts, indent=2, sort_keys=True) + "\n")
    print(json.dumps(counts, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, default=DEFAULT_STORE)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    args = parser.parse_args()
    manifest = {path: digest for digest, path in (line.split("  ", 1)
                for line in (HERE / "INPUTS.sha256").read_text().splitlines())}
    assert (HERE / "INPUTS.sha256").read_bytes() == (SPRINT / "INPUTS.sha256").read_bytes()
    subprocess.run(["shasum", "-a", "256", "-c", str(HERE / "INPUTS.sha256")], cwd=args.store, check=True)
    # The inherited extractor enumerates the ITA directory. Fail if its inputs differ from the seal.
    ita_dir = args.store / "raw/osha/2026-11-22-archive-snapshot/raw/ita"
    assert {str(p.relative_to(args.store)) for p in ita_dir.iterdir() if p.suffix in (".csv", ".zip")} == {
        name for name in manifest if "/raw/ita/" in name}
    with TemporaryDirectory(prefix="atlas-size-cache-") as tmp:
        cache = Path(tmp)
        for kind in SOURCES:
            subprocess.run([sys.executable, "-I", str(SPRINT / "extract_oh.py"),
                            str(args.store / "raw"), tmp, kind], check=True)
        build(cache, args.data_dir, args.out, manifest)


if __name__ == "__main__":
    main()
