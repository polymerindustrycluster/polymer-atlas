"""Named check for the PIC-18 ITA site-size-band lane. Run from anywhere: python3 tasks/pic18-size-ita-2026-11-22/check.py [base-ref]
Independent of build.py: its own street/name matcher and band table. Recomputes every disposition and band from
establishments.csv and the data rows, asserts held rows are untouched, applied + held = 23, diffs the whole data/ tree
against the base, then plants defects and shows each one fails."""
import copy, csv, io, re, subprocess, sys
from pathlib import Path

csv.field_size_limit(10 ** 9)
D = Path(__file__).resolve().parent
ROOT = D.parents[1]
S_FRAME = Path("/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/briefs/w1122/size-frame.csv")
BY = "claude-code pic18-size-ita-2026-11-22"
TABLE = [(1, 9, "1-9"), (10, 49, "10-49"), (50, 99, "50-99"), (100, 249, "100-249"), (250, 499, "250-499"), (500, 999, "500-999"), (1000, 4999, "1000-4999"), (5000, 10 ** 9, "5000+")]
ORDER = [b for _, _, b in TABLE]
JUDGED_STREET = {"SITE-000264", "SITE-000620", "SITE-001109"}  # named in README "Judgment calls"; the matcher below must also see them as near-equal
JUDGED_NAME = {"SITE-000383"}
FRAME_N = 23


def read(p): return list(csv.DictReader(open(p, newline="", encoding="utf-8")))
def git(*a): return subprocess.check_output(["git", *a], cwd=ROOT, text=True)
def band(n): return next(b for lo, hi, b in TABLE if lo <= n <= hi)


SUFFIX = {"road", "rd", "street", "st", "avenue", "ave", "parkway", "pkwy", "drive", "dr", "boulevard", "blvd", "highway", "hwy", "lane", "ln"}
DIRW = {"n", "s", "e", "w", "ne", "nw", "se", "sw", "north", "south", "east", "west"}


def street_sig(s):
    """(house number, tuple of 4-letter stems of the street's name words); suffixes and trailing quadrant dropped, unit tail cut."""
    s = re.split(r"\b(?:suite|ste|unit)\b", s.lower().replace(".", ""))[0]
    m = re.match(r"\s*(\d+)([a-z]?)\b\s*(.*)", s)
    if not m: return None
    words = [{"north": "n", "south": "s", "east": "e", "west": "w"}.get(w, w) for w in re.findall(r"[a-z0-9]+", m.group(3))]
    while len(words) > 1 and words[-1] in DIRW: words.pop()
    return m.group(1), tuple(w[:4] for w in words if w not in SUFFIX), m.group(2)


def street_ok(rec, ita):
    a, b = street_sig(rec), street_sig(ita)
    return bool(a and b and a[0] == b[0] and a[1] == b[1])  # a unit letter (a[2]) is ignored here; judged rows are listed separately


def tie(s):
    return re.sub(r"\b(inc|llc|corp|corporation|company|co|the|division|facility|plant)\b", "", re.sub(r"[^a-z0-9 ]", " ", s.lower())).split()


def name_ok(site, org, i):
    mine = [tie(re.split(r" [—–-] ", site["site_name"])[0]), tie(org["legal_name"])] + [tie(t) for t in org["trade_names"].split(";") if t.strip()]
    theirs = [tie(re.split(r" [—–-] ", i["establishment_name"])[0]), tie(i["establishment_name"]), tie(i["company_name"])]
    return any(m and m == t for m in mine for t in theirs)


def expected(fr, sites, orgs, ita, spine, ev):
    """Independent re-derivation: ('applied', band) or ('held', reason-key)."""
    sid, est = fr["site_id"], fr["establishment_id"]
    s, i = sites[sid], ita[est]; o = orgs[s["org_id"]]
    n = int(i["annual_average_employees"]); b = band(n)
    assert b == i["band_from_avg_employees"], f"{est}: file band column {i['band_from_avg_employees']} != recomputed {b}"
    pointers = [r for f in ("frame.csv", "extra_bindings.csv") for r in read(D / f)]
    bound = {r["site_id"] for r in pointers if r["establishment_id"] == est}
    for x in bound - {sid}: assert sites[x]["org_id"] == s["org_id"] and sites[x]["city"] == s["city"], f"{x}: binding pointer is not a same-organization, same-city twin of {sid}"
    why = []
    if not s["street_address"].strip(): why.append("nostreet")
    elif not street_ok(s["street_address"], i["street"]): why.append("street")
    if not (name_ok(s, o, i) or sid in JUDGED_NAME): why.append("name")
    if i["reliability"] != "ok": why.append("reliability")
    if len(bound | {sid}) != 1: why.append("twosites")
    if i["ita_estabs_at_address"] != "1": why.append("multi_estab")
    sp = spine.get(sid)
    if sp and any(abs(ORDER.index(x) - ORDER.index(b)) > 1 for x in set(sp["bands_seen_all_inspections"].split(";")) | {sp["proposed_employee_band_site"]} if x): why.append("r13")
    if sid in JUDGED_STREET: assert s["street_address"].strip() and street_sig(s["street_address"])[0][:3] == street_sig(i["street"])[0][:3], "judged street must still share the house number"
    return ("held", why) if why else ("applied", b)


