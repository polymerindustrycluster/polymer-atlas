# National capability batch b01 (2026-11-18)

**+12 section-3 tags on 7 sites, +7 `site_capabilities` rows, +12 evidence rows.** Two more terms are capability rows
only. Every applied term was judged SOUND by **both** codex and grok on the final full set. The batch is a pilot of the
PIC-18 corpus method (`tasks/pic18-capabilities-corpus-2b-2026-11-16`) outside Ohio.

## Frame (`frame.py`, base `base.txt`)

The frame is 100 sites drawn with seed 20261118 from a pool of 277. A site is in the pool when it is:
- active and outside Ohio (the PIC-18 lanes own Ohio);
- `ring_primary` 1–2;
- blank in **both** `processes` and `materials`;
- the only active Atlas site of an active organization that has a website.

The slice is PA 63, UT 6, MI 4, NV 4, IL 3 and 20 other states. By tier: A 27, B 49, C 24.

## Method

1. **Stored corpus (`fetch.py`).** For each organization: its homepage plus up to 5 same-host capability, service,
   product, material, about or contact pages. Raw HTML and text are stored with their SHA-256, outside the repository.
   90 of the 100 sites had at least one readable page (432 pages).
2. **Lanes.** Five Sonnet lanes read only the stored pages. Each accepted term needed one quote of 25 words or fewer
   and a locality witness from the same company. Every site got a decision or a hold (`lane_decisions.csv`: 164 term
   rows on 37 sites; `lane_holds.csv`).
3. **Builder (`build.py`).** It re-checks every quote and witness against the stored raw page and its hash, then
   applies the rules:
   - narrative sentence = `supports_A`; list item = `supports_C`;
   - a list item on a tier A/B site becomes a capability row only (owner ruling 2026-11-14);
   - cells are filled only where they are blank.

   A self-test confirms the checks refuse 6 injected defects.

## Review rounds (unit: lane term rows)

| Round | Reviewer | Set | Result | What changed after it |
|-|-|-|-|-|
| 1 | codex | random 40 | 9 WRONG, 7 DOUBT | Gates: multi-location screen over all stored pages; narrative strength only when the quote names an actor; example lists dropped; formulation needs "formulate" |
| 2 | grok | fresh random 40 | 9 WRONG, 11 DOUBT | Gates: open lists ("include", "and more", "options"); supply, expertise or customer wording; materials need a processing verb and their own name; list strength only on capability pages; the witness must name the record's city and the pages the record's company |
| 3 | codex | all 35 remaining | 26 SOUND, 7 WRONG, 2 DOUBT | Kept only its SOUND rows |
| 4 | grok | all 26 remaining | 14 SOUND, 4 WRONG, 8 DOUBT | Kept only rows both families judged SOUND |

The gates did not converge on their own: round 1 had 9 wrong in 40 and round 2 had 9 wrong in a fresh 40. Each round
found phrasings the last gate missed. What is applied is the intersection of two full-set reviews, not the output of
the gates alone.

## Result (unit: frame sites)

| | Sites |
|-|-|
| Tagged (section-3 terms applied) | 7 |
| Capability rows only | 2 more |
| Held, with a reason and settling fact (`verdicts.csv`) | the rest of the 37 the lanes decided |
| Nothing accepted, or no readable page | 63 |

Yield is 9 of 100 sites, close to the PIC-18 corpus lane's 10 of 110. Most single-site companies' own pages do not
state their processes in a form that survives both reviews.

## Held facts worth a follow-up

- **SITE-002586 (Src Elastomerics):** the pages are Stockwell Elastomerics'. Codex found Stockwell's live page
  describing the legal-name relationship and a single facility. Stored, that page would settle five terms.
- **SITE-008255 (FallLine):** the witness is a city-level "headquarters in Reno" line; it needs the street.
- **SITE-002477 (Smooth-On):** a second address (a seminar entrance) is unresolved.
