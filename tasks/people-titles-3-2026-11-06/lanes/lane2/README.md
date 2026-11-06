# Current institutional titles — lane 2

The bounded input contains **56 existing candidate people**. Outcomes are **31 VERIFIED rechecks (55.4%)**, **6 REJECT dispositions for positively stated excluded current ranks**, and **19 STILL_UNCERTAIN holds**. There are no creates, deletions, merges, affiliation changes, or specialty changes. Five of the 31 verified people already have exactly the printed title and controlled role; those are observations rather than field edits.

`verified.csv` proposes only the controlled role and exact printed title together, with current institution-owned title and polymer-material research witnesses. The integrating reviewer owns source additions and verification dates. Separate name, address, department, or appointment headings are not concatenated. Two actual formal title fields contain literal pipes. Three person headings require removing the printed name or address from the formal rank; the checker explicitly bounds those exceptions. Current faculty rank conflicts remain held unless dated institution-owned evidence resolves them.

`rank_resolution.csv` supplies two deciding dated promotion witnesses: Hallinan effective August 2025 and Stache effective July 2026. Bowden’s dated appointment history and Nelson’s promotion history corroborate their current unambiguous professor titles; they are not substitutes for current formal title evidence.

The research inspected **141 distinct primary URL routes**, linked to 144 candidate-person/source observations because three pages are shared. Each shared URL was fetched once within this pass and reused; the maximum was six distinct routes for any one person. Of those routes, 111 returned inspectable text and 30 remained uninspectable. Relative to the input’s cited URLs, 78 routes were new, including 56 successful routes. These are source availability counts, not additional candidate people or verification outcomes. No broad directory census was conducted.

Scope comes from person-specific current research statements, named institution-hosted lab programs, and a bound faculty-catalog entry. The Clemson `/experts/` page used for one witness is a current institutional expert profile, not a dated news article. Publication titles, paper abstracts, generic menus, center rosters, and external labs do not supply scope. A university-owned summer research program explicitly naming the lab supplies one current program narrative. Chipara’s independent faculty-catalog scope was extracted with real `pdftotext`; both eight-page catalog routes yielded 8/8 pages, and page 2’s candidate column was inspected. Parent independent inspection additionally rendered that page and confirmed the column.

Holds include unresolved current rank conflicts, current home-institution questions, missing formal federal-lab titles, and missing current person-level polymer-material narratives. Failed routes and missing keywords were never deciding rejection facts. Excluded current ranks are practice, adjunct, or emeritus appointments; records remain held for the integrator’s disposition.

`source_manifest.json` contains 42 carrying or deciding source observations. Original sanitized-text hashes are preserved separately from hashes after contact redaction. Hashes describe extracted text, not HTTP bytes. Retrieved bodies and working notes remain only under `/tmp`; permanent packet files contain professional facts, short quotes, URL/status/hash metadata, and aggregate results. A shared-cache privacy sanitation incident touched other lanes’ observations; all proposed professional quotes and exact titles were rechecked after redaction, with no research refetch solely to obtain a new hash.

The named check is:

```sh
python3 tasks/people-titles-3-2026-11-06/lanes/lane2/check.py "$LANE_PRIVATE" "$LANE_CACHE"
```

It passes exact 56-ID ordered accounting, 31-proposal yield, held identity parity, controlled roles, printed title case/punctuation, source hashes, LF CSV formatting, institution domains, quote limits, explicit candidate identity, privacy, and PDF extraction yield. Calibration uses five actual known-answer people; token-boundary/affix and neighboring-wrong-person fixtures pass. False-quote, wrong-identity, and rank-affix mutations are rejected. The check uses the frozen sanitized observations supplied to it and makes no network requests.

Integration, evidence allocation, main-data edits, and independent completion reviews remain outside this packet. This is bounded verification, not an exhaustive faculty or federal-laboratory census.

Freeze correction: the parent’s check against the later shared cache returned FAIL (exit 1) for five carrying-source hashes. The earlier lane PASS referred to a different frozen text snapshot and did not establish parity with that current shared cache. The original attestations remain preserved. All 141 owned URL observations were subsequently copied from the current shared-cache text fields byte-for-byte into the lane snapshot; 15 hashes changed, including those five carrying sources. The 31 proposal rows, titles, and quotes are byte-for-byte unchanged. The named check now passes against both the current shared cache and the lane snapshot. No refetch, shared-cache write, or quote/hash guard relaxation was used. The final hash basis is UTF-8 of the exact current sanitized extracted-text string, not HTTP bytes.
