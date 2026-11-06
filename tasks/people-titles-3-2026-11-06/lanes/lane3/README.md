# Current institutional title recheck: lane 3

The frozen frame contains **56 existing candidate people**. This packet verifies 28 people against current institution-owned title and polymer-material research sources, holds 27 people for named settling facts, and records one rejection supported by an institution’s dated memorial. It proposes no new people, deletions, specialty changes, or canonical data writes.

Of the 28 verified rechecks, **26 people have proposed role/title field edits** and two people are **already exact**. Both role and printed title are supplied together. `verified.csv` contains only verified professional facts; the full uncertain/rejected discovery roster remains private. `rank_resolution.csv` supplies four additional already-inspected rank witnesses, including the dated promotion resolving a current header/biography conflict. A blank date means the source gives a promotion year without a calendar day; no day was invented.

The evidence register records 157 candidate-source observations over 151 distinct institutional URL routes. Six routes are shared by two candidate entries each and count once in the distinct-route total. The maximum is five recorded routes for one person. There are 79 candidate–URL observations whose URLs were absent from that person’s held source list. These counts measure research coverage, not institutional staffing or program size.

New individual department profiles, current catalogs, and named laboratory research statements resolve legacy narrative titles and broad discovery URLs. Formal title fields are checked separately from biography prose. Shared directory entries are bound to the correct person; adjacent faculty titles cannot supply a rank. Current conflicting ranks remain held unless a dated own source resolves them. Named-professorship cases preserve an existing professor enum under the governing KEEP precedent in `tasks/role-rank-recheck-2026-11-03`; no university `named_chair` enum is introduced.

Verification uses four real institutional known answers from Illinois, Bucknell, LLNL, and Kansas State, followed by five wrong-person, rank, affix, and token-boundary negative fixtures. Fabricated-quote and wrong-identity mutations must fail. The checker enforces all 56 IDs in input order, canonical identity/old-field parity, controlled roles, exact printed titles and quotes, the 40-word identity boundary, institution domains, LF CSVs, source accounting/hashes, and privacy.

Run from the checkout root:

```sh
python3 tasks/people-titles-3-2026-11-06/lanes/lane3/check.py --private-root /path/to/people-titles-3-private/lane3
```

The private input/dispositions and temporary sanitized source cache are required; a missing inspectable source fails the check. Raw source bodies remain in temporary storage. Durable source metadata distinguishes sanitized extracted-text hashes from HTTP bytes and preserves earlier recorded hashes alongside hashes after the shared-cache contact-redaction incident. Two nondeciding CINT capability observations retain inspected rendered excerpts rather than complete page bodies; their hash basis explicitly says so. No contacts were restored and no refetch was made merely to undo redaction.

Holds include missing formal appointment fields, unresolved current rank conflicts, missing current person-bound polymer-material research, unavailable current routes, and controlled-role/scope questions reserved for the owner. News, publication titles, and natural biological molecules alone do not establish a current materials program. Failed routes never establish absence. No PDF bytes were treated as prose; the attempted institutional PDF route returned no PDF, so its extraction yield is zero.

Canonical application, final independent inspection, and completion reviews remain with the integrator. The packet does not itself declare task completion or change tracker status.

The Kroonblawd role-mapping hold is superseded by merged PR149 (`2845288`): Maiti’s existing Deputy Group Leader styling maps to `group_leader` under SCHEMA §4.9. This packet applies that established mapping to Kroonblawd’s exact current formal title, “Deputy Group Leader,” and person-bound polymer material-system statement. No new policy or role value is introduced.
