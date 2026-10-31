# F5 final count reconciliation — 2026-10-31

**Result: the F5 documentation/count-reconciliation task is complete.** The new
source addendum settles both outstanding accounting questions. Six facilities
remain deliberately held by the integrator; completing F5 does not release those
holds, change any verdict, or certify comprehensive industry coverage. PR #10
remains draft for review/integration; nothing is merged.

## Explicit pins and scope

Metadata advanced from `884c2c0344b6d071406761ee39a203eac7e07d72` to
`e7ea638fa0ce0b3ef93d73ab4649a82fabb76df3`, observed 11:39 UTC on 2026-10-31.
Diff: packet README addendum plus county aggregates and seven-disposition CSVs.
Canonical data, schema and scripts are unchanged from the original data pin
`eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05`. AGENTS, unchanged schema and queue
were inspected in order. Existing F5 claim and all other queue entries preserved;
no silent rebase, canonical edits, new IDs, main pushes or merges.

The earlier source report independently rebuilt all 2,199 creation records and
checked the 1,797-TRIFID ledger. Those checks stand: the underlying inputs did
not change. This final note governs the two previously open questions and
supersedes earlier “still blocked” statements while retaining their history.

## PIC-12 official aggregate cells now reproducible

60 unique county×code cells, 12 named PIC-12 counties × 5 families, checked for
FIPS, year, field, status and source metadata. The banked BLS QCEW extract
specifies `own_code=5`, `qtr=A`, `size_code=0`, value `annual_avg_estabs`;
2023 annual county area URLs are recorded per row. Aggregate level is 75 for
326 and 76 for the four-digit families. Published values with disclosure code
N remain establishment values; unknown/no-row cells remain blank, never zero.
This reproduces the banked extract, not a fresh rerun of inaccessible live APIs.

| NAICS | Published counties | Sum of published establishment cells | Missing counties | Meaning |
|---|---:|---:|---|---|
| 326 | 12/12 | 367 | None | Complete PIC-12 aggregate |
| 3261 | 12/12 | 283 | None | Complete PIC-12 aggregate |
| 3262 | 12/12 | 84 | None | Complete PIC-12 aggregate |
| 3252 | 10/12 | 52 | Mahoning; Trumbull | Published-cell sum only, not complete PIC-12 denominator |
| 3259 | 10/12 | 62 | Ashtabula; Mahoning | Published-cell sum only, not complete PIC-12 denominator |

The old 62–63 ambiguity resolves to **62 as the sum of published 3259 cells**,
not a claim that the two unknown county cells are zero. No all-PIC-12 ratio is
computed against 52 or 62. Ashtabula is 39007 (not Ashland 39005); its 326 cell
is 21. The complete 326 sum is 367, superseding the erroneous historical 353.
The older mixed CBP/QCEW six-digit file is not substituted for these aggregates.

### Current numerator comparisons — not matched coverage

Unit: Atlas **site rows** in OH/PIC-12 recorded counties, own primary NAICS
prefix, status active/unknown. Primary = tiers A/B/C; recorded = any tier.
No parent-NAICS inheritance, site-type or ring restriction. Unknown status is
not active confirmation. Denominator unit: QCEW private annual-average
establishments, 2023. Atlas inventory is the 2026 pinned data. These incompatible
frames yield **count ratios, not facility-matched coverage, recall or completeness**.

| Geography / NAICS | Primary sites | Recorded sites | QCEW 2023 establishments | Primary count ratio | Recorded count ratio |
|---|---:|---:|---:|---:|---:|
| PIC-12 / 326 | 423 | 437 | 367 | 115.3% | 119.1% |
| PIC-12 / 3261 | 325 | 335 | 283 | 114.8% | 118.4% |
| PIC-12 / 3262 | 98 | 102 | 84 | 116.7% | 121.4% |
| OH / 326 | 815 | 988 | 890 | 91.6% | 111.0% |
| PA / 326 | 396 | 396 | 642 | 61.7% | 61.7% |

PIC-12 3252 numerator 41 primary / 46 recorded sites and 3259 numerator 49/56
remain standalone counts. The full OH/PA family comparison and disclosure
qualifiers are in `F5_SOURCE_RECONCILIATION_2026-10-31.md`. Ratios exceeding
100% reflect differing classification, site scope and vintage—not excess verified
coverage. The old pass-10 decomposition is not reused as a current explanation.

