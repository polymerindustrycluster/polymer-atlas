# Evidence backfill, TRI-filing lane (2026-11-20)

**Result:** 80 `existence` evidence rows (EVD-410026 to EVD-410105) on 80 active organizations that had none.
- **By tier:** 71 tier A/B (supports_A), 5 tier C (supports_A) and 4 tier U (supports_U).
- **Witness:** each row is witnessed by the organization's EPA TRI facility record, a `government_filing`.
- **Scope of change:** rows are appended to the organization evidence shards only. No record field, tier or status
  changed.
- **Baseline shrink:** per the file's shrink-only doctrine, `prune_baselines.py` drops the entries this lane now
  satisfies. Its `amended` note is untouched, to avoid conflicts.
  - V-65 ("no naked tier-A/B"): the 71 tier-A/B records now carry a supports_A row and leave it, 2,732 → 2,661 on main
    after PR #427.
  - V-68 (tier C/U presence floor, PR #430): the 9 tier-C/U records leave it, 858 → 849.

**Yield:** 80 of the 109 framed organizations (73%) gained a row.

## Why

The owner's targets (2026-11-20) were at least one evidence row per zero-row record, mechanical claims first.
- 111 zero-evidence organizations already hold a `registry_links` TRI_TRIFID row, but none of them had an evidence row.
- A TRI facility record is a dated filing the facility makes to EPA: SCHEMA §4.13 `government_filing`, which can carry
  supports_A.
- Main already holds about 6,300 rows witnessed this way, for example EVD-011344.
- The owner approved this lane on 2026-11-20 after a 20-record probe (16 named by their facility record).

## Method

`build.py` runs with no model.
1. **Frame** (`frame.csv`): active organizations with no evidence row and at least one TRI_TRIFID link: 109 records
   (A 36, B 63, C 5, U 5).
   - Thirteen records that PR #427 (the URL-lead pilot) evidences are left to it.
2. **Fetch** (`fetch.csv`): each linked TRIFID's record from `data.epa.gov/efservice/tri_facility`. 235 of 235 were
   cached.
   - TRI records carry facility contact names, emails and phones. Every field matching contact, phone or email is
     dropped at fetch and never cached, printed or written (AGENTS.md §6).
3. **Match** (`ledger.csv`, `packet_rows.csv`): deterministic and identity-based.
   - A row is proposed when the filing's facility name or parent-company name equals one of the organization's
     legal, trade or dba names after normalization (case, punctuation, `&`/`and`, legal suffixes; parentheticals tried
     with and without; a trailing `- <city>` plant label is tried without).
   - Ledger: witnessed on the facility name 72, on the parent-company name 9, no match 27 (held), closed-facility flag
     1 (held).
4. **Citation:** each row cites the filing by name and TRIFID ("EPA TRI facility record TRIFID … (data.epa.gov
   efservice tri_facility)"). That is a named-source citation, so V-66 archive-at-capture does not apply. The claim
   detail quotes the facility name, parent and address from the filing.
5. **Refute:** Codex (`review_codex.json`, all 81) and Antigravity (`review_agy_1.json`, `review_agy_2.json`, in halves
   for its 64 KB prompt limit) judged every proposed row under `review_brief.md`, at `--effort deep`.
   - Both judged 80 SOUND.
   - Both judged ORG-000038 UNSOUND: an Akron Panolam record against Panolam's Auburn, Maine (Pionite) plant, with no
     tie shown.
6. **Apply** (`apply.py`): only rows both families judged SOUND, with IDs ascending from EVD-410026, into each record's
   home shard. It then shrinks the V-65 baseline.

## Defect injections, all caught

- `build.py plant`: every framed organization scored against another organization's TRI records produced **0**
  witnesses from 109 mismatched pairings.
- One applied row was altered in `data/`: `check.py` failed ("EVD-410026 differs from applied.csv"), then passed once
  the file was restored.
- `build.py selftest`: dba splitting, parentheticals, plant labels, suffix normalization, the Leggett & Platt division
  non-match, and the personal-field filter.

## Record-health leads (no writes; for triage)

- **ORG-002443 Euramax International:** its own TRI facility now files as OmniMax International LLC (Euramax rebranded
  as OmniMax in 2018). The parent field still says Euramax.
- **ORG-000038 Panolam:** the TRIFID link points to the Auburn, Maine Pionite plant; the Akron record's link deserves a
  look.
- **ORG-000286 THIEM:** its TRI facility carries the closed flag (`fac_closed_ind = 1`). That's a closure lead, never a
  closure (AGENTS.md §3).
- **27 organizations whose TRI record names a different facility or parent:** listed in `ledger.csv` (`NO_MATCH`).
  Some are divisions or renamed plants, so their links may need review.

## Not done

- **Address rows:** a TRI facility address is a plant address, not the organization's HQ (the must-have address
  claim).
- **Liveness rows:** a TRI reporting year as operating evidence has no owner ruling yet.
- **NAICS `code` rows.**

## Merge with PR #427 and PR #430

Both merged to main first. Merging main into this branch conflicted in four files.
- **The OH and PA organization shards:** resolved as main's rows plus this lane's, in ascending evidence-ID order. Every
  row from both sides is present (OH 3,656 + 46; PA 852 + 30).
- **`tasks/QUEUE.md`:** both lines kept; V-68 marked done.
- **`validate_debt_baseline.json`:** main's file, re-shrunk with `prune_baselines.py`.

## Reproduce

```
python3 tasks/evidence-tri-filings-2026-11-20/build.py selftest
python3 tasks/evidence-tri-filings-2026-11-20/build.py frame . <corpus>
python3 tasks/evidence-tri-filings-2026-11-20/build.py fetch <corpus>        # live: data.epa.gov
python3 tasks/evidence-tri-filings-2026-11-20/build.py match . <corpus>
python3 tasks/evidence-tri-filings-2026-11-20/build.py plant <corpus>        # expect 0
python3 tasks/evidence-tri-filings-2026-11-20/apply.py . --start EVD-410026 review_codex.json review_agy_1.json review_agy_2.json
python3 tasks/evidence-tri-filings-2026-11-20/check.py
```
