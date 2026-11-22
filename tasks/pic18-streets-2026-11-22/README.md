# PIC-18 streets for sites with no street, 2026-11-22 (lane atlas-w22-streets)

Packet only: nothing under `data/` changes, no PR. Base `393c3895`. Owner pick 2026-11-22 ("Yes, those 121"). Controller thr_9i2c6byhcz. **Unit for every count: site records in the frame below.**

## Frame
Active tier A-C Ohio sites in a PIC-18 county whose organization has no size band (site bands and `employee_band_ohio` all unknown: 443 organizations, 465 sites) and whose `street_address` is blank: **121 sites of 118 organizations = the owner's 121, no difference.** `check.py` recounts it without `frame.py`'s code. 100 of the 121 have a website on the record (bare domains get `https://`; one value carries trailing note text, its first token is the URL). Canary = first 25 of `random.Random(20261122).shuffle` over sorted site_ids (`shuffle_rank` in `frame.csv`); the canary was reported first and the controller said go.

## Result
**Streets VERIFIED: 8 of 121 (6.6%; 95% Wilson 3.4%-12.6%).** Canary: 3 of 25 under the main-text rule. By route (how many of the 121 each settles):
| Route | Settles | Notes |
|---|---|---|
| Live own page (main text) | 5 | CF Extrusion, Profile Rubber, R&S Technologies, Silgan/Cobra Macedonia, 3D Dental |
| 1 Archived copy (Wayback, dated 2024-11-22 or later, live site unreadable) | 3 | Amros (capture 2026-05-06), Prime Plastics (2026-05-10), EnergyEne (2026-04-10) |
| 2 Rendered (Firecrawl, main content) | 0 | 5 pages over 3 sites loaded, none states a street; 2 sites (Raydar, Sherwood) failed all engines, 1 (Veretec) timed out. RealTruck's HTTP 202 empty page (2 sites) was treated as a wall and not tried |
| 3 Address image (tesseract) | 0 | one site (Dal-Little) has a footer GIF; it reads only a phone number and an email, no address (not transcribed); no other address image found by a scan of the stored pages' img tags |
| 4 Official page by search | 0, NOT RUN | the SearXNG tool answered "Server busy" on every call (5 attempts over the session) |
| Own government files (OSHA, EPA) | not mine | per the controller; the size-sprint lane |
8 packet rows; the 8 streets are listed for that lane in `packet.csv`.
**Holds: 113, by reason:**
| Reason | Sites |
|---|---|
| NO_ADDRESS_ON_PAGES_READ | 30 |
| NO_WEBSITE_ON_RECORD | 22 |
| ADDRESS_OUTSIDE_MAIN_TEXT | 9 |
| ADDRESS_ELSEWHERE | 8 |
| THIN_PAGE | 6 |
| TLS_ERROR | 5 |
| TWO_CANDIDATES | 5 |
| CITY_DIFFERS | 5 |
| MAILING_LABEL | 3 |
| NO_DNS | 3 |
| HOME_404 | 3 |
| HQ_LABEL_ON_PLANT | 2 |
| TIMEOUT | 2 |
| HOME_HTTP_202 | 2 |
| ROBOTS_DISALLOWS | 2 |
| SIBLING_SAME_CITY | 1 |
| ADDRESS_NOT_IN_VISIBLE_TEXT | 1 |
| ROBOTS_HTTP_403 | 1 |
| ZIP_CONFLICT | 1 |
| PHONE_INTERLEAVED_IN_ADDRESS | 1 |
| CONNECTION_REFUSED | 1 |

Reading of the reasons: NO_WEBSITE_ON_RECORD (22) and the unreachable classes (NO_DNS, TLS_ERROR, TIMEOUT, CONNECTION_REFUSED, ROBOTS_HTTP_403, HOME_404, THIN_PAGE, HOME_HTTP_202, ROBOTS_DISALLOWS: 25 together) are availability facts, never evidence of absence; `wayback_availability.csv` records, for each, whether Wayback holds a capture and its date, 31 organizations were checked, 30 have a capture, 22 of those are dated 2024-11-22 or later, and for 12 a capture of the home page (and up to 5 links) could be read (route 1; the other captures were error pages or redirects; a capture with no street states none). `record_health_leads.csv` lists the 6 sites whose record website does not resolve or returns 404 (a stale-website lead, not a closure). ADDRESS_OUTSIDE_MAIN_TEXT (9): the street is stated in a footer or header, not main text; see owner question 8.

## How many of the 8 can the size sprint then match
**0 of 8** under the size sprint's own rule (`size_rerun.py` copies the sibling lane's `build.py` and its cached OSHA ITA, inspection and Form 5500 extracts into a temp tree with the 8 streets written in; `size_rerun.csv`): name_not_held 3 (Profile Rubber, Amros, 3D Dental), stale_over_5_years 3 (R&S, Silgan, Prime Plastics: filings exist at the street under a held name, all before 2021-11-22), no_filing_at_street 2 (CF Extrusion, EnergyEne). Expected change in the size-unknown count of 443 organizations: 0. The sibling lane's code was re-run twice during the session and changed in between (frame 465 then 463 sites); the 0 held on both runs.

