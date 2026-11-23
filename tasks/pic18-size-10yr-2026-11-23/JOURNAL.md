# Ten-year PIC-18 size integration

Packet `f3ad3053`. Application base `15183872` after #507. The integrator
verified the #507 merge data against reviewed head `d2964b36`. The #507 census
audit rides in this PR.

Owner ruling 2026-11-23 12:48 sets a 10-year window with an inclusive
2016-11-23 cutoff, filing-year display, and newer contradictory filing
precedence. Round 24 item 2 requires replay of each filing date at write
time and sampled filing checks in blind audit 12. Both are recorded in
DECISIONS.md and implemented by the packet replay.

`scripts/atlas.py next-id EVD` identified EVD-483048. This pass appends
EVD-483048 through EVD-483065. The pre-pass backup preserves the two
edited canonical CSVs. The raw-input manifest lists all 17 snapshots and
the source rows are keyed by source, member, row and filing identifier.

The canonical diff fills 18 blank or unknown size cells and appends their
18 dated source notes. Each filing witness carries `supports_B`. Nine of these owners qualify only under the longer
window. The 386 site holds in the original unknown frame stay in the
packet. The audit sample is a separate blind-draw step.

The raw replay matched all 17 snapshot checksums and reproduced the four
packet artifacts byte for byte. The cutoff and newer-filing controls passed.
The integration replay passed for all 18 size-band claims and reduced the
size-unknown outcome to 374 of 794 PIC-18 owners. A planted missing claim
failed. Validation and row-loss passed under the heavy lock, and the
binding gate accepted all 18 new filing observations.
