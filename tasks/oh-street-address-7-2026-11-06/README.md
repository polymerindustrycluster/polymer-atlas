# Ohio street addresses round 7 — final A/B cohort, L2, 2026-11-06

Acceptance before fetch: controller-assigned original448frame positions361–448 only,88active stored-PIC18 A/B blank-street site rows.360prior+88worked+0future=448. EVD-152360–152447 are fixed frame-position reservations inside Ohio150000–154999; Pennsylvania155000–159999 remains separate. New branch agent/codex/oh-street-address-7 off current main (baseline.json). Integrator application delegation persists. This is the final new round; then only review fixes on156/192/207/208 and this batch.

Reuse corrected round-six own-site fetch/build/check/audit. Three LIVE known literal answers before selected88sourcefetch; wrongcity/PObox/phoneprefix, actualbymail/postal/email and ten notes/suite/unit/number fixtures. Five research pages per operator reserve one fresh source audit. Raw quotes must bind held operator host, physical street, recorded city and known ZIP; existing notes/site/unit/ZIP/mailing contradictions held. Sameoperatorcity/ZIP peers require site-specific street binding. Full88sourceyield/attempts/fetched/unavailable counts mandatory, unavailable never absence.

Only street_address/supporting sources on existing sites plus append-only own_site/address/supports_A evidence. No county/county_source/ZIP/coordinates/tier/status/ring/registry/derived edits; no entity creates/deletes/merges. county_source stays unchanged because street presence does not adjudicate county. No private/licensed/PIC CRM data. First user Atlas integrator, review2026-11-06; non-use finding2026-11-13.

Before readiness: check.py fieldboundary/byte-idempotence/street+globalEVD fail-beforewrite; seeded30freshaudit (census if fewer than30); validate0errors; mainkey/legacyEVD preservation and rowloss/diffcheck; two-family deep Codex+Grok refutes on shortest queues. Main conflict recipe is main's two Ohio data files plus builder replay, never handCSVmerge. Final outcomes/holds/checks will be appended after research; no completion claim.

