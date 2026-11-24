# Repair site NAICS from bound establishment filings

Builder family — OpenAI Codex. Queue claim — atlas-p1-filing-repairs, 2026-11-24. Base commit — `27fae8f2811fe1ddb3251bd4c56fdc0970a61595`.

The November 24 census screened every establishment, all statuses. Replaying the specified conflict reason at this base returned 252 candidate sites, including 14 in PIC-18. Of those, 127 sites received a correction, 19 retained a confirmed value, and 106 were held. 8 corrected sites are in PIC-18.

Corrected site cells by field — 72 naics_confidence, 127 naics_primary, 21 naics_primary_source_type. Corrected sites by held verification tier — A 4, B 16, C 101, U 6. Added 0 site size evidence rows. All site row counts and verification tiers reconcile to the base. Each hold and its reason are recorded by site ID in `packet.json`. No inclusion decisions were made.

The packet compares primary NAICS at establishment grain. A correction requires a cited filing, an establishment-name and street match, equal unit designators, and agreement among binding filing codes in the comparison. OSHA ITA codes receive medium confidence. Direct inspection and TRI codes receive high confidence. Site shards have no source-name column. The packet preserves each deciding locator.

Source files and SHA-256 digests are in `INPUTS.sha256`, relative to `ATLAS_STORE`. The committed inspection spine screens candidates. Each proposed value is replayed from the original store filing. The bounds of the census are the cited ITA/inspection/TRI filings in the specified snapshot.
