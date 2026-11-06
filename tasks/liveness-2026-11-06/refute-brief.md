Adversarial completion review, deep. Inspect tasks/liveness-2026-11-06 in this worktree. Attempt to REFUTE technical packet correctness and compliance. End APPROVE or REFUTE; distinguish verified defects from uninspected material. This is a bounded initial liveness pass, not a claim all queued organizations are resolved.

Deliverables: unchanged existing full liveness sweep; separate federal_signals.py aggregates exact restored registry keys into newest TRI reporting year through EPA DMAP; held Form 5500 newest plan years by EIN; build.py makes one ranked row per active/unknown organization+ecosystem row; compare.py compares prior/full and common-domain observations. README describes scoring, source coverage, top-ranked investigations and remaining holds. Zero data changes unless explicitly described in README. Registry input from pinned d264380 PR129; no registry writes.

Run python3 tasks/liveness-2026-11-06/check.py and python3 scripts/validate.py. Existing python3 -m unittest scripts/test_liveness_sweep.py passed 26. No scripts/ code changed. Raw TRI known answers reconcile independent REST COUNT and all form rows (99/8/180), max year 2024, versus grouped new fetcher. 2153 TRI link rows, 2150 distinct keys, all returned. Filing/website failures are never closure evidence. No absent coverage treated as stale.

Look for silent skips/truncation, false key matches, missing orgs/duplicate rows, misleading common-domain comparison, privacy, unsupported status/ownership changes, flawed scoring, untested new logic, rerun instability. Remaining queue is explicitly held for future dated research; do not equate remaining scope with data correctness. New scripts live only in task folder.

Round 2: Codex round1 REFUTE reproduced gate defects; Grok round1 APPROVE with hardening. See final inline README dispositions. New checks reject all 4 injected output/input defects; entire-PR data gate rejects committed mutation. New website-change branch has 2-case isolated builder test. Review final changes, not stale round1 code. End APPROVE/REFUTE.

## Inline evidence (local filesystem access not required)

