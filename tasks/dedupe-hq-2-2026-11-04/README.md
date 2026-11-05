# Dedupe pairs and HQ pass 2 (2026-11-04)

The repo owner chose this pass in session on 2026-11-04. It works through findings that earlier passes held:
- the shared-domain pairs from the website pass (#121);
- the duplicates and identity errors held by the ownership pilot (#122);
- the Mechanical Rubber parent link and the G&T question from the 2026-11-04 state batch (#120);
- the 12 HQ disagreements that batch flagged on held records;
- two announced plant closures to watch.

**Stacked on #122.** Merge #122 first, then this PR retargets to main.

## How the work was done
- Two packet lanes ran under `LANE_BRIEF.md`. Lane D took 15 pairs (`lanes/D_in.csv` → `D_out.csv`). Lane H took 16
  HQ checks (`lanes/H_in.csv` → `H_out.csv`); the Sekisui name matched five records.
- **Raw check.** Every quote was re-fetched through Firecrawl, then Jina Reader, and matched as a word sequence
  (`rawcheck_D.csv`, `rawcheck_H.csv`). Pairs: 13 of 15 passed. HQ checks: 14 of 16 passed. The two HQ misses keep their
  held value anyway.
- **Applied by `build.py`.** Decisions are written per organization, and `journal.txt` holds the log. AGENTS.md §3
  applies: when in doubt, do not merge.

## Applied
| Change | Records |
|-|-:|
| HQ corrected, with an `address` evidence row; 10 move shard with their organization evidence rows | 11 organizations |
| Duplicate consolidated (`status=merged`, survivor in `successor_org_id`, generated `merged_into` edge; record lineage, not a corporate merger) | 3 organizations |
| Bought on a dated deal (`status=acquired`, `status_date`, `successor_org_id`, generated `successor_of` edge, `parent` evidence row) | 3 organizations |
| Identity corrected and marked acquired (Ametek → Niche Polymer), with the plant and its FRS facility link moved to the operator | 1 organization, 1 site, 1 registry link |
| `parent_org_id` set, with its generated `parent_of` edge and a `parent` evidence row | 1 organization |
| `monitor_watch=true` (a queue flag, not a status change) | 2 organizations |

17 evidence rows and 8 generated relationship rows.

- **HQ:** Sekisui Kasei USA → Mount Pleasant, TN; Ring Container → Oakland, TN; Southeastern Container → Enka, NC;
  Washington Penn → Washington, PA; RTP → Winona, MN; Sun Chemical → Parsippany, NJ; Westfall Technik → Tempe, AZ;
  Macro Plastics → Fairfield, CA; Jeld-Wen → Charlotte, NC; HSM Solutions → Hickory, NC; Wilbert → Huntersville, NC.
  Each old city is a plant, and its site rows are unchanged.
- **Duplicates:** Esstech (Division of Esschem) → Esstech, Inc. (same Essington, PA operation); Advanced Polymer
  Technology (Harmony, PA) → APT (Evans City, PA, same company and domain); Formco / Molded Devices → Aptyx (rebranded
  2023-10).
- **Acquired:** Performance Elastomers, Ravenna, OH → Pexco (2021-12-01); Pilot Plastics, Peninsula, OH → PLP (asset
  purchase, 2023-02-02); Tekniplex Healthcare / Dunn Industries, Manchester, NH → Tekni-Plex (2018-04-04).
- **Ametek (ORG-002556):** the record carried its former owner's name. It is Westchester Plastics in Nesquehoning, PA,
  which Ametek sold to Niche Polymer (ORG-004886) on 2021-09-07 (dated local press). The record's legal name becomes
  "Ametek Westchester Plastics", and "Ametek" stays in `trade_names`. It is marked acquired, and the plant SITE-002544
  and its FRS link move to Niche.
- **Parent:** Mechanical Rubber Ohio (ORG-000119) → Mechanical Rubber Products Company (ORG-007802, Warwick, NY).
- **Watch:** H.B. Fuller (the Paducah, KY plant closes about Q1 2027) and INOAC USA (the Livingston plant closes about
  April 2027). Both are verified operating today.

## Held (not applied)
- **Quote not raw-verified:** KNF (same Tamaqua address, likely one company); 84 Fairmount Street (a property of The
  Plastics Group of America).
- **Uncertain or not a merge:**
  - PPC Flex: the Alliance, OH record may be the acquired Plastic Packaging Technologies.
  - Creative Composites Group: it is unclear whether CCG is a legal entity.
  - G&T Industries: the Leola division may be closed, but there is no dated source.
  - Vaupell and Kumho: siblings under a common parent, so not duplicates.
  - Klöckner Pentaplast: which entity the record models (global group or the US operating company) is a modelling
    question.
  - Sekisui Products: Dallas vs Farmers Branch may be the same address.
- **Follow-ups:**
  - Performance Plastics → Pexco (#122 held it while Pexco was held twice) can now be applied.
  - Esstech's Linwood site belongs to its sibling Esschem.
  - Westfall's held "Corporate Headquarters (Las Vegas)" site looks stale.

Checks: rehearsed on a temp copy. `python scripts/validate.py` exits 0 on the committed tree.
