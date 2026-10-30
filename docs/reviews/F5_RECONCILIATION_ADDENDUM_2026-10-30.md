# F5 reconciliation addendum — remaining open item

**Current-main observation: 2026-10-30 23:22 UTC**, pin
`4a406991c9466b10896f17913f9995b541b39713`.
F5 remains claimed on `agent/codex/f5-public-counts`, draft PR #10; this is a
continuation of that task, not a new lane. No queue entry was changed again.

## Result first

The newly published F1 class-map v2 resolves the **creation-frame inventory**:
**2,199 unique created record IDs = 682 organization IDs + 1,517 site IDs**.
Of those, **1,972 are TRI-classified creations = 589 organizations + 1,383 sites**;
**227 NOT_TRI creations = 93 organizations + 134 sites** are excluded from the
F1 TRI sampling population. Thus the queue's 1,517 pass-20–25 site creations
are not all TRI-origin sites. Do not silently relabel all 1,517 as TRI facilities.

The map does **not** resolve the Pennsylvania/PIC-12 QCEW denominator gaps or
prove the separate 1,797-facility campaign verdict accounting. F5's verified
coverage reconciliation therefore remains **open, blocked on named inputs**.
No percentage uses 2,199 or 1,972 as a substitute establishment denominator.

## Pins and drift

The original F5 data pin remains `eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05`.
Comparison to current main shows changes only to `AGENTS.md` and the two
`tasks/f1-class-map/` files. Canonical `data/`, `docs/SCHEMA.md`, and `scripts/`
are byte-identical. Consequently all earlier F5 canonical counts/fingerprints
remain valid at this observation. No silent rebase or absorption was performed.
AGENTS, schema, then queue were inspected in order; new rule 10 was applied.