### README.md
```
# L8 liveness sweep — 2026-11-06

Owner: atlas-L8-liveness. Branch: agent/codex/liveness-sweep-2. Claimed by controller; QUEUE untouched.
First user: Atlas campaign integrator, on delivery of this PR; non-use finding date: 2026-11-13.

Acceptance criteria: full eligible-domain sweep; ranked organization queue with exact EIN/TRIFID joins and explicit missing/failed coverage; compare November 1 sweep on both full and common-domain frames; no status mutation without dated primary/near-primary evidence and raw-checked quote; validate.py zero errors. Acquirer identity/grain questions stay held. No registry or derived-field edits.

Registry input pinned to restore branch commit d26438057e4e0199a2407d2a9508238494f31deb (PR #129). Snapshot is an input only, never applied to data/.

Methods and decisions (append-only journal):
- Sweep uses the existing script unchanged: active/unknown organizations plus ecosystem, excludes missing/invalid/shared-platform websites and groups shared normalized domains. It does not inspect acquired/closed rows.
- Rank score is triage only: NXDOMAIN 30, parked 25, cross-domain redirect 20; all matched EIN years older than 2024 adds 10; any latest-year all-final/short sponsor flag adds 10; all matched TRI years older than 2024 adds 5. Missing keys contribute zero, not a negative activity inference. Ties sort by org_id. Every active/unknown row remains in signals.csv, even score zero or NOT_SWEPT.
- EIN years are newest plan years in the held November 1 spine, not fresh DOL searches. No sponsor-address equivalence is assumed. All EIN links, including unmatched ones, remain in federal_link_signals.csv.
- TRI years fetched 2026-11-06 through EPA DMAP, grouped by exact held TRIFID, max(reporting_year) across historical reporting forms. Query selects no personal fields. 2,153 restored TRI link rows represent 2,150 distinct facility keys; repeated keys are not dropped at link grain. No TRI parent name is used.
- Source documentation: https://www.epa.gov/enviro/dmap-graphql-api ; https://www.epa.gov/toxics-release-inventory-tri-program/reporting-tri-facilities . TRI reporting depends on activity and thresholds; ceasing reporting does not establish closure.
- Known answers: independent legacy REST COUNT + complete forms reconciled 99, 8, 180 input forms for TRIFIDs 44224STRKT201ES, 4430WLTRRN12EWA, 44305RPBLC60SOU; all newest years = 2024. Only counts/year retained, no contact fields. EIN known keys 631127539=2024, 881282156=2025, 341352998=2023 checked in held spine. Exact-key matcher does not perform name inference.
- Estate search on Mac returned partial coverage (Documents inventory / wiki / RAG missing); this does not establish absence. TRI registry route was held and successfully queried; no missing estate source was needed.
- pytest is absent from base Python; scripts/ is unchanged. Existing sweep unittest suite passed 26 tests. No dependency added.
- Cross-thread lead from L9 (thr_t3bqpsncvw): ORG-000451 Molded Fiber Glass Companies newsroom https://moldedfiberglass.com/category/company-news/ reportedly HTTP 200, latest listed actual item 2023-10-26. This is L9's observation, not independently verified here, and not closure evidence (AGENTS §3). Keep as supplemental re-verification lead; do not change queue rank from a sibling-only observation.

## Results

- Input: 4,945 organization rows plus 400 ecosystem rows. Ranked frame: 5,288 active/unknown organization+ecosystem rows, exactly one per org_id; 154 have score > 0. No row is silently discarded for missing website/federal link.
- Full eligible-domain sweep: 4,327 unique normalized domains; 31 NXDOMAIN + 3 parked = 34 dead/parked **domain observations**, not closures. November 1: 3,629 domains; 24 NXDOMAIN + 3 parked = 27. Shared frame: 3,594 domains; prior 27 vs current 32 combined observations (24→29 NXDOMAIN, 3→3 parked). There are 733 newly eligible domains and 35 no longer eligible; route and website corrections can change observations. `comparison.csv` exposes every transition.
- All 2,150 distinct TRI keys returned 2024, so no TRI-staleness score was added. All 320 EIN links matched the held spine. Federal link output: 2,473 rows (2,153 TRI + 320 EIN).
- Applied data rows: **0**, evidence rows: **0**, status changes: **0**; verification tiers unchanged (A/B/C/U: 0 each). No EVD ids consumed. No inclusion-log entries or relationships required.

## Initial top-down review and holds

This pass investigates the first **10 ranked organization rows**. The remaining **144 positive-priority rows** are uninvestigated, explicitly held for the next dated-evidence pass. No claim of a completed queue-wide closure census is made. `verdicts.csv` names the settling facts; raw observations are in `rawcheck.csv`. Search snippets are discovery only. No dated closure witness was found for these ten; no organization is rejected for closure. Every domain failure stays a signal under AGENTS §3.

| Rank / organization | Verdict | Hold / recommended reading and settling fact |
|---|---|---|
| 1 ORG-002133 Vinyl Tool & Die | STILL_UNCERTAIN | EIN 341570514 newest PY2024, latest all-final/short flag. This is plan wind-down only. Need dated company/outcome record at Youngstown establishment; directory “closed now” is business hours, not closure. |
| 2 ORG-002712 Fay L Wagner | STILL_UNCERTAIN | EIN 251290948 newest PY2025, final/short flag. TIPS public dealer list is a counter-lead, not operating proof; need dated establishment outcome or current company statement. |
| 3 ORG-000422 Littlern | STILL_UNCERTAIN | Historical own-site description cannot establish current activity when domain fails. Need dated operating or cessation witness at Barberton. |
| 4 ORG-000443 Midlands Technologies | STILL_UNCERTAIN | Read own contact page at midlands-technologies.com; stored midlandstech.com was already flagged as wrong in record notes. Need identity/address confirmation before website correction; the 2026 court case being “Closed” does not mean company closure. No scope self-ruling. |
| 5 ORG-000654 Advanced Technology Products | STILL_UNCERTAIN | Own about page indexed at www.atp4pneumatics.com; domain-level DNS observation differs from indexed route. Need raw accessible current operating witness; no closure inference. |
| 6 ORG-000960 Midwest Plastics | STILL_UNCERTAIN | Lima domain fails; similarly named midwestplastics.com is not established to be same entity. Need dated Lima establishment witness. |
| 7 ORG-001427 KN Rubber | STILL_UNCERTAIN | Indexed about/fact sheet describe Koneta/National Rubber combination but no dated transaction/outcome is established. Need current operator and dated ownership chain; HOLD grain question, do not infer successor. |
| 8 ORG-001685 Kittyhawk Molding | STILL_UNCERTAIN | Chemstar's own about page names Kittyhawk as parent manufacturer, a counter-lead to dead domain. Need independently current operator/identity witness; no closure. |
| 9 ORG-001719 Pyramid Plastics | STILL_UNCERTAIN | Atlas row is Cleveland; pyramidplastics.com describes Rockford IL. HOLD identity; never apply Rockford acquisition/parent facts to Cleveland from name alone. Need Cleveland primary witness. |
| 10 ORG-001729 ICU Medical | STILL_UNCERTAIN | ICU announcement dated 2022-01-06 covers acquisition of Smiths Medical; held record already named ICU Medical, but old Smiths domain. HOLD record grain/identity before any acquisition tombstone. Acquirer buying a business does not mean acquirer was acquired. |

## Reproduce and checks

```sh
python3 scripts/liveness_sweep.py --out tasks/liveness-2026-11-06/sweep  # new network observation
python3 tasks/liveness-2026-11-06/federal_signals.py  # cached TRI batches; remove/review cache only for a new dated run
python3 tasks/liveness-2026-11-06/build.py
python3 tasks/liveness-2026-11-06/compare.py
python3 tasks/liveness-2026-11-06/check.py
python3 scripts/validate.py
python3 -m unittest scripts/test_liveness_sweep.py
```

`build.py` is idempotent and writes task packets only; on rebase rerun it against fresh main. Historical sweep/registry/federal inputs remain frozen for this dated comparison. Base data is branch history (bd57a08); there is no data application. No new abstraction or dependency, no status inference, no website repair outside lane scope.

Raw follow-up outcome: 2 of 10 business snippets passed direct curl word checks (Midlands contact; Chemstar about). The other 8 failed both direct and fallback availability or could not return a usable page. No snippet from those eight is used as evidence; search-indexed descriptions above are explicitly counter-leads/identity cautions. No acquisition or closure is applied. The top two Form 5500 sponsor addresses were checked in the held spine: 1144 Meadowbrook Avenue, Youngstown and 500 North Main Street, Yeagertown. They do not resolve cessation. Each case used at most two primary raw fetch attempts plus indexed discovery.

Offline checks run: `check.py` PASS (2,150 TRI keys, 3 independent TRI known answers, 3 EIN known answers, 5,288 unique ranked rows, score boundaries, zero data mutation); `validate.py` PASS 0 errors; existing sweep unittest PASS 26 tests. Scripts/ unchanged; full scripts pytest not required.

Additional deterministic checks: queue coverage equals the independent set of active/unknown input IDs; an injected duplicate was rejected by the uniqueness gate. Queue/federal/comparison rebuilds were SHA-256 byte-identical. `test_research.py`: 5 tests passed (known-good words, absent quote, curl failure with body, HTTP failure, empty quote). Data mutation remains forbidden by `check.py` for this signal-only packet.

Lead check refinement during review: zero-data-change assertion now compares the entire PR against `merge-base(HEAD, origin/main)`, including committed edits, rather than only the working tree against HEAD. It passes; this strengthens the signal-only packet gate without changing any output or data.
Whole-PR mutation-gate known defect test: in an isolated temporary git repository, committed an injected `active`→`closed` CSV change after the simulated origin/main base; the identical merge-base/diff command returned 1 and rejected it. The Atlas data tree was never edited.

## Cross-family refute

Grok, grok-4.7 xhigh (`--effort deep`): **APPROVE** for the explicitly bounded packet. Useful hardening adopted: check all 2,150 TRI keys are found/year 2024, all 320 EIN link hits and 2,473 link rows, recompute every queue score, pin registry snapshot SHA-256 (b830d047d4bedc576b7628cf0bbdebf685a6288cb2ed4d2ddbf1700d9e741953; separately byte-compared to d264380), and reject duplicate sponsor EIN input rows. The whole-PR data gate was already strengthened during the review. These checks pass. Grok inspected inline code/journal/rawcheck/verdicts, not the full CSVs or live sources; the deterministic checks supply population ground truth.

Other observations held as limits, not hidden: error/empty TRI query batches are explicitly marked and cached, but the frozen-run check now rejects them; a new dated fetch must refresh/review its caches. No empirical pre-aggregation truncation was demonstrated: documented query selects grouped maxima with 10,000 output limit for 100 keys, all 100 keys per batch reconciled, with three independent full-form max-year comparisons. The legacy REST row counts (99/8/180) are observation receipts, not an offline re-fetch. HTTP-200 interstitials without the requested quote return no match and may need manual alternate routes; no data change is supported by that checker. Business sponsor addresses and public reseller RecordID are public business data, not private identifiers or personal contact data.

Codex round 1, GPT-6 Astra max (`--effort deep`): **REFUTE** — reproduced committed status changes escaping HEAD-only comparison, all-zero scores passing, missing federal/comparison outputs passing, and a failed non-control TRI key passing. All addressed: merge-base + untracked-data check, full source/link-multiset/field reconciliation, explicit all-key year/coverage assertions, every comparison transition checked, researched top-ten alignment checked. Injected all-zero scores, dropped federal/comparison rows, and a TimeoutError TRI key now each fail `check.py`; original files restored after each test. No CSV output content was repaired silently by the checker.

Codex also identified a rerun risk after website edits: builder now records current_website and sweep_domain separately; a changed normalized hostname yields WEBSITE_CHANGED_SINCE_SWEEP (no old-domain liveness points, no stale redirect URL). The raw historical observation remains in sweep/. `test_build.py` passes two cases (same domain retains NXDOMAIN score; changed domain clears it). Queue population and priority counts are unchanged on this tree. This is a task-local signal label, never a schema value or data mutation. A rebase that changes the researched top ten fails the gate and requires renewed research.
```

