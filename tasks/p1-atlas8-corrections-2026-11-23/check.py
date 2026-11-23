#!/usr/bin/env python3
"""Replay sealed P1 dispositions and check the complete canonical data delta."""
import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
import zipfile
from collections import Counter, defaultdict
from datetime import date
from itertools import islice
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKETS = Path.home() / ".bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist"
STORE = Path("/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store")
CLAIM_HEADER = ("table", "record_id", "field", "verdict", "evidence_id")
KEYS = {"organizations": "org_id", "sites": "site_id", "ecosystem": "org_id",
        "programs": "program_id", "people": "person_id"}
PROGRAM_FIELDS = (
    "institution_org_id program_name program_type credential_types level specialty_processes "
    "specialty_materials research_areas url public_door_url status unit_department city state county admissions_status"
).split()
READERS = {
    "read-418": (190, 4, 15),
    "read-pic18-other": (54, 6, 1),
    "read-progs-people": (157, 1, 26),
    "read-contradictions": (47, 3, 3),
    "read-claude-built": (152, 0, 42),
}
VERDICTS = ("VERIFIED", "REJECT", "STILL_UNCERTAIN")
ITA = "raw/osha/2026-11-22-archive-snapshot/raw/ita/"
ITA_2025 = ITA + "ITA_300A_Summary_Data_2025_partial.csv"
ITA_2022 = ITA + "ITA-data-cy2022.zip"
SAM = "raw/sam/2026-11-22-archive-snapshot/raw/SAM_PUBLIC_UTF-8_MONTHLY_V2_20261101_408dc50804f5434894ba3cc3ed4b914b.dat"
SAM_SITES = {"SITE-000037", "SITE-000592", "SITE-001611", "SITE-001723"}
TAG_REMOVALS = {
    "PROG-000362": {"research_areas": {"biomedical_polymers"}},
    "PROG-000377": {"research_areas": {"rheology", "polymer_physics"}},
    "PROG-000378": {"research_areas": {"composites_frp"}, "specialty_materials": {"composites_frp"}},
    "PROG-000384": {"research_areas": {"liquid_crystals", "characterization_methods", "polymer_physics"},
                    "specialty_materials": {"liquid_crystals"}},
}
# OSHA 300A record ordinals. Quotes use the held operator as printed in each filing.
ITA_ROWS = {
    "SITE-000133": (ITA_2025, "", 12459, "company_name"),
    "SITE-000336": (ITA_2025, "", 146939, "establishment_name"),
    "SITE-000677": (ITA_2025, "", 174584, "establishment_name"),
    "SITE-001438": (ITA_2022, "CY 2022.csv", 157028, "company_name"),
    "SITE-001484": (ITA_2025, "", 19284, "company_name"),
}
ADMISSION_HOLDS = {
    ("ecosystem", "ORG-000503", "polymer_program_name"): "V-16 requires the PROG-000014 rename and main cannot check programs evidence",
}


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def git(*argv):
    return subprocess.check_output(["git", *argv], cwd=ROOT)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def parse(data):
    return csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))


def key(row):
    return tuple(row[col] for col in CLAIM_HEADER[:3])


def unique(rows, key_fn, label):
    result = {}
    for row in rows:
        k = key_fn(row)
        require(k not in result, f"{label}: repeated key {k}")
        result[k] = row
    return result


def packet_path(name):
    return f"p1-{name}-2026-11-23/"


def sealed_inputs(manifest, directory):
    checked = set()
    for line in (HERE / manifest).read_text().splitlines():
        digest, path = line.split("  ", 1)
        require(path not in checked, f"{manifest}: repeated path")
        with (directory / path).open("rb") as stream:
            require(hashlib.file_digest(stream, "sha256").hexdigest() == digest, f"{path}: checksum mismatch")
        checked.add(path)
    require(checked, f"{manifest}: no inputs")
    return checked


def snapshot(ref):
    files = git("ls-tree", "-r", "--name-only", ref, "--", "data/").decode().splitlines()
    records, evidence = {}, {}
    for path in files:
        name = Path(path).stem
        table = name.split("_", 1)[0]
        if not path.endswith(".csv") or name.endswith("_all"):
            continue
        if name in KEYS or (table in {"organizations", "sites"} and re.fullmatch(r"[A-Z_]+", name.split("_", 1)[1])):
            for row in parse(git("show", f"{ref}:{path}")):
                k = (table, row[KEYS[table]])
                require(k not in records, f"{ref}: repeated record {k}")
                records[k] = (path, row)
        if name.startswith("evidence_"):
            for row in parse(git("show", f"{ref}:{path}")):
                eid = row["evidence_id"]
                require(eid not in evidence, f"{ref}: repeated evidence {eid}")
                evidence[eid] = row
    return records, evidence


