#!/usr/bin/env python3
"""Regenerate README.md from verdicts.csv / witnesses.csv so every published count is computed.
No lead names, URLs or quotes are written here (owner ruling 2026-11-17); they live in controller storage."""
import csv
from collections import Counter
v = list(csv.DictReader(open('verdicts.csv'))); w = list(csv.DictReader(open('witnesses.csv')))
vc, wc, pc = (Counter(r[k] for r in v) for k in ('verdict', 'work_done', 'url_provenance'))
read_leads = sum(r['work_done'] in ('own-site', 'search') for r in v)
rank = lambda verdict: ', '.join(r['rank'] for r in v if r['verdict'] == verdict)
tbl = '\n'.join(f"| {r['rank']} | {r['verdict']} | {r['disposition']} | {r['target_record']} | {r['work_done']} | {r['url_provenance']} | {r['settling_fact'].replace('|', '/')} |" for r in v)
text = f"""# PIC-18 discovery, real research pass (DISC2) — 2026-11-16

Claim: atlas-w16-disc2 (integrator for exactly this scope). First user: PIC membership prospector; non-use finding due 2026-12-15. Draft packet for controller review, not a completion or merge approval.

## Result
{len(v)} held leads adjudicated (unit: ranked lead names from PR #356's frozen frame: 80 ranked names minus its 8 DUPLICATE_OF). Lead names, URLs and quotes are not published (owner ruling 2026-11-17); rank, verdict, held-record target and settling fact only, as in the first packet. **Zero were VERIFIED, so zero organization, site or evidence rows were applied.** data/ is untouched and the ID blocks ORG-014300..014499, SITE-020400..020599, EVD-391000..392999 are unused. The pass found that the first lane's guessed-domain dedupe had missed {vc['DUPLICATE_OF']} companies the Atlas already holds, and it did not reach a create for any not-held company inside the time box.

## Counts (unit: held leads adjudicated)
Verdicts, recomputed by check.py: DUPLICATE_OF {vc['DUPLICATE_OF']}, STILL_UNCERTAIN {vc['STILL_UNCERTAIN']}, REJECT {vc['REJECT']}, VERIFIED {vc['VERIFIED']}. Applied 0; held {len(v)}.
- DUPLICATE_OF {vc['DUPLICATE_OF']} (ranks {rank('DUPLICATE_OF')}): each maps to a held Atlas record in `target_record`. No existing row is edited (rule 13); these are alias follow-ups. Ranks 28, 39 and 43 were settled by reading the company's own site (the first lane's guessed domains were wrong or absent); ranks 1 and 41 by the street check with no own page read; rank 80 by name (borrower spelling variant) plus city only.
- REJECT {vc['REJECT']} (rank {rank('REJECT')}): the own page, whose domain a web search returned, states a business with no polymer link. Ranks 11, 62, 68, 77 and 79 were first drafted as REJECT on pages reached through the first lane's guessed domains; under the controller's rule against guessed addresses they are STILL_UNCERTAIN.
- STILL_UNCERTAIN {vc['STILL_UNCERTAIN']}: ranks 6, 17, 18, 19, 23, 32, 48, 52, 59, 64, 65 share a street, domain, name or group with a held record (target_record carries it); ranks 7, 34, 36, 37, 58 are metal, coating-removal, chemical-blending or wire businesses needing an owner scope ruling (recommendation: out of scope); ranks 47, 69, 75, 76 look like polymer companies but no own page could be read; the rest keep the first lane's hold.
Work done (`work_done`): own-site read {wc['own-site']} leads, search only {wc['search']}, dedupe only {wc['dedupe']}. {len(w)} stored witness quotes (hashes only here).

## Dedupe
All {len(v)} went through `atlas.dedupe` with name, street and city and no domain, so AGENTS 3 steps 2 to 5 ran for all of them; step 1 (domain) ran only for confirmed own-site domains and for the first lane's guessed-domain run, which proves nothing about identity. A street search of site notes and a first-token name screen of organizations and sites were added. The CLI misses a street that sits only in held site notes (ranks 18 and 59), exactly the first lane's rank 23 case; those are holds with that fact.

## Order and limits (about 35 minutes)
The brief said to work the frame in order; I did not. After one bulk dedupe pass I prioritised polymer-sounding names and leads whose guessed domain had a stored page, so a low rank may have had less attention than a high one.

{read_leads} of {len(v)} leads got a search or own-site read; the other {wc['dedupe']} carry the first lane's generic hold. No create was possible because no plausibly polymer, not-held lead had an own-site URL I could tie to it by name and location (ranks 47, 69, 75, 76). A failed fetch is availability, never absence.

## URL provenance
Every verdict row has `url_provenance`: `held-record` ({pc['held-record']}), `web-search` ({pc['web-search']}) or `none` ({pc['none']}). Per the controller's rule a URL is used only if it is on a held record, was returned by a search I ran, or is linked from a fetched page; the first lane's guessed domains are discarded, and check.py fails a witness on a `none` row. Before that rule reached me I fetched a few URLs I had constructed; none is cited. Search results and directory listings were used only to find leads and real domains; nothing from them, SAM or PPP is recorded.

## Proposed follow-ups (not in this PR)
1. Rank 47 (sheet rubber flooring per directories; not held): read a current own page or a federal filing, then create at tier C.
2. Ranks 69 and 75 (injection molding, vinyl packaging; not held): find an own-site URL by search, then read it and create.
3. Alias notes for the {vc['DUPLICATE_OF']} DUPLICATE_OF ranks, if the owner wants them (needs a column edit this lane may not make).
4. Method fix for any lead lane: dedupe by name, street and site notes before guessing domains.
5. Owner scope rulings for ranks 7, 34, 36, 37 and 58.

## Files
verdicts.csv (all {len(v)}), witnesses.csv (witness id, rank, sha256), make_readme.py, build.py (idempotent; asserts zero VERIFIED and unused ID blocks), check.py (recomputes counts, yield {len(v)} vs frame 80 minus 8, re-verifies quotes and hashes from private storage, scans every committed file for lead names and URL hosts from the private name list, checks held-record facts, proves failure on 8 injected defects). Names, URLs, quotes, the packet generator and the first lane's verdict copy live in controller storage (S/persist/pic18-discovery-2/private), as do raw pages (contract rule 8). Earlier commits on this branch still contain the names; history is not rewritten.

## Applied / held register
| Rank | Verdict | Applied / held | Target | Work | URL provenance | Settling fact |
|---|---|---|---|---|---|---|
{tbl}
"""
open('README.md', 'w').write(text)
