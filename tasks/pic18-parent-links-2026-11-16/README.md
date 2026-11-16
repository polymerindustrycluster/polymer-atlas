# PIC-18 parent links — 2026-11-16

Claim: atlas-w16-parents, controller-designated PAR integrator. First user: PIC member-prospecting owner; non-use review at handoff 2026-11-16.

Frame: **517 organizations** with an active Ohio site in PIC-18, at least one retained status=ok corpus page, and both parent columns blank at pinned base.txt. Independent frame recomputation uses canonical site counties, not corporate HQ. Organizations with no retained page are outside this corpus-conditioned frame; fetch failures establish no absence. The parent leads in PRs #343 and #347 were explicitly considered (Struktol applied; Steelastic and Chemionics already have parent names and are excluded; IML, Pinnacle and Argueso held).

Applied: **11 parent fills** in organization rows, with 11 evidence rows EVD-384000–384010 and one generated parent_of row REL-000480 (Novation Solutions → parent RDAbbott). **506 held organizations**. dispositions.csv gives an applied/held result and settling fact for every organization. No records created, removed, moved or re-tiered. Only parent_org_id or ultimate_parent_name changes on existing organizations; sources, notes, dates and every other field are untouched.

Acceptance: explicit company self-statement of parentage, exact source-styled unheld name or resolved held immediate-parent ID, quote words in order in retained corpus, no PE/brand/distributor inference, generated edge parity, unchanged other cells, append-only evidence and an idempotent builder. All selected pages are the company's own pages; B-PARENT's parent-domain exception is not needed. Existing tiers and status are not restated.

Sources: proposals.json holds URLs, ordered quotes, manifest indices, route and hashes; full contact-bearing pages remain in the assigned external corpus. No live sources fetched. Dedupe receipts search names, trade names, notes/successors and site names; domain/street inputs were unavailable and are marked skipped. Related US affiliates (Sumitomo Bakelite North America, HEXPOL Compounding) are not substituted for named global parents. No parent organization is created. Pre-pass byte backups and journal location: journal.txt.

Checks: `python3 tasks/pic18-parent-links-2026-11-16/check.py` recomputes the independent frame and every published yield, compares the entire organization-cell delta, checks quote/hash/evidence alignment, proves idempotence, and rejects fabricated quote, altered hash and forbidden-column mutations (3/3). Repository validation, row-loss guard and vocabulary check recorded in checks.txt.

## Proposed follow-ups

Resolve held legal-identity cases in dispositions.csv, particularly Medco/OEM alias self-links, the Ravago legal-name mismatch and SIMONA's duplicate parent candidates. Corpus lexical screening finds leads; holds do not establish independence. No exhaustive external ownership history or financial-sponsor analysis was performed. Cross-family refutation remains with the controller; this draft is not merge-approved.
