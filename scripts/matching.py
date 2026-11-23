"""One street test for the whole repo (is this printed street the record's street?), and the one name extension the
owner allows on top of it (corporate_form_extension).

Moved here from scripts/derive_last_activity.py (PR #463, owner ruling 2026-11-22 "Fix script, re-derive") so that the
derivation and the evidence binding gate (scripts/check_evidence_binding.py) share one definition (controller ruling
2026-11-22, Codex review of PR #467). Do not keep a second copy anywhere.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atlas import squash, street_key  # noqa: E402  (stdlib-only module, no import side effects)
from build_echo_spine import STATE_NAMES  # noqa: E402  (stdlib-only; the repo's one state-name table)

_UNIT = re.compile(r"\b(?:suite|ste|unit|apt|apartment|room|rm)\b\.?\s*#?\s*([a-z0-9-]+)|(?<=\S)\s*#\s*([a-z0-9-]+)", re.I)
_NUMBER_WORDS = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"}


def units(street: str) -> set:
    """Suite / unit designators a street string states (`Suite 100`, `Ste. 5`, `Unit B`, `Apt 2`, `Rm 7`, a non-leading `#12`)."""
    return {re.sub(r"[^a-z0-9]", "", (g1 or g2).lower()) for g1, g2 in _UNIT.findall(street or "")} - {""}


def has_civic_number(key: str) -> bool:
    """A civic number in a street key: a token containing a digit, or a leading number word (one to ten); not a PO box in any spelling (PO Box, P.O. Box, P O Box, POB, P.O.B., Post Office Box)."""
    toks = key.split()
    if re.search(r"\b(?:p ?o ?b(?:ox)?|post ?office ?box)(?=[\s\d]|$)", key):
        return False                                                    # a PO box is not a civic address
    return any(re.search(r"\d", t) for t in toks) or bool(toks) and toks[0] in _NUMBER_WORDS


def same_street(site_street: str, printed: str) -> bool:
    """The extract's street is the site's street: both `atlas.street_key` values are equal, non-empty, and carry a civic
    number plus at least one more token (a bare number cannot witness a street). `street_key` discards suites, so when
    the record and the extract both state a suite or unit and they differ, the row is not applied. A blank street is
    never equal. No second normaliser lives here: variants the key misses are rejected, not guessed."""
    key = street_key(site_street)
    if not key or key != street_key(printed) or not has_civic_number(key) or len(key.split()) < 2:
        return False
    return not designators_conflict(site_street, printed)


_BUILDING = re.compile(r"\b(?:bldg|building)\b\.?\s*#?\s*([a-z]?\d+[a-z]?|[a-z])\b", re.I)
# A comma part that is only a designator ("Ste. 300", "Bldg B", "#12"): street-line parsers keep it with the street.
DESIGNATOR_ONLY_RE = re.compile(r"^\s*(?:(?:suite|ste|unit|apt|apartment|bldg|building|floor|fl|room|rm|dept|department)"
                                r"\b\.?|#)\s*#?\s*[\w-]*\s*$", re.I)


def buildings(street: str) -> set:
    """Building designators a street string states (`Building A`, `Bldg. 2`, `Bldg #3`)."""
    return {g.lower() for g in _BUILDING.findall(street or "")}


def designators_conflict(a: str, b: str) -> bool:
    """Both strings state a suite/unit, or both state a building, and the two differ (owner split of PR #467,
    Codex r2 finding 2: "Building A" vs "Building B" is a different place). One-sided designators never conflict."""
    return any(x and y and x != y for x, y in ((units(a), units(b)), (buildings(a), buildings(b))))


# Owner ruling 2026-11-22 (multiple choice, DECISIONS.md): on a structured row whose street already passes
# same_street(), a filing or permit name also binds when a held name is a leading run of it and every extra token is a
# corporate-form word from this fixed list. Not for web rows, organization rows without a street test, or predecessor,
# parent or notes-only names.
CORPORATE_FORM_WORDS = ("Inc", "Incorporated", "LLC", "L.L.C.", "Corp", "Corporation", "Co", "Company", "Ltd",
                        "Limited", "LP", "LLP", "Holdings", "Holding", "Group", "US", "USA", "U.S.", "North America",
                        "Americas")
_FORMS = sorted({tuple(squash(w).split()) for w in CORPORATE_FORM_WORDS}, key=len, reverse=True)


def corporate_form_extension(held_key: str, quoted_key: str) -> bool:
    """Is quoted_key a held name followed only by corporate-form words? Both are atlas.name_key values."""
    h, q = held_key.split(), quoted_key.split()
    if not h or len(q) <= len(h) or q[:len(h)] != h:
        return False
    rest = q[len(h):]
    while rest:
        form = next((f for f in _FORMS if tuple(rest[:len(f)]) == f), None)
        if form is None:
            return False
        rest = rest[len(form):]
    return True


# Owner ruling 2026-11-22 (multiple choice, DECISIONS.md), "drop generic labels only": a site-name part is ignored as a
# held name only when every token in it is a generic label from this one fixed list, or the site's own city or county.
# Any other part (a brand, a division, a trading name) is a held name.
GENERIC_LABELS = {
    "facility": ("plant", "facility", "warehouse", "works", "site", "office", "hq", "headquarters", "building", "unit",
                 "main"),  # "main": added by the owner, 2026-11-22
    "number": ("no", "number", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "first",
               "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"),  # and 2, #2, 2nd; never "3m"
    "compass": ("north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest", "n", "s", "e", "w",
                "ne", "nw", "se", "sw"),
    "us_state": tuple(sorted(squash(n) for n, c in STATE_NAMES.items() if c not in ("PR", "VI"))
                      + sorted(c.lower() for c in STATE_NAMES.values() if c not in ("PR", "VI"))),
}
_LABEL_WORDS = {w for c in ("facility", "number", "compass") for w in GENERIC_LABELS[c]}
_STATE_PHRASES = set(GENERIC_LABELS["us_state"])


def generic_label(key: str, city: str = "", county: str = "") -> bool:
    """Is every token of a site-name part (an atlas.name_key) a generic label: a facility word, a number or ordinal, a
    compass word, a US state, or the site's own city or county ("Plant 2", "North Warehouse", "Ohio", "Akron")?"""
    places = {squash(city), squash(county), squash(county) + " county" if squash(county) else ""} - {""}
    rest = f" {key} "
    for phrase in sorted(_STATE_PHRASES | places, key=len, reverse=True):
        while f" {phrase} " in rest:
            rest = rest.replace(f" {phrase} ", " ")
    return bool(key.split()) and all(t in _LABEL_WORDS or re.fullmatch(r"#?\d+|\d+(?:st|nd|rd|th)", t)
                                     for t in rest.split())



