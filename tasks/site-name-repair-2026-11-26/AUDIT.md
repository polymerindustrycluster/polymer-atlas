# Census audit of the site-name repair batch

Label: claude-code site-name-repair-2026-11-26; site-name-repair-2026-11-26
Result: PASS
Sample: Census of all six corrected site names and all 44 held site rows in PR #569. Replayed the six evidence quotes on the six captures listed in INPUTS.sha256.
Reviewers: atlas-review-571-codex, GPT-6.2 Astra (OpenAI). Claude Sonnet built the batch.

Main was bbfbc2d1e9e2a0f4901049762a335a65dc8ade61 at audit time. Compared with its parent 1fa7c334, the Ohio site shard retained exactly the same IDs. The six changed rows matched the six corrected IDs in CLAIMS_CHECKED.csv. Only site_name and notes changed on each. Both cells matched reviewed head f282f5fc exactly. Each old and new name also matched its packet. All 44 held rows matched the parent and reviewed head across every column.

Each stored capture passed SHA-256 verification before replay. For each corrected claim, the evidence and proof agreed on site ID and claim digest. The evidence quote equaled the packet quote and matched capture_text at the recorded offset.

| Site | Merged site name | Evidence | Offset |
|---|---|---|---:|
| SITE-000063 | Akron Gasket and Packing Enterprises — Tallmadge | EVD-483144 | 336 |
| SITE-000081 | Novex Operating Company, LLC — Barberton | EVD-483145 | 1190 |
| SITE-000279 | Carlisle TyrFil — Berea | EVD-483146 | 585 |
| SITE-000401 | IMS Company — Chagrin Falls | EVD-483147 | 64 |
| SITE-000646 | Third Dimension Division — Geneva | EVD-483148 | 4113 |
| SITE-002008 | Stroup Belting | EVD-483149 | 1907 |

The independent census command, `PYTHONDONTWRITEBYTECODE=1 python3 /tmp/replay569hng.py`, exited 0. Replacing SITE-000063's name with “Wrong rename” in a scratch copy caused the same reviewed-head comparison to fail on SITE-000063.

## What this audit is not

The findings cover this merged batch and its pinned captures. The held-row check establishes preservation of those records. Current signage and subsequent operator changes were outside the audit.
