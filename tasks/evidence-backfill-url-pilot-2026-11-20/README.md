# Evidence backfill, URL-lead pilot (2026-11-20)

**Result:** 17 evidence rows (EVD-410001 to EVD-410017: 12 existence, 5 address) on 12 records that had none. The
rows are appended to three evidence shards only. No record field, tier or status changed.

**Coverage:** 12 of the 50 sampled records (24%; Wilson 95% interval 14–37%) gained a row.
- At that rate the 662-record frame yields about 159 records (95–248), which is about 5% of the 3,455-record gap.
- The frame covers only records citing their **own domain**. The other ~1,560 URL-lead records cite government,
  registry, directory or trade-press hosts, which this pilot did not test. The owner's split ("this lane takes the
  2,222 URL-lead records") may need re-ruling once those classes are measured.

## Why

On main at `6c29fa6c`, 3,455 of 14,465 records (organizations, sites, ecosystem, programs, people) had zero evidence
rows (`scripts/audit_evidence_coverage.py`).
- **2,691 existed before their evidence class did:** organizations, sites, ecosystem and programs before `db582b6d`
  (2026-10-30); people before `3a6aa592` (2026-11-05). SCHEMA §4.13 grandfathers them and names the only honest
  route: re-observe each witness.
- **Nearly all of the other 764** came from integration passes 16–18 on 2026-10-30/31, at the contract cutover.
- 2,222 of the 3,455 already cite a URL in `sources`.

**Owner rulings (John, 2026-11-20):**
1. Target at least one row per zero-row record. Existence, address and liveness come first; full must-have coverage
   comes later.
2. A fresh witness that is weaker than the record's tier, or that conflicts with the record, is held for the owner. No
   row is written and the tier does not change.
3. Split the work. This lane takes the URL-lead records. Muse (`agent/spaghetti`) takes the 1,233 with no URL, using
   separate EVD blocks. This lane uses EVD-410001 upward.

## Method

`build.py` and `apply.py` run with no model. `review_bundle.py` writes the refute brief.
1. **Frame** (`frame.csv`): organizations and sites with tier A/B, `active` status and zero evidence rows, whose
   `sources` cites a URL on the record's own website domain (for a site, the operator's). Licensed hosts are excluded.
   - The frame holds 662 records: organizations 154 A + 186 B, sites 60 A + 262 B.
   - That comes from 2,319 zero-row A/B active records (1,130 organizations, 1,189 sites).
2. **Sample** (`sample.csv`): 50 records drawn with seed 20261120, stratified by table and tier (13/12/13/12).
3. **Fetch** (`fetch.csv`): a direct GET of the cited URL, then the Jina reader on failure. Page text stays out of the
   repo, in `pic-github/_atlas-corpus/evd-pilot-2026-11-20/pages/`.
   - The NAS Firecrawl returned 502 and Jina returned 402 (out of credit), so every failed direct fetch stayed failed.
   - A failed fetch is an availability signal, never a verdict.
4. **Match** (`ledger.csv`, `packet_rows.csv`): deterministic string matching, and every quote is cut verbatim from
   the saved page.
   - **Existence:** the record's legal name, a trade name or a dba name appears on the page.
   - **Address (organization):** the HQ city and state appear together.
   - **Address (site):** the site's street number, street word and city appear together.
   - **Liveness:** a copyright year of 2025 or later.
   - **HOLD** for a redirect off the cited host, a closure phrase, or an ownership-change phrase within 150 characters
     of the name.
5. **Refute:** Codex (`review_codex.json`) and Antigravity (`review_agy.json`) each judged all 50 proposed rows under
   `review_brief.md`, with the first 6,000 characters of each saved page in front of them.
   - Grok was unavailable (HTTP 402, out of quota). Antigravity got the bundle in two halves because of its 64 KB
     direct-prompt limit.
   - Three applied candidates (ORG-001451 address; SITE-002150 existence and address) quote text past character
     6,000. Both families re-judged them with a 1,500-character window around the quote
     (`rereview_brief.md`, `rereview_*.json`), and all three were SOUND both times.
6. **Apply** (`applied.csv`, `withheld.csv`):
   - Only rows that every review judged SOUND are applied.
   - A record whose existence row any review rejected loses every row.
   - Liveness rows are held whole (owner question 3).

**Defect injections, all caught:**
- Three records scored against another record's page produced 0 rows (`build.py match --plant`).
- A directory-class existence row on a zero-row tier-A record fails `validate.py` (V-25).
- An altered applied row in `data/` fails `check.py`.

