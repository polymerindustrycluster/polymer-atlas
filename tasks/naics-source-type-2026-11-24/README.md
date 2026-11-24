# naics-source-type-2026-11-24

22 organizations and sites violated V-47 at the pinned base. Of those, 13 had company_website and two had own_site. None of their own supporting evidence rows contain the six-digit code. All 15 become researcher_inferred, retaining confidence. The validator baseline drops those 15 exemptions.

Seven site records remain in debt. Six lack both provenance and confidence, and one has government_filing without confidence. A script cannot assign confidence.

- SITE-001115 — empty confidence, existing type (blank)
- SITE-003018 — empty confidence, existing type (blank)
- SITE-003020 — empty confidence, existing type (blank)
- SITE-003021 — empty confidence, existing type (blank)
- SITE-003022 — empty confidence, existing type (blank)
- SITE-003023 — empty confidence, existing type (blank)
- SITE-003224 — empty confidence, existing type government_filing

Changed records by verification tier: A 4, B 7, C 4. No rows added. No tier or inclusion decisions. Source: canonical CSVs at the commit in BASE_REF.

Run `python3 tasks/naics-source-type-2026-11-24/build.py` to apply and `python3 tasks/naics-source-type-2026-11-24/check.py` to compare the complete data tree against BASE_REF. CHECK.md records the three negative controls. `python3 scripts/validate.py` passed.

**Rule as merged (round 4):** the brief's mapping from a quoted code to `company_disclosed` / `government_filing` / `directory_assigned` is not used. A record whose evidence mentions its code anywhere is held for a reader; only a code no evidence row mentions becomes `researcher_inferred`. None of the 15 changed rows had a mention, so the data is the same as in round 1.
