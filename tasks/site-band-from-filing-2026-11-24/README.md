# Repair site employee band from bound establishment filings

Builder family — OpenAI Codex. Queue claim — atlas-p1-filing-repairs, 2026-11-24. Base commit — `27fae8f2811fe1ddb3251bd4c56fdc0970a61595`.

The November 24 census screened every establishment, all statuses. Replaying the specified conflict reason at this base returned 24 candidate sites, including 3 in PIC-18. Of those, 12 sites received a correction, 1 retained a confirmed value, and 11 were held. 1 corrected sites are in PIC-18.

Corrected site cells by field — 12 employee_band_site, 12 notes. Corrected sites by held verification tier — A 3, B 7, C 2. Added 12 site size evidence rows. All site row counts and verification tiers reconcile to the base. Each hold and its reason are recorded by site ID in `packet.json`. No inclusion decisions were made.

The packet selects a positive employee count from the latest binding ITA or inspection filing within ten years. A same-date disagreement that would change the held band stays unresolved. Each correction replaces the dated BAND-SOURCE segment and appends dated size evidence. Plan participant counts are outside the frame.

Source files and SHA-256 digests are in `INPUTS.sha256`, relative to `ATLAS_STORE`. The committed inspection spine screens candidates. Each proposed value is replayed from the original store filing. The bounds of the census are the cited ITA/inspection filings in the specified snapshot.
