#!/usr/bin/env python3
"""Own-site market fills for the LinkedIn reading pilot's owners (owner ruling 2026-11-25 20:51, "Leads only, refetch sites").

    python3 build.py --prepare DIR   SPEC.csv and the decoded captures in DIR -> CANDIDATES.csv (digest, offset); the rows for the second reader
    python3 build.py --apply         CANDIDATES.csv and READS.csv (a VERIFIED line per row) -> data/, proofs and trackers

Nothing is fetched here. The captures were read once through the project's transport (scripts/site_corpus.py, declared agent),
gzip-decoded with the binding gate's own decode_capture, and are replayed from the pinned files: DIR, or the shared store
provenance/<task>/captures/<sha256>.html. A row that is not VERIFIED in READS.csv is never applied.
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
OBSERVED = "2026-11-25"  # the day the pages were read
FIRST_ID = 483150  # PR #569 holds EVD-483144 to EVD-483149; allocate above it whatever the base maximum is
STORE = Path("/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store/provenance") / TASK / "captures"
WAYBACK = re.compile(r"https://web\.archive\.org/web/(\d{4})(\d\d)(\d\d)(\d{6})id_/(.+)")
ROLE_MAIL = {"info", "sales", "support", "service", "office", "contact", "marketing", "orders", "customerservice",
             "privacy", "admin", "corporate", "testing", "accounting"}
MAIL_EXCEPTION = {"cmc@chem-materials.com": "the company's general mailbox: the initials of Chem-Materials Company"}
NOTES = {
    "ORG-001936": "Wayback capture, not the live page: the page's bytes changed between 2026-11-16 and 2026-11-25 (as #559 did for Sprayworks). The capture is the one Wayback resolves the 2026-06-17 timestamp to.",
    "ORG-001497": "Wayback capture: the live page was unreadable on 2026-11-25 (curl empty reply on HTTP/2 and on HTTP/1.1).",
    "ORG-000147": "Wayback capture: the live page was unreadable on 2026-11-25 (curl empty reply on HTTP/2 and on HTTP/1.1).",
}
EVIDENCE_COLS = ("evidence_id,record_table,record_id,claim_type,claim_detail,source_class,source_ref,observed_date,"
                 "tier_effect,created_by,notes,address_role").split(",")
CAND_COLS = ["owner", "value", "url", "capture", "capture_date", "capture_sha256", "quote_offset", "quote"]
sys.path.insert(0, str(ROOT / "scripts"))
import check_evidence_binding as gate  # noqa: E402  (text, claim and decode helpers only; never used to fetch)


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


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


def market_vocabulary():
    s = (ROOT / "docs/SCHEMA.md").read_text()
    return set(re.findall(r"`([a-z0-9_]+)`", s.split("### 3.3 Markets")[1].split("### 3.4 Certifications")[0]))


def locate(base, org_id):
    for path in git("ls-tree", "--name-only", base, "data/").decode().split():
        if re.fullmatch(r"data/organizations_[A-Z]+\.csv", path):
            for r in parse(git("show", f"{base}:{path}"))[1]:
                if r["org_id"] == org_id:
                    return path, r
    raise KeyError(org_id)


def individual_mail(data):
    found = {m.lower() for m in re.findall(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", data.decode("utf-8", "replace"), re.I)
             if m.split("@")[0].lower() not in ROLE_MAIL and not re.search(r"\.(png|jpe?g|gif|svg|webp)$", m, re.I)}
    return sorted(found - set(MAIL_EXCEPTION))


def pinned(digest, *dirs):
    for d in dirs:
        f = Path(d) / f"{digest}.html"
        if f.exists():
            data = f.read_bytes()
            assert hashlib.sha256(data).hexdigest() == digest, f"{f} does not hash to its name"
            return data
    raise FileNotFoundError(f"capture {digest} is in none of {[str(d) for d in dirs]}")


def verify_row(base, r, data):
    """Every mechanical fact a row rests on, from the pinned bytes. Returns the org's (path, record)."""
    path, org = locate(base, r["owner"])
    assert not org["markets_served"].strip(), f"{r['owner']} markets_served is held: {org['markets_served']!r}"
    assert r["value"] in market_vocabulary(), f"{r['value']} is not a markets_served term"
    assert gate.own_domain(gate.host_path(r["url"]), gate.host_path(org["website"])), f"{r['url']} is not {r['owner']}'s site"
    m = WAYBACK.fullmatch(r["capture"])
    assert m and gate.same_page(m[5], r["url"]) and f"{m[1]}-{m[2]}-{m[3]}" == r["capture_date"], f"{r['capture']} is not a Wayback capture of {r['url']}"
    text = gate.capture_text(data)
    assert hashlib.sha256(data).hexdigest() == r["capture_sha256"]
    assert text.count(r["quote"]) == 1 and text.index(r["quote"]) == int(r["quote_offset"]), f"{r['owner']}: the quote is not once at its offset"
    assert len(" ".join(r["quote"].split())) >= 20
    assert not individual_mail(data), f"{r['owner']}: the capture holds an individual's email {individual_mail(data)}"
    return path, org


