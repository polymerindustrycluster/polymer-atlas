# Evidence blindness and limited metadata exposure

Post-freeze transparency clarification, 2026-10-30 23:23 UTC. The original `PROTOCOL.md`, draw and blind-verdict files are not rewritten.

The independent sampler withheld record sources, evidence rows, source notes, creation tiers and the per-record class manifest from verification workers. Existing evidence was first released only after all 65 verdicts were frozen, as recorded in the freeze/start manifests.

However, verifier workers inherited the task conversation. The owner's earlier map-correction instruction named five watch organizations and explicitly described them as P3. One of those five, **Carlstar ORG-004252**, was subsequently sampled. Its verifier could therefore know that class from task context even though the identity-only batch did not carry it. No creation tier, original evidence row, source note or previous per-record verification rationale was exposed through that instruction.

Consequently this is an **evidence-blind audit, not an absolutely metadata-blind experiment**. Identity and location were deliberately provided as search keys; Carlstar additionally had possible class exposure. The protocol's stronger intended tier/class shielding was not perfect for that one class label. This does not warrant pretending the exposure did not happen, changing the random draw, dropping the record or rewriting its frozen verdict. The full 65-record sample and all outcome denominators remain intact. There is no evidence in the observed workflow that this class label supplied the independent headquarters source or its finding, but absence of influence cannot be proved.

The required boundary—no reading the record's own evidence rows/source notes until the independent verdict is written—was maintained. The source-backed field discrepancy, uncertainty and weighting caveats remain as originally assessed. Future runs should start verifier workers without inherited sampling discussion, supplying only protocol plus identity-only batches.
