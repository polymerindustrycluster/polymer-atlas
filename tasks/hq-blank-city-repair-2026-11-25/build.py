#!/usr/bin/env python3
"""Apply the repair to an unedited checkout of main (run once): clear ORG-000197's HQ cells and move it back to the residual shard.

Rule applied is the one of PR #563 for the seven organizations whose HQ no source states: no HQ cells, no county.
Reads and writes data/ in the working tree; adds no evidence row.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KENDA, EVD = "ORG-000197", ("EVD-421274", "EVD-483143")
CLEAR = ("hq_city", "hq_state", "hq_country", "hq_in_scope", "hq_county")
NOTE = (" | 2026-11-25: HQ not established (census audit of #563, FAIL): the company's locations page lists this centre under "
        "Offices and never calls it the headquarters, and SITE-000988 (Reynoldsburg) is noted as a distribution/HQ establishment, "
        "so hq_city, hq_state, hq_country, hq_in_scope and hq_county are blank, as for the seven other organizations whose HQ no "
        "source states. The physical location of this unit (Green, Summit County) stays on SITE-000204 and in the county note "
        "above; it is not an HQ statement. Settles it: a page or filing that names the headquarters of this organization.")


def load(name):
    with (ROOT / "data" / f"{name}.csv").open(newline="") as f:
        return list(csv.reader(f))


def save(name, rows):
    with (ROOT / "data" / f"{name}.csv").open("w", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows(rows)


oh = load("organizations_OH")
key = {c: i for i, c in enumerate(oh[0])}
row = next(r for r in oh[1:] if r[0] == KENDA)
for c in CLEAR:
    assert row[key[c]], c
    row[key[c]] = ""
row[key["notes"]] += NOTE
save("organizations_OH", [r for r in oh if r is not row])
us = load("organizations_US")
assert us[0] == oh[0]
at = next(i for i, r in enumerate(us[1:], 1) if r[0] > KENDA)  # the shard is sorted by org_id
save("organizations_US", us[:at] + [row] + us[at:])

eoh, eus = load("evidence_organizations_OH"), load("evidence_organizations_US")
moved = [r for r in eoh[1:] if r[2] == KENDA]
assert tuple(r[0] for r in moved) == EVD and eoh[0] == eus[0]
save("evidence_organizations_OH", [r for r in eoh if r not in moved])
save("evidence_organizations_US", eus + moved)
