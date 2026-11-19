# Owner rulings, 2026-11-19b (follow-ups from PR #402)

The repo owner ruled two items in session on 2026-11-19, as multiple choice. This file records each item. The ruling
text is separate from how each is applied. Counts are at main c96d4699 unless stated.

## 1. `rubber_extrusion` at capability grain (PR #402, SITE-000264)

PR #402 held the permit lane's `rubber_extrusion` term at SITE-000264 (tier A, permit P0127945) with no capability
destination, because §3.6's `extrusion` rollup listed only the plastics subtypes.

- **Ruled:** `rubber_extrusion` rolls into the §3.6 `extrusion` capability rollup, as `calendering` already covers
  `rubber_calendering`. No new §3.6 term.
- Not chosen: a separate `rubber_extrusion` §3.6 term (the `rubber_molding` precedent); leaving it unmapped.

## 2. A direction word missing from a printed street (PR #402, SITE-000936)

- **Ruled:** a direction word missing from a printed street breaks binding. Owner ruling 2026-11-19 P2 stays narrow: a
  USPS-standard abbreviation or a `Twp.` suffix only. SITE-000936 (printed `302 Conwell Ave.`, Atlas
  `302 S. Conwell Ave`) stays held.
- Not chosen: binding when the Facility ID, holder and street number agree.

## How each is applied (method, not ruling)

1. **SCHEMA** (dated revision): §3.6's `extrusion` ROLLUP row adds `rubber_extrusion`, with this date and file.
   `scripts/export_vocab.py --check` stays current because no term is added.
2. **Data** (`tasks/permit-rubber-extrusion-2026-11-19b/`): the permit packet's capability map gains
   `rubber_extrusion -> extrusion` and the 33-site frame is re-scored with no other rule changed. One new
   `data/site_capabilities.csv` row results: SITE-000264 `extrusion` at `supports_C`.
3. **Item 2** changes no data: SITE-000936 stays unbound, and the packet's check fails if it is ever bound.
