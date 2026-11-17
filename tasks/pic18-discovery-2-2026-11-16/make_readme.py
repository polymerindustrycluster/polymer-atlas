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
{len(v)} held leads adjudicated (unit: ranked lead names from PR #356's frozen frame: 80 ranked names minus its 8 DUPLICATE_OF; names come from privacy-filtered PPP/SAM lead lists and are not published here). **Zero were VERIFIED, so zero organization, site or evidence rows were applied.** data/ is untouched and the ID blocks ORG-014300..014499, SITE-020400..020599, EVD-391000..392999 are unused. The pass found that the first lane's guessed-domain dedupe had missed {vc['DUPLICATE_OF']} companies the Atlas already holds, and cleared {vc['REJECT']} leads as having no polymer link (own page, same name). It did not reach a create for any not-held company inside the time box.

## Counts (unit: held leads adjudicated)
Verdicts, recomputed by check.py: DUPLICATE_OF {vc['DUPLICATE_OF']}, STILL_UNCERTAIN {vc['STILL_UNCERTAIN']}, REJECT {vc['REJECT']}, VERIFIED {vc['VERIFIED']}. Applied 0; held {len(v)}.
- DUPLICATE_OF {vc['DUPLICATE_OF']}: ranks 1, 28, 39, 41, 43, 80 map to ORG-000416/SITE-000445, ORG-000117/SITE-000116, ORG-000336/SITE-000357, ORG-000215/SITE-000228, ORG-001597/SITE-001669, ORG-000140/SITE-000140. No existing row is edited (rule 13); these are alias follow-ups. Ranks 28, 39 and 43 came from reading each company's real own site (the first lane's guessed domains were wrong or absent); ranks 1 and 41 from the street check, with no own page read; rank 80 from name (the lead spells it SPECIALY) plus city only.
- REJECT {vc['REJECT']}: Chagrin Valley Soap & Salve only (rank 74): its domain was returned by a web search for the lead's name and city, and its own page reads "Natural & Organic Skin Care". Ranks 11, 62, 68, 77 and 79 were first drafted as REJECT on pages reached through the first lane's guessed domains; under the controller's rule against guessed addresses they are STILL_UNCERTAIN with no own page tied to the lead.
- STILL_UNCERTAIN {vc['STILL_UNCERTAIN']}: ranks 6, 17, 18, 19, 23, 32, 48, 52, 59, 64, 65 share a street, domain, name or group with a held record (target_record carries it); ranks 7, 36, 37, 58 have an own page (URL from a search) showing a metal, coating-removal, chemical-blending or wire business, an owner scope ruling (recommendation: out of scope), and rank 34 is the same kind of question without an own page; ranks 47, 69, 75, 76 look like polymer companies but no own page could be read; the rest keep the first lane's generic hold.
Work done (verdicts.csv `work_done`): own-site read {wc['own-site']} leads, search only {wc['search']}, dedupe only {wc['dedupe']}. {len(w)} stored quotes on {witness_leads} leads.

## Dedupe
All {len(v)} went through `atlas.dedupe` with name, street and city and no domain, so AGENTS 3 steps 2 to 5 ran for all of them; step 1 (domain) ran only for the confirmed own-site domains here and for the first lane's guessed-domain run, which proves nothing about identity. A street search of site notes and a first-token name screen of organizations and sites (dedupe2.json in controller persistence). The CLI misses a street that sits only in held site notes (ranks 18 and 59), exactly the first lane's MVP case; both are holds with that fact.

## Order and limits (about 35 minutes)
The brief said to work the frame in order; I did not. After one bulk dedupe pass I prioritised polymer-sounding names and leads whose guessed domain had a stored page, so a low rank may have had less attention than a high one.


{read_leads} of {len(v)} leads got a search or own-site read; the other {wc['dedupe']} carry the first lane's generic hold. No create was possible because no plausibly polymer, not-held lead had an own-site URL I could tie to it by name and location: Command Plastic and Genesis Plastic Technologies appear only in directories, R.C.A. Rubber's directory-listed domain answers with a redirect stub, Globe Plastic Technologies was not found. A failed fetch is availability, never absence. Lead names and verdicts.csv `own_site_name` values are published here although the first lane withheld names; the controller should decide whether to keep them. Search results and directory listings were used only to find leads and real domains; nothing from them, SAM or PPP is recorded.

## URL provenance
Every verdict row has `url_provenance`: a held-record website, a web-search query and result URL, or `none`. Per the controller's rule, a URL is used only if it is on a held record, was returned by a search I ran, or is linked from a fetched page; the first lane's guessed domains are discarded, and check.py fails a witness on a `none` row. Before that rule reached me I fetched a few URLs I had constructed (advpolymer.com, suburbanplastics.com, lukeengineering.com, globeplastictech.com, advancedpolymercoatings.com, commandplastic.com/.net, srpindustries.com, genesis variants); none is cited or used as evidence.

## Proposed follow-ups (not in this PR)
1. R.C.A. Rubber Co (rank 47, Akron, sheet rubber flooring per directories; not held): read a current own page or a federal filing, then create at tier C.
2. Command Plastic Corp (rank 75, Tallmadge, vinyl packaging) and Genesis Plastic Technologies LLC (rank 69, Solon, injection molding): read own pages by another route, then create.
3. Alias notes for the six DUPLICATE_OF ranks, if the owner wants them (needs a column edit this lane may not make).
4. Method fix for any lead lane: dedupe by name, street and site notes before guessing domains.
5. Owner scope rulings for the chemical blenders, metal finishers and wire makers in the frame (ranks 7, 34, 36, 37, 58).

## Files
verdicts.csv (all {len(v)}), witnesses.csv (URL, stored raw file, sha256, quote), make_packet.py (regenerates both and validates every quote), make_readme.py (regenerates this file), build.py (idempotent; asserts zero VERIFIED and unused ID blocks), check.py (recomputes counts, yield {len(v)} vs frame 80 minus 8, re-verifies quotes and hashes, checks held-record facts, proves failure on 6 injected defects), prior_pr356_verdicts.csv (copy of the first lane's verdicts, the independent count). Raw pages stay in controller persistence (S/persist/pic18-discovery-2/raw and S/persist/pic18-discovery-leads) per contract rule 8.

## Applied / held register
| Rank | Verdict | Applied / held | Target | Work | Settling fact |
|---|---|---|---|---|---|
{tbl}
"""
open('README.md', 'w').write(text)
