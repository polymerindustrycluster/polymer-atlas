#!/usr/bin/env python3
"""Show harvest wave 1 (2026-11-06): exhibitor, sponsor and speaker participation rows from organizer-published
lists, organization grain only.

    python3 tasks/show-harvest-w1-2026-11-06/build.py --data-dir data --harvest <staging harvest dir> \
        --conferences ../conferences [--apply --i-am-the-integrator]

Input: the banked wave-1 harvest (staging `harvest-2026-11/out/*.json`, one file per show edition, raw page behind
every list under `out/raw/`; never committed). Method as tasks/exhibitor-links-2026-11-06, extended to three roles:
- A name mints only when it appears verbatim in that list's banked raw file, is not on controller_drops.csv, and its
  normalized name (atlas.name_key) is held by exactly one active/unknown organization. Ambiguous keys are held.
- edition_year is the LIST's own edition year, never the show key's year (a 2027 page often carries the 2026 list),
  so the same list copied onto several show files collapses to one row per (event, org, year, role).
- A list covering several co-located shows with no per-company show label mints only under a declared umbrella
  event (the AMI expos -> EVT-000007). Otherwise it is skipped (README lists them).
- An edition abroad whose list gives no company country is held (tasks/exhibitor-links-2026-11-06, the Momentive
  GmbH / MPM Silicones LLC trade-name trap).
- Attendee lists wait for schema v1.12 (PR #250) and a terms check (SCHEMA 4.12.2 harvest-only rule 4).
Writes matches.csv and participation_append.csv here; unmatched names go to <harvest>/controller/ (never committed).
"""
import argparse, csv, html, json, re, sys
from collections import Counter
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "scripts"))
sys.path.insert(0, str(HERE.parent / "census-gap-people-2026-11-03"))
import atlas as A  # noqa: E402
from build_integration import append_rows, read  # noqa: E402

BY = "claude-code show-harvest-w1-2026-11-06"
ROLES = {"exhibitor", "sponsor", "speaker"}
UMBRELLA = {"EVT-000008": "EVT-000007", "EVT-000009": "EVT-000007", "EVT-000051": "EVT-000007",
            "EVT-000052": "EVT-000007"}  # AMI component expos share one gallery -> the umbrella series
UMBRELLA_EVENTS = {"EVT-000007"}
# foam-expo.com's speaker page is the shared Foam Expo + Adhesives & Bonding conference (adhesive-only speakers appear
# on it) but is not flagged combined in the harvest file. Its sponsor page is show-specific and stays.
COMBINED = {("foam-expo-north-america", "speaker")}
MEDIA_PARTNERS = re.compile(r"/(supporters|media-partners?)\b", re.I)  # media partners are not sponsors
COUNTRY = {"DE": "Germany", "CA": "Canada", "MX": "Mexico", "GB": "United Kingdom", "FR": "France", "IT": "Italy",
           "CN": "China", "JP": "Japan", "IN": "India", "NL": "Netherlands", "CH": "Switzerland"}
PERSONAL = re.compile(r"[\w.+-]+@[\w-]+\.|\b(Dr|Mr|Mrs|Ms|Prof)\.?\s+[A-Z]|\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}")


def norm(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s)).replace(" ", " ").replace("’", "'")
    return re.sub(r"\s+", " ", s).lower()


def edition(conf_dir, slug, year):
    p = Path(conf_dir) / "data" / "series" / f"{slug}.yaml"
    if not p.exists():
        return {}
    s = yaml.safe_load(p.read_text(encoding="utf-8"))
    return next((e for e in s["editions"] if str(e["year"]) == str(year)), {})


def state(ed):
    """SCHEMA 4.12.2: a USPS code for a US edition, else the full country name; empty when unknown."""
    if not ed:
        return ""
    if ed.get("country", "US") == "US":
        return ed.get("region") or ""
    return COUNTRY.get(ed["country"], "")  # shortcut: small map; add a country when a new one appears


