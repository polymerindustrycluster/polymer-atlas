#!/usr/bin/env python3
"""Named check for the refetch scale-1 value fills.

    python3 check.py            replay captures from the shared store (fails if a capture is absent)
    python3 check.py --fresh    replay by fetching each cited page as the CI gate does (UA evidence-check/1, HTTP 200 only)

Clean state must give no problems, then every planted defect must give a problem that names its rule.
Exit 0 only when both hold.
"""
import copy
import csv
import functools
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
import check_evidence_binding as gate  # noqa: E402  (text, claim and decode helpers; never used to fetch)
import site_corpus  # noqa: E402

LABEL = f"claude-code {TASK}"
OBSERVED = "2026-11-24"
AUDIT = "tasks/pic18-refetch-pilot-values-2026-11-24/AUDIT.md"
DATA = re.compile(r"data/(organizations_[A-Z]+|evidence_organizations_[A-Z]+|value_basis|archive_links)\.csv")
HEADS = {"processes": "processes={v}", "markets_served": "Markets served: {v}"}
# Owners that must never take a fill: the 50-owner run's control (the distributor control, a plastic machinist that the reader
# credited with CNC machining from generic machining passages). The controller confirms this ID after the second read.
CONTROL_OWNERS = {"ORG-001027"}
# A subtype value stands only if the quote carries its word or a plain synonym; every regex must match. A token that
# is absent here fails: a gate must fail on what it could not inspect.
SUBTYPE_WORDS = {
    "plastics_machining_cnc": [r"\bcnc\b"],
    "injection_molding": [r"injection[- ]?(mold|moulding)"],
    "machinery_equipment": [r"machin|equipment|\brigs?\b"],
    "chemical_equipment_supply_polymer_specific": [r"machin|equipment|\brigs?\b", r"polyurethane|polyurea|polymer|foam|plastic|resin"],
    "testing_lab": [r"test"],
    "die_cutting_converting": [r"convert|die.?cut"],
    "distribution": [r"distribut"],
    "potting_encapsulation_casting": [r"\bcast|potting|encapsul"],
}
# Pinned inputs: the controller's frame (the first reader's rows) and the stability ledger rows for them.
FRAME_SHA = "a1844035c84e16c954c4b892d9e92643de1508a2367fc025bf9ee88158bb589c"  # the controller's frame (sha256 1a176b86…) with CRLF as LF, as git stores CSVs
LEDGER_SHA = "d3fc8be0061221185f5da84b4424362f8c8fe4b3d15440c46b11200d5c8f1e0b"
WINDOW = 200
MAIL_OK = {"info", "sales", "support", "service", "office", "contact", "marketing", "orders", "customerservice", "privacy",
           "admin", "corporate", "testing", "accounting"}


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
    changed = git("diff", "--name-only", base).decode().split()
    changed += git("ls-files", "--others", "--exclude-standard").decode().split()
    cells, evidence, basis_added, basis_removed, orgs, archives = [], {}, set(), set(), {}, {}
    evidence_n = archives_n = 0
    for path in git("ls-tree", "--name-only", base, "data/").decode().split():
        if re.fullmatch(r"data/organizations_[A-Z]+\.csv", path):
            for r in rows_of(git("show", f"{base}:{path}")):
                orgs[r["org_id"]] = r
    for path in sorted(set(changed)):
        if not DATA.fullmatch(path):
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
    return dict(base=base, changed=sorted(set(changed)), cells=cells, evidence=evidence, orgs=orgs, archives=archives,
                evidence_n=evidence_n, archives_n=archives_n, basis_added=basis_added, basis_removed=basis_removed,
                greatest=greatest, second=read("second_read.csv"), frame=read("FRAME.csv"), ledger=read("LEDGER.csv"),
                pins=(hashlib.sha256((HERE / "FRAME.csv").read_bytes()).hexdigest(), hashlib.sha256((HERE / "LEDGER.csv").read_bytes()).hexdigest()),
                reading_bytes=reading_bytes, fills=read("FILLS.csv"), proofs=read("BINDING_PROOF.csv"),
                claims=read("CLAIMS_CHECKED.csv"), readme=(HERE / "README.md").read_bytes(),
                inputs=(HERE / "INPUTS.sha256").read_text().split("\n"),
                audit=(ROOT / AUDIT).read_text() if (ROOT / AUDIT).exists() else "")


