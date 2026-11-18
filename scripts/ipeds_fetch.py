"""Every US polymer, plastics and materials degree or certificate program, 1991-present.

WHAT THIS IS. The national census of who teaches this subject in the United States, from
IPEDS completions at 6-digit CIP detail, served by the Urban Institute Education Data API.
It is the backbone of the programs map: authoritative, free, annual, and it reaches back
thirty-three years, which no hand-built list ever will.

WHAT ONE ROW IS. One (year, institution, CIP-6, award level) count of degrees or
certificates CONFERRED, race=99 and sex=99 so the number is a total rather than a
demographic cell. `awards` is a count of completions, never of enrolled students and never
of programs.

THE COUNTING TRAP THAT DEFINES THIS FILE. IPEDS reports COMPLETIONS. A real program that
conferred nothing in a given year may be absent from that year entirely, so a single year
UNDERCOUNTS the programs that exist. The API does return some explicit zero rows, but not
reliably for every institution. Therefore: **a program is enumerated from the UNION of all
years it appears in, never from the latest year.** `ipeds_build.py` records first_year and
last_year per (institution, CIP, award level) so a dormant program stays visible and a
closed one is legible as closed. Reading the latest year alone would have said 14
institutions teach polymer engineering; the union says otherwise, and both numbers are
true statements about different questions.

WHY majornum IS CONDITIONAL. IPEDS did not distinguish first and second majors before 2000
(the field does not exist), so filtering majornum=1 in an earlier year returns zero rows and
looks exactly like "no programs existed". The filter is applied from 2000 and dropped before
it. This trap already cost a probe on a sibling script; it is fixed here by construction.

CIP SET. Six codes, verified against the NCES CIP 2020 file. Three are the polymer core and
three are the materials ring that a polymer analysis usually wants alongside it. Note that
40.0510 is FORENSIC chemistry, not materials chemistry, and is deliberately absent - the
name is close enough to have been miscoded elsewhere. There is NO rubber-specific CIP code;
rubber is taught inside 14.3201 and 15.0607 and cannot be separated here.

Run:  python fetch_ipeds_national.py        ->  raw_ipeds_national.json
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

BASE = "https://educationdata.urban.org/api/v1/college-university/ipeds"
# No personal address by default: set PIC_CONTACT only if a service asks for one.
CONTACT = os.environ.get("PIC_CONTACT", "")
UA = {"User-Agent": f"PIC-polymer-programs/1.0 ({CONTACT})" if CONTACT else "PIC-polymer-programs/1.0"}

CIP = {
    "143201": ("Polymer/Plastics Engineering", "polymer"),
    "400507": ("Polymer Chemistry", "polymer"),
    "150607": ("Plastics and Polymer Engineering Technology/Technician", "polymer"),
    "141801": ("Materials Engineering", "materials"),
    "401001": ("Materials Science", "materials"),
    "401002": ("Materials Chemistry", "materials"),
}
# 40.1001 and 40.1002 are CIP 2010 additions; they cannot appear before 2010 and their
# absence in earlier years is a fact about the taxonomy, not about the field.
NEW_IN_CIP2010 = {"401001", "401002"}

# Pinned to the api-values codebook, re-asserted every run (see assert_codebook).
AWARD = {1: "Cert <1yr", 2: "Cert <2yr", 3: "Cert 1-2yr", 4: "Associate",
         5: "Award 1-4yr", 6: "Award 2-4yr", 7: "Bachelor", 9: "Master",
         8: "Post-bacc/post-master cert", 20: "Doctorate (pre-2008)",
         21: "First-professional (pre-2008)", 22: "Doctorate (research)",
         23: "Doctorate (professional)", 24: "Doctorate (other)",
         30: "Cert <12wk", 31: "Cert 12wk-1yr", 32: "Cert 1-2yr", 33: "Cert 2-4yr"}
ASSERT = {4: "Associate's degree", 7: "Bachelor's degree", 9: "Master's degree",
          22: "Doctor's degree, research/scholarship (starting 2007)"}

FIRST_YEAR = 1991          # probed 1983-1990: zero rows for every code and geography
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "ipeds", "raw_ipeds_national.json")


def get(url, tries=4, quiet=False):
    """One GET with backoff. Returns None on a persistent failure, never a partial."""
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                        timeout=180) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (404, 500) and not quiet:
                print(f"    HTTP {e.code}  {url.split('/ipeds/')[-1][:70]}")
            if e.code in (404, 500):
                return None
            time.sleep(3 * (i + 1))
        except Exception:
            time.sleep(3 * (i + 1))
    return None


def paged(url):
    """Follow the API's `next` links. Returns every result row across all pages."""
    out, seen = [], 0
    while url:
        d = get(url)
        if not d:
            break
        out.extend(d.get("results", []))
        url = d.get("next")
        seen += 1
        if seen > 60:                      # a runaway-pagination backstop, never reached
            print("    WARNING: pagination exceeded 60 pages, stopping")
            break
    return out


