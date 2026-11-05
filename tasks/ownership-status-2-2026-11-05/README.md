# Ownership and status, round 2 (2026-11-05)

The repo owner chose this pass in session on 2026-11-05. It works the rest of round 1's lead pool and the
organizations whose website round 1 cleared.

## Pool (`lead_pool_2.csv`, 136 organizations)
- **97** round-1 leads not worked in round 1 and still active or unknown on today's main.
- **39** organizations whose `website` #122 or #126 cleared because it held a directory, press or permit page, or was
  hijacked. For these, the lanes also looked for the current own site.

There were four packet lanes (`lanes/O3`–`O6`). The brief is round 1's, with a round-2 addendum: the quote must name
both parties, name the immediate owner, give full ISO dates or none, and be saved after every org. Every quote was
re-fetched through Firecrawl, then Jina Reader, and matched as a word sequence (`rawcheck.csv`): 100 of the 106
quoted rows passed.

## Outcomes (unit: pool organizations; 136)
| Lane outcome | Orgs |
|-|-:|
| ACTIVE_UNCHANGED | 62 |
| ACQUIRED_SUBSIDIARY | 32 |
| NONE_FOUND | 30 |
| ACQUIRED_ABSORBED | 6 |
| REBRANDED | 5 |
| MERGED | 1 |

## Applied (`build.py`, decisions per organization; `journal.txt`)
| Change | Organizations |
|-|-:|
| `parent_org_id` set to a held buyer, with its generated `parent_of` edge | 5 |
| `ultimate_parent_name` set where it was empty and the buyer is the top of its chain | 9 |
| `website` filled (it had been cleared) or moved to the business's current own domain | 36 |
| `trade_names` gains a new brand | 2 |

50 evidence rows and 5 generated relationship rows.

- **Parents:** HPE Extrusion Solutions → Pexco; Adhesives Technology → Meridian Adhesives Group; Magee Plastics →
  Trelleborg Corp; Fiber-Tech → National Manufacturing Group; Res-Tek → A.P. Nonweiler (APN Performance Coatings).
- **Ultimate parents:** CHT USA → CHT Group; ASAP Hydraulics → RG Group; Arcosa Marine → Wynnchurch Capital; Seemann
  Composites → Karman Space & Defense; Janco → MacLean Investment Partners; UES → AeroVironment; Adams Manufacturing →
  Keter Group; Ultimate RB → Carlisle Companies; TPC Group → ENEOS Holdings.
- **Websites:** 12 fills for cleared records, for example Ensinger Inc. → `ensingerplastics.com` and Y-TEX →
  `y-tex.com`. The other 24 are same-business migrations or rebrands, for example UPM Raflatac →
  `adhesivematerials.upm.com` and A.P. Nonweiler → `apncoatings.com`. A US subsidiary's site swapped for a foreign
  parent's group site is **not** applied (Evonik, Untha, Futamura, Silon, Sigmasoft, Unimatec, Econ, Bekum and others).

## Held
- **Possible duplicates, for a dedupe pass:**
  - Roboworld, Gellner and Whirley: each new domain is already held by an adjacent record (ORG-002003, ORG-002405,
    ORG-002691).
  - National Composites rebranded as National Manufacturing Group, already held as ORG-007026.
  - Precision Thermoplastic Components was absorbed into Kreate, which matches two held records.
- **Buyer not held:** Pinnacle Recycling → Rumpke; Carstin Brands → Wolf Home Products; Southern Adhesives → Kodiak;
  StockPKG Columbus → StockPKG Omaha.
- **Wrong or unknown ownership level:** BioBag (Novamont is owned by Versalis), Hudson-Sharp (Thiele is owned by
  Barry-Wehmiller), Florikan, OX Engineered Products, Marine Concepts.
- **Other:**
  - GF Central Plastics: the held GF record may be a sibling, not the parent.
  - Hennecke Inc.: the quote names the Hennecke Group, not the Bridgeville entity.
  - Electro Prime: only a facility was sold.
  - Belt Concepts: the plant may have changed hands again in 2024.
  - Photo Tex: its site carries injected spam.
  - Medical Precision Plastics: a product site only.
  - Sur-Seal and Atlantic Footcare: quotes not raw-verified.
- **NONE_FOUND (30):** unchanged. A failed search is not evidence.

Checks: rehearsed on a temp copy. `python scripts/validate.py` exits 0 on the committed tree.
