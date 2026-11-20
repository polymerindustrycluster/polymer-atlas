# Evidence backfill, OSHA site lane (2026-11-20)

**Result:** 251 evidence rows (EVD-410106 to EVD-410356) on 84 active sites that had none.
- **By claim:** 84 `existence`, 83 `address`, 84 `liveness`.
- **By tier:** 13 A, 66 B, 5 C (supports_A on each).
- **Witness:** each site's own 2025 OSHA Injury Tracking Application Form 300A summary, a `government_filing`.
- **Scope of change:** rows are appended to the site evidence shards only. No record field, tier or status changed.
- **Baseline shrink:** the evidenced sites leave the shrink-only baselines. V-65 (tier A/B) goes 2,661 → 2,582 and V-68
  (tier C/U) goes 849 → 844. The `amended` note is untouched.
- **Held for a second family:** 43 more address-and-name matches (129 rows). Codex has reviewed them, but Antigravity
  ran out of quota mid-review (`review_agy_3_FAILED_quota.txt`, resets in about 4 days) and both Grok routes have
  expired keys. They are held, never applied, until a second family judges them (see "Pending").

## Why

**Sites are the largest part of the evidence gap:** 1,838 of 3,360 zero-row records on main `18cb709c`.
- 917 have no street in the Atlas.
- The cited-URL route witnesses few sites, because operator homepages rarely print plant addresses (the URL pilot; a
  locations-page probe found 2 of 19).
- EPA FRS is a `registry`, capped at B, and at C for addresses.

**Why OSHA works.** A Form 300A summary is filed by the establishment itself, giving its name, company, street, city,
state and average employees for a calendar year. As a `government_filing` it can carry supports_A for existence and
address, so it also helps tier-A sites.

## Owner ruling 2026-11-20 (ruling 8 for the evidence lanes)

A dated government filing whose covered period ended within 24 months witnesses `liveness`, at up to supports_A. That
includes a TRI reporting year, an OSHA 300A calendar year, and a Form 5500 with active participants. The witnessed
date is the end of the period.
- It extends ruling 6 (an own-site dated event within 12 months), which still governs own-site liveness.
- A 2025 Form 300A covers calendar 2025, which ended 2025-12-31.
- Also recorded on this lane's QUEUE line.

## Method

`build.py` runs with no model.
1. **Source:** `ITA_300A_Summary_Data_2025_through_08-31-2026.csv` from osha.gov (400,288 establishment filings; 88 MB;
   sha256 `9ea2ee5d7265cddf…`; fetched 2026-11-20).
   - osha.gov returns 403 to non-browser User-Agents.
   - The file is kept outside the repo, in `_atlas-corpus/osha-ita/`.
2. **Frame:** active zero-evidence sites with a parseable street. That's 915.
3. **Match** (`ledger.csv`): a filing qualifies only when it sits at the site's address (same state, street number,
   first street word and city) **and** carries the operator's or site's name.
   - The name test is exact or containment, with names of four characters or more.
   - A filing named only for its town is ignored.
   - Verdicts: address and name 133, address only 123 (held, not written), no match 659.
4. **Rows** (`packet_rows.csv`): `existence`, `address` and `liveness` for each matched site.
   - Each row cites the filing by name and establishment ID ("OSHA ITA Form 300A summary, filing year 2025,
     establishment ID … (osha.gov ITA_300A_…csv)"). That is a named source, so V-66 archive-at-capture does not apply.
   - The address row notes that the filing carries no county.
5. **Refute** (`review_brief.md`, `--effort deep`, in three parts):
   - Codex judged all 399 rows (`review_codex_1..3.json`).
   - Antigravity judged parts 1–2 (`review_agy_1..2.json`, 270 rows) before its quota ran out.
6. **Apply** (`apply.py`):
   - Only rows SOUND in both families apply.
   - A site whose existence row either family rejected loses all its rows.
   - Rows a family has not judged are withheld as "awaiting review".
   - IDs ascend from EVD-410106.

**Withheld, rejected (19 rows).** Six sites lost existence:
- **Street-type mismatch:** SITE-002620 (Birchmont Road vs Drive), SITE-002698 (Palmer Industrial Drive vs Road).
- **Filer is a related but different entity:**
  - SITE-002734: LORD Corporation filed, Parker-Hannifin is the operator;
  - SITE-003846: Brown LLC for BMG LLC;
  - SITE-003869: American Rheinmetall for Loc Performance;
  - SITE-004032: Alro Steel for Alro Plastics.
- One further row was rejected individually.

## Defect injections, all caught

- `build.py plant`: each site's names scored against another site's address produced 0 matches from 915 pairings.
  - The first run found 3. Two were real false positives, filings named only for the town ("Leola", "Nashville"),
    and the matcher now ignores those. The third was two Atlas sites at the same address, which the test now skips.
- One applied row was altered in `data/`: `check.py` failed ("EVD-410106 differs from applied.csv"), then passed once
  the file was restored.
- `build.py selftest`: street keys, suffix normalization, town-name filings, short-name containment.

## Record-health leads (no writes)

123 sites have a 2025 OSHA filing at their exact address under **another** name (`ledger.csv`, `ADDR_ONLY`).
- Some are successor or affiliate operators: Lehigh Gasket's address now files as Staver Hydraulics; J-B Weld's as
  EG4 Electronics; Resinall's as its parent Ergon.
- Some are multi-tenant buildings.
- Each is a lead for operator re-verification, never a change by itself.

## Part 3: applied on Codex alone, under the owner's waiver of 2026-11-20

**Why.** No second family was available. Antigravity was out of quota, both Grok routes had expired keys, and the
Gemini CLI hung on login. The owner ruled (2026-11-20, multiple choice) **"Codex-only for now"**: Codex alone gates the
evidence lanes until a second family returns.

**Result** (`apply_part3.py`, `applied_part3.csv`, merged in a follow-up PR):
- Of the 43 held sites (129 rows), the rows Codex judged SOUND apply: **120 rows, EVD-410357..410476, on 40 sites**.
- Three sites whose existence row Codex rejected lose all their rows.
- Each part-3 row's notes say it was reviewed by Codex only, under the waiver.
- V-65 2,582 → 2,549 and V-68 844 → 837.
- `check.py` covers both rounds.

**Across both rounds:** 371 rows on 124 sites.

## Reproduce

```
python3 tasks/evidence-osha-sites-2026-11-20/build.py selftest
python3 tasks/evidence-osha-sites-2026-11-20/build.py match . <osha.csv> <corpus>
python3 tasks/evidence-osha-sites-2026-11-20/build.py plant . <osha.csv>     # expect 0
python3 tasks/evidence-osha-sites-2026-11-20/apply.py . --start EVD-410106 --codex review_codex_1.json review_codex_2.json review_codex_3.json --agy review_agy_1.json review_agy_2.json
python3 tasks/evidence-osha-sites-2026-11-20/check.py
```
