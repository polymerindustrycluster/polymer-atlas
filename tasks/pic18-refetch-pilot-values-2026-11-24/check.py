#!/usr/bin/env python3
"""Named check for the refetch-pilot value fills.

    python3 check.py            replay captures from the shared store (fails if a capture is absent)
    python3 check.py --fresh    replay by fetching each page as the CI gate does (UA evidence-check/1, HTTP 200 only)

Clean state must give no problems, then every planted defect must give a problem that names its rule.
Exit 0 only when both hold.
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
STORE = Path("/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store")
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(HERE))
import check_evidence_binding as gate  # noqa: E402

LABEL = f"claude-code {TASK}"
ALLOWED = re.compile(r"data/(organizations_[A-Z]+|evidence_organizations_[A-Z]+|value_basis|archive_links)\.csv")
HEADS = {"processes": "processes={v}", "markets_served": "Markets served: {v}"}


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def rows_of(blob):
    return list(csv.DictReader(io.StringIO(blob.decode(), newline="")))


def read(name):
    with open(HERE / name, newline="") as f:
        return list(csv.DictReader(f))


def vocabulary():
    s = (ROOT / "docs/SCHEMA.md").read_text()
    proc = s.split("### 3.1 Processes")[1].split("### 3.2 Materials")[0]
    market = s.split("### 3.3 Markets")[1].split("### 3.4 Certifications")[0]
    terms = lambda v: set(re.findall(r"`([a-z0-9_]+)`", v))
    regular, ring3 = proc.split("Ring 3 services", maxsplit=1)
    return {"processes": terms(regular), "markets_served": terms(market)}, terms(ring3) - {"processes_other_note"}


def load():
    base = git("merge-base", "HEAD", "origin/main").decode().strip()
    changed = git("diff", "--name-only", base, "--", "data/").decode().split()
    changed += git("ls-files", "--others", "--exclude-standard", "data/").decode().split()
    cells, evidence, basis_added, basis_removed, orgs, archives = [], {}, set(), set(), {}, {}
    evidence_n = archives_n = 0
    for path in git("ls-tree", "--name-only", base, "data/").decode().split():
        if re.fullmatch(r"data/organizations_[A-Z]+\.csv", path):
            for r in rows_of(git("show", f"{base}:{path}")):
                orgs[r["org_id"]] = r
    for path in sorted(set(changed)):
        if not ALLOWED.fullmatch(path):
            continue
        old, new = git("show", f"{base}:{path}"), (ROOT / path).read_bytes()
        if path.startswith("data/organizations_"):
            before, after = rows_of(old), rows_of(new)
            if [r["org_id"] for r in before] != [r["org_id"] for r in after]:
                cells.append((path, "*", "row set", "", ""))
                continue
            for b, a in zip(before, after):
                for k in b:
                    if b[k] != a[k]:
                        cells.append((path, b["org_id"], k, b[k], a[k]))
        elif path.startswith("data/evidence_"):
            if not new.startswith(old):
                cells.append((path, "*", "evidence rewrite", "", ""))
                continue
            header = old.splitlines()[0].decode()
            for r in rows_of((header + "\n").encode() + new[len(old):]):
                evidence[r["evidence_id"]] = r
                evidence_n += 1
        elif path == "data/archive_links.csv":
            if not new.startswith(old):
                cells.append((path, "*", "archive rewrite", "", ""))
                continue
            header = old.splitlines()[0].decode()
            for r in rows_of((header + "\n").encode() + new[len(old):]):
                archives[r["evidence_id"]] = r
                archives_n += 1
        else:  # value_basis.csv
            key = lambda r: tuple(r.values())
            before, after = {key(r) for r in rows_of(old)}, {key(r) for r in rows_of(new)}
            basis_added, basis_removed = after - before, before - after
    greatest = max(int(r["evidence_id"].split("-")[1])
                   for p in git("ls-tree", "--name-only", base, "data/").decode().split()
                   if re.fullmatch(r"data/evidence_[A-Za-z_]+\.csv", p) for r in rows_of(git("show", f"{base}:{p}")))
    return dict(base=base, changed=sorted(set(changed)), cells=cells, evidence=evidence, orgs=orgs, archives=archives, evidence_n=evidence_n, archives_n=archives_n,
                basis_added=basis_added, basis_removed=basis_removed, greatest=greatest,
                second=read("second_read.csv"), fills=read("FILLS.csv"), proofs=read("BINDING_PROOF.csv"),
                claims=read("CLAIMS_CHECKED.csv"), readme=(HERE / "README.md").read_bytes(),
                inputs=(HERE / "INPUTS.sha256").read_text().split("\n"))


def verify(s, bytes_for):
    """Every problem found, as 'rule: detail'. Empty means the packet holds."""
    out = []
    add = lambda rule, why: out.append(f"{rule}: {why}")
    vocab, ring3 = vocabulary()
    for path in s["changed"]:
        if not ALLOWED.fullmatch(path):
            add("files", f"{path} is outside the allowed data files")
    fills = {(f["record_id"], f["field"], f["new"]): f for f in s["fills"]}
    # cell diff: exactly the filled cells, nothing else on any organization row
    changed = {(c[1], c[2], c[4]): c for c in s["cells"]}
    want = {}
    for f in s["fills"]:
        want.setdefault((f["record_id"], f["field"]), []).append(f["new"])
    want = {(o, fld): ";".join(sorted(v)) for (o, fld), v in want.items()}
    got = {(c[1], c[2]): c[4] for c in s["cells"]}
    if got != want or len(got) != len(s["cells"]):
        add("cell diff", f"changed cells {sorted(got.items())} differ from the fills {sorted(want.items())}")
    for c in s["cells"]:
        if c[2] not in ("processes", "markets_served"):
            add("cell diff", f"{c[1]} column {c[2]} changed")
    # exact row sets: every appended row is one a fill accounts for, once
    ids = {f["evidence_id"] for f in s["fills"]}
    if len(ids) != len(s["fills"]) or set(s["evidence"]) != ids or s["evidence_n"] != len(ids):
        add("extra rows", f"appended evidence rows ({s['evidence_n']}: {sorted(s['evidence'])}) are not exactly the fills' IDs {sorted(ids)}")
    if set(s["archives"]) != ids or s["archives_n"] != len(ids):
        add("extra rows", f"appended archive rows ({s['archives_n']}: {sorted(s['archives'])}) are not exactly the fills' IDs {sorted(ids)}")
    if [p["evidence_id"] for p in s["proofs"]] != [f["evidence_id"] for f in s["fills"]]:
        add("extra rows", "BINDING_PROOF lines are not exactly the fills, in order")
    # per fill
    seconds = {(r["owner"], r["field"], r["value"]): r for r in s["second"]}
    proofs = {p["evidence_id"]: p for p in s["proofs"]}
    for f in s["fills"]:
        tag = f"{f['record_id']} {f['field']}={f['new']}"
        org = s["orgs"].get(f["record_id"])
        sec = seconds.get((f["record_id"], f["field"], f["new"]))
        if not sec or sec["second_read"] != "VERIFIED" or sec["applied"] != "yes" or sec["gate_bytes_stable"] != "yes":
            add("second read", f"{tag} is not a VERIFIED, applied, byte-stable row")
        if not org or org[f["field"]].strip():
            add("held value", f"{tag}: the base cell is not blank ({org[f['field']] if org else 'no record'!r})")
        allowed = vocab[f["field"]] | (ring3 if f["field"] == "processes" and org and org["ring_primary"] == "3" else set())
        if f["new"] not in allowed:
            add("vocabulary", f"{tag} is not a SCHEMA section 3 token for this record")
        if not org or not gate.own_domain(gate.host_path(f["url"]), gate.host_path(org["website"])):
            add("own page", f"{tag}: {f['url']} is not on the record's own website")
        ev = s["evidence"].get(f["evidence_id"])
        if not ev:
            add("evidence", f"{tag}: no appended evidence row {f['evidence_id']}")
            continue
        head, _, quote = ev["claim_detail"].partition("; quote: ")
        if (ev["record_table"], ev["record_id"], ev["claim_type"], ev["source_class"], ev["source_ref"], ev["tier_effect"],
                ev["created_by"], head) != ("organizations", f["record_id"], "activity", "own_site", f["url"], "supports_B",
                                            LABEL, HEADS[f["field"]].format(v=f["new"])):
            add("evidence", f"{tag}: row {f['evidence_id']} does not name exactly this value, record, page and label")
        if sec and (sec["pilot_sha256"], sec["pilot_offset"]) != (f["capture_sha256"], f["quote_offset"]):
            add("pilot reading", f"{tag}: the capture (sha {f['capture_sha256'][:12]}, offset {f['quote_offset']}) is not the bytes the pilot reader read (sha {sec['pilot_sha256'][:12]}, offset {sec['pilot_offset']})")
        if quote != f["quote"] or (sec and quote != sec["quote"]):
            add("quote", f"{tag}: evidence quote differs from the FILLS and second-read quote")
        if int(f["evidence_id"].split("-")[1]) <= s["greatest"]:
            add("evidence id", f"{f['evidence_id']} is not above the base maximum EVD-{s['greatest']}")
        a = s["archives"].get(f["evidence_id"])
        m = re.fullmatch(r"https://web\.archive\.org/web/(\d{4})(\d\d)(\d\d)\d{6}/(.+)", a["archive_ref"]) if a else None
        if not m or m[4] != f["url"] or a["captured_at"] != f"{m[1]}-{m[2]}-{m[3]}" or a["created_by"] != LABEL:
            add("archive", f"{tag}: archive_links row for {f['evidence_id']} is absent or is not a capture of {f['url']}")
        # capture replay
        try:
            data = bytes_for(f)
        except Exception as e:  # An absent capture is a failure, never a pass.
            add("capture", f"{tag}: cannot inspect: {e}")
            continue
        digest = hashlib.sha256(data).hexdigest()
        if digest != f["capture_sha256"]:
            add("capture sha", f"{tag}: bytes hash to {digest[:12]}, recorded {f['capture_sha256'][:12]}")
        text = gate.capture_text(data)
        if text[int(f["quote_offset"]):][:len(f["quote"])] != f["quote"]:
            add("offset", f"{tag}: the quote is not at offset {f['quote_offset']}")
        if f["quote"] not in text:
            add("quote", f"{tag}: the quote is not in the capture")
        if f"{digest}  provenance/{TASK}/captures/{digest}.html" not in s["inputs"] and digest == f["capture_sha256"]:
            add("inputs", f"{tag}: capture {digest[:12]} is not in INPUTS.sha256")
        p = proofs.get(f["evidence_id"])
        if not p or (p["record_id"], p["capture"], p["capture_sha256"], p["quote_offset"], p["verdict"]) != (
                f["record_id"], f["url"], f["capture_sha256"], f["quote_offset"], "VERIFIED"):
            add("proof", f"{tag}: BINDING_PROOF line is absent or differs from the fill")
        elif p["claim_sha256"] != gate.claim_sha256(ev):
            add("proof", f"{tag}: claim_sha256 does not match the evidence row")
        elif not (gate.family_of_text(p["reader_family"]) and gate.family_of_text(p["reader_family"]) != gate.builder_family(s["readme"])):
            add("proof", f"{tag}: reader and builder are not different known families")
    # trackers and value basis
    claims = {(c["table"], c["record_id"], c["field"], c["verdict"], c["evidence_id"]) for c in s["claims"]}
    expected = {("organizations", f["record_id"], f["field"], "corrected", f["evidence_id"]) for f in s["fills"]}
    if claims != expected:
        add("claims", f"CLAIMS_CHECKED rows differ from the fills by {sorted(claims ^ expected)}")
    keys = {("organizations", f["record_id"], f["field"], f["new"]) for f in s["fills"]}
    added = {r[:4] for r in s["basis_added"]}
    if added != keys or s["basis_removed"] or any(r[4] != "stated" for r in s["basis_added"]):
        add("value basis", f"value_basis.csv added {sorted(added)}, removed {len(s['basis_removed'])}; every filled value must come out stated")
    return out


def fresh_bytes(f):
    return gate.fetch_url(f["url"])


def store_bytes(f):
    return (STORE / "provenance" / TASK / "captures" / f"{f['capture_sha256']}.html").read_bytes()


def plants(s, good):
    """(rule, mutated state, bytes_for): each must fail on exactly the named rule."""
    def mutated(fn):
        t = copy.deepcopy(s)
        fn(t)
        return t
    first = s["fills"][0]
    yield "held value", mutated(lambda t: t["orgs"][first["record_id"]].__setitem__(first["field"], "laminating")), good
    yield "vocabulary", mutated(lambda t: t["fills"][0].__setitem__("new", "not_a_term")), good
    yield "quote", mutated(lambda t: t["fills"][0].__setitem__("quote", "Our FRP pipe is designed and welded to meet pressure classes")), good
    yield "offset", mutated(lambda t: t["fills"][0].__setitem__("quote_offset", str(int(first["quote_offset"]) + 1))), good
    yield "capture sha", s, lambda f: good(f) + b" "
    yield "own page", mutated(lambda t: t["fills"][0].__setitem__("url", "https://www.alphaworld.com/")), good
    def reject(t):  # a whole REJECT row presented as a fill: same record, field and value as the second-read row
        t["fills"][0].update(record_id="ORG-000378", field="markets_served", new="aerospace_defense")
    yield "second read", mutated(reject), good
    yield "cell diff", mutated(lambda t: t["cells"].append(("data/organizations_OH.csv", "ORG-000485", "website", "a", "b"))), good
    yield "files", mutated(lambda t: t["changed"].append("data/sites_OH.csv")), good
    yield "archive", mutated(lambda t: t["archives"].pop(first["evidence_id"])), good
    yield "extra rows", mutated(lambda t: t["evidence"].__setitem__("EVD-999999", dict(t["evidence"][first["evidence_id"]], evidence_id="EVD-999999"))), good
    yield "extra rows", mutated(lambda t: t["archives"].__setitem__("EVD-999999", dict(t["archives"][first["evidence_id"]], evidence_id="EVD-999999"))), good
    yield "extra rows", mutated(lambda t: t.__setitem__("evidence_n", t["evidence_n"] + 1)), good
    yield "extra rows", mutated(lambda t: t["proofs"].append(dict(t["proofs"][0]))), good
    def other_bytes(t):
        for r in t["second"]:
            if (r["owner"], r["value"]) == (first["record_id"], first["new"]):
                r["pilot_sha256"] = "0" * 64
    yield "pilot reading", mutated(other_bytes), good
    def other_offset(t):
        for r in t["second"]:
            if (r["owner"], r["value"]) == (first["record_id"], first["new"]):
                r["pilot_offset"] = str(int(r["pilot_offset"]) + 1)
    yield "pilot reading", mutated(other_offset), good


def main():
    good = fresh_bytes if "--fresh" in sys.argv else store_bytes
    s = load()
    problems = verify(s, good)
    for p in problems:
        print("FAIL", p)
    caught = 0
    for rule, t, source in plants(s, good):
        found = [p for p in verify(t, source) if p.startswith(rule)]
        print(("caught " if found else "MISSED ") + f"planted defect: {rule}")
        caught += bool(found)
    n = len(list(plants(s, good)))
    if problems or caught != n:
        print(f"FAIL: {len(problems)} problem(s); {caught}/{n} planted defects caught")
        return 1
    print(f"PASS: {len(s['fills'])} fills replayed from {'live fetch' if good is fresh_bytes else 'the store'}; {caught}/{n} planted defects caught")
    return 0


if __name__ == "__main__":
    sys.exit(main())
