# Notes history: move working history off the public row (design + 25-record canary)

Status: PROPOSAL and canary packet. Nothing under `data/` changed (check.py proves it). Owner ruling 2026-11-22, "Move history out".
Branch `agent/claude-code/notes-history-2026-11-22`, base `393c3895`. Run `python3 tasks/notes-history-2026-11-22/check.py` (PASS at the time of writing); `python3 numbers.py` prints every figure quoted in §0, §1 and §5 (saved in `numbers.txt`).

Units: **rows** are rows of `data/organizations_*.csv` (5,026) and `data/sites_*.csv` (7,196) on base `393c3895`; a **piece** is one sentence-sized
segment of a `notes` value, cut by `notes_split.pieces` (whitespace stays on a piece, so cutting loses no character).

## 0. Count reconciliation (AGENTS §2 rule 10c: investigate, not explain away)

The controller measured "agent or pass words in notes": 4,243 of 5,026 organization rows, 5,576 of 7,196 site rows (BOARD.md line 2206; the regex is not recorded).
My nearest regex, `Grok|spaghetti|Muse|Codex|Claude|[Pp]ass[- ]\d+|PASS \d+|integration pass`, gives **4,168 and 5,573**: sites match within 3 rows, organizations differ by 75.
I could not close the 75-row gap from the file; **the controller's exact pattern is needed**. All "before/after" numbers below use my regex and say so.
Other measures on the same rows: wider pipeline vocabulary (agent + pass + wave + verdict + staging + packet + lane + burn-down + integrator): 4,904 / 6,931;
this lane's word list: 5,011 / 7,145; the controller-style regex in `stats.py` (`Grok|spaghetti|PASS \d|verdicts.csv|staging|working/|burn-down|integrator assert`): 2,756 / 2,435.
Rows with an empty note: 5 organizations, 15 sites.

## 1. Taxonomy of what notes contain

Read: 200 notes (100 organization + 100 site rows, every tier, seed 20261122, `sample200.py`) plus every canary note. Pieces were assigned a class by first-match regex
(`notes_split.kind_of`) after the read; counts below are regex counts spot-checked against the read, not hand counts. A note usually holds several classes.

| class | sample: pieces / notes containing it (of 200) | all 12,222 rows: pieces / rows | what it is |
|---|---|---|---|
| T1 creation line | 180 / 163 | 9,608 / 9,016 | "Created 2026-10-30 in integration pass 18 from verification wave 2 verdict ... (lane A13, tier B)" |
| T2 harvest or staging wrapper | 75 / 33 | 6,676 / 2,668 | "Source: Grok team Ohio list ... requires Atlas verification wave", Grok ids, "federal sources only" |
| T3 verification, tier, NAICS history | 43 / 32 | 2,703 / 2,086 | "PASS 8 ... Tier U -> A", "NAICS corrected per wave packet" |
| T4 schema or vocabulary mapping | 17 / 15 | 738 / 679 | "Packet entity_type 'company' mapped to 'unknown' per SCHEMA §4.4 enum" |
| T5 dedupe, merge, retire, fold | 16 / 11 | 412 / 344 | "[Dedupe ...: site re-pointed ORG-x -> ORG-y]", "RETIRED ... duplicate of SITE-x" |
| T6 structured marker (BAND-SOURCE, CERT-SITE, CAPABILITY-QUEUE) | 37 / 33 | 2,308 / 2,193 | machine prefixes holding a real fact (size band and its source, certifications, a capability with no vocabulary term) |
| T7 street recorded in notes | 24 / 24 | 2,038 / 2,014 | "Street: 1365 Shuler Ave", written when the schema had no street column; still the only street on rows with a blank `street_address` |
| T8 flag or caution to an integrator or owner | 9 / 9 | 325 / 319 | "INTEGRATOR FLAG ... must not be merged", "do not promote" |
| T9 correction or withdrawn claim | 21 / 20 | 808 / 789 | "address corrected to ...", "wrong foam class", superseded flags |
| T10 source description or quote | 100 / 72 | 6,872 / 4,955 | what an own site, filing or directory said; the reader-useful core |
| T11 other plain fact | 327 / 157 | 23,415 / 9,641 | rebrands, parents, headcounts, certifications, address caveats, scope remarks (graded by hand, §6) |

