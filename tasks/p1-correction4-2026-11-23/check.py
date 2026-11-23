#!/usr/bin/env python3
"""Replay the correction 4 reader decisions and compare the exact canonical diff."""
import argparse
from collections import Counter, defaultdict
from datetime import date
from html import unescape
import io
from pathlib import Path
import re
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "3fb1c0baab80cdc7127390d58794b47a01043412"
LABEL = HERE.name
PACKETS = Path.home() / ".bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist"
STORE = Path("/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store")
PROVENANCE = "provenance/correction4-2026-11-23/captures"
DAY = "2026-11-23"
P8 = "p1-read-atlas8-open-2026-11-23"
PEOPLE = "p1-reread-people-gemini-2026-11-23"
OH = "p1-read-atlas9-rest-ohio-2026-11-23"
PIC = f"{OH}/pic18-screen5"
US = "p1-read-atlas9-rest-us-2026-11-23"
CROSS = "p1-reread-gemini-2026-11-23"
PACKET_NAMES = (P8, PEOPLE, OH, PIC, US, CROSS)
PACKET_INPUTS = tuple(f"{p}/{f}" for p in PACKET_NAMES for f in ("README.md", "verdicts.csv")) + (
    f"{P8}/claude_built.csv", f"{CROSS}/agreement.csv",
)
CLAIMS = ("table", "record_id", "field", "verdict", "evidence_id")
QUEUE = (*CLAIMS[:3], "packet", "packet_line", "settling_fact")
ATTEST = (*CLAIMS[:3], "capture_sha256", "quote_offset", "quote_length")
ARCHIVES = ("evidence_id", "archive_ref", "captured_at", "created_by")
BODY_SHA = {
    "SITE-001579": "e51987dcccf8d5920fc4f19ee7a01399755df58f8a06d6145940902841f7fa47",
    "EVD-423769": "057ea53d0f7cc84a265ddd8f3984b798dac85106f066062eb84c1ff5b724097d",
    "EVD-014329": "e0193d99a127dbce6a4606de3a4d5140857fdc7a39cff2cbd061816e897c99c4",
    "EVD-018632": "948b90701ece36ccd95fa37bf6aa6a39f770623567e7e3c1b3ef02bae0395725",
    "EVD-387001": "826bf082da467910af873f11e73ea9f09145ea56de695b271da6f5ad5119bb33",
    "PERSON-002497": "c952c86cfbbc7bbc8e20ab400bb13646e95f001dab94703709007e73e1be9f09",
}
BODY_FILE = {k: f"{PROVENANCE}/{v}{'.txt' if k.startswith('PERSON-') else '.html'}" for k, v in BODY_SHA.items()}

prior = runpy.run_path(str(HERE.parent / "p1-atlas8-corrections-2026-11-23/check.py"))
git, parse, require, sha, unique, csv_bytes, snapshot, witness_id, key0 = (
    prior[k] for k in ("git", "parse", "require", "sha", "unique", "csv_bytes", "snapshot", "witness_id", "key")
)
sys.path.insert(0, str(ROOT / "scripts"))
import check_evidence_binding as gate


def artifact(name, ref):
    path = HERE / name
    return git("show", f"{ref}:{path.relative_to(ROOT)}") if ref else path.read_bytes()


def checked_inputs(name, inputs, root, ref):
    files = {}
    for line in artifact(name, ref).decode().splitlines():
        digest, path = line.split("  ", 1)
        require(path in inputs and path not in files, f"{name}: invalid or duplicate manifest path")
        contents = (root / path).read_bytes()
        require(sha(contents) == digest, f"{name}: checksum differs for {path}")
        files[path] = contents
    require(files.keys() == set(inputs), f"{name}: incomplete manifest")
    return files


def packet_rows(raw, name):
    reader = parse(raw[f"{name}/verdicts.csv"])
    return [dict(row, _packet=name, _line=reader.line_num) for row in reader]


def hold_reason(row):
    fact = row["deciding_fact"].casefold()
    if any(s in fact for s in ("unreach", "403", "timeout", "refused", "not retriev", "could not fetch")):
        return "A readable, attributable copy of the cited source that states this claim."
    if any(s in fact for s in ("operator", "premis", "site-specific", "same entity", "different entity")):
        return "A primary witness tying the asserted fact to the exact operator and premises."
    if any(s in fact for s in ("histor", "curr", "recen")):
        return "A dated primary witness confirming that the held claim is current."
    return "A primary witness explicitly stating the held value. See the sealed reader locator for the unresolved fact."


