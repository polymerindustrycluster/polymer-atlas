"""Named oracle: committed samples -> yields; Census API totals -> CBP parity.
Run from any directory. --write refreshes derived metrics; default checks them.
"""
import csv,json,math,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import atlas
from regions import PIC18

def wilson(k,n):
 if not n:return None
 z=1.959963984540054;d=1+z*z/n;c=(k/n+z*z/(2*n))/d;h=z*math.sqrt(k/n*(1-k/n)/n+z*z/(4*n*n))/d
 return [round(max(0,c-h),6),round(min(1,c+h),6)]

def summarize(rows):
 assert len(rows)==20,'sample must contain exactly 20 rows'
 assert len({r['name'] for r in rows})==20,'duplicate sample names'
 k=0
 for r in rows:
  assert r['verdict'] in {'VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF'}
  assert r['verified_new'] in {'0','1'}
  assert (r['verified_new']=='1')==(r['verdict']=='VERIFIED')
  k+=int(r['verified_new'])
 return dict(sampled=len(rows),verified_new=k,yield_fraction=k/len(rows),wilson95=wilson(k,len(rows)),verdicts={v:sum(r['verdict']==v for r in rows) for v in sorted({r['verdict'] for r in rows})})

def main():
 # Known Wilson answers and intentional malformed-sample rejection prove the gate fails.
 assert wilson(0,20)==[0,0.161125] and wilson(20,20)==[0.838875,1]
 try:summarize([{'name':'bad'}]*20)
 except AssertionError:pass
 else:raise AssertionError('defect injection was not caught')
 tables=atlas.load_tables(ROOT/'data')
 for name,oid in [('The Goodyear Tire & Rubber Company','ORG-000003'),('Avient Corporation','ORG-000001'),('The Lubrizol Corporation','ORG-000002')]:
  hits=atlas.dedupe(tables,name=name)['steps'][1]['hits'];assert oid in {h['id'] for h in hits},(name,hits)
 metrics={}
 for source in ['association','patentsview']:
  rows=list(csv.DictReader((HERE/source/'sample.csv').open()));metrics[source]=summarize(rows)
  for r in rows:
   if r['verdict']=='DUPLICATE_OF':
    ids=(r.get('dedupe_hits') or r.get('atlas_ids')).split(';');assert len(ids)==1
    assert any(x['org_id']==ids[0] for x in tables['organizations'].rows+tables['ecosystem'].rows)
 api=json.loads((HERE/'cbp/api_totals.json').read_text());api=[dict(zip(api[0],r)) for r in api[1:]]
 bulk=list(csv.DictReader((ROOT/'docs/denominators/cbp_size_classes_polymer.csv').open()))
 codes={'005','029','043','077','139','157'}
 expected={(r['state']+r['county'],r['NAICS2017']):int(r['ESTAB']) for r in api if r['county'] in codes}
 actual={(r['geo_fips'],r['naics']):int(r['estab']) for r in bulk if r['geo_level']=='county' and r['geo_fips'][:2]=='39' and r['geo_fips'][2:] in codes and r['size_code']=='all'}
 assert len(expected)==16 and actual==expected,(actual,expected)
 assert len({(r['geo_level'],r['geo_fips'],r['naics'],r['size_code']) for r in bulk})==len(bulk)
 # Check published yield strings as well as JSON, so stale prose cannot silently pass.
 for source,ratio,percent,interval in [('association','3/20','15%','5.24–36.04%'),('patentsview','0/20','0%','0–16.11%')]:
  m=metrics[source];assert ratio==f"{m['verified_new']}/{m['sampled']}"
  assert percent==f"{100*m['yield_fraction']:g}%"
  assert interval==(f"{100*m['wilson95'][0]:.2f}–{100*m['wilson95'][1]:.2f}%" if source=='association' else f"0–{100*m['wilson95'][1]:.2f}%")
  for path in [HERE/'README.md',HERE/source/'README.md',ROOT/'docs/SOURCES.md']:
   prose=path.read_text();assert ratio in prose and interval in prose,(path,source)
 raw=list(csv.DictReader((HERE/'association/raw_checks.csv').open()));assert len(raw)==6
 samples={r['name']:r for r in csv.DictReader((HERE/'association/sample.csv').open())}
 for r in raw:assert r['raw_words_in_order']=='PASS' and r['quote']==samples[r['name']][r['claim']]
 metrics['cbp']=dict(counties=6,county_naics_totals_reconciled=len(actual),size_class_rows=sum(r['geo_level']=='county' and r['geo_fips'][:2]=='39' and r['geo_fips'][2:] in codes for r in bulk),naics326_establishments=sum(v for (f,c),v in actual.items() if c=='326'))
 assignees=list(csv.DictReader((HERE/'patentsview/assignees.csv').open()));assert len(assignees)==len({r['assignee_id'] for r in assignees})==12939
 counts=json.loads((HERE/'patentsview/counts.json').read_text());assert counts['organization_assignees']==len(assignees)
 assert counts['exact_name_candidates']==sum(bool(r['atlas_ids']) for r in assignees)
 assert counts['pic18_location_assignees']==sum(int(r['pic18_assignee_location']) for r in assignees)
 metrics['patent_match_rate']=dict(matched_assignee_candidates=counts['exact_name_candidates'],assignees=len(assignees),fraction=counts['exact_name_candidates']/len(assignees))
 dest=HERE/'metrics.json'
 if '--write' in sys.argv:dest.write_text(json.dumps(metrics,indent=2)+'\n')
 else:assert json.loads(dest.read_text())==metrics,'metrics stale'
 print(json.dumps(metrics,indent=2));print('PASS: sample yields, duplicate targets, known answers, injected defect, CBP API totals, ID uniqueness')
if __name__=='__main__':main()