Reader-facts with no column of their own, by regex over the 200: parent or ownership change 64 notes; employee size 33 (band notes and prose); certification 9; rebrand or name change 7;
second-site or co-location caution 5. These are why the split cannot be "delete the pipeline lines".

## 2. Design in ten lines

1. Split each note into pieces; each piece is **kept** (reader fact, as written), **restated** (reader fact in a plain sentence), or **moved** (pipeline history, verbatim).
2. New table `data/record_history.csv`, one row per piece of every note: `history_id, table, record_id, seq, n_pieces, on_row, text, restated_as, kind, first_date, actor, decided_by`.
3. `text` is the piece verbatim, whitespace included, **for every piece** (kept and restated too), so the original note is the concatenation of `text` by `seq`. Nothing is deleted.
4. `on_row` is `kept | moved | restated | person-held`. A person-held piece stays on the row exactly as today and its `text` is empty in the history file.
5. `restated_as` is the sentence now on the row; `kind` is the §1 class; `first_date` is the first ISO date in the piece's text (often a filing or creation date, not the event date); `actor` is an agent word if the text names one (derived, best effort); `decided_by` is `script` or `reader: <reason>`.
6. The row's `notes` becomes the kept pieces plus restatements, in `seq` order, joined by one space. A kept piece with no closing punctuation gets a full stop; `|` separators and trailing `;` are dropped on the row (the history file keeps them).
7. A line is traced back by `(table, record_id, seq)`; a restated sentence carries no marker on the row, the history row names it. Readers that need the whole story (dedupe, the spines) take the note **rebuilt from history by `seq`**, byte-identical to today's note (asserted for all 12,222 rows), so their output cannot change.
8. Style of what stays: plain sentences, no agent or pipeline words, no tier letters, no Atlas-internal ring numbers, no file paths, no field values with underscores. Dates and source names stay.
9. A script finishes only pieces it can name (§5); every other piece goes to a reader, who writes the decision (`canary_decisions.py` shows the form).
10. Forward rule (otherwise rows re-pollute): writers (`build_integration_sets.py` appends BAND-SOURCE and CERT-SITE to `notes`, `scripts/integrate/`) must write a history row, not a note append, and a validator rule rejects a pipeline word in a new `notes` value.

## 3. Readers of `notes` and how each keeps working

