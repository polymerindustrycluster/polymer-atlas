# PIC-18 refetch scale-1 value fills (second read and data PR)

Built by: Claude Code (Anthropic)

Claimed by atlas-p3-refetch-apply-2 on 2026-11-24. First user is Polymer Industry Cluster staff who read the Atlas process field on the public site. Check for use by 2026-12-20. Base `bb07e85d` (#557 merged).

## Result

**Eight process values in five process cells, on five owners.** Unit and filter: organizations that hold an active tier A–C site in PIC-18 (792). Owners with a blank process (`python3 scripts/value_basis.py --summary`, 792 less owners with values): **331 before, 326 after.** Owners with a blank market: 303 before and after (the one market value the reader found, ST BlowMoulding, is rejected below). Owners with a blank size: unchanged (372).

| Owner | Values | Route of the cited bytes |
|---|---|---|
| ORG-001978 Sprayworks Equipment Group | `machinery_equipment`, `chemical_equipment_supply_polymer_specific` | Wayback `id_` capture of 2026-10-06 (live page unstable) |
| ORG-001749 Standards Testing Laboratories | `testing_lab`, `machinery_equipment` | stable live |
| ORG-001717 FlexLink | `die_cutting_converting` | stable live |
| ORG-001655 C4 Polymers | `distribution`, `recycling_unspecified` | stable live |
| ORG-001992 Precision Polymer Casting | `potting_encapsulation_casting` | stable live |

Each value has one `own_site` activity row (`supports_B`, label `claude-code pic18-refetch-scale1-values-2026-11-24`) whose head names exactly that value, a `BINDING_PROOF.csv` line, an `archive_links` row (V-66) and a generated `stated` row in `value_basis.csv`. Nothing else changes in `data/`: `check.py` diffs every organization row against the merge-base and allows only these cells. The PR also adds `tasks/pic18-refetch-pilot-values-2026-11-24/AUDIT.md` for #557's label (AGENTS section 2a rule 5) and a claim line in `tasks/QUEUE.md`.

## Step 1, second read (Claude, second family; the reader was Codex)

Frame: the controller's `refetch-apply-2-frame.csv` (sha256 `1a176b86…129e`): 28 STATED raw-HTML rows on 12 owners of the 50-owner run. I read every row from the cited page's own text (`second_read.csv`), using the quote with about 350 characters either side.

| Second read | Rows |
|---|---:|
| VERIFIED, applied | 8 |
| VERIFIED, held | 2 |
| REJECT | 18 |

REJECT by reason (rows): group-level wording on the group's site, not the US operator's 4 (all four ORG-003771 rows); subtype word not in the quote 5 (three Guardian rubber and latex rows, "plastic machining" read as CNC, "apply PS labels" read as printing or decorating); generic wording 3 (a "go-to shop" read as distribution; "supply and warehouse" read as distribution; "debonding services" read as contract services); wrong grain 3 (machine fabrication read as polymer fabrication; metal recovery read as polymer recovery; secondary operations on machined parts of unstated material); implied not stated 2 (company history read as an R&D service; "design" in a verb list); out of the §1 meaning 1 (servicing Graco reactors read as `contract_services`).

VERIFIED and held (2): Chemstress `rd_design_engineering` (the page carries a named individual's email and direct phone beside the quote, so the capture stays out of the shared store); GHSP `injection_molding` (the gate's fetcher returns bytes with a different digest from the ledger's stable digest, and no Wayback capture is indexed, so CI cannot replay it).

Rule used: a subtype (CNC, injection, blow, rotational, rubber, latex, printing) counts only when that word or its plain synonym is in the quote. Ledger route "neither" is never applied (3 rows, all REJECT on the words as well).

**The control was not blind to me.** `SUMMARY.md` and `CHECK.txt` in the packet name the false accept (case `bf037ee539`, ORG-001027 Paramont Machine Company, "plastics_machining_cnc"), and I read them before the frame as instructed. I did not open `controls.csv`. Both Paramont rows are REJECT on the words (the quote says "plastic machining", never CNC; the other row is a screw-machine secondary operation with no polymer stated), and the base `processes` cell there already holds `distribution`, so no fill is possible either way. `check.py` carries `CONTROL_OWNERS = {ORG-001027}` and refuses any fill or applied row for it; the controller confirms that ID.

**Grain call on ST BlowMoulding USA LLC (ORG-003771).** Its held website is the group's global site; the quotes ("designs and delivers extrusion-blow moulding machines", "partner of excellence to the main global players in the Industrial Packaging, Automotive and Specialties sectors", "since 1980") are group wording that the page never assigns to the US operator. I treated it as I understand the Absolute Haitian drop on #557 (a statement the page does not attribute to this entity). The named fact that would settle it: a page of the US operator, or an owner ruling that the group site speaks for its US arm.

## Cited bytes and the reading's bytes

The binding gate replays the cited page, not the page the Codex reader saw. For 4 of the 8 applied values the page has changed since the reading (`original_agrees=no` in the ledger: both Sprayworks values, FlexLink, Precision Polymer). The proof therefore uses the ledger's stable bytes (two fetches 120 s apart, equal digest and offset; or the archive capture), and `check.py` requires (a) the quote is character-identical to the reading's, (b) digest and offset equal the ledger's, (c) where the ledger says the page still matches the reading, digest and offset equal the reading's too, and (d) where it does not, the quote with 200 characters either side is identical in the reading's capture and the cited bytes (`reading_window_same=yes`, computed from both files). This replaces #557's "capture equals the reading's bytes" for those rows and is a call the reviewers can overrule.

## Step 2, how the batch was built

`build.py` reads `second_read.csv` (rows with `applied=yes`) and `ARCHIVES.csv`, fetches each cited page with the gate's own `fetch_url` (UA `evidence-check/1`, HTTP 200 only, retried on a refused connection), refuses to proceed unless the bytes hash to the ledger digest and hold the quote exactly once at the ledger offset and carry no individual's email, and writes the cells, evidence rows, archive rows, `BINDING_PROOF.csv`, `FILLS.csv`, `CLAIMS_CHECKED.csv`, `INPUTS.sha256`, then runs `scripts/value_basis.py`. Captures go to the shared store at `provenance/pic18-refetch-scale1-values-2026-11-24/captures/<sha>.html`. Evidence IDs run from EVD-483137 (the base maximum is EVD-483136; the open PR that adds evidence, #543, uses EVD-483118 and EVD-483119).

**Wayback route.** Sprayworks' live page changes between fetches, so the proof cites the `id_` capture of 2026-10-06 (`capture_date` and `captured_at` both 2026-10-06, inside the two years before `observed_date`); its `archive_links` row is that capture. **Archive links for the live proofs.** Wayback already held captures for STL `about-us`, FlexLink and Precision Polymer (ledger, replayed). For STL's rolling-resistance page and both C4 URLs no capture existed, so I asked Save Page Now through `site_corpus.Corpus.request` on 2026-11-24 and read the new captures back in `id_` form with the quote present (CDX timestamps 20261124211447 and 20261124211513).

**Reading by another family.** `BINDING_PROOF.csv` names the reader as Codex (OpenAI), dated 2026-11-24. The builder is Claude (Anthropic). My own read is the second reading and also Anthropic; it is not the reading the gate counts.

`check.py` is the named check. It passes on the clean tree and catches all 28 planted defects: everything #557's check planted (a held value overwritten, a value outside the vocabulary, a quote not in the capture, a wrong offset, a capture digest mismatch, another owner's page, a REJECT row applied, a changed column, a data file outside the allowed set, a missing archive link, extra or duplicated appended evidence, archive or proof rows, a capture whose digest or offset differs from the reading's) and the new ones: a subtype value whose quote lacks the subtype word (CNC, injection), a Wayback-only value without its archive row (and one whose row is a different capture), a fill and an applied row for the control owner, an individual's email in a capture, a cited page whose surrounding words were not shown identical to the reading's, a wrong proof capture date, a changed file outside the allowed set, a missing AUDIT.md. `python3 check.py --fresh` replays by live fetch instead of the store.

## Requests made, and what was not checked

- Requests outside the declared `AtlasSiteCorpus/1.0` agent: the gate's own fetcher (`evidence-check/1`) in `build.py`, `check.py --fresh` and my one-off probes, because the CI gate fetches that way and only its bytes decide admission; two `curl` calls for `c4poly.com/robots.txt` and `www.c4poly.com/robots.txt` (both 200 and empty) to explain why `site_corpus` reported `ROBOTS_BLOCKED` for C4 (it reads an empty robots file as a failure; the page is allowed). C4's quotes were read from the packet's retained capture, which replays.
- The binding gate checks mechanics and replays bytes. It does not decide whether a page states a value; that rests on two readers (Codex, Claude) reading a short quote each, and on my grain and subtype calls above.
- CI re-fetches the live page from another origin. #557's Schibley row passed on the lane machine and failed on the hosted guard, so a live-proof row here can still fail there; a page that changes after this PR fails later replays.
- A fetch that failed or changed is never evidence about the owner. The ledger's route "neither" and the two held rows say nothing about the claim.
- `value_basis.csv` is generated (`scripts/value_basis.py`); the eight `stated` rows follow from the evidence and proof rows.
- Sprayworks `chemical_equipment_supply_polymer_specific` rests on the same sentence as `machinery_equipment`; it names the polymers (polyurethane, polyurea) the machines are for, which is why I kept both tokens.
