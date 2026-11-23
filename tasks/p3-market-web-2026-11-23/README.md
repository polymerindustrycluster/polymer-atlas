# PIC-18 own-site market integration

Built by: Codex GPT-6.2 Sol
Integrator: atlas-p1-integrator-1
Base: `66b39a53`

The sealed P3 packet replay reconciles 316 market-unknown owners of active
tier A–C PIC-18 sites out of 794. Gemini Hydrogen's first batch met the
pre-registered threshold with four verified owners of 40. The remaining
276 owners were screened under the same read rules. Claude Sonnet supplied
the controller-authorized scale read after Gemini reached its usage limit.
The full packet has 40 observations, of which 29 are verified, nine held
and two rejected.

P3-MKT-000007 remains held under the controller ruling. The other 28
verified observations have a public archived quote and exact proof replay.
They cover 15 canonical market cells (12 organization and three site) and
12 formerly market-unknown owners. The applied frame is 304 market-unknown
owners out of 794, from 316. The new evidence comprises 12
`supports_A`, 15 `supports_B` and one `supports_C` observation.

The evidence and archive tables are append-only. `CLAIMS_CHECKED.csv`
has one corrected row per changed canonical market cell. Several verified
terms can share a cell. `CAPTURE_READS.csv` and `BINDING_PROOF.csv`
cover every appended witness and `OPEN_QUEUE.csv` records the 12 excluded
packet dispositions and their basis. Six are regional-operator binding
holds.

## Replay

`python3 -I tasks/p3-market-web-2026-11-23/check.py --at <head>` replays
the sealed 40-candidate packet, exact capture and archive proofs, full data
delta, claim ledger and frame outcome. The 16 reviewed by-hash bodies are in
private provenance with paths sealed in `INPUTS.sha256`. The controller's
independent store check verified all 16.
