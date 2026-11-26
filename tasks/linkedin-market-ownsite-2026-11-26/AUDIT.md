# Census audit of the own-site market fills

Label: claude-code linkedin-market-ownsite-2026-11-26
Result: PASS
Sample: Census of seven corrected market values on three organizations and both held owners in PR #571. Replayed all seven evidence quotes on the three captures listed in INPUTS.sha256.
Reviewers: atlas-review-571-codex, GPT-6.2 Astra (OpenAI). Claude Sonnet built the batch.

Main was e4fd658566cfd251154179725a3b7931fd80d37a at audit time. The data tree and task folder matched reviewed head 6baf37cf byte for byte. Against parent bbfbc2d1, three markets_served cells changed. The evidence, archive_links and value_basis tables each gained exactly seven rows. The seven corrected entries in CLAIMS_CHECKED.csv linked each value to its owner's evidence, archive capture and stated basis. The complete organization rows for held owners ORG-001584 and ORG-001470 matched the parent.

All three capture files passed shasum -a 256 -c against INPUTS.sha256. Each evidence quote appeared exactly once in capture_text at its proof offset.

| Owner | Evidence | Market values in evidence ID order | Offset |
|---|---|---|---:|
| ORG-001936 Rotocast | EVD-483150 | plastics_rubber_processors | 611 |
| ORG-001497 Budzar | EVD-483151 through EVD-483154 | pharmaceutical_biotech, chemical_mining_metals_processing, food_processing_foodservice, plastics_rubber_processors | 378 |
| ORG-000147 Chem-Materials | EVD-483155 and EVD-483156 | plastics_rubber_processors, construction_building_products | 2168 |

At the merge, the task checker's problems(load('HEAD^', [build.STORE])) returned zero findings. Replacing Rotocast's market with marine in a scratch copy produced a finding naming ORG-001936, the planted value and the expected plastics_rubber_processors value.

## What this audit is not

The census covers the seven merged claims and preservation of the two held records. It uses the pinned own-site pages. Current market coverage and additional markets beyond the pilot were outside its scope.