Map v2 was published at `bf7857a7826ba62cdcf67af3ba718c3d5a9b32be` and is
unchanged at the current-main pin. Sources:
- `tasks/f1-class-map/f1_record_tri_class_mapping.csv` (record-level derived map).
- `tasks/f1-class-map/README.md` (orchestrator's creation-class and correction account).
- F1 draft PR #9, head `5769762851e949d991624e89e777eea1ff24a2db`, reports the same
  2,199/1,972 frame. Its 65-record audit and evidence drafts are not the full
  campaign facility verdict ledger and cannot substitute for it.

Map SHA-256: `86e78616b3c4aac23ceb143fd724acc3e287a64ce9b9071b08088249ec0b8fd7`.

## Reproduced map counts

Unit throughout: **unique created canonical record IDs listed in the map**, not
facilities, companies, current active entities, registry links or verdict rows.
All map rows are included in the first table, independent of current status/tier.

| Creation pass | Organization IDs | Site IDs | Total record IDs | Map class counts |
|---|---:|---:|---:|---|
| 20 | 96 | 177 | 273 | NOT_TRI 227; P1 46 |
| 21 | 5 | 282 | 287 | P1 287 |
| 22 | 50 | 273 | 323 | P1 84; P2 180; P3 59 |
| 23 | 163 | 280 | 443 | P3 443 |
| 24 | 134 | 251 | 385 | P3 269; P4 116 |
| 25 | 234 | 254 | 488 | P4 488 |

| Creating-facility class | Organization IDs | Site IDs | Total record IDs |
|---|---:|---:|---:|
| P0 | 0 | 0 | 0 |
| NOT_TRI | 93 | 134 | 227 |
| P1 | 8 | 409 | 417 |
| P2 | 21 | 159 | 180 |
| P3 | 269 | 502 | 771 |
| P4 | 291 | 313 | 604 |

Assertions passed: 2,199 IDs are unique; every ID resolves to a canonical row
of its declared grain; pass and class values use the explicit map vocabulary;
per-pass sums equal the total; all published map README class/type totals agree.
Pass 20's 227 NOT_TRI entries agree with 89 SC-wave + 138 Q01/Q02 records.
Pass 20's 46 TRI records and pass 21's 287 records agree with the README's
explicit counts. F1's independently published aggregate also agrees.

**Source-level limit:** this verifies the published derived map, not its absent
raw allocation files. The per-pass `id_allocation.csv`, packet design files and
original journals remain in orchestrator staging, not this public tree. Therefore
this addendum does not claim to rerun their creation-class whitelist or to
independently certify every per-pass creation count against those originals.
Raw-marker rows were never input to this calculation. The README explicitly
withdraws v1's 2,204/P3 776 and explains the five `org_create_watch` duplicates;
v2's 2,199/P3 771 are the only accepted frame counts. Any conflicting raw
allocation count must stop reuse pending investigation under AGENTS rule 10.

P0 has zero creations in this frame: it concerns links on held records. A zero
P0 creation count is not zero P0 facilities, links, errors or review obligations.

## Separate ledgers — no false reconciliation

| Universe | Unit/filter | State |
|---|---|---|
| Current Atlas | All canonical organization/site rows | 4,179 / 5,770; unchanged |
| Pass-20–25 map | Unique created IDs, all origins/statuses | 2,199; reproduced |
| F1 eligible population | Map rows with class P1–P4 | 1,972; reproduced; no P0 creations |
| Campaign worklist | Facilities with one final campaign verdict | Reported 1,797 = 1,657 VERIFIED + 84 REJECT + 56 STILL_UNCERTAIN; arithmetic only |
| Canonical TRI registry | registry == TRI_TRIFID, all statuses | 2,153 rows / 2,147 distinct identifier strings / 1,193 org IDs; unchanged |
| QCEW coverage benchmarks | Official annual-average private establishments, geography × NAICS | Not derivable from any campaign universe |

Creation rows can include an organization and its site, and map classes exclude
non-creations and rejected/uncertain facilities. Distinct TRIFIDs in such a map
would still not reconstruct the full worklist or establish exact-once verdicts.
The unmatched differences above are differences in universe, not arithmetic
residuals to allocate or infer into missing data.

## Exact remaining inputs and status

1. **PA QCEW — BLOCKED / input unavailable, not denied authorization.** Supply
   the banked official 2023 annual Pennsylvania extract (area 42000), ownership
   5, relevant NAICS cells and `annual_avg_estabs`, disclosure flags, vintage,
   source URL and file hash. Earlier direct API fetch was inaccessible; no new
   broad research attempted in this continuation. Numerator 396 active/unknown,
   A–C NAICS-326 site rows is reproduced; no PA ratio is published.
2. **PIC-12 QCEW — BLOCKED / input unavailable.** Supply the banked
   `denominators_pic12.csv`, `denominators_notes.md` and underlying official
   county cells/extracts, with FIPS/vintage/ownership/disclosure metadata.
   Historical 367 is not freshly validated by the class map. The existing
   62–63 NAICS-3259 explanation also remains unverified. Current NAICS-326
   numerators 423 A–C / 437 any-tier active/unknown sites remain reproducible.
3. **Final TRI campaign facility accounting — BLOCKED / source ledger absent.**
   Supply the complete 1,797-facility worklist plus final verdict ledger keyed
   by facility/TRIFID and any held/creation/link crosswalk. Need uniqueness,
   exhaustive membership and one final verdict per facility, not only selected
   creation IDs. No substitute from the 65-record blind audit is valid.
4. **Raw per-pass creation provenance — LIMITED to published map.** Supply the
   exact allocation/design/journal inputs and pass-specific allowed creation
   classes if independent rebuild beyond v2 map reconciliation is required.
   Published map uniqueness, canonical resolution, distributions and README
   totals are now checked; raw derivation is not.

OH's previously checked published QCEW-2023 benchmark and all canonical count
calculations remain completed work. No data changes, IDs, merges, contacts or
main pushes are requested or performed. The original report's other historical
external-source qualifications remain; this addendum does not reverify them.

## Reproduce map checks

At the current-main pin, execute this read-only standard-library snippet; output
is JSON. All counts derive from the map, never from ID bounds or marker names.

```python
import csv,collections,hashlib,json,subprocess
from pathlib import Path
pin='4a406991c9466b10896f17913f9995b541b39713'
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==pin
p=Path('tasks/f1-class-map/f1_record_tri_class_mapping.csv')
rr=list(csv.DictReader(p.open()));ids=[r['record_id'] for r in rr]
assert len(ids)==len(set(ids)), 'duplicate record IDs'
assert all(r['record_type'] in ('ORG','SITE') and r['creation_pass'] in ('20','21','22','23','24','25') and r['tri_class'] in ('P0','P1','P2','P3','P4','NOT_TRI') for r in rr)
held={}
for kind,pattern,key in [('ORG','organizations_*.csv','org_id'),('SITE','sites_*.csv','site_id')]:
 rows=[r for f in sorted(Path('data').glob(pattern)) for r in csv.DictReader(f.open())]
 assert len(rows)==len({r[key] for r in rows})
 held[kind]={r[key] for r in rows}
assert all(r['record_id'] in held[r['record_type']] for r in rr)
counts=lambda rows:dict(sorted(collections.Counter(r['record_type'] for r in rows).items()))
out={'main_pin':pin,'map_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'unique_records':len(ids),'types':counts(rr),'classes':dict(sorted(collections.Counter(r['tri_class'] for r in rr).items())),'per_pass':{},'class_by_type':{},'raw_allocation_classes_revalidated':False}
for v in sorted({r['creation_pass'] for r in rr}):
 rows=[r for r in rr if r['creation_pass']==v];out['per_pass'][v]={'total':len(rows),'types':counts(rows),'classes':dict(sorted(collections.Counter(r['tri_class'] for r in rows).items()))}
for v in sorted({r['tri_class'] for r in rr}):out['class_by_type'][v]=counts([r for r in rr if r['tri_class']==v])
for k,v in [('total',2199),('ORG',682),('SITE',1517)]:assert (len(rr) if k=='total' else out['types'][k])==v
assert out['classes']=={'NOT_TRI':227,'P1':417,'P2':180,'P3':771,'P4':604}
print(json.dumps(out,indent=2,sort_keys=True))
```

Checks also rerun at current main: full validator PASS, SQLite build PASS,
37 tests PASS; generated build files are not committed. The F5 branch's docs-only
change set was validated separately. No CI claim. Recheck main and source pins
before integration, and keep F5 coverage-count reconciliation open until its
required sources are supplied and checked.
