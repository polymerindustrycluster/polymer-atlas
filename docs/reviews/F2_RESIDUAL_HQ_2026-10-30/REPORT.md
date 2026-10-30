# F2 — residual headquarters evidence packet

**163 of 163 pinned organizations researched: 52 HQ_FOUND, 111 STILL_UNKNOWN.**
The 52 findings have unallocated address-evidence drafts. No canonical values changed; no county is proposed. This is a bounded public-source research pass, not a claim that all headquarters are resolved.

## Authority and baseline

- Pin: `eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05`, observed 2026-10-30 21:32 UTC.
- Population: every row of `data/organizations_US.csv` at that pin, original order, index 0–162. Exact original-row JSON and SHA256 accompany all rows.
- Branch: `agent/codex/f2-residual-hq`; draft PR #7. Only F2's claim marker changes in the queue; every other entry is preserved.
- Main rechecked at 2026-10-30 21:45 UTC: still the pin. No drift absorbed.
- Packet lane only: no `data/` edits, merges, main pushes, canonical ID allocation, shard changes, parent changes or owner grain rulings.

## Outcome semantics

F2's requested `outcome` is paired with AGENTS' exact `verdict`: HQ_FOUND / VERIFIED means the cited witness supports the proposed headquarters city/state at the source's stated grain and date; STILL_UNKNOWN / STILL_UNCERTAIN means the named settling fact remains necessary. VERIFIED is **not** permission to integrate or a current operating-status/tier finding.

Own-source explicit headquarters, corporate-office or principal-office roles are distinguished from manufacturing, warehouse, showroom, service, mail and registered-agent addresses. State-registry principal-address findings are **principal-office-basis candidates**, not quotations that the registry calls them headquarters. These three candidates (Cytiva US, Blue Water Dynamics, Classic Cultured Marble) warrant integrator confirmation that the filing's principal-office role meets the intended HQ definition; they are address-only `registry/supports_C` drafts.

No county is inferred from city, ZIP, mailing address, service area or parent HQ. Blank proposed county is not an instruction to erase an existing value. Spazzolplastica's existing Summit county conflicts with the own-source Mentor headquarters lead; that county issue remains held. Dicar's explicit HQ label supports Pine Brook city/state only, not a parcel or physical street conclusion. Source city labels such as Sylmar are not silently normalized to municipalities.

## Sources and limitations

The per-organization source ledger names the witness, URL, observation date, retrieval date, access route, concise paraphrase and settling fact. Additional witnesses supplied by helpers are retained in `additional_sources_json`. ISO observation dates do not invent a day for year/month-only documents; coarse dates stay in prose. The shared retrieval date is 2026-10-30.

Research used public web search-index page extractions and direct public pages/PDFs where accessible. A page URL in the ledger is not a representation that a direct HTTP fetch succeeded: indexed page text was often the available witness. Availability failures, empty searches and unrelated lookalikes never mean closure or nonexistence. No private systems, logins, outbound communications or paid datasets were used.

The bounded effort budget is approximately six primary routes/documents per organization, not a six-request minimum. `primary_fetches` records research's primary-page attempts/witness checks (including failures), not search-engine queries, retries of the same cached extraction, or a network-audit counter. Zero means an exact-name search produced no usable primary route, not that the organization was excluded. Two such rows, Pro-Tect Plastics and Eagle Plastics Inc, explicitly retain that limitation and the exact identity/HQ fact needed.

This is a triage-grade source-backed draft: indexed extraction may omit context; dated witnesses may be stale; legal-entity suffixes/brand continuity may need integrator confirmation. Reopen the primary witness before applying any change.

## Important holds and distinctions

- LyondellBasell multiple HQs, Giesecke America entity ambiguity, UBE America conflicting offices, and RESRG generic-versus-holding grain stay unresolved.
- OMNOVA, Lamson, Hankook technical-center duplicate, Paneltech LLC succession, and other lineage/tombstone issues do not inherit a parent's or successor's HQ.
- Zanini Tennessee and GEZOLAN US production sites do not inherit overseas parent HQs. J-LOK Corp is not automatically J-LOK Co or Jennmar.
- Amerityre and Jacuzzi contradictory own pages remain held; inaccessible routes are not adverse status findings.
- DiversiTech's 2013 HQ brochure, Premier Foam's May2008 policy, and Neutron's 2006 court HQ are held for current confirmation rather than promoted on historical evidence alone.
- RPS Composites Inc has a source-backed Canadian HQ candidate (Mahone Bay, NS). Its eventual shard is an integrator decision under Appendix C, not a US-state substitution.
- Spears' own January2020 corporate-office certificate agrees with current company contact, but currentness still merits integration recheck.

## Files and verification

- `verdicts.csv`: exactly 163 population outcomes, original identity, proposed city/state/country, rationale and settling facts.
- `source_ledger.csv`: one named source-route record per organization plus supplemental-source JSON.
- `evidence_draft.csv`: 52 schema-shaped address drafts; evidence_id deliberately empty. No existence/scope/status assertion or canonical tier upgrade.
- `original_rows.csv`: all immutable baseline rows and compact sorted-JSON SHA256 fingerprints.
- `manifest.json`: pin, counts and SHA256 for CSV artifacts.
- `guard_packet.py`: read-only exact coverage, FK, no-ID, verdict, date, class ceiling, original fingerprint, manifest and queue/data-isolation checks.
- `validator.txt`: full pinned-tree validator output, PASS (existing warnings retained).

Run from repository root:
```sh
python3 scripts/validate.py
python3 docs/reviews/F2_RESIDUAL_HQ_2026-10-30/guard_packet.py
```

## Remaining action

**Action:** integrator review; **target:** these 52 HQ candidates and 111 settling facts; **reason:** packet lane cannot adjudicate grain, allocate evidence IDs, move shards or apply canonical updates; **status:** held for review, not a publication blocker. No claim is made that the 111 unknown HQs were found.
