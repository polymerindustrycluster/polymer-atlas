#!/usr/bin/env python3
"""Role-title re-check, wave 2 (2026-11-03): turn lane outputs into hash-checked title edits.

    python3 tasks/role-title-recheck-2-2026-11-03/build_titles.py --data-dir data
        -> edits.csv (scripts/apply_p1_crm_scrub.py --packet-dir), holds.csv

The rules are wave 1's (tasks/atlas-cleanup-2026-11-03/build_cleanup.py, imported, not copied): a title is applied
only when the lane CONFIRMED it, it reads as a title (no quotes, narrative, name or '|'), its page is one the record
already cites, and the lane reports no rank disagreement. A rank disagreement is held: role changes need their own
check. Wave 2 adds one gate: the lanes read pages through WebFetch, which hands back a model's quotation, so each
title's page was re-fetched raw (NAS Firecrawl, owner's laptop) and the title applies only when its words appear on
that page in order (raw_check.csv: found / not_found / unfetchable). Stdlib only.
"""
import argparse, csv, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tasks" / "atlas-cleanup-2026-11-03"))
from build_cleanup import EDIT_COLS, bad_title, norm_url, read, sha  # noqa: E402

TODAY = "2026-11-03"
# Integrator review of the 41 rows that passed every gate: these read as prose, not a printed title line (wave 1 kept
# the same kind of list, TITLE_HOLD in build_cleanup.py).
TITLE_HOLD = {
    "PERSON-001109": "bio-sentence text ('... and lab director; head of the department of ...'), not a title line",
    "PERSON-001201": "news-sentence fragment ('... in the Department of ... at the FAMU-FSU College of Engineering')",
    "PERSON-001217": "prose with a lowercase rank ('... professor of chemical engineering; director of ...')",
    "PERSON-001219": "prose ('Mechanical engineering professor'), not a title line",
    "PERSON-001130": "title plus a sentence tail ('University Professor in the Department of Chemistry')",
    "PERSON-001090": "punctuation unconfirmed: the lane saw 'Professor Chemistry', the record had 'Professor, Chemistry'",
}


def build(data):
    P = {p["person_id"]: p for p in read(data / "people.csv")}
    raw = {(r["person_id"], r["title_url"]): r["raw_status"] for r in read(HERE / "raw_check.csv")}
    edits, holds = [], []
    for f in sorted((HERE / "lanes").glob("batch*_out.csv")):
        for r in read(f):
            pid = r["person_id"].strip()
            if pid not in P:
                holds.append({"record": pid, "item": "role_as_published", "reason": "not in people.csv"}); continue
            p, t = P[pid], (r.get("new_role_as_published") or "").strip()
            cited = {norm_url(u) for u in [p["public_profile_url"]] + p["sources"].split(";") if u.strip()}
            note = (r.get("rank_note") or "").strip()
            if r["status"].strip() != "CONFIRMED":
                why = "lane could not confirm: " + note[:140]
            elif not t or bad_title(t) or p["full_name"].split()[-1].lower() in t.lower():
                why = f"lane title is not a clean title line: {t[:80]!r}"
            elif norm_url(r["title_url"]) not in cited:
                why = "title page is not one the record cites: " + r["title_url"][:90]
            elif note:
                why = "page rank differs from the record's role; title and role held together for review: " + note[:140]
            elif raw.get((pid, r["title_url"].strip())) != "found":
                why = "title not found verbatim on the raw page: " + raw.get((pid, r["title_url"].strip()), "not checked")
            elif pid in TITLE_HOLD:
                why = "integrator review: " + TITLE_HOLD[pid]
            elif t == p["role_as_published"]:
                continue
            else:
                edits.append({"file": "people.csv", "row_id": pid, "column": "role_as_published",
                              "old_sha256": sha(p["role_as_published"]), "new_value": t, "edit_class": "ROLE_TITLE_EXACT",
                              "rationale": f"exact title re-read {TODAY} from the cited page {r['title_url'][:100]}"})
                continue
            holds.append({"record": pid, "item": "role_as_published", "reason": why})
    assert len({e["row_id"] for e in edits}) == len(edits), "one edit per person"
    return edits, holds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=str(ROOT / "data"))
    edits, holds = build(Path(ap.parse_args().data_dir))
    for name, cols, rows in (("edits.csv", EDIT_COLS, edits), ("holds.csv", ["record", "item", "reason"], holds)):
        with open(HERE / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    print(f"title edits: {len(edits)}; held: {len(holds)}")


if __name__ == "__main__":
    main()
