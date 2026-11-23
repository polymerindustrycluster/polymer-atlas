#!/usr/bin/env python3
"""Ohio-only packet wrapper around the #468 matcher. Writes IDs and provenance, never raw text."""
import argparse
import csv
import io
import importlib.util
import hashlib
import random
import re
import runpy
import subprocess
from collections import Counter, defaultdict
from contextlib import nullcontext
from datetime import date
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
UPSTREAM = HERE.parent / "pic18-size-sprint-2026-11-22"
REGION = "ohio_outside_pic18"
SEED = 20261122
OSHA = {"ita": "ita_oh.csv", "insp": "insp_oh.csv"}
BY = "codex ohio-size-osha-2026-11-22"
EDITS = ("file", "row_id", "column", "old_sha256", "new_value", "edit_class", "rationale")
EVIDENCE = ("evidence_id", "record_table", "record_id", "claim_type", "claim_detail", "source_class",
            "source_ref", "observed_date", "tier_effect", "created_by", "notes", "address_role")
SNAPSHOT = "osha/2026-11-22-archive-snapshot/raw/"
FRAME = ("site_id", "org_id", "county", "verification_tier", "civic_street")
PACKET = ("site_id", "org_id", "source", "source_file", "file_sha256", "row_locator",
          "filing_year", "source_date", "band", "r13_source", "name_match",
          "adjacent_source_file", "adjacent_row_locator", "adjacent_source_date", "adjacent_band")
HOLDS = ("site_id", "org_id", "reason", "source_rows")
GENERIC = set("plant facility site location factory office warehouse headquarters distribution center manufacturing production".split())
ENTITY = re.compile(r"\b(?:inc(?:orporated)?|l\.?l\.?c\.?|corp(?:oration)?|ltd|limited|l\.?l\.?p\.?|l\.?p\.?)\b", re.I)
PROPRIETOR = re.compile(r"\b(?:sole proprietor(?:ship)?|individual(?: owner)?)\b", re.I)


