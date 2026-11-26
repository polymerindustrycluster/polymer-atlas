# Census audit of the CF Extrusion Technologies street fill

Label: claude-code note-street-lookup-2026-11-26
Result: PASS
Sample: Census of the one evidence row carrying this label in data/evidence_sites_OH.csv at merge 73488319. Replayed EVD-483296 and checked its linked street cell and archive row.
Reviewers: atlas-review-576-codex, GPT-6.2 Astra (OpenAI). Claude Sonnet built the batch.

The data tree and task folder at 73488319 had identical Git tree IDs to their counterparts at reviewed head 141c3e47. Against parent f921eba8, SITE-000056.street_address went from blank to “2748 2nd Street Suite C”. The only other data changes were the addition of EVD-483296 and its archive link. The number of active Ohio sites in PIC-18 at tiers A through C with a blank street fell from 152 to 151.

The stored contact page passed shasum -a 256 -c against INPUTS.sha256 before inspection. At offset 596 in the page's main text, the evidence quote replayed verbatim as “Shipping/Receiving 2748 2nd Street Suite C Cuyahoga Falls, OH 44221”. The mailing address is listed separately.

At the merge, python3 tasks/note-street-lookup-2026-11-26/check.py f921eba8 passed and caught all 14 built-in plants. Changing the filled street to Suite Z in a scratch copy made the same command exit 1. It named SITE-000056, gave the expected Suite C street and reported unit_differs.

## What this audit is not

The census covers the merged street claim and its pinned capture. The present-day address and other site records were outside its scope.