## Method as run
- **Fetch:** `fetch.py`, adapted from the sibling web-canary lane's (branch `agent/claude-code/pic18-web-canary-2026-11-22`): record website, then at most 5 same-domain links found on fetched pages (contact, location, about first); never a guessed URL; robots.txt per host and hop (a robots.txt that cannot be read closes the host); 1.2 s per host; one retry after a transport failure, **on HTTP/1.1 sending the bare token `AtlasSiteCorpus/1.0`** (the robots agent) after curl exit 52, 56 or 92. **Disclosure:** the controller's instruction was "the same declared user-agent"; I found that the `Mozilla/5.0 (compatible; AtlasSiteCorpus/1.0)` form is what these servers reset (plain probes: 200 only for the bare token or curl's default), so the retry sends the bare token, which is our declared identity without a browser-style prefix. It recovered 5 organizations. If the controller reads that as a second user-agent, the 5 are SITE-000147, 000239, 000396, 000524 and 001575, and their rows should be re-judged. Earlier plain probes of robots.txt files (7 hosts, by `curl` from the shell) are not in `fetches.csv`.
- **Reading:** mine (Sonnet 5.5) over `screen.py`'s display of street-shaped strings (outputs in the store, not the repo, because the context windows can show names); every VERIFIED and every address hold in `verdicts.csv` was read from context; `build.py` computes offsets and runs the rule gates that do not depend on my reading (a same-operator sibling in the same city, another candidate street in the site notes or in the earlier street lanes' leads, dedupe over every site shard, archive present, quote in main text).
- **Quote text = main text (controller ruling 2026-11-22):** `captext.main_text` (documented in its docstring so the follow-up PR can reproduce it): decode the capture bytes as UTF-8; parse with `fetch.Page` (drops script, style, noscript, nav, header, footer, aside, svg, form, select, button, iframe, template, head and menu-like classes; block elements start a new line; falls back to a tag-only pass if under 200 characters); join the lines with one space; collapse whitespace. `offset` and `length` index that string. Replaces the binding gate's whole-page `capture_text` (#467 c5d886be), which I first mirrored.
- **Archive (SCHEMA 4.22):** each cited live page was saved with Wayback Save Page Now (`archive.py`; `archive.csv`); `capture_sha256` is the hash of the archived original bytes after undoing the gzip Content-Encoding Wayback serves them with (`archive_served_sha256` is the hash as served; the gate's `fetch_url` does not decode: the controller has this on the follow-up list). R&S failed once (HTTP 523) and succeeded on the later retry. For archived-copy rows the capture is Wayback's own copy (`wayback.py`, stored decoded), `archive_url` is its capture URL, `observed_date` its date.
- **County** is the record's, unchanged, as the earlier street lanes did; the page gives a city, not a county (R&S, Bellevue: unproven).

## Owner questions (listed, not settled)
1. Does a group or parent page speak for the entity? (no row rests on it now; ChemSpec fell to ADDRESS_OUTSIDE_MAIN_TEXT)
2. May a page's structured-data (JSON-LD) address be cited when the visible text lacks it? Held: Aropha (SITE-002067).
3. Is "Shipping/Receiving" or "Shipping Address" the site's physical address (CF Extrusion, Profile Rubber)? Proposed as physical; both pages also give a P.O. Box as the mailing address.
4. Same-operator siblings and a second candidate street are held, not ruled (Perry Fiberglass SITE-000519 with SITE-000520; CSU, Grove Bags, STERIS x2, C4 Polymers, Full Circle).
5. Campus/HQ labels: MacDivitt and CleveMed "Corporate Headquarters/Office" on plants are held as HQ_LABEL_ON_PLANT (the 2026-11-17 lane's rule).
6. Postal city versus municipality: Kenda and Eagle Plastics (page says North Canton, record says Green), NSL (page Cleveland, record Warrensville Heights): held CITY_DIFFERS; ZIPs agree.
7. May a quote carry a company's phone/fax lines when they sit between street and city (Baker Plastics)? AGENTS section 6 (2026-11-22) allows it incidentally; my brief said cut. Held.
8. May a street in a page footer or header count? Controller ruled main text only; 9 sites state their street only there (`ADDRESS_OUTSIDE_MAIN_TEXT`: ChemSpec, CSU, Chem-Materials, VisionAir, FlexLink, PKG, Precision Polymer Casting, ECM, Triangle Chemical).
9. SCHEMA: I judge **§4.13 needs a dated sentence** to let `own_site` evidence cite a Wayback capture (the binding gate's own-site test is a host match, so an archive URL fails it) and to name `source_route` in `claim_detail`; §4.22 can stay. Not written: the controller asked to be told first.
10. The record zip field holds a street number at SITE-001798, 001806 and 001793 (ZIP edit out of scope).

## Checks
`python3 tasks/pic18-streets-2026-11-22/check.py` (reads the store; arg overrides): independent frame recount 121; every site attempted exactly once across packet and holds; packet captures re-hash; quote at offset in main text; street, whole-word city and ZIP in the quote; no phone number or email in a quote; source URL on the record's domain; archive URL in SCHEMA 4.22 form for the cited URL; archived-copy rows dated 2024-11-22 or later with the timestamp equal to the observed date and the live home page not readable; seven planted defects (paraphrase, shifted offset, bad hash, phone in quote, off-domain source, two real addresses from another city) each caught. Result: `frame=121 (independent recount 121) attempted=121 packet=8 holds=113 fetch rows=480; planted defects caught 7/7`.

## Not checked
No second family has read any row (the gate needs one per web row, and web rows have no admission path until the follow-up merges); no county was derived from a page; links beyond the first 6 fetches; PDFs; image text other than one GIF; route 4 not run; whether any quoted address is still current; the 9 footer-only streets and the 25 unreachable sites' live pages.
First user: the controller reviewing this packet; non-use by 2026-11-29 is a non-use finding. Files: `frame.csv`, `packet.csv`, `holds.csv`, `dedupe_leads.csv`, `fetches.csv`, `archived_fetches.csv`, `archive.csv`, `wayback_availability.csv`, `record_health_leads.csv`, `size_rerun.csv`, `verdicts.csv` (hand readings), `fetch.py`, `captext.py`, `screen.py`, `build.py`, `archive.py`, `wayback.py`, `check.py`.
