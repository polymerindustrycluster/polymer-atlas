#!/usr/bin/env python3
"""Replay G8 settlement decisions, witnesses, and the complete canonical diff."""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import date
import hashlib
import io
import zipfile
from pathlib import Path
import re
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "1600f540234aa9b8780309e0cc75db195c595daf"
LABEL = HERE.name
PACKET = Path.home() / ".bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist" / LABEL
STORE = Path("/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store")
CAPTURES = "provenance/pic18-settle-2026-11-23/captures"
SIBLING_CAPTURES = "provenance/pic18-settle-siblings-2026-11-23/captures"
OSHA_RAW = {
    "98012": "raw/osha/2026-11-22-archive-snapshot/raw/ita/ITA_300A_Summary_Data_2025_partial.csv",
    "118521": "raw/osha/2026-11-22-archive-snapshot/raw/ita/ITA_300A_Summary_Data_2024.zip",
    "1418310": "raw/osha/2026-11-22-archive-snapshot/raw/ita/ITA_300A_Summary_Data_2024.zip",
}
ECHO_RAW = "raw/echo/2026-11-22-archive-snapshot/raw/rcra_downloads.zip"
FRS_RAW = "raw/echo/2026-11-22-archive-snapshot/raw/frs_downloads.zip"
RAW_DOWNLOADS = {*OSHA_RAW.values(), ECHO_RAW, FRS_RAW}
REGISTRY = {
    "osha": "raw/osha/2026-11-22-archive-snapshot/out/ita_establishment_index.csv",
    "echo": "raw/echo/2026-11-22-archive-snapshot/out/echo_establishment_index.csv",
}
READ_PACKETS = {"read-a": ("queue_sonnet.csv", 105, 12, 28), "read-b": ("queue_gemini.csv", 116, 1, 33)}
PARTS = {
    "read-a/README.md", "read-a/verdicts.csv", "read-a/claude_built.csv",
    "read-b/README.md", "read-b/verdicts.csv", "read-b/claude_built.csv",
    "recite/README.md", "recite/actions.csv", "recite.scratch/actions_plain.csv",
    "recite.scratch/new_evidence_rows.csv", "recite.scratch/captures.csv",
    "queue_sonnet.csv", "queue_gemini.csv", "queue_recite.csv", "queue_recite_add.csv", "RULINGS.md",
}
CLAIMS = ("table", "record_id", "field", "verdict", "evidence_id")
QUEUE = (*CLAIMS[:3], "settling_fact")

base_replay = runpy.run_path(str(HERE.parent / "p1-atlas8-corrections-2026-11-23/check.py"))
git, parse, require, sha, unique, csv_bytes, snapshot = (
    base_replay[k] for k in ("git", "parse", "require", "sha", "unique", "csv_bytes", "snapshot")
)
quote_check = runpy.run_path(str(HERE / "replay_read_bodies.py"))
sys.path.insert(0, str(ROOT / "scripts"))
import check_evidence_binding as gate


def artifact(name, ref):
    f = HERE / name
    return git("show", f"{ref}:{f.relative_to(ROOT)}") if ref else f.read_bytes()


def hashes(blob):
    values = {}
    for line in blob.decode().splitlines():
        digest, path = line.split("  ", 1)
        require(path not in values and re.fullmatch(r"[0-9a-f]{64}", digest), "Duplicate path or malformed hash")
        values[path] = digest
    return values


def checked_packet(packet, ref):
    digests = hashes(artifact("PACKET.sha256", ref))
    require(digests.keys() == PARTS, "Packet input set differs")
    raw = {}
    for path, expected in digests.items():
        data = (packet / path).read_bytes()
        require(sha(data) == expected, f"{path}: packet hash mismatch")
        raw[path] = data
    return raw


def source_bodies(store, ref):
    digests = hashes(artifact("INPUTS.sha256", ref))
    registry_files = set(REGISTRY.values()) | RAW_DOWNLOADS
    capture_paths = digests.keys() - registry_files
    names = {r["filename"] for f in ("READ_BODIES.csv", "RECITE_BODIES.csv", "SIBLING_BODIES.csv") for r in parse(artifact(f, ref))}
    require(len(capture_paths) == len(names) and {Path(p).name for p in capture_paths} == names
            and registry_files <= digests.keys(), "Source capture or registry set differs")
    bodies = {}
    for path in capture_paths:
        name = Path(path).name
        require(path in {f"{folder}/{name}" for folder in (CAPTURES, SIBLING_CAPTURES)} and name == digests[path]+".body", "Noncanonical capture path")
        data = (store / path).read_bytes()
        require(sha(data) == digests[path], f"{name}: source body hash mismatch")
        bodies[name] = data
    return bodies, digests


