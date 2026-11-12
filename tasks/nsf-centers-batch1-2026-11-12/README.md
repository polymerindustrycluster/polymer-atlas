# Wave 3 — NSF centers verification batch 1 (2026-11-12)

**Packet only.** No repo data was edited and nothing was pushed. Input worklist:
`working/discovery-scan-nsf-centers-2026-11-12.md` (discovery only — NSF award
records were treated as discovery context throughout and verify nothing here).
Atlas state checked against `~/workspace/atlas-p2-2026-11-12/data/`
(== main `f2c7c814`). Grain precedent: BioPACIFIC MIP, PROG-000071
(center row on the host institution, partners in the description, level `none`,
tier B). Depth cells drafted using only SCHEMA §3 vocabulary (§3.1 processes /
§3.2 materials / §3.5 research-area supplement; characterization fills neither
specialty field; `scale_band` left blank for every center — the v1.13
enrollment rule has no application to centers).

## Counts

Unit = one candidate center from the batch-1 scope in
`working/wave3-batch-plan-2026-11-12.md`; filter = the 10 named centers.

| Verdict | Count |
|---|---|
| Centres in scope | 10 |
| **VERIFIED** (proposed row in `proposed_rows.csv`) | **8** |
| REJECT | 0 |
| **STILL_UNCERTAIN** | **2** |
| Proposed rows written | 8 (one carries an institution-row blocker — CHARM) |

## Verdicts

| # | Center (host) | Verdict | Basis in one line |
|---|---|---|---|
| 1 | UCSB Materials Research Laboratory — MRSEC (UC Santa Barbara, ORG-002854) | **VERIFIED** | MRL's own research page lists IRG-1 "Electrostatically Mediated Polymer Processing" and IRG-2 "Bioinspired Plasticity" (hydrogel networks). Strongest row in the batch. |
| 2 | Princeton Center for Complex Materials — PCCM (Princeton) | **STILL_UNCERTAIN** | Rotated: the center's own 2026–2032 program is IRG-1 quantum materials + IRG-2 biomolecular condensates; no polymer research line is stated in the current program. Settling fact below. Also: Princeton has no ecosystem row (see gaps). |
| 3 | Brandeis MRSEC — Bioinspired Soft Materials (Brandeis, ORG-004753) | **VERIFIED** | Center pages name IRG 1 Self-Limiting Assembly + IRG 2 Soft Active Materials; the IRG-2 program text integrates active units into "viscoelastic polymeric fluids". Thinnest polymer wording of the verified MRSECs (weakest links). |
| 4 | University of Chicago MRSEC (UChicago, ORG-004660) | **VERIFIED** | IRG 1 (de Pablo / Rowan / Jaeger) produces liquid-crystalline-elastomer particle suspensions with tunable shape memory — `liquid_crystals` drafted per the v1.13 S1 dual-listing. |
| 5 | Harvard MRSEC (Harvard, ORG-004653) | **VERIFIED** | Center homepage: soft-matter center under NSF Award #2614298 (2026 renewal captured on the site itself); IRG II is architected microgels and vesicles for biotechnology. |
| 6 | Center for Complex and Active Materials — CCAM (UC Irvine, ORG-004722) | **STILL_UNCERTAIN** | Thin on its own pages: CCAM's published research areas are complex concentrated metals/ceramics and supramolecular "living" materials; no polymer system is named. Settling fact below. |
| 7 | Center for Hybrid, Active, and Responsive Materials — CHARM (U Delaware) | **VERIFIED — institution row required first** | Center site (mrsec.udel.edu) names IRG 1 Peptide Active Materials / IRG 2 Hybrid Quantum Materials; UD's MSE page names CHARM as "the new NSF MRSEC at UD". Host is absent from the Atlas ecosystem (see gaps). |
| 8 | MONET — CCI Phase II (Duke, ORG-004691) | **VERIFIED** | Duke institutional pages + the NSF CCI directory: a Duke-led center on "the science of polymer networks", $19.8M new Phase II. Center's own domain did not resolve from this lane (availability only). |
| 9 | Center for Sustainable Polymers — CSP, CCI (U Minnesota, ORG-002855) | **VERIFIED** | The center's live site is polymer through-and-through ("transforms how plastics are made, unmade, and remade"). Status drafting note below — CCI funding period has closed, center continues. |
| 10 | TARDISS — ERC (lead: NC State, ORG-002851) | **VERIFIED** | Lead discrepancy settled for NC State from the center's own site (next section). |

### STILL_UNCERTAIN — settling facts

- **PCCM (Princeton):** a PCCM page for the 2026–2032 program (research or
  investigator pages) that scopes synthetic-polymer research as a center
  activity — the copolymer work of the Register/Priestley groups is the
  candidate fact — rather than the condensates-only framing the homepage and
  the Princeton Engineering announcement currently publish. Until then this is
  the MIT-MRSEC / Penn State CNS pattern: a formerly polymer-central center
  whose current program has rotated, and the honest entry is no row yet.
