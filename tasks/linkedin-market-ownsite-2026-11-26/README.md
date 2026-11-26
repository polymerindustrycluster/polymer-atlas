# LinkedIn pilot owners: own-site market fills

Built by: Claude Code (Anthropic)

Claimed by atlas-p2-linkedin-market-ownsite on 2026-11-25 (owner ruling 2026-11-25 20:51, "Leads only, refetch sites"). First user is Polymer Industry Cluster staff who read the Atlas market field on the public site. Check for use by 2026-12-20. Base `5164203c`.

## Result

**Seven `markets_served` values on three organizations, each from the organization's own page.** Unit and filter: organizations that hold an active tier A–C site in PIC-18 (792). Owners with a blank market (`python3 scripts/value_basis.py --summary`, 792 less owners with values): **303 before, 300 after.** Process and size are unchanged.

The LinkedIn reading pilot (`persist/linkedin-reading-pilot-2026-11-26`, outside the repo) found nine market values for five owners that two readers confirmed from LinkedIn text. LinkedIn text stays a lead. Each value was looked for on the owner's own domain, and a value merges only where an own-domain page states it. Own-site result, in values of the pilot's nine: **7 STATED, 2 NOT_STATED.**

| Owner | Values | Own page (immutable Wayback `id_` copy) | Evidence |
|---|---|---|---|
| ORG-001936 Rotocast Technologies | `plastics_rubber_processors` | `http://rotocastmold.com/`, 2026-05-16 | EVD-483150 |
| ORG-001497 Budzar Industries | `pharmaceutical_biotech`, `chemical_mining_metals_processing`, `food_processing_foodservice`, `plastics_rubber_processors` | `https://www.budzar.com/`, 2025-04-17 | EVD-483151 to EVD-483154 |
| ORG-000147 Chem-Materials | `plastics_rubber_processors`, `construction_building_products` | `https://www.chem-materials.com/`, 2025-03-30 | EVD-483155, EVD-483156 |
| ORG-001584 Green Innovations | held, NOT_STATED | live `www` services page and the 2026-07-17 home capture | none |
| ORG-001470 The Pittsburgh Paints Company | held, NOT_STATED | six own pages | none |

Each value has one `own_site` activity row (`supports_B`, label `claude-code linkedin-market-ownsite-2026-11-26`) whose head names exactly that value, a `BINDING_PROOF.csv` line, an `archive_links` row (V-66) and a generated `stated` row in `value_basis.csv` (the 7 added lines are the only `stated` change: 50 before, 57 after). Nothing else changes in `data/`: `check.py` diffs every organization row against the merge-base and allows only these three cells. The PR also adds the pilot's experiments row to `docs/ACQUISITION.md` and a claim line in `tasks/QUEUE.md`.

## The rule that decided STATED (one rule, applied to all five owners)

A market value is STATED only when the quote names the sector, industry or customer type as the one the company's products or services go to, in words that map to the tag with no outside knowledge beyond the tag's plain meaning. A product name, a material or waste handled, or a list of what the company makes does not state a market. If in doubt, NOT_STATED. The quote is 20 or more characters, exact, and replayed on the capture by `capture_text` in `scripts/check_evidence_binding.py`.

- **Rotocast:** "the industry's largest rotational molders turn to Rotocast Technologies" names the customer type (rotational molders, which are plastics processors).
- **Budzar:** the home page headline reads "delivers accurate process temperature control equipment to numerous industries" and the four lines under it in the same block list "Pharmaceutical / Chemical / Food", "Energy / Medical / Plastics", "Extraction / Semiconductor", "Defense / Rubber / Tire" (confirmed in the raw HTML: one slider block). Four of the pilot's values map to words in that list. The list also names energy, medical, extraction, semiconductor and defense, which this PR does not fill.
- **Chem-Materials:** "providing technical service and products to the Paint & Coatings, Inks, Adhesives, Sealants, Resin Synthesis, Plastics, Fiber Reinforced Composites, Industrial & Institutional, Agriculture, Construction, Paper, Rubber, and Lubricants industries" names the sectors; two of the pilot's values map to it. It also names agriculture and other sectors, not filled here.
- **Green Innovations, NOT_STATED:** the pages name a waste stream and the plastics handled ("all waste generated at an industrial level, specifically plastic scrap"), and a services list. No page names plastics or rubber processors, molders or converters as the customers.
- **The Pittsburgh Paints Company, NOT_STATED:** the brands page names a product line ("Liquid Nails Construction Adhesives & Caulk - Industry leader in construction adhesives") and one customer wording ("light industrial solutions for OEMs and custom coaters"). A product name is not a sector served. This is the closest call of the five; under a looser rule it would be a value, so it is held as a lead rather than rejected. Six own pages were read (`/brands`, `/mission-values`, `/where-to-buy` live on 2026-11-25; home, about and newsroom held from 2026-11-16), the lane's cap.

## Routes, and what ran

