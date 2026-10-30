# Audit 8 resumption — 2026-10-30

The owner supplied an authoritative class map on main `65dc7d4f2810b144d6fdc6e377c6bc07b7e6cf89` at `tasks/f1-class-map/f1_record_tri_class_mapping.csv`, with build/column documentation alongside it. This is an **explicit metadata-pin advance**, not an absorbed data revision. The audit branch retains its original main ancestor `eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05`; both revisions have identical `data/` tree object `10d3144d9c3527d3ca9d819586af7d3b9197a2e1`. The only main changes are the two class-map files. AGENTS.md, SCHEMA.md and QUEUE.md are unchanged; instructions were checked again before resumption.

## Pre-draw discrepancy — owner clarification pending

The owner described the map as 2,204 creations (687 organizations + 1,517 sites), correcting the prior 2,199 reconstruction. Before drawing, two independent checks found the CSV contains **2,204 rows but 2,199 distinct record IDs: 682 organizations + 1,517 sites**. Five IDs occur twice, with identical full rows in each pair: ORG-004131 (Jasper), ORG-004218 (Barnhardt), ORG-004229 (Fiberon), ORG-004252 (Carlstar), and ORG-004288 (Timken). They were already in the ID-difference population; they are not five additional unique records.

Raw row class counts: P0 0, P1 417, P2 180, P3 776, P4 604, NOT_TRI 227. Distinct-ID class counts: P0 0, P1 417, P2 180, P3 771, P4 604, NOT_TRI 227. The map README correctly says 2,204 rows but incorrectly equates that with unique creations and says the previous sample frame omitted the five watch organizations.

**No draw has occurred.** The original fixed seed and allocation remain untouched. Sampling 2,204 rows would double-weight five organizations, contrary to a unique-record audit. The parent task has the machine-backed discrepancy and is requesting authorization to use the deduplicated **2,199-unique-record frame (1,972 eligible TRI records after excluding NOT_TRI)**. The source map is not edited by this lane.

P0 has no creations by construction. No artificial P0 stratum will be drawn: auditing P0 links requires a separate pre-existing-record/link-row frame and a protocol amendment. Class is the creating facility priority, not prior held status. No mixed-class organizations are reported by the source. All NOT_TRI rows are pass 20.

The independent sampler receives the map; verifiers will receive identity-only search keys. Existing evidence and source notes remain sealed until every independent verdict is frozen. No canonical data changes or ID allocations are made.

## Resolution and v2 metadata pin — 2026-10-30 22:58 UTC

The owner confirmed the v1 duplication was an orchestrator-map error: each of the five watch markers duplicated a normal `org_create` allocation. The prior 2,199 reconstruction was correct; the owner's earlier “5 short” statement is retracted in the v2 README. The owner explicitly authorized the unique-record frame and proceeding with the draw.

Corrected v2 metadata pin: `bf7857a7826ba62cdcf67af3ba718c3d5a9b32be`, same class-map paths. Full frame **2,199 unique creations = 682 organizations + 1,517 sites**; class counts P0 0, P1 417, P2 180, P3 771, P4 604, NOT_TRI 227, unresolved 0. Eligible TRI creation frame **1,972 unique records**. Source v2 is used, rather than silently repairing v1. The original data pin remains unchanged; only the map and its README differ from the original tree. Instructions and schema remain byte-identical. The fixed seed/allocation protocol is now applied to this validated unique frame; no previous draw occurred.