- **CCAM (UC Irvine):** a CCAM research/IRG page naming polymer systems
  (e.g. responsive or self-assembling polymers) as a research line. The
  discovery scan's "responsive polymer systems" phrasing is not borne out by
  the center's own current pages.

## TARDISS lead settlement

**Settled: North Carolina State University is the lead/host, on the center's
own presentation.** Evidence, all from `tardiss.ncsu.edu` itself: the site is
hosted on the NC State domain; it gives the center's address as the Department
of Chemical and Biomolecular Engineering, 911 Partners Way, EB-1, Raleigh, NC;
and its funding line reads "supported by the U.S. National Science Foundation
under Cooperative Agreements No. 2330145 and 2630557". This agrees with the
NSF award record for 2630557 (NC State awardee, PI McKenna) and NSF's ERC
page. Ohio State — named as lead in the August 2024 announcement coverage —
appears in the partner set (Caltech, Ohio State, Texas Tech, UC Merced). The
2024 press framing is superseded; the proposed row is drafted on ORG-002851
with the full center name. Note the center site publishes *two* cooperative
agreement numbers (2330145 and 2630557); both are quoted verbatim in the row's
notes rather than silently choosing one.

## Institution gaps (flagged, not drafted)

- **University of Delaware** — absent from `data/ecosystem.csv` (confirmed by
  name grep). CHARM's proposed row cannot land until an institution row
  exists; its `institution_org_id` in `proposed_rows.csv` is the placeholder
  `TBD-UD-INSTITUTION-ROW-REQUIRED`.
- **Princeton University** — also absent from `data/ecosystem.csv` (the scan
  named no ORG id for Princeton, correctly). PCCM is STILL_UNCERTAIN on scope
  grounds anyway, but any future row needs the institution row first.

All eight other batch hosts are present in the ecosystem (UCSB ORG-002854,
UMN ORG-002855, Brandeis ORG-004753, UChicago ORG-004660, Harvard ORG-004653,
UCI ORG-004722, NC State ORG-002851, Duke ORG-004691), and none of the ten
centers is carried in `programs.csv` under any name — the carried rows at
these hosts are other programs (BioPACIFIC at UCSB; IPRIME + MSE at UMN;
PCC/MSE/FPS degrees at NC State; an MSME degree at Harvard; a Polymer Science
and Engineering MEng-track degree at UChicago).

## Status and coordination notes

- **CSP status:** drafted `active` because the center's own site presents
  continuing work, but its NSF CCI support ran 2011–2024 per the center's own
  history (scan: Phase II 1901635 ended 07/2025). If the owner prefers rows to
  follow the funding period, this is the row to flip — flagged here rather
  than decided in the lane.
- **Minnesota lane coordination:** the wave-3 Minnesota lane packet did not
  exist in `working/wave3-2026-11-12/` when this packet closed, so nothing
  was taken from it and nothing here waits on it. CSP facts are independent
  of that lane's IPRIME/MSE scope; the integrator should still read the two
  packets side by side before the Minnesota/CSP integration, since both touch
  ORG-002855.
