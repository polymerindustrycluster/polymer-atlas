# Refute brief: TRI-filing existence rows for zero-evidence Polymer Atlas organizations

You are an adversarial reviewer. Each item below proposes ONE evidence row: an `existence` claim for an Atlas
organization, witnessed by that organization's EPA Toxics Release Inventory (TRI) facility record. Judge each row
**SOUND** or **UNSOUND**. Do not edit anything; answer only from the data given.

## The rules you are applying
- **`existence` means the entity is the entity claimed** (its legal name or identity). The row says nothing about
  address, scope or whether the company is still operating.
- **Witness class.** A TRI facility record is a filing a facility makes to EPA (SCHEMA source class
  `government_filing`, A-capable). The Atlas already links each of these TRIFIDs to the organization (a
  `registry_links` row); the link's basis is in the notes and can be fuzzy. Your job is to decide whether the filing
  really names THIS organization.
- **Owner ruling (2026-11-20): identity, not legal form.**
  - A trade name, or the legal name without its suffix, witnesses existence; "Inc" vs "LLC" alone does not refute.
  - It does NOT cover a different legal entity, a parent, an acquirer, a subsidiary, or a coincidental name.
- **Facility-name match ("matches ... on the facility name").** SOUND when the facility named in the filing is this
  organization (or this organization's own plant under its own name). UNSOUND when the name only coincides with a
  different company, for example a same-name firm in another state with no tie to this record, or when the facility
  is a different entity.
- **Parent-name match ("matches ... on the parent-company name").** The filing names this organization as the parent
  company of the reporting facility. That witnesses that the parent company exists under that name. It is SOUND only if
  the Atlas record IS that parent company. It is UNSOUND if the Atlas record is a different entity, such as the
  subsidiary, a division, or a company that shares a word with the parent.
- When the name match leans on stripping a qualifier (a plant name, a parenthetical, "dba"), check that the remainder
  still identifies this organization.

## Output
Return JSON only:
`{"verdicts": [{"record_id": "...", "claim_type": "existence", "verdict": "SOUND" | "UNSOUND", "reason": "<one line>"}]}`
One verdict per item, covering every item. A reason is required for every UNSOUND and every borderline SOUND.

## Items