### federal_signals.py
```
"""Exact registry-key joins; federal years are signals only, never closure evidence."""
import csv
import json
from pathlib import Path
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
API = 'https://data.epa.gov/dmapservice/query'

def read(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def write(path, rows, fields):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)

def query_years(ids):
    q = ('query { tri__tri_reporting_form (limit: 10000, groupBy: ["tri_facility_id"], '
         'where: {tri_facility_id: {in: ' + json.dumps(ids) + '}}) '
         '{ tri_facility_id fn__max(parameters: ["reporting_year"], alias: "latest_year") } }')
    req = urllib.request.Request(API, data=json.dumps({'query': q}).encode(),
                                 headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=180) as f:
        data = json.load(f)
    assert data.get('status') == 'COMPLETED', data
    rows = data['data']['tri__tri_reporting_form']
    assert len(rows) < 10000
    assert len({r['tri_facility_id'] for r in rows}) == len(rows)
    assert all(r['tri_facility_id'] in ids for r in rows)
    return rows

def fetch():
    ids = sorted({r['registry_id'] for r in read(HERE / 'registry_links_snapshot.csv') if r['registry'] == 'TRI_TRIFID'})
    rows = []
    for start in range(0, len(ids), 100):
        batch = ids[start:start+100]
        cache = HERE / 'tri_batches' / f'{start:04}.json'
        cache.parent.mkdir(exist_ok=True)
        if cache.exists():
            result = json.loads(cache.read_text())
        else:
            try:
                found = {r['tri_facility_id']: r['latest_year'] for r in query_years(batch)}
                result = [dict(trifid=i, latest_year=found.get(i, ''), coverage='found' if i in found else 'no_return') for i in batch]
            except Exception as exc:
                result = [dict(trifid=i, latest_year='', coverage=type(exc).__name__) for i in batch]
            cache.write_text(json.dumps(result, indent=2)+'\n')
        assert {r['trifid'] for r in result} == set(batch)
        rows.extend(result)
        print(start+len(batch), '/', len(ids), flush=True)
    assert len(rows) == len(ids) == len({r['trifid'] for r in rows})
    write(HERE / 'tri_years.csv', rows, ['trifid','latest_year','coverage'])

if __name__ == '__main__':
    fetch()
```

