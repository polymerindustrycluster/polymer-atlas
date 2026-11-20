#!/usr/bin/env python3
"""Participation rows from organizer lists a Muse research pass found (2026-11-19), banked and read by the controller.

Muse's lists are leads only. The controller banked every source (staging muse-leads-2026-11-19: raw/, manifest.json),
extracted each list (lists/*.json) and compared it, by exact name, with Muse's own transcription. This build re-reads
the banked source for every name and applies the gates of #411 (tasks/show-harvest-newseries-2026-11-19/build.py),
which it imports:
- the name is in the source's text (PDF text layer, or a page's visible text and real alt/title attributes);
- a legal-name match to exactly one active/unknown organization; trade-name hits are held (trade_name_holds.csv);
- not held by the wave 2-3 review; rule (i)/(ii) holds of #404, #411, #414 and this pass (HOLDS) bind at their event;
- an edition abroad mints only when the list prints the company's country and it equals the organization's HQ
  country; an international series is always abroad (as #411);
- no (event, org, year, role) the table already holds.
Owner ruling 2026-11-20 (tasks/owner-rulings-2026-11-20/): a rule (i) hold binds a bare group name only. A listing
whose printed name equals the held organization's legal name, legal suffix included ("BASF Corporation"), names the US
entity itself and is not bound. Under it, three names on the Coatings Trends 2026 registration list that #414 held
are admitted here.
    python3 tasks/show-harvest-muse-leads-2026-11-20/build.py --data-dir data --staging <muse-leads staging>
        --harvest <harvest-2026-11 staging> --conferences ../conferences [--apply --i-am-the-integrator]
"""
import argparse, csv, html, importlib.util, json, re, subprocess, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASKS = HERE.parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


N = _load("newseries_build", TASKS / "show-harvest-newseries-2026-11-19" / "build.py")  # #411: gates and helpers
R = _load("rulings_build", TASKS / "show-harvest-rulings-2026-11-19" / "build.py")  # #404: SAMPE holds
D = _load("ctt_reg_build", TASKS / "owner-rulings-2026-11-19d" / "build.py")  # #414: the registration list
A = N.A
BY = "claude-code show-harvest-muse-leads-2026-11-20"
RULING = " A rule (i) hold binds a bare group name only; this listing names the US entity itself (owner ruling 2026-11-20)."

# file in lists/ -> (event, edition year, role, the list's own as-of date or None, note every row carries).
# Expected counts are the controller's independent count of the source, which equals Muse's transcription.
LISTS = {
    "ampp_2025_exhibitor": ("EVT-000072", "2025", "exhibitor", "2025-03-20", 367,
                            "The organizer's on-site guide prints this exhibitor list \"as of March 20, 2025\"."),
    "ampp_2025_sponsor": ("EVT-000072", "2025", "sponsor", "2025-03-20", 36,
                          "Sponsor: the on-site guide's exhibitor list flags the company \"S Event Sponsor\" (as of "
                          "March 20, 2025)."),
    "ampp_2026_exhibitor": ("EVT-000072", "2026", "exhibitor", "2025-09-15", 291,
                            "The organizer's advance program prints this exhibitor list \"as of September 15, 2025\"."),
    "ampp_2026_sponsor": ("EVT-000072", "2026", "sponsor", "2025-09-15", 20,
                          "Sponsor: the advance program's exhibitor list flags the company \"S Event Sponsor\" (as of "
                          "September 15, 2025)."),
    "ecs_2025_exhibitor": ("EVT-000080", "2025", "exhibitor", None, 1213,
                           "The organizer's \"List of Exhibitors\" for 2025 is headed \"As of March 2025\", the month of "
                           "the edition."),
    "carbonfiber_2026_speaker": ("EVT-000074", "2026", "speaker", None, 37,
                                 "Speaker: the employer printed in the organizer's \"Carbon Fiber 2026 Agenda\"."),
    "ctt_2026_speaker": ("EVT-000077", "2026", "speaker", None, 58,
                         "Speaker: the employer printed beside the speaker in the organizer's 2026 agenda."),
    "ctt_2026_sponsor": ("EVT-000077", "2026", "sponsor", "2026-08-17", 19,
                         "Sponsor: the organizer's blog post of 2026-08-17, \"We are grateful to our 2026 sponsors:\"."),
    "radtech_2025_exhibitor": ("EVT-000092", "2025", "exhibitor", None, 56,
                               "The organizer's list page is titled \"RadTech 2025 :: Exhibitor List\"."),
    "meximold_2026_exhibitor_us": ("EVT-000085", "2026", "exhibitor", None, 3,
                                   "The organizer's directory (Meximold 2026) prints the country on the exhibitor's "
                                   "page."),
    "meximold_2027_exhibitor_us": ("EVT-000085", "2027", "exhibitor", "2026-11-19", 3,
                                   "The organizer's directory (Meximold 2027) prints the country on the exhibitor's "
                                   "page; the directory was still filling when read."),
    "expoplast_2026_exhibitor_us": ("EVT-000081", "2026", "exhibitor", None, 2,
                                    "The ADM Montréal 2026 directory places the exhibitor in \"ADM Plastiques 2026\", "
                                    "which continues EXPOPLAST (owner ruling 2026-11-19d item 3; the organizer's release "
                                    "of 15 September 2026)."),
}
US_ARM = N.US_ARM
HOLDS = {  # this pass's rule (i)/(ii) holds, keyed (event, name_key) as #411's, from the bare-name screen (README)
    ("EVT-000077", A.name_key("Evonik")): US_ARM + " (Evonik Corporation; the dated sponsor list prints the bare name)",
}