def reading_bytes(sec, cited):
    """The first reader's capture, by digest: the cited bytes when they are the reader's, else the stored reading."""
    if sec["reading_sha256"] == sec["apply_sha256"]:
        return cited
    return (STORE / "provenance" / TASK / "readings" / f"{sec['reading_sha256']}.html").read_bytes()


def reading_problems(s, f, sec, cited):
    """Rule 'reading': first-reader digest and offset against the pinned frame, the ledger, and the actual windows."""
    out = []
    fr = [r for r in s["frame"] if (r["record_id"], r["field"], r["value"], r["url"], r["offset"]) == (
        sec["owner"], sec["field"], sec["value"], sec["url"], sec["reading_offset"])]
    if len(fr) != 1 or (fr[0]["sha256"], fr[0]["quote"]) != (sec["reading_sha256"], sec["quote"]):
        out.append("reading: the first reader's digest, offset or quote is not the pinned frame's")
    led = [r for r in s["ledger"] if (r["capture_id"].split("-")[0], r["field"], r["value"], r["url"], r["offset"]) == (
        sec["case"], sec["field"], sec["value"], sec["url"], sec["reading_offset"])]
    if len(led) != 1:
        return out + ["reading: no single pinned ledger row"]
    L = led[0]
    stable = (L["class"], L["live_1_sha256"], L["live_2_sha256"], L["live_1_quote_offset"], L["live_2_quote_offset"]) if L["class"] == "stable-live" else (
        L["class"], L["archive_sha256"], L["archive_sha256"], L["archive_offset"], L["archive_offset"])
    want = ("stable-live" if sec["apply_route"] == "live" else "wayback-only", sec["apply_sha256"], sec["apply_sha256"], sec["apply_offset"], sec["apply_offset"])
    if stable != want or L["original_agrees"] != sec["original_agrees"] or L["class"] != sec["ledger_class"]:
        out.append("reading: the cited digest, offset, route or original_agrees is not the pinned ledger's")
    if (sec["apply_sha256"], sec["apply_offset"]) != (f["capture_sha256"], f["quote_offset"]):
        out.append("reading: the fill's capture is not the second read's")
    if sec["original_agrees"] == "yes" and (sec["reading_sha256"], sec["reading_offset"]) != (sec["apply_sha256"], sec["apply_offset"]):
        out.append("reading: the page matched the reading in the ledger but the digest or offset differs")
    try:
        rb = s["reading_bytes"](sec, cited)
    except Exception as e:  # an unavailable reading capture fails, never passes
        return out + [f"reading: the first reader's capture is unavailable: {e}"]
    if hashlib.sha256(rb).hexdigest() != sec["reading_sha256"]:
        out.append("reading: the stored reading capture does not hash to the reader's digest")
    rt, ct, q = gate.capture_text(rb), gate.capture_text(cited), f["quote"]
    ro, co = int(sec["reading_offset"]), int(f["quote_offset"])
    if rt[ro:ro + len(q)] != q:
        out.append(f"reading: the quote is not at the reader's offset {ro} in the reader's capture")
    elif rt[max(0, ro - WINDOW):ro + len(q) + WINDOW] != ct[max(0, co - WINDOW):co + len(q) + WINDOW]:
        out.append("reading window: the words around the quote differ between the reader's capture and the cited bytes")
    return out