def read_claims(raw, bodies, evidence, ref):
    mapping = unique(parse(artifact("READ_BODIES.csv", ref)), lambda r: (r["lane"], r["evidence_id"]), "reader capture map")
    normalized, verified, uncertain = {}, {}, {}
    for lane, (queue_file, v, u, l) in READ_PACKETS.items():
        queue = unique(parse(raw[queue_file]), lambda r: r["evidence_id"], f"{lane} queue")
        rows = unique(parse(raw[f"{lane}/verdicts.csv"]), lambda r: r["evidence_id"], f"{lane} verdicts")
        claude = unique(parse(raw[f"{lane}/claude_built.csv"]), lambda r: r["evidence_id"], f"{lane} Claude-built filter")
        require(queue.keys() == rows.keys() and not (rows.keys() & (verified.keys() | uncertain.keys()))
                and Counter(r["verdict"] for r in rows.values()) == {"VERIFIED": v, "STILL_UNCERTAIN": u}
                and claude.keys() <= rows.keys() and len(claude) == (0 if lane == "read-a" else 65),
                f"{lane}: assigned population or verdict count differs")
        require(sum(not r["capture_ref"].startswith("https://web.archive.org") for r in rows.values()) == l,
                f"{lane}: live route count differs")
        for eid, r in rows.items():
            require(evidence[eid]["record_id"] == r["record_id"], f"{eid}: reader record differs from main")
            location = mapping.pop((lane, eid), None)
            if r["verdict"] == "STILL_UNCERTAIN":
                uncertain[eid] = r
                if location is not None:
                    require(location["filename"] in bodies and location["verdict"] == r["verdict"]
                            and location["capture_route"] == "live" and not r["capture_ref"].startswith("https://web.archive.org"),
                            f"{eid}: unexpected held live capture")
                continue
            route = "archive" if r["capture_ref"].startswith("https://web.archive.org") else "live"
            require(location and location["verdict"] == r["verdict"] and location["capture_route"] == route,
                    f"{eid}: missing or wrong reader capture route")
            name = location["filename"]
            key = lane, name
            if key not in normalized:
                body_text = quote_check["text"](bodies[name], lane)
                normalized[key] = quote_check["fold"](body_text, lane)
            require(quote_check["quote_matches"](r["quote"], normalized[key], lane),
                    f"{eid}: accepted reader quote does not replay")
            verified[eid] = r
    require(not mapping and len(verified) == 221 and len(uncertain) == 13, "Reader coverage differs")
    return verified, uncertain


def registry_matches(plain, store, digests):
    by_source = defaultdict(dict)
    for eid, p in plain.items():
        if p["action"] == "RECITE" and p["gate_verdict"] == "PASS":
            by_source[p["store_file"]][eid] = (p["store_key"], p["quote"])
    require({k: len(v) for k, v in by_source.items()} == {"osha": 3, "echo": 3},
            "Static registry route split differs")
    for kind, targets in by_source.items():
        path = REGISTRY[kind]
        index = 13 if kind == "osha" else 7
        wanted = defaultdict(list)
        for eid, (key, quote) in targets.items():
            wanted[key].append((eid, quote))
        needed = [x.encode() for x in wanted]
        checksum = hashlib.sha256()
        found = set()
        with (store / path).open("rb") as stream:
            for line in stream:
                checksum.update(line)
                if not any(needle in line for needle in needed):
                    continue
                r = next(csv.reader([line.decode("utf-8", "replace")]))
                if len(r) <= index or r[index] not in wanted:
                    continue
                if kind == "osha":
                    raw_quotes = {f"{name}, {r[5]}, {r[6]}, {r[2]} {r[7]}" for name in (r[3], r[4])}
                elif r[0] == "RCRA":
                    raw_quotes = {f"{r[1]}; {r[2]}, {r[3]}, {r[4]} {r[5]}; FRS registry {r[6]}"}
                else:
                    continue
                for eid, quote in wanted[r[index]]:
                    if quote in raw_quotes:
                        found.add(eid)
        require(checksum.hexdigest() == digests[path] and found == targets.keys(),
                f"Registry store hash or witness coverage differs for {kind}")


def recite_claims(raw, bodies, evidence, uncertain, store, digests, ref):
    actions = unique(parse(raw["recite/actions.csv"]), lambda r: r["evidence_id"], "recite action")
    past = unique(parse(raw["queue_recite.csv"]), lambda r: r["evidence_id"], "initial recite queue")
    added = unique(parse(raw["queue_recite_add.csv"]), lambda r: r["evidence_id"], "reader holds moved to recite")
    require(len(past) == 43 and not past.keys() & added.keys() and added.keys() == uncertain.keys()
            and actions.keys() == past.keys() | added.keys() and
            Counter(r["action"] for r in actions.values()) ==
            {"RECITE": 7, "REJECT_VALUE": 1, "WITHDRAW": 27, "HOLD_FOR_CONTROLLER": 21},
            "Re-citation packet population or actions differ")
    plain = unique(parse(raw["recite.scratch/actions_plain.csv"]), lambda r: r["evidence_id"], "re-citation source detail")
    proposed = unique(parse(raw["recite.scratch/new_evidence_rows.csv"]), lambda r: r["replaces_evidence_id"],
                      "re-citation candidate witness")
    require({k for k, r in proposed.items() if r["status"] == "HOLD_FOR_CONTROLLER"} ==
            {"EVD-405007", "EVD-421581", "EVD-421582"}, "Press candidates must be held")
    candidates = {k: r for k, r in proposed.items() if r["status"] == "RECITE"}
    require(plain.keys() == actions.keys() and candidates.keys() ==
            {eid for eid, a in actions.items() if a["action"] == "RECITE"}, "Candidate evidence coverage differs")
    for eid, r in actions.items():
        p = plain[eid]
        require((r["record_id"], r["action"], r["capture_ref"]) ==
                (evidence[eid]["record_id"], p["action"], p["capture_ref"])
                and r["record_id"] == p["record_id"] and r["cell_action"] == p["cell_action"],
                f"{eid}: redacted versus source-detail discrepancy")
        if eid in candidates:
            ev = candidates[eid]
            require((ev["record_id"], ev["record_table"]) == (r["record_id"], evidence[eid]["record_table"])
                    and ev["claim_detail"] == p["new_claim_detail"] and ev["source_ref"] == p["new_source_ref"]
                    and ev["claim_type"] == r["claim_type"] and ev["source_class"] == r["source_class"]
                    and ev["claim_detail"].partition("quote:")[2].strip() == p["quote"],
                    f"{eid}: candidate observation does not match its packet")
    all_meta = unique(parse(raw["recite.scratch/captures.csv"]), lambda r: r["evidence_id"], "recite web source metadata")
    web = {eid for eid, a in actions.items() if a["action"] in {"RECITE", "REJECT_VALUE"}
           and a["capture_ref"].startswith("https://web.archive.org/")}
    meta = {eid: all_meta[eid] for eid in web}
    mapping = unique(parse(artifact("RECITE_BODIES.csv", ref)), lambda r: r["evidence_id"], "recite capture map")
    require(meta.keys() == mapping.keys() == {"EVD-421209", "EVD-425423"},
            "Recite web capture coverage differs")
    for eid, m in meta.items():
        row = mapping[eid]
        require(all(row[f] == m[f] for f in m) and row["filename"] == m["capture_sha256"]+".body"
                and m["capture_ref"] == plain[eid]["capture_ref"], f"{eid}: source capture pointer differs")
        t = gate.capture_text(bodies[row["filename"]])
        q = plain[eid]["quote"]
        i = int(m["quote_offset"])
        require(i >= 0 and t[i:i+len(q)] == q, f"{eid}: capture does not carry the proposed quote")
    return actions, plain, candidates, meta