- **Naming:** UCI's center name (CCAM) comes from the center site / mrsec.org,
  not the NSF award title, per the scan's flag 3. Harvard and Princeton rows
  would cite the 2026-class renewal awards visible on the centers' own sites
  (Harvard #2614298; PCCM DMR-2614599) — quoted in notes where relevant, not
  used as verification.

## Weakest links in this packet

1. **UChicago** — the center's own homepage is generic; the polymer witness
   leans on the MRSEC program's highlight page (mrsec.org) describing IRG 1's
   LCE work. Solid, but one notch below a center-site research page.
2. **Brandeis** — verified on genuinely thin polymer wording ("viscoelastic
   polymeric fluids" inside an active-matter IRG). If the integrator wants a
   second witness, the center's research-highlights pages are the place.
3. **MONET** — monet.duke.edu did not resolve from this lane; the row rests on
   Duke institutional pages + the NSF CCI directory (which publishes that URL
   as the center's). A center-site read-back at integration is recommended.
4. **CHARM** — charm.udel.edu failed DNS from this lane; mrsec.udel.edu (the
   center site on the UD domain) carried the witness instead. Both failures
   were treated as availability signals, never as absence.

## Fetch log / cost

Free routes only; **paid calls: 0**. Fetches per center ≤6 (cap): UCSB MRL 2
(center home + research page via search result), PCCM 2 (home + renewal
coverage incl. the center's own 2026–2032 research page), Brandeis 2,
UChicago 2, Harvard 2 (home + IRG II page), CCAM 1, CHARM 2 (failed DNS on
the scan's URL; center site via search), MONET 2 (failed resolve on the
center domain; Duke + CCI directory pages), CSP 1, TARDISS 1. Plus one local
data pass over `programs.csv` / `ecosystem.csv`.

## Integration record (integrator of record, 2026-11-12)

**Applied** on branch `agent/spaghetti/wave3-nsf-centers-batch1` from
origin/main `2443c84` (Penn College PR #290 head; build only — not
pushed; PR follows the standing batched-approval pattern).
Build script: `~/workspace/atlas-resync-2026-11-10/build_nsfcenters_wave3.py`;
pre-pass backups: `~/workspace/atlas-wave3-nsfcenters-backups-2026-11-12/`.

- **Program rows created (6 of the packet's 8 VERIFIED)** — the packet's
  `proposed_rows.csv` applied verbatim (witness/verdict columns dropped)
  with allocated IDs, in packet order among the created six:
  **PROG-000310** Materials Research Laboratory (UCSB MRSEC), UCSB
  ORG-002854; **PROG-000311** University of Chicago MRSEC, ORG-004660;
  **PROG-000312** Harvard MRSEC, ORG-004653; **PROG-000313** Brandeis
  MRSEC, ORG-004753; **PROG-000314** Center for the Chemistry of
  Molecularly Optimized Networks (MONET), Duke ORG-004691;
  **PROG-000315** Transformation of American Rubber through Domestic
  Innovation for Supply Security (TARDISS), NC State ORG-002851 — the
  center's own funding line quotes both NSF Cooperative Agreements
  No. 2330145 and 2630557 (carried in the row notes and in evidence
  row EVD-333756); Ohio State is recorded as a partner, not the anchor.
  All six are `center`, level `none`, tier B, on the BioPACIFIC
  (PROG-000071) grain. Allocation note: this tree's scan shows max
  PROG-000308 on main; PROG-000309 was taken by the Pittsburg State
  unit ahead of this one in merge order, so this unit allocates
  310–315.
- **Evidence minted (12 rows)** — programs EVD-333746..EVD-333757,
  existence + scope per created row, `tier_effect=supports_B` from the
  rows' tier B. Source classes as observed: `own_site` where the
  packet's witness is the center's or host institution's own pages;
  `directory` for the two scope rows whose polymer witness sits on a
  program directory rather than the center's own domain — UChicago
  (NSF MRSEC program highlight page, mrsec.org) and MONET (NSF CCI
  program directory; the center's own domain did not resolve from the
  packet lane, an availability signal only). Allocation starts at
  EVD-333746 per the serial sequence — preceding wave-3 units consumed
  EVD-333539..EVD-333745 on their own branches (this tree's scan max is
  EVD-333710; the gap does not exist on this branch and was not
  backfilled). **Next free: PROG-000316 / EVD-333758.**
- **Ecosystem rollups (V-16) recomputed for all six hosts** in the same
  pass (sort: program-type precedence degree < center < …, then name):
  ORG-002854 name "BioPACIFIC MIP" → "BioPACIFIC MIP; Materials
  Research Laboratory (UCSB MRSEC)", URL unchanged
  (https://biopacificmip.org/); ORG-004660 name gains "; University of
  Chicago Materials Research Science and Engineering Center (MRSEC)",
  URL unchanged (the degree row still sorts first); ORG-004653 name
  gains "; Harvard Materials Research Science and Engineering Center
  (MRSEC)", URL unchanged; ORG-004753 `polymer_program` false → true,
  name (blank) → "Brandeis Materials Research Science and Engineering
  Center (MRSEC)", URL → https://www.brandeis.edu/mrsec/;
  ORG-004691 `polymer_program` false → true, name (blank) → "Center
  for the Chemistry of Molecularly Optimized Networks (MONET)", URL →
  https://monet.duke.edu/; ORG-002851 name gains "; Transformation of
  American Rubber through Domestic Innovation for Supply Security
  (TARDISS)", URL unchanged. `last_verified` → 2026-11-12 on the six
  rows; no other ecosystem field or row changed.
- **HELD for the owner battery (2 of the packet's 8 VERIFIED — drafted
  rows preserved in `proposed_rows.csv` as authored):** CHARM
  (University of Delaware) — the host is organizations-layer only
  (ORG-003896) with no ecosystem row, so the row's institution
  mechanics are an owner decision; the packet's placeholder
  `institution_org_id` was NOT landed. CSP (U Minnesota ORG-002855) —
  status decision: the packet drafts `active` on the center's own
  continuing presentation, but its NSF CCI support is dated 2011–2024
  (Phase II 1901635 ended 07/2025); which convention governs is the
  owner's call. Minnesota's banked Hillmyer–CSP affiliation stays
  unminted — no CSP row exists.
- **STILL_UNCERTAIN (2) — no rows, no evidence:** Princeton PCCM
  (current 2026–2032 program names no polymer line; Princeton also has
  no ecosystem row) and UC Irvine CCAM (own pages name no polymer
  system). Settling facts stand in the packet README above.
- **No people records or links** in this unit; center rosters are a
  later pass.
- **QUEUE:** the Penn College claim (the one straggler standing
  `claimed` on this main) flipped to `done 2026-11-12 (PR #290,
  merged)`; this unit's claim added after it. All other prior wave-3
  claims already stood done (PRs #283–#289).