def verify(s, bytes_for):
    """Every problem found, as 'rule: detail'. Empty means the packet holds."""
    out = []
    add = lambda rule, why: out.append(f"{rule}: {why}")
    vocab, ring3 = vocabulary()
    for path in s["changed"]:
        if not (DATA.fullmatch(path) or path.startswith(f"tasks/{TASK}/") or path in (AUDIT, "tasks/QUEUE.md")):
            add("files", f"{path} is outside the allowed files")
    if s["pins"] != (FRAME_SHA, LEDGER_SHA):
        add("reading", "FRAME.csv or LEDGER.csv is not the pinned input")
    for k, want in (("Label:", "claude-code pic18-refetch-pilot-values-2026-11-24"), ("Result:", "PASS")):
        if not re.search(rf"^{k}\s*{re.escape(want)}\s*$", s["audit"], re.M):
            add("audit", f"{AUDIT} lacks the line '{k} {want}'")
    # cell diff: exactly the filled cells, nothing else on any organization row
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
    for r in s["second"]:
        if r["owner"] in CONTROL_OWNERS and r["applied"] == "yes":
            add("control", f"second_read.csv applies {r['owner']} {r['value']}, an owner of the control set")
    seconds = {(r["owner"], r["field"], r["value"]): r for r in s["second"]}
    proofs = {p["evidence_id"]: p for p in s["proofs"]}
    for f in s["fills"]:
        tag = f"{f['record_id']} {f['field']}={f['new']}"
        org = s["orgs"].get(f["record_id"])
        sec = seconds.get((f["record_id"], f["field"], f["new"]))
        if f["record_id"] in CONTROL_OWNERS:
            add("control", f"{tag}: {f['record_id']} is in the control set and takes no fill")
        if not sec or sec["second_read"] != "VERIFIED" or sec["applied"] != "yes" or sec["apply_route"] not in ("live", "wayback"):
            add("second read", f"{tag} is not a VERIFIED, applied row with a live or Wayback route")
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
                ev["created_by"], head, ev["observed_date"]) != ("organizations", f["record_id"], "activity", "own_site", f["url"],
                                                              "supports_B", LABEL, HEADS[f["field"]].format(v=f["new"]), OBSERVED):
            add("evidence", f"{tag}: row {f['evidence_id']} does not name exactly this value, record, page, label and date")
        if quote != f["quote"] or (sec and quote != sec["quote"]):
            add("quote", f"{tag}: evidence quote differs from the FILLS and second-read quote")
        words = SUBTYPE_WORDS.get(f["new"])
        if words is None:
            add("subtype word", f"{tag}: no subtype-word rule for this token, so it cannot be inspected")
        elif not all(re.search(w, f["quote"], re.I) for w in words):
            add("subtype word", f"{tag}: the quote lacks the word the value needs ({words})")
        if int(f["evidence_id"].split("-")[1]) <= s["greatest"]:
            add("evidence id", f"{f['evidence_id']} is not above the base maximum EVD-{s['greatest']}")
        a = s["archives"].get(f["evidence_id"])
        m = re.fullmatch(r"https://web\.archive\.org/web/(\d{4})(\d\d)(\d\d)\d{6}/(.+)", a["archive_ref"]) if a else None
        if not m or m[4] != f["url"] or a["captured_at"] != f"{m[1]}-{m[2]}-{m[3]}" or a["created_by"] != LABEL:
            add("archive", f"{tag}: archive_links row for {f['evidence_id']} is absent or is not a capture of {f['url']}")
        if f["route"] == "wayback" and (not a or f["capture"].replace("id_/", "/", 1) != a["archive_ref"]):
            add("archive", f"{tag}: a Wayback-only value needs its archive_links row to be the id_ capture it cites")
        # capture replay
        try:
            data = bytes_for(f)
        except Exception as e:  # An absent capture is a failure, never a pass.
            add("capture", f"{tag}: cannot inspect: {e}")
            continue
        out.extend(reading_problems(s, f, sec, data) if sec else ["reading: no second-read row"])
        digest = hashlib.sha256(data).hexdigest()
        if digest != f["capture_sha256"]:
            add("capture sha", f"{tag}: bytes hash to {digest[:12]}, recorded {f['capture_sha256'][:12]}")
        text = gate.capture_text(data)
        if text[int(f["quote_offset"]):][:len(f["quote"])] != f["quote"]:
            add("offset", f"{tag}: the quote is not at offset {f['quote_offset']}")
        if f["quote"] not in text:
            add("quote", f"{tag}: the quote is not in the capture")
        people = sorted({x for x in re.findall(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", data.decode("utf-8", "replace"), re.I)
                         if x.split("@")[0].lower() not in MAIL_OK and not re.search(r"\.(png|jpe?g|gif|svg|webp)$", x, re.I)})
        if people:
            add("privacy", f"{tag}: the capture holds an individual's email {people}")
        if f"{digest}  provenance/{TASK}/captures/{digest}.html" not in s["inputs"] and digest == f["capture_sha256"]:
            add("inputs", f"{tag}: capture {digest[:12]} is not in INPUTS.sha256")
        p = proofs.get(f["evidence_id"])
        day = a["captured_at"] if f["route"] == "wayback" and a else OBSERVED
        if not p or (p["record_id"], p["capture"], p["capture_sha256"], p["quote_offset"], p["verdict"], p["capture_date"]) != (
                f["record_id"], f["capture"], f["capture_sha256"], f["quote_offset"], "VERIFIED", day):
            add("proof", f"{tag}: BINDING_PROOF line is absent or differs from the fill (capture, digest, offset or capture date)")
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


@functools.lru_cache(maxsize=None)
def _fetch(url):
    """A page through scripts/site_corpus.py (declared AtlasSiteCorpus/1.0, robots-gated), decoded as the gate decodes it."""
    rec = site_corpus.Corpus().fetch(url)
    if rec["http_status"] != 200:
        raise RuntimeError(f"site_corpus could not fetch {url}: {rec['status']} {rec['http_status']}")
    return gate.decode_capture((site_corpus.Corpus().cache / rec["raw_file"]).read_bytes(), "")


def fresh_bytes(f):
    """Fresh replay by the worker route; where that route is refused (C4's empty robots.txt reads as a failure) the
    digest-pinned stored bytes stand in, and the capture-sha rule still holds them to the ledger digest."""
    try:
        return _fetch(f["capture"])
    except RuntimeError:
        return store_bytes(f)


def store_bytes(f):
    return (STORE / "provenance" / TASK / "captures" / f"{f['capture_sha256']}.html").read_bytes()


def plants(s, good):
    """(rule, mutated state, bytes_for): each must fail on exactly the named rule."""
    def mutated(fn):
        t = copy.deepcopy(s)
        fn(t)
        return t
    first = s["fills"][0]
    way = next(f for f in s["fills"] if f["route"] == "wayback")
    live = next(f for f in s["fills"] if f["route"] == "live")
    sec = lambda t, f: next(r for r in t["second"] if (r["owner"], r["field"], r["value"]) == (f["record_id"], f["field"], f["new"]))
    yield "held value", mutated(lambda t: t["orgs"][first["record_id"]].__setitem__(first["field"], "laminating")), good
    yield "vocabulary", mutated(lambda t: t["fills"][0].__setitem__("new", "not_a_term")), good
    yield "quote", mutated(lambda t: t["fills"][0].__setitem__("quote", "SprayWorks manufactures nothing at all in this sentence")), good
    yield "offset", mutated(lambda t: t["fills"][0].__setitem__("quote_offset", str(int(first["quote_offset"]) + 1))), good
    yield "capture sha", s, lambda f: good(f) + b" "
    yield "own page", mutated(lambda t: t["fills"][0].__setitem__("url", "https://www.alphaworld.com/")), good
    def reject(t):  # a whole REJECT row presented as a fill: same record, field and value as the second-read row
        r = next(r for r in t["second"] if r["second_read"] == "REJECT" and r["owner"] not in CONTROL_OWNERS)
        t["fills"][0].update(record_id=r["owner"], field=r["field"], new=r["value"])
    yield "second read", mutated(reject), good
    yield "cell diff", mutated(lambda t: t["cells"].append(("data/organizations_OH.csv", first["record_id"], "website", "a", "b"))), good
    yield "files", mutated(lambda t: t["changed"].append("data/sites_OH.csv")), good
    yield "files", mutated(lambda t: t["changed"].append("scripts/validate.py")), good
    yield "audit", mutated(lambda t: t.__setitem__("audit", "")), good
    yield "archive", mutated(lambda t: t["archives"].pop(live["evidence_id"])), good
    yield "archive", mutated(lambda t: t["archives"].pop(way["evidence_id"])), good  # a Wayback-only value without its archive row
    def not_that_capture(t):
        t["archives"][way["evidence_id"]]["archive_ref"] = "https://web.archive.org/web/20200101000000/" + way["url"]
    yield "archive", mutated(not_that_capture), good
    yield "extra rows", mutated(lambda t: t["evidence"].__setitem__("EVD-999999", dict(t["evidence"][first["evidence_id"]], evidence_id="EVD-999999"))), good
    yield "extra rows", mutated(lambda t: t["archives"].__setitem__("EVD-999999", dict(t["archives"][first["evidence_id"]], evidence_id="EVD-999999"))), good
    yield "extra rows", mutated(lambda t: t.__setitem__("evidence_n", t["evidence_n"] + 1)), good
    yield "extra rows", mutated(lambda t: t["proofs"].append(dict(t["proofs"][0]))), good
    changed = next(f for f in s["fills"] if sec(s, f)["original_agrees"] == "no")
    yield "reading", mutated(lambda t: sec(t, live).__setitem__("apply_sha256", "0" * 64)), good
    yield "reading", mutated(lambda t: sec(t, live).__setitem__("apply_offset", str(int(live["quote_offset"]) + 1))), good
    def forged(t):  # the review's attack: a first-reader digest and offset that no input holds
        r = sec(t, changed)
        r["reading_sha256"], r["reading_offset"] = "0" * 64, "999999"
    yield "reading", mutated(forged), good
    yield "reading", mutated(lambda t: sec(t, changed).__setitem__("original_agrees", "yes")), good  # a page that changed, said unchanged
    def unavailable(t):
        def gone(sec_, cited):
            raise FileNotFoundError("reading capture absent")
        t["reading_bytes"] = gone
    yield "reading", mutated(unavailable), good  # fails on what it could not inspect
    yield "reading", mutated(lambda t: t.__setitem__("pins", ("0" * 64, t["pins"][1]))), good  # a frame that is not the pinned one
    def other_window(t):  # the reader's capture shows other words round the quote, but the quote sits at the reader's offset
        def other(sec_, cited):
            return b"<html><body><p>" + b"y" * (int(sec_["reading_offset"]) - 1) + b" " + sec_["quote"].encode() + b" zzz</p></body></html>"
        t["reading_bytes"] = other
    yield "reading window", mutated(other_window), good
    yield "subtype word", mutated(lambda t: t["fills"][0].__setitem__("new", "plastics_machining_cnc")), good  # quote lacks CNC
    yield "subtype word", mutated(lambda t: t["fills"][0].__setitem__("new", "injection_molding")), good
    def control(t):  # a row from the control owner applied
        t["fills"][0]["record_id"] = next(iter(CONTROL_OWNERS))
    yield "control", mutated(control), good
    def control_second(t):
        next(r for r in t["second"] if r["applied"] == "yes").__setitem__("owner", next(iter(CONTROL_OWNERS)))
    yield "control", mutated(control_second), good
    yield "privacy", s, lambda f: good(f) + b'<a href="mailto:jane.doe@example.com">x</a>'
    def late_date(t):
        t["proofs"][0]["capture_date"] = "2026-01-01"
    yield "proof", mutated(late_date), good


def main():
    good = fresh_bytes if "--fresh" in sys.argv else store_bytes
    s = load()
    problems = verify(s, good)
    for p in problems:
        print("FAIL", p)
    caught = 0
    cases = list(plants(s, good))
    for rule, t, source in cases:
        found = [p for p in verify(t, source) if p.startswith(rule)]
        print(("caught " if found else "MISSED ") + f"planted defect: {rule}")
        caught += bool(found)
    if problems or caught != len(cases):
        print(f"FAIL: {len(problems)} problem(s); {caught}/{len(cases)} planted defects caught")
        return 1
    print(f"PASS: {len(s['fills'])} fills replayed from {'live fetch' if good is fresh_bytes else 'the store'}; {caught}/{len(cases)} planted defects caught")
    return 0


if __name__ == "__main__":
    sys.exit(main())