def canonical_diff(records, changes, new_evs, archives):
    by_path = defaultdict(lambda: defaultdict(dict))
    for (table, rid, field), value in changes.items():
        path, row = records[table, rid]
        require(row[field] != value, f"{rid}/{field}: proposed edit is a no-op")
        by_path[path][rid][field] = value
    out = {}
    for path, by_id in by_path.items():
        old = git("show", f"{BASE}:{path}")
        rd = parse(old)
        lines = list(io.StringIO(old.decode(), newline=""))
        chunks, end, seen = [lines[0].encode()], 1, set()
        id_field = prior["KEYS"][Path(path).stem.split("_")[0]]
        for row in rd:
            start, end = end, rd.line_num
            rid = row[id_field]
            if rid in by_id:
                row.update(by_id[rid])
                chunks.append(csv_bytes([row], rd.fieldnames, with_header=False))
                seen.add(rid)
            else:
                chunks.append("".join(lines[start:end]).encode())
        require(seen == by_id.keys(), f"{path}: edited records not found")
        out[path] = b"".join(chunks)
    for path, rows in dict(new_evs, **{"data/archive_links.csv": archives}).items():
        old = git("show", f"{BASE}:{path}")
        require(old.endswith(b"\n"), f"{path}: no newline before evidence append")
        out[path] = old + csv_bytes(rows, parse(old).fieldnames, with_header=False)
    return out


