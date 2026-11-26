#!/usr/bin/env python3
"""Named check for the SITE-000056 street fill (own-site route, one cell).

    python3 check.py [BASE [STORE]]    BASE defaults to the merge-base with origin/main; STORE to the shared atlas-store

Clean state must give no problems, then every planted defect must give a problem that names its rule.
Exit 0 only when both hold. The capture is replayed from the shared store only; this check fetches nothing.
The gate's own live replay (--verify-proofs) runs in CI. BINDING_PROOF.csv holds PENDING_READ until a model family
other than Anthropic has read the page: this check fails closed on that, by design.
"""
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
BASE = sys.argv[1] if len(sys.argv) > 1 else subprocess.check_output(
    ["git", "-C", str(ROOT), "merge-base", "origin/main", "HEAD"], text=True).strip()
STORE = Path(sys.argv[2] if len(sys.argv) > 2 else "/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store")
sys.path.insert(0, str(ROOT / "scripts"))
import check_evidence_binding as gate  # noqa: E402  (text and claim helpers only; nothing here fetches)
from regions import PIC18  # noqa: E402

LABEL = f"claude-code {TASK}"
SITE, EVD, STREET = "SITE-000056", "EVD-483296", "2748 2nd Street Suite C"
QUOTE = "Shipping/Receiving 2748 2nd Street Suite C Cuyahoga Falls, OH 44221"
CAPTURE = "https://web.archive.org/web/20260811080031id_/https://cfextrusion.com/site/contact/"
ALLOWED = re.compile(r"data/(sites_OH|evidence_sites_OH|archive_links)\.csv|tasks/" + TASK + r"/[^/]+"
                     r"|tasks/ppp-size-bands-rerun-2026-11-26/AUDIT\.md")
EMAILS_REVIEWED = {"info@cfextrusion.com"}  # a company role address; no individual's address is in the capture


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def rows(blob):
    return list(csv.DictReader(io.StringIO(blob.decode(), newline="")))


def read(name, base):
    return rows(git("show", f"{BASE}:{name}") if base else (ROOT / name).read_bytes())


def evidence(base):
    names = git("ls-tree", "--name-only", BASE, "data/").decode().split() if base else \
        [f"data/{p.name}" for p in (ROOT / "data").iterdir()]
    return {r["evidence_id"]: r for n in sorted(names) if re.fullmatch(r"data/evidence_[A-Za-z_]+\.csv", n) for r in read(n, base)}


def blank_street_count(sites):
    return sum(1 for r in sites if r["state"] == "OH" and r["county"] in PIC18 and r["operating_status"] == "active"
               and r["verification_tier"] in "ABC" and not r["street_address"].strip())


