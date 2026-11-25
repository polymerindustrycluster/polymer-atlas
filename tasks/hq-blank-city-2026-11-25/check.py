#!/usr/bin/env python3
"""Named check for the HQ blank-city repair (8 organizations).

    python3 check.py [BASE [STORE]]    BASE defaults to the merge-base with origin/main; STORE to the shared atlas-store

Clean state must give no problems, then every planted defect must give a problem that names its rule.
Exit 0 only when both hold. The capture is replayed from the shared store only; this check fetches nothing.
"""
import copy
import csv
import hashlib
import io
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TASK = HERE.name
BASE = sys.argv[1] if len(sys.argv) > 1 else subprocess.check_output(
    ["git", "-C", str(ROOT), "merge-base", "origin/main", "HEAD"], text=True).strip()
STORE = Path(sys.argv[2] if len(sys.argv) > 2 else "/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store")
sys.path.insert(0, str(ROOT / "scripts"))
import check_evidence_binding as gate  # noqa: E402  (text and claim helpers only; nothing here fetches)
import value_basis  # noqa: E402

LABEL = f"claude-code {TASK}"
KENDA, EVD = "ORG-000197", "EVD-483143"
FRAME = ["ORG-000022", "ORG-000033", "ORG-000050", "ORG-000073", "ORG-000186", "ORG-000197", "ORG-000202", "ORG-003703"]
CLEARED = {"ORG-000022": "Summit", "ORG-000033": "Summit", "ORG-000050": "Portage", "ORG-000073": "Summit",
           "ORG-000186": "Cuyahoga", "ORG-000202": "Lorain", "ORG-003703": "GA"}
FILLED = {"hq_city": "Green", "hq_state": "OH", "hq_country": "US", "hq_in_scope": "ne_ohio"}
QUOTE = "Kenda American Technology Center 5801 Mayfair Road N. Canton , OH 44720 United States"
PIC18_OWNERS = 792
# Addresses in the capture, read by the builder: company or role addresses, no individual's. Any other fails.
EMAILS_REVIEWED = {"kenda@kenda.com.tw", "info@kendausa.com", "info@kendaeurope.eu", "kendaid@kenda.com.tw",
                   "kvm1100@kenda.com.tw"}
ALLOWED_FILES = re.compile(r"data/(organizations_(US|OH)|evidence_organizations_(US|OH)|archive_links)\.csv"
                           rf"|tasks/{TASK}/[^/]+|tasks/pic18-refetch-scale1-values-2026-11-24/AUDIT\.md|tasks/QUEUE\.md")
USPS_OH = "OH"


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def rows_of(blob):
    return list(csv.DictReader(io.StringIO(blob.decode(), newline="")))


def shards(prefix, base):
    out = {}
    names = git("ls-tree", "--name-only", BASE, "data/").decode().split() if base else \
        [f"data/{p.name}" for p in (ROOT / "data").iterdir()]
    for n in sorted(names):
        m = re.fullmatch(rf"data/{prefix}_([A-Z]+)\.csv", n)
        if m:
            out[m[1]] = rows_of(git("show", f"{BASE}:{n}") if base else (ROOT / n).read_bytes())
    return out


def load(base):
    f = (lambda n: rows_of(git("show", f"{BASE}:data/{n}.csv"))) if base else (lambda n: rows_of((ROOT / "data" / f"{n}.csv").read_bytes()))
    return dict(orgs=shards("organizations", base), evs=shards("evidence_organizations", base), archive=f("archive_links"))


def packet(name):
    return rows_of((HERE / name).read_bytes())


def org_shard(o):
    st, c = o["hq_state"].strip().upper(), o["hq_country"].strip().upper()
    return st if st else ("INTL" if c not in ("", "US", "USA", "UNITED STATES") else "US")


def flat(shard_map, key):
    return {r[key]: (s, r) for s, rs in shard_map.items() for r in rs}


def count_for(data):
    return value_basis.pic18_summary(data)[0]


