"""Offline packet oracle. Missing requested frames stay unmeasured, never zero."""
import csv,json,sys,math,random,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import atlas
from regions import PIC18

def read(p):return list(csv.DictReader(p.open()))
def wilson(k,n):
 if not n:return None
 z=1.959963984540054;d=1+z*z/n;c=(k/n+z*z/(2*n))/d;h=z*math.sqrt(k/n*(1-k/n)/n+z*z/(4*n*n))/d
 return [round(max(0,c-h),6),round(min(1,c+h),6)]
def unique(rows,key,n):assert len(rows)==len({r[key] for r in rows})==n

def main():
 assert wilson(0,20)==[0,0.161125] and wilson(20,20)==[0.838875,1]
 try:unique([{'id':'dup'}]*20,'id',20)
 except AssertionError:pass
 else:raise AssertionError('duplicate-ID injection escaped')
 tables=atlas.load_tables(ROOT/'data');sites={r['site_id']:r for r in tables['sites'].rows}
 for name,oid in [('Avient Corporation','ORG-000001'),('The Lubrizol Corporation','ORG-000002'),('The Goodyear Tire & Rubber Company','ORG-000003')]:assert oid in {h['id'] for h in atlas.dedupe(tables,name=name)['steps'][1]['hits']}
 metrics={}
 for source in ['ohio-air','ocs-blue','caa-sb54','nsf61']:
  assert read(HERE/source/'sample.csv')==[]
  metrics[source]=dict(sampled=None,verified_new=None,yield_fraction=None,wilson95=None,reason='requested frame gated by route/terms; not sampled')
 frame=read(HERE/'ohio-air/pbr_frame.csv');sample=read(HERE/'ohio-air/pbr_sample.csv');counts=json.loads((HERE/'ohio-air/pbr_counts.json').read_text())
 unique(frame,'facility_id',21);unique(sample,'facility_id',20)
 assert [r['facility_id'] for r in random.Random(20261106).sample(frame,20)]==[r['facility_id'] for r in sample]
 byid={r['facility_id']:r for r in frame}
 for r in sample:assert r==byid[r['facility_id']]
 for r in frame:
  assert r['county'] in PIC18 and r['state']=='OH'
  assert r['verdict'] in {'DUPLICATE_OF','STILL_UNCERTAIN'} and r['verified_new']=='0'
  d=atlas.dedupe(tables,name=r['name'],street=r['street'],city=r['city'],state=r['state'],zip_=r['zip']);ids={h['id'] for h in d['steps'][2]['hits']}
  assert ids==set(filter(None,r['site_hits'].split(';'))), f"current held-street matches changed: {r['facility_id']} {sorted(ids)}"
  if r['verdict']=='DUPLICATE_OF':assert ids=={r['duplicate_of']} and r['duplicate_of'] in sites
  else:assert len(ids)!=1 and r['reason'].startswith('settling fact:')
 assert sum(int(r['unit_rows']) for r in frame)==counts['keyword_unit_rows']==33
 expected=dict(whole_workbook_unit_rows=19443,whole_workbook_facility_ids=12196,state_oh_unit_rows=19440,state_oh_facility_ids=12194,pic18_county_only_unit_rows=7824,pic18_county_only_facility_ids=4758,pic18_county_and_state_oh_unit_rows=7822,pic18_county_and_state_oh_facility_ids=4757,non_oh_coded_unit_rows=3,non_oh_coded_facility_ids=2)
 assert {k:counts[k] for k in expected}==expected and counts['input_blank_rows']==1 and counts['keyword_facility_ids']==21
 independent=read(HERE/'ohio-air/independent_counts.csv');assert independent==[{k:str(v) for k,v in expected.items()}]
 anomalies=read(HERE/'ohio-air/geography_anomalies.csv')
 assert len(anomalies)==counts['non_oh_coded_unit_rows']==counts['whole_workbook_unit_rows']-counts['state_oh_unit_rows']
 assert {r['facility_id'] for r in anomalies}=={'04-48-01-2010','13-18-00-8701'} and all(r['state']!='OH' for r in anomalies)
 assert len({r['facility_id'] for r in anomalies})==counts['non_oh_coded_facility_ids']==counts['whole_workbook_facility_ids']-counts['state_oh_facility_ids']
 pic_anomalies=[r for r in anomalies if r['county'] in PIC18]
 assert len(pic_anomalies)==counts['pic18_county_only_unit_rows']-counts['pic18_county_and_state_oh_unit_rows']==2
 assert len({r['facility_id'] for r in pic_anomalies})==counts['pic18_county_only_facility_ids']-counts['pic18_county_and_state_oh_facility_ids']==1
 assert not {r['facility_id'] for r in anomalies}&set(byid)
 assert [(r['state'],r['county']) for r in anomalies]==[('IN','Out_of_state_county'),('NC','Cuyahoga'),('NC','Cuyahoga')]
 metrics['pbr_keyword_fallback']=dict(sampled=20,verified_new=0,yield_fraction=0,wilson95=wilson(0,20),duplicate_sample_sites=sum(r['verdict']=='DUPLICATE_OF' for r in sample),uncertain_sample_sites=sum(r['verdict']=='STILL_UNCERTAIN' for r in sample),frame_facility_ids=21,frame_unit_rows=33)
 assert metrics['pbr_keyword_fallback']['duplicate_sample_sites']==4
 metrics['pbr_keyword_fallback']['sample_exact_street_match_fraction']=4/20
 metrics['pbr_keyword_fallback']['sample_exact_street_match_wilson95']=wilson(4,20)
 metrics['pbr_keyword_fallback']['frame_exact_street_matches']=sum(r['verdict']=='DUPLICATE_OF' for r in frame)
 metrics['pbr_keyword_fallback']['frame_exact_street_match_fraction']=sum(r['verdict']=='DUPLICATE_OF' for r in frame)/len(frame)
 for name in ['README.md','ohio-air/README.md','docs_proposals.md']:
  s=(HERE/name).read_text();assert '0/20' in s and '0–16.11%' in s
 terms=read(HERE/'raw_checks.csv');assert len(terms)==4
 for r in terms:assert r['raw_words_in_order']=='PASS' and r['quote'] in (HERE/r['source']/'README.md').read_text()
 routes=read(HERE/'routes.csv');assert len(routes)>=7
 edoc=[r for r in routes if r['route']=='edocument_search'];assert edoc and edoc[0]['content_verdict']=='CHALLENGE'
 dest=HERE/'metrics.json'
 if '--write' in sys.argv:dest.write_text(json.dumps(metrics,indent=2)+'\n')
 else:assert json.loads(dest.read_text())==metrics
 print(json.dumps(metrics,indent=2));print('PASS: requested unmeasured gates; separate20-PBR sample; counties/counts/held dedupe; known answers and defect controls')
if __name__=='__main__':main()
