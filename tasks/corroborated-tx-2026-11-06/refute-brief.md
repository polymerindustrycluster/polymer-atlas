# L6 TX adversarial refute

Review final branch agent/codex/corroborated-tx, task tasks/corroborated-tx-2026-11-06. Return VERDICT: APPROVE or REFUTE with record-level findings and inspected/missing yield. This continues CA draft PR135 on a separate main-based branch.

BLIND FIRST: read blind-input.csv,20 shuffled source rows sampled from21 creates; do NOT open verdicts/allocations first. Give an independent identity, address, scope and operator assessment for each20 clusters. Then reconcile decisions against allocations.csv/verdicts.csv. Do not approve unread witnesses. Federal packet permission and provisional C convention do not excuse aliases, office-only locations or contradictory operators.

Read AGENTS.md, SCHEMA§1/§4.13, task README. Controller allows inherited ITA/OSHA packets at2026-11-01 vintage without fresh bulk download. ITA quotes are government public record; own-page quotes would require raw check, but none are published. New parent/site records allC; current status, HQ and county unknown rather than inferred. No capability inference. Ring2 for Orrex comes from explicit ITA description Compounding Plastics under existing schema compounding rule, not a new scope ruling. Codes alone remain provisional C. IDs subset ORG10500+/SITE15000+/EVD190000+ reserved by controller, disjoint from CA.

40 worked clusters =21VERIFIED/19STILL_UNCERTAIN; +11 parentC,+21 sitesC,+164 evidence. Holding both Farathane and Atkore domain ambiguities, BWAY/Mauser, NOV, Solo/Dart, Cryovac parent issues; office vs manufacture cases; unresolved operators; source unitB13 discrepancy. Inteplast personal attention line removed from new street/output; second IBS PLANT witness excluded. StarPak missing road suffix normalized with house/directional/locality intact. Extra federal-frame IDs only in notes, not registry links. Inspect them for establishment-grain conflation.

Run:
python3 scripts/validate.py #0errors/OK
python3 tasks/corroborated-tx-2026-11-06/check.py #40unique verdicts,20-row sample, idempotent canonical replay, QCEW delta
python3 tasks/corroborated-tx-2026-11-06/build.py #dryrun, apply only with --apply

QCEW2023privateNAICS326=953. Strict sites107→128 (+21),11.2277%→13.4313%. Count ratio, not matched census coverage. Existing canonical rows compared by ID against HEAD unchanged; append_sorted may reorder historical evidence only. Two preexisting CRLF-dirty federal-frame files excluded from PR.

Refute wrong domains/parents, duplicate addresses, legal-label guesses, insufficient scope at a physical establishment, tier claims, evidence omissions, ID reuse and non-idempotence. Any finding must be fixed or held before ready. Do not count failed fetches as closure evidence.
