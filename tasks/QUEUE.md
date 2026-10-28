# Task queue — claim before you build (AGENTS.md §2)

Status values: `open` · `claimed:<agent-or-name> <YYYY-MM-DD>` · `in-pr:<link>` · `done`

## Phase 0 — Foundations
- [ ] `open` Rule on docs/OPEN_ISSUES.md items 1–2 (GEON parent ruling; PIC-12 vs 19-county canonical geography) — OWNER ONLY (John)
- [ ] `open` Fold scoping reports (source/count reconciliation, Summit pilot) into docs/ after coordinator synthesis
- [ ] `open` Add tombstone parent record: Chromaflo Technologies → successor Vibrantz (ORG-000007)

## Phase 1 — PIC-12 core (Rings 1–2)
- [ ] `open` Summit County: convert the ~99-candidate pilot list to tiered records (staging = tier U/C, promote on verification)
- [ ] `open` Cuyahoga County candidate harvest (same multi-source method as Summit pilot)
- [x] `done 2026-10-28` Plastics News account audit (final): free registered account ("Greater Akron Chamber GAC", no subscription). Per-list audit of all 27 Data Center items: 15 lists RENDER FULLY for viewing (injection 612 records, 6-processor index 1,310, thermoformers 204, pipe/profile 198, compounders 196, recyclers 184, film/sheet 174, blow 101, roto 103, LSR 75, associations 224, family-owned 175) with pagination + company search. Downloads still require All Access ($499/yr); tables show HQ location + plant counts, not plant addresses. Mold/Tool Makers list (433) is BROKEN ("LIST UNAVAILABLE"), 11 items are download-only snapshots. First-pass "fully paywalled" verdict was a load-timing error (JS tables), corrected same day — full matrix in staging plastics-news-access-audit.md. All Access decision: DEFERRED (view access + Data Axle spine cover Phase 1; revisit only if plant-address Excel files are needed)
- [ ] `open` Plastics News rankings pull — Ohio processors (DISCOVERY ONLY per AGENTS.md §5: verify each against primary/public source before any row ships)
- [ ] `open` Ask JobsOhio / Shale Crescent USA for their cleaned 616-company Ohio dataset (documented 326199 definition) — costs one email; draft for John's approval before sending
- [ ] `open` Library spine pull: Data Axle Reference Solutions via Cleveland Public Library / Cuyahoga County PL card (250-record download cap per search — batch by NAICS x county). Akron-Summit PL carries AtoZ Databases instead
- [ ] `open` Rubber: Rubber News is a SEPARATE Crain subscription (no evidence John's Plastics News login bundles it) and has no equivalent downloadable data center — rubber (NAICS 3262) is the thinnest segment; use ACS Rubber Division + Ohio Rubber Group + Thomasnet + QCEW denominators
- [ ] `open` Sites pass for seed orgs: full site lists with street addresses for the 9 seeded parents

## Phase 2 — Rest of Ohio (Rings 1–2), then Ring 3 statewide
- [ ] `open` County-by-county harvest, benchmarked against Census CBP / BLS QCEW establishment counts per NAICS per county (coverage audit: found ÷ expected)

## Phase 3 — Ecosystem (Ring 5) + Ring 4 test pass
- [ ] `open` Universities/CTE/workforce, associations, EDOs for PIC-12, then Ohio
- [ ] `open` Ring 4 candidates: apply the 2-of-3 test, log every decision in inclusion_log.csv

## Phase 4 — National tiers
- [ ] `open` National associations, materials/OEM ultimate parents of Ohio subsidiaries, majors — Parents only, no national site sweep in v1

## Standing — maintenance swarms
- [ ] `open` Weekly signals sweep (news, WARN notices, Ohio SOS new filings, JobsOhio/Team NEO announcements) → propose record changes as PRs
- [ ] `open` Quarterly re-verification rotation: oldest last_verified records first
