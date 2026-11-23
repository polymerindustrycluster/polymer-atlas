"""Binding rules shared by build.py and check.py (stdlib only; imports the repo's own street and name functions).

Binding for a SITE: same_street (scripts/derive_last_activity.py), same state, city equal or ZIP5 equal, and the source's
operator name is a held name: exact, or held name plus corporate-form words only. Binding for an ORG: name as above, and
the quoted city/state is the recorded HQ (or the source's street is the street of one of the org's own sites).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from atlas import squash, name_key, org_name_fields, tokens_semicolon, LOCALITY_SEP_RE  # noqa: E402
from derive_last_activity import same_street  # noqa: E402

CORP_WORDS = {"inc", "incorporated", "llc", "corp", "corporation", "co", "company", "ltd", "limited", "lp", "llp",
              "holdings", "holding", "group", "us", "usa", "northamerica", "americas"}
GENERIC = {"plant", "plants", "facility", "facilities", "warehouse", "main", "north", "south", "east", "west", "n", "s", "e", "w",
           "ne", "nw", "se", "sw", "northeast", "northwest", "southeast", "southwest", "central", "and", "the", "of"}
STATES = {"alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware", "florida", "georgia", "hawaii",
          "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine", "maryland", "massachusetts", "michigan",
          "minnesota", "mississippi", "missouri", "montana", "nebraska", "nevada", "hampshire", "jersey", "mexico", "york", "carolina",
          "dakota", "ohio", "oklahoma", "oregon", "pennsylvania", "rhode", "island", "tennessee", "texas", "utah", "vermont", "virginia",
          "washington", "wisconsin", "wyoming", "oh", "pa", "mi", "in", "ky", "wv"}


def name_match(held, src):
    """held and src are atlas.name_key strings. Exact, or held followed only by corporate-form words (views.sql macro)."""
    if not held or not src:
        return False
    if held == src:
        return True
    if src.startswith(held + " "):
        rest = src[len(held) + 1:].replace("north america", "northamerica").split()
        return all(t in CORP_WORDS for t in rest)
    return False


def city_parts(city):
    """'Akron (Ellet)' -> {'akron', 'ellet'}: the Atlas city may carry a second locality in parentheses; accept either part."""
    c = city or ""
    parts = {squash(re.sub(r"\(.*?\)", " ", c))} | {squash(m) for m in re.findall(r"\(([^()]*)\)", c)}
    return {p for p in parts if p}


def city_or_zip(site_city, site_zip, src_city, src_zip):
    z = (site_zip or "")[:5]
    sz = (src_zip or "")[:5]
    return (bool(z) and z.isdigit() and z == sz) or squash(src_city) in city_parts(site_city)


def site_name_parts(site_name):
    """Parts of a site name split at ' - ', en/em dash, and parenthesised text; the whole name is also a part."""
    s = site_name or ""
    out = [s] + LOCALITY_SEP_RE.split(s) + re.findall(r"\(([^()]*)\)", s) + [re.sub(r"\(.*?\)", " ", s)]
    seen, res = set(), []
    for p in out:
        p = p.strip()
        if p and p not in seen:
            seen.add(p)
            res.append(p)
    return res


def is_generic_part(part, city, county):
    """Every word is a generic label: plant, facility, warehouse, main, a number, a compass word, a state, the site's city or county."""
    ban = GENERIC | STATES | set(squash(city).split()) | set(squash(county).split()) | set(squash(county + " county").split())
    toks = squash(part).split()
    return not toks or all(t in ban or t.isdigit() or re.fullmatch(r"\d+(st|nd|rd|th)?", t) for t in toks)


def parent_keys(org, parent_org=None):
    """name_keys of the recorded parent: ultimate_parent_name and the names of the parent_org_id record."""
    ks = {name_key((org or {}).get("ultimate_parent_name", ""))}
    if parent_org:
        ks |= {name_key(v) for _, v in org_name_fields(parent_org)}
    return {k for k in ks if k}


def held_names(site, org, parent_org=None):
    """-> list of (name, name_key, kind) a site answers to: the org's legal/trade/marked-alias names plus the site-name parts that are not
    generic labels. A recorded parent's name never binds, on any path: an entry whose key is a parent key is dropped unless it is the
    org's own legal_name (owner round 9)."""
    pk = parent_keys(org, parent_org)
    out = []
    for fld, val in (org_name_fields(org) if org else []):
        out.append((val, name_key(val), f"org:{fld}"))
    for p in site_name_parts(site["site_name"]):
        if not is_generic_part(p, site["city"], site["county"]):
            out.append((p, name_key(p), "site_name_part"))
    return [x for x in out if x[1] and not (x[1] in pk and x[2] != "org:legal_name")]


def match_held(src_name_key, held):
    """First held name that matches; a legal_name (or its marked alias) match is preferred over any other kind."""
    hits = [(name, kind) for name, k, kind in held if name_match(k, src_name_key)]
    hits.sort(key=lambda x: 0 if x[1].startswith("org:legal_name") else 1)
    return hits[0] if hits else None


BUSINESS = set("""inc incorporated llc corp corporation co company ltd limited lp llp holdings holding group us usa industries industrial plastics plastic rubber
products product manufacturing mfg tool tools mold molds molding machine machining systems system technologies technology tech services service enterprises
enterprise solutions supply supplies sales trading packaging polymer polymers composites composite coatings coating foam films film fabrication fabricators
engineering engineers design designs international intl global american ohio akron cleveland associates partners labs laboratory laboratories materials
material recycling recyclers metal metals steel plating finishing plastics custom precision quality advanced applied innovative dynamics tire tires
automotive auto electric electronics controls instruments instrument chemical chemicals paper stock sons brothers bros works shop corporation pattern
rotational extrusion thermoforming injection die dies sealing seals gasket gaskets hose belting lighting sign signs products medical biofilms""".split())


