# Integrator backlog 3 (2026-11-05)

The repo owner chose this pass in session on 2026-11-05. It settles 14 items that #122, #123 and #124 held or found.
One evidence lane answered each from dated public sources (`LANE_BRIEF.md` → `findings.csv`). Every quote was
re-fetched through Firecrawl, then Jina Reader, and matched as a word sequence (`rawcheck.csv`): 10 of 14 passed.

## Applied (`build.py`; `journal.txt`)
| Change | Organizations |
|-|-:|
| `status=acquired` on a dated deal, with its `successor_of` edge and a `parent` evidence row | 2 |
| `status=merged` (a corporate combination), with its `merged_into` edge and a `parent` evidence row | 1 |
| HQ city corrected within its state, with an `address` evidence row | 2 |
| `website` cleared: the domain now serves unrelated content or is for sale (old value kept in notes) | 3 |
| `website` replaced: the company now trades under a new name and domain | 1 |

The details:
- **Acquired:** Performance Plastics, Cincinnati → Pexco, 2022-09-15, from Pexco's own timeline. #122 held it while
  Pexco was recorded twice. Johnsonite → Tarkett North America, 2005-12-08; that is the announcement date, since no
  closing date was found.
- **Merged:** BWAY → Mauser Packaging Solutions, 2018-10-08. This is the corporate combination, not a record
  consolidation.
- **HQ:** Ametek → Berwyn, PA. #123 flagged the old value, which came from the sold Nesquehoning plant. Clearly Clean
  → Frackville, PA.
- **Websites:**
  - W.B. Wagner Tire's domain redirects to a gambling site.
  - HPE Extrusion's serves unrelated content, and the lane notes Pexco as a possible successor, a lead for the next
    ownership round.
  - Paddington Group's is for sale. Two independent lanes saw this, so the field is cleared without a raw-verified
    quote; clearing asserts nothing about the company.
  - Federal Process now trades as FPC International (`fpcintl.com`), added as a trade name.

6 evidence rows and 3 generated relationship rows.

## Review
Codex and grok each tried to refute the applied changes (deep effort, read-only).
- **Grok:** 7 OK, 1 overreach, 1 unsure.
- **Codex:** 5 OK. Its other flags came mostly from a prompt that left out the successor names; the second prompt
  gave them.
- **Held after review:** the KNF duplicate. Both records share one address and website, but no source states that they
  are one legal entity, and a sister company, KNF Clean Room, exists. AGENTS.md §3: when in doubt, do not merge.
- **Kept against a flag:**
  - Johnsonite's date is the announcement date. The record's notes say so, which SCHEMA §5.4 allows.
  - Paddington's website is cleared even though its quote was not raw-verified. Two lanes saw the domain-for-sale
    page, and a clear asserts nothing about the company.

## Held
- KNF Flexpak / KNF Corp.: held after review, as above.
- 84 Fairmount Street: the quote again failed the raw check, because the page renders by script.
- Esschem, Linwood: the plant belongs to Esschem, Inc., a separate Justi Group company that the Atlas does not hold.
  Creating it needs its own evidence.
- Westfall, Las Vegas: Westfall no longer lists the location, but that is not closure evidence.
- Ronald Mark: Hillside, NJ is confirmed, so nothing changes.

Checks: rehearsed on a temp copy. `python scripts/validate.py` exits 0 on the committed tree.
