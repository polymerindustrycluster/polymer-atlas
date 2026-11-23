#!/usr/bin/env python3
"""Replay every packet row from the raw store, by path and hash, and fail on anything that does not hold.

  python3 -I check.py [--dir DIR] [--rehash] [--selftest]      (run from the repo root; stdlib only)

For each packet row: the raw file's sha256 must equal raw/MANIFEST.sha256 (and the packet's; --rehash re-reads the file and hashes
it); the record at the stated row must carry the quoted name and address; binding (binding.py: same_street, state, city or ZIP5,
held name, parent never binds, physical role, HQ rule for an organization) must hold on the raw fields; the date must be at most
five years old; the claim must still be missing at the strength the tier needs in today's data/; there is exactly one row per
(record, claim); the quote, source_ref and notes must equal what build.py builds from the raw row; no personal-data pattern.
--selftest plants five defects and requires each to be rejected: a different street, a parent-name row, a surplus second witness,
a claim already witnessed in data/, and a wrong sha256.
"""
import csv
import hashlib
import io
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import binding as B  # noqa: E402
import build as K  # noqa: E402
from atlas import name_key  # noqa: E402

RAW = K.LAKE.parent.parent / "raw"
LAKE_MANIFEST = K.LAKE / "MANIFEST.csv"
FIELDS = {   # family -> (name, street, city, state, zip, date, record key) raw column names
    "osha_inspection": ("ESTAB_NAME", "SITE_ADDRESS", "SITE_CITY", "SITE_STATE", "SITE_ZIP", "OPEN_DATE", "ACTIVITY_NR", "physical"),
    "osha_ita": ("establishment_name", "street_address", "city", "state", "zip_code", ("created_timestamp", "date_submitted"), ("id", "ID"), "physical"),
    "form5500_main_loc": ("SPONSOR_DFE_NAME", "SPONS_DFE_LOC_US_ADDRESS1", "SPONS_DFE_LOC_US_CITY", "SPONS_DFE_LOC_US_STATE", "SPONS_DFE_LOC_US_ZIP", "DATE_RECEIVED", "ACK_ID", "physical"),
    "form5500_sf_loc": ("SF_SPONSOR_NAME", "SF_SPONS_LOC_US_ADDRESS1", "SF_SPONS_LOC_US_CITY", "SF_SPONS_LOC_US_STATE", "SF_SPONS_LOC_US_ZIP", "DATE_RECEIVED", "ACK_ID", "physical"),
    "form5500_main_mail": ("SPONSOR_DFE_NAME", "SPONS_DFE_MAIL_US_ADDRESS1", "SPONS_DFE_MAIL_US_CITY", "SPONS_DFE_MAIL_US_STATE", "SPONS_DFE_MAIL_US_ZIP", "DATE_RECEIVED", "ACK_ID", "mailing"),
    "form5500_sf_mail": ("SF_SPONSOR_NAME", "SF_SPONS_US_ADDRESS1", "SF_SPONS_US_CITY", "SF_SPONS_US_STATE", "SF_SPONS_US_ZIP", "DATE_RECEIVED", "ACK_ID", "mailing"),
}
PERSONAL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+|\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b")
_manifest_cache = {}


def manifest_sha(path_under_raw):
    if not _manifest_cache:
        for line in open(RAW / "MANIFEST.sha256", encoding="utf-8"):
            sha, _, p = line.rstrip("\n").partition("  ")
            _manifest_cache[p[2:] if p.startswith("./") else p] = sha
    return _manifest_cache.get(path_under_raw.split("!")[0])


def encoding_of(path_under_raw):
    for r in csv.DictReader(open(LAKE_MANIFEST, newline="", encoding="utf-8")):
        if r["raw_path_under_raw"] == path_under_raw:
            return r["encoding"]
    return "utf-8-sig"


def read_rows(path_under_raw, wanted):
    """{row_number: {column: value}} for 1-based CSV records of the member file (header not counted)."""
    fpath, _, member = path_under_raw.partition("!")
    enc = encoding_of(path_under_raw)
    fh = zipfile.ZipFile(RAW / fpath).open(member) if member else open(RAW / fpath, "rb")
    rd = csv.reader(io.TextIOWrapper(fh, encoding=enc, newline=""))
    hdr, out, last = next(rd), {}, max(wanted)
    for i, row in enumerate(rd, 1):
        if i in wanted:
            out[i] = dict(zip(hdr, row))
        if i >= last:
            break
    return out


def source_row(fam, raw):
    n, st, ci, sa, zi, da, ky, role = FIELDS[fam]
    d = next((raw[x] for x in ((da,) if isinstance(da, str) else da) if raw.get(x)), "")
    return dict(name=raw[n], street=raw[st], city=raw[ci], state=raw[sa], zip=raw[zi], d=d, rid=next(raw[x] for x in ((ky,) if isinstance(ky, str) else ky) if x in raw), role=role, fam=fam)


