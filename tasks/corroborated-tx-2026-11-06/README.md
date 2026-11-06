# L6 TX CORROBORATED, 2026-11-06

Continuation after CA draft PR135, separately branched from origin/main. Controller thr_9i2c6byhcz delegates application to lane atlas-L6-corr-ca-tx. First user: campaign integrator on2026-11-06; non-use finding date2026-11-13. Controller owns task state.

Acceptance: validate.py zero errors;40 selected clusters appear exactly once in verdicts.csv; byte-identical builder replay;20-row independent blind source recheck; strict NAICS326 site count ratio to QCEW2023 before/after using scripts/build_qcew_denominators.py; two-family deep refute approval before ready. Controller05:55 BOARD clerk rule permits draft PR before refutes, superseding original council-only/push-after-refute sequence.

Selection: first40 of233 TX CORROBORATED clusters, explicit core prefixes3252/3261/3262/325991 first, score descending, cluster_id ascending.21 VERIFIED establishment candidates,19 STILL_UNCERTAIN with settling facts. Proposed:11 new parent organizations at C and21 TX establishments at C,164 appended evidence rows. New HQ and current status are unknown; no plant address is asserted as corporate HQ. County remains blank because the cluster county is orientation-only. No capability inference from codes.

IDs: controller-reserved block subset ORG-010500+, SITE-015000+, EVD-190000+. CA uses ORG-010000+,SITE-014000+,EVD-180000+ in PR135. Gaps are permanent. Branch history is pre-pass backup; allocations.csv is ID journal. Builder collision assertions prevent reuse; repeat of identical packet is a no-op.

Sources: inherited OSHA ITA CY2025/inspection extracts at2026-11-01 packet vintage (controller grant relayed by L7 and BOARD), reviewed2026-11-06. ITA evidence names establishment_ID, submission date and verified bulk URL under /sites/default/largefiles/. Provisional federal-only C follows STRONG-wave conventions; no tierB claim or own-page quote is published. Own-domain pages fetched for identity/dedupe; fetch failure is availability only. ECHO/FRS and exact same-address extra federal-frame IDs appear in notes only, not registry evidence/links. No FRS REST used. No employer-plan counts or exact employee headcounts added to canonical rows.

Dedupe uses atlas.py domain, normalized name, street/locality, trade_names/notes across all shards; results dedupe.json. Known-answer domains: Inteplast→ORG-003476; Closure Systems→ORG-004819; ORBIS→ORG-000474. US Farathane and Atkore ambiguous held-parent pairs are held. LoneStar filed company_name=Inteplast; linkage follows domain first. Creative Liquid Coatings and Parker link to existing operator parents. The Inteplast street excludes a personal attention line; original source extract remains read-only. A second Inteplast witness names IBS PLANT and is excluded, rather than collapsing plant qualifiers. Street suffix omission normalizes Road/none at StarPak; house number, directional, locality remain required. Mauser B13/unitless ITA mismatch is held.

## Holds and schema decisions

19 settling facts in verdicts.csv are authoritative: ambiguous Farathane/Atkore/NOV held parent; BWAY/Mauser, Solo/Dart, Cryovac/SealedAir operator; DuraPlas Addison and UTEX Houston HQ vs manufacture; Utex Weimar legal label; ECHO+employerForm5500-only candidates; Lixil AmericanStandard legal identity; unrelated Evolve/Aurora name hits; T.C./NextGen identity; Mauser buildingB13. No closure/no-establishment REJECT, scope exception, parent correction or vocabulary addition is applied. Orrex's ITA description explicitly states Compounding Plastics, so existing SCHEMA§1 compounding rule gives ring2 rather than the default shaping ring1; no new ruling.

## Checks / refutes

Pending final runs and clerk reviews.20-row fixed-seed blind sample omits lane verdict/tier/link fields; reviewer independently checks sources before allocations. All21 create source records resolve in the builder. House word matcher self-checks3 positives/2 injected negatives, though no own quotes are published. Current-status unknown and provisional C are not proof of today's physical operation.

Named checks2026-11-06: `python3 scripts/validate.py` zero errors/OK. `python3 tasks/corroborated-tx-2026-11-06/check.py` PASS:40unique verdicts,20/21blind sample source witnesses, canonical rerun bytes identical; strict326107→128/953 (11.2277%→13.4313%). Existing canonical rows all preserved by ID dictionary comparison to HEAD. No shared scripts changed, so scripts pytest trigger does not apply. Two-family clerk reviews pending.