Found by grep over `scripts/` (non-test) and `.github/`; `tasks/` holds 226 scripts that read `notes`, but `run_task_checks.py` runs each check against the tree it was written for, so none reads today's `data/`.
`check.py` section 3 measures every class on the whole tree with each reader's own regex and in the unit that reader reads (sites only, organizations only, or both), in two bounds:
**script-only** (unresolved READER pieces stay on the row) and **worst case** (they all move, pinned pieces excepted). Each class must inspect more than zero positives or the check fails.
Two routes keep a reader working: **pinned** (code reads a phrase on the row, so the row keeps it) and **rebuilt note** (the reader takes the note rebuilt from history by `seq`; identical to today's note for all 12,222 rows, asserted).

| reader (file:line) | reads | positives / lost from the row: script-only, worst case | route |
|---|---|---|---|
| `validate.py:497` | `parcel candidate queue` on an Ohio site with a blank county | zero live positives today, so the rule is vacuous now; tested by blanking the county in memory on the 3 marker rows: phrase survives both bounds | pinned. Canary SITE-001634 shows a reader dropping a stale marker once the county is filled |
| `validate.py:1390` (V-24) | `Settling fact:` on active + closure_signature + watched **organization** rows | 1 live positive; lost 0, 0 | pinned (the phrase reads as jargon: owner question 3) |
| `build_osha_ita.py:657, 668` | `tombstoned as duplicate of SITE-nnnnnn`, `WARN` (site rows) | 14 and 14 positives; lost 0, 0 | pinned |
| `build_lead_fusion.py:551`, `build_osha_ita.py:357`, `build_echo_spine.py:375` | the `Street...:` phrase, **only when `street_address` is blank** (sites) | 899 sites; lost 1 and 1 by raw key, **0 and 0** after allowing for the readers' own sentence split failing after an initial ("County Road K. CERT-SITE", SITE-001990, where the row actually gets a cleaner key) | pinned: a street piece on a blank-column site is never moved; a script-moved piece is restated to `Street: X.` or `Address mentioned in the source: X.` (927 reader pieces are pinned this way) |
| `atlas.py:440-444` (dedupe step 3) | street keys from `NOTES_STREET_RE` for sites with a different or blank column | 1,585 sites carry a key that is not the column's; lost 49 / 612. Many are false matches of the regex itself ("480 employees St") | rebuilt note |
| `atlas.py:463`, `build_form5500_spine.py:307,439`, `build_federal_leads.py:492` (step 4) | other-organization names (organization rows) | 359 organizations mention another's legal name; lost 75 / 350 | rebuilt note; without it a rebrand or parent named in a moved line stops blocking a duplicate |
| `build_echo_spine.py:395, 761` (`FRS_ID_RE`) | 12-digit FRS ids in **site** notes | 757 sites; lost 199 / 320. Canary SITE-010321 shows it: a second FRS id sat in the moved creation line | rebuilt note (ids still must be checked against `registry_links` before any link is minted: AGENTS §4 phantom rule) |
| `build_federal_leads.py:431, 441` (`FEI_RE`) | FEI numbers in organization **and** site notes (and `sources`) | 132 rows; lost 64 / 132 | rebuilt note; `registry_links` holds only 2 FDA_FEI rows, so history is the only other home |
| `build_integration_sets.py:808-859` (writer) | appends `BAND-SOURCE:` and `CERT-SITE (...)` to site and organization notes | writer, not a reader | write history rows instead (ten-line item 10) |
| `build_site.py`, `build_changelog.py`, `export_release.py`, `build_graph.py` | none: each says it never publishes `notes` | n/a | no change |
| `validate.py` V-50 (CRM word) and the contact-pattern scans | every column of every `data/*.csv` | the new file is scanned automatically (`validate.py:626`) | confirm the contact-pattern guard also covers `record_history.csv`; `build_sqlite.py` needs a table entry |

What the lost columns mean: the **rebuilt-note** classes break if a reader keeps taking only the row text, and are unchanged if it takes the rebuilt note. This is a design requirement
(five call sites listed above), measured by regex, not by running those readers' full code paths (§9). **Pinned** classes lose nothing in either bound (asserted).
The canary adds a per-reader diff on its 25 rows (check.py 3b): one real loss from the row, SITE-010321's second FRS id.

## 4. Schema revision proposed (wording is the owner's to approve; nothing edited in `docs/SCHEMA.md`)

Proposed **v1.20**, three items:
- **§4.4 / §4.5, `notes`:** "`notes` carries facts a reader of the record needs that have no field of their own, in plain sentences. Working history (which pass, wave, agent or file produced a value, tier changes, dedupe moves, schema mappings) never goes in `notes`."
- **§4.24 `data/record_history.csv` (new table):** the columns of §2 item 2; "append-only; one row per piece; the history of a record is never attached to its public row; `text` concatenated by `seq` is the note as it stood when split."
- **§3.6.3:** the `CAPABILITY-QUEUE:` note prefix (the only one of the three defined in SCHEMA) is replaced: a capability with no term becomes a plain sentence on the row plus a history row of `kind` `capability-queue`. `BAND-SOURCE:` and `CERT-SITE` are `build_integration_sets.py` conventions, not schema, so rewording them is a writer change. Owner question 1.

## 5. What a script can do alone (corpus-wide, final rules; figures from `numbers.py`)

| piece disposition | pieces, organizations | pieces, sites |
|---|---|---|
| MOVE (lead-in or template match) | 14,204 | 16,002 |
| RESTATE by template (BAND, CERT, capability, ring subtype, FRS id, parent, city grain, CIK, extracted street) | 798 | 2,691 |
| KEEP (street fact, a few listed plain templates) | 155 | 1,114 |
| PERSON (stays on the row verbatim, text not copied) | 1 | 1 |
| READER (needs a person or a second pass) | 9,623 (5,624 plain-unlisted, 3,983 contain pipeline words, 16 pinned, street or unclean restatement) | 11,314 (5,591 plain-unlisted, 4,680 contain pipeline words, 1,043 pinned, street or unclean restatement) |

Rows with **no** READER piece and a non-empty note: **2,409** (712 of 5,026 organizations and 1,717 of 7,196 sites, less rows whose note is already empty): 20% of 12,222 rows.
Tested (check.py 3c): of those 2,409, **22 still fail the independent residue test** and **1,519 end with an empty note** (all their pieces move), so 868 end with a clean, non-empty note.
An empty note is the right result for the owner but means those rows lose their only note text to history, so the 4% MOVE fact-loss rate applies to them.
Rows that need a reader: **4,314 organizations and 5,479 sites (9,793 rows, 80%)**, 20,937 piece decisions: about 11,215 plain pieces a reader mostly confirms and about 8,663 that contain pipeline
words and need rewriting. Hand grading (grading_rounds.md, grading_pieces.csv): script MOVE decisions lose a reader fact about 4% of the time (3 of 70);
defaulting unlisted plain text to KEEP leaves pipeline talk on the row 14% of the time (7 of 50) after three rounds of word-list repair, so a script may not decide those.

Effect on the controller's measure (my regex, §0): organization rows with an agent or pass word **4,168 -> 358** if every READER piece stays, **-> 0** if every READER piece moves; sites **5,573 -> 795 / 530**
(the 530 are pinned street pieces that a reader must restate). Under this lane's stricter independent residue test (check.py; includes "Tier A", ALL-CAPS tokens, ids) rows still holding residue:
2,591 + 3,402 script-only, 13 + 781 worst case. Effect on the PIC-18 unknown-fields outcome line: **none**: `outcome.py` and `pic18_unknown.py` do not read `notes`.

## 6. Canary (25 records, `canary.csv`, `canary_history.csv`; rebuild with `build_canary.py`)

Seeded 20261122 (`pick_canary.py`): nine rows forced by a code-read marker so the dependency check inspects positives (organization Settling fact, site Settling fact, parcel queue, tombstone,
WARN, CERT-SITE, CAPABILITY-QUEUE, an organization FEI, a street that exists only in notes), plus 16 seeded fills. Final mix: organizations 10 (A 3, B 4, C 2, U 1), sites 15 (A 6, B 4, C 4, U 1).
Result: 111 pieces: 14 kept, 58 moved, 39 restated, 50 resolved by a reader. Before and after sit side by side in `canary.csv`; every piece is one line in `canary_history.csv`.

Read as the company's owner, what the split got wrong or left wrong:
1. **The script cannot finish most rows.** 22 of 25 canary rows needed a reader (50 piece decisions). Without them the rows kept sentences such as "Own site opened in full" or "at the exact packet address".
2. **My own first reader pass was too lenient**: I kept "opened in full" (SITE-001879, SITE-002834, SITE-001841) and "the exact packet address" (ORG-002619); the independent residue test caught the last, and I rewrote the rest on a second read. A reader needs the word list in front of them.
3. **Source truncation survives any split.** Notes cut mid-word in the source (ORG-007330 "Hudson", SITE-010321 "ECHO carries two FRS I", SITE-001841 "fabricated in its pur…") cannot be restated; I moved the fragments and flagged them. The row loses a clause the source never finished.
4. **Pinned markers read as jargon.** ORG-002154 keeps `Settling fact: ...`, SITE-001841 keeps `tombstoned as duplicate of SITE-001149`, SITE-001914 keeps `WARN notice`, because code reads those words on the row. Owner question 3.
5. **Facts that look like pipeline are sometimes the point.** SITE-001914's "EPC is the successor operator at this plant ... INOAC closed" sits next to grading talk; the split had to separate them by hand. "Casting process inferred ... the company does not state it" is a plain caution the owner may keep or drop.
6. **Restated street duplicates the address** when the site also says it in prose (SITE-000136, SITE-001879): harmless, slightly repetitive.
7. **Run-on sentences:** a kept piece with no full stop ran into the next sentence (SITE-002818) until `tidy` added one. That is one of the characters the row gains that the original did not have; the history keeps the verbatim form.
8. **A restatement can add a claim the source does not make.** The digit test (every digit run in a restatement is in its source piece) passes on every template restatement and all 39 canary ones, but reading the 39 as the owner found two added claims, both fixed: "the company does not state it" (ORG-004838) and "the other names are not part of this company" (ORG-007330; the source says they should not be added). A digit test cannot see that. At bulk about 8,660 pieces are rewritten this way, so a second reader should audit a sample.
9. **One real reader loss on the canary:** SITE-010321's second FRS id sat in the moved creation line and is gone from the row (check.py 3b); it needs the rebuilt-note route.
10. **Marker rewording loses exact numbers' provenance wording:** "plan count, not a headcount; R7f" becomes "a band, not a headcount"; the rule number goes to history.

Checks passed (check.py): person-held pieces stay verbatim; the rebuild by seq equals the original for all 12,222 notes; lossless for 25 of 25 (history reproduces each original exactly and as a segment multiset); no residue word on any canary row; both planted misses caught
(a "Reviewed in integration pass 9 by Grok" sentence, and an underscore / ALL-CAPS token only the independent list knows), both injected through `after_note`; every dependency class inspected more than zero positives;
`data/` identical to `origin/main`. The check is not circular: the classifier's word list (`notes_split.WORDS`) and the checker's (`check.py RES`, plus shape tests) are separate, and the checker found one defect the classifier missed (ORG-002619).

## 7. Personal data

No individual's name is carried into any file in this folder: the person pattern pins a piece to the row and empties its `text`; `canary.csv` excludes both rows below.
Rows whose `notes` name an individual or a trust named for one (path:line, no names copied):
- `data/organizations_OH.csv:1134` (a founder and chief executive named in the note)
- `data/sites_MI.csv:168` (a TRI parent string that is a family trust named for an individual)

Not rescanned here but already in the user review: `data/evidence_organizations_OH.csv:3235`, `:3260`, `:3261` and `data/evidence_sites_OH.csv:4889`, `:4919`, `:4946`, `:4947` (internal audit `notes`
naming an individual). The pattern's positive control flags `evidence_organizations_OH.csv:3235`. Street names that contain a first name (for example "Joseph Lloyd Parkway") are addresses, not people, and were reviewed by eye and left alone.
No email or phone appears in `organizations`/`sites` notes by pattern.

## 8. Owner rulings this design needs (listed, not settled)

1. Wording of `CAPABILITY-QUEUE` (a SCHEMA §3.6.3 notes prefix) and of `BAND-SOURCE` / `CERT-SITE` (writer conventions): may they be reworded to plain sentences, with the history row as the machine-readable form?
2. Do source acronyms (TRI, ITA, OSHA, ECHO, FRS, EDGAR), record ids (ORG-, SITE-) and tier letters count as pipeline words? This lane left acronyms and ids on rows and removed tier letters and ring numbers.
3. May the code-read phrases `Settling fact:`, `tombstoned as duplicate of`, `parcel candidate queue` and the word `WARN` be reworded, with the readers (`validate.py:497, 1390`, `build_osha_ita.py:657-668`) changed to match?
4. `created_by` (columns of the same rows) and `description_1line` carry agent names too (`spaghetti-grok-pic12-staging`, "Staging lane row ..."); in scope for the same reader complaint?
5. May dedupe readers search `record_history.csv`, and is the history file itself public (it carries agent names by design; the ruling says "kept in the repo for audit")?
6. Does the forward rule bind: a validator rule rejecting pipeline words in a new `notes`, and writers moved to history rows?
7. Who completes truncated source notes, or may fragments be moved without completion?

## 9. Not checked

Only 25 records read as the owner (the samples graded were pieces, not whole rows); the 200-note taxonomy is regex-classed, not hand-counted; the dependency check ran each reader's regex, not the readers' full code paths
(`atlas.py dedupe-check` and the spines were not executed against the after-tree); no page fetch was needed or made; the 14% residual and 4% loss rates have wide intervals (n=50 and n=70), and rounds 1 and 2 cannot be redrawn; person detection is a title and trust pattern with a positive control but unmeasured recall (a first-name-only mention at ORG-001377 piece 9 is not caught); the tone of restatements was judged by one reader; code-simplifier was applied by hand to `notes_split.py` (dead code removed), not run as a separate pass;
the controller's own jargon regex was not available. The history file's size (every piece verbatim, about 5.5 MB of note text) and its effect on `build_sqlite.py`, `check_row_loss.py` keys and CSV merge conflicts were not measured.