def mint_recitations(evidence, records, actions, candidates, meta, bodies, ref):
    """Allocate and bind the approved recitations without editing their prior rows."""
    idx = gate.Index.load(BASE)
    approved = {eid for eid, a in actions.items() if a["action"] == "RECITE" and a["gate_verdict"] == "PASS"}
    approved.add("EVD-421209")
    readers = unique(parse(artifact("WEB_READ.csv", ref)), lambda r: r["evidence_id"], "web reader")
    require(readers.keys() == {"EVD-421209", "EVD-425423"} and approved <= candidates.keys(), "Approved recitation set differs")
    eid_next = max(int(e.split("-")[1]) for e in evidence)+1
    new_evs, archives, proofs, linked = defaultdict(list), [], [], {}
    for old_id, p in candidates.items():
        if old_id not in approved:
            continue
        eid = f"EVD-{eid_next+len(linked):06d}"
        table, rid = p["record_table"], p["record_id"]
        path, _ = records[table, rid]
        destination = {
            "sites": lambda: path.replace("data/sites_", "data/evidence_sites_", 1),
            "organizations": lambda: path.replace("data/organizations_", "data/evidence_organizations_", 1),
        }[table]()
        new = dict(p)
        del new["replaces_evidence_id"], new["capture_ref"], new["status"]
        raw_source = OSHA_RAW.get(re.search(r"id (\d+)$", new["source_ref"])[1]) if new["source_class"] == "government_filing" else ECHO_RAW
        new.update(evidence_id=eid, created_by=LABEL,
                   notes=f"Re-cites the claim previously witnessed by {old_id}." + (f" Raw download {raw_source}." if old_id != "EVD-421209" else ""),
                   address_role="physical" if new["claim_type"] == "address" else "")
        quote = new["claim_detail"].partition("quote:")[2].strip()
        require(quote and not re.search(r"[\w.+-]+@[\w.-]+|\d{3}[-. ]\d{3}[-. ]\d{4}", quote),
                f"{old_id}: contact detail in selected quote")
        if old_id == "EVD-421209":
            m = meta[old_id]
            read = readers[old_id]
            require(read["verdict"] == "VERIFIED" and
                    (read["capture_sha256"], read["quote_offset"]) == (m["capture_sha256"], m["quote_offset"]) and
                    gate.family_of_text(read["reader_family"]) == "google",
                    f"{old_id}: independent exact-source read differs")
            cap = m["capture_ref"]
            a = gate.ARCHIVE_RE.fullmatch(cap)
            require(a and a[2] and a[3] == new["source_ref"], f"{old_id}: archive source identity differs")
            stamp = a[1]
            captured_at = date(int(stamp[:4]), int(stamp[4:6]), int(stamp[6:8])).isoformat()
            previous = [a for a in parse(git("show", f"{BASE}:data/archive_links.csv"))
                        if a["evidence_id"] == "EVD-483046"]
            require(len(previous) == 1 and previous[0]["archive_ref"] == cap.replace(f"{stamp}id_/", f"{stamp}/", 1)
                    and previous[0]["captured_at"] == captured_at and previous[0]["created_by"] == "unknown",
                    f"{old_id}: reusable archive attribution differs")
            archive = dict(previous[0], evidence_id=eid)
            new["claim_detail"] = f"{new['claim_detail'].partition('quote:')[0].strip().rstrip(';')} (Wayback capture); quote: {quote}"
            proof = dict(zip(gate.PROOF_COLS, (eid, rid, gate.claim_sha256(new), cap, captured_at,
                                             m["capture_sha256"], m["quote_offset"], read["verdict"],
                                             read["reader_family"], read["reader_date"])))
            require(gate.judge(new, idx)[:2] == ("READ_REQUIRED", "mechanics_clear") and
                    not gate.proof_problem(proof, new, idx, idx, archive, date.fromisoformat(new["observed_date"]),
                                           "openai", lambda url: bodies[m["capture_sha256"]+".body"]),
                    f"{old_id}: own-site web proof fails")
            proofs.append(proof)
            archives.append(archive)
        else:
            require(gate.judge(new, idx)[0] == "PASS", f"{old_id}: structured binding fails on merged base")
        new_evs[destination].append(new)
        linked[old_id] = eid
    require(len(linked) == 7 and len(proofs) == len(archives) == 1, "Recitation output coverage differs")
    return new_evs, archives, proofs, linked