### build.py
```
"""Rebuild the ranked queue from frozen sweep and exact federal-key inputs; no data writes."""
from collections import defaultdict
import sys
from federal_signals import HERE, ROOT, read, write
sys.path.insert(0, str(ROOT/"scripts"))
from liveness_sweep import normalize_website


def score(signal, years, final, tri):
    return ({'NXDOMAIN':30,'PARKED_SUSPECT':25,'REDIRECT_CROSS_DOMAIN':20}.get(signal,0)
            + (10 if years and max(years)<2024 else 0) + (10 if final else 0)
            + (5 if tri and max(tri)<2024 else 0))


def main():
    orgs = [r for p in sorted((ROOT/'data').glob('organizations_*.csv')) for r in read(p)] + read(ROOT/'data/ecosystem.csv')
    assert len({r['org_id'] for r in orgs}) == len(orgs)
    sponsor_rows=read(ROOT/'tasks/form5500-spine-2026-11-01/sponsors.csv')
    sponsors = {r['ein']:r for r in sponsor_rows}
    assert len(sponsors)==len(sponsor_rows)
    tri = {r['trifid']:r for r in read(HERE/'tri_years.csv')}
    link_rows=[]
    links = defaultdict(list)
    for r in read(HERE/'registry_links_snapshot.csv'):
        if r['registry'] in ('EIN','TRI_TRIFID'):
            links[r['org_id']].append(r)
            key=r['registry_id']
            if r['registry']=='EIN':
                year=sponsors.get(key,{}).get('latest_filed_plan_year_any','')
                coverage='found' if year else 'NOT_IN_SPINE'
            else:
                year=tri[key]['latest_year']; coverage=tri[key]['coverage']
            link_rows.append(dict(org_id=r['org_id'],site_id=r['site_id'],registry=r['registry'],registry_id=key,latest_year=year,coverage=coverage))
    write(HERE/'federal_link_signals.csv',link_rows,list(link_rows[0]))
    sweep = {}
    for r in read(HERE/'sweep/signals.csv'):
        for oid in r['org_id'].split(';'):
            assert oid not in sweep
            sweep[oid] = r
    rows=[]
    for o in orgs:
        if o['status'] not in ('active','unknown'):
            continue
        oid=o['org_id']; f=[]; t=[]
        for link in links[oid]:
            key=link['registry_id']
            if link['registry']=='EIN':
                r=sponsors.get(key,{})
                f.append((key,r.get('latest_filed_plan_year_any',''),r.get('latest_py_all_final_or_short','')))
            else:
                r=tri[key]
                t.append((key,r['latest_year'],r['coverage']))
        sy=[int(y) for _,y,_ in f if y]; ty=[int(y) for _,y,_ in t if y]
        final=any(v=='1' for _,_,v in f)
        s=sweep.get(oid,{})
        current_domain,_=normalize_website(o['website'])
        changed=bool(s and current_domain!=s['domain'])
        signal='WEBSITE_CHANGED_SINCE_SWEEP' if changed else s.get('signal_class','NOT_SWEPT')
        rows.append(dict(rank='',score=score(signal,sy,final,ty),org_id=oid,legal_name=o['legal_name'],
                         domain=current_domain or '',current_website=o['website'],sweep_domain=s.get('domain',''),signal_class=signal,final_url='' if changed else s.get('final_url',''),
                         ein_years=';'.join(k+':'+(y or 'NOT_IN_SPINE') for k,y,_ in f),
                         form5500_latest_year=max(sy) if sy else '',form5500_final_or_short=int(final),
                         trifid_years=';'.join(k+':'+(y or cov) for k,y,cov in t),
                         tri_latest_year=max(ty) if ty else '',tri_unresolved=sum(not y for _,y,_ in t),
                         federal_note='Signal only; sponsor address not assumed to equal establishment; no link is unknown coverage'))
    rows.sort(key=lambda r:(-r['score'],r['org_id']))
    for n,r in enumerate(rows,1): r['rank']=n
    assert len(rows)==len({r['org_id'] for r in rows})
    write(HERE/'signals.csv',rows,list(rows[0]))
    print('active/unknown organization+ecosystem rows:',len(rows),'positive priority:',sum(r['score']>0 for r in rows))

if __name__=='__main__': main()
```

