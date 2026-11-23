# PIC-18 evidence re-citations after #520

Built by: Codex GPT-6.2 Sol

The owner approved the binding routes in #520. At base `b5958a78`,
five of 18 G8a re-admission cases clear the new routes. The existing
evidence remains historical; each new row names the earlier evidence
it replaces in the claim ledger. Thirteen cases carry forward in
`REMAINING_RE_ADMISSION.csv`. The Kent program name and its ecosystem
rollup change together from the same institution source.

| Case | Binding |
| --- | --- |
| EVD-405007 Stretchtape | Houlihan Capital names the entity and its Cleveland headquarters in a 2023 sale notice. This witnesses existence in 2023. |
| EVD-421581 ACE Innovations | A dated Rubber World notice names the operator. The dateline does not claim an HQ, so EVD-421582 remains queued. |
| EVD-421870 Mitsubishi | The original CY2021 ITA field is 43 characters. CY2017 links the full-name prefix and the same address at establishment 356540. |
| EVD-422344 ShurTech | CY2017 ITA and FRS give the same street, city and ZIP. FRS supplies the county. This is a place-only witness for the held site. |
| EVD-420042 Lincoln Electric | The SEC submission business block matches the sole linked CIK, the held HQ street and the exact Cleveland/Euclid postal pair at ZIP 44117. This is a named SEC filing citation under SCHEMA §4.13. |
| PROG-000014 Kent | Kent's archived heading says “Characterization Facility.” The published name and its matching rollup entry use that heading. |

Seven corrected claim rows cover five re-citations and two changed
canonical cells. Six evidence rows support A (one), B (two), C (one),
or U (two). Three existing Wayback captures receive archive links.
Four capture proofs carry the exact-byte Sonnet 5.5 read logged in
`WEB_READ.csv`. Canonical verification tiers are unchanged.

## Replay

```sh
lockf -k /tmp/polymer-atlas-heavy.lock python3 -I tasks/p1-gate-recite-2026-11-23/check.py --at HEAD
```

The replay checks seven raw or capture hashes and three sealed packet
hashes. It reconstructs the exact changed data and claim ledgers,
verifies each gate route from the original witness, and rejects any unexpected change in the full data diff. No audit sample is drawn.
