#!/usr/bin/env python3
"""Cleanup pass (owner decisions 2026-11-03): duplicate people, exact role titles,
nonexistent ROR ids, an email-bearing source URL.

    python3 tasks/atlas-cleanup-2026-11-03/build_cleanup.py --data-dir data --ipeds-ror <ipeds_ror.tsv> --ror-cache <dir>
        -> edits.csv (hash-checked cell edits, scripts/apply_p1_crm_scrub.py --packet-dir)
           removals.csv (people rows to remove, each with the sha256 of the whole row)
           inclusion_log_append.csv, holds.csv
    python3 tasks/atlas-cleanup-2026-11-03/build_cleanup.py --data-dir data --remove --i-am-the-integrator
        -> removes the rows in removals.csv (whole-row hash checked) and appends the inclusion-log rows

Decisions applied
  * Duplicates (owner: "merge into older"): the 14 same-institution, same-name pairs.
    The older PERSON id is kept. From the copy it takes extra sources (union),
    a personal profile URL where the keeper's is a shared listing page, a clean
    title where the keeper's is narrative, and specialties where the keeper has none.
    The copy row is removed; its id is retired and never reused. Each removal is
    logged in inclusion_log.csv.
  * Role titles (owner: "re-read the cited page"): lane outputs in
    tasks/role-title-recheck-2026-11-03/lanes/*_out.csv. A title is applied only
    when the lane CONFIRMED it, it reads as a title (no quotes, narrative, name or
    '|'), and its page is one the record already cites. Rank disagreements are
    listed in holds.csv, never applied: role changes need their own check.
  * ROR: ids that api.ror.org says do not exist are replaced with the crosswalk
    candidate when it verifies (active, US, same state, name/domain agree), or
    cleared on a sub-unit row (V-14: a sub-unit never carries the parent's ROR).
  * PERSON-000366: the source URL that embeds an email address is dropped.
Stdlib only.
"""
import argparse, csv, hashlib, io, json, re, sys, urllib.request
from pathlib import Path

csv.field_size_limit(10 ** 9)
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TODAY = "2026-11-03"
BY = "claude-code atlas-cleanup-2026-11-03"
EDIT_COLS = ["file", "row_id", "column", "old_sha256", "new_value", "edit_class", "rationale"]
DUP_PAIRS = [("PERSON-000015", "PERSON-000959"), ("PERSON-000061", "PERSON-000837"), ("PERSON-000172", "PERSON-000973"),
             ("PERSON-000177", "PERSON-001035"), ("PERSON-000178", "PERSON-000982"), ("PERSON-000179", "PERSON-000979"),
             ("PERSON-000180", "PERSON-001056"), ("PERSON-000184", "PERSON-000976"), ("PERSON-000194", "PERSON-001013"),
             ("PERSON-000338", "PERSON-000951"), ("PERSON-000406", "PERSON-000963"), ("PERSON-000452", "PERSON-000996"),
             ("PERSON-000742", "PERSON-000953"), ("PERSON-000804", "PERSON-001005")]
PHANTOM_ROR = {"ORG-002087": "201441", "ORG-002088": "204857", "ORG-002089": "169910", "ORG-002090": "240417",
               "ORG-002091": "170055", "ORG-002092": "155681"}
# Integrator review of lane titles: not title lines as printed.
TITLE_HOLD = {"PERSON-000607": "lane line is a team-role label ('PMC M&P team member'), not a title",
              "PERSON-000847": "lane line comes from a news sentence ('promoted to Full Professor of Chemistry'), not a printed title",
              "PERSON-001078": "lane joined an administrative header with a rank taken from bio prose"}
CLEAR_ROR = {"ORG-002104": "sub-unit of ORG-000501 (University of Akron); its ror_id 00zx12t90 does not exist in ROR, "
                           "and a sub-unit never carries the parent's ROR (V-14)"}


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def read(p, delim=","):
    with open(p, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader([l for l in fh if not l.startswith("#")], delimiter=delim))


def bad_title(t):
    return bool('"' in t or re.match(r"[a-z]", t) or len(t) > 160 or "|" in t
                or re.search(r"\b(is an?|joined|promoted|was|news|listed|per page)\b", t, re.I))


def norm_url(u):
    return re.sub(r"^https?://(www\.)?", "", (u or "").strip().lower()).rstrip("/")


def ror_check(rid, cache, state, names, doms):
    key = rid.rsplit("/", 1)[-1]
    p = cache / f"{key}.json"
    if not p.exists():
        with urllib.request.urlopen(f"https://api.ror.org/v2/organizations/{key}", timeout=30) as r:
            p.write_bytes(r.read())
    rec = json.loads(p.read_text())
    g = (rec.get("locations") or [{}])[0].get("geonames_details", {})
    rn = {re.sub(r"[^a-z0-9]+", " ", n.get("value", "").lower()).strip() for n in rec.get("names", [])}
    ok = (rec.get("status") == "active" and g.get("country_code") == "US"
          and (g.get("country_subdivision_code") or "") in (state, "US-" + state)
          and (set(rec.get("domains", [])) & set(doms) or rn & {re.sub(r"[^a-z0-9]+", " ", n.lower()).strip() for n in names}))
    return bool(ok), (rec.get("names") or [{}])[0].get("value", "")