### check.py
```
"""Named offline check: score boundaries, federal coverage, unique queue and dated-status gate."""
import json
from build import score
from federal_signals import HERE, ROOT, read

assert score('NXDOMAIN',[],False,[])==30
assert score('PARKED_SUSPECT',[2023],True,[2020])==50
assert score('BOT_WALL_SUSPECT',[],False,[])==0
assert score('OK',[2024],False,[2024])==0
assert score('OK',[2023,2025],False,[2010,2024])==0
links=read(HERE/'registry_links_snapshot.csv')
tri=read(HERE/'tri_years.csv')
assert len(tri)==len({r['trifid'] for r in tri})
assert {r['trifid'] for r in tri}=={r['registry_id'] for r in links if r['registry']=='TRI_TRIFID'}
actual={r['trifid']:r['latest_year'] for r in tri}
for r in json.loads((HERE/'known_answers.json').read_text()):
    assert int(actual[r['trifid']])==r['expected_year']
rows=read(HERE/'signals.csv')
def unique(records):
    assert len(records)==len({r['org_id'] for r in records})
unique(rows)
try:
    unique(rows+[rows[0]])
except AssertionError:
    pass
else:
    raise AssertionError('injected duplicate escaped uniqueness gate')
expected=[r for p in sorted((ROOT/'data').glob('organizations_*.csv')) for r in read(p)] + read(ROOT/'data/ecosystem.csv')
assert {r['org_id'] for r in rows} == {r['org_id'] for r in expected if r['status'] in ('active','unknown')}

assert [int(r['rank']) for r in rows]==list(range(1,len(rows)+1))
assert [int(r['score']) for r in rows]==sorted([int(r['score']) for r in rows],reverse=True)
print(f'PASS: {len(tri)} distinct TRI keys accounted; 3 independent known answers; {len(rows)} unique ranked rows; score boundaries')

sponsors={r['ein']:r for r in read(ROOT/'tasks/form5500-spine-2026-11-01/sponsors.csv')}
for key,year in [('631127539','2024'),('881282156','2025'),('341352998','2023')]:
    assert sponsors[key]['latest_filed_plan_year_any']==year
print('PASS: 3 Form 5500 known-key years (2024 / 2025 / 2023)')
import subprocess
# This packet applies zero mutations; any data edit requires a new dated-evidence application contract.
base=subprocess.check_output(['git','merge-base','HEAD','origin/main'],cwd=ROOT,text=True).strip()
subprocess.run(['git','diff','--exit-code',base,'--','data/'],cwd=ROOT,check=True,stdout=subprocess.PIPE)
print('PASS: zero data/status changes; dated-status evidence gate has no applied cases')

assert len(tri)==2150 and all(r['coverage']=='found' and r['latest_year']=='2024' for r in tri)
federal=read(HERE/'federal_link_signals.csv')
assert len(federal)==2473
assert sum(r['registry']=='EIN' and r['coverage']=='found' for r in federal)==320
assert all(r['coverage']=='found' for r in federal)
import hashlib
assert hashlib.sha256((HERE/'registry_links_snapshot.csv').read_bytes()).hexdigest()=='b830d047d4bedc576b7628cf0bbdebf685a6288cb2ed4d2ddbf1700d9e741953'
for r in rows:
    sy=[int(item.rsplit(':',1)[1]) for item in r['ein_years'].split(';') if item and item.rsplit(':',1)[1].isdigit()]
    ty=[int(item.rsplit(':',1)[1]) for item in r['trifid_years'].split(';') if item and item.rsplit(':',1)[1].isdigit()]
    assert int(r['score'])==score(r['signal_class'],sy,r['form5500_final_or_short']=='1',ty)
print('PASS: frozen-run all-key coverage/year claims; pinned snapshot; every queue score recomputed')

assert not subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','data/'],cwd=ROOT,text=True).strip(), 'untracked data files'
from collections import Counter, defaultdict
from build import normalize_website
by_org=defaultdict(list)
expected_links=[]
for link in links:
    if link['registry'] not in ('EIN','TRI_TRIFID'): continue
    by_org[link['org_id']].append(link)
    key=link['registry_id']
    if link['registry']=='EIN':
        year=sponsors.get(key,{}).get('latest_filed_plan_year_any','')
        coverage='found' if year else 'NOT_IN_SPINE'
    else:
        item=next(r for r in tri if r['trifid']==key)
        year=item['latest_year'];coverage=item['coverage']
    expected_links.append(dict(org_id=link['org_id'],site_id=link['site_id'],registry=link['registry'],registry_id=key,latest_year=year,coverage=coverage))
assert Counter(tuple(sorted(r.items())) for r in federal)==Counter(tuple(sorted(r.items())) for r in expected_links)
orgs={r['org_id']:r for r in expected}
sweep={oid:r for r in read(HERE/'sweep/signals.csv') for oid in r['org_id'].split(';')}
tri_index={r['trifid']:r for r in tri}
for r in rows:
    oid=r['org_id']; f=[];t=[]
    for link in by_org[oid]:
        key=link['registry_id']
        if link['registry']=='EIN':
            item=sponsors.get(key,{})
            f.append((key,item.get('latest_filed_plan_year_any',''),item.get('latest_py_all_final_or_short','')))
        else:
            item=tri_index[key];t.append((key,item['latest_year'],item['coverage']))
    assert r['ein_years']==';'.join(k+':'+(y or 'NOT_IN_SPINE') for k,y,_ in f)
    assert r['trifid_years']==';'.join(k+':'+(y or cov) for k,y,cov in t)
    assert r['form5500_final_or_short']==str(int(any(v=='1' for _,_,v in f)))
    fy=[int(y) for _,y,_ in f if y];ty=[int(y) for _,y,_ in t if y]
    assert r['form5500_latest_year']==(str(max(fy)) if fy else '')
    assert r['tri_latest_year']==(str(max(ty)) if ty else '')
    assert r['tri_unresolved']==str(sum(not y for _,y,_ in t))
    assert r['current_website']==orgs[oid]['website'] and r['legal_name']==orgs[oid]['legal_name']
    domain,_=normalize_website(orgs[oid]['website']); obs=sweep.get(oid,{})
    changed=bool(obs and domain!=obs['domain'])
    assert r['domain']==(domain or '') and r['sweep_domain']==obs.get('domain','')
    assert r['signal_class']==('WEBSITE_CHANGED_SINCE_SWEEP' if changed else obs.get('signal_class','NOT_SWEPT'))
    assert r['final_url']==('' if changed else obs.get('final_url',''))
old={r['domain']:r for r in read(ROOT/'tasks/liveness-sweep-2026-11-01/signals.csv')}
new={r['domain']:r for r in read(HERE/'sweep/signals.csv')}
comparison=read(HERE/'comparison.csv')
assert len(comparison)==len({r['domain'] for r in comparison})==len(old.keys()|new.keys())
for r in comparison:
    assert r['previous']==old.get(r['domain'],{}).get('signal_class','NOT_IN_FRAME')
    assert r['current']==new.get(r['domain'],{}).get('signal_class','NOT_IN_FRAME')
assert {r['domain'] for r in comparison}==old.keys()|new.keys()
from research import CASES
assert [r['org_id'] for r in rows[:10]]==[r['org_id'] for r in read(HERE/'verdicts.csv')]==[r[0] for r in CASES]
print('PASS: full federal-link multiset; source field joins; every comparison transition; current websites; research top-ten alignment; no untracked data')
```

