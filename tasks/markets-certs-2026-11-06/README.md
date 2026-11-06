# L10 markets and certifications — PIC-18 batch, 2026-11-06

Claim: atlas-L10-markets-certs (IDEAS B-01/B-07), delegated integrator scope: only organization markets_served and certifications plus their evidence. Branch `agent/codex/markets-certs`; baseline `bd57a08`. First user: PIC supplier-matching staff; use review due 2026-12-15 (campaign T1 date; controller owns follow-up).

## Acceptance and result

Own-site statements only; corporate claims, no inferred ISO-to-market mapping. Markets use SCHEMA §3.3 / vocab.json exactly, automotive without OEM stays automotive_unspecified, medical without device stays medical_healthcare_general. Certifications follow owner 2026-11-01 R3c/R12: current edition named on current page, or current certificate; no expired/future certificate, edition-less claim or product-compliance claim. Four ISO9001:2015 candidates are held after the edition check (battery below). No other org column or existing evidence row changes; no tier change, record create, inclusion ruling, or registry link.

Unit/filter: all active organization rows on baseline, 4,884 (the brief's 4,893 denominator does not match this checked-out tree). Filled markets_served 394 → 405 (+11 organizations); certifications 47 → 52 (+5 organizations). 14 active organizations changed, all with a PIC-18 site; 55 market value fills and 5 certification fills, each with one evidence row: 60 appended, EVD-240000–240063 (four ISO9001 candidate IDs reserved and unused), OH (59) and WI (1) evidence shards. Changed organizations by unchanged verification tier: A 6 / B 8. counts.json records the initial before/after.

This is a bounded first PIC-18 batch, not completion of the 900+ PIC-18 backlog or the national gap. Lower-priority Tier-1/other Ohio/Pennsylvania phases were not reached. 24 active organizations were screened or followed up at own-site pages/certificates; 14 enriched, 10 without fills. One extra attempted cyplas.com address was a failed route, not attributed to an Atlas organization.

## Sources and holds

inputs.csv is the reviewed verdict packet: organization, field, exact value, public own-site URL, raw quote, verdict, certification expiry when shown. No private/CRM/licensed material. The held company quality page links Design Molded Products LLC's Intertek CERT-0145662, at the matching two Bavaria Drive addresses; valid 2025-05-29 to 2028-06-01. This is certificate attribution, not an entity-name correction.

holds.csv is the holds table (18 claim/organization cases, STILL_UNCERTAIN, each naming the settling fact). Main holds: Ferriot certificate current cycle starts 2026-11-20 (future at observation; expiry 2029-09-30), CIMA ISO 9001:2000 obsolete and aspirational, retail/security/material-handling/communication/transportation markets ambiguous or off vocabulary, unavailable sites, and Ohio Precision Molding domain serving Design Molded content. Recommended reading for vocabulary holds: owner 2026-11-01 R2/R8, SCHEMA §3.3; retain holds until an explicit mapping or narrower evidence exists. No organization markets_other_note column exists, so no off-vocabulary notes written. Missing certifications on other worked organizations mean unfilled, never uncertified.

## Reproduction and checks

- `python3 tasks/markets-certs-2026-11-06/check.py`: 4/4 live known answers (CIMA markets, ESTERLE ISO, Hudson ISO, CIMA negative ISO2015); fabricated quote defect rejected 4/4. All 64 candidate quotes pass (60 VERIFIED, four ISO9001 holds); unavailable source fails loudly. Then fresh network retrieval of seeded random 30 **value rows**, seed 20261106: **0 raw quote errors**. audit30.csv records every sampled value. The sample is at value-row grain, not 30 distinct organizations, and measures quote support, not an independent human semantic audit.
- `python3 tasks/markets-certs-2026-11-06/build.py`: 60 evidence appends first run, zero second run; field union preserves existing tags. Evidence ID collision or altered pre-existing observation fails. All active/input/PIC-18/vocabulary/own-domain/unique-value conditions asserted. Only markets_served/certifications differ on 14 org rows; historical evidence unchanged. No new dependency.
- `python3 scripts/validate.py`: **OK — validation passed; 0 errors** (35,413 evidence rows total). Initial run caught B-strength activity evidence against five tier-A records (V-25); regenerated unpublished lane evidence with own_site's allowed supports_A strength. Existing evidence and org tiers untouched.

The named ownership-status-2 raw checker was absent. fetch.py reuses the existing evidence-repair-2 prep.W token normalization/contiguous-order matcher, with curl browser UA (compressed responses supported), Jina fallback and pdftotext for PDF. Parsed visible HTML text is matched, never a model summary. Known answers caught a gzip response issue before inputs were trusted. Fallback failure is availability only. Source snapshots were temporary; only public claim excerpts are committed. Network re-checks can later fail if a witness changes.

Rebase: restore fresh main's data/organizations_OH.csv and data/evidence_organizations_OH.csv, then rerun build.py and validate; never hand-merge CSV. Preserve this inputs.csv ordering because IDs derive from it. The branch base is the pre-pass backup.

## Coordination and review

Controller notified via bb thread tell and shared BOARD: ownership-status-2 checker absent, repair-2 matcher reused; two-column scope and ID block unchanged. Controller confirmed the ISO transition hold and requested battery recommendation (a); recorded below. No files owned by L4/L9 beyond the two explicitly delegated columns were changed. Controller alone merges/statuses tasks.

Reviews pending on the final packet via controller-designated Codex/Grok refute clerks (05:55 BOARD direction supersedes council-only/before-PR gate; draft PR may precede review). Initial council reviews targeted an earlier packet and are not final approval.


Accepted certification details: Denney NSF-ISR C0588169-AS2 AS9100D expires 2027-09-09; Paramont Amtivo264532 AS9100D expires 2027-01-16; STERIS BSI FM75837 ISO13485:2016 expires 2027-12-18; US Endoscopy BSI FM75888 expires 2027-12-21; Flambeau Sharon Center ABS38565.E/IATF0555367 IATF16949:2016 expires 2027-11-17. Each quote comes from the company-hosted original PDF. Certificate coverage is limited to its named entity/sites/scope, as recorded in evidence notes. ISO9001 components on joint certificates are not filled. ISO13485:2016 current status confirmed at https://www.iso.org/standard/59752.html.

## Owner battery item B-L10-ISO-TRANSITION — HOLD

Question: does R3c's bar on a superseded edition also bar an otherwise current, unexpired certificate during the official accreditation transition window?

Facts checked 2026-11-06: [ISO's standard record](https://www.iso.org/standard/62085.html) marks ISO9001:2015 withdrawn 2026-09-16, replaced by ISO9001:2026. [ISO's transition explainer](https://www.iso.org/quality-management/iso-9001-2026) states a three-year transition for existing certificate holders. The [Dutch national accreditation body's 2026-10-27 notice](https://www.rva.nl/en/nieuws/transistion-iso-9001/) attributes the policy to GLOBAL ACI (the IAF successor), specifies 36 months, final certificate-holder deadline 2029-09-30 and last initial/recertification audits against 2015/AMD1 on 2028-03-31. The original Global ACI/IAF policy PDF was not directly retrieved; this is the accreditation body's first-party published implementation, not an inferred deadline. These normative sources are battery context, never own-site evidence for any organization's certification.

Recommendation (a), requested by controller: a certificate of a superseded edition stays recordable while unexpired and within the published IAF/Global ACI transition window, with edition and expiry in its evidence note; use the earlier of printed expiry and transition deadline. An undated logo/current page alone would not establish certificate validity within that exception. Keep four ISO9001:2015 candidate fills held until the owner rules; no existing certifications changed. Ferriot additionally has a future cycle start; that requires a currently effective certificate irrespective of the transition ruling. Controller message explicitly confirmed this interpretation is an owner ruling (AGENTS §2 rule 9), not a lane decision.

shard_io.append_sorted also restores ascending order of 17 existing Wisconsin evidence rows; their field values are byte-for-byte equivalent after CSV parsing. No historical evidence observation is edited.
