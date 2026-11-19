# Band-B census faculty leads → people (2026-11-19)

**+95 people (PERSON-002403 to PERSON-002497), tier A, with 285 evidence rows (EVD-399100 to EVD-399384): existence,
scope and parent for each, all own_site, supports_A.** Owner-approved 2026-11-18 as item 4: "the band-B census
faculty leads".

## What went in, and what was held

| Step | Rows in | Rows out | File |
|-|-|-|-|
| Frame: the band-B census leads not sampled on 11/03 (see below) | 572 | 515 | `frame.csv` |
| Ten packet lanes, own-institution pages only (`LANE_BRIEF.md`) | 515 | 115 VERIFIED (366 REJECT, 34 STILL_UNCERTAIN) | `verified.csv` |
| Raw check: both gate quotes re-fetched and matched word for word; surname within 40 words of the Gate A quote | 115 | 115 | `rawcheck.csv` |
| Full-set review, two families; only rows BOTH judged SOUND go on | 115 | 101 | `review_holds.csv`, `reviews/` |
| Mechanical gates in `build_people.py` | 101 | 95 | `outcomes.csv` |

**The frame.** The source is `polymer-faculty-census/cache/exports/atlas_leads_2026-11-03.csv`, which holds 632
band-B leads. A lead ID is `BB-` plus the lead's row index among them. The 11/03 sample took 60, using
`random.Random(20261103).sample(leads, 60)`, which left 572. The frame then excluded 57 of those:
- 37 were already held under the same first and last name;
- 16 were marked moved or emeritus by the census page check;
- 4 are at Ohio State University-Main Campus, which matches no Atlas institution row by IPEDS unit ID or by name.

The Delaware and Princeton leads, 17 in all, were mapped by name.

**The raw check was tested before it was trusted.** Three rows were injected, and each was caught:
- a fake Gate A quote failed Gate A;
- a wrong surname failed the surname check;
- a fake Gate B quote failed Gate B.

**Full-set review** (`--effort deep`, every row, two halves per family):
- **codex:** 109 SOUND, 6 DOUBT, 0 WRONG.
- **Antigravity (Gemini 3.8):** 105 SOUND, 4 WRONG, 6 DOUBT.
- **Both SOUND:** 101. The other 14 are held, with each family's reason in `review_holds.csv`.
  - **Rank or appointment doubtful:**
    - Brown: a courtesy appointment at NC State, and the primary profile shows a different rank.
    - Rao: filed under University Park, but the page is Behrend. The Behrend row is admitted.
    - Dalir: Purdue Indianapolis.
    - Zimmerman: Research Professor and Emeritus.
    - Krogstad: the lead is marked "Former".
    - Allcock: is "Atherton Professor" emeritus?
  - **Gate B named polymers only through a publication title, a grant title or an application:**
    Healy, Gabrielson, Ghosh, Nutt, Daraio, Haq, Lanagan and Han.

  Grok was the intended second family. It returned HTTP 402 (quota) on both halves, so Antigravity replaced it.

**Mechanical holds (6):**
- **Five are already held** at the same institution: Kloxin, Brinson, Nieh, Velankar and Escobedo. They are
  duplicates, not movers.
- **One page fails V-62:** Ceniceros's only pages are `/~hdc/` personal-account URLs, which owner rulings
  2026-11-18 bar.

## Gates in `build_people.py`

A row is admitted only when every one of these holds:

1. The raw check passed for both gates and the surname.
2. Both families judged it SOUND.
3. Both gate URLs are on the institution's own domains. These are its website's domain, plus any domain at least two
   of its held people already use (universities run more than one; a website cell can be blank).
4. The role is a SCHEMA 4.9 value.
5. No URL contains `@` or a personal-account identifier (V-62, checked with the same `people_url.py` parser
   `validate.py` uses).
6. The name is not already held.

## Reproduce

These scripts run from the corpus directory, outside the repo:

- `python -I rawcheck_people.py verified.csv rawcheck.csv`: resumable. It fetches through NAS Firecrawl, then Jina
  Reader, then a plain GET.
- `python review_packets.py`, then `council-ask codex|gemini --effort deep "$(cat review_partN.md)"`.
- `python review_holds.py codex gemini`: fails closed on an unfinished review file or a row a family skipped.

Then, from the Atlas root: `python <corpus>/build_people.py <corpus> --apply`.

The lane work files (`lane*.json`, `out/`, and `work*/` with its fetch cache) stay in the corpus folder.