def data_delta(records, changes, new_evs, archives, inclusions, moved):
    """Write checked cells and optional HQ moves while retaining every other CSV line."""
    by_path = defaultdict(lambda: defaultdict(dict))
    for (table, rid, field), value in changes.items():
        path, row = records[table, rid]
        require(row[field] != value, f"{rid}/{field}: selected edit is a no-op")
        by_path[path][rid][field] = value
    exports = defaultdict(dict)
    for rid, path in moved.items():
        before_path, row = records["organizations", rid]
        require(before_path in by_path and rid in by_path[before_path] and path != before_path,
                f"{rid}: expected cross-shard correction")
        exports[path][rid] = dict(row, **by_path[before_path][rid])
        by_path.setdefault(path, {})
    out = {}
    for path, edits in by_path.items():
        original = git("show", f"{BASE}:{path}")
        lines = list(io.StringIO(original.decode(), newline=""))
        rd = parse(original)
        fields = rd.fieldnames
        id_col = base_replay["KEYS"][Path(path).stem.split("_")[0]]
        parts, seen, end = [lines[0].encode()], set(), 1
        incoming = iter(sorted(exports[path].items()))
        insert = next(incoming, None)
        for row in rd:
            start, end = end, rd.line_num
            rid = row[id_col]
            while insert and insert[0] < rid:
                parts.append(csv_bytes([insert[1]], fields, with_header=False))
                insert = next(incoming, None)
            require(rid not in exports[path], f"{rid}: record already in destination shard")
            if rid in edits:
                seen.add(rid)
                if rid not in moved:
                    row.update(edits[rid])
                    parts.append(csv_bytes([row], fields, with_header=False))
            else:
                parts.append("".join(lines[start:end]).encode())
        if insert:
            parts.append(csv_bytes([insert[1], *(v for _, v in incoming)], fields, with_header=False))
        require(seen == edits.keys(), f"{path}: edited record missing")
        out[path] = b"".join(parts)
    append = {**new_evs, "data/archive_links.csv": archives, "data/inclusion_log.csv": inclusions}
    for path, rows in append.items():
        original = git("show", f"{BASE}:{path}")
        require(original.endswith(b"\n"), f"{path}: append would run into last line")
        out[path] = original + csv_bytes(rows, parse(original).fieldnames, with_header=False)
    return out


def raw_download_matches(plain, store, digests):
    """Trace each cited index row back to its checked original download."""
    from contextlib import ExitStack

    groups = defaultdict(dict)
    for eid, p in plain.items():
        if p["action"] == "RECITE" and p["gate_verdict"] == "PASS":
            kind, key = p["store_file"], p["store_key"]
            path = OSHA_RAW[key] if kind == "osha" else ECHO_RAW
            groups[path][key] = p["quote"]
    require(groups.keys() == RAW_DOWNLOADS - {FRS_RAW}, "Original registry download assignments differ")
    for path in RAW_DOWNLOADS:
        with (store / path).open("rb") as body:
            require(hashlib.file_digest(body, "sha256").hexdigest() == digests[path], f"{path}: raw download checksum differs")

    registry_ids = defaultdict(set)
    with zipfile.ZipFile(store / FRS_RAW) as z, z.open("FRS_PROGRAM_LINKS.csv") as stream:
        rd = csv.reader(io.TextIOWrapper(stream, encoding="utf-8-sig", errors="replace", newline=""))
        require(next(rd)[:3] == ["PGM_SYS_ACRNM", "PGM_SYS_ID", "REGISTRY_ID"], "FRS program-link columns differ")
        for row in rd:
            if row and row[0] == "RCRAINFO" and row[1] in groups[ECHO_RAW]:
                registry_ids[row[1]].add(row[2])
    for key, quote in groups[ECHO_RAW].items():
        registry_id = quote.rpartition("; FRS registry ")[2]
        require(re.fullmatch(r"[0-9]{12}", registry_id) and registry_ids[key] == {registry_id},
                f"{key}: quoted FRS ID differs from the original RCRAINFO program link")

    for path, wanted in groups.items():
        source = store / path
        with ExitStack() as stack:
            if path.endswith(".zip"):
                z = stack.enter_context(zipfile.ZipFile(source))
                member = "RCRA_FACILITIES.csv" if path == ECHO_RAW else next(n for n in z.namelist() if n.lower().endswith(".csv"))
                stream = stack.enter_context(z.open(member))
            else:
                stream = stack.enter_context(source.open("rb"))
            rd = csv.DictReader(io.TextIOWrapper(stream, encoding="utf-8-sig", errors="replace", newline=""))
            found = set()
            for r in rd:
                key = r["ID_NUMBER"] if path == ECHO_RAW else (r.get("establishment_ID") or r.get("establishment_id"))
                if key not in wanted:
                    continue
                q = wanted[key]
                if path == ECHO_RAW:
                    source_quote = "; ".join((r["FACILITY_NAME"], f'{r["STREET_ADDRESS"]}, {r["CITY_NAME"]}, {r["STATE_CODE"]} {r["ZIP_CODE"]}'))
                    if gate.norm_space(q.rpartition("; FRS registry ")[0]).casefold() == gate.norm_space(source_quote).casefold():
                        found.add(key)
                else:
                    addr = f'{r["street_address"]}, {r["city"]}, {r["state"]} {r["zip_code"]}'
                    if any(gate.norm_space(q).casefold() == gate.norm_space(f"{name}, {addr}").casefold()
                           for name in (r["company_name"], r["establishment_name"])):
                        found.add(key)
            require(found == wanted.keys(), f"{path}: a cited quote lacks its exact original download row")


