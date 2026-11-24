"""Decide from the fixed base and actual establishment filings before consulting proposed edits."""

import re
from frame import BASE, HERE, git, rows
from atlas import name_key, site_name_key, squash
from matching import designators_compare, same_street
from build_osha_ita import band_of
from check_evidence_binding import Index, judge

FIELD = "employee_band_site"
CUTOFF = "2016-11-24"


def adjudicate(frame, raw):
    index = Index.load(BASE)
    files = git("ls-tree", "-r", "--name-only", BASE, "data").decode().splitlines()
    evs = [
        e for f in files if re.fullmatch(r"data/evidence_.*\.csv", f) for e in rows(f)
    ]
    top = max(int(e["evidence_id"][4:]) for e in evs)
    # The parallel HQ packet reserved EVD-483118 and EVD-483119.
    top = max(top, 483119)
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
            if not spine_band:
                continue
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
            value = band_of(int(count)) if count.isdigit() else ""
            if not value or value != spine_band:
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
        if matches:
            latest = max(f[1] for f in cited if f[3])
            matches = [m for m in matches if m[0] == latest]
        result["source"] = " | ".join(sorted({m[2] for m in matches}))
        reason = ""
        values = {m[1] for m in matches}
        screening_day = max(f[1] for f in cited if f[3])
        screening_bands = {f[3] for f in cited if f[1] == screening_day and f[3]}
        if len(screening_bands) > 1 and values != {s[FIELD]}:
            result["reason"] = "co-located same-date filings disagree; establishment unresolved"
            continue
        if any("raw locator" in r or "screening extract" in r for r in reasons):
            reason = "raw replay unresolved"
        elif len(values) > 1:
            reason = "bound filings disagree"
        elif not any(m[5] for m in matches):
            reason = "no binding cited establishment filing"
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
        if any(
            e["record_id"] == sid
            and e["source_class"] == "own_site"
            and e["claim_type"] == "size_band"
            and e["observed_date"] >= day
            for e in evs
        ):
            changes.clear()
            result["reason"] = "newer own-site size evidence requires reading"
            continue
        old = (
            r"BAND-SOURCE: employee_band_site="
            + re.escape(s[FIELD])
            + r" from [^.]*?\(government_filing[^)]*\)\."
        )
        note = f"BAND-SOURCE: employee_band_site={value} from {ref}, source date {day} (government_filing; band only, not a headcount)."
        new, n = re.subn(old, note, s["notes"])
        if n != 1:
            raise ValueError((sid, "ambiguous note", s["notes"]))
        changes["notes"] = new
        ev = dict(
            evidence_id=f"EVD-{top + 1:06}",
            record_table="sites",
            record_id=sid,
            claim_type="size_band",
            claim_detail=f"employee_band_site={value} from {ref}, source date {day}; quote: {quote}",
            source_class="government_filing",
            source_ref=ref,
            observed_date=day,
            tier_effect="supports_B",
            created_by="atlas-p1 " + HERE.name,
            notes="",
            address_role="",
        )
        # A separately bound establishment can also be quoted by its actual company_name field.
        if (
            judge(ev, index)[0] != "PASS"
            and kind == "ITA"
            and name_key(company) in held_names
        ):
            ev["claim_detail"] = (
                ev["claim_detail"].split("quote: ")[0]
                + "quote: "
                + company
                + quote[len(name) :]
            )
        verdict, why, _ = judge(ev, index)
        if verdict != "PASS":
            changes.clear()
            result["reason"] = "binding gate " + why
            continue
        top += 1
        result["evidence"] = ev
        result.update(verdict="corrected", reason=ref)
    return answer
