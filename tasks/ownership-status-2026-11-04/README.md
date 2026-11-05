# Ownership and status pilot, website hygiene (2026-11-04)

The repo owner chose this pass in session on 2026-11-04, as a pilot of about 50 organizations before scaling. The
same PR applies two smaller owner-approved items: website hygiene, and a notes flag on plant records whose website is
their corporate group's domain (owner ruling 2026-11-04, "allow, flag in notes"; recorded in
`tasks/OWNER_BATTERY_2026-11-04.md`).

## Lead pool (`lead_pool.csv`, 147 active or unknown organizations)
Leads, not verdicts. Built from three sources:
- **Liveness sweep, 2026-11-01** (`tasks/liveness-sweep-2026-11-01/`). Its re-verification queue had not been
  worked. It contributes 104 cross-domain redirects, 23 dead domains and 3 parked domains whose website is unchanged.
- **Website run, 2026-11-04** (#121, `no_own_domain.csv`). 14 organizations whose name search returned a domain that
  another Atlas organization holds as its website. Directory and press hosts are excluded.
- **Named leads, 5.** These are dlhBOWLES, Revlis, Firestone Polymers, Cooper Tire and Ametek, from the #121 README and its review.

Leads where the buyer's domain is already held are ranked first. The pilot is the top 50, run in two packet lanes
(`lanes/O1`, `lanes/O2`; brief in `LANE_BRIEF.md`). Every lane quote was re-fetched raw, through Firecrawl and then
Jina Reader, and matched as a word sequence (`rawcheck.csv`).

## Outcomes (unit: pilot organizations; 50)
| Lane outcome | Rows | Quote raw-verified |
|-|-:|-:|
| ACQUIRED_SUBSIDIARY | 15 | 14 |
| ACTIVE_UNCHANGED | 19 | 17 |
| ACQUIRED_ABSORBED | 4 | 4 |
| REBRANDED | 2 | 2 |
| MERGED | 1 | 1 |
| IDENTITY_ERROR | 2 | 1 |
| NONE_FOUND | 7 | n/a |

## Applied (`build.py`, decisions written per organization; `journal.txt`)
| Change | Organizations |
|-|-:|
| `parent_org_id` set to a held buyer, with its generated `parent_of` edge | 2 |
| `ultimate_parent_name` made precise (buyer not held) | 1 |
| `status=acquired` with `status_date` and `successor_org_id`, with its generated `successor_of` edge | 1 |
| `website` moved to the business's current own site (the old domain redirected) | 6 |
| `trade_names` gains a new brand (legal name unchanged) | 1 |
| evidence-only: the parent was already recorded | 2 |

- Parents: Corr Tech → Indelco ("Corr-Tech, now a division of Indelco"); Foster → GEON (completed acquisition).
- Acquisition: Charter Plastics, Titusville, PA → WL Plastics (asset purchase, 2021-12-31). The record is kept as a
  tombstone. Its sites stay linked historically until the successor's site linkage is reviewed.
- 12 evidence rows (`parent` or `existence`), each carrying the raw-verified lane quote. The ceiling is `supports_B` for
  press, and `supports_A` for own sites and the parties' own releases.
- 3D Dental's old domain now belongs to an unrelated firm. Its website moves to `3d-dent.com`.

## Review
Two other model families, grok and codex, each tried to refute the 23 changes of the first build (deep effort,
read-only). Grok flagged 13 and codex 11, mostly as OVERREACH: the quote did not carry the specific link.
- **Held after review, 11:**
  - 5 parent links. Firestone Polymers: a pilot-center release. Specialty Products: a brand bundle. Sylvin: subsidiary
    vs absorbed is open. Composite Advantage: the buyer named is Hill & Smith. Integrated Bagging: a division transfer.
  - 4 ultimate parents. Tubro and OEM/Miller may be at the wrong level. SPR and Martin Wheel were already right.
  - 2 websites. GMR's new domain may be Principal Plastics' site. Packaging Products' quote is a generic slogan.
  Each reason is in `build.py` (`COUNCIL_HELD`) and `journal.txt`.
- **Kept against a flag:** Foster → GEON, and the dlhBOWLES and Berry evidence rows. `parent_org_id` records ownership,
  and each quote is a completed acquisition by the named parent. Both reviewers read "parent" as "still operates under
  its own name". That came from the integrator's own prompt wording, not the schema. Harwood → corelinerollers.com is
  kept too: the page is the business's current combined brand.

## Held (not applied)
- **Duplicates, for the dedupe pass:** Performance Plastics → Pexco, which is held twice (ORG-002534, ORG-000484).
  Molded Devices → Aptyx, already held as ORG-000449. Kumho America Technical Center, whose new domain is held by
  ORG-007503.
- **Identity errors, for the dedupe/HQ pass:**
  - Ametek, Nesquehoning (ORG-002556). The plant is Westchester Plastics, sold by Ametek to Niche Polymer (ORG-004886)
    on 2021-09-07.
  - 84 Fairmount Street (ORG-006217). It is a property of The Plastics Group of America (ORG-003880), and the quote is
    not raw-verified.
- **No full date** (AGENTS.md §4): BWAY → Mauser Packaging Solutions; Johnsonite → Tarkett (2005).
- **Buyer not held:** Reduction Engineering Scheer, absorbed into Maag (Dover).
- **Quote not raw-verified:** Cooper Tire (its parent is already recorded) and the rows the journal lists.
- **NONE_FOUND (7):** unchanged. A failed search is not evidence. Ohio Precision Molding's site redirects to Design
  Molded Plastics, and an auction was listed in December 2024; it is a lead for the next round.

## Website hygiene (`website_hygiene.csv`, 50 organizations, hand-classified)
A scan of all 4,162 websites flagged 73 that are not plainly an organization's own homepage. They were classified by
hand:
- **Cleared, 37.** The field held a directory profile (Thomasnet, Mergr, Datanyze, GlobalSpec, ProcessRegister,
  HigherGov), a press article, a government permit or PDF, or prose. The old value is kept in `notes`. These
  organizations become candidates for the next website search.
- **Trimmed to the root domain, 12.** The field held a blog post, PDF or product page on the organization's own domain.
- **Flagged, 1.** VS Rubber's website is a Dutch site; whether it is this company needs a check.
- **Left, 23.** These are university domains and plant pages on a corporate group's domain. The latter are allowed by
  the owner ruling above.

## Group-domain flag
Siliconature, Valmet, Viscofan USA and Tecomet carry their corporate group's domain as `website`. Each gets a notes
flag. Nothing else changes.

Checks: rehearsed on a temp copy. `python scripts/validate.py` exits 0 on the committed tree.
