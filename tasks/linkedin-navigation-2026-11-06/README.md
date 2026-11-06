# LinkedIn navigation — 2026-11-06

Controller-assigned branch agent/codex/linkedin-navigation, accepted SPEC before fetching. SCHEMA4.4/v1.11/B-LINKEDIN and V58 permit a navigation link only. Only blank organizations.linkedin_url cells change. Zero record creates, zero evidence rows, no IDs; no status/tier/website/monitoring or other-field changes. Explicit no-EVD/no-LinkedIn-fetch instruction governs this pass over the general evidence contract.

## Frame, result and provenance

Frozen inputs.csv contains2,061distinct held organization rows:1,299with nonblank tier1_qualifier first, then762additional organizations with at least one active Ohio site in house regions.PIC18. This includes all rings, not just R1–2. Ten non-active organization rows are held; the frame is not a statement that all2,061are currently operating. All navigation cells were blank. Input row names/aliases/sites are already public Atlas records; no CRM, private worksheet, licensed source or outreach data was used.

345navigation cells on40organization shards are verified:245Tier1/100PIC18remainder. Frozen verification tiers of changed organization rows:136A/180B/28C/1U; tiers themselves do not change.1,716frame organization rows remain STILL_UNCERTAIN. This is a count of navigation cells/organization rows, never companies reached or operational impact.

Discovery covered all1,708eligible distinct own-site URLs, in Tier1-first phases:1,285HTTP200and423unavailable/blocked/other-status outcomes.2,214logged HTTPrequests include same-domain redirects. No external redirect destination was requested; explicit redirects to LinkedIn stop before the request. No LinkedIn page was fetched, scraped, used as evidence or designated for monitoring. Site scripts/assets/linked pages are not fetched by curl. Header/footer company anchors appeared on536pages after parsing correction; only one unique company URL plus exact held-name/trade-name slug and unique held domain can pass. The other188one-link pages need a name/alias bridge; multiple candidates/none are held. All345candidates were independently re-fetched from their own source pages,345PASS/0FAIL with exact published href/canonical company link in a header/footer; raw-outcomes.csv/rawcheck.csv/raw-requests.json contain the full census and source digests, no skipped candidates.

The source is each held website, not LinkedIn. proposals.csv carries the source/final own URL, exact href, header/footer location, observed date and canonical navigation link. Query/fragment tracking and localized LinkedIn hostnames normalize to www/company/slug/; the slug is preserved. Only declared V58 company-page shapes are allowed; personal/share URLs, unsafe hosts/schemes and encoded dot segments fail. The house atlas.name_key supplies the conservative exact legal/trade-name comparison (spaces/hyphens/punctuation and legal suffixes); no fuzzy match or parent substitution. All held organization and ecosystem domains participate in ambiguity screening; even an apparent self-link is held when another held entity shares the domain. Existing parent/alias fields are not changed.

## Holds and availability

Every frame org has one verdict, with its own settling fact in verdicts.csv. Counts are disjoint final frame outcomes:

| Reason | Held organization rows |
|---|---:|
| Own route unavailable/non200, unsafe/external redirect or redirect budget | 423 |
| No single recognized own header/footer company link | 752 |
| Published slug needs exact held legal/trade-name bridge | 188 |
| Multiple held entities share website domain | 98 |
| Non-active frozen organization status | 10 |
| No held own website | 245 |
| Total | 1716 |

Failed fetches and missing recognized anchors never establish absence, closure or lack of a LinkedIn page. discovery.json lists every attempted own URL/status and safe request chain, including blockers. No fallback reader was admitted: extracted main-content text cannot prove a header/footer anchor. Physical availability, a live LinkedIn destination, legal ownership changes or completeness beyond this frozen frame are not inferred. Holds are research dispositions, not new owner rulings.

## Calibration and corrections

Before bulk matching, manually read literal own-site anchors for Avient Corporation, RTP Company and Avery Dennison; expected company slugs avient-corporation/rtp-company/avery-dennison. self_check.py re-fetches these three own pages and requires exact extraction3/3. known-answers.json records source/final URLs, expected canonical values, locations and raw digests. Personal/share/body-only/encoded-dot/unsafeURL tests reject; mocked direct and redirected LinkedIn routes prove zero LinkedIn subprocess requests.

One live empty-href attribute stopped the first parser after94persisted URL outcomes. Normalize valueless HTML attributes to empty strings; resume preserves completed outcomes. The94-row checkpoint's literal newline trailer was repaired without dropping any row. Some queued requests had completed before the exception; their raw caches were not admitted without a successful outcome and were fetched again. Thus2,214is the successful final discovery log's request count, not total network cost including the interrupted attempt/calibration/raw pass. No whole-run time/cost claim is made.

A second adversarial check found global body classes such as theme-header-footer could falsely classify body content. Only actual header/footer or container tags (div/section/nav/aside/ul/li) carrying section markers now qualify; body/html/main/article are excluded as class markers. Every1285HTTP200snapshot was re-parsed from its digest-verified cache before classification;0missing/changed caches,536pages with anchors versus540before. The raw345/345pass uses the corrected parser. Empty-href and global-body-class regressions are permanent. Downloaded HTML stays uncommitted under build/linkedin-navigation/raw because it can include personal contacts; no such content is copied into the task packet.

## Reproduction and gates

Input frame is frozen at frame-base.txt. base.txt pins the canonical integration snapshot used by check.py. Regenerate discovery with python3 tasks/linkedin-navigation-2026-11-06/discover.py; classified discovery.json is a finite outcome packet, not silent success on unavailable pages. classify.py binds exact identity; rawcheck.py freshly checks every proposed value and moves failed candidates to held outcomes. Re-running research can change results and must be reviewed; it is not the idempotent data replay.

Apply packet with python3 tasks/linkedin-navigation-2026-11-06/build.py --apply. It preflights every held org, frozen identity/website, own source/final URL, unique domain, exact slug bridge, safe href, header/footer/raw witness and blank-or-exact value before any write. No ID append occurs. Replaying on applied data produces0changes.

Named check: python3 tasks/linkedin-navigation-2026-11-06/check.py. It reconciles all2061verdicts,1708URLs/own-only request chains,345fresh raw witnesses, exact345-cell projection on40shards versus immutable main, all other canonical bytes/keys/fields unchanged, zero-change replay and3negative controls. CLI conflicting existing navigation and changed held entity each fail before any CSV write; poisoned company identity also refuses. Check logs, validator0 and native row-loss guardPASS are retained. Production scripts/ are untouched, so full scripts pytest is not repeated.

First user: PIC staff using the public dataset to navigate organization profiles. Non-use review2026-12-06; no usage/deployment claim. Codex+Grok deep adversarial refutes pending; draft until both approve. No LinkedIn destination check, browser/JS-only footer inventory, hosted deployment or complete nationwide org census was performed.
