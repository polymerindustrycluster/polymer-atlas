"""`ohio_statewide` -> `ohio_other` for an Ohio HQ county outside PIC-18 (owner ruling 2026-11-22, round 13: "PIC-18 exactly" with the
follow-up that the rows still carrying the undefined value `ohio_statewide` and a named Ohio county outside PIC-18 get `ohio_other`).
One rule, used by build.py and check.py. Reuses ../region-labels-2026-11-22/rules.py's county list (the repo's county shapes) and PIC-18 (scripts/regions.py).
    hq_state OH, hq_county a valid Ohio county not in PIC-18, hq_in_scope = ohio_statewide  -> ohio_other
    no county / not an Ohio county / county in PIC-18 / a same-city Ohio site sits in another county   -> hold (listed)"""
import region_rules as R


def classify(org, same_city_site_counties):
    """(after or '', category)."""
    if org["hq_in_scope"].strip() != "ohio_statewide":
        return "", "not_ohio_statewide"
    s, c = org["hq_state"].strip(), org["hq_county"].strip()
    if s != "OH":
        return "", "hold_state_not_ohio"
    if not c:
        return "", "hold_county_blank"
    if c not in R.COUNTIES["OH"]:
        return "", "hold_county_not_an_ohio_county"
    if c in R.PIC18:
        return "", "hold_pic18_county_should_be_ne_ohio"
    if same_city_site_counties and c not in same_city_site_counties:
        return "", "hold_county_vs_site_county"
    return "ohio_other", "relabel_ohio_statewide"