### compare.py
```
"""Compare observed DNS/parking signals, not business closures."""
from collections import Counter
from federal_signals import HERE, ROOT, read, write
old={r['domain']:r for r in read(ROOT/'tasks/liveness-sweep-2026-11-01/signals.csv')}
new={r['domain']:r for r in read(HERE/'sweep/signals.csv')}
assert len(old)==len(read(ROOT/'tasks/liveness-sweep-2026-11-01/signals.csv'))
assert len(new)==len(read(HERE/'sweep/signals.csv'))
common=old.keys() & new.keys()
rows=[dict(domain=d,previous=old.get(d,{}).get('signal_class','NOT_IN_FRAME'),current=new.get(d,{}).get('signal_class','NOT_IN_FRAME')) for d in sorted(old.keys()|new.keys())]
write(HERE/'comparison.csv',rows,['domain','previous','current'])
print('Unit: unique normalized eligible domains (not business closures).')
for label, domains in [('previous_full',old),('current_full',new),('common_previous',{d:old[d] for d in common}),('common_current',{d:new[d] for d in common})]:
    c=Counter(r['signal_class'] for r in domains.values())
    print(label,len(domains),'NXDOMAIN',c['NXDOMAIN'],'PARKED_SUSPECT',c['PARKED_SUSPECT'],'combined',c['NXDOMAIN']+c['PARKED_SUSPECT'])
print('new frame',len(new.keys()-old.keys()),'left frame',len(old.keys()-new.keys()))
```

