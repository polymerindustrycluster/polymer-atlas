#!/usr/bin/env python3
"""Seed the event series that qualify among the show harvest's untracked series (2026-11-19).

    python3 tasks/new-series-2026-11-19/build.py --data-dir data [--apply --i-am-the-integrator]

Input: verdicts.csv here, one row per researched candidate: the organizer's own subject statement (quoted, with its
URL, read 2026-11-19 by a codex research lane and cross-checked by agy, Gemini 4 Hydrogen), the proposed series
fields, and the verdict with its basis (the lane, or the owner rulings of 2026-11-19 in
tasks/owner-rulings-2026-11-19/). Each IN row becomes one data/events.csv row (SCHEMA 4.12.1), IDs allocated from
the table's maximum. Borderline and owner-ruled calls, and the OUT calls that name a polymer subject, also get a
data/inclusion_log.csv row (SCHEMA Appendix A). No participation row is created here.
"""
import argparse, csv, sys
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "census-gap-people-2026-11-03"))
from build_integration import append_rows, read  # noqa: E402

BY = "claude-code new-series-2026-11-19"
READ = "2026-11-19"
NAME = {  # the series name as the organizer styles it, without edition year or city (SCHEMA 4.12.1)
    "expoplast-montreal": "EXPOPLAST", "plastics-recycling-show-brazil-prs-brazil": "Plastics Recycling Show Brazil",
}
TRADE = {"plastics-recycling-show-brazil-prs-brazil": "PRS Brazil", "expoplast-montreal": "EXPOPLAST Montréal"}
ORGANIZER_ID = {"meximold": "ORG-001502", "carbon-fiber": "ORG-001502"}  # Gardner Business Media (CompositesWorld)
LOG_OUT = {"acs-poly-fall-show", "amlci-materials-day-polymers-and-elastomers", "ami-textile-recycling-expo-europe",
           "ami-textiles-recycling-expo-usa", "moulding-expo", "geosynthetics-conference"}  # OUT calls naming polymers


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    a = ap.parse_args()
    data = Path(a.data_dir).resolve()
    conf = Path(a.data_dir).resolve().parents[2] / "conferences" / "data" / "series"
    events = read(data / "events.csv")
    held_slugs = {s.strip() for e in events for s in (e.get("pic_events_slug") or "").split(";") if s.strip()}
    names = {e["name"].lower() for e in events}
    domains = {urlsplit(e["event_url"]).netloc.lower().removeprefix("www.") for e in events if e["event_url"]}
    nxt = max(int(e["event_id"][4:]) for e in events) + 1
    verdicts = read(HERE / "verdicts.csv")
    rows, log = [], []
    for v in sorted(verdicts, key=lambda v: v["slug"]):
        slug = v["slug"]
        assert slug not in held_slugs, f"{slug} is already an Atlas series"
        if v["verdict"] == "IN":
            name = NAME.get(slug) or yaml_name(conf, slug)
            assert name.lower() not in names, f"{name} duplicates an Atlas series name"
            # SCHEMA 4.12.1 dedupe, step 1: the event_url domain (one organizer domain can host several series, so a
            # hit is printed for the controller to settle, not asserted)
            dom = urlsplit(v["event_url"]).netloc.lower().removeprefix("www.")
            if dom in domains:
                print(f"domain shared with an Atlas series, settle by hand: {slug} {dom}")
            owner = v["basis"].startswith("owner ruling")
            # SCHEMA 4.12.1: an international series leaves home_state empty and names the country in geography_note
            intl, country = v["home_region"] == "international", v["home_state"]
            geo = v["geography_note"]
            if intl and country and country.lower() not in geo.lower():
                geo = f"{geo.rstrip('.')}; {country}."
            rows.append({
                "event_id": f"EVT-{nxt:06d}", "name": name, "trade_names": TRADE.get(slug, ""),
                "organizer_name": v["organizer_name"].replace(";", "; "), "organizer_org_id": ORGANIZER_ID.get(slug, ""),
                "event_format": v["event_format"], "cadence": v["cadence"],
                "cadence_note": v["cadence_note"] if v["cadence"] == "irregular" else "",  # V-17: only if irregular
                "typical_timing": v["typical_timing"], "home_city": v["home_city"],
                "home_state": "" if intl else v["home_state"], "home_region": v["home_region"], "geography_note": geo,
                "subject_scope": v["subject_scope"], "subject_note": f"\"{v['subject_quote']}\" ({v['subject_quote_url']})",
                "event_url": v["event_url"], "status": "active", "status_date": "", "status_source": "",
                "sources": f"Organizer's own site, read {READ}: {v['subject_quote_url']} (subject statement); edition "
                           f"facts from the PIC conferences repo, data/series/{slug}.yaml",
                "verification_tier": "A", "last_verified": READ, "pic_relevance": "", "created_by": BY,
                "notes": (f"Seeded {READ} from the show harvest's untracked series (tasks/new-series-2026-11-19): "
                          f"named-subject prong (a). Basis: {v['basis']}."
                          + (f" Cadence: {v['cadence_note'].rstrip('.')}." if v["cadence"] != "irregular"
                             and v["cadence_note"] else "")
                          + (f" {v['umbrella_or_colocated'][0].upper()}{v['umbrella_or_colocated'][1:]}."
                             if v["umbrella_or_colocated"] not in ("", "none") else "")),
                "pic_events_slug": slug})
            nxt += 1
            if owner:
                log.append(entry(v, f"include — Atlas event series {rows[-1]['event_id']}", owner=True))
        elif slug in LOG_OUT:
            log.append(entry(v, "exclude — not an Atlas event series", owner=v["basis"].startswith("owner ruling")))
    print(f"series rows {len(rows)} ({rows[0]['event_id']}..{rows[-1]['event_id']}); inclusion-log rows {len(log)}")
    with open(HERE / "events_append.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(events[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
    il = read(data / "inclusion_log.csv")
    with open(HERE / "inclusion_log_append.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(il[0]), lineterminator="\n"); w.writeheader(); w.writerows(log)
    if a.apply:
        if data == (HERE.parents[1] / "data").resolve() and not a.i_am_the_integrator:
            sys.exit("appending to the real data/ is integrator work; pass --i-am-the-integrator")
        append_rows(data / "events.csv", rows)
        append_rows(data / "inclusion_log.csv", log)
        print("applied")


def yaml_name(conf, slug):
    import yaml
    return yaml.safe_load(open(conf / f"{slug}.yaml", encoding="utf-8"))["name"]


def entry(v, decision, owner):
    return {"date": READ, "entity": f"{v['organizer_name'].split(';')[0]}: {v['slug']}", "decision": decision,
            "rule_cited": "SCHEMA §4.12.1 named-subject qualification test" + (" (owner ruling 2026-11-19)" if owner else ""),
            "researcher": BY,
            "notes": f"Organizer's statement ({v['subject_quote_url']}): \"{v['subject_quote']}\". {v['reason']}"}


if __name__ == "__main__":
    main()
