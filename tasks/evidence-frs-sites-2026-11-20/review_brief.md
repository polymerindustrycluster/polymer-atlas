# Refute brief: EPA FRS rows for zero-evidence Polymer Atlas sites

You are an adversarial reviewer. Each item is one Atlas **site** (a physical establishment run by an operator
organization) and the EPA Facility Registry Service (FRS) record that the Atlas already links to it. A deterministic
matcher re-read that record in EPA's own state combined file and found it in the site's state and city, under a
matching name. Your job is to judge **each proposed row** SOUND or UNSOUND. Do not edit anything; answer only from the
data given.

The `verdict` field says which match each item is:
- **`ADDR+NAME`**: the FRS street is the Atlas street.
- **`CITY+NAME`**: the Atlas holds no street for this site, so only the city (or ZIP) and the name were compared.

`frs_link_basis` is how the Atlas link was first made. ECHO street-exact means EPA's ECHO exporter matched the street at
link time.

## What each claim means (Atlas schema, §4.13)

### `existence`
The site is the operator's establishment at that location. The operator rule applies: a site belongs to the
organization that runs the process there.
- **SOUND** when the FRS facility is this operator's establishment at this location, under one of:
  - the operator's own name;
  - a trade name;
  - a plant name carrying the operator's name.
- **UNSOUND** in any of these cases:
  - The FRS name is a different company, such as a predecessor, an affiliate, a tenant, a landlord or an unrelated
    business, even when the Atlas site name repeats that company's name. Give the deciding fact.
  - The names share only a generic word.
  - For `CITY+NAME`: the record could plausibly be a different establishment of the same operator in the same city.
    One example is a large multi-plant company whose FRS name does not tie it to this site.

### `address`
Proposed only for tier-C/U sites with `ADDR+NAME`. The claim is that the Atlas street address is the site's address.
- **SOUND** when the FRS street is the same street address. Abbreviations, a direction word, a suite or a building
  name may differ.
- **UNSOUND** when the street number or the street itself differs, when the street type conflicts (Road vs Drive), or
  when `existence` is UNSOUND.

## Witness class and limits
- **Class:** FRS is a `registry`. Existence caps at supports_B and a registry address at supports_C. Tier-U sites get
  supports_U.
- **Contents:** these are public facility records with no personal data.
- **Not a liveness claim:** an FRS record can persist after a facility closes. Existence is an identity claim here,
  not a claim that the facility is operating, so do not judge liveness. The Atlas lists every site in this packet as
  active.
- **Owner ruling 2026-11-20 (identity, not legal form):** a missing or different legal suffix alone does not refute.
  An FRS name carrying an internal ID in parentheses is the same name.

## Output
Return JSON only:
`{"verdicts": [{"record_id": "SITE-…", "claim_type": "existence" | "address", "verdict": "SOUND" | "UNSOUND", "reason": "<one line>"}]}`
- Return one verdict per proposed row, covering every item.
- A reason is required for every UNSOUND and every borderline SOUND.

## Items
