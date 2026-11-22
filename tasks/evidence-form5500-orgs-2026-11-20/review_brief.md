# Refute brief: Form 5500 rows for zero-evidence Polymer Atlas organizations

You are an adversarial reviewer. Each item is one Atlas **organization** (a company) and the DOL Form 5500 or 5500-SF
employee-benefit-plan filing that a deterministic matcher found for it. The match is one of two kinds:
- **`EIN+NAME`**: the sponsor's EIN is one the Atlas links to the organization, and the sponsor name matches.
- **`NAME+CITY`**: the sponsor name (or DBA) equals the organization's legal or trade name, after removing legal
  suffixes and punctuation. The sponsor's address is also in the organization's HQ city and state, and only one EIN
  files under that name there.

Each item proposes up to three rows: `existence`, `address` and `liveness`. Judge **each row** SOUND or UNSOUND. Do not
edit anything; answer only from the data given.

## The 2026-11-22 cut

Items are the cut packet: 76 organizations with `existence` (and some `address`/`liveness`) proposed, and 176 organizations
evidenced elsewhere with `liveness` only. A liveness-only item has no `existence` row; judge its `liveness` row SOUND only
if the sponsor is also the organization (identity). Each `address` item now also states a street match
(`filing.location_street` / `mailing_street` against `atlas_hq_site_streets`); judge it UNSOUND if they are not the same
street. Return verdicts for the proposed rows only.

## What each claim means (Atlas schema, §4.13)

### `existence`
The organization exists, as the entity named.
- **SOUND** when the plan sponsor is this organization: the same company under its legal name, a DBA, or a trade name
  that is the same legal entity.
- **UNSOUND** in either of these cases:
  - The sponsor is a different legal entity, such as a subsidiary, parent, predecessor or affiliate. This applies even
    when the Atlas lists that entity's name as a trade name. The claim detail says when the match runs through an
    Atlas trade name.
  - The name is generic enough that a different business in the same city could plausibly carry it.

  Give the deciding fact.

### `address`
The organization's HQ is in the stated city and state.
- **SOUND** when `existence` is SOUND and the sponsor's address in the filing is in that city and state. The filing's
  location address governs when one is given; otherwise the mailing address is used.
- **UNSOUND** when `existence` is UNSOUND, or when the data shows the address belongs to someone else, such as a
  third-party administrator or payroll provider.

### `liveness`
The organization was operating at the plan-year end.
- **Owner ruling 2026-11-20:** a government filing whose covered period ended within 24 months witnesses liveness. The
  row's `observed_date` is the plan-year end.
- **SOUND** when all of these hold:
  - `existence` is SOUND;
  - the plan year ended on or after 2024-11-20;
  - the filing reports active participants above zero at year end;
  - it is not a final filing.
- **UNSOUND** otherwise.

## Witness class and limits
- **Class:** a Form 5500 is a filing the plan sponsor makes to the Department of Labor (source class
  `government_filing`, which can carry supports_A). Tier-U organizations get supports_U.
- **What a sponsor is:** the plan sponsor is normally the employer.
- **Contents:** only business fields are shown. No signer, phone or personal data is used.
- **Owner ruling 2026-11-20 (identity, not legal form):** a missing or different legal suffix alone does not refute.

## Output
Return JSON only:
`{"verdicts": [{"record_id": "ORG-…", "claim_type": "existence" | "address" | "liveness", "verdict": "SOUND" | "UNSOUND", "reason": "<one line>"}]}`
- Return one verdict per proposed row, covering every item.
- A reason is required for every UNSOUND and every borderline SOUND.

## Items
