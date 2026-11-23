"""hq_in_scope recomputed from the HQ state and county. One rule, used by build.py and check.py.

Definition (AGENTS.md section 8, owner ruling 2026-11-03): the cluster reporting region is PIC-18, read from
scripts/regions.py. SCHEMA section 4.4 (v1.19.2) reads `ne_ohio` as "HQ county is in PIC-18"; the earlier 20-county list there was
superseded by that ruling. Only a row whose hq_state is OH is recomputed:
    county in PIC-18                       -> ne_ohio
    other valid Ohio county                -> ohio_other
A relabel is proposed only where the stored label disagrees with that, the label is one of the three
labels that contradict an HQ in a PIC-18 county (pic12 = the retired 12-county region, ohio_other, ohio_statewide), and the county
is not itself in doubt (an Ohio site in the same city sits in a different county, or the county is not a county of Ohio).
Everything else that disagrees is a hold, with its class."""
import json
from regions import REGION as PIC18   # the one region definition (PIC-18); another region is a one-line change here

_g = json.load(open(__import__("pathlib").Path(__file__).resolve().parents[2] / "scripts/assets/us-atlas/counties-albers-10m.json"))
FIPS_ST = {"01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE", "11": "DC", "12": "FL",
           "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME",
           "24": "MD", "25": "MA", "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
           "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
           "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI", "56": "WY"}
COUNTIES = {}
for _x in _g["objects"]["counties"]["geometries"]:
    COUNTIES.setdefault(FIPS_ST.get(_x["id"][:2]), set()).add(_x["properties"]["name"])
RELABEL = {"pic12", "ohio_other", "ohio_statewide"}      # labels that contradict a PIC-18 county HQ


def expected(state, county):
    """ne_ohio | ohio_other for an Ohio HQ with a valid county; '' when not recomputable."""
    if state != "OH" or county not in COUNTIES["OH"]:
        return ""
    return "ne_ohio" if county in PIC18 else "ohio_other"


def classify(org, same_city_site_counties):
    """(after or '', category). category 'relabel_*' carries a proposed value; every other category is a hold or a pass."""
    s, c, lab = org["hq_state"].strip(), org["hq_county"].strip(), org["hq_in_scope"].strip()
    if not s:
        return "", "hold_state_blank" if lab or c else "skip_no_state"
    if s != "OH":
        if lab in ("ne_ohio", "ohio_other", "ohio_statewide", "pic12"):
            return "", "record_error_ohio_label_on_non_ohio_state"
        if c and c in PIC18 and c not in COUNTIES.get(s, set()):
            return "", "record_error_county_not_in_state"
        return "", "skip_non_ohio"
    if not c:
        return "", "hold_county_blank"
    if c not in COUNTIES["OH"]:
        return "", "record_error_county_not_in_ohio"
    want = expected(s, c)
    if lab == want:
        return "", "agree"
    if same_city_site_counties and c not in same_city_site_counties:
        return "", "record_error_county_vs_site_county"
    if lab == "":
        return "", "hold_label_blank"
    if want == "ne_ohio" and lab in RELABEL:
        return want, "relabel_" + lab
    if want == "ne_ohio" and lab in ("national_us", "international"):
        return "", "hold_label_outside_ohio_but_ohio_pic18_county"
    if want == "ohio_other" and lab == "ohio_statewide":
        return "", "hold_ohio_statewide_undefined"
    return "", f"hold_other_{lab}_vs_{want}"
