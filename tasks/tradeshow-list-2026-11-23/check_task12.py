#!/usr/bin/env python3
"""Compare the public event captions with PIC-18 participation in a matching Atlas DB.

Run from this repo with uv run --with playwright python -I <script> BASE_URL DB.
BASE_URL is the site root (e.g. https://polymerindustrycluster.github.io/polymer-atlas/).
Install Chromium with uv run --with playwright playwright install chromium if needed.
"""
import argparse
import re
import sqlite3
import sys
from collections import Counter
from contextlib import closing
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from regions import PIC18


def sql_participants(db):
    counties = ",".join("?" for _ in PIC18)
    with closing(sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)) as con:
        names = dict(con.execute("SELECT event_id, name FROM events"))
        expected = {event_id: {} for event_id in names}
        for event_id, org_id, name in con.execute(f"""
            WITH footprint AS (
                SELECT org_id FROM organizations WHERE hq_state = 'OH' AND hq_county IN ({counties})
                UNION
                SELECT org_id FROM sites WHERE state = 'OH' AND county IN ({counties})
                    AND operating_status IS NOT 'closed'
                UNION
                SELECT org_id FROM ecosystem WHERE state = 'OH' AND county IN ({counties})
            )
            SELECT DISTINCT p.event_id, p.org_id, COALESCE(o.legal_name, e.legal_name)
            FROM event_participation p
            JOIN footprint f ON f.org_id = p.org_id
            LEFT JOIN organizations o ON o.org_id = p.org_id
            LEFT JOIN ecosystem e ON e.org_id = p.org_id
        """, PIC18 * 3):
            expected[event_id][org_id] = " ".join(name.split())
    return names, expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url")
    parser.add_argument("db", type=Path)
    args = parser.parse_args()
    names, expected = sql_participants(args.db)
    title_counts = Counter(names.values())
    event_ids = {name: event_id for event_id, name in names.items() if title_counts[name] == 1}
    required = {event_id for event_id, orgs in expected.items() if orgs}
    if not required:
        sys.exit("FAIL task 12: DB has no event series with PIC-18 participants")

    errors = []
    visited = set()
    reached = 0
    with sync_playwright() as pw:
        with pw.chromium.launch(args=["--enable-unsafe-swiftshader"]) as browser:
            page = browser.new_page(reduced_motion="reduce", viewport={"width": 1280, "height": 860})
            page.set_default_timeout(5000)
            response = page.goto(args.base_url.rstrip("/") + "/graph/events.html", wait_until="domcontentloaded")
            if response is None or not response.ok:
                sys.exit(f"FAIL task 12: events page HTTP status {response.status if response else 'unavailable'}")
            caption = page.locator("#caption")
            step = caption.locator(".step")
            next_show = page.get_by_role("button", name="Next show")
            next_show.click()
            expect(step).to_have_text(re.compile(r"^Show 1 of [1-9]\d*\b"))
            total = int(re.search(r"^Show 1 of (\d+)", step.inner_text())[1])
            for number in range(1, total + 1):
                expect(step).to_have_text(re.compile(rf"^Show {number} of {total}\b"))
                title = caption.get_by_role("heading", level=2).inner_text()
                event_id = caption.get_attribute("data-event-id") or event_ids.get(title)
                if names.get(event_id) != title or event_id in visited:
                    errors.append(f"show {number}: unknown, mislabelled or repeated event")
                else:
                    visited.add(event_id)
                    orgs = expected[event_id]
                    name_counts = Counter(orgs.values())
                    legacy_ids = {name: org_id for org_id, name in orgs.items() if name_counts[name] == 1}
                    shown = Counter()
                    chips = caption.locator(".chips .chip:visible")
                    for chip in chips.all():
                        name = " ".join(chip.inner_text().split())
                        if re.fullmatch(r"\+\d+ more", name):
                            continue
                        org_id = chip.get_attribute("data-org-id") or legacy_ids.get(name)
                        shown[org_id, name] += 1
                    roster = caption.get_by_role("region", name="PIC-18 participants")
                    if chips.count() and roster.count():
                        roster.focus()
                        roster.press("End")
                        expect(chips.last).to_be_in_viewport()
                    wanted = Counter(orgs.items())
                    reached += sum((shown & wanted).values())
                    count = caption.locator(".nums > div:visible").filter(
                        has_text="in the PIC-18 counties").locator("b").inner_text()
                    if shown != wanted or count != str(len(orgs)):
                        errors.append(f"{event_id}: states {count}, SQL {len(orgs)}, "
                                      f"missing {sum((wanted - shown).values())}, "
                                      f"extra or repeated {sum((shown - wanted).values())}")
                next_show.click()
            expect(step).to_have_text(re.compile(rf"^Show 1 of {total}\b"))

    if missing_events := required - visited:
        errors.append("unreachable event series with PIC-18 participants: " + ", ".join(sorted(missing_events)))
    for error in errors:
        print(error)
    print(f"{'FAIL' if errors else 'PASS'} task 12: checked {len(visited)} event series, "
          f"reached {reached}/{sum(map(len, expected.values()))} PIC-18 organization–event pairs, "
          f"{len(errors)} discrepancies")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
