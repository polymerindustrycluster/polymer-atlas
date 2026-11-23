# Blind audit 12 protocol (ATLAS-7, the P1 exit test): protocol only, no sample drawn, no `data/` change

`PROTOCOL.md` is the protocol. `draw.py` is the sealed draw and its frame builder; `sizes.py` makes every number in PROTOCOL section 8 (output: `sizes.json`).
Owner rulings it implements are quoted in PROTOCOL section 1 (DECISIONS.md, 2026-11-23, rounds 17 and 18). It reuses audit 10 and 11's packet machinery
(`tasks/blind-audit-10-2026-11-14/`, `tasks/blind-audit-11-2026-11-17/`) and does not rebuild it.

**First user:** the repo owner, who decides from the report whether PIC-18 is good enough to publish. **Non-use is a finding on 2026-12-21** if the owner has
not answered the section 9 battery by then (recorded in `DECISIONS.md`); until it is answered nothing may draw.

## Check

```
python3 tasks/blind-audit-12-protocol-2026-11-23/sizes.py --selftest
python3 tasks/blind-audit-12-protocol-2026-11-23/draw.py --selftest     # needs origin/main for the real-data part
```

`sizes.py --selftest`: Wilson known answers (same as audit 11), the ruling's 55 and 71 reproduced, 205/460 reproduced within 3 records (203/457), the ruling's "35 at 1%"
shown to be the zero-error size (43 at 1%), exact acceptance numbers, exact enumeration of the two-stage rule checked by Monte Carlo, false pass below 2.5% in every stratum, and
`sizes.json` equal to the computed values. `draw.py --selftest` uses a throwaway seed and synthetic fixtures (no real people rows) and plants each failure: a wrong seed hash,
a second draw into the same folder, a duplicate ID, an ID in both organization tables, a site with no owner, an Ohio site with no county, a record with no region, an unclassified
column, a published-count mismatch, an `--at` that is not a full ancestor SHA, and a stale field table in PROTOCOL.md. It also asserts same input gives the same bytes, stage 1 is a
prefix of stage 2, a different n2 changes nothing before rank n1, plants never stand in for a sampled record, and the seed text is in no output. Last, it builds the real frame at
`origin/main` and requires the site builder's own counts to match (`python3 draw.py frame --at <SHA>` shows it without a seed).

## Not checked

The real draw (no seed seen; the sealed hash is only a constant), the packet builder, the replay harness over the binding gate, reader instructions for the new fields, and whether
the J/K/B classification is complete in meaning (it is complete in columns: a missing column fails). At `1b924786` the real frame has 31 records that fit no stratum, so a draw would refuse (PROTOCOL B6).
