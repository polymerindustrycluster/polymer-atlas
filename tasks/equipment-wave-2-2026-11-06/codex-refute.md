VERDICT: REFUTE (Codex/OpenAI — PR #181, L14)

Reviewed immutable head f66d0d3f8513acf3c1b451a0979c5c8ced6ee56b on review-181; compared range starts at ce4e22e9b509247f31c15fdb10f2edb08aab17b4. Two demonstrated metadata findings remain. No lane code or canonical data was edited.

1. **P2 — Seven Cincinnati instruments incorrectly publish unknown access.** EQP-000116–EQP-000122 all set `access_mode=not_stated` and have empty access witnesses in inputs.csv. The cited [Cincinnati AMCC own page](https://www.ceas.uc.edu/research/centers-labs/advanced-materials-characterization-center.html) explicitly offers external clients assisted and unassisted instrument use at external rates. Its internal hourly-rate table separately identifies SCIOS SEM/FIB, Apreo SEM, TEM, XRD, DSC, TGA and rheometer, covering every submitted instrument. Schema §4.19 requires the stated access mode; these seven rows support `fee_for_service`. Add the access witness and reconcile the seven rows, projection, checks and README's all-not-stated claim. This is a published access fact, without a claim that a particular booking is currently available.

   Proof: fresh `181-clerk-codex-4/raw/uc.html` and `raw/uc.txt` (Rates section, text lines 806–835); The existing raw-name/quote and render checks pass while retaining this incorrect field.

2. **P2 — EQP-000144 combines two distinct instruments into one equipment record.** The [Penn State Colby facilities page](https://sites.psu.edu/colbyrheology/facilities/) groups a PerkinElmer DSC and a Mettler Toledo FSC under one heading, then describes them separately and links separate operating procedures. The packet's own notes acknowledge both instruments, but justify one record using a published text line as the unit. Schema §4.19 permits one instrument, pilot line or named testing service per record; a shared heading is none of those combined units. Represent the two instruments separately, or hold the unresolved combination, preserving immutable ID discipline and reconciling counts, projection, verdicts and rendered output. This finding does not require a new class or a scope ruling.

   Proof: `181-clerk-codex-4/raw/psu-colby.html` and `raw/psu-colby.txt` lines 104–114; EQP-000144 in task inputs and data/equipment.csv. The notes explicitly record the grouping decision.

Reproduce the two findings from the repository root:

```sh
python3 /Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/reviews/181-clerk-codex-4/findings_repro.py
```

Ground-truth and independent checks completed:

- `python3 scripts/validate.py | tail -3`: zero errors; 87 equipment rows. Row-loss guard from agent/claude-code/row-loss-guard, with ROOT set to this checkout and `--base origin/main`: PASS against merge base ce4e22e.
- `python3 tasks/equipment-wave-2-2026-11-06/build.py --raw-check`: 53/53, eight sources, three known positives and fabricated-name negative pass; no additions on replay. `check.py` passes preservation, replay and existing-ID, duplicate-host/name and unheld-host zero-write negatives.
- Independently fetched all eight cited own pages with curl/browser UA: every submitted name and quote found (53/53). Reviewed all 53 records and 10 holds. Random ten changed rows, seed 18120261106: EQP suffixes 103,125,102,114,137,129,134,128,109,135. All ten have supporting fresh source text. Equipment uses the direct §4.19 source contract, so evidence-table rows and verification tiers are inapplicable.
- Independent fabricated raw quote for EQP-000100 makes `--raw-check --apply` fail before any canonical write (`raw-negative.json`). No fabricated host/source result was accepted.
- Recount: 53 additions, 41 Ohio/12 Pennsylvania; eight hosts; ten holds. All 34 pre-existing rows preserved byte-for-byte as the CSV prefix and unchanged by parsed values; 87 total. IDs EQP-000100–000152 are unique and in the claimed block. Existing and new host/name keys are unique. All hosts resolve to held operating institutions; all six program references resolve to CAMP/PROG-000020 under Ohio University. No site references were asserted.
- NASA's named analysis services and multifunction classifications were examined; no additional demonstrated blocker. CSU's Form 3+ SLA classification is supported by the host's model listing and [Formlabs' own technical report](https://formlabs-media.formlabs.com/filer_public/03/b0/03b0fe4e-f643-4d45-89e6-6c13aac94c91/25011026-wp.pdf). MCR301 rotational classification is also described by [Fraunhofer's primary laboratory page](https://www.igb.fraunhofer.de/en/analysis-and-testing-services/surface-analytics/further-analytical-methods/rheology.html).
- `python3 scripts/build_pages.py`: 5,460 HTML files generated. `python3 tasks/equipment-wave-2-2026-11-06/check.py --pages`: all 53 names/classes/access/source URLs found across eight host pages. Rendering accurately reproduces the two disputed metadata decisions; render success does not settle their correctness.
- All 28 manifest entries match their hashes. Only data/equipment.csv and the task folder are changed; neither CRLF federal-frame file nor scripts/schema/EVD files is in the diff. Final `git status --short` is empty.

Artifacts: [findings](181-clerk-codex-4/findings.json), [independent reconciliation](181-clerk-codex-4/reconcile.json), [raw audit](181-clerk-codex-4/raw-audit.json), [random sample](181-clerk-codex-4/random10.json), [negative mutation](181-clerk-codex-4/raw-negative.json), [manifest](181-clerk-codex-4/manifest-check.json). Source snapshots and runnable proofs are in the same directory.

Limits: checked local generated Pages, not a hosted deployment; no claim of physical inventory completeness, instrument operability or current booking availability. Those limits do not weaken the two demonstrated source/schema conflicts.
