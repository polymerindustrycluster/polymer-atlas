# Evidence backfill, FRS site lane (2026-11-20)

**Result:** 152 evidence rows (EVD-410477 to EVD-410628) on 137 active tier-B/C/U sites that had none.
- **Rows:** 137 `existence`, 15 `address`.
- **Sites by tier:** 107 B, 26 C, 4 U.
- **Witness:** each row cites the site's own EPA Facility Registry Service record, re-read in EPA's state combined file.
- **Source class:** `registry`. Existence carries supports_B (supports_U on tier U); an address carries supports_C.
- **Unchanged:** no record field, tier or status.
- **Baseline shrink:** V-65 (tier A/B) goes 2,549 → 2,442 and V-68 (tier C/U) 837 → 807.
- **Review:** Codex alone, under the owner's waiver of 2026-11-20 ("Codex-only for now"). Antigravity is out of quota
  until about 2026-11-24, and both Grok routes have expired keys. Each row's notes say so.

## Why

**The site gap.** After the OSHA lane, 1,432 active tier-B/C/U sites still had no evidence row (on this branch).
- 159 of them carry an Atlas FRS link (`data/registry_links.csv`).
- All 165 of those links were first made by EPA's ECHO exporter on a street-exact match.
- None had been turned into evidence.

**What FRS can carry.** FRS caps at B (address at C), so it can't help tier-A sites, but it closes V-65 for tier-B sites
and V-68 for tier-C/U.

## Method

`build.py` runs with no model.

1. **Source:** EPA's FRS state combined files, `state_single_<st>.zip`.
   - Fetched 2026-11-20 from `ordsext.epa.gov/FLA/www3/state_files/` for the 19 states in the frame.
   - Hashes are in the corpus MANIFEST and each row's notes.
   - The files stay outside the repo.
2. **Phantom check:** every link is re-read in EPA's extract (AGENTS.md §4). All 165 were found.
3. **Match:** a site is witnessed when its FRS record meets all of these:
   - same state;
   - same city, or the same ZIP (FRS's city field is sometimes a code);
   - the operator's or site's name (exact or containment, four characters or more, with common abbreviations such as
     MFG and CHEM expanded);
   - and either the site's street (number, street word, and no conflicting street type), or no Atlas street at all.
   Street-type conflicts (Road vs Drive, Street vs Avenue) are what the reviewers rejected in the OSHA lane.
4. **Verdicts** (`ledger.csv`): street and name 120; city and name, no Atlas street 30; name differs 9 (held as leads).
5. **Rows** (`packet_rows.csv`):
   - `existence` for every witnessed site.
   - `address` only for tier-C/U street matches. A C-strength address on a tier-B site would be a V-25 error.
   - No liveness: a registry record is not a dated filing, and FRS records persist after closure.
6. **Citation and notes:**
   - Rows cite "EPA FRS registry ID … (EPA FRS state combined file STATE_SINGLE_<ST>.CSV)", a named source, so V-66
     does not apply.
   - Notes carry the dated fetch marker (V-23) and the file hash, with no staging path (V-67).
7. **Refute** (`review_brief.md`, `--effort deep`, two parts): Codex judged all 166 rows (`review_codex_1..2.json`).
8. **Apply** (`apply.py`): Codex-SOUND rows only. A site whose existence row Codex rejected loses every row. IDs ascend
   from EVD-410477, and baselines are pruned through the TRI lane's `prune_baselines.py`.

## Withheld (14 rows on 13 sites)

Codex rejected existence wherever the FRS name is another company, even when the Atlas site name repeats it:
- **Crane Performance Siding vs Royal Building Products:** SITE-000827.
- **Teijin Automotive vs CSP:** SITE-000840.
- **Drew Foam vs Alleguard:** SITE-000867.
- **Queen City Foam vs Queen City Polymers:** SITE-001145.
- **Koneta vs KN Rubber:** SITE-001474.
- **Carclo Ind vs Carclo Technical Plastics:** SITE-002439.
- **Ashland vs INEOS Composites:** SITE-002580.
- **LORD vs Parker-Hannifin:** SITE-002734, SITE-002745.
- **Molded Fiber Glass Tray vs Molded Fiber Glass Companies:** SITE-002762.

It also rejected three related-entity names:
- **Huntsman Advance Materials vs Huntsman Advanced Materials Americas:** SITE-002749.
- **Evonik Degussa vs Evonik Corporation:** SITE-003234; its address row falls with it.
- **W. R. Grace & Co.-Conn vs W. R. Grace & Co.:** SITE-003552.

**The single-reviewer gate held.** Every one of the four operator mismatches seen in earlier lanes (Crane/Royal, Drew
Foam/Alleguard, Queen City Foam, LORD/Parker) reached review as witnessed, and Codex rejected all of them.

**Circularity check.** Only 3 SOUND rows match through the Atlas site name and not through the operator's legal or
trade names:
- SITE-002725, PPG R&D: "PPG" is under the four-character floor.
- SITE-002757, Westlake Royal Building Products: Royal's current name.
- SITE-002784, Mitsubishi Chem Advanced Material: a singular/plural difference.

Each was read by hand, and each is the operator.

## Defect injections, all caught

- **`build.py plant`, rotated records:** each site was scored against another site's FRS record (different operator,
  different city). Result: 0 witnesses from 165 pairings.
- **`build.py plant`, street-type flips:** the Atlas street type was flipped on every street match where both addresses
  carry one. Result: 0 of 97 still witnessed.
- **`check.py`:** it fails on each of three injections, and passes once they are restored:
  - an altered shard row;
  - a flipped Codex verdict;
  - a tier_effect raised above the registry ceiling.
- **`build.py selftest`:** street types, unit-letter numbers, city aliases (Mt, "City of"), the ZIP fallback,
  abbreviations, the short-name floor, and town-named facilities.

## Record-health leads (no writes)

**Name differs (9).** These sites' FRS records name another company at the same place (`ledger.csv`, `NAME_DIFF`):
- Midwest Tank Services for GMR (SITE-000928);
- Protec Pac for iVEX (SITE-000978);
- Lear for IAC Wauseon (SITE-003466);
- Phoenix Adhesives for RH Adhesives (SITE-004386);
- Industrial Laminates/Norplex for Norplex-Micarta (SITE-003364);
- "JAM Best One" for Best-One Retreading (SITE-001500);
- three that are probably typos or abbreviations on one side: "Tmp Acuisitions New" (SITE-002225), "Auria Homesville"
  (SITE-001496), and Crayola's plant label (SITE-002259).

**Rejected by Codex (13).** The withheld sites above are leads for operator re-verification too.

## Reproduce

```
python3 tasks/evidence-frs-sites-2026-11-20/build.py selftest
python3 tasks/evidence-frs-sites-2026-11-20/build.py match . <frs-state dir>
python3 tasks/evidence-frs-sites-2026-11-20/build.py plant . <frs-state dir>     # expect 0 and 0
python3 tasks/evidence-frs-sites-2026-11-20/apply.py . --start EVD-410477 review_codex_1.json review_codex_2.json
python3 tasks/evidence-frs-sites-2026-11-20/check.py
```
