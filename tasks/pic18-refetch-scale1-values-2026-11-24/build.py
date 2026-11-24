#!/usr/bin/env python3
"""Build the refetch scale-1 value fills: re-fetch each cited page (live page or Wayback id_ capture) through the binding
gate's own fetcher, recompute digest and offset from those bytes, and write the cells, evidence rows, proofs and trackers.

    python3 build.py            plan only: fetch, replay, print (writes nothing)
    python3 build.py --apply    write data/, the capture store and this folder's CSVs

Input is second_read.csv (rows with applied=yes) and ARCHIVES.csv (the archive capture for each live-proof page).
Nothing is written until every applied row replays: the cited bytes must hash to the ledger digest and hold the
reading's quote exactly once at the ledger offset. A row whose page now differs is held, never re-pointed.
"""
import argparse
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
LABEL = f"claude-code {TASK}"
STORE = Path("/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store")
CAPTURES = STORE / "provenance" / TASK / "captures"
OBSERVED = "2026-11-24"
READER = "Codex (OpenAI), refetch scale-1 reader"  # the reading, p3-refetch-scale-1-2026-11-24
ROLE_MAIL = {"info", "sales", "support", "service", "office", "contact", "marketing", "orders", "customerservice",
             "privacy", "admin", "corporate", "testing", "accounting"}  # generic mailboxes; any other address is an individual's
sys.path.insert(0, str(ROOT / "scripts"))
import check_evidence_binding as gate  # noqa: E402  (text, claim and decode helpers only; it is never used to fetch)
import site_corpus  # noqa: E402

PACKET = Path("/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/p3-refetch-scale-1-2026-11-24/captures")
PERSIST = PACKET.parent.parent
CORPUS = site_corpus.Corpus()  # worker fetches go through the declared AtlasSiteCorpus/1.0 route only
READINGS = STORE / "provenance" / TASK / "readings"


def worker_fetch(url):
    """Bytes of a page through scripts/site_corpus.py (robots-gated, declared agent), decoded as the gate decodes."""
    rec = CORPUS.fetch(url)
    if rec["http_status"] != 200:
        raise RuntimeError(f"site_corpus could not fetch {url}: {rec['status']} {rec['http_status']}")
    return gate.decode_capture((CORPUS.cache / rec["raw_file"]).read_bytes(), "")


def resolve(digest, url):
    """Pinned bytes first (the shared store, then the packet's retained captures); else a site_corpus fetch.
    Either way the bytes must hash to the ledger digest, or the row is held."""
    for d in (CAPTURES, PACKET):
        for name in (f"{digest}.html", digest):
            if (d / name).exists():
                data = (d / name).read_bytes()
                assert hashlib.sha256(data).hexdigest() == digest, f"{d / name} does not hash to its name"
                return data
    return worker_fetch(url)


FIELD_HEAD = {"processes": "processes={v}; quote: {q}", "markets_served": "Markets served: {v}; quote: {q}"}
EVIDENCE_COLS = ("evidence_id,record_table,record_id,claim_type,claim_detail,source_class,source_ref,observed_date,"
                 "tier_effect,created_by,notes,address_role").split(",")
WAYBACK = re.compile(r"https://web\.archive\.org/web/(\d{4})(\d\d)(\d\d)\d{6}id_/(.+)")


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def base_ref():
    return git("merge-base", "HEAD", "origin/main").decode().strip()


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def encode(rows, header, ending):
    stream = io.StringIO(newline="")
    w = csv.DictWriter(stream, header, lineterminator=ending)
    w.writeheader()
    w.writerows(rows)
    return stream.getvalue().encode()


def parse(blob):
    """(header, rows, line ending); refuses a file that does not round-trip, so only the filled cells can change."""
    ending = "\r\n" if b"\r\n" in blob else "\n"
    reader = csv.DictReader(io.StringIO(blob.decode(), newline=""))
    rows = list(reader)
    assert encode(rows, reader.fieldnames, ending) == blob, "base CSV does not round-trip"
    return reader.fieldnames, rows, ending


def vocabulary():
    s = (ROOT / "docs/SCHEMA.md").read_text()
    proc = s.split("### 3.1 Processes")[1].split("### 3.2 Materials")[0]
    market = s.split("### 3.3 Markets")[1].split("### 3.4 Certifications")[0]
    terms = lambda v: set(re.findall(r"`([a-z0-9_]+)`", v))
    regular, ring3 = proc.split("Ring 3 services", maxsplit=1)
    return {"processes": terms(regular), "markets_served": terms(market)}, terms(ring3) - {"processes_other_note"}


def locate(base, org_id):
    """(path, row) of the organization in the base tree."""
    for path in git("ls-tree", "--name-only", base, "data/").decode().split():
        if re.fullmatch(r"data/organizations_[A-Z]+\.csv", path):
            header, rows, ending = parse(git("show", f"{base}:{path}"))
            for r in rows:
                if r["org_id"] == org_id:
                    return path, r
    raise KeyError(org_id)