def expected(packets, store, ref=None):
    raw = checked_inputs("PACKET.sha256", PACKET_INPUTS, packets, ref)
    held = checked_inputs("INPUTS.sha256", BODY_FILE.values(), store, ref)
    bodies = {k: held[path] for k, path in BODY_FILE.items()}
    require(all(sha(bodies[k]) == digest for k, digest in BODY_SHA.items()), "Capture assignment differs")
    pkts = {n: packet_rows(raw, n) for n in PACKET_NAMES}
    require([Counter(r["verdict"] for r in pkts[n]) for n in PACKET_NAMES] == [
        {"VERIFIED": 63, "REJECT": 4, "STILL_UNCERTAIN": 19},
        {"VERIFIED": 34, "REJECT": 1, "STILL_UNCERTAIN": 2},
        {"VERIFIED": 47, "STILL_UNCERTAIN": 3},
        {"VERIFIED": 46, "STILL_UNCERTAIN": 4},
        {"VERIFIED": 42, "REJECT": 1, "STILL_UNCERTAIN": 48},
        {"VERIFIED": 17, "REJECT": 2, "STILL_UNCERTAIN": 4},
    ], "Reader populations differ")
    r8 = unique(pkts[P8], key0, "ATLAS-8 second read")
    people = unique(pkts[PEOPLE], lambda r: r["record_id"], "people cross-read")
    require(set(people) == {rid for tab, rid, _ in r8 if tab == "people"}, "People sample scope differs")
    claude8 = list(parse(raw[f"{P8}/claude_built.csv"]))
    require(set(people) == {r["record_id"] for r in claude8}, "People cross-read label set differs")
    r9 = unique(pkts[OH] + pkts[PIC] + pkts[US], lambda r: r["evidence_id"], "ATLAS-9 first-read sample")
    cross = unique(pkts[CROSS], lambda r: r["evidence_id"], "ATLAS-9 cross-read")
    disagreement = {eid for eid, r in cross.items() if r9[eid]["verdict"] != r["verdict"]}
    require(disagreement == {"EVD-014675", "EVD-015525", "EVD-015529", "EVD-423769"} and
            cross["EVD-423503"]["verdict"] == "REJECT", "Settled ATLAS-9 disagreement set differs")
    records, evidence = snapshot(BASE)
    idx = gate.Index.load(BASE)
    original_idx = gate.Index.load(BASE)
    witnesses = defaultdict(list)
    for ev in evidence.values():
        witnesses[ev["record_table"], ev["record_id"]].append(ev)

    claims, queued, changes = {}, {}, {}
    new_evs, archives, proofs, private_quote = defaultdict(list), [], [], []
    start_id = max(int(eid.split("-")[1]) for eid in evidence)+1

    def ledger(k, verdict, eid=""):
        require(k not in claims and k not in queued, f"Duplicate claim outcome: {k}")
        claims[k] = dict(zip(CLAIMS, (*k, verdict, eid)))

    def hold(k, row, reason=None):
        require(k not in queued and k not in claims, f"Duplicate queued item: {k}")
        queued[k] = dict(zip(QUEUE, (*k, row["_packet"], row["_line"], reason or hold_reason(row))))

    def archive_site(case, rid, source, stamp, off, quote, tier, reason):
        cap = f"https://web.archive.org/web/{stamp}id_/{source}"
        digest = BODY_SHA[case]
        day = date(int(stamp[:4]), int(stamp[4:6]), int(stamp[6:8])).isoformat()
        eid = f"EVD-{start_id+len(archives):06d}"
        require(gate.capture_text(bodies[case]).count(quote) == 1 and
                gate.capture_text(bodies[case])[off:off+len(quote)] == quote and
                not re.search(r"@|\d{3}[-. ]\d{3}[-. ]\d{4}", quote),
                f"{case}: quote was not witnessed or carries contact details")
        ev = dict(evidence_id=eid, record_table="sites", record_id=rid, claim_type="address",
                  claim_detail=f"street_address, site contact address (Wayback capture); quote: {quote}",
                  source_class="own_site", source_ref=source, observed_date=DAY, tier_effect=f"supports_{tier}",
                  created_by=LABEL, notes=reason, address_role="")
        archive = dict(evidence_id=eid, archive_ref=cap.replace(f"{stamp}id_/", f"{stamp}/", 1),
                       captured_at=day, created_by=LABEL)
        proof = dict(zip(gate.PROOF_COLS, (eid, rid, gate.claim_sha256(ev), cap, day, digest, str(off),
                                          "VERIFIED", "Claude Sonnet", DAY)))
        require(gate.judge(ev, idx)[:2] == ("READ_REQUIRED", "mechanics_clear"),
                f"{case}: trusted mechanical floor fails")
        require(not gate.proof_problem(proof, ev, idx, original_idx, archive,
                                       date.fromisoformat(DAY), "openai", lambda url: bodies[case]),
                f"{case}: local held-capture proof fails")
        path = records["sites", rid][0].replace("data/sites_", "data/evidence_sites_", 1)
        new_evs[path].append(ev)
        archives.append(archive)
        proofs.append(proof)
        return eid

    for k, r in r8.items():
        table, rid, field = k
        rec = records[table, rid][1]
        if table == "people":
            g = people[rid]
            if g["verdict"] == "VERIFIED":
                ledger(k, "verified", witness_id([dict(g, field=field)], witnesses, rec))
            elif g["verdict"] == "STILL_UNCERTAIN":
                require(rid in {"PERSON-002405", "PERSON-002437"}, "People hold set differs")
                hold(k, g, "A readable primary capture stating the affected professional claim.")
            else:
                require(rid == "PERSON-002497" and r["verdict"] == "REJECT"
                        and g["field"] == "full_name" and g["source_url"] == rec["public_profile_url"]
                        and g["source_url"] in rec["sources"], "People ruling or held faculty citation differs")
                name = g["correct_value"]
                text = bodies[rid].decode("utf-8")
                require(name and text.count(name) == 1 and rec["full_name"] != name and
                        g["capture_ref"].startswith(f"live:{g['source_url']} (HTTP 200, 9177efb72268230b.txt)"),
                        f"{rid}: exact faculty name or captured page did not replay")
                nk = table, rid, "full_name"
                ev = evidence["EVD-399382"]
                require((ev["record_table"], ev["record_id"], ev["source_ref"], ev["claim_type"]) ==
                        (table, rid, g["source_url"], "existence"), f"{rid}: held faculty evidence differs")
                changes[nk] = name
                ledger(nk, "corrected")
                private_quote.append(dict(zip(ATTEST, (*nk, BODY_SHA[rid], text.index(name), len(name)))))
        elif r["verdict"] == "VERIFIED":
            ledger(k, "verified", witness_id([r], witnesses, rec))
        elif r["verdict"] == "STILL_UNCERTAIN":
            hold(k, r)
        elif rid == "ORG-000503":
            hold(k, r, "A gate replay that retains the Kent page body, following the owner ruling on the extractor.")
        elif rid == "PROG-000356":
            nk = table, rid, "research_areas"
            changes[nk] = ""
            ledger(nk, "withdrawn")
        else:
            require(rid == "SITE-001579" and field == "street_address", "Unexpected ATLAS-8 correction")
            street = "549 E Washington Street"
            require(not rec[field] and r["correct_value"] == "sha256:"+sha(street.encode()),
                    f"{rid}: withdrawn street or replacement hash differs")
            changes[k] = street
            idx.sites[rid]["street_address"] = street
            eid = archive_site(rid, rid, r["source_url"], "20261123202519", 11, r["quote"],
                               rec["verification_tier"], "Contact address on the operator page at the held city and ZIP.")
            ledger(k, "corrected", eid)

    for eid, r in r9.items():
        ev = evidence[eid]
        rid = r["record_id"]
        k = "evidence", eid, "claim_detail"
        require(rid == ev["record_id"], f"{eid}: packet points to another record")
        if eid == "EVD-420042":
            hold(k, r, "An owner-approved, gate-readable SEC EDGAR route. G8 will settle the non-tying old citation.")
        elif eid == "EVD-014675":
            hold(k, cross[eid], "An exact held source body carrying the rubber-transfer quote. Route to G8 for settlement.")
        elif eid == "EVD-423769":
            require(r["verdict"] == "VERIFIED" and cross[eid]["verdict"] == "STILL_UNCERTAIN", "Jackson ruling differs")
            rec = records["sites", rid][1]
            quote = "Head Office Jackson Kayak 3300 McMinnville Hwy. Sparta, TN 38583"
            new = archive_site(eid, rid, "https://jacksonkayak.com/pages/contact-us", "20261123202521",
                               1640, quote, rec["verification_tier"],
                               "Re-cites the matching head-office address from EVD-423769. Plant function has separate evidence.")
            ledger(k, "corrected", new)
        elif eid == "EVD-423503":
            require(r["verdict"] == "REJECT" and rid == "SITE-003748" and
                    cross[eid]["capture_ref"].find("https://exelcomposites.com/contact-us/") >= 0,
                    "Exel controller withdrawal differs")
            changes["sites", rid, "street_address"] = ""
            ledger(k, "withdrawn")
            ledger(("sites", rid, "street_address"), "withdrawn")
            hold(("sites", rid, "street_address_replacement"), cross[eid],
                 "A readable public archive of the live Exel contact-us page with the current Erlanger street.")
        elif cross.get(eid, r)["verdict"] == "VERIFIED":
            ledger(k, "verified", eid)
        else:
            require(r["verdict"] == "STILL_UNCERTAIN", f"{eid}: unexpected reject")
            hold(k, cross.get(eid, r))

    for eid in ("EVD-014329", "EVD-018632", "EVD-387001"):
        ev = evidence[eid]
        table, rid = ev["record_table"], ev["record_id"]
        rec = records[table, rid][1]
        k = table, rid, "processes"
        body = bodies[eid]
        text = gate.capture_text(body)
        q = (re.search(r'quote:\s*"([^"]+)"', ev["notes"], re.I) or
             re.search(r"quote:\s*(.+)", ev["claim_detail"], re.I))
        quote_text = " ".join(q[1].split())
        # Woodlawn's original service label occurs in the HTML outside the main-text region.
        held_text = " ".join(re.sub(r"<[^>]+>", " ", unescape(body.decode())).split()) if eid == "EVD-018632" else text
        require(quote_text in held_text and re.search(r"\btransfer molding\b", quote_text, re.I)
                and not re.search(r"\b(?:plastics?|thermosets?|thermoplastics?) transfer molding\b", text, re.I),
                f"{eid}: held rubber-only quote does not replay")
        terms = rec["processes"].split(";")
        require(terms.count("transfer_molding") == 1 and "rubber_molding_transfer" not in terms,
                f"{k}: schema correction does not match the held cell")
        changes[k] = ";".join("rubber_molding_transfer" if t == "transfer_molding" else t for t in terms)
        ledger(k, "corrected", eid)

    require(Counter(r["verdict"] for r in claims.values()) == {"verified": 197, "corrected": 6, "withdrawn": 3} and
            len(queued) == 76 and len(changes) == 7 and len(proofs) == 2, "Final correction counts differ")
    data = canonical_diff(records, changes, new_evs, archives)
    artifacts = {
        "CLAIMS_CHECKED.csv": csv_bytes([claims[k] for k in sorted(claims)], CLAIMS),
        "OPEN_QUEUE.csv": csv_bytes([queued[k] for k in sorted(queued)], QUEUE),
        "BINDING_PROOF.csv": csv_bytes(proofs, gate.PROOF_COLS),
        "FACULTY_WITNESS.csv": csv_bytes(private_quote, ATTEST),
    }
    return data, artifacts, changes


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--at", default="HEAD")
    ap.add_argument("--packets", type=Path, default=PACKETS)
    ap.add_argument("--store", type=Path, default=STORE)
    a = ap.parse_args()
    data, artifacts, changes = expected(a.packets, a.store, a.at)
    changed = set(git("diff", "--name-only", BASE, a.at, "--", "data/").decode().splitlines())
    require(changed == data.keys(), "Unexpected set of changed data files")
    for path, wanted in data.items():
        require(git("show", f"{a.at}:{path}") == wanted, f"{path}: canonical correction diff differs")
    for path, wanted in artifacts.items():
        require(artifact(path, a.at) == wanted, f"{path}: packet replay differs")
    print(f"PASS: {len(changes)} changed cells, 206 checked claims (197 verified, 6 corrected, 3 withdrawn), "
          "76 queue entries, 2 archive-bound observations, 6 replayed captures")


if __name__ == "__main__":
    main()