def scope_review(evidence, bodies, ref):
    """Apply §2 only to siblings whose replay shows the same defect."""
    source_sets = {
        "EVD-014722": range(14718, 14726),
        "EVD-015360": (15360, 15365, 15366),
        "EVD-015361": (15361, 15363, 15364),
        "EVD-015362": (15362, 15368),
        "EVD-015367": (15367, 15369),
        "EVD-015525": (*range(15524, 15530), 15544, 15548, 15551),
        "EVD-017845": range(17844, 17855),
    }
    body_rows = unique(parse(artifact("SIBLING_BODIES.csv", ref)), lambda r: r["case"], "scope source capture")
    require(body_rows.keys() == source_sets.keys() | {"EVD-425055"}, "Scope source captures differ")
    selected, checked = set(), []
    for key, members in source_sets.items():
        body = bodies[body_rows[key]["filename"]]
        t = quote_check["fold"](quote_check["text"](body, "read-b"), "read-b")
        if key.startswith("EVD-01536"):
            defect = "middlefield" not in t and "44062" not in t
            require(defect == (key == "EVD-015362"), f"{key}: JK Plastics site locality result differs")
            reason = ("Homepage gives neither Middlefield nor 44062." if defect else
                      "This cited page explicitly prints Middlefield and 44062.")
        elif key == "EVD-014722":
            require("solon" not in t and "chagrin falls" not in t and "industries" in t,
                    "Lattice site-scope result differs")
            defect, reason = True, "Operator-level page gives no Solon or Chagrin Falls site tie."
        elif key == "EVD-015525":
            require("industries who use extruded polymers" in t and "industries we serve" not in t,
                    "MES generic-scope result differs")
            defect, reason = True, "The generic industries list does not identify MES customers."
        else:
            require("irrigation" in t and "agricultur" not in t
                    and all(x in t for x in ("aerospace", "military", "appliance", "automotive",
                                            "construction", "electrical", "food", "medical",
                                            "fluoropolymer", "compression molding", "machining")),
                    "Dover list or process replay differs")
        initial = evidence[key]
        member_ids = {f"EVD-{i:06d}" for i in members}
        same_scope = {e["evidence_id"] for e in evidence.values() if e["source_ref"] == initial["source_ref"]
                      and e["record_id"] == initial["record_id"] and e["claim_type"] == "scope"}
        require(member_ids == same_scope, f"{key}: same-site, same-URL scope census differs")
        for eid in sorted(member_ids):
            if key == "EVD-015525" and int(eid[4:]) >= 15544:
                defect = False
                reason = "The material and process claims use separate production wording, outside the generic market list."
            if key == "EVD-017845":
                defect = eid == key
                reason = ("Irrigation is stated and agriculture is absent." if defect else
                          "The cited page explicitly names the corresponding sector, material or process.")
            if defect:
                selected.add(eid)
            checked.append(dict(evidence_id=eid, record_id=evidence[eid]["record_id"], source_case=key,
                                capture_sha256=body_rows[key]["capture_sha256"],
                                decision="withdraw" if defect else "retain", deciding_fact=reason))
    intertex = gate.capture_text(bodies[body_rows["EVD-425055"]["filename"]])
    require(intertex and not re.search(r"carrollton|headquarter|head office", intertex, re.I),
            "Intertex gate main-text route has changed; re-evaluate the conditional HQ case")
    return selected, checked


GATE_LIMITS = {
    **dict.fromkeys(("EVD-405007", "EVD-421581", "EVD-421582"), "A gate route for independent press-page proof."),
    **dict.fromkeys(("EVD-422344", "EVD-422451", "EVD-422452", "EVD-425347", "EVD-424304"),
                   "Owner-approved registry binding for a record whose held street is blank."),
    "EVD-421870": "A gate route for the truncated operator name on the OSHA ITA filing.",
    **dict.fromkeys(("EVD-421737", "EVD-425054"), "A gate route for postal city versus municipality."),
    **dict.fromkeys(("EVD-425134", "EVD-425135", "EVD-425240", "EVD-421634", "EVD-422240", "EVD-422241"),
                   "A gate route for the documented operator variant at the held place."),
    "EVD-420042": "A gate-readable SEC EDGAR route for the held street.",
}
RULE4_EXTRA = {"EVD-422644", "EVD-422645", "EVD-405015", "EVD-422583", "EVD-422235", "EVD-422256"}
RANK = {"supports_U": 0, "supports_C": 1, "supports_B": 2, "supports_A": 3}
STRENGTH = "UCBA"
MUST_HAVE = {
    "organizations": {"existence", "address", "scope", "code"},
    "sites": {"existence", "address", "scope", "code", "parent"},
}
FLOOR_HEADER = ("table", "record_id", "evidence_id", "floor", "held_tier", "supported_tier", "floor_position")


def restated_tier(table, rec, eligible):
    wanted = MUST_HAVE[table]
    if rec.get("status", rec.get("operating_status")) == "active":
        wanted = wanted | {"activity", "liveness"}
    supported = []
    for claim in wanted:
        witnesses = [e for e in eligible if e["claim_type"] == claim]
        positive = [e for e in witnesses if e["tier_effect"] in RANK]
        newest = max((e["observed_date"] for e in positive), default="")
        if any(e["tier_effect"] == "contradicts" and e["observed_date"] >= newest for e in witnesses):
            supported.append(1)
        elif positive:
            supported.append(max(RANK[e["tier_effect"]] for e in positive))
    return STRENGTH[min(supported)] if supported else "none"


def floor_census(records, evidence, selected, new, replaced, projected):
    grouped, added = defaultdict(list), defaultdict(list)
    for row in evidence.values():
        grouped[row["record_table"], row["record_id"]].append(row)
    for rows in new.values():
        for row in rows:
            added[row["record_table"], row["record_id"]].append(row)
    selected_by_record = defaultdict(set)
    for eid in selected:
        ev = evidence[eid]
        selected_by_record[ev["record_table"], ev["record_id"]].add(eid)
    blockers, affected = [], set()
    for (table, rid), withdrawing in sorted(selected_by_record.items()):
        rec = records[table, rid][1]
        tier = rec["verification_tier"]
        after_tier = projected.get((table, rid), tier)
        earlier = grouped[table, rid]
        after = [e for e in earlier if e["evidence_id"] not in selected | replaced] + added[table, rid]
        f = "V-65" if after_tier in {"A", "B"} else "V-68"
        def clears(rows):
            return (any(RANK.get(e["tier_effect"], -1) >= STRENGTH.index(after_tier) for e in rows)
                    if f == "V-65" else bool(rows))
        supported = restated_tier(table, rec, after)
        if not clears(after):
            affected.add((table, rid))
            for eid in sorted(withdrawing):
                blockers.append(dict(zip(FLOOR_HEADER, (table, rid, eid, f, tier, supported,
                    "new loss" if clears(earlier) else "pre-existing floor gap"))))
    return blockers, affected