def assert_codebook():
    """The award-level labels are pinned above; prove the API still agrees."""
    d = get("https://educationdata.urban.org/api/v1/api-values/"
            "?format=json&format_name=award_level")
    labels = {r["code"]: r["code_label"] for r in (d or {}).get("results", [])}
    if not labels:
        print("  codebook unreachable - proceeding on the pinned map")
        return
    for code, want in ASSERT.items():
        got = labels.get(code, "")
        if want not in got:
            raise SystemExit(f"FATAL: award_level {code} is {got!r} in the live codebook, "
                             f"expected {want!r}. The pinned AWARD map is stale - read the "
                             f"codebook before trusting any label in this dataset.")
    print(f"  codebook re-asserted: {len(ASSERT)} award levels match")


def main():
    print("IPEDS national pull - polymer, plastics and materials programs")
    assert_codebook()

    last = FIRST_YEAR
    rows, per_year = [], {}
    year = FIRST_YEAR
    while True:
        got_year = 0
        for cip, (title, group) in CIP.items():
            if cip in NEW_IN_CIP2010 and year < 2010:
                continue
            url = (f"{BASE}/completions-cip-6/{year}/?cipcode_6digit={cip}"
                   f"&race=99&sex=99")
            if year >= 2000:               # the field does not exist before 2000
                url += "&majornum=1"
            for r in paged(url):
                aw = r.get("awards_6digit")
                rows.append({
                    "year": year,
                    "unitid": r["unitid"],
                    "fips": r.get("fips"),
                    "cip": cip,
                    "cip_title": title,
                    "group": group,
                    "award_level": r.get("award_level"),
                    "award": AWARD.get(r.get("award_level"), f"code {r.get('award_level')}"),
                    "awards": aw if isinstance(aw, int) and aw >= 0 else 0,
                })
                got_year += 1
        per_year[year] = got_year
        if got_year:
            last = year
            print(f"  {year}  {got_year:5d} rows")
        elif year > 2020:
            # A modern year with nothing is the end of the published series, not a gap.
            print(f"  {year}      0 rows - end of series")
            break
        year += 1
        if year > 2035:
            break

    insts = sorted({r["unitid"] for r in rows})
    print(f"\n  fetching directory metadata for {len(insts)} institutions")
    directory = {}
    for i in range(0, len(insts), 300):
        chunk = ",".join(map(str, insts[i:i + 300]))
        for r in paged(f"{BASE}/directory/2023/?unitid={chunk}"):
            directory[r["unitid"]] = {
                "name": r.get("inst_name"), "state": r.get("state_abbr"),
                "city": r.get("city"), "sector": r.get("sector"),
                "control": r.get("inst_control"), "url": r.get("inst_url"),
            }
    # 2023's directory misses institutions that closed earlier; fill from the last year
    # each one actually appears, so a closed program still names its institution.
    missing = [u for u in insts if u not in directory]
    if missing:
        print(f"  {len(missing)} not in the 2023 directory (likely closed) - backfilling")
        for u in missing:
            yrs = sorted({r["year"] for r in rows if r["unitid"] == u}, reverse=True)
            for y in yrs[:3]:
                d = get(f"{BASE}/directory/{y}/?unitid={u}", quiet=True)
                res = (d or {}).get("results") or []
                if res:
                    directory[u] = {"name": res[0].get("inst_name"),
                                    "state": res[0].get("state_abbr"),
                                    "city": res[0].get("city"),
                                    "sector": res[0].get("sector"),
                                    "control": res[0].get("inst_control"),
                                    "url": res[0].get("inst_url"),
                                    "closed_after": y}
                    break

    payload = {
        "meta": {
            "source": "IPEDS completions by 6-digit CIP, via the Urban Institute Education "
                      "Data API (educationdata.urban.org)",
            "endpoint": f"{BASE}/completions-cip-6/{{year}}/",
            "row": "one (year, institution, CIP-6, award level) count of completions, "
                   "race=99 sex=99 totals",
            "years": [FIRST_YEAR, last],
            "cip": {k: v[0] for k, v in CIP.items()},
            "counting_rule": "IPEDS counts COMPLETIONS, not programs and not enrolment. A "
                             "program with no completions in a year may be absent from that "
                             "year. Enumerate programs from the UNION of years, never one "
                             "year.",
            "majornum": "filter applied from 2000 only; the field does not exist earlier",
            "no_rubber_cip": "There is no rubber-specific CIP code. Rubber is taught inside "
                             "14.3201 and 15.0607 and cannot be separated in this source.",
            "fetched": time.strftime("%Y-%m-%d"),
        },
        "rows": rows,
        "directory": directory,
        "rows_per_year": per_year,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    with_awards = sum(1 for r in rows if r["awards"] > 0)
    print(f"\n  {len(rows):,} rows  ({with_awards:,} with awards > 0)")
    print(f"  {len(insts):,} institutions  ·  {FIRST_YEAR}-{last}")
    print(f"  wrote {OUT}")


if __name__ == "__main__":
    main()