def need_rank(rule, tier):
    return 3 if rule == "V-65" else (K.RANK["supports_C"] if tier == "C" else K.RANK["supports_U"])


def verify_row(p, c, ctx, sha_check, mailing=False):
    """-> list of failure strings for packet row p given its replayed source row c. ctx: orgs, sites, claim_best, frame (id -> frame row), org_sites."""
    f = []
    t, rid, claim = p["record_table"], p["record_id"], p["claim_type"]
    fr = ctx["frame"].get((t, rid))
    if not fr:
        return [f"{rid}: not in the V-65/V-68 frame"]
    if sha_check != p["src_sha256"]:
        f.append(f"{rid} {claim}: sha256 {p['src_sha256'][:12]} != raw/MANIFEST.sha256 {str(sha_check)[:12]}")
    if claim not in K.CLAIMS:
        f.append(f"{rid}: claim {claim} is not existence/address")
    if K.RANK.get(fr[f"best_{claim}"], -1) >= fr["need_rank"]:
        f.append(f"{rid} {claim}: already witnessed at the strength the tier needs in data/ ({fr[f'best_{claim}']})")
    if p["source_class"] != "government_filing":
        f.append(f"{rid}: source_class {p['source_class']}")
    d = K.parse_date(str(c["d"]))
    if not d or d < K.STALE_BEFORE:
        f.append(f"{rid} {claim}: filing date {d} is older than five years or unreadable")
        return f
    ords = ctx["orgs"]
    if t == "sites":
        site = ctx["sites"][rid]
        org = ords.get(site["org_id"])
        v, why = B.bind_site(site, org, c, ords.get((org or {}).get("parent_org_id", "")))
        rec, own = site, ()
        if c["fam"] == "sam":
            f.append(f"{rid}: SAM rows are held")
    else:
        org = ords[rid]
        porg = ords.get(org.get("parent_org_id", ""))
        v, why = (B.bind_org_existence(org, c, ctx["org_sites"].get(rid, []), porg) if claim == "existence" else B.bind_org_address(org, c, ctx["org_sites"].get(rid, []), porg, allow_mailing=mailing))
        rec, own = org, ctx["org_sites"].get(rid, [])
    if v != "ok":
        f.append(f"{rid} {claim}: binding fails: {why}")
        return f
    cc = {**c, "src_path": p["src_path_under_raw"], "src_sha256": p["src_sha256"], "src_row": p["src_row"]}
    exp = K.make_row(t, rec, claim, cc, d, why, 3, own)
    for k, val in exp.items():
        if str(p.get(k, "")) != str(val):
            f.append(f"{rid} {claim}: column {k} differs from what build.py builds from the raw row")
    if PERSONAL.search(" ".join(str(p.get(k, "")) for k in ("quote", "notes", "claim_detail", "source_ref"))):
        f.append(f"{rid} {claim}: an e-mail or phone-like string is in the row")
    return f


def context():
    orgs, sites, ev = K.load()
    frame = {(r["record_table"], r["record_id"]): r for r in K.build_frame(orgs, sites, ev)}
    org_sites = defaultdict(list)
    for s in sites.values():
        if K.in_region(s["state"], s["county"]):
            org_sites[s["org_id"]].append(s)
    return dict(orgs=orgs, sites=sites, frame=frame, org_sites=org_sites)


def replay(packet, rehash):
    by_file = defaultdict(set)
    for p in packet:
        by_file[p["src_path_under_raw"]].add(int(p["src_row"]))
    got, sha = {}, {}
    for path, rows in sorted(by_file.items()):
        got[path] = read_rows(path, rows)
        sha[path] = manifest_sha(path)
        if rehash:
            h, fp = hashlib.sha256(), RAW / path.split("!")[0]
            with open(fp, "rb") as fh:
                for blk in iter(lambda: fh.read(1 << 24), b""):
                    h.update(blk)
            if h.hexdigest() != sha[path]:
                raise SystemExit(f"REHASH MISMATCH {fp}: {h.hexdigest()} != {sha[path]}")
    return got, sha


def check(packet, ctx, got, sha, mailing=False):
    fails = []
    seen = Counter((p["record_table"], p["record_id"], p["claim_type"]) for p in packet)
    fails += [f"{k}: {n} witnesses for one claim (one witness per missing claim per record)" for k, n in seen.items() if n > 1]
    for p in packet:
        raw = got[p["src_path_under_raw"]].get(int(p["src_row"]))
        if raw is None:
            fails.append(f"{p['record_id']}: row {p['src_row']} not found in {p['src_path_under_raw']}")
            continue
        fails += verify_row(p, source_row(p["source_family"], raw), ctx, sha[p["src_path_under_raw"]], mailing)
    return fails