## Seven link cases reconciled — not missing facilities

The packet README now explicitly defines ledger `link_org_id`, `link_site_id`
and `link_match_basis` as **packet-proposed**, not applied outcomes. A lane
VERIFIED verdict and integration disposition are separate axes. The earlier F5
phrase “link-outcome discrepancies” described proposed-versus-canonical differences;
it must not imply seven missing facilities, accidental omissions, or bad canonical
records. The crosswalk supplies documented freeze dispositions for all seven.

| TRIFID | Disposition | Reconciliation |
|---|---|---|
| 77511QNTMC2MILE | Pass 21 §5 hold | Chocolate Bayou proposal held: licensed-source existence leg; public existence/address fact needed |
| 25401KRPLS2011M | Pass 21 §5 hold | MAAX Martinsburg proposal held: old licensed address/scope leg; public address/scope fact needed |
| 46563KRPLS1001N | Pass 21 §5 hold | MAAX Plymouth proposal held on same basis; public address/scope fact needed |
| 9176WPCFCR1671S | Pass 21 §5 hold | Elite Comfort Ontario proposal held: paid wrong-company citation; public operator/address or succession evidence needed |
| 5254WNHNCT299IN | Pass 22 liveness hold | Inhance Centerville absent from current footprint; no dated closure; continued operation or dated closure evidence needed |
| 92807XRXSC1210N | Pass 22 liveness hold | Xerxes Anaheim absent from current list; old brochure/RY2024 filing insufficient; dated current operation or closure evidence needed |
| 81503CLRDC56924 | Applied forward link, freeze correction | SITE-004546 already held under ORG-004005; packet ORG-003165 attribution was not applied |

Checks against canonical data and available pass allocations:
- Each of the six held TRIFIDs has no canonical TRI link, no created IDs in
  the ledger, and no site-creation allocation for its proposed design key in
  the relevant pass. That is consistent with an explicit hold, not a reject.
- Cray Valley's canonical pair is `(ORG-004005, 81503CLRDC56924)`; SITE-004546
  belongs to ORG-004005; the pass-23 `registry_link` allocation resolves that
  TRIFID to SITE-004546. The proposed ORG-003165 pair is absent, as intended.
- All seven remain VERIFIED in the research ledger. No status or verdict is
  changed by this accounting reconciliation; the six settling facts remain
  research holds owned by the integrator, outside this completed docs task.

Evidence limit: full pass journals are not published in this tree. Their freeze
rationale is supplied by the orchestrator's dated `ledger_link_dispositions.csv`,
not independently re-read from absent journals. The observable canonical and
allocation outcomes above agree with that crosswalk. F5 does not certify the
held proposals' facts or conduct new facility research to release them. A dated
closure signal does not automatically convert a hold into REJECT: any future
closure/no-establishment rejection still requires AGENTS' applicable dated
outcome standard and Form 5500 establishment-address check.

## Reproduction and checks

`F5_FINAL_RECONCILIATION_CHECKS_2026-10-31.json` contains exact aggregate sums,
unknown cells, per-disposition check results and SHA-256 hashes of the three
new/changed source files. Run the following read-only checker at source pin
e7ea638; output is the committed checks JSON. It asserts canonical nonmutation,
60 unique cells, all source filters, expected sums/missingness and all seven
crosswalk outcomes. Analysis output may be redirected to `/tmp`, never `data/`.

