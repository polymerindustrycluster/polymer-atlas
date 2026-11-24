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

- **Frame.** Owners of an active A–C PIC-18 site and those sites (controller ruling). HQ-only owners are excluded by reason (218 organizations, 31 ecosystem at `6516b6cf`).
- **Builder family.** Labels resolve by family word, then the task folder's `Built by:`, then a controller-approved CSV (`families_proposed.csv`, built by `labels` from the first commit adding each label, its PR's `agent/<harness>/` branch, else a `Co-Authored-By` trailer). Repair history is every `tasks/*/CLAIMS_CHECKED.csv` listing the record. `uncertain` routes primary to Astra and always gets a Hydrogen second read, with no check coin. An unmapped label or no label blocks.
- **Flagged = any non-VERIFIED value, missing assessment or adverse receipt.** On the known-answer run that was every record, so nearly every record gets a second read; the 10% flag share in `sizes.py` is far too low.
- **Combining reads.** A contradiction counts only if its quote replays in order against the cached page. A replayed contradiction from either read stands. An unconfirmed claim clears only when an independent second read verifies it; the builder-family exception reader can object but never clear.
- **Child findings** gate only when the reader ties the contradicted child value to a core field (`core_effect`) and the quote replays.
- **Plants** use `draw.plants` (a same-table value from another record) with a keyed seed, three per provider (Astra, Hydrogen, Sonnet), from records independent of that provider's family and outside the real sample. A missed plant suspends the run.
- **Stall watchdog** is the 1,500 s call timeout; a failed call suspends the run.

## Replay coverage

Receipts exist for bands from OSHA ITA and OSHA inspection filings (operator, street, city, age, band; checksum from the store sidecar). Form 5500 gets a `LEAD_ONLY` receipt. A replayer that runs and cannot settle issues an `UNRESOLVED` receipt. **A class with no replayer blocks preflight and is counted; nothing is reported as inspected that was not replayed.** Not built: PPP-URL bands, other band sources, filing NAICS and every registry ID (EIN, FRS, TRI, RCRA, NPDES, LEI, UEI, SEC, Ohio SOS, Wikidata). Registry "conflicting owners" and "wrong vintage" tests exist only for bands.

## Results (aggregates only; no sampled record was read)

**Preflight, whole frame, `6516b6cf`, no model calls, 2 min wall, 1,671 records (879 sites, 785 organizations, 7 ecosystem), digest `0d83c5d5…`.** With the proposed label map: 0 unknown builders; routes Hydrogen 1,206 / Astra 465 (sizes.py assumed 30 / 70); 1,430 packets build, 241 blocked. 1,074 records block: 48 band-other, 206 PPP, 194 filing NAICS and 14–543 per registry class with no replayer; 96 NAICS source name blank and 139 withheld (dependency gate); 6 evidence-URL leak flags (need the controller's approval files, not supplied). Without the map 1,405 records block on unknown builder family. Band receipts: ITA 93 match, 61 do not bind operator and street, 13 row or file not in store; inspection 40 match, 10 do not bind, 1 contradicts; 93 Form 5500 lead-only.

**Known-answer run, snapshot `985ed36`, 10 records outside the frame (file contents not reproduced).** 9 ran (one packet failed the NAICS dependency gate and was skipped); 5 Astra primaries, 4 Hydrogen. Every record was flagged, so all 9 got a second read; 32 metered calls. Source-contradicted expected errors: 2 of 9 (an HQ city, an archive capture date), both Hydrogen primaries. Expected field flagged as specifically unsettled: 5 more. Missed: 2 (invalid-vocabulary process literals, which need the controlled vocabulary the packet does not carry; that check is machine-side). 159 of 229 audited values (69%) came back unconfirmed, mostly because 9 of 22 sources were unavailable or silent.

| Provider | Calls | Mean input tokens per call | sizes.py assumption | Mean output tokens |
|---|---:|---:|---:|---:|
| Astra | 18 | 17,352 | 50,000 | 10,523 |
| Hydrogen | 14 | 35,597 | 100,000 | 16,657 |

Input per call is about a third of the assumption, but calls per record were 3.6 (second reads and one REQUEST round) against about 1.25 assumed: 0.090M input per record against 0.104M in `sizes.py`. Calls took 70–420 s.

## Not checked

The frame-level draw, packets for the real sample, and any real-frame `run`. Replays for filing NAICS and registry IDs. The `--approved` files for the 6 leak flags. Sonnet as a second reader and the REQUEST round for a record built by the second family (selftest only). Windows paths. The label map's 91 direct-push labels are `uncertain` because their pass journals were not read.
