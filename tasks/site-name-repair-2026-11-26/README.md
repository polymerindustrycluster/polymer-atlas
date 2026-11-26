# Site-name repair (owner rulings 2026-11-25 18:16 and 20:12)

Built by: Claude Code Sonnet 5.5

Claimed in `tasks/QUEUE.md` by the controller for P1. First user: the audit 13 smoke readers' next draw; non-use is a finding if the 2026-12-15 re-grade shows no change in site-name contradictions.

Audit 13 smoke attempt 3 stopped at 20 of 40 records with 2 contradicted `site_name` cells: the site is named for a legal entity or its parent while the operator's own page prints another name at that street. Owner ruling 2026-11-25 20:12, "Name on the door": `site_name` becomes the name the operator's own page prints at that street wherever the held name differs by more than a legal-form word (legal entity, parent, predecessor, brand or division); the old name stays in the site's `notes`; a legal-form-only difference stays. This PR applies it where the binding gate can admit the proof.

## What changes (6 `site_name` cells, `data/sites_OH.csv`; 6 own-site evidence rows, `data/evidence_sites_OH.csv`)

| Site | Held name | New name | Own page (capture) |
|---|---|---|---|
| SITE-000063 | Akron Gasket — Tallmadge | Akron Gasket and Packing Enterprises — Tallmadge | https://akron-gasket.com/contact/ |
| SITE-000081 | Novex, Inc. — Barberton | Novex Operating Company, LLC — Barberton | https://novexinc.com/ |
| SITE-000279 | Carlisle Polyurethane Systems — Berea | Carlisle TyrFil — Berea | https://carlisletyrfil.com/contact/ |
| SITE-000401 | IMS Industrial Molding Supplies — Chagrin Falls | IMS Company — Chagrin Falls | https://imscompany.com/contact-us/ |
| SITE-000646 | THIRD DIMENSION, INC. — Geneva | Third Dimension Division — Geneva | https://gbp.com/locations/ |
| SITE-002008 | Stroup & Son Ltd | Stroup Belting | https://www.stroupbelting.com/ |

Nothing else changes in the data: no other site column and no organization row. The one other edit is the `notes` of each renamed site: six appends of one sentence, `Former site_name (renamed by site-name-repair-2026-11-26, <ruling>): <old site_name>.`, after the existing notes (`check.py` requires exactly that append and no other notes change). Each evidence row is `claim_type=existence`, `source_class=own_site`, `supports_A`, and its quote holds the printed name and the held street in the page's main text. Five rows have `observed_date` equal to their capture date, 2026-11-26 (the Wayback timestamp is UTC, a day after the local fetch). Stroup Belting (SITE-002008) differs: its `observed_date` is 2026-11-25, the day the live page was fetched and read, and its proof is the live page itself, captured 2026-11-26 (UTC), not a snapshot. Its archive link still names the existing snapshot of 2026-11-17, whose bytes equal the live page's (same SHA-256 and the same quote offset), but that snapshot answered HTTP 302 to the gate's fetcher on two CI runs, so it cannot serve as the proof capture. The live page returned the same bytes on every fetch here. Each row has a `BINDING_PROOF.csv` line (capture hash, offset, a Codex reading, `VERIFIED`); the readings are in `READINGS.jsonl`. For five rows the proof capture is the page's Wayback `id_` snapshot, made by Save Page Now on 2026-11-26 UTC, and the `archive_links.csv` row names the same snapshot; for Stroup Belting the proof is the live page (see below) and its archive link names the existing snapshot of 2026-11-17: a live page can change before the gate replays it at merge (the gbp.com page changed once during this work), an archive snapshot cannot. The bytes are in the shared store at `provenance/site-name-repair-2026-11-26/captures/` and named in `INPUTS.sha256`. Before archiving, each page was fetched twice with the gate's own fetcher and returned the same bytes.

## What did not change, and why (`CLAIMS_CHECKED.csv`: 50 rows: 6 corrected, 44 held)
The finder (`candidates.py`) found 115 candidates among 727 PIC-18 sites (active, tier A-C, street held). A rename needs the printed name and the held street together in the main text the binding gate reads (`capture_text` leaves out headers, footers and navigation), a page that returns 200 with the same bytes on two fetches (the gate does not follow redirects), and a page on the record's held website. Pilot reads under the rule that were evidence-clean but fail the gate:
- name and street only in a footer or a header: SITE-001568 (NextStep Arthropedix), SITE-001776 (HAR Adhesive Technologies), SITE-000672, SITE-000889, SITE-001846, SITE-001843, SITE-000310, SITE-000466.
- bytes differ between two fetches: SITE-000263 (Blade-Tech Holsters), SITE-001801 (SealMaster), SITE-000361.
- SITE-001778 (known answer): its held website `tensiletestinginc.com` redirects to `tensile.com`; the gate does not follow a redirect and `tensile.com` is not the held website's domain. It needs the organization website updated first.
- SITE-000439: the page prints two entities at the street.
- SITE-000273 and SITE-000327: no name printed at that street, and a sentence, so held.
The other 50-odd candidates print the held name, a short form, an abbreviation or a section label (see `PILOT.csv`), or were not read.

## Check and replay
`python3 tasks/site-name-repair-2026-11-26/check.py` (needs the store mount, or `--store DIR`). It asserts, against the merge base: the changed `site_name` cells, the corrected claims, the PACKET rows and the batch evidence rows are the same site IDs, each listed once; a renamed site's `notes` is the old notes plus exactly the one old-name sentence, and any other site's `notes` is unchanged; no other site column changes; each evidence claim names the new `site_name` and its quote holds that name (without the locality suffix) and the held street; each site named in this README is in `CLAIMS_CHECKED.csv` and the README's row counts match the file; each capture replays at its offset. Twelve planted defects are each rejected (an unclaimed change, a claim without a change, a wrong name, a missing or duplicated PACKET entry, a missing evidence row, a lost note, an omitted former name, a new name absent from the quote, a wrong README count, a README site with no claims row, a shifted offset). Exit status: 0 only when everything was inspected, 1 on a failure, 2 when something could not be inspected: `--no-store` skips the capture replay and the shifted-offset plant, prints `NOT_INSPECTED` with the count, and exits 2.
`build.py --apply` replays the frozen `PACKET.csv`. `candidates.py --selftest` is the finder's known-answer test. The finder, screen, live capture and reader scripts (`candidates.py`, `screen.py`, `live.py`, `capture.py`, `archive.py`, `archive_proof.py`, `reader.py`) are kept for the audit trail.

## Follow-ups
- `DECISIONS.md` records the two rulings and defers the list of held sites to this README. A held site is not a decision, but the owner may want that list in the ledger.
- `check.py` does not re-validate `BINDING_PROOF.csv` or `archive_links.csv`; the binding gate, V-59 and V-66 do.

## Limits
- Held-name matching is a text pattern; recall beyond the two known answers is unmeasured.
- The own-site proof date must fall within 30 days of the merge commit.
- A name a page prints beside a street is the operator's own page only by the held website; no source states the link between the old and the new name except where the page does (not stated for most rows).
