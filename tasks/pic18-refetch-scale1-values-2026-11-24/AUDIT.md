# Audit record for the refetch scale-1 value fills (#559)

Label: claude-code pic18-refetch-scale1-values-2026-11-24
Result: PASS
Sample: census, all 6 evidence rows EVD-483137 to EVD-483142 replayed at their offsets against digest-verified captures
Reviewers: GPT-6.2 Astra (atlas-review-563-codex), a family other than the Claude builder; census run during the review of #563 at `f64a3d26`, record in PR #563 comment 7161500265

For every evidence row under the exact label the reviewer hashed the stored page at its `INPUTS.sha256` path, replayed the quote at the proof offset, read its context, and matched the claimed process token to the same owner's current `processes` cell. All six quotes matched, across five distinct capture bodies.

| Evidence | Owner | Held process | Offset |
|---|---|---|---:|
| EVD-483137 | ORG-001978 SprayWorks | machinery_equipment | 774 |
| EVD-483138 | ORG-001749 STL | testing_lab | 561 |
| EVD-483139 | ORG-001978 SprayWorks | chemical_equipment_supply_polymer_specific | 774 |
| EVD-483140 | ORG-001717 FlexLink | die_cutting_converting | 1148 |
| EVD-483141 | ORG-001655 C4 Polymers | distribution | 4369 |
| EVD-483142 | ORG-001749 STL | machinery_equipment | 2093 |

The parent-to-merge organization diff at `7ea75205` changes four previously blank `processes` cells on four owners and adds six tokens. The "eight values on five owners" in the squash subject was true at `5d650d66`; review later removed C4's `recycling_unspecified` and held Precision Polymer Casting. The merge kept all six surviving values.