def prepare(src):
    base = git("merge-base", "HEAD", "origin/main").decode().strip()
    out = []
    for s in read_csv(HERE / "SPEC.csv"):
        data = (Path(src) / s["capture_file"]).read_bytes()
        m = WAYBACK.fullmatch(s["capture"])
        row = dict(owner=s["owner"], value=s["value"], url=s["url"], capture=s["capture"], capture_date=f"{m[1]}-{m[2]}-{m[3]}",
                   capture_sha256=hashlib.sha256(data).hexdigest(), quote_offset=gate.capture_text(data).index(s["quote"]), quote=s["quote"])
        verify_row(base, row, data)
        (Path(src) / f"{row['capture_sha256']}.html").write_bytes(data)
        out.append(row)
    write_csv(HERE / "CANDIDATES.csv", out, CAND_COLS)
    print(f"{len(out)} candidate rows on {len({r['owner'] for r in out})} owners written")


def apply(captures):
    base = git("merge-base", "HEAD", "origin/main").decode().strip()
    reads = {(r["owner"], r["value"]): r for r in read_csv(HERE / "READS.csv")}
    rows = [r for r in read_csv(HERE / "CANDIDATES.csv") if reads.get((r["owner"], r["value"]), {}).get("verdict") == "VERIFIED"]
    assert rows, "no VERIFIED rows in READS.csv"
    greatest = max(int(e["evidence_id"].split("-")[1]) for p in git("ls-tree", "--name-only", base, "data/").decode().split()
                   if re.fullmatch(r"data/evidence_[A-Za-z_]+\.csv", p) for e in parse(git("show", f"{base}:{p}"))[1])
    greatest = max(greatest, FIRST_ID - 1)
    plan, cells = [], {}
    for n, r in enumerate(rows, start=1):
        data = pinned(r["capture_sha256"], *captures)
        path, org = verify_row(base, r, data)
        plan.append(dict(r, path=path, shard=path.split("_")[-1][:-4], evidence_id=f"EVD-{greatest + n:06d}"))
        cells.setdefault((path, r["owner"]), []).append(r["value"])
    for path in sorted({k[0] for k in cells}):
        header, org_rows, ending = parse(git("show", f"{base}:{path}"))
        by_id = {o["org_id"]: o for o in org_rows}
        for (pth, oid), values in cells.items():
            if pth == path:
                by_id[oid]["markets_served"] = ";".join(sorted(values))
        (ROOT / path).write_bytes(encode(org_rows, header, ending))
    by_shard = {}
    for p in plan:
        p["ev"] = dict(evidence_id=p["evidence_id"], record_table="organizations", record_id=p["owner"], claim_type="activity",
                       claim_detail=f"Markets served: {p['value']} (Wayback capture); quote: {p['quote']}", source_class="own_site",
                       source_ref=p["url"], observed_date=OBSERVED, tier_effect="supports_B", created_by=LABEL,
                       notes=NOTES[p["owner"]], address_role="")
        by_shard.setdefault(f"data/evidence_organizations_{p['shard']}.csv", []).append(p["ev"])
    for path, evs in by_shard.items():
        old = git("show", f"{base}:{path}")
        ending = "\r\n" if old.endswith(b"\r\n") else "\n"
        stream = io.StringIO(newline="")
        csv.DictWriter(stream, EVIDENCE_COLS, lineterminator=ending).writerows(evs)
        (ROOT / path).write_bytes(old + stream.getvalue().encode())
    old = git("show", f"{base}:data/archive_links.csv")
    ending = "\r\n" if old.endswith(b"\r\n") else "\n"
    stream = io.StringIO(newline="")
    csv.DictWriter(stream, ["evidence_id", "archive_ref", "captured_at", "created_by"], lineterminator=ending).writerows(
        [dict(evidence_id=p["evidence_id"], archive_ref=p["capture"].replace("id_/", "/", 1), captured_at=p["capture_date"], created_by=LABEL)
         for p in plan])
    (ROOT / "data/archive_links.csv").write_bytes(old + stream.getvalue().encode())
    write_csv(HERE / "BINDING_PROOF.csv", [dict(evidence_id=p["evidence_id"], record_id=p["owner"], claim_sha256=gate.claim_sha256(p["ev"]),
              capture=p["capture"], capture_date=p["capture_date"], capture_sha256=p["capture_sha256"], quote_offset=p["quote_offset"],
              verdict="VERIFIED", reader_family=reads[(p["owner"], p["value"])]["reader_family"],
              reader_date=reads[(p["owner"], p["value"])]["reader_date"]) for p in plan], list(gate.PROOF_COLS))
    held = [dict(table="organizations", record_id=h["owner"], field="markets_served", verdict="held", evidence_id="") for h in read_csv(HERE / "HELD.csv")]
    write_csv(HERE / "CLAIMS_CHECKED.csv", [dict(table="organizations", record_id=p["owner"], field="markets_served", verdict="corrected",
              evidence_id=p["evidence_id"]) for p in plan] + held, ["table", "record_id", "field", "verdict", "evidence_id"])
    (HERE / "INPUTS.sha256").write_text("".join(f"{d}  provenance/{TASK}/captures/{d}.html\n" for d in sorted({p["capture_sha256"] for p in plan})))
    subprocess.check_call([sys.executable, str(ROOT / "scripts/value_basis.py")], cwd=ROOT)
    print(f"applied {len(plan)} value(s) on {len({p['owner'] for p in plan})} owner(s)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepare", metavar="DIR")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--captures", action="append", default=[], help="extra directory of <sha256>.html captures (the store is always tried)")
    a = ap.parse_args()
    if a.prepare:
        prepare(a.prepare)
    elif a.apply:
        apply([*a.captures, STORE])
    else:
        ap.error("--prepare DIR or --apply")
