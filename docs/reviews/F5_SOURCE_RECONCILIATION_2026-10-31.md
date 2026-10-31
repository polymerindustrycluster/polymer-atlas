# F5 source-packet reconciliation — 2026-10-31

**Explicit metadata advance:** `884c2c0344b6d071406761ee39a203eac7e07d72`,
observed 01:49 UTC, supersedes the earlier `4a406991` metadata observation.
Only twelve `tasks/f5-source-packet/` files were added. Canonical data, schema
and scripts are byte-identical to F5's `eceead3a` data pin. Existing PR #10
claim/queue preserved; no rebase, data edits, IDs, merges or main pushes.

## What closes, and what does not

- **Closed:** PA/OH state denominator availability and packet-level provenance;
  51 unique jurisdiction rows in the banked derived extract checked, 2023 separated from 2024 sensitivity.
- **Closed:** ledger uniqueness/outcome accounting and all creation joins:
  1,797 unique TRIFIDs; 1,657 VERIFIED / 84 REJECT / 56 STILL_UNCERTAIN.
- **Closed:** independent allocation/design reconstruction reproduces every
  field of all 2,199 published map rows exactly, excluding marker classes.
- **Still open:** PIC-12 aggregate denominator cells are absent; the supplied
  county table contains only six-digit codes, so it cannot reproduce 367.
- **New discrepancy:** seven ledger link outcomes fail canonical reconciliation
  after design-key resolution. These are packet/accounting issues, not automatic
  canonical corrections. Exact cases below; no outcome is silently rewritten.

This supersedes earlier F5 statements that the ledger and allocation inputs
were absent. Those statements remain dated history, not current blockers.

## Denominators: provenance, filters and count ratios