def check_state(frame, sites, orgs, ita, spine, ev, verdicts, base_sites, base_orgs, base_max):
    assert len(frame) == FRAME_N == len({f["site_id"] for f in frame}), "frame is not 23 distinct sites"
    vd = {v["site_id"]: v for v in verdicts}
    assert set(vd) == {f["site_id"] for f in frame}, "verdicts do not cover the frame exactly"
    mine = [e for e in ev if e["created_by"] == BY]
    mid = [e["evidence_id"] for e in mine]
    assert len(set(mid)) == len(mid) and all(480000 <= int(i[4:]) <= 480099 and int(i[4:]) > base_max for i in mid), "evidence ID outside EVD-480000..480099 or not above the base maximum"
    all_ids = [e["evidence_id"] for e in ev]
    assert len(all_ids) == len(set(all_ids)), "duplicate evidence_id tree-wide"
    n_applied = n_held = 0
    for fr in frame:
        sid, est = fr["site_id"], fr["establishment_id"]
        s, v = sites[sid], vd[sid]
        kind, what = expected(fr, sites, orgs, ita, spine, ev)
        assert v["disposition"] == kind, f"{sid}: verdict {v['disposition']} != recomputed {kind} ({what})"
        assert v["verdict"] == ("VERIFIED" if kind == "applied" else "STILL_UNCERTAIN"), f"{sid}: verdict grammar"
        rows = [e for e in mine if e["record_id"] == sid]
        if kind == "applied":
            n_applied += 1
            assert s["employee_band_site"] == what == v["ita_band"], f"{sid}: cell {s['employee_band_site']!r} != recomputed band {what}"
            assert base_sites[sid]["employee_band_site"] == "", f"{sid}: base cell was not blank (overwrite)"
            assert len(rows) == 1, f"{sid}: need exactly one size_band row, have {len(rows)}"
            e = rows[0]
            assert (e["claim_type"], e["source_class"], e["tier_effect"], e["record_table"]) == ("size_band", "government_filing", "supports_B", "sites")
            assert f"establishment_id {est}" in e["source_ref"] and e["claim_detail"].startswith(f"employee_band_site={what}:"), f"{sid}: evidence row does not name the band and establishment"
            assert not re.search(r"\b\d+ employees|average employees \d", e["claim_detail"]) and ita[est]["annual_average_employees"] not in re.findall(r"\d+", e["claim_detail"].split(":", 1)[1].replace(est, "")), f"{sid}: headcount in evidence claim_detail"
            assert re.search(rf"BAND-SOURCE: employee_band_site={re.escape(what)} from OSHA ITA Form 300A CY2025, filed {ita[est]['date_submitted']}", s["notes"]), f"{sid}: source-date note missing"
        else:
            n_held += 1
            assert s["employee_band_site"] == base_sites[sid]["employee_band_site"] == "", f"{sid}: held site carries a band"
            assert not rows, f"{sid}: held site has an evidence row"
            assert s["notes"] == base_sites[sid]["notes"], f"{sid}: held site's notes changed"
            assert v["reasons"], f"{sid}: held with no settling fact"
    assert n_applied + n_held == FRAME_N, "applied + held != 23"
    assert len(mine) == n_applied, "evidence rows != applied fills"
    return n_applied, n_held


def check_tree(base, sites, orgs):
    """Whole data/ tree vs base: only band cells + note suffixes on applied sites, and appended evidence rows."""
    names = git("diff", "--name-only", base, "--", "data").split()
    assert set(names) <= {"data/sites_OH.csv", "data/evidence_sites_OH.csv"}, f"unexpected files changed: {names}"
    assert git("ls-files", "--others", "--exclude-standard", "data").strip() == "", "untracked file under data/"
    old = list(csv.DictReader(io.StringIO(git("show", f"{base}:data/sites_OH.csv"))))
    new = read(ROOT / "data/sites_OH.csv")
    assert [r["site_id"] for r in old] == [r["site_id"] for r in new], "site rows added, removed or reordered"
    changed = 0
    for a, b in zip(old, new):
        if a == b: continue
        diff = {k for k in a if a[k] != b[k]}
        assert diff <= {"employee_band_site", "notes"}, f"{a['site_id']}: cells other than band/notes changed: {diff}"
        assert a["employee_band_site"] == "" and b["notes"].startswith(a["notes"]) and b["notes"][len(a["notes"]):].lstrip().startswith("BAND-SOURCE:"), f"{a['site_id']}: not a blank-only fill with a note suffix"
        changed += 1
    oe = git("show", f"{base}:data/evidence_sites_OH.csv"); ne = (ROOT / "data/evidence_sites_OH.csv").read_text(encoding="utf-8")
    assert ne.startswith(oe), "existing evidence rows were edited or reordered"
    appended = list(csv.DictReader(io.StringIO(oe.split("\n", 1)[0] + "\n" + ne[len(oe):])))
    assert all(e["created_by"] == BY for e in appended) and len(appended) == changed, f"{len(appended)} appended evidence rows vs {changed} filled sites"
    return changed


