# Raw matcher calibration

House NFKD/ascii alphanumeric word-sequence convention; no status inference.

- PASS positive: expected True; text `GF Central Plastics manufactures pipe`, quote `Central Plastics manufactures`.
- PASS normalization: expected True; text `Ritmo’s fusion — equipment`, quote `Ritmos fusion equipment`.
- PASS quote absent: expected False; text `UPM supplies labels`, quote `UPM closed permanently`.
- PASS empty failed response: expected False; text ``, quote `operating`.

Run: python3 tasks/liveness-continuation-2026-11-06/lanes/B/check_packet.py (includes these cases).
