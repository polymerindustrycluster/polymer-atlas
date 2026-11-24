# Audit 13 smoke harness

ATLAS-7 · `claimed:atlas-p1-smoke-runner 2026-11-24` · Built by: Claude Code (Sonnet 5.5). Tools only: no `data/` row changes, no draw on the PIC-18 frame.

One record per fresh short reader call, from sources fetched once by script. [PROTOCOL.md](../blind-audit-13-protocol-2026-11-24/PROTOCOL.md) says what counts; this folder is the runner.

```sh
python3 tasks/blind-audit-13-smoke-2026-11-24/check.py                                 # selftest, no frame, no model (18 planted cases)
smoke.py frame     --at SHA --out DIR                                                  # PIC-18 frame, reconciliation, exclusions, digest
smoke.py preflight --at SHA --out DIR [--families CSV] [--approved CSV]...             # whole frame, no model calls; exit 1 on any block
smoke.py labels    --at SHA --preflight DIR --out CSV                                  # label -> family evidence (git history), for the controller to approve
smoke.py draw      --at SHA --preflight DIR --secret-file PATH --out DIR               # controller only
smoke.py fetch     --draw DIR --cache DIR                                              # fetch once per source; replay receipts; packets
smoke.py run       --draw DIR --cache DIR --out DIR                                    # sealed order; stop at k = 3; cancels the rest
smoke.py score     --run DIR                                                           # aggregates only
```

## Reused, forked, and why

| Reused unchanged | From |
|---|---|
| `GitReader`, `build_frame`, `FIELD_CLASS`, `plants`, `csv_text`, `write_private`, `require_ancestor` | audit 12 `draw.py` |
| `Head`, `render_row`, `leak_scan`, `CHILDREN`, approvals format | audit 12 `packets.py` |
| `pinned_gate` (`family_of_text`, `label_folder`, `builder_family`) | audit 12 `replay.py` |
| `Corpus.fetch` (robots, cache, hash receipts) | `scripts/site_corpus.py` |
| `held_names`, `name_class`, `same_street`, `city_ok`, `band_of`, the 10-year cutoff | size sprint / `pic18-size-10yr` |

**Forked: the draw.** `draw.run_draw` cannot run a one-stratum plan: `STRATA = list(sizes.PLAN)` (six strata, `draw.py:21`), `sealed_plan()` requires `sizes.json` to equal `sizes.PLAN` (`:375`), `run_draw` loops every stratum and takes plants per stratum (`:391`), and the seed hash is a constant with no override (`:20`). It also orders with plain SHA-256, not a keyed HMAC per purpose. `packets.build` and `read_draw` need that six-stratum directory and 18 plants (`packets.py:127`). So `smoke.py draw` is new (HMAC orderings for smoke, plant pool, plants, display order, check coin), and packets are made by calling `render_row` and `leak_scan` directly.

**Registered, not forked.** `load()` adds what `draw.py` predates: the derived table `value_basis` (SCHEMA §4.24, class D) and the `processes_other_note` / `materials_other_note` organization columns (class J). Any other unclassified column still fails `build_frame` and blocks sampling. A `not_found_pending_refetch` token is withheld from display, so it is dropped from the packet (none was counted at `6516b6cf`).

**Gemini is called with `agy` directly**, not `council-ask gemini`: `agy-headless` keeps only the text and drops the stream's `usage` record. `call_model` asserts the resolved model on every call (Hydrogen High, `gpt-6.2-astra`, `sonnet`) and refuses any other (Neon, Argon) and any call with no usage record.

## Choices the protocol does not state (for the controller to confirm)

- **Frame.** Owners of an active A–C PIC-18 site and those sites (controller ruling). HQ-only owners are excluded by reason (218 organizations, 31 ecosystem at `6516b6cf`). `hq_county` stays a core field (ruling 15:15).
- **Builder family.** Labels resolve by family word, then the task folder's `Built by:`, then the approved CSV (`families_proposed.csv`, built by `labels` from the first commit adding each label, its PR's `agent/<harness>/` branch, else a `Co-Authored-By` trailer). Provenance covers the record, its evidence rows, every scoped child (including `host_org_id` equipment and archive links) and every `tasks/*/CLAIMS_CHECKED.csv` listing the record. `uncertain` routes primary to Astra and always gets a Hydrogen second read (forced even if Google built it: marked a routing exception whose objection is reviewed but cannot clear a flag), with no check coin. An unmapped label or no label blocks.
- **Flagged = any non-VERIFIED value, missing assessment or adverse receipt.** On the known-answer run that was every record, so nearly every record gets a second read; the 10% flag share in `sizes.py` is far too low.
- **A contradiction binds the incompatible fact.** The reader gives `source_value` (the value the source states), it must differ from the held value (a corroborating address is support), appear inside a quote that replays in order against the cached page or a replay receipt (`R#` counts as a source), and name a source that exists. The deciding quote is kept in the private results. A replayed contradiction from either read stands and is marked disputed if the other read verified; an unconfirmed claim clears only when an independent second read verified it.
- **Sealed run.** `fetch` and `run` verify the sample digest, the 40 + 3/3/3 sizes and the stop count of 3 in a frame run; every sealed item must have a packet (an explicit-list fixture may skip gated packets, listed in `skipped.json`). Dispatch is bounded to the unscored window; a failed, empty, unmetered or wrong-model call halts the run without a retry (only an unparseable answer from a healthy call is retried once); per-provider stage budgets (twice the `sizes.py` smoke row) halt the run for repricing. One bounded source set per record is shared by both readers, including a requested page.
- **Child findings** gate only when the reader ties the contradicted child value to a core field (`core_effect`) and the quote replays.
- **Plants.** `make_plants` is `draw.plants` forked to try the core and locality fields first (`street_address`, `county`, `hq_county`, `legal_name`, `site_name`, `hq_city`, `city`, `zip`), falling back to any other populated judged field except `status` and `verification_tier` (those two, and the synthetic polymer-relevance key and child rows, are never planted). A plant swaps one field for a different record's value of the same table, in the packet only. A reader detects a street, county, name or locality swap by finding a cited page that states a different value (CONTRADICTED with a replayed quote) or by naming the specific page that would settle it (UNCONFIRMED with a specific `settling_fact`; "withheld" or "unavailable" earns nothing). Three per provider, from records independent of that provider's family and outside the real sample. A missed plant suspends the run. Detection rate from cached excerpts is not demonstrated: the known-answer run planted none.
- **Stall watchdog** is the 1,500 s call timeout; a failed call halts the run.

