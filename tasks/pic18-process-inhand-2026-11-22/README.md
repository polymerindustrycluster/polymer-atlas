# PIC-18 process fills from material already held: canary (Part A), 2026-11-22

Lane `atlas-w22-process-inhand` (Claude Sonnet 5.5), controller thr_9i2c6byhcz. **Canary packet only: nothing under `data/` changed, no PR, no integrator action.** First user and review date belong to the controller's wave record; no issue is closed. Cross-family review is the controller's.

## Frame and unit
Unit: **active tier A–C Ohio sites in the 18 PIC-18 counties of `scripts/regions.py`** whose organization has no `processes` token at site or organization grain (the harness definition): **333 sites in 322 organization rows** (reproduces `pic18_unknown.py`: 794 org rows, 322 process-unknown). 216 of the 322 organizations have at least one stored readable page in the 2026-11-16 corpus (controller `persist/pic18-corpus-2026-11-16`, the store the earlier capability lanes read); 71 have a website on record and no stored page; 35 have no website. Canary: 25 sites, seed 20261122, `random.Random(seed).sample` over the sorted frame (`check.py` recomputes it).

## Canary result (unit: sites; each of the 25 appears in exactly one of the three files)
| File | Sites | Notes |
|---|---:|---|
| `packet.csv` fills | **1** (2 terms) | SITE-001930 Rotocast Technologies (Akron, tier A, sole active site): `tooling_repair_maintenance` and `mold_tool_making`, each quoted from the company's own stored page with the street printed on the same page |
| `leads.csv` | **9** | route A 5 (a URL already on the record names the statement; no capture held; one permitted fetch settles it), route B 3 (the note names a source with no URL on the record: new research), route C 1 (a live capability row; owner question 1) |
| `holds.csv` | **15** | distributor 3, no 3.1 term fits 3, no statement in hand 3, no process named 2, and one each: wrong company page, error page, material developer, grain question |

Yield: 1 of 25 (4%; a Wilson 95% interval would be roughly 1% to 20%, too wide to project). Earlier lanes read the same corpus: PR #351 filled 3 of 224 sites, CAP2A 14 of 110, the 2026-11-18 organization canary 0 of 10. The conversion path that matters is the leads: if all 5 route-A leads settled as fills, the canary would be 6 of 25, but each needs a fetch of an on-record page and a sentence, so that is a ceiling, not a forecast.

## What decided each fill
A fill needs one sentence on a stored page of a source the record already cites, stating that the plant itself does a §3.1 process, plus a locality witness tying the page to this site's street (`check.py` verifies: quote verbatim in the stored text; raw SHA-256 equals the manifest; the page host is a source on the record; term in `docs/schema/vocab.json` PROCESSES; the quote is a full sentence, not a menu line; the site street is printed in the locality quote). Our own notes are not a source: every note-only candidate is a lead.

## For the controller before the go
1. **The review's own example is outside this frame.** Of the seven plants the staff review and brief name, only **SITE-001916 (Hedstrom)** is in the frame. SITE-000335 (Dura-Line conduit) has blank site `processes` but its organization row carries `extrusion_pipe_tube`, so the harness counts it known; SITE-000336 (the accessories plant that must not extrude) has its own site cell; SITE-000227 carries free text (`film extrusion, flexographic printing, bag converting`); SITE-000453 holds `distribution`; SITE-001514 and SITE-000678 hold organization-grain terms. For Dura-Line the only support for "conduit extrusion plant" is a note citing Orbia careers postings, which are not on the record: a route-B lead if it were in the frame. Hedstrom's note ("Custom rotational + injection molding plant") has no stored page stating it.
2. **Two outcome-line gaps, surfaced not fixed.** (a) **154 PIC-18 active A–C sites in 122 organizations have a blank site cell but a non-blank organization cell**; the review reads site grain, the outcome line reads either grain. (b) **75 PIC-18 organization rows are counted process-known on cells holding no §3.1 term at all** (free text, or `distribution`, `machinery_equipment`, `tooling_mold_die`, `recycling_recovery`); 89 rows carry at least one off-vocabulary token. Counted from the base tree against `docs/schema/vocab.json`.
3. **Owner questions (listed, not settled).**
   - Q1 (§3.6.2): may a live `site_capabilities` process row whose term equals a §3.1 string fill `processes[]` when the permit or filing sentence is not retained? §3.6.2 says a capability row never creates a §3 tag. Affects the 5 frame sites with live process rows (SITE-000264 Blair Rubber, -000601 Schneller, -000667 Vinylume, -001530 Tremco CPG, -002855 Mitsubishi Chemical Performance); only SITE-000601 was in the canary.
   - Q2: is a customer testimonial printed on the company's own page a narrative statement? The `mold_tool_making` fill rests on one; the services page lists "Fabricated Molds … CNC Molds" as a menu (supports_C, barred on tier A by V-25). The `tooling_repair_maintenance` fill is a plain company sentence.
   - Q3: does `tooling_repair_maintenance` cover mold repair for polymer processors only (my reading) or any tooling? (§3.1 names it and does not define it; the 2026-11-18 canary held Alcon on the same question.)
4. **Not run:** the other 308 frame sites; any live fetch; the 71 organizations with a website and no stored page; non-corpus stores. `material.py` is the reading aid, `build.py` holds the hand adjudications.

## Reproduce
`python3 tasks/pic18-process-inhand-2026-11-22/build.py` rewrites the three CSVs and `summary.json`; `python3 tasks/pic18-process-inhand-2026-11-22/check.py` is the gate (6 planted defects: paraphrase, menu line, invented term, wrong locality, site not in frame, quote from another organization's page; all rejected). It fails, never skips, when the corpus is unreadable.

## Proposed follow-ups
- On the go: run the same reading over the other 308 sites; route-A leads get one fetch each from the on-record URL, stored under controller persist.
- Owner batch: Q1 to Q3 above, plus the two outcome-line gaps.