def pittsburgh_hq(evidence, records, plain, meta, bodies, new, archives, proofs, linked, ref):
    """Apply the one authorized HQ correction and preserve the Huron site."""
    case, rid = "EVD-425423", "ORG-001470"
    before = records["organizations", rid][1]
    require((before["hq_city"], before["hq_state"], before["hq_county"], before["hq_in_scope"], before["hq_country"]) ==
            ("Huron", "OH", "Erie", "ne_ohio", "US"), "Pittsburgh Paints HQ base drifted")
    m = meta[case]
    att = next(r for r in parse(artifact("WEB_READ.csv", ref)) if r["evidence_id"] == case)
    require(att["verdict"] == "VERIFIED" and att["capture_sha256"] == m["capture_sha256"]
            and att["quote_offset"] == m["quote_offset"] and gate.family_of_text(att["reader_family"]) == "google",
            "Pittsburgh Paints independent exact-capture read differs")
    stamp, modifier, source = gate.ARCHIVE_RE.fullmatch(m["capture_ref"]).groups()
    require(modifier and stamp == "20260420085610" and source.startswith("https://www.pittsburghpaintsco.com/"),
            "Pittsburgh Paints capture authority differs")
    q = plain[case]["quote"]
    require("headquarters is in Cranberry Township, Pennsylvania" in q and not re.search(r"@|\d{3}[-. ]\d{3}[-. ]\d{4}", q),
            "Pittsburgh Paints explicit HQ quote differs")
    eid = f"EVD-{max(int(e[4:]) for e in evidence)+len(linked)+1:06d}"
    ev = dict(evidence_id=eid, record_table="organizations", record_id=rid, claim_type="address",
              claim_detail=f"hq_city=Cranberry Township, hq_state=PA (Wayback capture); quote: {q}",
              source_class="own_site", source_ref=source, observed_date="2026-11-23",
              tier_effect=f"supports_{before['verification_tier']}", created_by=LABEL,
              notes=f"Corrects the HQ location in {case}. The Huron plant has separate site evidence.",
              address_role="physical")
    archive = dict(evidence_id=eid, archive_ref=m["capture_ref"].replace(f"{stamp}id_/", f"{stamp}/", 1),
                   captured_at="2026-04-20", created_by="unknown")
    proof = dict(zip(gate.PROOF_COLS, (eid, rid, gate.claim_sha256(ev), m["capture_ref"], archive["captured_at"],
              m["capture_sha256"], m["quote_offset"], att["verdict"], att["reader_family"], att["reader_date"])))
    idx = gate.Index.load(BASE)
    require(gate.judge(ev, idx)[:2] == ("READ_REQUIRED","mechanics_clear") and
            not gate.proof_problem(proof, ev, idx, idx, archive, date.fromisoformat(ev["observed_date"]),
                                   "openai", lambda url: bodies[m["capture_sha256"]+".body"]),
            "Pittsburgh Paints HQ web proof fails")
    require(all(evidence[e]["record_id"] == rid for e in ("EVD-170006","EVD-369007")),
            "Pittsburgh Paints separate legal-name witnesses differ")
    new["data/evidence_organizations_PA.csv"].append(ev)
    archives.append(archive)
    proofs.append(proof)
    linked[case] = eid
    return dict(date=ev["observed_date"], entity=f"{rid} Pittsburgh Paints",
                decision=f"correct HQ scope from {before['hq_in_scope']} to national_us",
                rule_cited="SCHEMA Appendix C §4 (placement correction)", researcher=LABEL,
                notes=f"organizations_OH.csv to organizations_PA.csv. {eid} witnesses the HQ in "
                      "Cranberry Township, Pennsylvania. The Huron plant remains SITE-001531.")


OWNER_MARK = {"ORG-000068", "ORG-000206", "ORG-001762", "ORG-001886", "ORG-002011", "SITE-001575", "ORG-001832"}
OWNER_KEEP = {"ORG-000024", "ORG-000114", "ORG-000127", "ORG-001831",
              "ORG-001862", "ORG-001867", "SITE-000126", "SITE-000137", "SITE-000928"}
FIXED_SCOPE = {"EVD-014722", "EVD-014723", "EVD-015525", "EVD-015529", "EVD-017845", "EVD-015362"}