Final cohort result: **88 site rows = 24 VERIFIED fills + 64 STILL_UNCERTAIN holds.** All24 fills are own_site/address/supports_A, record tiers unchanged A20/B4. Sparse fill IDs EVD-152361–152430 retain original frame positions. Active Ohio site rows with streets rise324/1,883(17.21%)→348/1,883(18.48%), excluding pending156/192/207/208. Research yield166attempts=134fetched+32unavailable, exactly88siteIDs,28raw-address sites. Holds:60no admissible raw block,1mailing context(Cosar),2notes/unit/other-plant conflicts(GuildSuite350,Hedstrom100HedstromDr vs2040Cellar),1multiple-own-streets plus notes(Smetzer's dedicated truck/retread location). All settling facts in holds.csv. No future original-frame rows remain unworked.

Controller ruling explicitly supersedes the initial street/sources-only boundary for **six notes flags**: apply four factual overlapping street fills and flag both records in each pair as possible co-location/duplicate, with other site_id and primary sources. No merge/site_group/status inference is authorized. Four existing fill evidence rows also cover their flag, plus controller-allocated EVD-152448/152449 cover two notes-only rows(R6SITE001721/001717). Total26append-only address evidence,26changed site records(24street fields and6notes fields, four overlap). note_flags.csv freezes the exact authorized note suffixes; unrelated note drift rejects before writes.

| Dedupe lead, owner reading only | Common published street | Primary witnesses |
|---|---|---|
| SITE-001858 AmericanSign / SITE-001904 Thermoprene |5718TransportationBlvd,GarfieldHeights|https://americansignproducts.com ; https://thermoprene.com|
| SITE-001882 Horsemen'sPride / SITE-001721 Tusco(round6) |10008StateRoute43,Streetsboro|https://horsemenspride.com ; http://www.tuscoproducts.com/|
| SITE-001924 ITPlastics / SITE-001717 Overmold(round6) |7675JentherDr,Mentor|http://www.itplastics.com/ ; https://www.overmoldexpress.com/|

Recommended reading: AGENTS§3 link-and-flag when uncertain and SCHEMA§4.5 multioperator campus. The controller accepted factual street fills; whether these are duplicate operators or distinct co-located establishments remains an owner dedupe lead. address_overlaps.csv records both sources and IDs. No new entity or site_group is created. **Merge #208 before this PR**, because its strict frozen-notes guard otherwise correctly refuses these later note additions; this builder preserves the two round6 street fields when present.

Named checks from repo root:

- fetch.py --known —3 LIVE literal addresses before scaling; wrongcity/PObox/phoneprefix cases. The unchanged fetcher covers all88IDs.
- check.py —PASS24fills/6authorized notes/26evidence;10notes grammar fixtures, ordinary Rte/Route and PARK/Pk aliases, different house/route numbers and units preserved, four genuine conflicts held. Field boundary, byte-idempotence, injected street and unrelated-note drift, both fill-ID and late notes-only foreign-ID collisions reject before any canonical write.
- audit.py —full accepted-population census:24/24street-fill witnesses plus2/2notes-only witnesses freshly fetched,0errors. Quote/city/held-host/non-mailing context checked. No30-row sample is possible because there are only24fills.
- validate.py —OK,0errors. Main-key/legacy-evidence comparison retains every baseline record and old EVD, with exactly24street fills/6notes changes/26EVD appends. git diff --check passes. No scripts/ edits.
- Original448identity/order/reserved slots checked against immutable reviewed171@7af4219; selected IDs exactlypositions361–448. Main419678b is mid controller-declared non-data deletion incident, so missing main task files do not imply absence. No merge of origin/main before restorationPR209; after restoration, replay on main and rerun native row-loss/validator guards.

The only new matching change in this batch is the literal Rte→Route abbreviation;2184StateRte43 matches2184StateRoute43 but notRoute44. Ten notes/provenance/suite fixtures from round6 are unchanged. No source qualifier or unit threshold was relaxed.

Pre-pass backups local/ignored; baseline/journal pin source main, fields, evidence IDs, counts and hashes. Deep Codex+Grok refutes remain pending. This final cohort ends new rounds; review fixes on156/192/207/208 and this PR remain owned.

Original A/B frame completion, unit:448 unique active blank-street site rows frozen after the first Ohio pass.

| Cohort | Site rows | VERIFIED | Holds |
|---|---:|---:|---:|
|PR156|60|19|41|
|Merged171|100|38|62|
|PR207|100|25|75|
|PR208|100|36|64|
|Final88|88|24|64|
|Total|448|142|306|

frame_completion.csv and frame_completion_summary.json reconcile exact IDs and source commits;0unworked. Only38fills are merged in this baseline;104 remain proposed across156/207/208/final88, with all reviews still respected. The separate40-row C/U packet192 is outside this A/B frame.

Pre-restoration row-loss check: PASS at HEAD66cc2d7 against explicit419678b2e3e415194dad804af8daca649b163f3e, using the unchanged house scripts/check_row_loss.py from round6's branch. Since the incident removed that script from this branch, it was executed with __file__ bound to this worktree's scripts/check_row_loss.py (ROOT=this cwd), not /tmp. Native guard must be rerun after209restores main; no pre-restoration result is presented as a native-file run.

Restoration209 merged before any main merge here. Then main merged (parent 1e5834394f592f7237a5919500d9fbd5f2c48ad5) and main's Ohio files were taken/replayed. All26 changed-record values and26 EVD rows remain identical to ff0f9d1; all main keys/legacy EVD survive exactly. Native scripts/check_row_loss.py --base origin/main --head HEAD PASS, check24/6notes/26EVD PASS, validator0errors. Main data comparison pin 4ea5659562be6f267d84c450f3c9fb133ff61fe2; coverage remains324→348/1883. This supersedes the earlier native-guard deferral, not the pending independent reviews.