def selftest(packet, ctx, got, sha):
    """Each planted defect must be rejected. Returns the number rejected out of the number planted."""
    base = next((p for p in packet if p["record_table"] == "sites"), None)
    orgrow = next((p for p in packet if p["record_table"] == "organizations" and p["claim_type"] == "existence"), None)
    results = []

    def planted(name, rows, mutate_raw=None, mutate_ctx=None, expect=None):
        g = {k: {r: dict(v) for r, v in d.items()} for k, d in got.items()}
        c2 = {**ctx, "orgs": {k: dict(v) for k, v in ctx["orgs"].items()}, "frame": dict(ctx["frame"])}
        if mutate_raw:
            mutate_raw(g)
        if mutate_ctx:
            mutate_ctx(c2)
        fails = check(rows, c2, g, sha, False)
        ok = bool(fails) and (expect is None or any(expect in x for x in fails))
        results.append((name, ok, fails[:1]))

    if base:
        planted("planted row at a different street", [base],
                mutate_raw=lambda g: g[base["src_path_under_raw"]][int(base["src_row"])].__setitem__(FIELDS[base["source_family"]][1], "9999 Nowhere Boulevard"),
                expect="binding fails")
        planted("planted surplus second witness", [base, dict(base)], expect="witnesses for one claim")
        planted("planted wrong sha256", [dict(base, src_sha256="0" * 64)], expect="sha256")
        fr = ctx["frame"][(base["record_table"], base["record_id"])]
        planted("planted claim already witnessed in data/", [base],
                mutate_ctx=lambda c2: c2["frame"].__setitem__((base["record_table"], base["record_id"]), {**fr, f"best_{base['claim_type']}": "supports_A"}),
                expect="already witnessed")
    if base:
        # a site-name part that is the recorded parent: binds as site_name_part without the parent rule, must fail as parent
        sid = base["record_id"]
        def plant_site(c2):
            s2 = dict(ctx["sites"][sid], site_name="Planted Parent Co - " + ctx["sites"][sid]["city"])
            c2["sites"] = {**ctx["sites"], sid: s2}
            o = dict(c2["orgs"][s2["org_id"]], ultimate_parent_name="Planted Parent Co")
            c2["orgs"][s2["org_id"]] = o
        def parent_raw(g):
            g[base["src_path_under_raw"]][int(base["src_row"])][FIELDS[base["source_family"]][0]] = "PLANTED PARENT CO"
        planted("planted parent-name row (site-name part equals the recorded parent)", [base], mutate_raw=parent_raw, mutate_ctx=plant_site, expect="name_is_recorded_parent_only")
    if orgrow:
        org = ctx["orgs"][orgrow["record_id"]]
        def to_parent(g):
            g[orgrow["src_path_under_raw"]][int(orgrow["src_row"])][FIELDS[orgrow["source_family"]][0]] = "PLANTED PARENT CO"
        planted("planted parent-name row (organization)", [orgrow], mutate_raw=to_parent,
                mutate_ctx=lambda c2: c2["orgs"][orgrow["record_id"]].__setitem__("ultimate_parent_name", "Planted Parent Co"), expect="name_is_recorded_parent_only")
    return results


def main():
    d = Path(sys.argv[sys.argv.index("--dir") + 1]) if "--dir" in sys.argv else HERE
    if "--region" in sys.argv:
        K.REGION = sys.argv[sys.argv.index("--region") + 1]
    fname = sys.argv[sys.argv.index("--file") + 1] if "--file" in sys.argv else "packet.csv"
    mailing = fname == "candidates_mailing.csv"
    packet = list(csv.DictReader(open(d / fname, newline="", encoding="utf-8")))
    ctx = context()
    for nm in ("frame.csv", "packet.csv", "candidates_mailing.csv", "leads.csv", "discards.csv", "held_filer_not_the_record.csv", "sites_without_civic_street.csv"):
        if (d / nm).exists() and PERSONAL.search((d / nm).read_text(encoding="utf-8")):
            print("FAIL personal-data pattern in", nm)
            return 1
    got, sha = replay(packet, "--rehash" in sys.argv)
    fails = check(packet, ctx, got, sha, mailing)
    print(f"replayed {len(packet)} packet rows from {len(got)} raw files; failures {len(fails)}")
    for x in fails[:50]:
        print("FAIL", x)
    if "--selftest" in sys.argv and not mailing:
        res = selftest(packet, ctx, got, sha)
        for name, ok, ex in res:
            print(("rejected " if ok else "NOT REJECTED "), name, "|", ex[0][:110] if ex else "")
        if not all(ok for _, ok, _ in res):
            return 1
        print(f"selftest: {sum(ok for _, ok, _ in res)}/{len(res)} planted defects rejected")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
