# Integrator backlog 4 — 2026-11-16

Fixed owner manifest, `atlas-w16-fixes`. Acceptance: no new organization/site IDs, unrelated edits, inferred parents or authored relationships; preserve existing tombstones, require plant-specific scope and pass local checks. First operator: controller for this integration pass, 2026-11-16. No tracker/queue change or issue closure.

9 manifest cases: 4 VERIFIED-applied, 5 STILL_UNCERTAIN (3 partially applied). `dispositions.csv` gives an applied/held column and settling fact for each. Baseline already had the HEXPOL fold, Reiser duplicate tombstone, AltraSet parent, Pittsburgh website and PPG/SHW tier A. These are retained, with additional witnesses where supported; no tier, parent, status or relationship changed.

Current delta: 13 evidence rows (EVD-369000–369009 and EVD-369012–369014) on 8 existing records (5 organizations, 3 sites): 10 organization-grain observations, 3 site-grain observations; 12 supports_A, 1 supports_C. Three records gain material fields: Silgan Thomaston recycled_content_pcr_pir; Kingspan Stillwater organization and site other_specified_in_notes, with the exact Polyiso material named in notes (site materials_other_note). All three remain tier C. Their sources and last_verified are updated. No organization/site added or removed. No inclusion-log changes.

## Review correction

Both reviews of 1d4a95a refuted completion. This revision addresses only their cited findings:

- EVD-369012/369013 replace the prospective Kingspan USA permit with Kingspan Roofing + Waterproofing's own operating statement: the Polyiso insulation product heading and adjoining sentence say it is shipping from the Stillwater manufacturing facility. Record the exact named insulation using the existing other_specified_in_notes vocabulary rather than inventing a polyiso tag or inferring TPO extrusion. Process remains held.
- NOV EVD-369010/369011 were product-specification bullets and a table footnote, which cap at C. The PDF says November 2020, with no day. Withdraw both new unmerged rows and the epoxy material fill, rather than invent a full ISO date for this dated source. Both IDs remain reserved and unused; not reused. NOV material and process remain held pending a source with usable dating/current narrative. Original source retained for inspection. No NOV verification-date advancement is claimed.
- Silgan's narrative PCR statement remains A-strength evidence with its actual 2021-09-21 publication date. Thomaston sources now cite it and last_verified advances to 2026-11-16.
- Full privacy-filtered witnesses and SHA-256 manifest permit reviewers to inspect all source context when origins return 403. Hash checks cover the stored raw original and complete privacy-filtered text, and quote checks use the stored complete text, not selected-excerpt files.

PPG/Sherwin evidence comes from fiscal-2025 10-Ks and Exhibit 21/21.1. Exhibit 21 lists downstream subsidiaries, not an upstream parent of either registrant; none is invented. PPG Item 2 establishes Pittsburgh HQ; Sherwin cover establishes Cleveland executive offices. Reiser certificate establishes historical operator/address, not current certification; expiry does not prove closure. HEXPOL independent legal identity and Huron street remain held. H-TARKETT excluded.

## Reproducing witnesses

Stored sources: `/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/integrator-backlog-4/`. `fetch-receipts.json` maps each URL to original SHA-256, complete privacy-filtered witness filename and witness SHA-256. Cache stays outside the public repository. Selected public excerpts in this folder are reading aids only.

Working fetch route for SEC (both 10-Ks and both Exhibit 21 schedules), NOV assets.nov.com PDF and Silgan own-site announcement was **direct urllib.request to the exact URLs in fetch.py**, with this declared User-Agent:

`Atlas research contact research@polymerindustrycluster.org`

Use `urllib.request.Request(url, headers={'User-Agent': 'Atlas research contact research@polymerindustrycluster.org'})`, then `urllib.request.urlopen(request, timeout=35).read()`. The same route worked for the other stored witnesses. No proxy, browser or search summary supplied the stored content. Some reviewer attempts received 403; that is route availability, not absence evidence. Run `python3 tasks/integrator-backlog-4-2026-11-16/fetch.py` to resume missing downloads, convert PDFs with `pdftotext -layout`, strip HTML tags/scripts/styles and decode entities, redact individual email/phone contact fields, and regenerate hashes. Existing cache is reused, so stored observation bytes stay inspectable even when origin access fails. A fresh download belongs in a separate directory when comparing bytes; don't overwrite the observation under review. No more than six primary source URLs fetched per organization.

## Named checks

- `python3 tasks/integrator-backlog-4-2026-11-16/check.py`: 13 input proposals / 13 evidence rows, 8 evidenced records against 9 manifest dispositions; reserved-ID uniqueness, stored-source hashes and quote presence, exact data cells and source/verification-date checks. Three injected defects rejected (input loss, duplicate ID, invented quote).
- `python3 tasks/integrator-backlog-4-2026-11-16/build.py --apply`: repeat reports 0 operations. The builder revises only its unmerged evidence IDs, checks they are absent from origin/main before replacement/withdrawal, and keeps pre-revision backups in controller storage.
- `python3 scripts/validate.py`, `python3 scripts/check_row_loss.py --base origin/main`, `python3 scripts/export_vocab.py --check`: PASS on updated tree (validator 0 errors; no keyed row loss; vocabulary current).

No independent-family approval claimed on this revision; controller routes re-review. Not checked: the five explicit holds, unrelated records, current certification. Local estate inventory is incomplete on Mac (Windows Documents catalogue absent), a platform gap rather than absence evidence. Proposed follow-ups outside fixed scope: none.