def person_like(name, org):
    """looks_like_person AND the record has no website: an organization with its own website is a business, not an individual."""
    return looks_like_person(name) and not ((org or {}).get("website") or "").strip()


def looks_like_person(name):
    """A source name of 2-3 alphabetic words and no business word reads as a natural person (sole proprietor, trustee, individual filer).
    shortcut: word-list heuristic, upgrade if a reviewer finds a miss; matches are held back and their text is never written."""
    toks = squash(name).split()
    return 2 <= len(toks) <= 3 and all(t.isalpha() for t in toks) and not any(t in BUSINESS for t in toks)


def same_street_pair(site_street, printed):
    return same_street(site_street, printed)


# ---- the two decisions, used by build.py and replayed by check.py -----------------------------------------------
def bind_site(site, org, c, parent_org=None):
    """c: a source row (name, street, city, state, zip, role, fam). -> ('ok', basis) or ('lead', reason)."""
    if not same_street(site["street_address"], c["street"]):
        return "lead", "street_differs"
    if (c["state"] or "").strip().upper() != "OH":
        return "lead", "state_differs"
    if not city_or_zip(site["city"], site["zip"], c["city"], c["zip"]):
        return "lead", "city_and_zip_differ"
    held = held_names(site, org, parent_org)
    nk = name_key(c["name"])
    m = match_held(nk, held)
    if not m:
        pk = parent_keys(org, parent_org)
        return "lead", ("name_is_recorded_parent_only" if any(name_match(k, nk) for k in pk) else "operator_name_not_held")
    if person_like(c["name"], org):
        return "lead", "source_name_looks_like_a_natural_person"
    if c["role"] != "physical":
        return "lead", "mailing_role_only_not_a_physical_location_witness"
    return "ok", f"held name '{m[0]}' ({m[1]}); same street; state OH; city or ZIP5 equal"


def org_held(org, parent_org=None):
    pk = parent_keys(org, parent_org)
    return [(v, name_key(v), f"org:{k}") for k, v in org_name_fields(org) if name_key(v) and not (name_key(v) in pk and k != "legal_name")]


def _org_name(org, parent_org, c):
    """Held-name test for an organization record. Only the record's own legal name (or a marked alias of it) witnesses the entity: a
    match through trade_names alone may be a different legal entity (an operating subsidiary), which does not witness the holding record
    (controller ruling 2026-11-22, Q5): reason different_entity_trade_name."""
    nk = name_key(c["name"])
    m = match_held(nk, org_held(org, parent_org))
    if m and person_like(c["name"], org):
        return None, "source_name_looks_like_a_natural_person"
    if m and m[1].startswith("org:legal_name"):
        return m, None
    if m:
        return None, "different_entity_trade_name"
    pk = parent_keys(org, parent_org)
    return None, ("name_is_recorded_parent_only" if any(name_match(k, nk) for k in pk) else "operator_name_not_held")


def _hq(org, c):
    return squash(c["city"]) in city_parts(org["hq_city"]) and (c["state"] or "").strip().upper() == org["hq_state"].strip().upper()


def bind_org_existence(org, c, own_sites=(), parent_org=None):
    """Held legal name and (quoted city/state = recorded HQ, or the source's street is the street of one of the org's own sites)."""
    m, why = _org_name(org, parent_org, c)
    if not m:
        return "lead", why
    if _hq(org, c):
        return "ok", f"held name '{m[0]}'; quoted city/state = recorded HQ {org['hq_city']}, {org['hq_state']}"
    for s in own_sites:
        if c["role"] == "physical" and same_street(s["street_address"], c["street"]) and city_or_zip(s["city"], s["zip"], c["city"], c["zip"]):
            return "ok", f"held name '{m[0]}' at the street of own site {s['site_id']}"
    return "lead", "quoted_location_is_not_the_recorded_hq_or_an_own_site_street"


def bind_org_address(org, c, own_sites=(), parent_org=None, allow_mailing=False):
    """An `address` claim only from a source that states the entity's own address (a Form 5500 sponsor address), only when the quoted city and
    state are the recorded HQ (SCHEMA 4.8 S-5), and (strict reading, owner question Q1) only from a location-role address or a street that is
    an own site's street. A mailing-role address that is neither is `mailing_role_address_owner_question_q1`: allowed only with allow_mailing."""
    if c["fam"] == "sam":
        return "lead", "sam_held_owner_question_dnb_flag"
    if not c["fam"].startswith("form5500"):
        return "lead", "establishment_address_is_not_the_entitys_own_address"
    m, why = _org_name(org, parent_org, c)
    if not m:
        return "lead", why
    if not _hq(org, c):
        return "lead", "quoted_city_state_is_not_the_recorded_hq"
    own_street = any(same_street(s["street_address"], c["street"]) for s in own_sites)
    if c["role"] != "physical" and not own_street and not allow_mailing:
        return "lead", "mailing_role_address_owner_question_q1"
    return "ok", f"sponsor's own {c['role']} address; held name '{m[0]}'; quoted city/state = recorded HQ {org['hq_city']}, {org['hq_state']}"
