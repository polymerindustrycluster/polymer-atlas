# PIC-18 size-sprint hold canaries

Controller-assigned to `atlas-w22-size-unlock`, 2026-11-22. Base `14e0ce9a`, with 396 of 794 PIC-18 organization rows size-unknown. First user is the Atlas controller. The canaries test whether the held public files justify a specific identity or street repair and whether it would produce an OSHA size band under R13. Known-answer controls precede both samples. This packet proposes leads in place of edits to canonical data.

## Result

The two canaries yielded **two usable OSHA size bands** across 40 sampled PIC-18 hold-site rows. Both came from the missing-street frame. They belong to different previously size-unknown PIC-18 organization rows, ORG-000015 and ORG-000155. Applying just those two simulated repairs would move the pinned outcome from **396 to 394 size-unknown organization rows of 794**. This branch changes only the canary packet.

Each sample used a fresh `random.Random(20261122)` on the sorted site IDs of its own published hold reason. The checks reproduced three known #468 fills before drawing either sample. The name classifier re-bound the held operator and the street finder recovered the hidden site street. The matcher reproduced the original source and band for SITE-000006, SITE-000035 and SITE-000062. Two additional known fills, SITE-000043 and SITE-000060, retained their expected street among multiple candidates and correctly went to the ambiguity hold when their Atlas street was hidden.

### Unheld operator name

| Class | Sampled sites out of 20 | Wilson 95% | Projection to 96 sites (Wilson range) |
|---|---:|---:|---:|
| SAME_COMPANY | 0 | 0–16.1% | 0 (0–15.5) |
| OTHER_TENANT | 0 | 0–16.1% | 0 (0–15.5) |
| STILL_UNCERTAIN | 20 | 83.9–100% | 96 (80.5–96) |
| Would receive an OSHA band | 0 | 0–16.1% | 0 (0–15.5) |

The published name frame is mixed. **16 of its 96 sites, including five of the 20 sampled sites**, list Form 5500 only in the original hold. The remaining 80 frame sites, including 15 in the sample, list OSHA. Keeping all 96 in the denominator answers the published-hold question. The OSHA-bearing subset yielded zero proven aliases or other tenants across its 15 sampled sites (Wilson 95% upper bound 20.4%). The per-site packet names the record needed to settle each case.

### Missing street

| Class | Sampled sites out of 20 | Wilson 95% | Projection to 121 sites (Wilson range) |
|---|---:|---:|---:|
| One supported street | 6 | 14.5–51.9% | 36.3 (17.6–62.8) |
| Multiple plausible streets | 4 | 8.1–41.6% | 24.2 (9.8–50.3) |
| No held street witness | 10 | 29.9–70.1% | 60.5 (36.2–84.8) |
| Multiple explicit units | 0 | 0–16.1% | 0 (0–19.5) |
| Street already held by a sibling site | 0 | 0–16.1% | 0 (0–19.5) |
| Would receive an OSHA band | 2 | 2.8–30.1% | 12.1 (3.4–36.4) |

Three of the six single-street cases had only stale OSHA bands. One had a later filing under another operator name. The two qualifying cases used ITA. The point projection of roughly 12 additional banded site rows from the 121-site frame would reduce the PIC-18 outcome to about 384 unknown organization rows only if each projected fill belongs to a different still-unknown organization. Overlap among sites of an organization can reduce that yield. Wilson ranges are sample-rate intervals scaled to the corresponding site frame, with no finite-population adjustment.

## Source and match rules

The size replay calls the #468 matcher with the proposed street or documented alias in memory. It uses the 2021-11-22 cutoff, ranks ITA above inspection, and keeps conflicts and superseding-filing holds. The owner’s round-14 ruling limits Form 5500 counts to leads. A location-role Form 5500 entry can supply a candidate address for the street check. The street search also uses the Ohio OSHA extract, physical ECHO/FRS program facility addresses, the permitted SAM physical extract, and explicit Ohio air permit facility-location blocks. It processed all 84 PDFs present in the snapshot and found 11 labeled civic-location blocks. A permit issuance recipient block supplies no street candidate.

Aliases require a legal/DBA pair at the plant or an Ohio charter chain that binds to the held organization. The available identity files were the public SAM, FMCSA and location-role Form 5500 legal/DBA fields and the five held Ohio SOS filings extracts. Separate Ohio formation records and a recent exact-street OSHA row can corroborate a different business. An OSHA display name, a similar company name, and the parent’s name are insufficient on their own. The Ohio SOS extracts cover selected filings. Full charter histories and live records were outside this pass.

Citations use `raw/path[!member]@ordinal#sha256`. CSV ordinals count data rows after the header. PDF ordinals give page and extracted line. Files contain no raw operator name text, contact fields or street strings. Run from the repository root on the branch with the shared store mounted and the #468 Ohio cache available.

```sh
python3.12 -B tasks/pic18-size-unlock-2026-11-22/build.py --check
git diff --exit-code 14e0ce9a -- data/
```

The packet check regenerates and compares all canary rows, known answers and counts. It checks SHA-256 for the selected witnesses and reopens their OSHA rows from the raw files.

Replay passed on the pinned data. It verified five cited file hashes, reopened nine raw OSHA witness rows, and reproduced all 40 canary decisions. The separate scope check found zero data changes.