## Funnel (unit: sampled records, then proposed rows)

| Step | Organizations | Sites | Total |
|-|-|-|-|
| Sampled | 25 | 25 | 50 |
| Page not fetched | 3 | 7 | 10 |
| Held (redirect or ownership/closure phrase) | 2 | 2 | 4 |
| No witness on the page | 2 | 12 | 14 |
| Witnessed | 18 | 4 | 22 |
| Gained at least one applied row | 9 | 3 | 12 |

Proposed rows: 50. Codex judged 34 SOUND and Antigravity 25; both judged 25 SOUND. 17 were applied and 33 withheld
(`withheld.csv`, `held` column).
- **Held for owner question 3:** all 11 liveness rows.
- **Not SOUND in every review:** 15.
  - Organization address rows on contact pages that never say "headquarters": both families rejected these.
  - Existence rows Antigravity rejected for a missing legal suffix ("True Indicating" against "True Indicating LLC")
    or a name mismatch: Codex judged all of these SOUND.
- **Dropped because the record's existence row failed a review:** 7.

**Site yield is the weak point.** Most site URLs are the operator's homepage, which does not print the plant's street
address.

## Owner questions

The target is records with at least one row. Questions 2 and 3 can add records; question 1 mostly adds rows to records
that already gain an existence row.

1. **Contact-page address.** Does a single address on a company's own contact page, with no "headquarters" label,
   witness the organization's HQ city? Existing rows on main already accept this (for example, the Enduro Rubber
   contact-page address row from the PIC-18 health lane). Both families rejected such rows under this pilot's stricter
   brief.
   - Recommendation: yes for a single-address company.
2. **Short name.** Does existence hold when the page uses the trade or short name without the legal suffix ("C&J
   Industries" for `C & J Ind`)? Codex said yes and Antigravity said no on 8 rows across 8 records.
   - Recommendation: yes, because the claim is identity, not the legal form.
3. **Liveness witness.** Is a current copyright year on the company's own site enough for a `liveness` row, and at
   what effect?
   - The pilot proposed `supports_A`. The live-page liveness rows already on main carry `supports_B` or `supports_C`,
     and a footer year is often generated automatically.
   - A `supports_B` liveness row on a tier-A record fails V-25.
   - Recommendation: a copyright year alone is not a witness. Use a dated own-site operating event (a dated news post,
     product release or job posting within 12 months) instead.

## Record-health leads (no writes; for triage)

- **ORG-002541 Monadnock Non-Wovens:** its own news page says "Precision Products Group Acquires Monadnock
  Non-Wovens" (2026-10-09).
- **ORG-002208 and SITE-002171:** the cited domain now redirects to `legacymobileautospa.com`.
- **ORG-002409 Biocoat:** the page carries "Integer Medical Coatings" branding and an `integer.net` contact.
- **ORG-001874 PVS Plastics Technology Corp.:** the cited page is the German parent's group site.
- **ORG-001777:** the legal name is American Consolidated Industries Inc, but the site styles itself "Anchor
  Industries, Inc.".
- **SITE-002779:** the site name "Sherman-Williams Manufacturing Company" looks like a misspelling of the operator,
  Sherwin-Williams.

## Before scaling

- **Records, not rows:** the levers that add records are question 2, a working fetch route, and site locations pages.
- **Fetch route:** restore one, the NAS Firecrawl or Jina credit. 10 of the 50 sampled pages (20%) did not load
  directly; a working fallback makes them fetchable, not necessarily witnessed.
- **Sites:** take the street-address witness from the operator's locations page rather than the cited homepage.
- **Reviewer view:** show reviewers a window around every quote, not the head of the page.
- **Liveness:** if question 3 keeps copyright years, require the year to equal the observation year.

## Reproduce

```
python tasks/evidence-backfill-url-pilot-2026-11-20/build.py frame . <corpus>
python tasks/evidence-backfill-url-pilot-2026-11-20/build.py fetch <corpus>        # live network
python tasks/evidence-backfill-url-pilot-2026-11-20/build.py match . <corpus>
python tasks/evidence-backfill-url-pilot-2026-11-20/apply.py . <corpus> --start EVD-410001 --hold-claims liveness \
    review_codex.json review_agy.json rereview_codex.json rereview_agy.json
python tasks/evidence-backfill-url-pilot-2026-11-20/check.py
```
