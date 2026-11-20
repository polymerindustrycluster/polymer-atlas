# Refute brief: OSHA Form 300A rows for zero-evidence Polymer Atlas sites

You are an adversarial reviewer. Each item is one Atlas **site** (a physical establishment run by an operator
organization) and the 2025 OSHA Injury Tracking Application Form 300A summary that a deterministic matcher found at the
site's street address under a matching name. Each item proposes three evidence rows: `existence`, `address` and
`liveness`. Judge **each row** SOUND or UNSOUND. Do not edit anything; answer only from the data given.

## What each claim means (Atlas schema, §4.13)
- **`existence`**: the site is the operator's site at that address. The operator rule applies: a site belongs to the
  organization that runs the process there.
  - SOUND when the OSHA establishment is this operator's establishment at this address, under the operator's own name,
    a trade name, or a plant name filed under the operator's company name.
  - UNSOUND when the filer is a different company at the same address: a tenant, a landlord, a staffing or facilities
    firm, or an unrelated business in a multi-tenant building. Also UNSOUND when the name match is only a shared generic
    word.
- **`address`**: the Atlas street address is the site's address.
  - SOUND when the OSHA street is the same street address. Abbreviations, a direction word, a suite or a building name
    may differ.
  - UNSOUND when the street number or the street itself differs, or when `existence` is UNSOUND (the filing is then
    not this site's).
- **`liveness`**: the site was operating at a date. Owner ruling 2026-11-20: a government filing whose covered period
  ended within 24 months witnesses liveness. A 2025 Form 300A covers calendar 2025.
  - SOUND when `existence` is SOUND and the filing is for 2025 with employees reported.
  - UNSOUND otherwise.

**Witness class.** A Form 300A summary is a filing the employer makes to OSHA (SCHEMA source class `government_filing`,
which can carry supports_A). These are public establishment records with no personal data.

**Owner ruling 2026-11-20: identity, not legal form.** A missing or different legal suffix alone does not refute.

## Output
Return JSON only:
`{"verdicts": [{"record_id": "SITE-…", "claim_type": "existence" | "address" | "liveness", "verdict": "SOUND" | "UNSOUND", "reason": "<one line>"}]}`
Return three verdicts per item, covering every item. A reason is required for every UNSOUND and every borderline SOUND.

## Items