def read_inputs(packets, records):
    files = sealed_inputs("PACKETS.sha256", packets)

    def load(name):
        require(name in files, f"unsealed input: {name}")
        return list(parse((packets / name).read_bytes()))

    frame = unique(load(packet_path("frames") + "frame8_cells.csv"), key, "ATLAS-8 frame")
    reads = defaultdict(list)
    claude_people = {}
    for name, expected in READERS.items():
        raw = load(packet_path(name) + "verdicts.csv")
        if name == "read-claude-built":
            other = load(packet_path(name) + "pic18-other/verdicts.csv")
            combined = {(key(row), row["verdict"], row["value_on_main_sha256"]) for row in raw}
            require(len(raw) == 220 and len(other) == 84 and all((key(row), row["verdict"], row["value_on_main_sha256"]) in combined for row in other),
                    "Claude-built combined file and PIC-18 subpacket differ")
            excluded = Counter(row["verdict"] for row in raw if row["frame_class"].startswith("9"))
            require(excluded == {"VERIFIED": 12, "REJECT": 6, "STILL_UNCERTAIN": 8}, "ATLAS-9 exclusion differs")
            raw = [row for row in raw if not row["frame_class"].startswith("9")]
            claude_people = unique([row for row in raw if row["table"] == "people"], key, name)
        require(Counter(row["verdict"] for row in raw) == Counter(dict(zip(VERDICTS, expected))),
                f"{name}: verdict counts differ")
        for k, row in unique(raw, key, name).items():
            _, record = records[k[:2]]
            if row["frame_class"] == "record_create":
                if k[0] == "programs":
                    value = "\n".join(f"{field}={record[field]}" for field in PROGRAM_FIELDS)
                else:
                    values = {field: v for field, v in record.items() if field != KEYS[k[0]] and v}
                    value = json.dumps(values, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
                require(any((k[0], k[1], field) in frame for field in record), f"{k}: record missing from frame")
            else:
                value = record[k[2]]
                if not row["frame_class"].startswith("DIFFERENT"):
                    require(k in frame and frame[k]["pr"] == row["pr"], f"{k}: packet/frame mismatch")
            require(sha(value.encode()) == row["value_on_main_sha256"], f"{k}: packet value drift")
            reads[k].append(row)
        print(f"{name}: reconciled {len(raw)} packet verdicts")

    people_fields = unique(load(packet_path("read-claude-built") + "people_fields.csv"), key, "Claude-built field detail")
    require(Counter(r["verdict"] for r in people_fields.values()) ==
            {"VERIFIED": 607, "STILL_UNCERTAIN": 189}, "Claude-built field totals differ")
    people_by_id = defaultdict(dict)
    for k, row in people_fields.items():
        v = records[k[:2]][1][k[2]]
        require(sha(v.encode()) == row["value_on_main_sha256"], f"{k}: people field drift")
        people_by_id[k[:2]][k[2]] = row["verdict"]
    for k, row in claude_people.items():
        fields = people_by_id[k[:2]]
        record = records[k[:2]][1]
        require(set(fields) == {f for f, v in record.items() if f != "person_id" and v}, f"{k}: incomplete field detail")
        world_facts = {v for f, v in fields.items() if f not in {"sources", "verification_tier", "last_verified"}}
        require((row["verdict"] == "VERIFIED") == (world_facts == {"VERIFIED"}), f"{k}: B8 record rollup differs")

    recompute = unique(load(packet_path("recompute") + "verdicts.csv"), key, "rule re-derivations")
    require(Counter(k[2] for k in recompute) == {"entity_type": 1016, "hq_in_scope": 391}, "rule totals differ")
    for k, r in recompute.items():
        require(k in frame and r["verdict"] == "verified"
                and r["value_on_main"] == r["rule_value"] == records[k[:2]][1][k[2]], f"{k}: rule replay drift")
        reads[k].append(dict(r, verdict="VERIFIED", capture_ref="", source_url="", quote=""))
    return reads, frame, recompute


def sam_filter(store, reads):
    sites_by_uei = {}
    for (_, rid, field), verdicts in reads.items():
        if rid in SAM_SITES and field == "street_address":
            match = re.search(r"\[uei=([A-Z0-9]{12})\]", verdicts[0]["capture_ref"])
            require(match is not None, f"{rid}: missing SAM key")
            sites_by_uei[match[1].encode()] = rid
    require(set(sites_by_uei.values()) == SAM_SITES, "SAM frame mismatch")
    result, dates = {}, {}
    with (store / SAM).open("rb") as stream:
        for line in stream:
            rid = sites_by_uei.get(line.split(b"|", 1)[0])
            if rid:
                fields = line.split(b"|")
                require(rid not in result and len(fields) >= 122, f"{rid}: ambiguous SAM row")
                updated = date.fromisoformat(fields[9].strip().decode("ascii"))
                result[rid] = updated >= date(2022, 4, 4) and fields[23].strip().upper() != b"Y" and b"D&B" not in fields[121].upper()
                dates[rid] = str(updated)
    require(result.keys() == SAM_SITES, "SAM lookup missed an assigned site")
    print("R-SAM", ", ".join(f"{rid} {dates[rid]} {'PASS' if result[rid] else 'HOLD'}" for rid in sorted(result)))
    return result


WITNESS_TYPES = {
    "legal_name": {"existence"}, "trade_names": {"existence"}, "ultimate_parent_name": {"parent"},
    "status": {"liveness"}, "status_date": {"liveness"}, "hq_city": {"address"}, "hq_county": {"address"},
    "street_address": {"address"}, "zip": {"address"}, "city": {"address"},
    "program_name": {"existence", "scope"}, "polymer_program_name": {"existence", "scope"},
}


def witness_terms(text):
    return " " + " ".join(re.findall(r"[\w]+", text.casefold())) + " "


def witness_id(rows, witnesses, record):
    fallback = ""
    for row in rows:
        candidates = [ev for ev in witnesses.get(key(row)[:2], ()) if ev["tier_effect"] != "contradicts"]
        field = row["field"]
        value = record.get(field, "")
        capture, source = row["capture_ref"], row["source_url"]
        explicit = set(re.findall(r"EVD-\d{6}", capture))
        if len(explicit) == 1:
            ids = [ev["evidence_id"] for ev in candidates if ev["evidence_id"] in explicit]
            if ids:
                return ids[0]
        locator = re.match(r"raw/.+?(?:@\d+|#TRIFD=[A-Z0-9]+| data row \d+)", capture)
        receipt = locator[0].replace(" data row ", "@") if locator else ""
        for ev in candidates:
            ref = ev["source_ref"]
            quote = " ".join(row["quote"].split())
            detail = " ".join(ev["claim_detail"].split())
            same_citation = bool(source and source == ref)
            exact_quote = bool(quote and quote in detail)
            stated_value = (value and ev["claim_type"] in WITNESS_TYPES.get(field, ())
                            and witness_terms(value) in witness_terms(detail))
            if (receipt and ref.endswith(receipt)) or (same_citation and exact_quote):
                return ev["evidence_id"]
            if same_citation and stated_value and not fallback:
                fallback = ev["evidence_id"]
    return fallback


def read_ita(store):
    result = {}
    for path, member in {(spec[0], spec[1]) for spec in ITA_ROWS.values()}:
        wanted = {n: rid for rid, (p, m, n, _) in ITA_ROWS.items() if (p, m) == (path, member)}
        with (zipfile.ZipFile(store / path).open(member) if member else (store / path).open("rb")) as raw:
            with io.TextIOWrapper(raw, encoding="utf-8-sig", newline="") as stream:
                for n, row in enumerate(islice(csv.DictReader(stream), max(wanted)), 1):
                    if n in wanted:
                        result[wanted[n]] = {k.lower(): v for k, v in row.items()}
    require(result.keys() == ITA_ROWS.keys(), "ITA packet locators did not all resolve")
    return result


def proposed_edits(reads, witnesses, records, store, first_id):
    sha_files = sealed_inputs("INPUTS.sha256", store)
    require(sha_files == {ITA_2022, ITA_2025, SAM}, "expected ITA and SAM inputs")
    sam = sam_filter(store, reads)
    ita = read_ita(store)
    corrections = {}
    for rid, (path, member, ordinal, name_field) in ITA_ROWS.items():
        raw = ita[rid]
        loc = f"{path}{'!' + member if member else ''}@{ordinal}"
        address = raw["street_address"]
        require(raw["state"] == "OH" and raw["year_filing_for"] in ("2022", "2025"), f"{rid}: wrong filing")
        packet = reads[("sites", rid, "street_address")]
        require(any((loc in r["capture_ref"] or f"{path} data row {ordinal}" in r["capture_ref"])
                    and address.lower().strip(".") in r["quote"].lower() for r in packet), f"{rid}: locator/quote mismatch")
        display_zip = raw["zip_code"][:5]
        evidence = {
            "evidence_id": f"EVD-{first_id + len(corrections):06d}",
            "record_table": "sites", "record_id": rid, "claim_type": "address",
            "claim_detail": f"physical site address; quote: {raw[name_field]}, {address}, {raw['city']}, {raw['state']} {display_zip}",
            "source_class": "government_filing", "source_ref": "OSHA ITA Form 300A; " + loc,
            "observed_date": raw["year_filing_for"] + "-12-31", "tier_effect": "supports_A",
            "created_by": f"codex {HERE.name}", "notes": "Replayed reader's filing on 2026-11-23.", "address_role": "physical",
        }
        # Use the street-only spelling from the primary reader. The independent
        # queue packets combine street, city and ZIP in their proposed value.
        value = next(r["correct_value"] for r in packet if not r["frame_class"].startswith("DIFFERENT"))
        require(value.casefold().rstrip(".") == address.casefold().strip().rstrip("."), f"{rid}: replacement differs from filing")
        corrections[rid] = (evidence, value, display_zip)

    claims, edits, holds = {}, {}, {}
    for k, rows in reads.items():
        table, rid, field = k
        votes = {r["verdict"] for r in rows}
        row = rows[0]
        if len(votes) != 1:
            holds[k] = "Reader disagreement (" + "/".join(sorted(votes)) + ")"
            continue
        if k in ADMISSION_HOLDS:
            require(votes == {"REJECT"}, f"{k}: stale gate hold")
            holds[k] = ADMISSION_HOLDS[k]
        elif table == "sites" and rid in SAM_SITES and not sam[rid] and "store:sam/" in row["capture_ref"]:
            holds[k] = "SAM-only witness failed R-SAM"
        elif votes == {"VERIFIED"}:
            claims[k] = ("verified", witness_id(rows, witnesses, records[k[:2]][1]))
        elif votes == {"STILL_UNCERTAIN"}:
            if table == "programs" and rid in TAG_REMOVALS:
                require(set(TAG_REMOVALS[rid]) <= set(field.split(";")), f"{k}: missing specialty verdict")
                record = records[k[:2]][1]
                for col, missing in TAG_REMOVALS[rid].items():
                    wanted = (table, rid, col)
                    old = re.split(r";\s*", record[col])
                    require(missing <= set(old), f"{wanted}: tag is already absent")
                    edits[wanted] = ";".join(tag for tag in old if tag not in missing)
                    claims[wanted] = ("withdrawn", "")
                if "credential_types" in field.split(";"):
                    holds[(table, rid, "credential_types")] = "Find a source for the M.S. and Ph.D. credentials at this program grain"
            else:
                holds[k] = "STILL_UNCERTAIN in sealed packet"
        elif votes == {"REJECT"}:
            if k == ("sites", "SITE-001579", "street_address"):
                require(row["correct_value"] == "549 E Washington Street", "S4 replacement differs")
                edits[k] = ""
                claims[k] = ("withdrawn", "")
                holds[k] = "Replacement awaits proof support for the S4 page; current street withdrawn"
            elif any(r["correct_value"] for r in rows):
                ev, street, zip5 = corrections[rid]
                if field == "zip":
                    require(row["correct_value"] == zip5, f"{k}: ZIP correction differs from filing")
                edits[k] = {"street_address": street, "zip": zip5}[field]
                claims[k] = ("corrected", ev["evidence_id"])
            else:
                edits[k] = ""
                claims[k] = ("withdrawn", "")
        else:
            raise SystemExit(f"{k}: unexpected verdict")
    require({eid for action, eid in claims.values() if action == "corrected"} ==
            {ev["evidence_id"] for ev, _, _ in corrections.values()}, "unclaimed correction witness")
    return claims, edits, holds, [ev for ev, _, _ in corrections.values()]


def csv_bytes(rows, header, with_header=True):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=header, lineterminator="\n")
    if with_header:
        writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode()