LEGAL_WORDS = {"inc", "incorporated", "llc", "lp", "ltd", "limited", "corp", "corporation", "co", "company", "gmbh",
               "ag", "sa", "plc", "bv"}


def canon(s):
    return re.sub(r"[^a-z0-9]+", " ", html.unescape(s).lower()).strip()


def names_us_entity(listed, legal):
    """The listing prints the organization's full legal name, a legal-form word included ("BASF Corporation"), not
    just the bare group name. An abbreviated suffix ("Corp." for "Corporation") does not count: the reading is strict."""
    return canon(listed) == canon(legal) and bool(set(canon(listed).split()) & LEGAL_WORDS)


EDITION_NAME = {"expoplast_2026_exhibitor_us": "ADM Plastiques 2026"}  # SCHEMA 4.12.2: the name the edition ran under


def rule_i_holds():
    """Every rule (i)/(ii) hold of #404, #411, #414 and this pass, with whether it is a bare-name (rule (i)) hold."""
    out = {}
    for h in (R.CONTROLLER_HOLDS, N.CONTROLLER_HOLDS, D.HOLDS, HOLDS):
        for k, why in h.items():
            out[k] = why.startswith("(i)") or why.startswith(US_ARM)
    return out


def raw_text(st, f):
    """A banked file's text: the PDF text layer (-raw keeps each list line whole), or a page's visible text plus real
    alt/title attributes, normalized like #411's page check."""
    p = st / "raw" / f
    if p.suffix == ".pdf":
        return subprocess.run(["pdftotext", "-enc", "UTF-8", "-raw", str(p), "-"], capture_output=True, text=True,
                              encoding="utf-8", check=True).stdout
    return N.text(p.read_text(encoding="utf-8", errors="replace"), True)


def flagged(pdf_text, name, booth):
    """The AMPP lists print a sponsor's flags before its name on the name's own line: "C S Sherwin-Williams.....1545".
    A long name may wrap onto the next line ("C S Advance Products and" / "Systems.....1726"), and a name's own final
    period runs into the dot leader ("S EIU Inc. .....619", extracted as "EIU Inc")."""
    words = r"\s+".join(re.escape(w) for w in name.split())
    pat = re.compile(r"^(?:C )?S " + words + r"\.?\s*\.{2,}\s*" + re.escape(booth) + r"\b", re.M)
    return bool(pat.search(pdf_text))


# The ADM Montréal release of 15 September 2026 (owner ruling 2026-11-19d item 3), in #411's normalized page text.
RELEASE = ("admmontreal-2026-release-globenewswire.html",
           "co-locate of legacy brands atx, d&m, expoplast, pbs, and packex, is now streamlined as solely adm montréal")