# Locality (controller ruling 2026-11-22, after the source-map lane's "Cleveland (Solon)" finding): a printed place is
# the record's place when the state is the same and the printed city is a spelling of the record's city or of either
# part of a parenthetical city, or when the two ZIP5 values are equal. One test for the gate and the derivation.
_CITY_WORDS = {"mt": "mount", "st": "saint", "ste": "sainte", "ft": "fort", "pk": "park", "twp": "township"}
_PLACE_KINDS = ("township", "city", "town", "village", "borough")


def city_keys(city: str) -> set:
    """Spellings of one city name, never another place: Mt/St/Ft/Pk spelled out, "City of X" and a trailing
    Township/City/Town/Village/Borough dropped, spaces ignored ("MC COOK" = "McCook", "WEST FENWICK TWP" = "West
    Fenwick"), and both parts of a parenthetical city ("Cleveland (Solon)" -> cleveland, solon). A county is not a city."""
    out = set()
    for name in [re.sub(r"\([^()]*\)", " ", city or "")] + re.findall(r"\(([^()]*)\)", city or ""):
        toks = [_CITY_WORDS.get(t, t) for t in squash(name).split()]
        if toks and toks[-1] in ("county", "parish"):
            continue
        if len(toks) > 2 and toks[1] == "of" and toks[0] in _PLACE_KINDS:
            toks = toks[2:]
        while len(toks) > 1 and toks[-1] in _PLACE_KINDS:
            toks.pop()
        if toks:
            out.add("".join(toks))
    return out


def zip5(z: str) -> str:
    """The 5-digit ZIP of "44139", "44139-1234" or "441391234"; "" for anything else (a 4-digit ZIP that lost its
    leading zero, "317E6", a Canadian postcode, the "00000" placeholder): an unreadable ZIP never matches."""
    m = re.fullmatch(r"\s*(\d{5})(?:-?\d{4})?\s*", z or "")
    return m[1] if m and m[1] != "00000" else ""


def same_zip5(a: str, b: str) -> bool:
    return bool(zip5(a)) and zip5(a) == zip5(b)


def city_differs(rec_city: str, rec_zip: str, q_city: str, q_zip: str) -> bool:
    """Contrary evidence: both sides name a city, no spelling of one is a spelling of the other, and the ZIP5 values are
    not equal. A missing city is not contrary evidence (the gate's state test is separate)."""
    qc, rc = city_keys(q_city), city_keys(rec_city)
    return bool(qc and rc and not qc & rc) and not same_zip5(rec_zip, q_zip)


def same_locality(rec_city: str, rec_state: str, rec_zip: str, q_city: str, q_state: str, q_zip: str) -> bool:
    """Positive test: the same state, and the city matches (either part of a parenthetical counts) or the ZIP5 values
    are equal."""
    st = (rec_state or "").strip().upper()
    if not st or st != (q_state or "").strip().upper():
        return False
    return bool(city_keys(q_city) & city_keys(rec_city)) or same_zip5(rec_zip, q_zip)