def problems(head, base, claims, proofs, manifest, capture, changed, count, base_violators):
    out = []
    ho, bo = flat(head["orgs"], "org_id"), flat(base["orgs"], "org_id")
    # 1. cells: exactly the claimed cells changed, nothing else, no organization added or lost
    if set(ho) != set(bo):
        out.append(f"cells: organization ids differ from base: {sorted(set(ho) ^ set(bo))[:5]}")
    diff = {(i, k) for i in set(ho) & set(bo) for k in ho[i][1] if ho[i][1][k] != bo[i][1].get(k)}
    claimed = {(c["record_id"], c["field"]) for c in claims}
    if diff != claimed:
        out.append(f"cells: changed cells differ from CLAIMS_CHECKED.csv: only changed {sorted(diff - claimed)[:5]}, only claimed {sorted(claimed - diff)[:5]}")
    if len(claims) != len(claimed):
        out.append("cells: CLAIMS_CHECKED.csv repeats a cell")
    for c in claims:
        i, k = c["record_id"], c["field"]
        if i not in ho or i not in bo:
            continue
        b, h = bo[i][1][k], ho[i][1][k]
        if c["verdict"] == "withdrawn" and not (b and not h and c["evidence_id"] == "" and k == "hq_county"):
            out.append(f"cells: {i} {k} is not a cleared hq_county")
        if c["verdict"] == "corrected" and not (c["evidence_id"] == EVD and not b and h == FILLED.get(k)):
            out.append(f"cells: {i} {k} is not the pinned fill from {EVD}")
        if c["verdict"] not in ("withdrawn", "corrected"):
            out.append(f"cells: {i} {k} verdict {c['verdict']!r}")
    allowed = {(i, "hq_county") for i in CLEARED} | {(KENDA, k) for k in FILLED}
    if claimed != allowed:  # the whole claimed set, not the part about the eight: a ninth owner must not ride in
        out.append(f"cells: the claimed cells are not exactly the 11 allowed pairs: extra {sorted(claimed - allowed)[:5]}, missing {sorted(allowed - claimed)[:5]}")
    # 2. no organization with a county and no city; the base set is the frame, so this cannot pass vacuously
    if sorted(base_violators) != FRAME:
        out.append(f"blank city: the base's county-without-city set is not the 8 framed organizations: {sorted(base_violators)}")
    bad = sorted(i for i, (_, r) in ho.items() if r["hq_county"].strip() and not r["hq_city"].strip())
    if bad:
        out.append(f"blank city: head organizations with hq_county set and hq_city blank: {bad}")
    # 3. the PIC-18 owner count
    if count != PIC18_OWNERS:
        out.append(f"count: PIC-18 owners of active A-C sites is {count}, not {PIC18_OWNERS}")
    # 4. shard placement, and evidence rows travel with their organization
    for i, (s, r) in ho.items():
        if i in FRAME and s != org_shard(r):  # the tree holds other misplaced rows; this PR answers for its own eight
            out.append(f"shard: {i} sits in {s}, its HQ places it in {org_shard(r)}")
    he, be = flat(head["evs"], "evidence_id"), flat(base["evs"], "evidence_id")
    lost = sorted(set(be) - set(he))
    if lost:
        out.append(f"evidence: base rows missing on head: {lost[:5]}")
    for e, (s, r) in he.items():
        if r["record_table"] == "organizations" and r["record_id"] in FRAME and r["record_id"] in ho and s != ho[r["record_id"]][0]:
            out.append(f"evidence: {e} sits in {s}, its organization in {ho[r['record_id']][0]}")
        if e in be and be[e][1] != r:
            out.append(f"evidence: {e} changed on the way to its new shard")
    added = sorted(set(he) - set(be))
    if added != [EVD]:
        out.append(f"evidence: rows added are {added}, not [{EVD}]")
    # 5. the new row, its proof, its archive link and its capture
    if EVD in he:
        ev = he[EVD][1]
        if (ev["record_id"], ev["claim_type"], ev["source_class"], ev["address_role"], ev["created_by"]) != \
                (KENDA, "address", "own_site", "physical", LABEL):
            out.append("proof: the new evidence row is not Kenda's physical own-site address row under the label")
        if gate.norm_space(ev["claim_detail"].partition("quote:")[2]) != QUOTE:
            out.append("proof: the row's quote is not the pinned quote")
        if len(proofs) != 1 or proofs[0]["evidence_id"] != EVD:
            out.append("proof: BINDING_PROOF.csv must hold exactly the one line for the new row")
        else:
            p = proofs[0]
            if p["claim_sha256"] != gate.claim_sha256(ev) or p["verdict"] != "VERIFIED" or p["record_id"] != KENDA:
                out.append("proof: claim_sha256, verdict or record differs from the evidence row")
            if gate.family_of_text(p["reader_family"]) in ("", "anthropic"):
                out.append("proof: the reader must be a known family other than the builder's (Anthropic)")
            arch = [a for a in head["archive"] if a["evidence_id"] == EVD]
            if len(arch) != 1 or arch[0]["archive_ref"] != p["capture"].replace("id_/", "/", 1) or arch[0]["captured_at"] != p["capture_date"]:
                out.append("archive: no single archive_links row equal to the proof's capture")
            sha = (manifest[0] if len(manifest) == 1 else "").partition("  ")[0]
            if len(manifest) != 1 or sha != p["capture_sha256"]:
                out.append("inputs: INPUTS.sha256 must hold the proof's one capture digest")
            if capture is None:
                out.append("capture: the capture is absent from the shared store (a gate must fail on what it could not inspect)")
            else:
                if hashlib.sha256(capture).hexdigest() != p["capture_sha256"]:
                    out.append("capture: bytes do not hash to the proof's digest")
                text = gate.capture_text(capture)
                if text[int(p["quote_offset"]):int(p["quote_offset"]) + len(QUOTE)] != QUOTE:
                    out.append("capture: the quote is not at the proof's offset in the capture's main text")
                # the raw bytes, not the main text: the store holds the whole page, nav and footer included
                mails = {m.lower() for m in re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", capture.decode("utf-8", "replace"))}
                if mails - EMAILS_REVIEWED:
                    out.append(f"capture: an address nobody reviewed is in the capture: {sorted(mails - EMAILS_REVIEWED)}")
    else:
        out.append("proof: no new evidence row to prove")
    if len(head["archive"]) != len(base["archive"]) + 1 or head["archive"][:-1] != base["archive"]:
        out.append("archive: archive_links.csv must gain exactly one row at the end")
    # 6. nothing else in the tree changed
    stray = [f for f in changed if not ALLOWED_FILES.fullmatch(f)]
    if stray:
        out.append(f"files: changed files outside the allowed set (no site row, ring, name or status): {stray[:5]}")
    if any(f.startswith(("data/sites_", "data/evidence_sites_")) for f in changed):
        out.append("files: a site or site-evidence file changed")
    return out


def audit_problem():
    p = ROOT / "tasks/pic18-refetch-scale1-values-2026-11-24/AUDIT.md"
    t = p.read_text() if p.exists() else ""
    return [] if "Label: claude-code pic18-refetch-scale1-values-2026-11-24" in t and re.search(r"(?m)^Result: PASS", t) else \
        ["audit: no PASS AUDIT.md for the label #559 left unaudited (AGENTS 2a rule 5)"]


def count_with(drop_site=None):
    """The count on a temp data dir that links every data file and optionally drops one site row."""
    with tempfile.TemporaryDirectory() as tmp:
        for p in (ROOT / "data").iterdir():
            if drop_site is None or not p.name.startswith("sites_OH"):
                (Path(tmp) / p.name).symlink_to(p)
        if drop_site:
            rows = list(csv.reader(io.StringIO((ROOT / "data/sites_OH.csv").read_text(), newline="")))
            keep = [r for r in rows if r[0] != drop_site]
            assert len(keep) == len(rows) - 1
            with (Path(tmp) / "sites_OH.csv").open("w", newline="") as f:
                csv.writer(f, lineterminator="\n").writerows(keep)
        return count_for(Path(tmp))


def main():
    base, head = load(True), load(False)
    claims, proofs = packet("CLAIMS_CHECKED.csv"), packet("BINDING_PROOF.csv")
    manifest = (HERE / "INPUTS.sha256").read_text().splitlines()
    sha = proofs[0]["capture_sha256"]
    cap_path = STORE / "provenance" / TASK / f"{sha}.html"
    capture = cap_path.read_bytes() if cap_path.exists() else None
    changed = git("diff", "--name-only", BASE).decode().split() + \
        git("ls-files", "--others", "--exclude-standard").decode().split()
    changed = sorted(set(changed))
    count = count_with()
    base_viol = [r["org_id"] for rs in base["orgs"].values() for r in rs if r["hq_county"].strip() and not r["hq_city"].strip()]
    args = dict(head=head, base=base, claims=claims, proofs=proofs, manifest=manifest, capture=capture,
                changed=changed, count=count, base_violators=base_viol)
    clean = problems(**args) + audit_problem()
    for p in clean:
        print("CLEAN STATE PROBLEM:", p)
    if clean:
        sys.exit(1)

    def plant(name, rule, mutate):
        a = copy.deepcopy({k: v for k, v in args.items() if k not in ("capture",)})
        a["capture"] = args["capture"]
        mutate(a)
        got = problems(**a)
        hit = [g for g in got if g.startswith(rule)]
        print(("planted " if hit else "MISSED  ") + name + (": " + hit[0][:110] if hit else ""))
        return bool(hit)

    def org(a, i):
        return flat(a["head"]["orgs"], "org_id")[i][1]

    def set_cell(i, k, v):
        return lambda a: org(a, i).__setitem__(k, v)

    def drop_claim(a):
        a["claims"] = [c for c in a["claims"] if not (c["record_id"] == "ORG-000033")]

    def kenda_stays(a):
        r = org(a, KENDA)
        a["head"]["orgs"]["OH"].remove(r)
        a["head"]["orgs"]["US"].append(r)

    def lose_evidence(a):
        s = a["head"]["evs"]["OH"]
        s.remove([r for r in s if r["evidence_id"] == "EVD-421274"][0])

    def edit_moved(a):
        [r for r in a["head"]["evs"]["OH"] if r["evidence_id"] == "EVD-421274"][0]["claim_detail"] += " x"

    def evidence_left_behind(a):
        s = a["head"]["evs"]["OH"]
        r = [r for r in s if r["evidence_id"] == "EVD-421274"][0]
        s.remove(r)
        a["head"]["evs"]["US"].append(r)

    def other_county(a):
        r = org(a, "ORG-000050")
        r["hq_county"], r["hq_city"] = "Portage", ""

    def extra_cell(a):
        org(a, "ORG-000022")["hq_in_scope"] = "national_us"

    def mail(a):
        a["capture"] = a["capture"].replace(b"info@kendausa.com", b"jane.doe@kendausa.com")
        a["proofs"][0]["capture_sha256"] = hashlib.sha256(a["capture"]).hexdigest()  # keep the digest honest: only the address rule can fire
        a["manifest"] = [a["proofs"][0]["capture_sha256"] + "  x"]

    def bad_offset(a):
        a["proofs"][0]["quote_offset"] = "472"

    def flipped_byte(a):
        a["capture"] = a["capture"] + b" "

    def ninth_owner(a):
        org(a, "ORG-000001")["hq_county"] = ""
        a["claims"].append(dict(table="organizations", record_id="ORG-000001", field="hq_county", verdict="withdrawn", evidence_id=""))

    results = [
        plant("a cell outside the claims (ORG-000022 hq_in_scope)", "cells", extra_cell),
        plant("a cleared cell left at its old value (ORG-000033 hq_county)", "cells", set_cell("ORG-000033", "hq_county", "Summit")),
        plant("a claim line dropped (ORG-000033)", "cells", drop_claim),
        plant("a ninth owner loses a valid county and CLAIMS_CHECKED.csv is edited to match (two-file defect)", "cells: the claimed cells are not exactly", ninth_owner),
        plant("Kenda's city set to the mailing city", "cells", set_cell(KENDA, "hq_city", "North Canton")),
        plant("a county with no city on another organization", "blank city", other_county),
        plant("the base set no longer the frame (vacuous pass)", "blank city", lambda a: a.__setitem__("base_violators", FRAME[:-1])),
        plant("PIC-18 owner count 791 (site SITE-000204 dropped from sites_OH)", "count",
              lambda a: a.__setitem__("count", count_with("SITE-000204"))),
        plant("Kenda left in the residual shard", "shard", kenda_stays),
        plant("Kenda's old evidence row lost", "evidence", lose_evidence),
        plant("Kenda's old evidence row altered", "evidence", edit_moved),
        plant("Kenda's old evidence row left in the US shard", "evidence", evidence_left_behind),
        plant("the new proof's quote offset off by one", "capture", bad_offset),
        plant("the capture bytes changed", "capture: bytes do not hash", flipped_byte),
        plant("an individual's address in the capture (digest kept consistent)", "capture: an address", mail),
        plant("the capture absent from the store", "capture", lambda a: a.__setitem__("capture", None)),
        plant("proof claim hash stale", "proof", lambda a: a["proofs"][0].__setitem__("claim_sha256", "0" * 64)),
        plant("reader is the builder's family", "proof", lambda a: a["proofs"][0].__setitem__("reader_family", "Claude (Anthropic)")),
        plant("archive link dropped", "archive", lambda a: a["head"].__setitem__("archive", a["head"]["archive"][:-1])),
        plant("a site file changed", "files", lambda a: a["changed"].append("data/sites_OH.csv")),
        plant("a file outside the allowed set changed", "files", lambda a: a["changed"].append("data/ecosystem.csv")),
    ]
    if not all(results):
        print("FAIL: a planted defect was not caught")
        sys.exit(1)
    print(f"OK: 8 records (4 Kenda cells filled, 7 hq_county cells cleared), 1 witness, 1 archive link, "
          f"{PIC18_OWNERS} PIC-18 owners unchanged, {len(results)} planted defects caught")


if __name__ == "__main__":
    main()
