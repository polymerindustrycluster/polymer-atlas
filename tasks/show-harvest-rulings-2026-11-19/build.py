#!/usr/bin/env python3
"""Apply the owner rulings of 2026-11-18 to the banked show harvest, for event series already held: participation
rows for exactly the evidence those rulings newly admit, and nothing else.

    python3 tasks/show-harvest-rulings-2026-11-19/build.py --data-dir data --harvest <staging harvest dir> \
        --conferences ../conferences [--apply --i-am-the-integrator]

The rulings (tasks/owner-rulings-2026-11-18c/README.md):
- A company list the organizer published for a named edition counts as an attendee list even when it is printed in
  the organizer's own sponsorship brochure (SAMPE 2026, "Industry leaders were here"). Only the lists in
  ATTENDEE_LISTS mint attendee rows; delegate lists that name people never do (SPE Polyolefins 2026).
- A name the organizer wrote as a logo's alt or title text counts as on the page. A name rebuilt from a link URL or
  an image file name never does.
Scope is deliberately narrow, so no row an earlier review removed can return: from exhibitor/sponsor/speaker lists
only names that appear in alt/title text and NOT in the visible text (the earlier passes already judged every
visible name); from ATTENDEE_LISTS every visible name. Every other gate of tasks/show-harvest-w23-2026-11-18 holds:
legal-name match to exactly one active/unknown organization (trade-name hits are held), the abroad country rule,
the controller drop lists of waves 1 and 2-3, that pass's review holds, combined-list and media-partner exclusions,
the AMI umbrella mapping of wave 1, and the list's own edition year.
"""
import argparse, csv, hashlib, html, importlib.util, json, re, sys
from html.parser import HTMLParser
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
W1, W23 = HERE.parent / "show-harvest-w1-2026-11-06", HERE.parent / "show-harvest-w23-2026-11-18"
sys.path.insert(0, str(HERE.parents[1] / "scripts"))
sys.path.insert(0, str(HERE.parent / "census-gap-people-2026-11-03"))
sys.path.insert(0, str(W23))
import atlas as A  # noqa: E402
import decisions  # noqa: E402  (the wave 2-3 review decisions; their holds bind here too)
from build_integration import append_rows, read  # noqa: E402

# the wave 2-3 build's gates, loaded under its own name (this file is also "build")
_spec = importlib.util.spec_from_file_location("w23_build", W23 / "build.py")
w23 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(w23)
MEDIA_PARTNERS, NOT_EVENT_LISTS, PERSONAL, USPS = w23.MEDIA_PARTNERS, w23.NOT_EVENT_LISTS, w23.PERSONAL, w23.USPS
edition, iso, org_index, state = w23.edition, w23.iso, w23.org_index, w23.state

BY = "claude-code show-harvest-rulings-2026-11-19"
ROLES = {"exhibitor", "sponsor", "speaker"}
ATTENDEE_LISTS = {  # source_url -> the one event it may mint for, and the note every row from it carries
    "https://b6e09292-fbc8-46fe-8a69-b4f2f89f8ed3.usrfiles.com/ugd/b6e092_53e0e8cd4fa74dc788418ca19fc3bd92.pdf": (
        "EVT-000035",
        "Attendee: the organizer's own company list for SAMPE 2026 (\"Industry leaders were here\"), printed in its "
        "sponsorship brochure; it counts as an attendee list under the owner ruling of 2026-11-18."),
}
# wave 1 (tasks/show-harvest-w1-2026-11-06): the AMI component expos share one gallery, recorded under the umbrella
UMBRELLA = {"EVT-000008": "EVT-000007", "EVT-000009": "EVT-000007", "EVT-000051": "EVT-000007",
            "EVT-000052": "EVT-000007"}
COMBINED = {("foam-expo-north-america", "speaker")}  # wave 1: the shared Foam Expo + A&B conference page
# Held by the controller (before review, and after its 2026-11-19 review), as the wave 2-3 review held "Trelleborg"
# and "ACS Group": the listed name does not pin one legal entity. Two kinds: (i) a bare group or brand name whose
# Atlas record is one national entity of a group that has others; (ii) a name several unrelated companies use.
# Keyed (event_id, name_key): binds every role, year and organization at the event.
CONTROLLER_HOLDS = {
    ("EVT-000035", A.name_key("Arkema")): "(i) the Atlas record is the US subsidiary Arkema Inc.",
    ("EVT-000035", A.name_key("Evonik")): "(i) the Atlas record is the US subsidiary Evonik Corporation",
    ("EVT-000035", A.name_key("Henkel")): "(i) the Atlas record is the US subsidiary Henkel Corporation",
    ("EVT-000035", A.name_key("United Initiators")): "(i) United Initiators GmbH and United Initiators Inc. both exist",
    ("EVT-000035", A.name_key("Microtex Composites")):
        "(i) Microtex Composites s.r.l. (Italy) and Microtex Composites Inc. both exist",
    ("EVT-000035", A.name_key("Hauschild SpeedMixer")): "(i) the Atlas record is the US arm of the German Hauschild group",
    ("EVT-000035", A.name_key("Sun Chemical")): "(i) the Atlas record is the US Sun Chemical Corporation of a global group",
    ("EVT-000035", A.name_key("Alpha Technologies")):
        "(ii) the list gives nothing that picks the Hudson OH instruments maker",
    ("EVT-000035", A.name_key("Advanced Composites")):
        "(ii) the Atlas record is a Sidney OH compounder; an unrelated Advanced Composites, Inc. in Salt Lake City "
        "works with SAMPE",
    ("EVT-000035", A.name_key("Specialty Materials")):
        "(ii) a generic name; the list gives nothing that picks the Lowell MA fiber maker",
}