```python
import csv,json,hashlib,collections,subprocess
from pathlib import Path
pin='e7ea638fa0ce0b3ef93d73ab4649a82fabb76df3'
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==pin
assert not subprocess.check_output(['git','diff','eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05',pin,'--','data/','scripts/','docs/SCHEMA.md'])
P=Path('tasks/f5-source-packet')
def read(p):return list(csv.DictReader(p.open()))
a=read(P/'qcew_pic12_county_aggregates_2023.csv');assert len(a)==len({(r['county_fips'],r['naics']) for r in a})==60
fips=dict(Ashtabula='39007',Cuyahoga='39035',Geauga='39055',Lake='39085',Lorain='39093',Mahoning='39099',Medina='39103',Portage='39133',Stark='39151',Summit='39153',Trumbull='39155',Wayne='39169')
for r in a:
 assert fips[r['county_name']]==r['county_fips']
 assert r['source_vintage']=='QCEW 2023 annual averages'
 for part in ['BLS QCEW','/2023/a/area/'+r['county_fips']+'.csv','own_code=5','qtr=A','size_code=0','annual_avg_estabs']:assert part in r['source']
 if r['annual_avg_estabs']:
  assert r['value_status']=='published' and r['agglvl_code']==('75' if r['naics']=='326' else '76')
 else:assert r['value_status']=='not_published_no_row'
for county in fips:
 cells={r['naics']:r['annual_avg_estabs'] for r in a if r['county_name']==county}
 assert int(cells['326'])==int(cells['3261'])+int(cells['3262'])
sums={};missing={}
for code,n in [('326',367),('3261',283),('3262',84),('3252',52),('3259',62)]:
 rr=[r for r in a if r['naics']==code];assert len(rr)==12
 sums[code]=sum(int(r['annual_avg_estabs']) for r in rr if r['annual_avg_estabs']);assert sums[code]==n
 missing[code]=[r['county_name'] for r in rr if not r['annual_avg_estabs']]
assert missing=={'326':[],'3261':[],'3262':[],'3252':['Mahoning','Trumbull'],'3259':['Ashtabula','Mahoning']}
D=read(P/'ledger_link_dispositions.csv');assert len(D)==len({r['trifid'] for r in D})==7
L={r['trifid']:r for r in read(P/'tri_worklist_verdict_ledger.csv')}
R=read(Path('data/registry_links.csv'));links={(r['org_id'],r['registry_id']) for r in R if r['registry']=='TRI_TRIFID'}
S={r['site_id']:r for p in Path('data').glob('sites_*.csv') for r in read(p)}
O={r['org_id']:r for p in Path('data').glob('organizations_*.csv') for r in read(p)}
results=[]
for d in D:
 t=d['trifid'];l=L[t];assert l['verdict']=='VERIFIED' and l['link_org_id']==d['packet_proposed_org_id']
 assert not l['created_org_ids'] and not l['created_site_ids']
 if d['disposition'].startswith('HELD_AT_FREEZE'):
  assert not d['applied_org_id'] and not d['applied_site_id']
  assert not any(tf==t for oi,tf in links)
  p=21 if d['disposition']=='HELD_AT_FREEZE_S5_BAR' else 22
  alloc=read(P/f'frame_allocations_pass{p}.csv')
  assert not any(r['source_key']==l['link_site_id'] and r['class'] in ('site_create','create') for r in alloc)
  result='hold consistent: no canonical TRI link, no site-creation allocation'
 else:
  assert d['disposition']=='APPLIED_AS_FORWARD_LINK_FREEZE_CORRECTION'
  assert d['applied_org_id'] in O and S[d['applied_site_id']]['org_id']==d['applied_org_id']
  assert (d['applied_org_id'],t) in links and (d['packet_proposed_org_id'],t) not in links
  alloc=read(P/'frame_allocations_pass23.csv')
  assert any(r['class']=='registry_link' and r['source_key']==t and r['resolves_to']==d['applied_site_id'] for r in alloc)
  result='applied forward link matches canonical operator and pass-23 allocation'
 results.append({'trifid':t,'disposition':d['disposition'],'result':result})
out={'source_pin':pin,'data_pin':'eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05','unique_aggregate_cells':60,'published_cell_sums':sums,'unknown_counties_by_code':missing,'disposition_counts':dict(collections.Counter(r['disposition'] for r in D)),'disposition_checks':results,'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [P/'README.md',P/'qcew_pic12_county_aggregates_2023.csv',P/'ledger_link_dispositions.csv']}}
print(json.dumps(out,indent=2,sort_keys=True))
```

Full repository validator, SQLite build and 37 tests rerun on both the final
source checkout and F5 docs tree; generated build files stay uncommitted.
No schema text was edited. Earlier schema birth/dormant-TRI wording clarification
remains a separately versioned documentation consideration, not an F5 data change.
The F5 deliverable is a reconciled, reproducible draft packet—not merge approval.