def upstream(name):
    spec = importlib.util.spec_from_file_location(f"size468_{name}", UPSTREAM / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


B = upstream("build")


def operator_key(text):
    # Preserve non-corporate words (including "the") and collapse only ruled dotted forms.
    text = text.casefold()
    for dotted, plain in ((r"l\.l\.c\.?", "llc"), (r"l\.l\.p\.?", "llp"), (r"u\.s\.?", "us")):
        text = re.sub(rf"\b{dotted}(?!\w)", plain, text)
    words = re.findall(r"[^\W_]+|&", text)
    while words:
        if words[-1] in B.CORP:
            words.pop()
        elif words[-2:] == ["north", "america"]:
            del words[-2:]
        else:
            break
    return " ".join(words)


def generic_part(text):
    words = B.squash(text).split()
    return bool(words) and set(words) <= GENERIC


def site_key(text, city=""):
    # A city followed by a plant label still names a locality; keep the whole part.
    from atlas import LOCALITY_SEP_RE, TRAILING_PAREN_RE
    m = TRAILING_PAREN_RE.search(text)
    if m and generic_part(m[1]):
        text = text[:m.start()]
    parts = LOCALITY_SEP_RE.split(text)
    if len(parts) > 1 and generic_part(parts[-1]):
        text = " - ".join(parts[:-1])
    return operator_key(text)


B.name_key = operator_key
B.site_name_key = site_key
B.coll = lambda key: key


def held_names(site, orgs):
    held = B.org_names(orgs.get(site["org_id"], {"legal_name": ""}), orgs)
    for key in (operator_key(site["site_name"]), site_key(site["site_name"])):
        if key and not generic_part(key):
            held.setdefault(key, site["site_name"])
    return held


B.held_names = held_names


def open_snapshot(path, base=None, **kwargs):
    if not base:
        return open(path, **kwargs)
    relative = Path(path).resolve().relative_to(ROOT)
    content = subprocess.check_output(["git", "-C", str(ROOT), "show", f"{base}:{relative}"])
    return io.StringIO(content.decode("utf-8"), newline="")


def read(path, base=None):
    with open_snapshot(path, base, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_atlas(data, base):
    with patch.object(B, "open", lambda path, **kwargs: open_snapshot(path, base, **kwargs), create=True):
        return B.load_atlas(data)


def write(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def manifest(raw):
    return {"raw/" + path.removeprefix("./"): digest
            for line in (raw / "MANIFEST.sha256").read_text().splitlines()
            for digest, _, path in [line.partition("  ")]}


def raw_inputs(raw):
    paths = [raw / SNAPSHOT / "OSHA_inspection.zip"]
    paths.extend(p for p in (raw / SNAPSHOT / "ita").iterdir() if p.suffix in (".csv", ".zip"))
    return sorted("raw/" + str(path.relative_to(raw)) for path in paths)


def extract(raw, kind):
    """Run the #468 extractor with its CSV output in memory to avoid storing raw names."""
    target = raw / OSHA[kind]
    output = io.StringIO()

    def open_extract(path, mode="r", **kwargs):
        if mode == "w":
            if Path(path) != target:
                raise ValueError("unexpected extract output path")
            return nullcontext(output)
        return open(path, mode, **kwargs)

    command = [str(UPSTREAM / "extract_oh.py"), str(raw), str(raw), kind]
    with patch("sys.argv", command):
        runpy.run_path(command[0], init_globals={"open": open_extract})
    output.seek(0)
    return list(csv.DictReader(output))


def indexes(raw, cache=None):
    return {kind: B.index(B.unify(read(cache / filename) if cache else extract(raw, kind), kind))
            for kind, filename in OSHA.items()}


def context(orgs, sites):
    active = [s for s in sites if s["operating_status"] == "active"]
    by_street = defaultdict(list)
    for site in active:
        site["_held"] = held_names(site, orgs)
        by_street[B.street_key(site["street_address"])].append(site)
    return Counter(s["org_id"] for s in active), by_street


def private(name):
    if PROPRIETOR.search(name):
        return True
    # Corporate form alone does not rescue a natural-looking base name.
    return B.personal(operator_key(name))


def corporate_operator(site, orgs):
    org = orgs.get(site["org_id"], {})
    legal = org.get("legal_name", "")
    return (org.get("entity_type") != "sole_proprietor" and bool(ENTITY.search(legal))
            and not private(legal))


def valid_source_date(value):
    try:
        return B.CUTOFF <= date.fromisoformat(value).isoformat() == value <= "2026-11-22"
    except ValueError:
        return False


def source_row(entry):
    row = entry["r"]
    member = f"!{row['member']}" if row["member"] else ""
    return f"raw/{row['file']}{member}:{row['row']}"


def decide(site, orgs, ix, active_n, by_street):
    street = site["street_address"]
    if not street.strip():
        return "no_street", []
    if not B.same_street(street, street):
        return "street_not_civic", []
    held = site["_held"]
    pairs, notes = defaultdict(list), {}
    for kind in OSHA:
        pairs[kind], notes[kind] = B.classify(site, held, ix[kind])
    all_rows = [e for pair in pairs.values() for e, _, _ in pair]
    nearby = [e for note in notes.values() for _, e, _ in note]
    held_rows = [e for pair in pairs.values() for e, c, _ in pair if B.RANK[c] >= 2]
    if orgs.get(site["org_id"], {}).get("entity_type") == "sole_proprietor":
        return "individual_filer_redacted", all_rows + nearby
    near = {k: band for k, values in notes.items() if (band := B.would_be_band(k, values))}
    decision = B.evaluate(site, "suffix", pairs, active_n, by_street, near, notes)
    if decision[0] == "hold":
        return decision[1], all_rows + nearby
    if decision[0] == "none":
        if B.parent_lead_any(held, pairs):
            return "parent_name_lead", all_rows
        if nearby:
            return "street_or_locality_differs", nearby
        return ("name_not_held" if all_rows else "no_filing_at_street"), all_rows

    fill = decision[1]
    entry = fill["e"]
    raw_names = entry["names"]
    # A separately named corporate operator makes "operator + filing city" a branch label.
    locality = operator_key(entry["city"])
    legal = operator_key(orgs.get(site["org_id"], {}).get("legal_name", ""))
    form_confirmed = corporate_operator(site, orgs)
    labels = {locality}
    if locality and legal and form_confirmed and any(operator_key(n) == legal for n in raw_names):
        labels.update((f"{legal} {locality}", f"{locality} {legal}"))
    suspect = [n for n in raw_names if operator_key(n) not in labels and private(n)]
    if suspect or (private(fill["matched_name"]) and operator_key(fill["matched_name"]) not in labels):
        return "individual_filer_redacted", [entry]
    if not form_confirmed:
        return "business_entity_unconfirmed", [entry]

    selected = B.source_date(entry)
    if not valid_source_date(selected):
        return "filing_date_invalid_or_future", [entry]
    if any(B.source_date(e) > selected for e in held_rows if e["kind"] == entry["kind"]):
        return "later_same_source_requires_review", held_rows
    if any(B.source_date(e) > selected for e in nearby):
        return "superseded_by_later_filing", nearby
    if any(B.source_date(e) > selected for e in all_rows if e not in held_rows):
        return "later_filing_other_name", all_rows

    # The newest qualifying record within the lower-ranked series is an adjacent witness only.
    if entry["kind"] == "ita":
        alternatives = [t for t in pairs["insp"] if B.RANK[t[1]] >= 2 and valid_source_date(B.source_date(t[0]))]
        if alternatives:
            other = B.choose("insp", alternatives)
            if other[0] == "fill" and B.dist(fill["band"], other[1]["band"]) == 1:
                fill["adjacent"] = other[1]
    return "fill", fill


def locator(row):
    return f"{row['member']}|row={row['row']}|id={row['rid']}"


def products(selection, orgs, sites, ix, digests):
    active_n, by_street = context(orgs, sites)
    frame, packet, holds = [], [], []
    for site in selection:
        identity = {key: site[key] for key in ("site_id", "org_id")}
        street = site["street_address"]
        frame.append(dict(identity, county=site["county"], verification_tier=site["verification_tier"],
                          civic_street="yes" if B.same_street(street, street) else "no"))
        decision, data = decide(site, orgs, ix, active_n, by_street)
        if decision != "fill":
            holds.append(dict(identity, reason=decision, source_rows=";".join(sorted({source_row(e) for e in data}))))
            continue
        entry = data["e"]
        row = entry["r"]
        path = "raw/" + row["file"]
        record = dict.fromkeys(PACKET, "")
        record.update(identity, source=data["source"], source_file=path, file_sha256=digests[path],
                      row_locator=locator(row), filing_year=str(data["year"]), source_date=B.source_date(entry),
                      band=data["band"], r13_source=str(data["r13"]), name_match=data["name_match"])
        if adjacent := data.get("adjacent"):
            witness = adjacent["e"]
            record.update(adjacent_source_file="raw/" + witness["r"]["file"], adjacent_row_locator=locator(witness["r"]),
                          adjacent_source_date=B.source_date(witness), adjacent_band=adjacent["band"])
        packet.append(record)
    return frame, packet, holds


def application_rows(packet, sites, first_id):
    label = upstream("build_apply").label
    by_site = {s["site_id"]: s for s in sites}
    edits, evidence = [], []
    for offset, filing in enumerate(packet):
        sid = filing["site_id"]
        site = by_site[sid]
        if site["state"] != "OH" or site["employee_band_site"] not in ("", "unknown"):
            raise ValueError(f"{sid}: packet no longer targets a blank Ohio site band")
        lab, measure, ref, note = label(filing)
        extra = ""
        if filing["adjacent_band"]:
            extra = (f" Adjacent OSHA inspection band {filing['adjacent_band']} on "
                     f"{filing['adjacent_source_date']}; R13 ITA precedence.")
        new_note = f"BAND-SOURCE: employee_band_site={filing['band']} from {note}{extra}"
        existing = site["notes"]
        if re.search(r"@|\d{3}[-. ]\d{3}[-. ]\d{4}", existing):
            raise ValueError(f"{sid}: review retained notes before writing the edits file")
        for col, value, kind in (("employee_band_site", filing["band"], "BAND_SITE"),
                                 ("notes", (existing.rstrip() + " " if existing.strip() else "") + new_note,
                                  "BAND_SOURCE_NOTE")):
            edits.append(dict(file="sites_OH.csv", row_id=sid, column=col,
                              old_sha256=hashlib.sha256(site[col].encode()).hexdigest(),
                              new_value=value, edit_class=kind, rationale=f"R13; packet.csv row {offset + 2}"))
        evidence.append(dict(evidence_id=f"EVD-{first_id + offset:06d}", record_table="sites", record_id=sid,
                             claim_type="size_band", claim_detail=f"employee_band_site={filing['band']}: {lab}: "
                             f"{measure} in {filing['band']} (band only, not a headcount)",
                             source_class="government_filing", source_ref=ref, observed_date=filing["source_date"],
                             tier_effect="supports_B", created_by=BY,
                             notes=f"packet tasks/{HERE.name}/packet.csv row {offset + 2}; "
                             f"{filing['name_match']} name match at equal civic street; Ohio outside PIC-18." + extra,
                             address_role=""))
    return edits, evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--cache", type=Path, help="existing #468 extract for development; default extracts the verified raw snapshot")
    parser.add_argument("--out", type=Path, default=HERE)
    parser.add_argument("--canary", action="store_true")
    parser.add_argument("--base", help="read the pre-application repo snapshot by git ref")
    parser.add_argument("--first-evidence-id", type=int, help="integrator-allocated first ID for the proposed application")
    args = parser.parse_args()
    orgs, sites = load_atlas(args.data_dir, args.base)
    selection, n_org, n_unknown = B.frame(orgs, sites, REGION)
    if args.canary:
        civic = [s for s in selection if B.same_street(s["street_address"], s["street_address"])]
        selection = random.Random(SEED).sample(civic, 25)
    digests = manifest(args.raw)
    frame, packet, holds = products(selection, orgs, sites, indexes(args.raw, args.cache), digests)
    args.out.mkdir(parents=True, exist_ok=True)
    for name, fields, rows in (("frame", FRAME, frame), ("packet", PACKET, packet), ("holds", HOLDS, holds)):
        write(args.out / f"{name}.csv", fields, rows)
    (args.out / "INPUTS.sha256").write_text("".join(f"{digests[p]}  {p}\n" for p in raw_inputs(args.raw)))
    if args.first_evidence_id is not None:
        edits, evidence = application_rows(packet, sites, args.first_evidence_id)
        write(args.out / "edits.csv", EDITS, edits)
        write(args.out / "evidence_rows.csv", EVIDENCE, evidence)
    print(f"Outside PIC-18, {n_unknown}/{n_org} size-unknown organization rows; "
          f"{len(frame)} frame site rows, {len(packet)} filled, {len(holds)} held.")
    print(dict(Counter(p["source"] for p in packet)), dict(Counter(h["reason"] for h in holds)))


if __name__ == "__main__":
    main()
