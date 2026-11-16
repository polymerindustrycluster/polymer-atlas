#!/usr/bin/env python3
"""Regenerate README.md from verdicts.csv / witnesses.csv so every published count is computed."""
import csv
from collections import Counter
v = list(csv.DictReader(open('verdicts.csv'))); w = list(csv.DictReader(open('witnesses.csv')))
vc = Counter(r['verdict'] for r in v); wc = Counter(r['work_done'] for r in v)
read_leads = sum(r['work_done'] in ('own-site', 'search') for r in v)
witness_leads = len({r['rank'] for r in w})
tbl = '\n'.join(f"| {r['rank']} | {r['verdict']} | {r['disposition']} | {r['target_record']} | {r['work_done']} | {r['settling_fact'].replace('|', '/')} |" for r in v)
text = f"""# PIC-18 discovery, real research pass (DISC2) — 2026-11-16

Claim: atlas-w16-disc2 (integrator for exactly this scope). First user: PIC membership prospector; non-use finding due 2026-12-15. Draft packet for controller review, not a completion or merge approval.

## Result
{len(v)} held leads adjudicated (unit: ranked lead names from PR #356's frozen frame: 80 ranked names minus its 8 DUPLICATE_OF; names come from privacy-filtered PPP/SAM lead lists and are not published here). **Zero were VERIFIED, so zero organization, site or evidence rows were applied.** data/ is untouched and the ID blocks ORG-014300..014499, SITE-020400..020599, EVD-391000..392999 are unused. The pass found that the first lane's guessed-domain dedupe had missed {vc['DUPLICATE_OF']} companies the Atlas already holds, and cleared {vc['REJECT']} leads as having no polymer link. It did not reach a create for any not-held company inside the time box.

## Counts (unit: held leads adjudicated)
Verdicts, recomputed by check.py: DUPLICATE_OF {vc['DUPLICATE_OF']}, STILL_UNCERTAIN {vc['STILL_UNCERTAIN']}, REJECT {vc['REJECT']}, VERIFIED {vc['VERIFIED']}. Applied 0; held {len(v)}.
- DUPLICATE_OF {vc['DUPLICATE_OF']}: ranks 1, 28, 39, 41, 43, 80 map to ORG-000416/SITE-000445, ORG-000117/SITE-000116, ORG-000336/SITE-000357, ORG-000215/SITE-000228, ORG-001597/SITE-001669, ORG-000140/SITE-000140. No existing row is edited (rule 13); these are alias follow-ups. Ranks 28, 39, 43, 80 came from reading each company's real own site (the first lane's guessed domains were wrong or absent); rank 1 and 41 from the street check.
- REJECT {vc['REJECT']}: the own page states a business with no polymer link, quoted in witnesses.csv: Hilltop Energy (drill and blast), Olmsted Transportation (car hauling, WA/OR), Deters Law, Harbor Industrial Services (port services), Auto Dealer Designs, Chagrin Valley Soap & Salve.
- STILL_UNCERTAIN {vc['STILL_UNCERTAIN']}: ranks 18, 32, 52, 59, 64, 65 share a street or group with a held record; ranks 7, 34, 36, 37, 58 are chemical, metal or wire businesses needing an owner scope ruling (recommendation: out of scope); ranks 47, 69, 75, 76 look like polymer companies but no own page could be read; the rest keep the first lane's generic hold.
Work done (verdicts.csv `work_done`): own-site read {wc['own-site']} leads, search only {wc['search']}, dedupe only {wc['dedupe']}. {len(w)} stored quotes on {witness_leads} leads.

## Dedupe
All {len(v)} went through `atlas.dedupe` (name, street, city; all five AGENTS 3 steps), a street search of site notes and a first-token name screen of organizations and sites (dedupe2.json in controller persistence). The CLI misses a street that sits only in held site notes (ranks 18 and 59), exactly the first lane's MVP case; both are holds with that fact.

## Limits (about 35 minutes)
{read_leads} of {len(v)} leads got a search or own-site read; the other {wc['dedupe']} carry the first lane's generic hold. No create was possible because every plausibly polymer, not-held lead had no readable own page: Command Plastic (own site: TLS handshake failure and HTTP 409), Genesis Plastic Technologies (directory domain does not resolve), R.C.A. Rubber (rcarubber.com answers with a redirect stub), Globe Plastic Technologies (no company found). A failed fetch is availability, never absence. Search results and directory listings were used only to find leads and real domains; nothing from them, SAM or PPP is recorded.

## Proposed follow-ups (not in this PR)
1. R.C.A. Rubber Co (rank 47, Akron, sheet rubber flooring per directories; not held): read a current own page or a federal filing, then create at tier C.
2. Command Plastic Corp (rank 75, Tallmadge, vinyl packaging) and Genesis Plastic Technologies LLC (rank 69, Solon, injection molding): read own pages by another route, then create.
3. Alias notes for the six DUPLICATE_OF ranks, if the owner wants them (needs a column edit this lane may not make).
4. Method fix for any lead lane: dedupe by name, street and site notes before guessing domains.
5. Owner scope rulings for the chemical blenders, metal finishers and wire makers in the frame (ranks 7, 34, 36, 37, 58).

## Files
verdicts.csv (all {len(v)}), witnesses.csv (URL, stored raw file, sha256, quote), make_packet.py (regenerates both and validates every quote), make_readme.py (regenerates this file), build.py (idempotent; asserts zero VERIFIED and unused ID blocks), check.py (recomputes counts, yield {len(v)} vs frame 80 minus 8, re-verifies quotes and hashes, checks held-record facts, proves failure on 5 injected defects), prior_pr356_verdicts.csv (copy of the first lane's verdicts, the independent count). Raw pages stay in controller persistence (S/persist/pic18-discovery-2/raw and S/persist/pic18-discovery-leads) per contract rule 8.

## Applied / held register
| Rank | Verdict | Applied / held | Target | Work | Settling fact |
|---|---|---|---|---|---|
{tbl}
"""
open('README.md', 'w').write(text)