def problems(head, base, claims, proofs, manifest, capture, changed, verdict):
    out = []
    hs, bs = {r["site_id"]: r for r in head["sites"]}, {r["site_id"]: r for r in base["sites"]}
    if set(hs) != set(bs):
        out.append(f"cells: site ids differ from base: {sorted(set(hs) ^ set(bs))[:5]}")
    diff = {(i, k) for i in set(hs) & set(bs) for k in hs[i] if hs[i][k] != bs[i].get(k)}
    claimed = {(c["record_id"], c["field"]) for c in claims}
    if diff != claimed or claimed != {(SITE, "street_address")}:
        out.append(f"cells: changed cells {sorted(diff)[:5]} are not exactly the claimed {sorted(claimed)[:5]} = the one street cell")
    if bs.get(SITE, {}).get("street_address") != "" or hs.get(SITE, {}).get("street_address") != STREET:
        out.append(f"cells: {SITE} street is not blank on base and {STREET!r} on head")
    nb, nh = blank_street_count(base["sites"]), blank_street_count(head["sites"])
    if nb != nh + 1:  # unit: active Ohio PIC-18 tier A-C sites with a blank street
        out.append(f"count: blank-street active PIC-18 tier A-C sites went {nb} -> {nh}, not by exactly one")
    he, be = head["evs"], base["evs"]
    if set(be) - set(he) or any(he[e] != be[e] for e in be if e in he):
        out.append("evidence: a base row is missing or changed on head")
    if sorted(set(he) - set(be)) != [EVD]:
        out.append(f"evidence: rows added are {sorted(set(he) - set(be))[:5]}, not [{EVD}]")
    ev = he.get(EVD)
    if not ev:
        return out + ["evidence: the new row is absent"]
    if (ev["record_table"], ev["record_id"], ev["claim_type"], ev["source_class"], ev["address_role"], ev["created_by"],
            ev["source_ref"]) != ("sites", SITE, "address", "own_site", "physical", LABEL, "https://cfextrusion.com/site/contact/"):
        out.append("evidence: the row is not the pinned physical own-site address row for the site under the label")
    if gate.norm_space(ev["claim_detail"].partition("quote:")[2]) != QUOTE or STREET not in QUOTE:
        out.append("evidence: the row's quote is not the pinned quote")
    if tuple(verdict) != ("READ_REQUIRED", "mechanics_clear"):
        out.append(f"gate: the row's mechanical verdict is {tuple(verdict)}, not READ_REQUIRED mechanics_clear")
    if len(proofs) != 1 or proofs[0]["evidence_id"] != EVD:
        return out + ["proof: BINDING_PROOF.csv must hold exactly the one line for the new row"]
    p = proofs[0]
    if p["claim_sha256"] != gate.claim_sha256(ev) or p["record_id"] != SITE or p["capture"] != CAPTURE:
        out.append("proof: claim_sha256, record or capture url differs from the evidence row")
    if p["verdict"] != "VERIFIED":
        out.append(f"proof: verdict is {p['verdict']!r}; only a VERIFIED reading admits the row")
    if gate.family_of_text(p["reader_family"]) in ("", "anthropic", None):
        out.append("proof: the reader must be a known family other than the builder's (Anthropic)")
    arch = [a for a in head["archive"] if a["evidence_id"] == EVD]
    if len(arch) != 1 or arch[0]["archive_ref"] != p["capture"].replace("id_/", "/", 1) or arch[0]["captured_at"] != p["capture_date"]:
        out.append("archive: no single archive_links row equal to the proof's capture")
    if len(head["archive"]) != len(base["archive"]) + 1 or head["archive"][:-1] != base["archive"]:
        out.append("archive: archive_links.csv must gain exactly one row at the end")
    if len(manifest) != 1 or manifest[0].partition("  ")[0] != p["capture_sha256"]:
        out.append("inputs: INPUTS.sha256 must hold the proof's one capture digest")
    if capture is None:
        out.append("capture: absent from the shared store (a gate must fail on what it could not inspect)")
    else:
        if hashlib.sha256(capture).hexdigest() != p["capture_sha256"]:
            out.append("capture: bytes do not hash to the proof's digest")
        text = gate.capture_text(capture)
        if text[int(p["quote_offset"]):int(p["quote_offset"]) + len(QUOTE)] != QUOTE:
            out.append("capture: the quote is not at the proof's offset in the capture's main text")
        mails = {m.lower() for m in re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", capture.decode("utf-8", "replace"))}
        if mails - EMAILS_REVIEWED:
            out.append(f"capture: an address nobody reviewed is in the capture: {sorted(mails - EMAILS_REVIEWED)}")
    stray = [f for f in changed if not ALLOWED.fullmatch(f)]
    if stray:
        out.append(f"files: changed files outside the allowed set: {stray[:5]}")
    return out


def gate_verdict(ev, street=None):
    """The gate's own mechanical verdict for the new row against the head record, optionally with another street planted."""
    idx = gate.Index.load()
    rec = dict(idx.record("sites", SITE), **({"street_address": street} if street else {}))
    v, why, _ = gate.judge_web(ev, rec, idx, ev["claim_detail"].partition("quote:")[2].strip())
    return v, why


def main():
    base = dict(sites=read("data/sites_OH.csv", True), evs=evidence(True), archive=read("data/archive_links.csv", True))
    head = dict(sites=read("data/sites_OH.csv", False), evs=evidence(False), archive=read("data/archive_links.csv", False))
    claims, proofs = rows((HERE / "CLAIMS_CHECKED.csv").read_bytes()), rows((HERE / "BINDING_PROOF.csv").read_bytes())
    manifest = (HERE / "INPUTS.sha256").read_text().splitlines()
    cap = STORE / "provenance" / TASK / f"{proofs[0]['capture_sha256']}.html"
    capture = cap.read_bytes() if cap.exists() else None
    changed = sorted(set(git("diff", "--name-only", BASE).decode().split() + git("ls-files", "--others", "--exclude-standard").decode().split()))
    args = dict(head=head, base=base, claims=claims, proofs=proofs, manifest=manifest, capture=capture, changed=changed,
                verdict=gate_verdict(head["evs"][EVD]) if EVD in head["evs"] else ("absent", ""))
    clean = problems(**args)
    for p in clean:
        print("CLEAN STATE PROBLEM:", p)
    if clean:
        sys.exit(1)

    def plant(name, rule, mutate):
        a = copy.deepcopy({k: v for k, v in args.items() if k != "capture"}); a["capture"] = args["capture"]
        mutate(a)
        hit = [g for g in problems(**a) if g.startswith(rule)]
        print(("planted " if hit else "MISSED  ") + name + (": " + hit[0][:100] if hit else ""))
        return bool(hit)

    def cell(k, v):
        return lambda a: [r for r in a["head"]["sites"] if r["site_id"] == SITE][0].__setitem__(k, v)

    def other_site_cell(a):
        [r for r in a["head"]["sites"] if r["site_id"] == "SITE-000212"][0]["zip"] = "44021"

    def mutate_quote(a):
        a["head"]["evs"][EVD]["claim_detail"] = a["head"]["evs"][EVD]["claim_detail"].replace("Suite C", "Suite D")

    def flip(a):
        a["capture"] = a["capture"] + b" "

    def mail(a):
        a["capture"] = a["capture"].replace(b"info@cfextrusion.com", b"jane.doe@cfextrusion.com")
        a["proofs"][0]["capture_sha256"] = hashlib.sha256(a["capture"]).hexdigest()  # digest kept honest: only the address rule fires
        a["manifest"] = [a["proofs"][0]["capture_sha256"] + "  x"]

    results = [
        plant("street cell set to a different street", "cells", cell("street_address", "2748 2nd Street")),
        plant("a second cell changed on the same row (zip)", "cells", cell("zip", "44221")),
        plant("a cell changed on another site", "cells", other_site_cell),
        plant("quote altered (Suite D)", "evidence: the row's quote", mutate_quote),
        plant("quote offset off by one", "capture", lambda a: a["proofs"][0].__setitem__("quote_offset", "597")),
        plant("capture bytes changed", "capture: bytes", flip),
        plant("capture absent from the store", "capture", lambda a: a.__setitem__("capture", None)),
        plant("individual's address in the capture", "capture: an address", mail),
        plant("proof claim hash stale", "proof", lambda a: a["proofs"][0].__setitem__("claim_sha256", "0" * 64)),
        plant("reader is the builder's family", "proof", lambda a: a["proofs"][0].__setitem__("reader_family", "Claude (Anthropic)")),
        plant("reading still pending", "proof: verdict", lambda a: a["proofs"][0].__setitem__("verdict", "PENDING_READ")),
        plant("archive row dropped", "archive", lambda a: a["head"].__setitem__("archive", a["head"]["archive"][:-1])),
        plant("a data file outside the allowed set changed", "files", lambda a: a["changed"].append("data/ecosystem.csv")),
        plant("street on the record is not the street in the quote (the gate itself judges it)", "gate",
              lambda a: a.__setitem__("verdict", gate_verdict(head["evs"][EVD], "2750 2nd Street Suite C"))),
    ]
    if not all(results):
        print("FAIL: a planted defect was not caught")
        sys.exit(1)
    print(f"OK: 1 street cell, 1 own-site row, 1 archive link, blank-street count {blank_street_count(base['sites'])} -> "
          f"{blank_street_count(head['sites'])}, {len(results)} planted defects caught")


if __name__ == "__main__":
    main()
