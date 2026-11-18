#!/usr/bin/env python3
"""Show harvest waves 2-3 (2026-11-18): exhibitor, sponsor and speaker participation rows from organizer-published
lists, organization grain only, for event series already held in data/events.csv.

    python3 tasks/show-harvest-w23-2026-11-18/build.py --data-dir data --harvest <staging harvest dir> \
        --conferences ../conferences [--apply --i-am-the-integrator]

Same method as tasks/show-harvest-w1-2026-11-06/build.py, plus the lessons of its 2026-11-09 review:
- Show slug -> event from events.csv `pic_events_slug` (schema v1.12), not a side file.
- A name mints only when its normalized key (atlas.name_key) is the LEGAL name of exactly one active/unknown
  organization. A hit on a trade name only is held for review (trade_name_holds.csv): trade_names carries brands,
  parents and subsidiaries, and #252 credited Coperion to Hillenbrand that way. review_decisions.csv records the
  cross-family review: trade-name hits both families judged the same entity (`accept`, for one org) and legal-name
  hits the review held (`hold`), each keyed by show, role, edition year and listed name.
- An edition abroad mints only when the list gives the company's country AND it equals the organization's
  hq_country; otherwise held (the Momentive GmbH / MPM Silicones LLC trap, tasks/exhibitor-links-2026-11-06).
- Attendee lists are not minted here: SPE Polyolefins 2026 is a delegate list naming people (owner ruling
  2026-11-09: never mints), and SAMPE 2026's company list sits in a sponsorship brochure (owner question).
- A name must appear verbatim in the visible text of its banked raw file. Logo alt text and names rebuilt from
  links or file names are held (owner question on alt text, 2026-11-09).
Writes matches.csv, participation_append.csv and trade_name_holds.csv here; unmatched names go to
<harvest>/controller/ (never committed).
"""
import argparse, csv, hashlib, html, json, re, sys
from collections import Counter
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "scripts"))
sys.path.insert(0, str(HERE.parent / "census-gap-people-2026-11-03"))
sys.path.insert(0, str(HERE))
import atlas as A  # noqa: E402
import decisions  # noqa: E402
from build_integration import append_rows, read  # noqa: E402

BY = "claude-code show-harvest-w23-2026-11-18"
WAVES = {"2", "3"}
ROLES = {"exhibitor", "sponsor", "speaker"}
MEDIA_PARTNERS = re.compile(r"(supporters|media[-_ ]?partners?|cooperating[-_ ]?media)", re.I)  # not sponsors
# shortcut: a small country map; a country missing here is held (never guessed), add it when one appears
ISO = {"us": "US", "usa": "US", "u.s.a.": "US", "united states": "US", "united states of america": "US",
       "germany": "DE", "deutschland": "DE", "france": "FR", "canada": "CA", "united kingdom": "GB", "uk": "GB",
       "great britain": "GB", "japan": "JP", "italy": "IT", "belgium": "BE", "norway": "NO", "netherlands": "NL",
       "switzerland": "CH", "austria": "AT", "china": "CN", "india": "IN", "mexico": "MX", "spain": "ES"}
for _c in list(ISO.values()):
    ISO[_c.lower()] = _c
COUNTRY_NAME = {"DE": "Germany", "FR": "France", "JP": "Japan", "CA": "Canada", "GB": "United Kingdom",
                "IT": "Italy", "CN": "China", "IN": "India", "MX": "Mexico", "NL": "Netherlands", "CH": "Switzerland"}
# lists the harvest filed under an event that are not that event's lists (read on the banked page)
NOT_EVENT_LISTS = {
    "https://www.blowmoldingdivision.org/corporate-education-sponsors":
        "the SPE Blow Molding Division's 2025 scholarship sponsors, not sponsors of an ABC conference edition",
}
# The cross-family review of PR #384 (codex + agy, 2026-11-18) lives in review_decisions.csv, loaded and validated by
# decisions.py (shared with check.py): `hold` = a legal-name hit that does not pin one legal entity, `accept` = a
# trade-name hit both families judged the same entity. Each applies only to its show, role, year, name AND org.
REVIEW_NOTES = {
    ("sampe-conference-and-exhibition:2027", "exhibitor", "2027", "Fiber Dynamics"):
        ' Listed in a joint entry, "NIAR | Fiber Dynamics | FILL USA INC".',
}
USPS = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH "
           "OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY PR".split())
