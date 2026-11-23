# Blind audit 12 reading tooling

ATLAS-7 · `claimed:atlas-p1-audit12-tooling 2026-11-23`

## Controller use

The controller retains the draw directory and passes its path to the tooling. The packet builder checks the hashes and counts in the draw receipt, reads public fields from the pinned commit, and checks B6 placements against the frame when the pinned draw reader provides them. The builder consumes the draw's placement decisions and excludes their reasoning from the reader files.

```sh
python3 tasks/blind-audit-12-tooling-2026-11-23/packets.py --draw "$DRAW" --out "$STAGE1"
python3 tasks/blind-audit-12-tooling-2026-11-23/packets.py --draw "$DRAW" --out "$STAGE2" --extend PIC18_RECORDS
```

Use a fresh private stage directory. Stage 1 includes the 18 plants. For stage 2 specify only the strata the decision rule extends. An extension contains only newly released records. Pass each reader their copy of the blind CSV, its SHA-256, these [reader instructions](REVIEWER_INSTRUCTIONS.md), the as-of date and any allowed schema materials. Keep `private_map.csv` for the controller to score plants. The output copies are byte-identical. A leak-scan hit stops the release. Use the blind ID and field in the diagnostic to review the underlying value privately before releasing anything.

### Evidence replay

```sh
lockf -k /tmp/polymer-atlas-heavy.lock python3 -I tasks/blind-audit-12-tooling-2026-11-23/replay.py \
  --draw "$DRAW" --out "$REPLAY_JSON"
```

Keep the report private. To replay an extension, pass the same `--extend` strata. The harness loads the unchanged gate and its dependencies from the pinned commit, runs the gate mechanics and compares verbatim quote words to saved source bytes. Web proofs reuse the gate's proof check and the batch's checksum manifest at the audit SHA. Replay tests binding to the published record at that SHA. The original PR's historical admission is outside this check.

Use `--store` to select the shared store path. For older evidence, `--captures` takes a controller-prepared CSV with header `evidence_id,capture_ref,sha256,path,format`. Each entry must identify a verified, complete, usable capture of that exact source or the indexed archive copy. For a keyed structured source, attest the source extract and specific cited row before supplying its unchanged text as the capture. Use `html` for saved HTML or `text` for UTF-8 source text, with a path under `raw/` or `provenance/`. A capture larger than the gate's 8 MiB limit needs independent reading or a separately identified exact source row. A capture's checksum proves byte identity and still depends on correct source identification. The harness makes no live requests. Unavailable captures, unsupported representations or mechanics that cannot settle a row stay unresolved pending independent reading.

A confirmed mismatch marks the sampled parent FIELD_ERROR. Unsettled evidence marks it UNRESOLVED once, even if several child rows are unsettled. Reconcile this report with the two human-facing reads, lead checks and deterministic derived-field checks before applying the protocol's decision rule. The prototype check gives an indication of the capture coverage gap, even for records with at least one admitted web proof.

## Reading size and assignment

Planned records per stratum come from the sealed `sizes.json`, assuming all six strata remain above their census cutoffs. Each reader also sees three plants per stratum at stage 1. Hours are per reader at a planning assumption of 10 minutes per presented record, including its children. They exclude replay, reconciliation and third reads.

| Stratum | Sample records stage 1 | Additional sample records if extended | Sample records through stage 2 | One reader hours stage 1 / through stage 2 |
|---|---:|---:|---:|---:|
| PIC18_RECORDS | 205 | 255 | 460 | 34.7 / 77.2 |
| REST_OHIO_RECORDS | 55 | 55 | 110 | 9.7 / 18.8 |
| REST_US_RECORDS | 55 | 55 | 110 | 9.7 / 18.8 |
| RESEARCHERS | 55 | 55 | 110 | 9.7 / 18.8 |
| PROGRAMS | 55 | 55 | 110 | 9.7 / 18.8 |
| EVENTS | 55 | 55 | 110 | 9.7 / 18.8 |
| Total | 480 | 530 | 1,010 | 83.0 / 171.3 |

For each of the six strata, use the protocol's Sonnet 5.5 and Codex GPT-6.2 Astra (default tier) as the initial pair, and Gemini 4 Hydrogen for adjudication, wherever all three families are eligible. Screen builder families on the controller side before assigning individual records, including claims from children. A family that built a record is ineligible to read it. If one default primary is excluded and the controller approves rotating assignments, give the two eligible families the primary reads. A required third read with only two eligible families, a record with fewer than two eligible readers, or unresolved builder attribution needs a controller ruling before dispatch. Keep attribution out of all reader files.

## Check

```sh
lockf -k /tmp/polymer-atlas-heavy.lock python3 tasks/blind-audit-12-tooling-2026-11-23/check.py
```

This check uses a synthetic draw and independently checks stage release, plant substitutions, byte-identical packets and leak rejection. It then checks evidence for ten distinct main records from the public process-web batch against the mounted read-only store and requires a replay PASS on each. A planted quoted word absent from the stored capture must produce FIELD_ERROR. Other evidence rows are reported individually as unresolved when no usable capture is indexed.