class _Text(HTMLParser):
    """Page text; with alt=True, also the value of every real alt or title attribute (never src, href or data-*)."""

    def __init__(self, alt):
        super().__init__(convert_charrefs=True)
        self.alt, self.parts, self.skip = alt, [], 0

    def handle_starttag(self, tag, attrs):
        self.skip += tag in ("script", "style")
        if self.alt:
            self.parts += [f" {v} " for k, v in attrs if k in ("alt", "title") and v]
        self.parts.append(" ")

    def handle_endtag(self, tag):
        self.skip -= tag in ("script", "style") and self.skip > 0
        self.parts.append(" ")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def text(raw, alt):
    """Page text, lowercased: visible text, plus (alt=True) the values of real alt/title attributes."""
    p = _Text(alt)
    p.feed(raw)
    p.close()
    s = "".join(p.parts).replace("\u00a0", " ").replace("\u2019", "'")
    return re.sub(r"\s+", " ", s).lower()


def norm(name):
    return re.sub(r"\s+", " ", html.unescape(name).replace(" ", " ").replace("’", "'")).lower()


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
    drops = {(r["show_key"], r["role"], r["name_sha256_16"])
             for p in (W1, W23) for r in read(p / "controller_drops.csv")}
    by_key, orgs = org_index(data)
    # the wave 2-3 review holds, widened to bind their name at the event in every role (as CONTROLLER_HOLDS do)
    held = {(e, nk) for e, _role, nk in decisions.held_names(
        decisions.load(W23 / "review_decisions.csv", events, orgs, shows=set(shows)))} | set(CONTROLLER_HOLDS)
    part = read(data / "event_participation.csv")
    have = {(p["event_id"], p["org_id"], p["edition_year"], p["role"]) for p in part}
    nxt = max(int(p["participation_id"][4:]) for p in part) + 1

    rows, holds, skip = [], [], Counter()
    for f in sorted((hv / "out").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        key = d["show_key"]
        slug = key.split(":")[0]
        ev = UMBRELLA.get(emap.get(slug, ""), emap.get(slug, ""))
        if ev not in events:
            continue
        for L in d["lists"]:
            role, url = L["role"], L["source_url"]
            attendee = role == "attendee" and ATTENDEE_LISTS.get(url, ("",))[0] == ev
            if role not in ROLES and not attendee:
                continue
            if MEDIA_PARTNERS.search(url) or url in NOT_EVENT_LISTS or (slug, role) in COMBINED:
                continue
            one_show = len(set(L.get("shows_covered") or [])) <= 1 or slug == "fakuma"
            if L.get("covers_multiple_shows") and not one_show and ev != "EVT-000007" and \
                    not any(c.get("show_assignment") for c in L["companies"]):
                continue
            yr = str(L["list_edition_year"])
            ed = edition(a.conferences, slug, yr)
            city = shows[key]["city"]
            abroad = ed.get("country", "US") != "US" if ed else city.rsplit(", ", 1)[-1] not in USPS
            raw = (hv / L["raw_file"]).read_text(encoding="utf-8", errors="replace")
            visible, with_alt = text(raw, False), text(raw, True)
            for c in L["companies"]:
                name = c["name"].strip()
                n = norm(name)
                if attendee:
                    if n not in visible:
                        skip["attendee name not in the visible text"] += 1; continue
                elif n in visible or n not in with_alt:
                    continue  # earlier passes judged visible names; a name in neither is rebuilt, never admitted
                if (key, role, hashlib.sha256(name.encode("utf-8")).hexdigest()[:16]) in drops:
                    skip["controller drop"] += 1; continue
                if c.get("show_assignment") and A.name_key(c["show_assignment"]) != A.name_key(events[ev]["name"]):
                    skip["labelled for a co-located show"] += 1; continue
                nk = A.name_key(name)
                if (ev, nk) in held:
                    skip["held (wave 2-3 review or CONTROLLER_HOLDS)"] += 1; continue
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
                pre = " Pre-show list, still filling as of the evidence date." \
                    if str(ed.get("start", "")) > d["retrieved"] else ""
                staged = f" The staging key's year ({key.split(':')[1]}) is the harvest's edition label; the row " \
                    f"year follows the year printed in the source." if key.split(":")[1] != yr else ""
                how = ATTENDEE_LISTS[url][1] if attendee else ("Listed by the organizer as a logo's alt text (counts as "
                                                            "on the page under the owner ruling of 2026-11-18).")
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
                             f"in staging (harvest-2026-11, {key}). {how}" + staged + pre
                             + (" Co-located AMI expos share one list; recorded under the umbrella event."
                                if ev == "EVT-000007" else "")})
                nxt += 1

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
