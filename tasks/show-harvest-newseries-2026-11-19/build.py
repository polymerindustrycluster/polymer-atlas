#!/usr/bin/env python3
"""Participation rows for the 27 event series seeded in PR #409 (EVT-000072..EVT-000098), from the banked show
harvest, organization grain only.

    python3 tasks/show-harvest-newseries-2026-11-19/build.py --data-dir data --harvest <staging harvest dir> \
        --conferences ../conferences [--apply --i-am-the-integrator]

These series' lists were never read by an earlier pass, so every name on them is judged here. The gates are those of
tasks/show-harvest-w23-2026-11-18 and tasks/show-harvest-rulings-2026-11-19, applied unchanged:
- a name is on the list when it is in the page's visible text or a real alt/title attribute (owner ruling
  2026-11-18c); a name rebuilt from a URL or file name is not;
- a legal-name match to exactly one active/unknown organization; a trade-name hit is held (trade_name_holds.csv);
- an edition abroad mints only when the list gives the company's country and it equals the organization's
  hq_country;
- the controller drop lists of waves 1 and 2-3; the media-partner, not-an-event-list and combined-list exclusions;
- the list's own edition year, with pre-show and partial notes;
- attendee rows only from ATTENDEE_LISTS: organizer-published company lists for a named edition, checked on the
  banked page (owner rulings 2026-11-09 and 2026-11-18c);
- CONTROLLER_HOLDS: listed forms that do not pin one legal entity (a bare group name whose Atlas record is the
  group's US entity, or a generic name), binding that listed form at the event in every role and year. A listed
  form naming the US entity itself ("Evonik Corporation") pins it and is not held. Every hold must match a
  listing, so a mistyped hold fails the build;
- an international series (home_region, set from the organizer in #409) is held abroad: the conferences editions
  of these series mostly carry no country, and the wave 2-3 default of "US" would credit US companies with
  exhibiting in Sao Paulo or Queretaro.
Writes participation_append.csv and trade_name_holds.csv here.
"""
import argparse, csv, hashlib, importlib.util, json, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASKS = HERE.parent
W1, W23, RUL = (TASKS / "show-harvest-w1-2026-11-06", TASKS / "show-harvest-w23-2026-11-18",
                TASKS / "show-harvest-rulings-2026-11-19")
sys.path.insert(0, str(HERE.parents[1] / "scripts"))
sys.path.insert(0, str(TASKS / "census-gap-people-2026-11-03"))
sys.path.insert(0, str(W23))
import atlas as A  # noqa: E402
import decisions  # noqa: E402  (the wave 2-3 review decisions; their holds bind here too)
from build_integration import append_rows, read  # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


w23, rul = _load("w23_build", W23 / "build.py"), _load("rulings_build", RUL / "build.py")
MEDIA_PARTNERS, NOT_EVENT_LISTS, PERSONAL = w23.MEDIA_PARTNERS, w23.NOT_EVENT_LISTS, w23.PERSONAL
edition, iso, org_index, state, text, norm = w23.edition, w23.iso, w23.org_index, w23.state, rul.text, rul.norm