- **Rotocast:** the live page returned 200 and its bytes were equal across two requests 13 minutes apart, but they differ from the 2026-11-16 held capture. The proof therefore cites a Wayback copy, as #559 did for Sprayworks, so a later replay cannot see different bytes. I first cited the 2026-06-17 timestamp, which my fetcher read as 200; the binding gate's fetcher got HTTP 302 to the 2026-05-16 capture (`20260516172255`, original `http://rotocastmold.com/`), so the proof cites that resolved capture. Its page text is identical to the one Codex read (same quote, same offset 611); the capture's bytes are `41502933…` (the earlier bytes `e82101d5…` are not cited).
- **Budzar and Chem-Materials:** the live pages could not be read. `scripts/site_corpus.py`'s curl got exit 52 (empty reply) on HTTP/2, and again on HTTP/1.1 with the same declared agent and verification on. The proofs are the in-window Wayback copies (SCHEMA section 4.13: a capture within the two years ending on `observed_date` may stand in for a page that cannot be read).
- **Green Innovations:** the held website `https://green-innovate.com/` fails its certificate (curl exit 60, no matching subject name). Verification was never turned off. The `www` host serves the same site and was read; no fill follows.
- **Legs that did not run:** the Jina fallback was denied by the sandbox, and the headed-Chrome retry was not run (no Playwright, and headed Chrome needs the sandbox off). Neither would be evidence of the claim. The failed live routes are logged as UNAVAILABLE in `NEGATIVES.csv`.
- **Requests per owner (cap 6):** Rotocast 3 (two live, one Wayback), Budzar 4 (two live, two Wayback), Chem-Materials 4 (two live, two Wayback), Green Innovations 5, Pittsburgh Paints 6. CDX lookups (one per page or domain) and the Wayback reads went to `web.archive.org`. No second user agent, no cookie, no TLS bypass.

## Readings

I (Claude Sonnet 5.5) built the rows. The reading the gate counts is by **OpenAI GPT-6.2 Astra (Codex)**, 7 of 7 VERIFIED on 2026-11-25, from a packet that held the rule, the page text and the quote and nothing from LinkedIn (`READS.csv`, sha256 `5fddd0a0…b543`, a copy of the controller's file). The Codex reader did not see the two held owners. `build.py --apply` applies only rows with a VERIFIED line in `READS.csv`.

## Check

`python3 tasks/linkedin-market-ownsite-2026-11-26/check.py` is the named check (offline; it replays the three pinned captures from `atlas-store/provenance/linkedin-market-ownsite-2026-11-26/captures/`). It asserts that the `corrected` lines of `CLAIMS_CHECKED.csv` equal the market cells the PR changes, owner by owner and value by value, and it passes on the clean tree and catches all 12 planted defects: a corrected line for an unchanged cell, a changed cell with no corrected line, a cell value no evidence row names, a held owner's cell filled, another organization column changed, a quote offset that is wrong, capture bytes that differ, a reader of the builder's family, a reading that is not VERIFIED, a claim edited after its reading, a value outside the vocabulary, and a missing archive line. `scripts/validate.py` and `scripts/check_evidence_binding.py --new-since origin/main` were also run (results in the PR description).

## Not checked, and limits

- The gate replays bytes and the quote. Whether a page states a value rests on two readers and the rule above. Budzar's four values rest on one slider string, and `capture_text` joins its separate paragraphs; the raw HTML shows them in one block under the headline.
- `cmc@chem-materials.com` is in the Chem-Materials capture (a company mailbox, the company's initials). `build.py` names it as the one exception to its individual-email scan (`MAIL_EXCEPTION`); no quote carries it. The site also has `/profiles/<name>/` staff pages; none was read or stored.
- A Wayback copy is a copy of one page on one day: Budzar's and Chem-Materials' pages may have changed since 2025.
- Rule 5 (AGENTS section 2a): the label `claude-code hq-blank-city-2026-11-25` (#563) has no `AUDIT.md` on main. The repair PR carries it; `pr-rules` fails until that merges and this branch is updated from main.
- `observed_date` is 2026-11-25, the day the pages were read (receipts are stamped 2026-11-26 UTC).

## Follow-ups (not fixed here)

- `scripts/site_corpus.py` marks a Wayback `id_` body that arrives gzip as FETCH_FAILED, because it decodes the wire bytes as UTF-8 (U+FFFD in the text check); three of five Wayback reads here failed that way and were read through `Corpus.request` plus the gate's `decode_capture`. The fetcher should gzip-decode (or send `--compressed`), as the gate does.
- It retries over HTTP/1.1 only on curl exits 35, 60 and 92; exit 52 (empty reply) gets no retry, and both Budzar and Chem-Materials fail that way on both transports.
- Failed receipts are cached and replayed (`Corpus.cached`), including ones caused by a sandbox rather than the site (a denied network, a missing Playwright). I deleted my own such receipts from the default cache.
- Green Innovations' recorded website `https://green-innovate.com/` fails its certificate while `https://www.green-innovate.com/` works: a website change is a separate PR under SCHEMA section 4.4.
- Values the pages state beyond the pilot's leads (Chem-Materials agriculture; Budzar energy, medical, semiconductor, defense) are not filled.
