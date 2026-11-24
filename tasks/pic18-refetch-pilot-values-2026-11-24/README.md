# PIC-18 refetch-pilot value fills (second read and data PR)

Built by: Claude Code (Anthropic)

Claimed by atlas-p3-refetch-apply on 2026-11-24. First user is Polymer Industry Cluster staff who read the Atlas process field on the public site. Check for use by 2026-12-20. Base `6516b6cf`.

## Result

**Two process values in two cells of one owner (Perry Fiberglass).** Unit and filter: organizations that hold an active tier A–C site in PIC-18. Owners with a blank process (the controller's `pic18_unknown.py`): **332 of 792 on the base, 331 of 792 on this head.** Owners with a blank market: 303 of 792 before and after (no market value cleared the gate, see below). The pilot's "8 of 30 owners" does not carry through: the second read and the gate's byte replay cut it to 1.

| Owner | Field | Value | Evidence row |
|---|---|---|---|
| ORG-000485 Perry Fiberglass Products | processes | `composites_filament_winding` | EVD-483136 |
| ORG-000485 Perry Fiberglass Products | processes | `fabrication_unspecified` | EVD-483135 |

Both fills go into one blank cell (`processes`), each with, its own `own_site` activity row (with its `archive_links` row, V-66) (`supports_B`, label `claude-code pic18-refetch-pilot-values-2026-11-24`) whose head names exactly that value, a `BINDING_PROOF.csv` line, and the generated `value_basis.csv` row, which comes out `stated` for both. Nothing else changes: `check.py` diffs every organization row against the merge-base and allows only these cells.

## Step 1, second read (Claude, second family; the pilot reader was Codex)

Frame: the pilot's 16 STATED raw-HTML verdicts less the 5 control-case rows, which leaves 11 owner-field-value triples on 8 pilot owners (`second_read.csv`). Out of this frame, by count only: 1 PDF row (ORG-001668, no admissible route), 5 IMPLIED rows, 0 rendered-DOM rows.

| Second read | Triples | What |
|---|---:|---|
| VERIFIED and applied | 2 | the two Perry fills above |
| VERIFIED, held for unstable bytes | 3 | ORG-000026 `rubber_molding_unspecified`, ORG-000263 `general_industrial`, ORG-001892 `distribution` |
| STILL_UNCERTAIN | 4 | ORG-002153 `footwear_apparel`, `electronics_electrical`, `toys_sporting_goods` (held by the controller's ruling: a retail segment list names the customer's trade); ORG-002922 `machinery_equipment` (below) |
| REJECT, implied not stated | 2 | ORG-000378 `aerospace_defense`, ORG-000358 `electronics_electrical` |

Rule used for a list item: a service the owner names ("Custom Rubber Molding" under Products & Services) is stated; a product name that carries an end use ("Fiberglass for Aviation and Ballistics") or a material "ideal for" an application is implied, because neither says who the owner serves.

- **Unstable bytes (the finding that cut the yield).** The CI gate fetches the cited URL live and compares the SHA-256 of the decoded bytes. Enterprise Rubber's page changes digest between consecutive fetches (same length). Carney's about page is an ASP.NET form whose `__VIEWSTATE` changes (three digests in four fetches, over three minutes). Infinity FRP and Grafix change too (the Grafix page now answers 403 to the gate's fetcher). A live capture that cannot be re-fetched byte-identically fails in CI, so none of these is applied. The two Perry pages returned identical bytes in every fetch (at least five fetches each) and the hosted CI fetch matched, and those bytes equal the digests the Codex reader recorded, so the Codex reading covers exactly the cited bytes. **Schibley (ORG-001892 `distribution`)** was byte-stable from the lane machine and passed the trusted `binding-gate` run, but the hosted `validate` guard on PR #557 fetched different bytes from the same URL (capture_sha256 mismatch, 2026-11-24 19:53 UTC). A hash that differs by fetch origin is not reliable in CI, so the value is held; its capture stays in the store. The route for the held rows is a dated Wayback capture with an archive-link row (SCHEMA 4.13, 4.22). The follow-up for these held rows is a dated Wayback capture used as the proof (archive links are in the diff, V-66; the open work is the capture-as-proof route).
- **Alpha World / Checkpoint Systems (ORG-002153).** The page lists "The Markets We Serve: Apparel, Grocery, Electronics, DIY, Mass Merchant, Sporting Goods". The owner is a retail loss-prevention vendor, so these are the retail segments it sells to, and three have no section 3.3 token. The controller held it on 2026-11-24 (a retail segment list names the customer's trade, and one owner does not merit an owner ruling). No held own-site market row rests on a retail-channel statement.
- **Absolute Haitian (ORG-002922 `machinery_equipment`), held after the Codex review (REFUTE at `59ab4f6f`, finding 1).** The quote "The World's Largest Injection Molding Machinery Supplier 5,000+ IMM installs in the U.S. and Canada since 2006" heads a group of statistics (global production facilities, 130 countries, 60+ years) that the page does not assign to this corporation. I made the one allowed check for a page on absolutehaitian.com that states the supply, sales or service for Absolute Haitian itself: the homepage text and the two held ORG-002922 captures. None does (the homepage names "Absolute Haitian" only for a support portal and its courses). The value stays STILL_UNCERTAIN; the named fact is such a page. Held row EVD-003162 calls it the exclusive US/Canada sales and service agent but saves no page words.
- **Grain note on the applied rows.** Perry: the page never names Ohio, but the held website carries held own-site rows for this record and the page names the held company. `fabrication_unspecified` is the section 3.1 token for fabrication with the type not stated; Perry's FRP pipe is "designed and fabricated", and the type is not stated there.

## Step 2, how the batch was built

`build.py` reads `second_read.csv` (rows with `applied=yes`), fetches each page with the gate's own `fetch_url` (UA `evidence-check/1`, HTTP 200 only), requires the pilot quote to occur exactly once in `capture_text`, refuses to emit a proof unless the digest and offset equal what the pilot reader recorded (`pilot_sha256`, `pilot_offset` in `second_read.csv`), and records the digest and zero-based character offset from those bytes. It stores each capture in the shared store at `provenance/pic18-refetch-pilot-values-2026-11-24/captures/<sha>.html` (listed in `INPUTS.sha256`) and writes the cells, evidence rows, `BINDING_PROOF.csv`, `FILLS.csv` and `CLAIMS_CHECKED.csv`. Quotes are character-identical to the Codex reading in the pilot packet (`verdicts.csv`, `/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/p3-refetch-pilot-2026-11-24/`). Evidence IDs run from EVD-483135 to EVD-483136, above the tree-wide maximum EVD-483134 (the one open PR that adds evidence rows, #543, uses EVD-483118 and EVD-483119).

**Archive links (V-66).** SCHEMA 4.22 requires an `archive_links` row for each new web evidence row, so the diff also appends two rows to `data/archive_links.csv` (`ARCHIVES.csv` lists them). I asked Wayback Save Page Now for each page on 2026-11-24. For Perry's products page and for Absolute Haitian, Wayback answered with its existing identical snapshot from 2026-11-16, and the link cites that real timestamp and date. Each capture was fetched in its `id_` form with HTTP 200 and holds the quote; the Perry and Absolute Haitian captures hold the same text offset. The captures are copies of the pages, not part of the gate's replay, which uses the live page.

**Reading by another family.** `BINDING_PROOF.csv` names the reader as Codex (OpenAI), the pilot reader, dated 2026-11-24. The builder is Claude (Anthropic). The gate requires different families. My own read (this folder's `second_read.csv`) is the second reading and also Anthropic; it is not the reading the gate counts.

`check.py` is the named check. It passes on the clean tree and catches all 16 planted defects (the last three kinds added after the Codex review, each shown missed before the check was added): a held value overwritten, a value outside the vocabulary, a quote not in the capture, a wrong offset, a capture digest mismatch, another owner's page, a REJECTed or unapplied row applied, a changed column outside the fills, a data file outside the allowed set, a missing archive link, extra or duplicated appended evidence, archive or proof rows, and a capture whose digest or offset differs from what the pilot reader read. `python3 check.py --fresh` replays by live fetch instead of the store.

## What the checks cannot see

- The binding gate checks mechanics and replays bytes. It does not decide whether a page states a value; that rests on two readers (Codex, Claude) reading a short quote each.
- CI re-fetches the live page. A page that changes its bytes after this PR (a redesign, a new nonce) fails the replay for later runs; the held proofs stay valid only for the capture digest recorded here.
- Both reads and the digest check are one fetch of one page per value. A failed or changed fetch is never evidence about the owner.
- `value_basis.csv` is generated (`scripts/value_basis.py`), so the two `stated` rows follow from the evidence and proof rows and are not separate evidence.
- The new `created_by` label needs an `AUDIT.md` before the next data PR can merge (AGENTS section 2a rule 5); this PR carries none because no label on main lacks one.