BY = "claude-code show-harvest-newseries-2026-11-19"
NEW_EVENTS = {f"EVT-{n:06d}" for n in range(72, 99)}  # seeded by PR #409
ROLES = {"exhibitor", "sponsor", "speaker"}
ATTENDEE_LISTS = {  # source_url -> (the one event it may mint for, the note every row from it carries)
    "https://www.pcimag.com/coatings-conference/registered-companies": (
        "EVT-000077", "Attendee: the organizer's \"final list of registered companies\" for the 2026 edition."),
    "https://greatlakescoatingsconference.com/attending/": (
        "EVT-000082", "Attendee: the organizer's list \"Companies attended in 2025\"."),
}
US_ARM = "(i) a bare group name; the Atlas record is the group's US entity"
CONTROLLER_HOLDS = {  # (event_id, the listed form as norm() gives it) -> reason. Held: the bare group name. Not held:
    # a listed form that names the US entity itself (e.g. "Evonik Corporation", "BASF Corporation"), which pins it.
    ("EVT-000072", "armacell"): US_ARM + " (Armacell LLC; the group is based in Luxembourg)",
    ("EVT-000072", "henkel"): US_ARM + " (Henkel Corporation)",
    ("EVT-000077", "evonik"): US_ARM + " (Evonik Corporation)",
    ("EVT-000077", "covestro"): US_ARM + " (Covestro LLC)",
    ("EVT-000077", "basf"): US_ARM + " (BASF Corporation)",
    ("EVT-000077", "omya"): US_ARM + " (Omya, Inc.; the group is Swiss)",
    ("EVT-000077", "arkema"): US_ARM + " (Arkema Inc.)",
    ("EVT-000077", "sun chemical"): US_ARM + " (Sun Chemical Corporation of a global group; as held at SAMPE in #404)",
    ("EVT-000082", "basf"): US_ARM + " (BASF Corporation)",
    ("EVT-000082", "covestro"): US_ARM + " (Covestro LLC)",
    ("EVT-000082", "henkel"): US_ARM + " (Henkel Corporation)",
    ("EVT-000082", "lanxess"): US_ARM + " (LANXESS Corporation)",
    ("EVT-000082", "omya"): US_ARM + " (Omya, Inc.)",
    ("EVT-000082", "sun chemical"): US_ARM + " (Sun Chemical Corporation)",
    ("EVT-000082", "synthomer"): US_ARM + " (Synthomer, Inc.; the group is British)",
    ("EVT-000082", "resin solutions"): "(ii) a generic name; the list gives nothing that picks the Exton PA company",
    ("EVT-000092", "alberdingk boley"): US_ARM + " (Alberdingk Boley, Inc.; the group is German)",
    ("EVT-000092", "arkema"): US_ARM + " (Arkema Inc.)",
    ("EVT-000095", "polyfil"): "(ii) the list gives only the name and country; nothing ties a tire-trade exhibitor to the "
                               "Rockaway NJ masterbatch maker",
    ("EVT-000098", "evonik"): US_ARM + " (Evonik Corporation)",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--harvest", required=True)
    ap.add_argument("--conferences", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    a = ap.parse_args()
    data, hv = Path(a.data_dir).resolve(), Path(a.harvest).resolve()
    events = {e["event_id"]: e for e in read(data / "events.csv")}
    emap = {s.strip(): e["event_id"] for e in events.values()
            for s in (e.get("pic_events_slug") or "").split(";") if s.strip()}
    shows = {r["show_key"]: r for r in read(hv / "shows.csv")}
    drops = {(r["show_key"], r["role"], r["name_sha256_16"]) for p in (W1, W23) for r in read(p / "controller_drops.csv")}
    by_key, orgs = org_index(data)
    held = {(e, nk) for e, _role, nk in decisions.held_names(
        decisions.load(W23 / "review_decisions.csv", events, orgs, shows=set(shows)))}
    hit = set()
    part = read(data / "event_participation.csv")
    have = {(p["event_id"], p["org_id"], p["edition_year"], p["role"]) for p in part}
    nxt = max(int(p["participation_id"][4:]) for p in part) + 1

    rows, holds, skip = [], [], Counter()
    for f in sorted((hv / "out").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        key = d["show_key"]
        slug = key.split(":")[0]
        ev = emap.get(slug, "")
        if ev not in NEW_EVENTS:
            continue
        for L in d["lists"]:
            role, url, n_co = L["role"], L["source_url"], len(L["companies"])
            attendee = role == "attendee" and ATTENDEE_LISTS.get(url, ("",))[0] == ev
            if role not in ROLES and not attendee:
                skip[f"{role} list not admitted"] += n_co; continue
            if MEDIA_PARTNERS.search(url) or url in NOT_EVENT_LISTS:
                skip["media-partner or not-an-event list"] += n_co; continue
            one_show = len(set(L.get("shows_covered") or [])) <= 1
            if L.get("covers_multiple_shows") and not one_show and not any(c.get("show_assignment")
                                                                            for c in L["companies"]):
                skip["combined co-located list, no per-company show"] += n_co; continue
            yr = str(L["list_edition_year"])
            ed = edition(a.conferences, slug, yr)
            # The conferences editions of these new series mostly carry no country (and ICERP's is mis-keyed US with
            # region IN), so the wave 2-3 default of "US" is unsafe here. #409 set home_region from the organizer:
            # an international series is held abroad, and a national one abroad only if its edition says so.
            abroad = events[ev]["home_region"] == "international" or ed.get("country", "US") != "US"
            if abroad and ed.get("country") in (None, "US"):
                ed = {k: v for k, v in ed.items() if k in ("start", "end", "city")}  # no country/region to trust
            page = text((hv / L["raw_file"]).read_text(encoding="utf-8", errors="replace"), True)
            for c in L["companies"]:
                name = c["name"].strip()
                if norm(name) not in page:
                    skip["name not on the page (visible or alt text)"] += 1; continue
                if (key, role, hashlib.sha256(name.encode("utf-8")).hexdigest()[:16]) in drops:
                    skip["controller drop"] += 1; continue
                if c.get("show_assignment") and A.name_key(c["show_assignment"]) != A.name_key(events[ev]["name"]):
                    skip["labelled for a co-located show"] += 1; continue
                nk = A.name_key(name)
                if (ev, nk) in held:
                    skip["held by the wave 2-3 review"] += 1; continue
                if (ev, norm(name)) in CONTROLLER_HOLDS:
                    hit.add((ev, norm(name)))
                    skip["held (CONTROLLER_HOLDS)"] += 1; continue
                hits = by_key.get(nk, {})
                if len(hits) != 1:
                    skip["no Atlas organization" if not hits else "ambiguous name key"] += 1; continue
                org, kind = next(iter(hits.items()))
                if abroad and (not iso(c.get("country")) or iso(c["country"]) != iso(orgs[org]["hq_country"])):
                    skip["edition abroad, listed country missing or not the org's HQ country"] += 1; continue
                if kind == "trade":
                    holds.append({"show_key": key, "event_id": ev, "edition_year": yr, "role": role,
                                  "listed_name": name, "org_id": org, "legal_name": orgs[org]["legal_name"],
                                  "trade_names": orgs[org].get("trade_names", ""), "source_url": url})
                    skip["trade-name hit, held"] += 1; continue
                k = (ev, org, yr, role)
                if k in have:
                    skip["already held"] += 1; continue
                have.add(k)
                detail = ({"exhibitor": c.get("booth"), "sponsor": c.get("sponsor_level"),
                           "speaker": c.get("session_title"), "attendee": ""}[role] or "").strip()
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
                    "evidence_source_url": url, "evidence_date": d["retrieved"],
                    "sources": f"{url} (read {d['retrieved']}; listed as \"{name}\")",
                    "verification_tier": "A", "last_verified": d["retrieved"], "created_by": BY,
                    "notes": f"{role.capitalize()} name matched to the org by exact normalized legal name; list banked "
                             f"in staging (harvest-2026-11, {key})." + staged + pre + partial
                             + (f" {ATTENDEE_LISTS[url][1]}" if attendee else "")
                             + (f" Edition abroad: the list gives the company's country ({c['country']}), which "
                                f"matches the organization's HQ country." if abroad else "")})
                nxt += 1

    unused = set(CONTROLLER_HOLDS) - hit
    assert not unused, f"CONTROLLER_HOLDS that matched no listing: {sorted(unused)}"
    fields = list(part[0].keys())
    for fname, rs, cols in (("participation_append.csv", rows, fields),
                            ("trade_name_holds.csv", holds, list(holds[0]) if holds else ["show_key"])):
        with open(HERE / fname, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
            w.writeheader(); w.writerows(rs)
    print(f"rows {len(rows)}; trade-name holds {len(holds)}")
    print("rows by event/role/year", sorted(Counter((r['event_id'], r['role'], r['edition_year']) for r in rows).items()))
    print("skipped", dict(skip))
    if a.apply:
        if data == (HERE.parents[1] / "data").resolve() and not a.i_am_the_integrator:
            sys.exit("appending to the real data/ is integrator work; pass --i-am-the-integrator")
        append_rows(data / "event_participation.csv", rows)
        print("applied")


if __name__ == "__main__":
    main()