def main():
    ap = argparse.ArgumentParser()
    for a_ in ("--data-dir", "--staging", "--harvest", "--conferences"):
        ap.add_argument(a_, required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    a = ap.parse_args()
    data, st = Path(a.data_dir).resolve(), Path(a.staging).resolve()
    events = {e["event_id"]: e for e in N.read(data / "events.csv")}
    by_key, orgs = N.org_index(data)
    held = {(e, nk) for e, _role, nk in N.decisions.held_names(
        N.decisions.load(N.W23 / "review_decisions.csv", events, orgs))}
    holds = rule_i_holds()
    part = N.read(data / "event_participation.csv")
    have = {(p["event_id"], p["org_id"], p["edition_year"], p["role"]) for p in part}
    nxt = max(int(p["participation_id"][4:]) for p in part) + 1
    manifest = json.loads((st / "manifest.json").read_text(encoding="utf-8"))

    rows, tholds, screen, skip, hit, held_rows, per = [], [], [], Counter(), set(), [], Counter()

    def mint(ev, yr, role, org, listed, url, retrieved, detail, notes, as_of=None, edition_name=""):
        """evidence_date is the list's own as-of date where printed, else the retrieval date (SCHEMA 4.12.2)."""
        nonlocal nxt
        ed = N.edition(a.conferences, events[ev]["pic_events_slug"].split(";")[0].strip(), yr)
        abroad = events[ev]["home_region"] == "international" or (ed.get("country") or "US") != "US"
        if abroad and (ed.get("country") or "US") == "US":
            ed = {k: v for k, v in ed.items() if k in ("start", "end", "city")}
        rows.append({
            "participation_id": f"EVP-{nxt:06d}", "event_id": ev, "org_id": org, "edition_year": yr,
            "edition_name": edition_name, "role": role, "role_detail": detail,
            "edition_dates": f"{ed['start']} to {ed['end']}" if ed.get("start") and ed.get("end") else "",
            "edition_city": ed.get("city", ""), "edition_state": N.state(ed),
            "evidence_source_name": f"{events[ev]['name']} {yr} {role} list (organizer-published)",
            "evidence_source_url": url, "evidence_date": as_of or retrieved,
            "sources": f"{url} (read {retrieved}; listed as \"{listed}\")",
            "verification_tier": "A", "last_verified": retrieved, "created_by": BY, "notes": notes})
        nxt += 1
        return abroad, ed

    for lf, (ev, yr, role, as_of, expect, note) in LISTS.items():
        L = json.loads((st / "lists" / f"{lf}.json").read_text(encoding="utf-8"))
        # A full list's entry count is the controller's own count of its source, equal to Muse's transcription. A *_us
        # list is only the US-printed exhibitors that match Atlas names (Muse leads); its count is that subset's size,
        # and its entries_on_page is the whole directory's, as read. Each _us entry is checked on its own page below.
        assert len(L["entries"]) == expect and (lf.endswith("_us") or L["entries_on_page"] == expect), f"{lf}: yield"
        texts = {}
        if lf.startswith("expoplast"):
            assert RELEASE[1] in N.norm(raw_text(st, RELEASE[0])), "the release no longer folds EXPOPLAST in"
        ed = N.edition(a.conferences, events[ev]["pic_events_slug"].split(";")[0].strip(), yr)
        abroad = events[ev]["home_region"] == "international" or (ed.get("country") or "US") != "US"
        for c in L["entries"]:
            listed = c["name"].strip()
            f = c.get("detail_file") or L["source_file"]  # a _us entry is read on its own exhibitor page
            raw = texts.setdefault(f, raw_text(st, f))
            page = N.norm(raw)
            if N.norm(listed) not in page:
                skip[f"{lf}: name not in the banked source"] += 1; continue
            if c.get("detail_file"):  # the exhibitor's own page prints the country (and, at ADM Montréal, the pavilion)
                assert N.norm(c["country"]) in page, f"{lf}: {listed}: country not on its page"
                assert not lf.startswith("expoplast") or "adm plastiques 2026" in page, f"{listed}: pavilion not on page"
            if lf.startswith("ampp") and role == "sponsor":
                assert flagged(raw, listed, c["booth"]), f"{lf}: no 'S' flag line for {listed}"
            nk = A.name_key(listed)
            if (ev, nk) in held:
                skip["held by the wave 2-3 review"] += 1; continue
            hits = by_key.get(nk, {})
            if len(hits) != 1:
                skip["no Atlas organization" if not hits else "ambiguous name key"] += 1; continue
            org, kind = next(iter(hits.items()))
            if (ev, nk) in holds:
                hit.add((ev, nk))
                if not (holds[(ev, nk)] and names_us_entity(listed, orgs[org]["legal_name"])):
                    held_rows.append({"list": lf, "event_id": ev, "listed_name": listed, "org_id": org,
                                      "legal_name": orgs[org]["legal_name"]})
                    skip["held (rule (i) bare name or rule (ii))"] += 1; per[(lf, "held")] += 1; continue
            if abroad and (not N.iso(c.get("country")) or N.iso(c["country"]) != N.iso(orgs[org]["hq_country"])):
                skip["edition abroad, listed country missing or not the org's HQ country"] += 1
                per[(lf, "abroad, country not the HQ country")] += 1; continue
            if kind == "trade":
                tholds.append({"list": lf, "event_id": ev, "edition_year": yr, "role": role, "listed_name": listed,
                               "org_id": org, "legal_name": orgs[org]["legal_name"],
                               "trade_names": orgs[org].get("trade_names", ""), "source_url": L["source_url"]})
                skip["trade-name hit, held"] += 1; per[(lf, "trade-name hit")] += 1; continue
            if (ev, org, yr, role) in have:
                skip["already a row"] += 1; per[(lf, "already a row")] += 1; continue
            per[(lf, "row")] += 1
            have.add((ev, org, yr, role))
            url = c.get("detail_url") or L["source_url"]
            src = c.get("detail_file") or L["source_file"]
            retrieved = manifest[src]["retrieved"]
            start = str(ed.get("start") or "")
            pre = " Pre-show list: the organizer's list predates the edition." if as_of and start and as_of < start else ""
            if as_of and not start:
                pre = " The edition's dates are not on record, so whether the list predates the show is not known."
            notes = (f"{role.capitalize()} name matched to the org by exact normalized legal name; source banked in "
                     f"staging (muse-leads-2026-11-19, {lf}). {note}{pre}"
                     + (RULING if (ev, nk) in holds else "")
                     + (f" Edition abroad: the list gives the company's country ({c['country']}), which matches the "
                        f"organization's HQ country." if abroad else ""))
            detail = (c.get("booth") if role == "exhibitor" else c.get("sponsor_level") or "") or ""
            mint(ev, yr, role, org, listed, url, retrieved, detail.strip(), notes, as_of, EDITION_NAME.get(lf, ""))
            o = orgs[org]
            if not set(canon(listed).split()) & LEGAL_WORDS:  # no legal-form word printed: read by the controller (README)
                screen.append({"participation_id": rows[-1]["participation_id"], "event_id": ev, "role": role,
                               "listed_name": listed, "org_id": org, "legal_name": o["legal_name"],
                               "hq_country": o["hq_country"], "ultimate_parent_name": o.get("ultimate_parent_name", "")})

    # Owner ruling 2026-11-20 applied to #414's list: names held under any rule (i) hold at EVT-000077 (#411's, #414's
    # or this pass's) that print the US entity itself. #414's other gates already passed every other name on this list.
    d = json.loads((Path(a.harvest).resolve() / "out" / "coatings-trends-and-technologies-summit_2027.json").read_text(
        encoding="utf-8"))
    (L,) = [x for x in d["lists"] if x["source_url"] == D.URL]
    reg_raw = (Path(a.harvest).resolve() / L["raw_file"]).read_text(encoding="utf-8", errors="replace")
    assert D.HEADING in reg_raw, "the banked registration page no longer carries its 'final list' heading"
    reg_entries = set(D.page_entries(reg_raw))  # #414's parse of the page: one entry per printed line
    for c in L["companies"]:
        listed = c["name"].strip()
        nk = A.name_key(listed)
        if (D.EVENT, nk) not in holds or (D.EVENT, nk) in held:
            continue
        assert " ".join(listed.split()) in reg_entries, f"{listed}: not a whole entry on the banked registration page"
        hits = by_key.get(nk, {})
        org, kind = next(iter(hits.items())) if len(hits) == 1 else (None, None)
        if not (org and kind == "legal" and holds[(D.EVENT, nk)] and names_us_entity(listed, orgs[org]["legal_name"])):
            skip["registration list: still held (bare name)"] += 1; continue
        if (D.EVENT, org, D.YEAR, "attendee") in have:
            skip["already a row"] += 1; continue
        have.add((D.EVENT, org, D.YEAR, "attendee"))
        mint(D.EVENT, D.YEAR, "attendee", org, listed, D.URL, d["retrieved"], "",
             f"Attendee name matched to the org by exact normalized legal name; list banked in staging (harvest-2026-11, "
             f"{D.SHOW_KEY}). {D.NOTE}{RULING}")

    unused = set(HOLDS) - hit
    assert not unused, f"HOLDS that matched no listing: {sorted(unused)}"
    fields = list(part[0].keys())
    for fname, rs, cols in (("participation_append.csv", rows, fields),
                            ("trade_name_holds.csv", tholds, list(tholds[0]) if tholds else ["listed_name"]),
                            ("screen_bare_names.csv", screen, list(screen[0]) if screen else ["listed_name"]),
                            ("held_listings.csv", held_rows, list(held_rows[0]) if held_rows else ["listed_name"])):
        with open(HERE / fname, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
            w.writeheader(); w.writerows(rs)
    print(f"rows {len(rows)}; trade-name holds {len(tholds)}; bare-name screen {len(screen)}")
    print("rows by event/role/year", sorted(Counter((r["event_id"], r["role"], r["edition_year"]) for r in rows).items()))
    print("skipped", dict(skip))
    print("per list (Atlas matches only)", sorted(per.items()))
    if a.apply:
        if data == (HERE.parents[1] / "data").resolve() and not a.i_am_the_integrator:
            sys.exit("appending to the real data/ is integrator work; pass --i-am-the-integrator")
        N.append_rows(data / "event_participation.csv", rows)
        print("applied")


if __name__ == "__main__":
    main()
