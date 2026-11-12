# Schema rulings application pass (2026-11-12) — SCHEMA v1.13

Owner rulings 2026-11-12 (John, in chat: "I approve your suggestions"), on the battery at
staging `working/academic-passes-retro-and-battery-2026-11-12.md`. This pass applies the
five rulings; it is the only pass that touches `docs/SCHEMA.md` and `scripts/validate.py`.

## The rulings and their application

- **S1 — `liquid_crystals` joins the §3.5 supplement.** Applied to the two held Ohio
  programs: PROG-000032 (AMLCI) research_areas + specialty_materials, PROG-000015
  specialty_materials, each on its Kent State page's own words (lane fills in
  `tasks/ohio-academic-depth-2026-11-11/`). Mechanism note (integrator, disclosed):
  `specialty_materials` validates against §3.2 only, so the term is **dual-listed** in
  §3.2 as well as §3.5 — liquid crystals are a material class, and dual-listing is the
  smallest change that delivers the ruled outcome (the held specialty_materials cells)
  instead of re-holding them on a technicality.
- **S2 — `dyeing_finishing` and `fiber_formation` join §3.1.** Applied to the held NC State
  rows: PROG-000065 specialty_processes += dyeing_finishing; fiber_formation (its page's
  "chemical modification of fabrics" remains unmapped — no slug claims it), PROG-000118
  specialty_processes += dyeing_finishing.
- **S3 — scale_band conversion rule** (published program enrollment: small <30, medium
  30–120, large >120 students; qualitative self-characterizations convert directly;
  dollars, faculty counts, credit hours, ratios, alumni counts never convert). Applied to
  the banked Ohio facts that convert: PROG-000007 AFMC (over 350 students) → large;
  PROG-000115 SPSPE ("one of the largest and broadest in the U.S.") → large. The other 12
  banked Ohio facts do not convert under the rule (faculty, dollars, ratios, credit
  hours, alumni) and stay blank, listed in the Ohio packet. Later school integrations
  apply the same rule to their banked facts as they land.
- **S4 — `supports_U` joins the evidence tier_effect vocabulary (V-22).** The one live
  row written under the old vocabulary, EVD-333167 (PERSON-000060, tier U), is corrected
  supports_C → supports_U with the correction noted on the row.
- **S5 — §4.21 name match clarified for the given-names record shape.** Applied:
  PERSON-000541 (Brittany A. Rodriguez, ORNL) is minted — ORCID iD 0009-0008-9557-1987,
  published on her ORNL staff page; the ORCID record (retrieved 2026-11-12) carries
  given-names "Brittany Rodriguez", family-name empty, other-names "Brittany A.
  Rodriguez", and a current ORNL employment ("Technical Staff - Advanced Polymer
  Composites"). match_basis `orcid_record_employment_match_name` under the clarified
  rule. People with an ORCID link: 816 of 1,451.

- **S6 — `lab_url` joins the §4.9 people field set** (owner ruling 2026-11-12, on the
  follow-up question "Are we finding separate lab websites in addition to the university
  faculty pages?"). The column is added empty; it populates from the wave 2–3 integrations
  (the packets' notes name lab sites — e.g. Sarmah's live lab site at Virginia Tech,
  which carried his MACR witness) and from future lanes, which are briefed to record a
  person's lab/group site on an institutional domain whenever they find one. Validator
  V-11's pinned field set is extended to match.

## Also in this PR

- `docs/SCHEMA.md` header moves to v1.13 with the rulings recorded; `scripts/validate.py`
  vocabularies extended to match (PROCESSES, RESEARCH_SUPPLEMENT, TIER_EFFECTS/EFF_RANK).
- QUEUE: this pass claimed; the NC State claim flips to done (PR #270), per the standing
  next-packet pattern.

Validation: `scripts/validate.py` must pass on the new vocabulary; row-loss guard OK.
