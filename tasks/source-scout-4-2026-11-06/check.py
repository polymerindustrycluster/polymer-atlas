"""Recompute sample yields and frame counts; no network or canonical mutation."""
import csv,json,math,sys,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT/'scripts'));import atlas

def read(path):return list(csv.DictReader(path.open()))
def module(path):
 spec=importlib.util.spec_from_file_location(path.parent.name+'_scout',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def wilson(k,n):
 if not n:return None
 z=1.959963984540054;d=1+z*z/n;c=(k/n+z*z/(2*n))/d;h=z*math.sqrt(k/n*(1-k/n)/n+z*z/(4*n*n))/d
 return [round(max(0,c-h),6),round(min(1,c+h),6)]

def yields(rows,id_field):
 assert len(rows)==20 and len({r[id_field] for r in rows})==20,'20 unique sample units required'
 k=0
 for r in rows:
  assert r['verdict'] in {'VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF'}
  assert r['verified_new'] in {'0','1'} and (r['verified_new']=='1')==(r['verdict']=='VERIFIED')
  k+=int(r['verified_new'])
 return dict(sampled=len(rows),verified_new=k,yield_fraction=k/len(rows),wilson95=wilson(k,len(rows)),verdicts={v:sum(r['verdict']==v for r in rows) for v in sorted({r['verdict'] for r in rows})})

def main():
 assert wilson(0,20)==[0,0.161125] and wilson(20,20)==[0.838875,1]
 try:yields([{'id':'dup'}]*20,'id')
 except AssertionError:pass
 else:raise AssertionError('duplicate-input mutation escaped gate')
 tables=atlas.load_tables(ROOT/'data');orgids={r['org_id'] for table in ['organizations','ecosystem'] for r in tables[table].rows};siteids={r['site_id'] for r in tables['sites'].rows}
 for name,oid in [('Avient Corporation','ORG-000001'),('The Lubrizol Corporation','ORG-000002'),('The Goodyear Tire & Rubber Company','ORG-000003')]:assert oid in {h['id'] for h in atlas.dedupe(tables,name=name)['steps'][1]['hits']}
 metrics={}
 for source,key,ids in [('acma','record_id',orgids),('epa-cdr','tsca_site_id',siteids)]:
  rows=read(HERE/source/'sample.csv');metrics[source]=yields(rows,key)
  for r in rows:
   if r['verdict']=='DUPLICATE_OF':assert r['duplicate_of'] in ids
  assert '0/20' in (HERE/source/'README.md').read_text() and '0–16.11%' in (HERE/source/'README.md').read_text()
 # Uninspected source gates remain explicit unavailable metrics, never passing zero samples.
 for source in ['apr','vinyl-institute','sam-gov']:
  assert read(HERE/source/'sample.csv')==[]
  metrics[source]=dict(sampled=None,verified_new=None,yield_fraction=None,wilson95=None,reason='terms/raw-route/credential gate; not sampled')
 independent=read(HERE/'epa-cdr/independent_counts.csv');assert independent==[dict(input_rows='50433',all_site_ids='4528',slice_rows='2924',slice_site_ids='290')]
 frame=read(HERE/'epa-cdr/frame.csv');counts=json.loads((HERE/'epa-cdr/counts.json').read_text())
 assert counts['input_chemical_reporting_rows']==50433 and counts['all_tsca_site_ids']==4528
 assert len(frame)==len({r['tsca_site_id'] for r in frame})==counts['slice_tsca_site_ids']==290
 assert sum(int(r['chemical_reporting_rows']) for r in frame)==counts['slice_chemical_reporting_rows']==2924
 byid={r['tsca_site_id']:r for r in frame}
 for r in read(HERE/'epa-cdr/sample.csv'):
  assert r['tsca_site_id'] in byid
  for key,value in byid[r['tsca_site_id']].items():assert r[key]==value
 cdr=module(HERE/'epa-cdr/build.py')
 for n in ['325211 Resin','326199 Plastics','326299 Rubber']:assert cdr.in_slice({'SITE NAICS CODE 1':n})
 for n in ['332618 Wire','CBI','NKRA','19326199 Fake']:assert not cdr.in_slice({'SITE NAICS CODE 1':n})
 acma=module(HERE/'acma/scout.py');fixture={str(i):dict(recordId=str(i),state=state,opt=opt,**{'organization-type':typ}) for i,(state,opt,typ) in enumerate([('OH',False,'Manufacturer'),('ON',False,'Manufacturer'),('OH',True,'Manufacturer'),('OH',False,'Supplier')])};assert len(acma.frame(fixture))==1
 # The review defect must be caught both during generation and in committed samples.
 assert acma.excerpt('Fiberglass components for industrial service')=='Fiberglass components for industrial service'
 for contact in ['PH: 555-010-2345','FX: 555-010-2345','sales@example.com','(555) 010-2345']:
  assert acma.excerpt('Fiberglass components '+contact)==''
  assert acma.CONTACT.search('Fiberglass components '+contact)
 for row in read(HERE/'acma/sample.csv'):
  assert not acma.CONTACT.search(row['scope_quote']),f"contact data in discovery excerpt: {row['record_id']}"
 c=json.loads((HERE/'acma/counts.json').read_text());assert c==dict(public_listings=252,manufacturer_listings=121,us_manufacturer_not_opted_out=98,sampled=20)
 metrics['frames']=dict(cdr_input_rows=counts['input_chemical_reporting_rows'],cdr_all_site_ids=counts['all_tsca_site_ids'],cdr_slice_site_ids=len(frame),cdr_slice_chemical_rows=2924,acma_public_listings=252,acma_us_manufacturer_not_opted_out=98)
 routes=read(HERE/'routes.csv');assert len(routes)==9 and all(r['http_status'] and r['sha256'] for r in routes)
 assert all(r['http_status']=='200' for r in routes if r['source'] in ['apr','acma','epa-cdr','vinyl-institute'])
 terms=read(HERE/'terms_checks.csv');assert len(terms)==6 and {r['source'] for r in terms}=={'apr','acma','epa-cdr','sam-gov','vinyl-institute'}
 for r in terms:assert r['raw_words_in_order']=='PASS' and r['quote'] in (HERE/r['source']/'README.md').read_text()
 dest=HERE/'metrics.json'
 if '--write' in sys.argv:dest.write_text(json.dumps(metrics,indent=2)+'\n')
 else:assert json.loads(dest.read_text())==metrics,'stale metrics'
 print(json.dumps(metrics,indent=2));print('PASS:40 sampled units; all uninspected gates explicit; known answers and injected defects; CDR frame and ACMA slice')
if __name__=='__main__':main()
