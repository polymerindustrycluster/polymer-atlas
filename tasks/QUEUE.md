# Task queue — claim before you build (AGENTS.md §2)

Status values: `open` · `claimed:<agent-or-name> <YYYY-MM-DD>` · `in-pr:<link>` · `blocked <YYYY-MM-DD>` · `done`

## Phase 0 — Foundations
- [x] `done 2026-10-28` GEON parent ruling (OPEN_ISSUES item 1): John ruled GEON is its own company (ORG-000010, HQ Westlake, ultimate parent SK Capital Partners); docs/SCHEMA.md §5.2 updated, item resolved
- [ ] `open` PIC-12 vs 19-county canonical geography (OPEN_ISSUES item 2) — OWNER ONLY (John); county stored on every record meanwhile, region applied at report time (AGENTS.md §8)
- [x] `done 2026-10-28` Fold scoping reports (source/count reconciliation, Summit pilot) into docs/ after coordinator synthesis — live as docs/SOURCE_COUNT_RECONCILIATION.md and docs/SUMMIT_COUNTY_PILOT.md
- [ ] `open` Add tombstone parent record: Chromaflo Technologies → successor Vibrantz (ORG-000007)

## Phase 1 — PIC-12 core (Rings 1–2)
- [x] `done 2026-10-28` Summit County: convert the ~99-candidate pilot list to tiered records (staging = tier U/C, promote on verification) — 94 organizations converted (ORG-000011–ORG-000104, incl. OMNOVA tombstone), promoted to repo
- [x] `done 2026-10-28` Cuyahoga County candidate harvest (same multi-source method as Summit pilot) — 73 candidates; 62 new organizations converted (ORG-000105–ORG-000166) plus sites under seeded/staged parents, promoted to repo
- [x] `done 2026-10-28` Rubber PIC-12 harvest + conversion (ACS Rubber Division / Ohio Rubber Group / Thomasnet) — 37 organizations (ORG-000167–ORG-000203, incl. Eliokem tombstone) + 41 sites, promoted to repo
- [x] `done 2026-10-28` Staging→repo promotion + ecosystem seed ID renumber (ORG-000101–103 → ORG-000501–503) — repo data files hold 189 organizations / 218 sites / 18 ecosystem / 10 inclusion-log rows, scripts/validate.py passing, remote read-back verified identical to local
- [x] `done 2026-10-28` Grok team Ohio list received + reconciled vs repo; PIC-12 verified batch converted to staging — 433 organizations / 467 sites (ORG-000206–ORG-000641, tiers C 188 / U 245 orgs) in staging grok-pic12/, staging only, awaiting verification wave 2
- [x] `done 2026-10-28` Plastics News account audit (final): free registered account ("Greater Akron Chamber GAC", no subscription). Per-list audit of all 27 Data Center items: 15 lists RENDER FULLY for viewing (injection 612 records, 6-processor index 1,310, thermoformers 204, pipe/profile 198, compounders 196, recyclers 184, film/sheet 174, blow 101, roto 103, LSR 75, associations 224, family-owned 175) with pagination + company search. Downloads still require All Access ($499/yr); tables show HQ location + plant counts, not plant addresses. Mold/Tool Makers list (433) is BROKEN ("LIST UNAVAILABLE"), 11 items are download-only snapshots. First-pass "fully paywalled" verdict was a load-timing error (JS tables), corrected same day — full matrix in staging plastics-news-access-audit.md. All Access decision: DEFERRED (view access + Data Axle spine cover Phase 1; revisit only if plant-address Excel files are needed)
- [ ] `claimed:spaghetti 2026-10-28` Plastics News rankings pull — Ohio processors (DISCOVERY ONLY per AGENTS.md §5: verify each against primary/public source before any row ships) — IN PROGRESS: 6-Processor Index (list 993) 800/1,310 rows and Injection Molders (list 438) 400/612 rows transcribed to local staging raw (never committed); round 6 running; remaining rendering lists follow only after 993/438 reconcile to their stated totals
- [ ] `open` Ask JobsOhio / Shale Crescent USA for their cleaned 616-company Ohio dataset (documented 326199 definition) — costs one email; draft for John's approval before sending — DRAFT WRITTEN (to Nathan Lord, President, Shale Crescent USA); held for John's send approval 2026-10-28, nothing sent
- [ ] `blocked 2026-10-28` Library spine pull: Data Axle Reference Solutions via Cleveland Public Library / Cuyahoga County PL card (250-record download cap per search — batch by NAICS x county). Akron-Summit PL carries AtoZ Databases instead — BLOCKED: OPLIN suspended the Cleveland Public Library proxy profile ("temporarily suspended due to heavy usage") 12:52 PM 2026-10-28, still suspended at the 4:40 PM retry; zero counts/downloads obtained. Next levers (owner decision): wait for the suspension to lift, OPLIN support email, or an alternate library gateway
- [x] `done 2026-10-28` Verification wave 2 — Grok PIC-12 staging batch: name-variant sweep vs repo first (17 already-in-repo, DayGlo ORG-000298 dropped as duplicate of ORG-000005), then top-25 CLEAR slice verified (20 orgs Tier A, 4 B, Yokohama split into ORG-000638/ORG-001336 + Polychem Dispersions split out as ORG-001335) and promoted in batch 2 — 27 organizations / 45 sites to the repo (incl. 3 new Steere Enterprises Tallmadge sites from the packet); remainder of the batch stays staged for later slices
- [ ] `open` Hankook duplicate merge (ORG-000167 vs ORG-000204) — prepared fix, awaiting owner pick
- [x] `done 2026-10-28` Kenda ATC county parcel check — RESOLVED: Green, Summit County (Summit County Fiscal Office parcel 2900022, GREEN CITY tax district; Stark control search negative); correction applied to the repo at repo fix 2026-10-28 (SITE-000204 Green/Summit/44720, ORG-000197 tier B)
- [ ] `open` Promotion-carry: ORG-001087 Roppe Corp. parent_org_id → ORG-001088 Roppe Holding — child promoted in batch 2 with parent_org_id blanked (ultimate_parent_name preserved); set the link when ORG-001088 promotes
- [ ] `open` Promotion-carries from repo fix 2026-10-28, still open: Plast-O-Meric ORG-001025 → Avient ORG-000001; Citadel ORG-000735 → LyondellBasell ORG-000033; Permatex ORG-000138 → ITW ORG-000889 — set parent_org_id when the staged endpoint promotes
- [ ] `open` Owner confirmation: SITE-000589 (Röchling Industrial Cleveland) was promoted under ORG-000550 Röchling Automotive USA LLP per the dedupe audit merge — the two are distinct Röchling divisions; confirm at promotion review or unwind (see staging working/dedupe-application-log.md advisory)
- [ ] `open` Rubber: Rubber News is a SEPARATE Crain subscription (no evidence John's Plastics News login bundles it) and has no equivalent downloadable data center — rubber (NAICS 3262) is the thinnest segment; use ACS Rubber Division + Ohio Rubber Group + Thomasnet + QCEW denominators
- [ ] `open` Sites pass for seed orgs: full site lists with street addresses for the 9 seeded parents

## Phase 2 — Rest of Ohio (Rings 1–2), then Ring 3 statewide
- [ ] `open` County-by-county harvest, benchmarked against Census CBP / BLS QCEW establishment counts per NAICS per county (coverage audit: found ÷ expected)
- [ ] `claimed:spaghetti 2026-10-28` Grok rest-of-Ohio verified conversion to staging (642 verified rows / 589 parents not in the Atlas, from the Grok team's 2026-10-28 Ohio list)
- [ ] `claimed:spaghetti 2026-10-28` PIC-12 coverage audit vs QCEW/CBP denominators (staging working/denominators_pic12.csv; single-source QCEW benchmark: PIC-12 NAICS 326 = 353 establishments, 2023)
- [x] `done 2026-10-28` Verification wave 2 — Grok rest-of-Ohio staging batch, top-25 slice: 22 orgs Tier A / 3 B (incl. Haviland identity correction ORG-000819 and Elyria Plastic Products ORG-001379), promoted in batch 2 — 26 organizations / 42 sites to the repo; remainder of the batch stays staged for later slices

## Phase 3 — Ecosystem (Ring 5) + Ring 4 test pass
- [ ] `claimed:spaghetti 2026-10-28` Grok ecosystem conversion to staging (134 net-new statewide rows from the Grok list's ecosystem set, 48 of them in PIC-12)
- [x] `done 2026-10-28` Ecosystem named-program test + promotion: all 118 staged ecosystem records classified (27 PASS named-program, 87 generalist, 4 wrong-type); the 35 promote-ready records (26 named-program + 9 Ring 5 generalists) promoted to repo ecosystem.csv in batch 2 — watchlist (54), excluded (27), re-ring candidate ORG-001261, and duplicate-of-repo ORG-001302 stay staged
- [ ] `open` Universities/CTE/workforce, associations, EDOs for PIC-12, then Ohio
- [ ] `open` Ring 4 candidates: apply the 2-of-3 test, log every decision in inclusion_log.csv

## Phase 4 — National tiers
- [ ] `open` National associations, materials/OEM ultimate parents of Ohio subsidiaries, majors — Parents only, no national site sweep in v1

## Standing — maintenance swarms
- [ ] `open` Weekly signals sweep (news, WARN notices, Ohio SOS new filings, JobsOhio/Team NEO announcements) → propose record changes as PRs
- [ ] `open` Quarterly re-verification rotation: oldest last_verified records first