### research.py
```
"""Raw curl observations for the first ten queue rows; retain only business snippets."""
import concurrent.futures
import html
import re
import subprocess
from federal_signals import HERE, read, write

CASES = [
('ORG-002133','https://vinyltoolanddie.com/',''),
('ORG-002712','https://www.tips-usa.com/resellers.cfm?RecordID=29C87E9F11A4DB5AA6A5C96614A47A74','FAY L WAGNER'),
('ORG-000422','https://www.littlern.com/index.html','Littlern Corporation'),
('ORG-000443','https://www.midlands-technologies.com/contact','1911 36th St NE'),
('ORG-000654','https://www.atp4pneumatics.com/about-us/','Advanced Technology Products'),
('ORG-000960','https://www.midwestplasticsoh.com/contactus.html',''),
('ORG-001427','https://www.knrubber.com/about.html','KN Rubber LLC'),
('ORG-001685','https://chemstar.direct/about/','Kittyhawk Molding'),
('ORG-001719','https://pyramidplastics.com/about/','Rockford'),
('ORG-001729','https://ir.icumed.com/news-releases/news-release-details/icu-medical-completes-acquisition-smiths-medical-smiths-group','January 6, 2022'),
]

def fetch(case):
    oid,url,quote=case
    for route in [url,'https://r.jina.ai/'+url]:
        proc=subprocess.run(['curl','-L','-sS','--max-time','25','-A','Mozilla/5.0','-w','\n%{http_code}',route],capture_output=True,text=True)
        body,_,status=proc.stdout.rpartition('\n')
        text=re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]*>',' ',body)))
        if proc.returncode==0 and status=='200':
            matched=bool(quote and quote.lower() in text.lower())
            return dict(org_id=oid,url=url,route=route,http=status,quote=quote,raw='yes' if matched else 'no',note='Raw page words checked; not a dated closure witness')
    return dict(org_id=oid,url=url,route=route,http=status,quote='',raw='unfetchable',note='Availability only; no closure inference')

if __name__=='__main__':
    assert [r['org_id'] for r in read(HERE/'signals.csv')[:10]]==[r[0] for r in CASES]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        rows=list(pool.map(fetch,CASES))
    write(HERE/'rawcheck.csv',rows,list(rows[0]))
    print([(r['org_id'],r['http'],r['raw']) for r in rows])
```

### test_research.py
```
"""Known curl result checks: never mistake a failed/empty route for evidence."""
import unittest
from unittest.mock import patch
from subprocess import CompletedProcess
from research import fetch

class RawCheckTests(unittest.TestCase):
    def result(self,stdout,code=0):
        return CompletedProcess([],code,stdout=stdout,stderr='')

    @patch('research.subprocess.run')
    def test_known_good_words(self,run):
        run.return_value=self.result('<p>Kittyhawk Molding</p>\n200')
        self.assertEqual(fetch(('ORG-X','https://example.com','Kittyhawk Molding'))['raw'],'yes')

    @patch('research.subprocess.run')
    def test_missing_quote(self,run):
        run.return_value=self.result('<p>Other business</p>\n200')
        self.assertEqual(fetch(('ORG-X','https://example.com','Kittyhawk Molding'))['raw'],'no')

    @patch('research.subprocess.run')
    def test_failed_curl_with_body(self,run):
        run.return_value=self.result('Kittyhawk Molding\n200',28)
        self.assertEqual(fetch(('ORG-X','https://example.com','Kittyhawk Molding'))['raw'],'unfetchable')

    @patch('research.subprocess.run')
    def test_http_failure(self,run):
        run.return_value=self.result('Kittyhawk Molding\n403')
        self.assertEqual(fetch(('ORG-X','https://example.com','Kittyhawk Molding'))['raw'],'unfetchable')

    @patch('research.subprocess.run')
    def test_empty_quote_never_passes(self,run):
        run.return_value=self.result('<p>hello</p>\n200')
        self.assertEqual(fetch(('ORG-X','https://example.com',''))['raw'],'no')

if __name__=='__main__': unittest.main()
```

### test_build.py
```
"""Rebase website changes must not inherit old-domain liveness scores."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import build
from federal_signals import read, write

class WebsiteRerunTests(unittest.TestCase):
    def test_changed_and_unchanged_domains(self):
        for website,signal,score in [('https://old.example.com/','NXDOMAIN','30'),('https://new.example.com/','WEBSITE_CHANGED_SINCE_SWEEP','0')]:
            with self.subTest(website=website), tempfile.TemporaryDirectory() as d:
                root=Path(d); task=root/'tasks/liveness'; (root/'data').mkdir(); (task/'sweep').mkdir(parents=True)
                sponsor=root/'tasks/form5500-spine-2026-11-01'; sponsor.mkdir()
                write(root/'data/organizations_OH.csv',[dict(org_id='ORG-TEST',legal_name='Test',status='active',website=website)],['org_id','legal_name','status','website'])
                write(root/'data/ecosystem.csv',[],['org_id','legal_name','status','website'])
                write(sponsor/'sponsors.csv',[dict(ein='123456789',latest_filed_plan_year_any='2024',latest_py_all_final_or_short='0')],['ein','latest_filed_plan_year_any','latest_py_all_final_or_short'])
                write(task/'registry_links_snapshot.csv',[dict(org_id='ORG-TEST',site_id='',registry='EIN',registry_id='123456789')],['org_id','site_id','registry','registry_id'])
                write(task/'tri_years.csv',[],['trifid','latest_year','coverage'])
                write(task/'sweep/signals.csv',[dict(org_id='ORG-TEST',domain='old.example.com',signal_class='NXDOMAIN',final_url='')],['org_id','domain','signal_class','final_url'])
                with patch.multiple(build,HERE=task,ROOT=root),contextlib.redirect_stdout(io.StringIO()): build.main()
                row=read(task/'signals.csv')[0]
                self.assertEqual((row['signal_class'],row['score']),(signal,score))
                self.assertEqual(row['sweep_domain'],'old.example.com')
                self.assertEqual(row['current_website'],website)

if __name__=='__main__': unittest.main()
```