def expected(packet, store, ref=None):
    raw = checked_packet(packet, ref)
    records, evidence = snapshot(BASE)
    bodies, digests = source_bodies(store, ref)
    verified, uncertain = read_claims(raw, bodies, evidence, ref)
    actions, plain, candidates, meta = recite_claims(raw, bodies, evidence, uncertain, store, digests, ref)
    scope, siblings = scope_review(evidence, bodies, ref)
    require(FIXED_SCOPE <= scope and len(scope) == 17 and not scope & verified.keys(),
            "Scope replay overlaps accepted VERIFICATION or has unexpected coverage")
    new, archives, proofs, linked = mint_recitations(evidence, records, actions, candidates, meta, bodies, ref)
    inclusion = pittsburgh_hq(evidence, records, plain, meta, bodies, new, archives, proofs, linked, ref)

    no_tie = ({eid for eid, r in actions.items() if r["action"] == "WITHDRAW"} | RULE4_EXTRA) - set(GATE_LIMITS) - scope - {"EVD-422303"}
    require("EVD-425055" in no_tie and actions["EVD-422303"]["other_support"].startswith("EVD-410477"),
            "Intertex or the independently tied existence claim differs")
    selected = scope | no_tie | set(GATE_LIMITS) | {"EVD-422303"}
    def key_of(eid):
        e = evidence[eid]
        return e["record_table"], e["record_id"]
    fields = defaultdict(set)
    for eid in no_tie:
        fields[key_of(eid)].add(evidence[eid]["claim_type"])
    grouped = defaultdict(list)
    for e in evidence.values():
        if e["evidence_id"] not in selected | linked.keys() and e["tier_effect"] in RANK:
            grouped[e["record_table"], e["record_id"]].append(e)
    for es in new.values():
        for e in es:
            grouped[e["record_table"], e["record_id"]].append(e)
    missing = {k: sorted(claim for claim in claims if not any(e["claim_type"] == claim for e in grouped[k]))
               for k, claims in fields.items()}
    projected = {k: "U" for k,v in missing.items() if v}
    # The proposed U projection checks the presence floor for a record with no
    # tying same-claim row. Held gate-limited cases test their held tier.
    floors, blocked = floor_census(records, evidence, selected, new, set(linked), projected)
    require(not {key_of(e) for e in linked} & blocked, "A re-citation cannot change a floor-suspended record")
    withdrawals = {eid for eid in selected - set(GATE_LIMITS) if key_of(eid) not in blocked}
    require("EVD-422303" in withdrawals, "Supported existence withdrawal hit a floor")
    for row in siblings:
        if row["decision"] == "withdraw" and row["evidence_id"] not in withdrawals:
            row["decision"] = "held_floor"
    states = {eid: ("verified", eid) for eid in verified}
    states.update((eid, ("corrected", new_eid)) for eid, new_eid in linked.items())
    states.update((eid, ("withdrawn", "")) for eid in withdrawals)
    claims = [dict(zip(CLAIMS, ("evidence", eid, "claim_detail", v, wit))) for eid, (v, wit) in sorted(states.items())]
    changes, cell_claims, notes = {}, {}, {}

    def edit(k, value, verdict, witness=""):
        require(k not in changes, f"{k}: double edit")
        changes[k] = value
        cell_claims[k] = dict(zip(CLAIMS, (*k, verdict, witness)))

    remove = defaultdict(set)
    for eid in scope & withdrawals:
        table, rid = key_of(eid)
        match = re.match(r"sites\.(processes|materials|markets_served) includes ([a-z0-9_]+) ", evidence[eid]["claim_detail"])
        require(table == "sites" and match, f"{eid}: scope locator differs")
        token = match[2]
        if not any(re.search(r"\b"+re.escape(token)+r"\b", e["claim_detail"]) for e in grouped[table,rid]):
            remove[table, rid, match[1]].add(token)
    for k, dropping in remove.items():
        tokens = records[k[:2]][1][k[2]].split(";")
        # A prior application can already have withdrawn a packet token.
        if dropping & set(tokens):
            edit(k, ";".join(t for t in tokens if t not in dropping and t != "unknown"), "withdrawn")

    for field, value in (("hq_city", "Cranberry Township"), ("hq_state", "PA"),
                         ("hq_county", ""), ("hq_in_scope", "national_us")):
        edit(("organizations", "ORG-001470", field), value, "corrected" if value else "withdrawn",
             linked["EVD-425423"] if value and field != "hq_in_scope" else "")
    reasons = {
        "ORG-000068": "the cited homepage gives no Macedonia, Ohio location",
        "ORG-000206": "the cited source gives no Middlefield, Ohio location for the operator",
        "ORG-001886": "the privacy page and archived homepage give no Seville, Ohio location",
        "ORG-002011": "the July 2026 capture names the firm without a location",
        "ORG-000212": "the page prints the group's Cleveland address without naming this operator's headquarters",
        "ORG-000265": "the ITA filing locates the Strongsville facility without stating a headquarters",
        "ORG-000404": "the cited page gives no headquarters and the live page returned an empty response",
        "ORG-001397": "the archived about page and news headline give no headquarters",
        "ORG-001857": "the cited sources give no current headquarters",
        "ORG-001762": "the own site gives a different street number and leaves the operator at the held place unstated",
        "SITE-001575": "the page names Beacon Bio Dx doing business as CleveMed",
        "ORG-001832": "the archived main text gives neither a labelled headquarters nor a tied Carrollton address",
    }
    marked = set()
    for key, claims_missing in sorted(missing.items()):
        table, rid = key
        rec = records[key][1]
        if not claims_missing or rec["verification_tier"] == "U" or (key in blocked and rid not in OWNER_MARK):
            continue
        require(rid not in OWNER_KEEP and (key not in blocked or rid in OWNER_MARK), f"{rid}: tier action lacks authority")
        if rid in reasons:
            reason = reasons[rid]
        elif rid == "SITE-001296":
            reason = "the EPA consent order identifies a different respondent"
        else:
            require(claims_missing == ["address"], f"{rid}: unruled non-floor reason")
            reason = "the cited source does not state the held headquarters address"
        label = " and ".join(claims_missing) + " claim"
        note = f"unverified 2026-11-23: {label} has no tying witness; {reason}"
        edit((*key, "verification_tier"), "U", "corrected")
        # The note records our adjudication rather than a separate published claim.
        changes[*key, "notes"] = "; ".join(part for part in (rec["notes"], note) if part)
        notes[key] = note
        marked.add(rid)
    require(OWNER_MARK <= marked and not OWNER_KEEP & marked, "Owner-approved tier marks differ")

    qrow = evidence["EVD-425223"]
    require(qrow["claim_type"] == "existence" and "twinsburg" not in qrow["claim_detail"].casefold(),
            "Q Holding's legal-name quote now ties to the older Twinsburg address")
    scope_ids = {r["evidence_id"] for r in siblings}
    coverage = set(actions) | scope_ids | {"EVD-420042", "EVD-014675"}
    queue, dispositions, readmit = [], [], []
    for eid in sorted(coverage):
        table, rid = key_of(eid)
        if eid in states:
            action = states[eid][0]
        elif eid in GATE_LIMITS:
            action = "held"
            readmit.append(dict(evidence_id=eid, record_id=rid, gate_extension=GATE_LIMITS[eid]))
            queue.append(dict(zip(QUEUE, ("evidence", eid, "claim_detail", GATE_LIMITS[eid]))))
        elif eid in scope_ids and eid not in scope:
            action = "retained"
        elif eid == "EVD-425223":
            action = "retained"
        else:
            action = "held"
            reason = ("Owner retained the evidence row at the evidence floor." if (table,rid) in blocked else
                      "A replayable held witness for the exact rubber-transfer claim.")
            require((table,rid) in blocked or eid == "EVD-014675", f"{eid}: disposition absent")
            queue.append(dict(zip(QUEUE, ("evidence", eid, "claim_detail", reason))))
        dispositions.append(dict(evidence_id=eid, record_id=rid, disposition=action))

    claims.extend(cell_claims[k] for k in sorted(cell_claims))
    require(len({tuple(r[c] for c in CLAIMS[:3]) for r in claims}) == len(claims), "Duplicate checked claim")
    data = data_delta(records, changes, new, archives, [inclusion],
                      {"ORG-001470": "data/organizations_PA.csv"})
    # Keep the shrink-only baseline aligned when an authorized tier mark resolves an existing V-65 gap.
    debt_path = "scripts/validate_debt_baseline.json"
    import json
    baseline = git("show", f"{BASE}:{debt_path}")
    debt = json.loads(baseline)
    resolved = sorted(set(debt["rules"]["V-65"]) & marked)
    if resolved:
        text = baseline.decode()
        for rid in resolved:
            text = re.sub(r'^\s*"' + rid + r'",\n', "", text, count=1, flags=re.M)
        updated = json.loads(text)
        require(set(debt["rules"]["V-65"])-set(updated["rules"]["V-65"]) == set(resolved),
                "V-65 debt baseline edit differs")
        data[debt_path] = text.encode()
    artifacts = {
        "CLAIMS_CHECKED.csv": csv_bytes(claims, CLAIMS),
        "OPEN_QUEUE.csv": csv_bytes(queue, QUEUE),
        "BINDING_PROOF.csv": csv_bytes(proofs, gate.PROOF_COLS),
        "RECITE_DISPOSITIONS.csv": csv_bytes(dispositions, ("evidence_id", "record_id", "disposition")),
        "RE_ADMISSION.csv": csv_bytes(readmit, ("evidence_id", "record_id", "gate_extension")),
        "SIBLING_CHECKS.csv": csv_bytes(siblings, ("evidence_id", "record_id", "source_case", "capture_sha256", "decision", "deciding_fact")),
        "floor-blockers.csv": csv_bytes(floors, FLOOR_HEADER),
    }
    stats = {"claims": dict(Counter(r["verdict"] for r in claims)), "withdrawn_evidence": len(withdrawals),
             "scope_candidates": len(scope), "scope_withdrawals": len(scope & withdrawals),
             "changed_cells": len(changes), "claim_cells": len(cell_claims), "notes": len(notes),
             "marked": sorted(marked), "held": len(queue), "floor_records": len(blocked),
             "floors": dict(Counter(f["floor"] for f in floors)), "re_admission": len(readmit),
             "witnesses": len(linked), "resolved_debt": resolved}
    registry_matches(plain, store, digests)
    raw_download_matches(plain, store, digests)
    return data, artifacts, stats


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--at", default="HEAD")
    ap.add_argument("--packet", type=Path, default=PACKET)
    ap.add_argument("--store", type=Path, default=STORE)
    a = ap.parse_args()
    data, artifacts, stats = expected(a.packet, a.store, a.at)
    delta = set(git("diff", "--name-only", BASE, a.at, "--", "data/", "scripts/validate_debt_baseline.json").decode().splitlines())
    require(delta == data.keys(), "Unexpected canonical paths or V-65 baseline change")
    for path, contents in data.items():
        require(git("show", f"{a.at}:{path}") == contents, f"{path}: applied bytes differ")
    for name, contents in artifacts.items():
        require(artifact(name, a.at) == contents, f"{name}: replay differs")
    draw = runpy.run_path(str(HERE.parent / "blind-audit-12-protocol-2026-11-23/draw.py"))
    reader = draw["GitReader"](BASE)
    frame, _, unassignable = draw["build_frame"](reader, reader.regions())
    require(not unassignable, "Baseline audit frame is unassignable")
    stratum = {r["record_id"]: r["stratum"] for r in frame}
    base_idx = gate.Index.load(BASE)
    current_idx = gate.Index.load(a.at)
    tier_marks = parse(artifact("TIER_MARKS.csv", a.at))
    fields = ("record_id", "held_tier", "tier", "audit_frame_at_1600f540")
    require(tuple(tier_marks.fieldnames) == fields, "Tier-mark frame header differs")
    require(list(tier_marks) == [dict(zip(fields, (rid, (base_idx.sites if rid.startswith("SITE-") else
                   base_idx.orgs)[rid]["verification_tier"], "U", stratum.get(rid, "outside"))))
                   for rid in stats["marked"]], "Tier-mark audit-frame census differs")
    pic18 = reader.regions()
    def owners(idx):
        return {s["org_id"] for s in idx.sites.values() if s["state"] == "OH" and s["county"] in pic18
                and s["operating_status"] == "active" and s["verification_tier"] in {"A", "B", "C"}}
    before, after = owners(base_idx), owners(current_idx)
    require((len(before), len(after)) == (794, 792) and before - after == {"ORG-001197", "ORG-001511"}
            and after <= before, "Owner-authorized PIC-18 frame count differs")
    print("PASS", stats)
    print("PIC-18 owners of active tier A–C sites: 794 -> 792")


if __name__ == "__main__":
    main()
