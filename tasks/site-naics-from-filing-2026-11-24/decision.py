"""Decide from the fixed base and actual establishment filings before consulting proposed edits."""

import re
from frame import BASE
from atlas import name_key, site_name_key, squash
from matching import designators_compare, same_street
from check_evidence_binding import Index

FIELD = "naics_primary"
CUTOFF = "2016-11-24"


def adjudicate(frame, raw):
    index = Index.load(BASE)
    answer = {}
    for sid, (cited, all_matches) in sorted(frame.items()):
        s = index.sites[sid]
        changes = {}
        result = dict(
            verdict="held", reason="", source="", changes=changes, evidence={}
        )
        answer[sid] = result
        held_names = index.org_keys(s["org_id"]) | {
            site_name_key(s["site_name"], s["city"]),
            name_key(s["site_name"]),
        }
        matches = []
        reasons = set()
        for kind, day, key, spine_band, spine_code, _, _ in all_matches:
            hits = raw.get((kind, day, key), set())
            if len(hits) != 1:
                reasons.add("missing or ambiguous raw locator " + key)
                continue
            name, company, street, city, state, zipcode, code, count = next(iter(hits))
            if (
                not same_street(s["street_address"], street)
                or designators_compare(street, s["street_address"]) != "equal"
                or squash(city) != squash(s["city"])
                or state != s["state"]
            ):
                reasons.add("street, unit or locality does not bind: " + key)
                continue
            if not held_names.intersection(
                {name_key(name), site_name_key(name, city)}
            ) - {""}:
                reasons.add("establishment name does not bind: " + key)
                continue
            value = code
            if not re.fullmatch(r"[1-9][0-9]{5}", value):
                continue
            if spine_code and value != spine_code:
                reasons.add("source differs from screening extract: " + key)
                continue
            quote = f"{name}, {street}, {city}, {state} {zipcode}"
            if kind == "ITA":
                ref = f"OSHA ITA CY{day[:4]} establishment {key}"
            elif kind == "inspection":
                ref = f"OSHA inspection {key} opened {day}"
            else:
                ref = f"EPA TRI RY{day[:4]} facility {key}"
            eligible = any(tuple(f[:3]) == (kind, day, key) for f in cited)
            matches.append((day, value, ref, quote, company, eligible, kind, name))
        result["source"] = " | ".join(sorted({m[2] for m in matches}))
        reason = ""
        values = {m[1] for m in matches}
        if any("raw locator" in r or "screening extract" in r for r in reasons):
            reason = "raw replay unresolved"
        elif len(values) > 1:
            reason = "bound filings disagree"
        elif not any(m[5] for m in matches):
            reason = "no binding cited establishment filing"
        elif sid == "SITE-000814":
            reason = "pilot could not settle establishment identity"
        if reason:
            result["reason"] = "; ".join([reason, *sorted(reasons)])
            continue
        day, value, ref, quote, company, _, kind, name = max(
            (m for m in matches if m[5]), key=lambda m: (m[0], m[6] == "ITA", m[2])
        )
        if day < CUTOFF:
            result["reason"] = "stale_over_10_years"
            continue
        if value == s[FIELD]:
            result.update(
                verdict="verified", reason="binding source confirms held value"
            )
            continue
        changes[FIELD] = value
        changes["naics_primary_source_type"] = "government_filing"
        changes["naics_confidence"] = "medium" if kind == "ITA" else "high"
        if "naics_primary_source_name" in s:
            changes["naics_primary_source_name"] = ref
        result.update(verdict="corrected", reason=ref)
    return answer