The published packet names BLS CEW annual state area extracts, filtering
`own_code=5`, `qtr=A`, `size_code=0`, taking `annual_avg_estabs`.
2023 is the reference year; 2024 values are sensitivity only. The packet is a
banked derived extract, not a full raw API response: filters are documented by
its source/notes columns, not independently rerun against raw official rows.
Direct opens of official [PA 2023](https://data.bls.gov/cew/data/api/2023/a/area/42000.csv)
and [Ashtabula 2023](https://data.bls.gov/cew/data/api/2023/a/area/39007.csv)
on 2026-10-31 remained inaccessible through the research tool. Ohio's published
2023 PDF anchors were independently opened in the original F5 pass.

Numerators below: **Atlas site rows** in stated physical state, own primary
NAICS prefix, `operating_status` active/unknown; primary tiers A/B/C, recorded
any tier. No parent, secondary-code, ring or manufacturing-site-type inference.
Denominators: packet's **QCEW-2023 private annual-average establishments**.
These are **unmatched count ratios, not coverage/recall**; different vintages,
classification and non-manufacturing Atlas sites can produce values above 100%.

| State | NAICS | A–C sites | Any-tier sites | QCEW 2023 establishments | A–C ratio | Any-tier ratio |
|---|---|---:|---:|---:|---:|---:|
| OH | 326 | 815 | 988 | 890 | 91.6% | 111.0% |
| OH | 3261 | 648 | 789 | 706 | 91.8% | 111.8% |
| OH | 3262 | 167 | 199 | 184 | 90.8% | 108.2% |
| OH | 3252 | 82 | 98 | 115 | 71.3% | 85.2% |
| OH | 3259 | 79 | 91 | 153 | 51.6% | 59.5% |
| OH | 325211 | 63 | 77 | 78 | 80.8% | 98.7% |
| OH | 325212 | 16 | 18 | 28 | 57.1% | 64.3% |
| OH | 325991 | 51 | 57 | 36 | 141.7% | 158.3% |
| PA | 326 | 396 | 396 | 642 | 61.7% | 61.7% |
| PA | 3261 | 347 | 347 | 551 | 63.0% | 63.0% |
| PA | 3262 | 49 | 49 | 91 | 53.8% | 53.8% |
| PA | 3252 | 86 | 86 | 62 | 138.7% | 138.7% |
| PA | 3259 | 24 | 24 | 135 | 17.8% | 17.8% |
| PA | 325211 | 75 | 75 | 54 | 138.9% | 138.9% |
| PA | 325212 | 9 | 9 | 4 | 225.0% | 225.0% |
| PA | 325991 | 22 | 22 | 23 | 95.7% | 95.7% |

Disclosure qualifications: OH 325991 and PA 325211/325212 carry disclosure
flags, but their establishment values are populated. Flags are not converted
to zero or silently discarded; employment/wage suppression is not assumed to
suppress an available establishment count. PA 326 = 642 = 551 + 91; OH 890 =
706 + 184. 2024 326 values OH 917 / PA 644 are not mixed into this table.
The state's `ring2_component_sum` is an arithmetic component sum, not an
official sector denominator. No missing state cell becomes zero.

### County table is distinguishable, but insufficient for aggregate ratios

240 unique county×code rows = 12 counties × 20 **six-digit** codes:
96 QCEW-sourced values, 35 CBP-sourced values, 97 blank unknown cells, and 12
rows for invalid/obsolete 326192 marked “Neither source — code not in NAICS
2017,” carrying literal 0. Those 12 are **not measured zero establishments**;
exclude them from benchmark arithmetic. The 97 blanks remain unknown, including
cases where no-row and withholding cannot be distinguished. Ashtabula's notes
also disclose that CBP cells were not pulled, so “Neither source published”
must not be generalized into a proven two-source absence.

Each cell's source is named; the table must not be summed across CBP and QCEW
into an official denominator. It has no rows at 326, 3261, 3262, 3252 or 3259.
Thus **367 remains a packet-README assertion**, not independently reproduced
from supplied cells. The replacement of erroneous Ashtabula 39005 (Ashland)
with 39007 is explicit and consistent in all Ashtabula packet rows; this FIPS
correction is distinct from validating the aggregate 367. No inferred suppressed
values or mixed-system lower bound is published as coverage.

**Smallest input to settle 367:** the 12 PIC-12 county NAICS-326 aggregate
rows from official QCEW-2023, own_code=5, qtr=A, size_code=0, annual_avg_estabs,
with FIPS/area titles, disclosure flags and source provenance. Add 3261/3262
(24 more rows; 36 total) for the subfamilies; add 3252/3259 (24 more rows) to settle those published family denominators and the
old 62–63 discrepancy. The source README supplies only the API URL template,
not these aggregate rows. Current PIC-12 numerator counts remain 423/437 for
NAICS326; conditional ratios against 367 in the older report remain conditional.

## Ledger and creation-frame checks

Unique ledger IDs and outcomes agree exactly with packet README; verdict tiers
are A 526, B 926, C 205, blank 140 (the 84 rejects + 56 uncertain facilities).
Facility priority-class counts: P0 252 / P1 438 / P2 171 / P3 571 / P4 365.
These are **facility** counts, not the creation-map strata counts.

1,383 ledger facilities have a creation outcome. Every `created_org_ids` and
`created_site_ids` set equals the independently rebuilt frame's reverse TRIFID
join. Ledger link-org and link-site columns are each populated for 1,648
facilities; nine VERIFIED facilities have neither, in addition to all 140
non-VERIFIED facilities. VERIFIED is therefore not synonymous with integrated
link/site creation. Full original EPA form/extract screening (77,295 form rows
→ 21,482 facilities → worklist) was not supplied/rebuilt; the completed check is
of the 1,797-row published worklist ledger, not national TRI completeness.

Builder inspected before use: original has fixed private staging paths and
writes an output CSV. It was not executed unmodified. The independent code below
reads packet files only, uses exact pass creation whitelists (`org_create` and
`site_create` in passes 20–24; `create` in pass 25), asserts ID uniqueness and
all design/worklist joins, then compares every rebuilt field with map v2.
Five `org_create_watch` rows, edits, repoints, folds, flips, unused counters and
other annotation/evidence/link classes are excluded. Withheld notes were neither
needed nor sought. Per-pass ORG/SITE counts: 20=96/177, 21=5/282, 22=50/273,
23=163/280, 24=134/251, 25=234/254. Sum 682/1,517 = 2,199 unique IDs; exact map
comparison passes. TRI subset 589/1,383 = 1,972; NOT_TRI 93/134 = 227; P3=771.

### Seven link-outcome discrepancies — integrator review, no data mutation

Ledger link columns sometimes contain packet design keys rather than canonical
IDs. Resolve using unique explicit allocation keys (including earlier passes),
and site-allocation parent fields joined to design org_ref for named aliases;
never equate a proposed design with a held site. Examples: ProVia’s explicit
`flip_to_held` resolves to ORG-001053; Zeus’s site allocation parent joined to
design org_ref resolves its NEW alias to ORG-003941 (also corroborated by its
existence/scope evidence allocation references). These are metadata crosswalks,
not name guesses. After these resolutions:

| TRIFID | Ledger proposed link | Observed issue at pin |
|---|---|---|
| 77511QNTMC2MILE | ORG-000033; Chocolate Bayou site design | Site design has no allocation; stated org/TRIFID registry pair absent |
| 25401KRPLS2011M | ORG-001409; MAAX Martinsburg design | Site design has no allocation; stated pair absent |
| 46563KRPLS1001N | ORG-001409; MAAX Plymouth design | Site design has no allocation; stated pair absent |
| 9176WPCFCR1671S | ORG-002216; Elite Comfort Ontario design | Site design has no allocation; stated pair absent |
| 5254WNHNCT299IN | ORG-002181; Inhance Centerville design | Site design has no allocation; stated pair absent |
| 92807XRXSC1210N | ORG-003367; Xerxes Anaheim design | Site design has no allocation; stated pair absent |
| 81503CLRDC56924 | ORG-003165; resolves SITE-004546 | Registry pair absent for stated org; held site operator is ORG-004005 |

These seven are VERIFIED ledger facilities. Six have no created IDs and no
resolvable site allocation, and the seventh maps to a held site under another
operator. **Required action:** provide the final integration disposition/crosswalk
for these seven ledger rows, distinguishing proposed from applied links and
explicit holds/reparents; correct the public ledger/report semantics if needed.
Do not automatically add links or rewrite parents to make totals agree. This
is a source-accounting mismatch, not a verdict that any facility is nonexistent.

## Reproduction, fingerprints and validation

`F5_SOURCE_RECONCILIATION_CHECKS_2026-10-31.json` retains every source-file
SHA-256, excluded allocation-class counts, per-pass totals and exact join issues. This is the compact checker output: the
1,797-entry `resolved_links` array is omitted; all other fields are unchanged.
The code below is the independently run checker (save outside the repository,
run from the pinned current-main checkout); it writes only `/tmp` analysis.
No canonical modification, network call or ID allocation occurs.

```python
import csv,collections,json,hashlib
from pathlib import Path
P=Path('tasks/f5-source-packet')
def read(p): return list(csv.DictReader(p.open()))
ledger=read(P/'tri_worklist_verdict_ledger.csv'); L={r['trifid']:r for r in ledger};assert len(L)==len(ledger)==1797
idx=read(P/'frame_design_key_index.csv');print('index_packets',collections.Counter(r['origin_packet'] for r in idx))
print('outcomes',collections.Counter(r['verdict'] for r in ledger));print('tiers',collections.Counter(r['verdict_tier'] for r in ledger))
frames=[];skip={};passcounts={}
for n,w in zip(range(20,26),['p001-p006','p007-p012','p013-p018','p019-p024','p025-p030','p031-p036']):
 alloc=read(P/f'frame_allocations_pass{n}.csv');allowed={'create'} if n==25 else {'org_create','site_create'}
 chosen=[r for r in alloc if r['class'] in allowed];skip[str(n)]=dict(collections.Counter(r['class'] for r in alloc if r['class'] not in allowed))
 designs=[r for r in idx if r['origin_packet']=='TRI '+w]; ds={r['design_key']:r for r in designs};assert len(ds)==len(designs)
 extra={r['design_key']:r for r in idx if r['origin_packet'] in ('SC_WAVE_1','CANDIDATE_QUEUE_Q01_Q02')}
 for a in chosen:
  rid,key=a['allocated_id'],a['source_key'];kind='ORG' if rid.startswith('ORG-') else 'SITE';assert rid.startswith(('ORG-','SITE-'))
  out=dict(record_id=rid,record_type=kind,creation_pass=str(n),origin='',tri_class='',packet_id='',trifids='',mixed_class='')
  if key in ds:
   d=ds[key];assert d['design_kind']==('org' if kind=='ORG' else 'site')
   tfs=sorted({d['tri_trifid']} if kind=='SITE' else {s['tri_trifid'] for s in designs if s['design_kind']=='site' and s['org_ref']==key and s['tri_trifid']})
   assert tfs and all(t in L for t in tfs)
   classes=sorted({L[t]['priority_class'] for t in tfs});assert len(classes)==1
   out.update(origin='TRI',tri_class=classes[0],packet_id=';'.join(sorted({L[t]['packet_id'] for t in tfs})),trifids=';'.join(tfs))
  else:
   assert n==20 and key in extra,(n,key)
   out.update(origin='NOT_TRI',tri_class='NOT_TRI',packet_id=extra[key]['origin_packet'])
  frames.append(out)
 passcounts[str(n)]=dict(collections.Counter(r['record_type'] for r in frames if r['creation_pass']==str(n)))
assert len(frames)==len({r['record_id'] for r in frames})==2199
published=read(Path('tasks/f1-class-map/f1_record_tri_class_mapping.csv'))
assert {r['record_id']:r for r in frames}=={r['record_id']:r for r in published},'frame mismatch'
created=collections.defaultdict(lambda: {'ORG':set(),'SITE':set()})
for r in frames:
 for t in filter(None,r['trifids'].split(';')):created[t][r['record_type']].add(r['record_id'])
for r in ledger:
 for kind,col in [('ORG','created_org_ids'),('SITE','created_site_ids')]:assert set(filter(None,r[col].split(';')))==created[r['trifid']][kind],(r['trifid'],col)
orgs={r['org_id']:r for p in Path('data').glob('organizations_*.csv') for r in read(p)}
sites={r['site_id']:r for p in Path('data').glob('sites_*.csv') for r in read(p)}
links={(r['org_id'],r['registry_id']) for r in read(Path('data/registry_links.csv')) if r['registry']=='TRI_TRIFID'}
issues=[]; resolved_links=[]
resolvers={}
for n in range(20,26):
 lookup=collections.defaultdict(set)
 for a in read(P/f'frame_allocations_pass{n}.csv'):
  value=a['allocated_id'] if a['class'] in ('org_create','site_create','create') else (a['resolves_to'] or a['allocated_id'])
  if a['source_key'] and value.startswith(('ORG-','SITE-')) and not a['class'].startswith('next_free'):
   lookup[a['source_key']].add(value)
 resolvers[n]=lookup
global_refs=collections.defaultdict(set)
for lookup in resolvers.values():
 for key,vals in lookup.items():global_refs[key].update(vals)
# Explicit site allocation parent (resolves_to) + design org_ref bridges aliases.
for n in range(20,26):
 for a in read(P/f'frame_allocations_pass{n}.csv'):
  if a['class'] not in ('site_create','create') or not a['allocated_id'].startswith('SITE-'):continue
  for d in idx:
   if d['design_kind']=='site' and d['design_key']==a['source_key'] and d['org_ref'].startswith('NEW:') and a['resolves_to'].startswith('ORG-'):
    global_refs[d['org_ref']].add(a['resolves_to'])
for r in ledger:
 n=20+(int(r['packet_id'].split('-')[-1])-1)//6
 def resolve(value,kind):
  if not value or value.startswith(('ORG-','SITE-')):return value
  hits={v for v in global_refs.get(value,set()) if v.startswith(kind+'-')}
  if len(hits)!=1: issues.append([r['trifid'],'unresolved design reference',value,sorted(hits)]);return ''
  return next(iter(hits))
 oi,si=resolve(r['link_org_id'],'ORG'),resolve(r['link_site_id'],'SITE')
 if oi and oi not in orgs:issues.append([r['trifid'],'org FK',oi])
 if si and si not in sites:issues.append([r['trifid'],'site FK',si])
 if oi and (oi,r['trifid']) not in links:issues.append([r['trifid'],'missing canonical registry link',oi])
 if oi and si in sites and sites[si]['org_id']!=oi:issues.append([r['trifid'],'site operator differs',si,oi,sites[si]['org_id']])
 resolved_links.append({'trifid':r['trifid'],'org_id':oi,'site_id':si})
C=read(P/'qcew_denominators_pic12_county_2023.csv');assert len(C)==len({(r['county_fips'],r['naics']) for r in C})==240
S=read(P/'qcew_denominators_by_state_2023.csv');assert len(S)==len({r['area_fips'] for r in S})==51
out={'frame_exact_match':True,'frame_pass_type_counts':passcounts,'excluded_allocation_classes':skip,'ledger_unique_trifids':len(L),'verdict_counts':dict(collections.Counter(r['verdict'] for r in ledger)),'ledger_class_counts':dict(collections.Counter(r['priority_class'] for r in ledger)),'ledger_creation_join_exact':True,'link_join_issues':issues,'resolved_links':resolved_links,'ledger_link_org_populated':sum(bool(r['link_org_id']) for r in ledger),'ledger_link_site_populated':sum(bool(r['link_site_id']) for r in ledger),'ledger_any_creation':sum(bool(r['created_org_ids'] or r['created_site_ids']) for r in ledger),'county_sources':dict(collections.Counter(r['source'] for r in C)),'county_blank_values':sum(not r['establishments'] for r in C),'county_codes':sorted({r['naics'] for r in C}),'source_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(P.iterdir()) if p.is_file()}}
Path('/tmp/f5-source-check.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2))
```

Full validator, SQLite build and all tests are rerun separately. Generated
build output is uncommitted. This packet closes reproducible source work but
keeps PIC-12 aggregate reconciliation and the seven link-outcome questions open.
Earlier reports remain historical; this dated source-backed result governs.