## Replay coverage and NOT_INSPECTED

Receipts exist for bands from OSHA ITA and OSHA inspection filings: the cited row is located, its operator, street and city must bind, the filing must fall inside the 10-year cutoff, and the **newest binding filing** decides (an older different band under a newer supporting one matches; a newer different band contradicts). Form 5500 gets a `LEAD_ONLY` receipt. A replayer that runs and cannot settle issues an `UNRESOLVED` receipt. **A filed value with no replayer is NOT_INSPECTED** (owner ruling 2026-11-24 15:15): PPP and other bands, filing NAICS (primary and `code_assignments`), every registry class, and a NAICS value with a blank or withheld source name. It does not block, is not shown to the reader as a checklist item (the packet lists it as not inspected), and is tallied by field in `score`. Known limits: the cutoff is dated from the snapshot commit, not from when the band was written; org-grain bands are `UNRESOLVED` (no single-site eligibility check); registry "conflicting owners" and "wrong vintage" tests do not exist.

## Results (aggregates only; no sampled record was read)

**Preflight, whole frame, `6516b6cf`, no model calls, about 2 min, 1,671 records (879 sites, 785 organizations, 7 ecosystem), digest `0d83c5d5…`.** With the approved label map plus 5 added `uncertain` rows (labels first reached through archive and equipment children): 0 unknown builders; routes Hydrogen 1,206 / Astra 465 (sizes.py assumed 30 / 70). **6 records block, all on leak flags** (7 exact public-URL cells, in a candidate CSV for the controller to approve). 1,665 packets build. Not inspected (filed claims, counted, not blocking): PPP bands 206, other bands 48, filing NAICS 194, registry IDs 2,201 across eleven classes (FRS 895, TRI 469, EIN 353, RCRA 210, UEI 99, LEI 71, NPDES 36, OH SOS 33, SEC 21, Wikidata 14); NAICS with a withheld source name: 139 cells. Band receipts: ITA 93 match, 61 do not bind operator and street, 13 row or file not in store; inspection 40 match, 10 do not bind, 1 contradicts; 93 Form 5500 lead-only.

**Known-answer run, snapshot `985ed36`, 10 records outside the frame (file contents not reproduced).** 9 ran (one packet failed the NAICS dependency gate and was skipped); 5 Astra primaries, 4 Hydrogen. Every record was flagged, so all 9 got a second read; 32 metered calls. Source-contradicted expected errors: 2 of 9 (an HQ city, an archive capture date), both Hydrogen primaries. Expected field flagged as specifically unsettled: 5 more. Missed: 2 (invalid-vocabulary process literals, which need the controlled vocabulary the packet does not carry; that check is machine-side). 159 of 229 audited values (69%) came back unconfirmed, mostly because 9 of 22 sources were unavailable or silent.

| Provider | Calls | Mean input tokens per call | sizes.py assumption | Mean output tokens |
|---|---:|---:|---:|---:|
| Astra | 18 | 17,352 | 50,000 | 10,523 |
| Hydrogen | 14 | 35,597 | 100,000 | 16,657 |

Input per call is about a third of the assumption, but calls per record were 3.6 (second reads and one REQUEST round) against about 1.25 assumed: 0.090M input per record against 0.104M in `sizes.py`. Calls took 70–420 s.

## Smoke run conditions

Owner ruling 2026-11-24 ([DECISIONS.md](../../DECISIONS.md)): the smoke runs with one worker (`smoke.py run ... --window 1`). The controller hand-checks every record counted in k, every plant verdict and every packet's record ID against its sealed row. The report marks the size-band and child-field tallies unreliable. The nine open Codex findings (PR #556 body) are fixed before any full draw.

## Not checked

The frame-mode `draw` (its frame/routes reconciliation is asserted, not exercised on a real preflight directory), packets for the real sample, and any real-frame `run`. Replays for filing NAICS and registry IDs (not inspected). The approval of the 6 leak flags. Sonnet as a second reader and the REQUEST round for a record built by the second family (selftest only). Windows paths. The label map's 91 direct-push labels are `uncertain` because their pass journals were not read.
