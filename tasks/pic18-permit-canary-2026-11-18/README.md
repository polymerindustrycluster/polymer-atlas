# PIC-18 Ohio EPA air-permit process scout — packet only (0 data rows)

Claim: atlas-w18-permit, controller-assigned, 2026-11-18. Packet only: no data file, queue, validator or `tier1_qualifier*` change.

First user: the Atlas integrator, deciding at the W18 review whether to open a full permit lane. Non-use is a finding if that lane has not been opened or declined by the next wave review.

## Pre-registered criteria (written and committed before the canary draw)

Disclosure of order: the 58-site screen (ECHO air flag, Ohio EPA eDocument search) and two permit excerpts (one single-unit PTIO, one Banbury/calender PTIO) were read while designing the loop, before these criteria were committed. No canary site was drawn and no unit text was mapped before this commit.

**Question.** Do Ohio EPA air-permit documents, issued to PIC-18 plants whose Atlas `processes` is unknown, name a process in words that a §3.1 term matches without being broader than the words, and do they bind it to that establishment?

**Would show it (GO case).** A canary site counts as a **specific hit** when its permit text (a) is bound to the establishment (printed Facility ID, holder name and street/city all match the Atlas site; one AIR ID per site, else hold), and (b) has at least one emissions-unit heading or equipment description whose words are matched exactly by a §3.1 term that is *not* an `_unspecified` term and *not* ancillary equipment (boilers, generators, tanks, baghouses, paint booths and cleaning are ancillary and name no §3.1 process). An **any-term hit** also admits `_unspecified` terms (the NEI scout already reached those from SCCs, so the added value of permits is in specific-subtype terms).

**Would refute it (NO-GO case).** Most retrievable permits list only ancillary units, generic "process"/"line" headings with no equipment noun, or cannot be bound to the establishment.

**Thresholds, fixed now.**
- GO for a full permit lane: specific yield ≥ 5/10 **and** ≥ 25 of the 58 pool sites with a retrievable permit.
- NO-GO: specific yield ≤ 2/10 **or** < 15 of 58 retrievable.
- Otherwise GO-as-leads (held packets for integrator triage, no fill campaign).
- Projection over the 331 = (retrievable permit sites of 58) × (specific yield) with its Wilson 95% interval; sites outside the 58 (no FRS link, multi-site organizations) are unreachable by this route as built.

**Definitions.**
- *Air-program record*: ECHO exporter `AIR_FLAG = Y` for an FRS ID that is on the Atlas record for that site/organization, from the pinned exporter extract (`persist/oh-federal-rematch`, retrieved 2026-11-16).
- *Retrievable permit document*: a stored PDF fetched from Ohio EPA's eDocument public portal, with a text layer containing the printed Facility ID, classed as a final permit-to-install / PTIO / Title V permit (not a cover letter, correspondence or draft), with at least one emissions-unit term.
- *Per-site document rule*: newest-first, up to 6 non-draft documents, no stop at first hit; units are the union across final permits, newest permit wins per unit ID.
- *Current*: no later non-draft permit document for that facility is listed in the portal search at retrieval date; permit effective/issue date is recorded.
