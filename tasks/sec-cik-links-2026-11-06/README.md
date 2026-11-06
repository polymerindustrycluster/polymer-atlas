# SEC CIK identity links — B-12

Scope: every organization with a stock ticker or public_parent qualifier/basis and no own SEC_CIK link at the pinned main baseline. Acceptance: every frozen organization gets VERIFIED or STILL_UNCERTAIN; only its own identity, confirmed in SEC company_tickers.json and the EDGAR company record, can mint a ten-digit SEC_CIK link. Parent/brand mismatches and unavailable routes remain held. No organization, tier, status, parent, or derived qualifier edits. The builder must preserve every existing registry row and replay without changes.

The SEC company page is client-rendered. Its official submissions API supplies its company information; the packet records both the browse URL and the directly retrieved API identity. Failed routes are availability observations only. Registry identity uses SCHEMA §4.8; registry_links is outside §4.13's record_table enum, so the source receipts and match_basis carry this identity-only provenance, with no evidence IDs or tier claims.

Controller clarification (2026-11-06): official submissions JSON satisfies AGENTS §4 source-system verification; rendered browse confirmation is not required. This supersedes the literal browse-page requirement in the initial B-12 brief. No rendered browse page is claimed as seen. Cross-thread agreement is also recorded on BOARD.

## Result and denominator

Frozen baseline `d1e618b06ae71588e80d117b042cf5c0308e0d50`: **103 organizations** have a nonempty stock_ticker, public_parent qualifier, or public_parent basis and lack an own SEC_CIK link. `check.py` independently reconstructs the full denominator from the pinned canonical shards and registry links. All 103 have exactly one verdict: **64 VERIFIED / 39 STILL_UNCERTAIN**. No REJECT, duplication, closure, or listing-status conclusion is made.

The builder appends **64 registry rows for 64 held organizations**, all SEC_CIK, all ten-digit zero-padded, each with its source URL, current SEC name, match basis and retrieval date. At this baseline registry rows increase **5,373→5,437**; own SEC_CIK rows increase **9→73**. Organization/site/evidence rows, all tiers and all derived fields are unchanged. No inclusion-log entry or evidence ID is minted.

## Sources and retrieval limits

- [SEC company_tickers.json](https://www.sec.gov/files/company_tickers.json): direct curl 403; exact official-URL retrieval through web.run. Large-page retrieval was partial. `sources/ticker-receipts.json` preserves the exact JSON entry for each positive candidate and calibration identity; it does **not** claim complete retrieval of every SEC listing. Missing entries never become negative facts. Repeated excerpts and unrelated listing entries are omitted from the repository.
- SEC company records: `https://data.sec.gov/submissions/CIK##########.json`, fetched directly with a browser UA. `sources/CIK*.json` preserves the CIK, current name, tickers, exchanges, source URL, HTTP status, as_of and original-response SHA-256, projecting away filings and irrelevant contact fields. Each name token was checked against the raw response before projection. Full raw bodies remain outside the repository at `/tmp/atlas-sec-cik-raw/`.
- **76 distinct company-record URLs** are represented: 73 candidate filer identities and three calibration-only identities. The four-record calibration and candidate research perform 77 API fetches, because Avient is independently read in both stages. Preliminary route/access probes are not included in that research-script total.
- Data-estate/name-resolution tooling was consulted before entity retrieval. Its Mac Documents inventory, entity database and full-text layers are unavailable; the degraded result is not evidence that sources or aliases are absent. No private/CRM or paid-source material was used.

The only changed held-ticker interpretation is **ORG-002886 CSW Industrials**: the official ticker entry and company record both carry current ticker CSW under the exact held issuer name. The held stock_ticker CSWI remains unchanged. No foreign ticker is translated speculatively. Exact held names lacking a legal form (Pentair; GrafTech International) accept the SEC legal-form completion explicitly; differing held legal forms remain significant (STERIS Corporation versus STERIS plc is held).

## Holds

Every unresolved organization has its own finding and named settling fact in `verdicts.csv`.

| Unit/filter | Count | Disposition and settling fact |
|---|---:|---|
| Organizations whose candidate filer differs from the held entity | 11 | HOLD own-filer attribution: STERIS/STERIS plc; Exxon Mobil/ExxonMobil Holdings; Valmont Composite/Valmont Industries; Synventive/Barrick (recycled B ticker); Legend Brands/RPM; Lippert Components/LCI; Carlstar/Titan; Gates/Gates Industrial; Oxy Vinyls and Occidental Chemical/Occidental Petroleum; Afton/NewMarket. Need source-system identity for the held own entity. No parent-filer link is minted here. |
| Organizations without a verified own ticker-file candidate in this partial retrieval | 28 | HOLD source resolution: includes six existing parent-filer-only records, foreign/annotated parent listings, and unresolved simple ticker routes. Need an own-entity ticker-file entry and matching SEC company record. This is not an assertion that a CIK, filing, or public listing does not exist. |

No scope/ring/vocabulary ruling is needed or adopted. Parent/brand links would require their own authorized source linkage; no organization-grain decision is made in this packet.

## Builder and checks

`python3 tasks/sec-cik-links-2026-11-06/build.py` reproduces `new_links.csv` and `verdicts.csv`. `--apply` appends to the current registry file only after all source and conflict preflights; `--data-dir DIR` rehearses on a copy. Rebase by taking fresh main's registry file and replaying this builder, never by merging CSV hunks. Source/input drift stops the builder for review.

The builder reuses `tasks/registry-links-2026-11-02/build_links.py:apply`. Registry links use composite keys and repeated org_ids; the single-ID `scripts/shard_io.append_sorted` is inapplicable. Existing registry bytes remain a literal prefix after the established registry writer appends this packet. No shared writer or script is modified.

Before trusting the fetcher, `python3 tasks/sec-cik-links-2026-11-06/fetch.py --known` passed four known CIK/name/ticker records: Apple 0000320193/AAPL; IBM 0000051143/IBM; Sherwin-Williams 0000089800/SHW; Avient 0001122976/AVNT. These independent answers are also asserted by the deterministic check.

Passed on the applied tree:

- `python3 tasks/sec-cik-links-2026-11-06/check.py`: exact 103-organization baseline census; 64/39 verdict reconciliation; all existing registry rows preserved; literal source-entry and SEC company-name/CIK/ticker agreement; four known answers; byte-identical replay; three-state Git check forbids changes to other canonical data.
- `python3 tasks/sec-cik-links-2026-11-06/test_build.py`: three test methods pass. Four real parent/brand/legal-form collisions reject; wrong CIK, wrong name, wrong ticker, missing/duplicate frozen row reject; a conflict in the final proposed link refuses the whole batch with zero writes.
- `python3 scripts/validate.py`: **0 errors**. `python3 scripts/check_row_loss.py --base origin/main`: PASS. `git diff --check`: PASS. Shared `scripts/` is unchanged.

## Review status and intended use

Two-family review pending; this packet is not called Done. The first intended user is the controller/integrator checking public-parent identity joins in the next integration pass. Check whether the new registry rows have been consumed by **2026-11-13**; non-use is a finding, not an automatic new commitment. No rendered EDGAR browse view, exhaustive SEC listing census, foreign listing database, or ownership exhibit audit is claimed.
