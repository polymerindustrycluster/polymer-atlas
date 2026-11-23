# PIC-18 size bands from ten years of OSHA filings

The owner’s 2026-11-23 12:48 “10 years, dated” ruling is in schema PR #506. For a band written on 2026-11-23, the inclusive cutoff is 2016-11-23. An ITA date is 31 December of its filing year and an inspection date is its open date. A newer admissible filing in a different band supersedes the older observation, including a difference of one band. An older filing is retained as a hold with its locator and the newer band where applicable. The blind audit 12 readers sample the applied bands.

## Frame and results

The controller’s `harness/pic18_unknown.py` outcome at `7a9731f2` reproduced **392 of 794 PIC-18 owners with unknown size** (49.4%). These are distinct organization or ecosystem IDs with an active tier A–C Ohio site in PIC-18. An owner has known size if any such site has a band or the organization has an Ohio band. The reused sprint frame independently yielded the same owner counts and **404 sites** under the unknown-size owners. The 50 band sites applied in #468 and the five applied in #486 are outside this frame.

| Outcome | Count and unit |
|---|---:|
| Proposed fills | 18 site bands across 18 distinct owners |
| Filing behind the proposed fill | 12 ITA site bands, 6 OSHA inspection site bands |
| Proposed evidence | 18 site `size_band` rows, all `supports_B` |
| Current-frame holds | 386 of 404 distinct sites |
| Filing holds at current-frame sites | 124 filings past the cutoff, 51 older filings in a different band from a newer filing |
| Five-year comparison under the same matching and precedence rules | 9 distinct owners qualify |
| Net gain from extending the window | 9 distinct owners |
| Projected outcome after all proposals are applied | 374 of 794 PIC-18 owners with unknown size |

The 26 distinct site rows held for age alone in the prior packet were rerun. Three are eligible, 19 still lack a name-and-street filing within the ten-year cutoff, three lack a held establishment-name match, and one failed the evidence-binding name check. The three eligible rows are already included in the 18.

The source map’s roughly +23 owners came from an early strict run of 92 versus 115 with the age limit removed. The merged sprint’s strict reference reproduced 73 versus 89 on the 443-owner pre-#468 frame, including Form 5500 and the earlier ITA name rules. In the current 392-owner frame under this packet’s rules, an unlimited window would qualify 36 owners versus 9 at five years. The actual ten-year cutoff qualifies 18 versus 9. The age-unlimited comparison therefore adds 18 more owners on net than the actual cutoff. Before the binding and privacy checks, the ten-year matcher proposes 22 owners and the five-year matcher proposes 11. The published count uses the 18 and 9 that pass those checks.

## Filing age and agreement

Across all 794 PIC-18 owners, 115 distinct owners had at least one site with a replayable filing band in **both** 2016–2020 and 2021–2026 using the in-hand snapshots. Each owner had one paired site. The two bands agree exactly for **83 of 115 owners (72.2%)**. For **110 of 115 owners (95.7%)**, they agree within one band. The comparison selects a site band independently within each date range using the same address, operator and evidence checks and the dated precedence rule. It excludes sites where either date range fails qualification. This is an agreement check among owners with usable filings in both periods. Owners qualifying solely from old filings lack a direct check of current size in these files.

## Integration and replay

Apply only the sites in `packet.csv` after the schema ruling, B6 and correction PR 3. Recheck each is still in the unknown-size frame and the matched site and owner names, street and locality still bind. The packet gives the band, source year and existing `BAND-SOURCE` note to append. Allocate evidence IDs at application from the current tree-wide maximum. Evidence `claim_detail` names the year and `observed_date` holds the source date. The site renderer already shows that date on the “Size band” evidence row. The packet produces no canonical data edits.

The original size sprint supplies the OSHA extractors and the civic street, held name, locality, shared-site, later-operator and source checks. ITA `company_name` is used only by the shared-street ambiguity check. Only the establishment name can bind. Form 5500 counts stay leads under SCHEMA v1.19.5. The six Form 5500 files remain in the copied prior input seal and their hashes are checked. Only OSHA files are parsed for this packet. Newer contradictory rows are resolved by filing date before the remaining checks select a band. The old near-cutoff look-back was a pending-owner guard. Under the dated ruling the cutoff determines admissibility. Each emitted evidence quote also passed the repository evidence binding check.

```sh
lockf -k /tmp/polymer-atlas-heavy.lock python3 -I tasks/pic18-size-10yr-2026-11-23/check.py
lockf -k /tmp/polymer-atlas-heavy.lock python3 scripts/validate.py
```

The replay exports the pinned base, verifies all 17 sealed inputs, extracts the Ohio OSHA rows with `python3 -I` and compares all four generated artifacts byte-for-byte. The controls hold a planted 2015 inspection, admit a filing on 2016-11-23 and select the one-band-different newer filing over a higher-precedence older source. Disabling either cutoff or supersession made its probe fail. No fresh sources were fetched.

## Data integration

Applied from the sealed packet at `f3ad3053` on main `15183872` after
correction PR 3 and the R13 schema revision (#506). The 18 Ohio site band
fills cover 18 distinct PIC-18 owners. Each has a dated `BAND-SOURCE` note
and a `supports_B` government-filing evidence row. `CLAIMS_CHECKED.csv`
records the 18 corrected band claims. The note is source bookkeeping for
that same claim.

Recheck the full integration at the requested commit with:

```sh
lockf -k /tmp/polymer-atlas-heavy.lock python3 -I tasks/pic18-size-10yr-2026-11-23/check.py --at <head>
```

The check replays the original packet from the raw store, validates each
candidate on the corrected base, compares the full canonical and claim
diff, and verifies the reduction from 392 to 374 unknown-size owners among
794 owners of active tier A–C PIC-18 sites.
