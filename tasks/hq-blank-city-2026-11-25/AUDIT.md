# Census audit of the HQ blank-city batch after repair

Label: claude-code hq-blank-city-2026-11-25
Result: PASS
Sample: census of all eight organizations and eleven original CLAIMS_CHECKED.csv rows in #563, plus all five withdrawals in repair PR #570. Replayed the sole cited capture against the moved evidence row.
Reviewers: atlas-review-569-codex, GPT-6.2 Astra (OpenAI). Claude built the original batch and the repair.

The first census returned FAIL for ORG-000197. The five merged data files matched #563's reviewed head 62517501 byte for byte. The problem was the interpretation of the address. The checksummed Kenda locations capture lists the American Technology Center at 5801 Mayfair Road under Offices. The quote in EVD-483143 replays at offset 471. The held parcel note places the center in Green, Summit County. Neither record establishes the headquarters role, and the notes on SITE-000988 describe a distribution/HQ establishment in Reynoldsburg.

The first census accepted seven hq_county withdrawals. All seven remain blank at the repair head: ORG-000022, ORG-000033, ORG-000050, ORG-000073, ORG-000186, ORG-000202 and ORG-003703. Those withdrawals cite no capture and assert no replacement county.

Repair PR #570 at b4a668e3964f63a0f83433b1011ffda738be33b2 clears ORG-000197's hq_city, hq_state, hq_country, hq_in_scope and hq_county. Each cleared cell has one withdrawn claim. The dated note preserves the original notes and explains the distinction between an office address and headquarters. Appendix C places the organization in the US residual shard with state and country unstated. Both evidence rows, EVD-421274 and EVD-483143, moved with it from OH to US, byte for byte. Comparison with PR base 5164203c found no other data changes.

At the repair head, python3 tasks/hq-blank-city-repair-2026-11-25/check.py 5164203c exited 0 and caught all 19 planted defects. The independent census checked the withdrawn values, row placement, capture digest and quote offset. python3 scripts/validate.py exited 0.

## What this audit is not

The verdict applies to the original batch with the reviewed #570 repair applied. It does not establish a headquarters for any of the eight organizations or attest that the repair has merged.