def planted(frame, sites, orgs, ita, spine, ev, verdicts, bsites, borgs, bmax):
    def run(label, mutate):
        s2, e2, v2 = copy.deepcopy(sites), copy.deepcopy(ev), copy.deepcopy(verdicts)
        mutate(s2, e2, v2)
        try: check_state(frame, s2, orgs, ita, spine, e2, v2, bsites, borgs, bmax)
        except AssertionError as x: print(f"  planted defect rejected: {label} -> {str(x)[:90]}"); return
        raise SystemExit(f"FAIL: planted defect NOT rejected: {label}")
    applied = [v["site_id"] for v in verdicts if v["disposition"] == "applied"]
    run("band on a held site (SITE-000138, reliability=review)", lambda s, e, v: s["SITE-000138"].update(employee_band_site="100-249"))
    run("wrong band on an applied site", lambda s, e, v: s[applied[0]].update(employee_band_site="250-499"))
    run("band on the site whose street differs (SITE-000517)", lambda s, e, v: s["SITE-000517"].update(employee_band_site="100-249"))
    run("band on one of the two sites sharing an establishment (SITE-002965)", lambda s, e, v: s["SITE-002965"].update(employee_band_site="10-49"))
    run("applied site loses its evidence row", lambda s, e, v: e.remove(next(x for x in e if x["created_by"] == BY)))
    run("headcount written into an evidence claim_detail", lambda s, e, v: next(x for x in e if x["created_by"] == BY).update(claim_detail="employee_band_site=100-249: OSHA ITA 300A CY2025, establishment_ID 656015: annual average employees 129 (band only)"))
    run("evidence ID outside the reserved block", lambda s, e, v: next(x for x in e if x["created_by"] == BY).update(evidence_id="EVD-480100"))
    run("held verdict flipped to applied", lambda s, e, v: next(x for x in v if x["site_id"] == "SITE-000639").update(disposition="applied", verdict="VERIFIED"))


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else git("merge-base", "HEAD", "origin/main").strip()
    frame = read(D / "frame.csv")
    if S_FRAME.exists(): assert read(S_FRAME) == frame, "frame.csv differs from the controller's copy"  # row-wise: git normalises the file's CRLF to LF
    else: print("  NOTE: controller frame copy not found; frame equality NOT checked")
    sites = {r["site_id"]: r for p in (ROOT / "data").glob("sites_*.csv") for r in read(p)}
    orgs = {r["org_id"]: r for p in (ROOT / "data").glob("organizations_*.csv") for r in read(p)}
    ev = [r for p in (ROOT / "data").glob("evidence_*.csv") for r in read(p)]
    names = [n for n in git("ls-tree", "--name-only", base, "data/").split() if n.startswith("data/") and Path(n).name.startswith(("sites_", "organizations_", "evidence_"))]
    bsites = {r["site_id"]: r for n in names if "/sites_" in n for r in csv.DictReader(io.StringIO(git("show", f"{base}:{n}")))}
    borgs = {r["org_id"]: r for n in names if "/organizations_" in n for r in csv.DictReader(io.StringIO(git("show", f"{base}:{n}")))}
    bmax = max(int(r["evidence_id"][4:]) for n in names if "/evidence_" in n for r in csv.DictReader(io.StringIO(git("show", f"{base}:{n}"))) if re.fullmatch(r"EVD-\d+", r["evidence_id"]))
    ita = {r["establishment_id"]: r for r in read(ROOT / "tasks/osha-ita-2026-11-01/establishments.csv")}
    spine = {r["site_id"]: r for r in read(ROOT / "tasks/osha-spine-2026-11-01/band_proposals.csv")}
    verdicts = read(D / "verdicts.csv")
    a, h = check_state(frame, sites, orgs, ita, spine, ev, verdicts, bsites, borgs, bmax)
    f = check_tree(base, sites, orgs)
    assert f == a, "tree diff fills != applied"
    assert all(borgs[o]["employee_band_ohio"] == orgs[o]["employee_band_ohio"] for o in borgs if o in orgs), "an organization band changed"
    planted(frame, sites, orgs, ita, spine, ev, verdicts, bsites, borgs, bmax)
    print(f"PASS: applied {a} + held {h} = {a + h}; {f} site cells + {f} evidence rows differ from base {base[:8]}; 8 planted defects rejected")


if __name__ == "__main__":
    main()