def expected_data(base, records, edits, new_evidence):
    by_path = defaultdict(lambda: defaultdict(dict))
    for k, value in edits.items():
        path, row = records[k[:2]]
        require(row[k[2]] != value, f"{k}: correction is a no-op")
        by_path[path][k[1]][k[2]] = value
    wanted = {}
    for path, by_id in by_path.items():
        old = git("show", f"{base}:{path}")
        lines = list(io.StringIO(old.decode(), newline=""))
        reader = parse(old)
        out = [lines[0].encode()]
        end = 1
        id_field = KEYS[Path(path).stem.split("_")[0]]
        seen = set()
        for row in reader:
            start, end = end, reader.line_num
            rid = row[id_field]
            if rid in by_id:
                seen.add(rid)
                row.update(by_id[rid])
                out.append(csv_bytes([row], reader.fieldnames, with_header=False))
            else:
                out.append("".join(lines[start:end]).encode())
        require(seen == by_id.keys(), f"{path}: missing corrected rows")
        wanted[path] = b"".join(out)
    path = "data/evidence_sites_OH.csv"
    old = git("show", f"{base}:{path}")
    require(old.endswith(b"\n"), "unexpected evidence shard terminator")
    wanted[path] = old + csv_bytes(new_evidence, parse(old).fieldnames, with_header=False)
    return wanted


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--packets", type=Path, default=PACKETS)
    ap.add_argument("--store", type=Path, default=STORE)
    ap.add_argument("--apply-backup", type=Path, help="apply from the merge base after backing up every edited shard")
    args = ap.parse_args()
    base = git("merge-base", "HEAD", "origin/main").decode().strip()
    records, evidence = snapshot(base)
    witnesses = defaultdict(list)
    for ev in evidence.values():
        witnesses[ev["record_table"], ev["record_id"]].append(ev)
    reads, frame, recompute = read_inputs(args.packets, records)
    # Allocation was obtained from atlas.py next-id against the application base.
    allocation = int((HERE / "FIRST_EVIDENCE_ID").read_text().strip().split("-")[1])
    require(allocation > max(int(eid.split("-")[1]) for eid in evidence), "evidence-ID allocation collides with base")
    claims, edits, holds, new_evidence = proposed_edits(reads, witnesses, records, args.store, allocation)
    claim_data = csv_bytes((dict(zip(CLAIM_HEADER, k + result)) for k, result in sorted(claims.items())), CLAIM_HEADER)
    queue_header = CLAIM_HEADER[:3] + ("reason",)
    queue_data = csv_bytes((dict(zip(queue_header, k + (reason,))) for k, reason in sorted(holds.items())), queue_header)
    expected = expected_data(base, records, edits, new_evidence)
    artifacts = {HERE / "CLAIMS_CHECKED.csv": claim_data, HERE / "OPEN_QUEUE.csv": queue_data}
    if args.apply_backup:
        args.apply_backup.mkdir(parents=True, exist_ok=True)
        for name in expected:
            original = git("show", f"{base}:{name}")
            require((ROOT / name).read_bytes() in (original, expected[name]), f"{name}: refusing to overwrite independent edits")
            backup = args.apply_backup / Path(name).name
            require(not backup.exists() or backup.read_bytes() == original, f"{name}: backup differs from base")
            backup.write_bytes(original)
        for name, content in ([(ROOT / name, value) for name, value in expected.items()] + list(artifacts.items())):
            pending = name.with_suffix(".pending")
            pending.write_bytes(content)
            pending.replace(name)
    for path, data in artifacts.items():
        require(path.read_bytes() == data, f"{path.name}: does not reconcile to sealed verdicts")
    changed = set(git("diff", "--name-only", base, "--", "data/").decode().splitlines())
    require(changed == expected.keys(), f"unexpected changed data files: {sorted(changed ^ expected.keys())}")
    for path, data in expected.items():
        require((ROOT / path).read_bytes() == data, f"{path}: data diff differs from replayed cells and appended evidence")
    record_regions = {(k[0], k[1]): r["region"] for k, r in frame.items()}
    for region in ("PIC-18", "Rest"):
        for is_rule in (False, True):
            counts = Counter(result[0] for k, result in claims.items()
                             if (k in recompute) == is_rule and record_regions.get(k[:2], "PIC-18") == region)
            print(region, "rule replay" if is_rule else "reader", dict(counts))
    print(f"PASS: {len(claims)} unique claim rows, {len(edits)} changed cells, "
          f"{len(new_evidence)} appended evidence rows, {len(holds)} open keys")


if __name__ == "__main__":
    main()