def build(data, xw_path, cache):
    people = read(data / "people.csv")
    P = {p["person_id"]: p for p in people}
    eco = {r["org_id"]: r for r in read(data / "ecosystem.csv")}
    edits, removals, log, holds = [], [], [], []
    cur = {}  # (file,row,col) -> value after earlier edits

    def edit(file, rid, col, old, new, cls, why):
        k = (file, rid, col)
        base = cur.get(k, old)
        if new == base:
            return
        prev = next((e for e in edits if (e["file"], e["row_id"], e["column"]) == k), None)
        if prev:
            prev.update(new_value=new, edit_class=prev["edit_class"] + "+" + cls, rationale=prev["rationale"] + "; " + why)
        else:
            edits.append({"file": file, "row_id": rid, "column": col, "old_sha256": sha(old), "new_value": new,
                          "edit_class": cls, "rationale": why})
        cur[k] = new

    # 1. duplicates
    shared = {}
    for p in people:
        shared.setdefault(norm_url(p["public_profile_url"]), []).append(p["person_id"])
    for keep_id, copy_id in DUP_PAIRS:
        k, c = P[keep_id], P[copy_id]
        assert k["institution_org_id"] == c["institution_org_id"], (keep_id, copy_id)
        src = list(dict.fromkeys(s.strip() for s in (k["sources"] + ";" + c["sources"]).split(";") if s.strip()))
        edit("people.csv", keep_id, "sources", k["sources"], ";".join(src), "DUP_MERGE_SOURCES", f"sources of retired duplicate {copy_id} carried over")
        if len(shared.get(norm_url(k["public_profile_url"]), [])) > 1 and len(shared.get(norm_url(c["public_profile_url"]), [])) == 1:
            edit("people.csv", keep_id, "public_profile_url", k["public_profile_url"], c["public_profile_url"], "DUP_MERGE_PROFILE",
                 f"keeper's URL is a shared listing page; {copy_id}'s is the personal profile")
        if bad_title(k["role_as_published"]) and not bad_title(c["role_as_published"]):
            edit("people.csv", keep_id, "role_as_published", k["role_as_published"], c["role_as_published"], "DUP_MERGE_TITLE",
                 f"keeper's title text is narrative; {copy_id}'s is the printed title")
        if not k["research_specialties"].strip() and c["research_specialties"].strip():
            edit("people.csv", keep_id, "research_specialties", "", c["research_specialties"], "DUP_MERGE_SPECIALTIES", f"from {copy_id}")
        row_text = ",".join(c[f] for f in c)
        removals.append({"file": "people.csv", "row_id": copy_id, "row_sha256": sha(row_text), "duplicate_of": keep_id})
        log.append({"date": TODAY, "entity": f"{copy_id} {c['full_name']}", "decision": f"REMOVED: duplicate of {keep_id} (same person, same institution {k['institution_org_id']}); merged into {keep_id}; id retired, never reused",
                    "rule_cited": "owner decision 2026-11-03 (merge duplicates into the older record); AGENTS.md section 3 (never reuse an ID)",
                    "researcher": BY, "notes": "duplicate created by integration pass 45 (R2 tranche 2)"})
    removed = {r["row_id"] for r in removals}

    # 2. role titles from the re-check lanes
    for f in sorted((ROOT / "tasks" / "role-title-recheck-2026-11-03" / "lanes").glob("batch*_out.csv")):
        for r in read(f):
            pid = r["person_id"].strip()
            if pid not in P or pid in removed:
                continue
            p, t = P[pid], (r.get("new_role_as_published") or "").strip()
            cited = {norm_url(u) for u in [p["public_profile_url"]] + p["sources"].split(";") if u.strip()}
            why = []
            if r["status"].strip() != "CONFIRMED": why.append("lane could not confirm: " + (r.get("rank_note") or "")[:120])
            elif not t or bad_title(t) or p["full_name"].split()[-1].lower() in t.lower(): why.append(f"lane title is not a clean title line: {t[:80]!r}")
            elif norm_url(r["title_url"]) not in cited: why.append("title page is not one the record cites: " + r["title_url"][:90])
            if (r.get("rank_note") or "").strip() and r["status"].strip() == "CONFIRMED" and not why:
                why.append("page rank differs from the record's role; title and role held together for review: " + r["rank_note"][:140])
            if pid in TITLE_HOLD and not why:
                why.append("integrator review: " + TITLE_HOLD[pid])
            if why:
                holds.append({"record": pid, "item": "role_as_published", "reason": "; ".join(why)}); continue
            edit("people.csv", pid, "role_as_published", p["role_as_published"], t, "ROLE_TITLE_EXACT",
                 f"exact title re-read {TODAY} from the cited page {r['title_url'][:100]}")

    # 3. ROR ids that do not exist
    xw = {r["unitid"]: r for r in read(xw_path, "\t")}
    held = {r["ror_id"] for r in eco.values() if r["ror_id"]}
    for oid, u in PHANTOM_ROR.items():
        r = eco[oid]
        cand = "https://ror.org/" + xw[u]["ror"].rsplit("/", 1)[-1]
        ok, nm = ror_check(cand, cache, r["state"], [r["legal_name"], xw[u]["label"]], [re.sub(r"^https?://(www\.)?", "", r["website"]).split("/")[0]])
        if ok and cand not in held:
            edit("ecosystem.csv", oid, "ror_id", r["ror_id"], cand, "ROR_PHANTOM_REPLACE",
                 f"{r['ror_id']} does not exist in ROR (api.ror.org {TODAY}); replaced by the crosswalk candidate for UNITID {u}, verified active/US-{r['state']}/{nm}")
            s = r["sources"].replace(r["ror_id"], cand) if r["ror_id"] in r["sources"] else r["sources"].rstrip() + "; " + cand
            edit("ecosystem.csv", oid, "sources", r["sources"], s, "ROR_PHANTOM_SOURCE", "cite the real ROR record")
        else:
            holds.append({"record": oid, "item": "ror_id", "reason": f"candidate {cand} did not verify; phantom left for review"})
    for oid, why in CLEAR_ROR.items():
        r = eco[oid]
        edit("ecosystem.csv", oid, "ror_id", r["ror_id"], "", "ROR_PHANTOM_CLEAR", why)
        if r["ror_id"] in r["sources"]:
            s = "; ".join(x.strip() for x in r["sources"].split(";") if x.strip() and r["ror_id"] not in x)
            edit("ecosystem.csv", oid, "sources", r["sources"], s, "ROR_PHANTOM_CLEAR_SOURCE", "drop the nonexistent ROR from sources")

    # 4. email-bearing source URL
    p = P["PERSON-000366"]
    s = ";".join(x for x in p["sources"].split(";") if x.strip() and "@" not in x)
    edit("people.csv", "PERSON-000366", "sources", cur.get(("people.csv", "PERSON-000366", "sources"), p["sources"]), s, "PRIVACY_EMAIL_URL",
         "drop a source URL that embeds an individual email address (AGENTS.md section 6)")
    return edits, removals, log, holds