PERSONAL = re.compile(r"[\w.+-]+@[\w-]+\.|\b(Dr|Mr|Mrs|Ms|Prof)\.?\s+[A-Z]|\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}")


def norm(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s)).replace(" ", " ").replace("’", "'")
    return re.sub(r"\s+", " ", s).lower()


def iso(country):
    return ISO.get((country or "").strip().lower(), "")


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
    return COUNTRY_NAME.get(ed["country"], "")


def org_index(data):
    """name_key -> {org_id: 'legal' | 'trade'}; legal wins when one org holds the key both ways."""
    by_key, orgs = {}, {}
    for f in sorted(data.glob("organizations_*.csv")):
        for o in read(f):
            if o["status"] not in ("active", "unknown"):
                continue
            orgs[o["org_id"]] = o
            for kind, names in (("trade", (o.get("trade_names") or "").split(";")), ("legal", [o["legal_name"]])):
                for n in names:
                    k = A.name_key(n)
                    if k and len(k) >= 4:
                        by_key.setdefault(k, {})[o["org_id"]] = kind
    return by_key, orgs


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
    emap = {s.strip(): e["event_id"] for e in events.values()
            for s in (e.get("pic_events_slug") or "").split(";") if s.strip()}
    shows = {r["show_key"]: r for r in read(hv / "shows.csv")}
    # names are stored hashed: a drop can be a person's name, and this repo is public (AGENTS section 6)
    drops = {(r["show_key"], r["role"], r["name_sha256_16"]) for r in read(HERE / "controller_drops.csv")}
    by_key, orgs = org_index(data)
    review = decisions.load(HERE / "review_decisions.csv", events, orgs)
    part = read(data / "event_participation.csv")
    have = {(p["event_id"], p["org_id"], p["edition_year"], p["role"]) for p in part}
    nxt = max(int(p["participation_id"][4:]) for p in part) + 1

    matches, leads, holds, rows, skip = [], [], [], [], Counter()
    for f in sorted((hv / "out").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        key = d["show_key"]
        if shows.get(key, {}).get("wave") not in WAVES:
            continue
        slug = key.split(":")[0]
        ev = emap.get(slug, "")
        for L in d["lists"]:
            role, n_co = L["role"], len(L["companies"])
            if role not in ROLES:
                skip[f"{role} list (not minted in this pass)"] += n_co; continue
            if ev not in events:
                skip["series not held in events.csv"] += n_co; continue
            if MEDIA_PARTNERS.search(L["source_url"]):
                skip["media-partner list, not sponsors"] += n_co; continue
            if L["source_url"] in NOT_EVENT_LISTS:
                skip["not a list for this event (see NOT_EVENT_LISTS)"] += n_co; continue
            # Fakuma's list is flagged combined only because shows.csv also carries a "market visit" key that the
            # organizer never lists separately (shows_covered = the one show); any other combined list is skipped.
            one_show = len(set(L.get("shows_covered") or [])) <= 1 or slug == "fakuma"
            if L.get("covers_multiple_shows") and not one_show and not any(c.get("show_assignment")
                                                                            for c in L["companies"]):
                skip["combined co-located list, no per-company show"] += n_co; continue
            yr = str(L["list_edition_year"])
            ed = edition(a.conferences, slug, yr)
            # no edition in the conferences repo for the list year: mint with empty dates, place from shows.csv
            city = shows[key]["city"]
            abroad = ed.get("country", "US") != "US" if ed else city.rsplit(", ", 1)[-1] not in USPS
            raw = norm((hv / L["raw_file"]).read_text(encoding="utf-8", errors="replace"))
            for c in L["companies"]:
                name = c["name"].strip()
                if (key, role, hashlib.sha256(name.encode("utf-8")).hexdigest()[:16]) in drops:
                    skip["controller drop"] += 1; continue
                if c.get("show_assignment") and A.name_key(c["show_assignment"]) != A.name_key(events[ev]["name"]):
                    skip["labelled for a co-located show"] += 1; continue
                if norm(name) not in raw:
                    skip["name not in the page's visible text (logo alt text or rebuilt)"] += 1; continue
                hits = by_key.get(A.name_key(name), {})
                if len(hits) != 1:
                    (leads.append({"show_key": key, "role": role, "year": yr, "name": name}) if not hits
                     else skip.update(["ambiguous name key"]))
                    continue
                org, kind = next(iter(hits.items()))
                decision = review.get((key, role, yr, A.name_key(name)), {})
                if decision.get("org_id") != org:
                    decision = {}  # a decision binds only the organization it names
                if decision.get("decision") == "hold":
                    skip["held by the cross-family review (review_decisions.csv)"] += 1; continue
                if abroad and (not iso(c.get("country")) or iso(c["country"]) != iso(orgs[org]["hq_country"])):
                    skip["edition abroad, listed country missing or not the org's HQ country"] += 1; continue
                accepted = decision["reason"] if kind == "trade" and decision.get("decision") == "accept" else None
                if kind == "trade" and not accepted:
                    holds.append({"show_key": key, "event_id": ev, "edition_year": yr, "role": role,
                                  "listed_name": name, "org_id": org, "legal_name": orgs[org]["legal_name"],
                                  "trade_names": orgs[org].get("trade_names", ""), "source_url": L["source_url"]})
                    skip["trade-name hit, held for review"] += 1; continue
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
                pre = " Pre-show list, still filling as of the evidence date." \
                    if str(ed.get("start", "")) > d["retrieved"] else ""
                staged = f" The staging key's year ({key.split(':')[1]}) is the harvest's edition label; the row " \
                    f"year follows the year printed in the source." if key.split(":")[1] != yr else ""
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
                    "notes": (f"{role.capitalize()} name matched to the org by exact normalized legal name; " if not
                              accepted else f"{role.capitalize()} name matched a trade name, adjudicated the same "
                              f"entity by cross-family review: {accepted}; ")
                             + f"list banked in staging (harvest-2026-11, {key})." + staged + pre + partial
                             + REVIEW_NOTES.get((key, role, yr, name), "")
                             + (f" Edition abroad: the list gives the company's country ({c['country']}), which "
                                f"matches the organization's HQ country." if abroad else "")})
                nxt += 1

    fields = list(part[0].keys())
    for fname, rs, cols in (("matches.csv", matches, list(matches[0]) if matches else ["show_key"]),
                            ("participation_append.csv", rows, fields),
                            ("trade_name_holds.csv", holds, list(holds[0]) if holds else ["show_key"])):
        with open(HERE / fname, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
            w.writeheader(); w.writerows(rs)
    (hv / "controller").mkdir(exist_ok=True)
    with open(hv / "controller" / "w23_leads.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["show_key", "role", "year", "name"], lineterminator="\n")
        w.writeheader(); w.writerows(leads)
    print(f"matches {len(matches)}; rows {len(rows)}; trade-name holds {len(holds)}; leads {len(leads)}")
    print("rows by event/role/year", sorted(Counter((r['event_id'], r['role'], r['edition_year']) for r in rows).items()))
    print("skipped", dict(skip))
    if a.apply:
        if data == (HERE.parents[1] / "data").resolve() and not a.i_am_the_integrator:
            sys.exit("appending to the real data/ is integrator work; pass --i-am-the-integrator")
        append_rows(data / "event_participation.csv", rows)
        print("applied")


if __name__ == "__main__":
    main()