### known_answers.json
```
[
  {
    "trifid": "44224STRKT201ES",
    "expected_year": 2024,
    "rows": 99
  },
  {
    "trifid": "4430WLTRRN12EWA",
    "expected_year": 2024,
    "rows": 8
  },
  {
    "trifid": "44305RPBLC60SOU",
    "expected_year": 2024,
    "rows": 180
  }
]
```

### rawcheck.csv
```
org_id,url,route,http,quote,raw,note
ORG-002133,https://vinyltoolanddie.com/,https://r.jina.ai/https://vinyltoolanddie.com/,422,,unfetchable,Availability only; no closure inference
ORG-002712,https://www.tips-usa.com/resellers.cfm?RecordID=29C87E9F11A4DB5AA6A5C96614A47A74,https://r.jina.ai/https://www.tips-usa.com/resellers.cfm?RecordID=29C87E9F11A4DB5AA6A5C96614A47A74,401,,unfetchable,Availability only; no closure inference
ORG-000422,https://www.littlern.com/index.html,https://r.jina.ai/https://www.littlern.com/index.html,401,,unfetchable,Availability only; no closure inference
ORG-000443,https://www.midlands-technologies.com/contact,https://www.midlands-technologies.com/contact,200,1911 36th St NE,yes,Raw page words checked; not a dated closure witness
ORG-000654,https://www.atp4pneumatics.com/about-us/,https://r.jina.ai/https://www.atp4pneumatics.com/about-us/,401,,unfetchable,Availability only; no closure inference
ORG-000960,https://www.midwestplasticsoh.com/contactus.html,https://r.jina.ai/https://www.midwestplasticsoh.com/contactus.html,401,,unfetchable,Availability only; no closure inference
ORG-001427,https://www.knrubber.com/about.html,https://r.jina.ai/https://www.knrubber.com/about.html,422,,unfetchable,Availability only; no closure inference
ORG-001685,https://chemstar.direct/about/,https://chemstar.direct/about/,200,Kittyhawk Molding,yes,Raw page words checked; not a dated closure witness
ORG-001719,https://pyramidplastics.com/about/,https://r.jina.ai/https://pyramidplastics.com/about/,401,,unfetchable,Availability only; no closure inference
ORG-001729,https://ir.icumed.com/news-releases/news-release-details/icu-medical-completes-acquisition-smiths-medical-smiths-group,https://r.jina.ai/https://ir.icumed.com/news-releases/news-release-details/icu-medical-completes-acquisition-smiths-medical-smiths-group,401,,unfetchable,Availability only; no closure inference
```

### verdicts.csv
```
rank,org_id,legal_name,verdict,settling_fact
1,ORG-002133,VINYL TOOL & DIE,STILL_UNCERTAIN,Dated operating or closure outcome at Youngstown; final plan filing alone insufficient
2,ORG-002712,Fay L Wagner Inc.,STILL_UNCERTAIN,Dated establishment outcome at 500 North Main Street Yeagertown; public dealer counter-lead needs verification
3,ORG-000422,Littlern Corp.,STILL_UNCERTAIN,Dated operating or cessation witness at Barberton
4,ORG-000443,"Midlands Technologies, Inc.",STILL_UNCERTAIN,Verify current contact-page identity/address before website correction; not court-case closure
5,ORG-000654,Advanced Technology Products,STILL_UNCERTAIN,Raw accessible current operating witness for Milford Center
6,ORG-000960,Midwest Plastics,STILL_UNCERTAIN,Dated Lima establishment witness; exclude namesake website
7,ORG-001427,KN Rubber LLC,STILL_UNCERTAIN,Current operator and dated ownership chain; owner grain ruling if acquired
8,ORG-001685,Kittyhawk Molding Company Inc,STILL_UNCERTAIN,Current operating/identity witness; Chemstar parent-company counter-lead
9,ORG-001719,"Pyramid Plastics, Inc.",STILL_UNCERTAIN,Cleveland primary witness; exclude Rockford namesake
10,ORG-001729,"ICU Medical, Inc.",STILL_UNCERTAIN,Resolve held ICU record grain; acquisition of Smiths is not acquisition of ICU
```

### comparison.txt
```
Unit: unique normalized eligible domains (not business closures).
previous_full 3629 NXDOMAIN 24 PARKED_SUSPECT 3 combined 27
current_full 4327 NXDOMAIN 31 PARKED_SUSPECT 3 combined 34
common_previous 3594 NXDOMAIN 24 PARKED_SUSPECT 3 combined 27
common_current 3594 NXDOMAIN 29 PARKED_SUSPECT 3 combined 32
new frame 733 left frame 35
```
