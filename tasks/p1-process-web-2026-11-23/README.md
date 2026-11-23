# PIC-18 own-site process corrections

Built by: Codex GPT-6.2 Sol

Atlas P1 correction/process PR 2. The application base is `0b191fe6` after PR #500. The preceding batch's reviewed evidence census is recorded in the [riding audit](../p1-atlas8-corrections-2026-11-23/AUDIT.md). The controller is the first user and the queue records 2026-11-30 as the use check.

## Scope and acceptance

Apply only sealed proposals with a verbatim own-site activity witness, the proper organization or plant grain, a different-family reading of the proof bytes, a verified Wayback archive link and a PASS from main's proof gate. Replay must reconcile every process cell, evidence row, archive link, claim ledger row and held proposal. Validate and row-loss must pass.

| Admitted observations by existing record tier | A | B | C | Total |
| --- | ---: | ---: | ---: | ---: |
| Organization process terms | 5 | 4 | 1 | 10 |
| Site process terms | 3 | 1 | 0 | 4 |
| Total appended evidence rows | 8 | 5 | 1 | 14 |

Fourteen terms fill eleven previously blank process cells across eight organizations and three sites. Each term has its own evidence row and archive link. For cells with multiple terms the claim ledger points at the first witness. Each witness uses the corresponding `supports_A`, `supports_B` or `supports_C` effect for its activity claim. Record-level tiers stay at their recorded values.

On the 794-owner PIC-18 frame, organizations with an active PIC-18 tier A–C site, the count with unknown processes goes from **320 to 312**. This is a coverage count of published process fields.

## Archive and reader dispositions

The sealed packet combined five pilot organization readings with thirteen scale readings. Claude Sonnet's November 23 readings cover the organization, site, quote and term for the admitted proposals. Nine admitted claims use live proof bytes. Five retain their sealed bodies and four use refreshed bodies whose extracted main text and quote offsets Sonnet independently rechecked. Technoform, Parker and Rotocast use five proofs on three separately read Wayback bodies. Seven live bodies and three archive bodies are pinned by hash in the private provenance store.

The authenticated Save Page Now round returned ten job timestamps. The exact Pioneer archive URLs reached their existing November 16 mementos, which both carry the reviewed quotes. Polymer Packaging uses an existing November 16 capture. The non-archive proofs still replay against the live URLs.

[OPEN_QUEUE.csv](OPEN_QUEUE.csv) accounts for the other four proposals. The two Dudick rows require a capture whose main text carries the quoted process wording. The two Blair Rubber rows require a capture whose bytes are stable across two gate fetches, or a held route. The collection packet's four unproposed plant attributions stay at organization grain because the website or held site type conflicts with locating the operation at the sole held site.

## Replay

Run from the repo root. The replay reads the sealed controller packet and the private shared store at the paths in `check.py`. Override them with `--packets` and `--store` if needed.

```sh
lockf -k /tmp/polymer-atlas-heavy.lock python3 -I tasks/p1-process-web-2026-11-23/check.py
lockf -k /tmp/polymer-atlas-heavy.lock python3 scripts/validate.py
lockf -k /tmp/polymer-atlas-heavy.lock python3 scripts/check_row_loss.py --base origin/main
python3 scripts/check_evidence_binding.py --provenance-since origin/main
```

`PACKET.sha256` pins the source proposal inputs. `CAPTURES.csv` records the exact original or refreshed live proof receipts. `ARCHIVES.csv` maps the admitted local packet IDs to their public capture references and supplies the archived proof digests and offsets. `INPUTS.sha256` gives the private by-hash inputs used by the final proofs. The replay rejects a planted shifted offset. The hosted binding gate separately applies the exact-byte check to the PR merge ref.