def applied():
    return [r for r in read_csv(HERE / "second_read.csv") if r["applied"] == "yes"]


def individual_mail(data):
    """Any email address in the page source that is not a generic mailbox."""
    return sorted({m for m in re.findall(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", data.decode("utf-8", "replace"), re.I)
                   if m.split("@")[0].lower() not in ROLE_MAIL and not re.search(r"\.(png|jpe?g|gif|svg|webp)$", m, re.I)})


def replay(r):
    """Resolve the cited bytes; return (bytes, digest, offset). Fails unless the ledger's bytes replay."""
    data = resolve(r["apply_sha256"], r["apply_url"])
    digest = hashlib.sha256(data).hexdigest()
    assert digest == r["apply_sha256"], f"{r['owner']} {r['value']}: the page now hashes to {digest[:12]}, the ledger says {r['apply_sha256'][:12]}"
    text = gate.capture_text(data)
    assert text.count(r["quote"]) == 1, f"{r['owner']} {r['value']}: quote occurs {text.count(r['quote'])} times"
    assert text.index(r["quote"]) == int(r["apply_offset"]), f"{r['owner']} {r['value']}: quote moved to {text.index(r['quote'])}"
    assert not individual_mail(data), f"{r['owner']} {r['value']}: the capture holds an individual's email {individual_mail(data)}"
    return data, digest, text.index(r["quote"])


def pin_reading(r, cited):
    """The first reader's capture, by digest, kept in the store so the check can compare windows. Returns its bytes."""
    if r["reading_sha256"] == r["apply_sha256"]:
        return cited
    frame = next(f for f in read_csv(HERE / "FRAME.csv") if (f["record_id"], f["field"], f["value"], f["url"], f["offset"]) == (
        r["owner"], r["field"], r["value"], r["url"], r["reading_offset"]))
    data = (PERSIST / frame["capture_file"]).read_bytes()
    assert hashlib.sha256(data).hexdigest() == r["reading_sha256"], f"{frame['capture_file']} is not the reading's digest"
    assert not individual_mail(data), f"reading capture of {r['owner']} holds an individual's email"
    assert gate.capture_text(data)[int(r["reading_offset"]):][:len(r["quote"])] == r["quote"]
    return data


def id_form(ref):
    return re.sub(r"/web/(\d{14})/", r"/web/\1id_/", ref, count=1)


def archive_for(r, archives):
    """(archive_ref, captured_at) for the evidence row: the proof capture itself for a Wayback route, else ARCHIVES.csv."""
    m = WAYBACK.fullmatch(r["apply_url"])
    if m:
        assert m[4] == r["url"], f"{r['apply_url']} is not a capture of {r['url']}"
        ref, day = r["apply_url"].replace("id_/", "/", 1), f"{m[1]}-{m[2]}-{m[3]}"
        assert day == r["archive_captured_at"]
        return ref, day
    a = archives[r["url"]]
    cap = WAYBACK.fullmatch(id_form(a["archive_ref"]))
    assert cap and cap[4] == r["url"] and a["captured_at"] == f"{cap[1]}-{cap[2]}-{cap[3]}", f"ARCHIVES.csv row for {r['url']} is malformed"
    held = gate.capture_text(worker_fetch(id_form(a["archive_ref"]))).count(r["quote"])
    assert held >= 1, f"the archive capture {a['archive_ref']} does not hold the quote"
    return a["archive_ref"], a["captured_at"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    base = base_ref()
    vocab, ring3 = vocabulary()
    rows = applied()
    archives = {a["url"]: a for a in read_csv(HERE / "ARCHIVES.csv")}
    greatest = max(int(e["evidence_id"].split("-")[1]) for p in git("ls-tree", "--name-only", base, "data/").decode().split()
                   if re.fullmatch(r"data/evidence_[A-Za-z_]+\.csv", p) for e in read_csv_blob(base, p))
    plan, cells = [], {}
    for n, r in enumerate(rows, start=1):
        assert r["second_read"] == "VERIFIED"
        path, org = locate(base, r["owner"])
        assert not org[r["field"]].strip(), f"{r['owner']} {r['field']} is held: {org[r['field']]!r}"
        allowed = vocab[r["field"]] | (ring3 if r["field"] == "processes" and org["ring_primary"] == "3" else set())
        assert r["value"] in allowed, f"{r['value']} is outside the vocabulary for {r['owner']}"
        assert gate.own_domain(gate.host_path(r["url"]), gate.host_path(org["website"])), f"{r['url']} is not {r['owner']}'s site"
        data, digest, offset = replay(r)
        reading = pin_reading(r, data)
        ref, day = archive_for(r, archives)
        wayback = bool(WAYBACK.fullmatch(r["apply_url"]))
        plan.append(dict(r, path=path, evidence_id=f"EVD-{greatest + n:06d}", digest=digest, offset=offset, data=data,
                         shard=path.split("_")[-1][:-4], ring=org["ring_primary"], reading=reading, archive_ref=ref, archive_day=day,
                         capture_date=day if wayback else OBSERVED))
        cells.setdefault((path, r["owner"], r["field"]), []).append(r["value"])
        print(f"{r['owner']} {r['field']}={r['value']} {r['apply_route']} offset {offset} sha {digest[:12]} ({len(data)} bytes) archive {ref[-40:]}")
    if not args.apply:
        return
    CAPTURES.mkdir(parents=True, exist_ok=True)
    for p in plan:
        f = CAPTURES / f"{p['digest']}.html"
        if f.exists():
            assert f.read_bytes() == p["data"], f"{f} exists with other bytes"
        else:
            f.write_bytes(p["data"])
    READINGS.mkdir(parents=True, exist_ok=True)
    for p in plan:
        (READINGS / f"{p['reading_sha256']}.html").write_bytes(p["reading"])
    for path in sorted({k[0] for k in cells}):
        header, org_rows, ending = parse(git("show", f"{base}:{path}"))
        by_id = {o["org_id"]: o for o in org_rows}
        for (pth, oid, field), values in cells.items():
            if pth == path:
                by_id[oid][field] = ";".join(sorted(values))
        (ROOT / path).write_bytes(encode(org_rows, header, ending))
    by_shard = {}
    for p in plan:
        detail = FIELD_HEAD[p["field"]].format(v=p["value"], q=p["quote"])
        ev = dict(evidence_id=p["evidence_id"], record_table="organizations", record_id=p["owner"], claim_type="activity",
                  claim_detail=detail, source_class="own_site", source_ref=p["url"], observed_date=OBSERVED,
                  tier_effect="supports_B", created_by=LABEL,
                  notes="Reading by Codex (p3-refetch-scale-1-2026-11-24); second read by Claude; capture is the gate fetch of the cited page.",
                  address_role="")
        p["ev"] = ev
        by_shard.setdefault(f"data/evidence_organizations_{p['shard']}.csv", []).append(ev)
    for path, evs in by_shard.items():
        old = git("show", f"{base}:{path}")
        ending = "\r\n" if old.endswith(b"\r\n") else "\n"
        assert old.endswith(b"\n")
        (ROOT / path).write_bytes(old + _body(evs, ending))
    old = git("show", f"{base}:data/archive_links.csv")
    ending = "\r\n" if old.endswith(b"\r\n") else "\n"
    assert old.endswith(b"\n")
    stream = io.StringIO(newline="")
    csv.DictWriter(stream, ["evidence_id", "archive_ref", "captured_at", "created_by"], lineterminator=ending).writerows(
        [dict(evidence_id=p["evidence_id"], archive_ref=p["archive_ref"], captured_at=p["archive_day"], created_by=LABEL) for p in plan])
    (ROOT / "data/archive_links.csv").write_bytes(old + stream.getvalue().encode())
    write(HERE / "BINDING_PROOF.csv", [dict(evidence_id=p["evidence_id"], record_id=p["owner"],
          claim_sha256=gate.claim_sha256(p["ev"]), capture=p["apply_url"], capture_date=p["capture_date"], capture_sha256=p["digest"],
          quote_offset=p["offset"], verdict="VERIFIED", reader_family=READER, reader_date=OBSERVED) for p in plan],
          list(gate.PROOF_COLS))
    write(HERE / "FILLS.csv", [dict(record_id=p["owner"], shard=p["path"], field=p["field"], old="", new=p["value"],
          evidence_id=p["evidence_id"], url=p["url"], route=p["apply_route"], capture=p["apply_url"], capture_sha256=p["digest"],
          quote_offset=p["offset"], quote=p["quote"]) for p in plan])
    write(HERE / "CLAIMS_CHECKED.csv", [dict(table="organizations", record_id=p["owner"], field=p["field"],
          verdict="corrected", evidence_id=p["evidence_id"]) for p in plan])
    (HERE / "INPUTS.sha256").write_text("".join(
        [f"{d}  provenance/{TASK}/captures/{d}.html\n" for d in sorted({p['digest'] for p in plan})]
        + [f"{d}  provenance/{TASK}/readings/{d}.html\n" for d in sorted({p['reading_sha256'] for p in plan} - {p['digest'] for p in plan})]))
    subprocess.check_call([sys.executable, str(ROOT / "scripts/value_basis.py")], cwd=ROOT)
    print(f"applied {len(plan)} value(s) on {len({p['owner'] for p in plan})} owner(s)")


def read_csv_blob(base, path):
    return list(csv.DictReader(io.StringIO(git("show", f"{base}:{path}").decode(), newline="")))


def _body(rows, ending):
    stream = io.StringIO(newline="")
    csv.DictWriter(stream, EVIDENCE_COLS, lineterminator=ending).writerows(rows)
    return stream.getvalue().encode()


def write(path, rows, fields=None):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fields or list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
