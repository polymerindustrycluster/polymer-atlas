# PIC-18 streets for sites with no street, 2026-11-22 (lane atlas-w22-streets)

Packet only: nothing under `data/` changes, no PR. Base `393c3895`. Owner pick 2026-11-22 ("Yes, those 121"). Status: **CANARY (25 sites) done; the full run waits for the controller's go.**

## Frame (unit: site records)
Active tier A-C Ohio sites in a PIC-18 county, organization with no size band (site bands and `employee_band_ohio` all unknown: 443 organizations, 465 sites), `street_address` blank: **121 sites of 118 organizations = the owner's 121, no difference.** Recounted independently in `check.py` (not `frame.py` code). Websites: 100 of 121 on the record (bare domains get `https://` added; one record value carries trailing note text, its first token is the URL; 3 `none_found`, rest blank). The sibling lane's `no_street_sites.csv` is not on a pushed branch yet; its README gives the same 121.
Canary = first 25 of `random.Random(20261122).shuffle` over frame site_ids sorted (`shuffle_rank` in `frame.csv`).

## Canary result (25 sites)
**VERIFIED 5 of 25 (20%; 95% Wilson 8.9%-39.1%)**; 4 of the 5 have an archive capture, **R&S (SITE-001150) could not be archived** (Wayback save returned HTTP 523 twice: origin unreachable from Wayback), so it cannot be minted until archived (V-66). Holds 20 of 25 by reason: website unavailable 9 (robots.txt or connection failure 7, script-rendered page 1, HTTP 404 on the record URL 1), no address on the pages read 3, mailing label 2, two candidates on record 1, same-operator sibling in the same city 1, HQ label on a plant 1, address in another state 1, address only in structured data 1, no website on the record 1. Dedupe: no verified street belongs to another site in the same city; one different-city key match (350 State St, a Rocky Mount record) is listed non-blocking in `dedupe_leads.csv`.
Projection to the frame: about 24 of 121 (range 11-47 at the interval), for planning only; the canary is 25 draws.
**Could the size sprint then match them?** `match_screen.py` (street-equal filings in the size lane's cached OSHA ITA, inspection and Form 5500 extracts, same city or ZIP, window from 2021-11-22, name NOT tested): 2 of the 5 have a candidate filing (SITE-000297 ITA 2021, establishment named "Macedonia"; SITE-000292 two ITA rows of another company at the street, "US OH Canton Office"). Neither name is the held name, so I expect **0 strict matches** from the canary. This is an upper bound screen, not the size lane's matcher.

## Verified rows (`packet.csv`; quotes are what the capture says)
| site | street | quote source |
|---|---|---|
| SITE-000056 CF Extrusion | 2748 2nd Street Suite C, Cuyahoga Falls 44221 | own home page, "Shipping/Receiving" (separate P.O. Box) |
| SITE-000562 Profile Rubber | 350 State Street Building #7, Wadsworth 44281 | own contact page, "Shipping Address" (separate P.O. Box) |
| SITE-001150 R&S Technologies | 2474 State Route 4, Bellevue 44811 | own contact page, plain address block; **not archived**; the page gives a city, not a county, so the record's county (Huron) is carried and unproven |
| SITE-000297 Silgan Dispensing (site named Cobra Plastics) | 1244 Highland Rd, Macedonia 44056 | operator's locations page; page does not name Cobra (the site notes say "former Cobra Plastics") |
| SITE-000292 ChemSpec | 4450 Belden Village St. NW, Suite 507, Canton 44718 | parent group's page titled ChemSpec Ltd., contact block; a name and phone before it are cut |

## Method as run
`fetch.py` is the sibling web-canary fetcher (branch `agent/claude-code/pic18-web-canary-2026-11-22`) with only these edits: store, frame, link priority contact/location/about, one run per organization (its sites share captures), a bare-domain scheme. Record URL plus at most 5 same-domain links found on fetched pages (never a guessed URL), robots.txt per host and hop, 1.2 s per host, one retry after a transport failure. 102 fetch rows (68 page requests) in `fetches.csv`; raw captures, extracted text and archive copies in `S/persist/streets-2026-11-22/`, outside the repo. Reading is mine (Sonnet 5.5): `screen.py` finds street-shaped strings in page text; every verdict was read from the context, hand-written in `verdicts.csv`; `build.py` then computes offsets and runs the rule gates (same-city sibling, other candidates in the site notes or the earlier street lanes' leads, dedupe over every site shard) so they do not depend on my reading.
- **Quote text is the binding gate's `capture_text`** (visible text of the whole HTML, whitespace collapsed; #467 head c5d886be), not the main-text extraction the task named: a footer address (Cleveland State was one) is excluded from main text, and offsets must index what the gate indexes. `captext.py` mirrors the gate's function.
- **Archive:** each cited page saved with Wayback Save Page Now at capture (`archive.csv`); the offset is computed on the archived original bytes, and the packet carries `archive_served_sha256` too. **Fault found in the gate as written:** Wayback serves the original bytes with their gzip Content-Encoding, and `fetch_url` in #467 does not decode, so for 5 of the 6 pages archived (gzip-served) the gate would hash compressed bytes and index garbage text; it must gunzip (gzip magic) before hashing and `capture_text`. I hash the decoded bytes (`capture_sha256`) and record the served bytes' hash.
- County: the record's county, unchanged, as the earlier street lanes did; not derived from the page.

## Owner rulings and decisions this needs (listed, not settled)
1. Does a group or parent page speak for the entity (ChemSpec, from the web canary's ruling 1)? Row proposed, flagged.
2. May a page's structured data (JSON-LD) address be cited when the visible text lacks it? Held: Aropha (SITE-002067).
3. Is "Shipping/Receiving" or "Shipping Address" the site's physical address (CF Extrusion, Profile Rubber)? Proposed on the reading that it is physical.
4. Controller: may the fetcher retry under a different user agent? Two sites (Philpott, Beacon/clevemed) answered curl's default user agent with HTTP 200 on a plain probe (not stored in `fetches.csv`: 7 probes of robots.txt files at 7 hosts, including these 2) but reset under the declared `AtlasSiteCorpus` one. Left as availability holds.
5. Campus/HQ labels: Cleveland State's two streets (own site 2121 Euclid Avenue; registry 2151 Euclid Ave in the site notes) and MacDivitt's "Corporate Headquarters" are held, not ruled.

## Checks
`python3 tasks/pic18-streets-2026-11-22/check.py` (reads the store; arg overrides): independent frame recount 121; every packet and hold site is an attempted site exactly once; each packet capture re-hashes; quote at offset in `capture_text`; street, whole-word city and ZIP in the quote; no phone or email in a quote; source URL on the record's domain; archive URL in SCHEMA 4.22 form for the cited URL; seven planted defects (paraphrase, shifted offset, bad hash, phone number in quote, off-domain source, two real addresses from another city) each caught. Result: `frame=121 (independent recount 121) attempted=25 packet=5 holds=20; planted defects caught 7/7`.

## Not checked
No second family has read these rows (the gate requires one per web row); no parcel or geocode county; CSU's, MacDivitt's and the three "no address on the pages read" sites' other pages (links beyond the first 6 fetches); PDFs; script-rendered pages; whether any quoted address is still current.
First user: the controller reviewing this packet; non-use by 2026-11-29 is a non-use finding.
