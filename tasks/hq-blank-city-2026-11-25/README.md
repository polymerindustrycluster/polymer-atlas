# HQ fields of the 8 organizations with a county and no city

Built by: Claude Code (Anthropic)

Claimed by atlas-p1-hq-blank-city on 2026-11-25. First user: the Atlas controller, whose audit 13 smoke runner (PR #561) refuses to run while any frame record declares `hq_county` with a blank `hq_city`. Check for use by 2026-12-01. Base `7ea75205`.

## Result

**Filled 1 of 8, cleared 7 of 8.** Unit: organization rows in `data/organizations_*.csv`. On `main`, exactly 8 organizations hold `hq_county` with `hq_city` blank (the frame in `check.py`); on this head none does. Their notes describe a branch-parent pattern: the harvest established the Ohio branch, not the parent HQ, so `hq_county` held the Ohio branch county. Kenda is the exception: the record is the Ohio unit itself.

| Org | Result | Cell(s) |
|---|---|---|
| ORG-000197 Kenda American Technology Center | **filled**, moved shard US to OH | `hq_city` Green, `hq_state` OH, `hq_country` US, `hq_in_scope` ne_ohio (`hq_county` Summit stays) |
| ORG-000022 Greatoo Inc. | cleared | `hq_county` Summit |
| ORG-000033 LyondellBasell | cleared | `hq_county` Summit |
| ORG-000050 Synthomer, Inc. | cleared | `hq_county` Portage |
| ORG-000073 Professional Plastics | cleared | `hq_county` Summit |
| ORG-000186 SKF USA Inc. | cleared | `hq_county` Cuyahoga |
| ORG-000202 Quality Belt Maintenance Ltd. | cleared | `hq_county` Lorain |
| ORG-003703 JTW International, Inc. | cleared | `hq_county` GA (a state code in the county cell) |

## Filled: Kenda (EVD-483143)

The company's own locations page lists "Kenda American Technology Center 5801 Mayfair Road N. Canton , OH 44720 United States". The row is an `own_site` `address` row, `address_role` physical, `supports_B`, with a per-row proof: Wayback `id_` capture of 2026-05-19 (the live page agrees, read 2026-11-25), capture sha256 `7fe2278a…4753`, quote at character offset 471 of the capture's main text, and an `archive_links` row. `hq_city` is Green, as the held site row SITE-000204 and the record's notes hold it (Summit County parcel 2900022, tax district Green City; North Canton is the USPS mailing city). The page prints the mailing city, so the quote does not contain "Green"; that is the one inference beyond the quote, resting on the parcel evidence already in the record's notes, and a reviewer can overrule it. The county was already right. `hq_in_scope` is `ne_ohio` because Summit is in PIC-18. The record moved to `organizations_OH` and its one existing evidence row (EVD-421274) moved with it unchanged. No site row, ring, name or status changes.

**Reading by another family.** Codex (OpenAI, GPT-6.2 Sol, `council-ask codex --effort standard`) read the page's whole 1,759-character main text with the quote and offset, 2026-11-25: quote exact at offset 471, states street and ZIP, no contradiction, no individual's contact detail near it, VERIFIED. The stored page (nav and footer included, scanned as raw bytes) holds five addresses, all company or role addresses (`check.py` pins them and fails on any other). I confirmed the same mechanics the hosted gate uses: `judge` gives READ_REQUIRED `mechanics_clear` and `proof_problem` returns none on this head, with the capture fetched through the gate's own `fetch_url`.

## Cleared: no readable HQ statement within the effort cap (about 6 fetches each)

Clearing is the only clearing allowed and says nothing about where the company is headquartered. A route that could not be read is not evidence that the site does not state it; each line names the fact that would settle the record.

- **Greatoo (ORG-000022):** `greatoo.com` is blocked by its robots.txt for `AtlasSiteCorpus`; two Wayback copies (2024-12-03 home and about) state no address. Settles it: a page or filing that states the HQ of Greatoo Inc. (U.S.), and whether the record is the US unit or the Qingdao parent.
- **LyondellBasell (ORG-000033):** home, contact and who-we-are pages state no address. The EDGAR route needs a held SEC CIK link and the record holds none (FRS, TRI and EIN only), so it cannot pass the gate in this PR. Settles it: a held `SEC_CIK` registry link, then the 10-K cover page business address.
- **Synthomer, Inc. (ORG-000050):** the contact page names the group headquarters (London, for Synthomer plc, not this entity) and the location pages print three Synthomer Inc. addresses (Houston, Beachwood, Akron) with no label saying which is its HQ. Settles it: a page or filing naming the US entity's headquarters.
- **Professional Plastics (ORG-000073):** the site is blocked by robots.txt; the one Wayback copy of AboutUs (2025-02-10) states no HQ. A CDX listing was cut off by its limit, so other pages may exist. Settles it: the company's locations page or a state filing.
- **SKF USA (ORG-000186):** skf.com/us pages are a script shell with no text (5 characters) for the fetcher, and the first 300 Wayback index rows for the path held no contact or about page. I did not use a text-proxy service for it. Settles it: a rendered copy of the US contact page or a state filing.
- **Quality Belt Maintenance (ORG-000202):** `qbm.ca/contact-us` lists nine locations with no headquarters label (the Avon Lake, Ohio branch is one); `about-us` returns 404. Settles it: a page or Canadian filing naming the head office.
- **JTW International (ORG-003703):** the contact block prints "Mailing / Shipping Address 312 Industrial Blvd. Toccoa, GA 30577", not labelled headquarters, and every page carrying it also prints named individuals' emails and direct phones, so no capture is admitted to the shared store (AGENTS section 6). `hq_state` stays blank: moving the "GA" in the county cell to `hq_state` would be a new fill without a gate-passing row. Settles it: a page or Georgia filing naming the headquarters without personal data.

## Checks

`python3 tasks/hq-blank-city-2026-11-25/check.py` is the named check. It asserts that the changed cells equal `CLAIMS_CHECKED.csv` exactly (4 `corrected`, 7 `withdrawn`), that on head no organization has `hq_county` set with `hq_city` blank and that the base set was exactly the 8 (so it cannot pass vacuously), that the PIC-18 owner count (`value_basis.pic18_summary`) is 792, shard placement of the 8, evidence rows moved intact, one added evidence row and one archive row, the proof digest, offset and reviewed addresses against the stored capture, and that only allowed files changed. It caught all 20 planted defects (one per assertion: an extra cell, a cleared cell left, a dropped claim line, a mailing-city fill, a county with no city, a vacuous base set, owner count 791 by dropping SITE-000204, Kenda left in the residual shard, its evidence row lost, altered or left behind, a wrong offset, changed bytes, an individual's address, an absent capture, a stale claim hash, a same-family reader, a dropped archive row, a changed site file, a stray file). `python3 scripts/validate.py` passes. Not checked: the hosted gate's own replay (it needs a merge commit), and CI re-fetches the Wayback page from another origin.

`tasks/pic18-refetch-scale1-values-2026-11-24/AUDIT.md` is added because #559's label is unaudited on `main` and rule 5 fails any `data/` PR until it is (AGENTS section 2a). It cites #559's review records and is not a fresh audit; see the file for its limits.