def write(name, cols, rows):
    with open(HERE / name, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n", extrasaction="ignore"); w.writeheader(); w.writerows(rows)


def remove_rows(data):
    rem = read(HERE / "removals.csv")
    path = data / "people.csv"
    raw = path.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    rows = list(csv.reader(io.StringIO(raw, newline="")))
    hdr, body = rows[0], rows[1:]
    want = {r["row_id"]: r for r in rem}
    keep, gone = [], set()
    for row in body:
        if row and row[0] in want:
            if sha(",".join(row)) != want[row[0]]["row_sha256"]:
                sys.exit(f"{row[0]} changed since the packet was built; rebuild")
            gone.add(row[0]); continue
        keep.append(row)
    if gone != set(want):
        sys.exit(f"rows not found: {sorted(set(want) - gone)}")
    buf = io.StringIO()
    csv.writer(buf, lineterminator=nl).writerows([hdr] + keep)
    path.write_bytes(buf.getvalue().encode("utf-8"))
    log = read(HERE / "inclusion_log_append.csv")
    lp = data / "inclusion_log.csv"
    lraw = lp.read_bytes()
    lnl = "\r\n" if b"\r\n" in lraw else "\n"
    lh = next(csv.reader(io.StringIO(lraw.decode("utf-8"))))
    b2 = io.StringIO()
    csv.writer(b2, lineterminator=lnl).writerows([[r[c] for c in lh] for r in log])
    lp.write_bytes(lraw + b2.getvalue().encode("utf-8"))
    print(f"removed {len(gone)} people rows; inclusion_log +{len(log)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--ipeds-ror")
    ap.add_argument("--ror-cache")
    ap.add_argument("--remove", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    a = ap.parse_args()
    data = Path(a.data_dir).resolve()
    if a.remove:
        if data == (ROOT / "data").resolve() and not a.i_am_the_integrator:
            sys.exit("removing rows from the real data/ is integrator work; pass --i-am-the-integrator")
        return remove_rows(data)
    cache = Path(a.ror_cache); cache.mkdir(parents=True, exist_ok=True)
    edits, removals, log, holds = build(data, a.ipeds_ror, cache)
    write("edits.csv", EDIT_COLS, edits)
    write("removals.csv", ["file", "row_id", "row_sha256", "duplicate_of"], removals)
    write("inclusion_log_append.csv", ["date", "entity", "decision", "rule_cited", "researcher", "notes"], log)
    write("holds.csv", ["record", "item", "reason"], holds)
    import collections
    print("edits by class:", dict(collections.Counter(e["edit_class"] for e in edits)))
    print(f"removals {len(removals)}; holds {len(holds)} ({dict(collections.Counter(h['item'] for h in holds))})")


if __name__ == "__main__":
    main()