def org_index(data):
    by_key = {}
    for f in sorted(data.glob("organizations_*.csv")):
        for o in read(f):
            if o["status"] not in ("active", "unknown"):
                continue
            for n in [o["legal_name"]] + (o.get("trade_names") or "").split(";"):
                k = A.name_key(n)
                if k and len(k) >= 4:
                    by_key.setdefault(k, set()).add(o["org_id"])
    return by_key


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--harvest", required=True, help="staging harvest-2026-11 folder (shows.csv, out/)")
    ap.add_argument("--conferences", required=True, help="the conferences repo checkout (edition facts)")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    a = ap.parse_args()
    data, hv = Path(a.data_dir).resolve(), Path(a.harvest).resolve()
    events = {e["event_id"]: e for e in read(data / "events.csv")}
    emap = {r["conf_slug"]: r["event_id"] for r in read(HERE / "event_map.csv")}
    shows = {r["show_key"]: r for r in read(hv / "shows.csv")}
    drops = {(r["show_key"], r["role"], r["name"]) for r in read(HERE / "controller_drops.csv")}
    by_key = org_index(data)
    part = read(data / "event_participation.csv")
    have = {(p["event_id"], p["org_id"], p["edition_year"], p["role"]) for p in part}
    nxt = max(int(p["participation_id"][4:]) for p in part) + 1

    matches, leads, rows, skip, lists_used = [], [], [], Counter(), Counter()
    for f in sorted((hv / "out").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        key = d["show_key"]
        if shows.get(key, {}).get("wave") != "1":
            continue
        slug = key.split(":")[0]
        ev = UMBRELLA.get(emap.get(slug, ""), emap.get(slug, ""))
        for L in d["lists"]:
            role, n_co = L["role"], len(L["companies"])
            if role not in ROLES:
                skip[f"{role} list (waits for v1.12)"] += n_co; continue
            if not ev or ev not in events:
                skip["series not held in events.csv"] += n_co; continue
            if MEDIA_PARTNERS.search(L["source_url"]):
                skip["media-partner list, not sponsors"] += n_co; continue
            if (slug, role) in COMBINED or L.get("covers_multiple_shows") and ev not in UMBRELLA_EVENTS and \
                    not any(c.get("show_assignment") for c in L["companies"]):
                skip["combined co-located list, no per-company show"] += n_co; continue
            yr = str(L["list_edition_year"])
            ed = edition(a.conferences, slug, yr)
            abroad = bool(ed) and ed.get("country", "US") != "US" or (not ed and shows[key]["city"].endswith(
                tuple(f", {c}" for c in COUNTRY)))
            raw = norm((hv / L["raw_file"]).read_text(encoding="utf-8", errors="replace"))
            lists_used[(key, role, yr)] += 1
            for c in L["companies"]:
                name = c["name"].strip()
                if (key, role, name) in drops:
                    skip["controller drop"] += 1; continue
                if c.get("show_assignment") and A.name_key(c["show_assignment"]) != A.name_key(events[ev]["name"]):
                    skip["labelled for a co-located show"] += 1; continue
                if norm(name) not in raw:
                    skip["name not verbatim on the banked page"] += 1; continue
                if abroad and not c.get("country"):
                    skip["edition abroad, list gives no country"] += 1; continue
                ids = by_key.get(A.name_key(name), set())
                if len(ids) != 1:
                    (leads.append({"show_key": key, "role": role, "year": yr, "name": name}) if not ids
                     else skip.update(["ambiguous name key"]))
                    continue
                org = next(iter(ids))
                matches.append({"show_key": key, "event_id": ev, "edition_year": yr, "role": role, "listed_name": name,
                                "source_url": L["source_url"], "org_id": org})
                k = (ev, org, yr, role)
                if k in have:
                    skip["already held"] += 1; continue
                have.add(k)
                detail = {"exhibitor": c.get("booth", ""), "sponsor": c.get("sponsor_level", ""),
                          "speaker": c.get("session_title", "")}[role].strip()
                if PERSONAL.search(detail):
                    detail = ""
                partial = "" if L.get("complete") else " The organizer's list was not read to the end (partial)."
                pre = " Pre-show list, still filling as of the evidence date." if role == "exhibitor" and \
                    str(ed.get("start", "")) > d["retrieved"] else ""
                e = events[ev]
                rows.append({
                    "participation_id": f"EVP-{nxt:06d}", "event_id": ev, "org_id": org, "edition_year": yr,
                    "edition_name": "", "role": role, "role_detail": detail,
                    "edition_dates": f"{ed['start']} to {ed['end']}" if ed.get("start") and ed.get("end") else "",
                    "edition_city": ed.get("city", ""), "edition_state": state(ed),
                    "evidence_source_name": f"{e['name']} {yr} {role} list (organizer-published)",
                    "evidence_source_url": L["source_url"], "evidence_date": d["retrieved"],
                    "sources": f"{L['source_url']} (read {d['retrieved']}; listed as \"{name}\")",
                    "verification_tier": "A", "last_verified": d["retrieved"], "created_by": BY,
                    "notes": f"{role.capitalize()} name matched to the org by exact normalized legal/trade name; "
                             f"list banked in staging (harvest-2026-11, {key})." + pre + partial
                             + (" Co-located AMI expos share one list; recorded under the umbrella event."
                                if ev == "EVT-000007" else "")})
                nxt += 1

    fields = list(part[0].keys())
    for name, rs, cols in (("matches.csv", matches, list(matches[0]) if matches else ["show_key"]),
                           ("participation_append.csv", rows, fields)):
        with open(HERE / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
            w.writeheader(); w.writerows(rs)
    (hv / "controller").mkdir(exist_ok=True)
    with open(hv / "controller" / "w1_leads.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["show_key", "role", "year", "name"], lineterminator="\n")
        w.writeheader(); w.writerows(leads)
    print(f"lists used {len(lists_used)}; matches {len(matches)}; rows {len(rows)}; leads {len(leads)}")
    print("rows by event/role", sorted(Counter((r['event_id'], r['role'], r['edition_year']) for r in rows).items()))
    print("skipped", dict(skip))
    if a.apply:
        if data == (HERE.parents[1] / "data").resolve() and not a.i_am_the_integrator:
            sys.exit("appending to the real data/ is integrator work; pass --i-am-the-integrator")
        append_rows(data / "event_participation.csv", rows)
        print("applied")


if __name__ == "__main__":
    main()
