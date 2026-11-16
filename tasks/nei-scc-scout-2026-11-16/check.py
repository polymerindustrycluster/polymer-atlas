"""Named check: pinned-index replay, independent SQL census, seeded review, three defect tests."""
import copy,hashlib,json,subprocess,sys,math
from build import *
sys.path.insert(0,str(ROOT/'scripts'));from site_corpus import on_page

def inspect(metrics,frame,sample):
 assert len({r['site_id'] for r in frame})==len(frame),'duplicate site'
 assert metrics['ohio']['matched_sites']==len(frame),'wrong matched count'
 assert len(sample)==20 and len({r['site_id'] for r in sample})==20
 assert {r['site_id'] for r in sample}=={r['site_id'] for r in read(HERE/'sample_frame.csv')},'seed drift'
 witnesses={r['site_id']:r for r in json.loads((HERE/'positive_witnesses.json').read_text())}
 receipts=json.loads((P/'sample_fetch.json').read_text())+json.loads((P/'extra_fetch.json').read_text())
 for r in sample:
  assert r['verdict'] in ('VERIFIED','STILL_UNCERTAIN','REJECT')
  assert r['assessment'] and r['disposition']=='held'
  if r['verdict']=='VERIFIED':
   witness=witnesses[r['site_id']];assert witness['url']==r['url']
   stored=(P/witness['stored_text']).read_bytes()
   assert hashlib.sha256(stored).hexdigest()==witness['text_sha256'],'stored witness changed'
   assert on_page(r['quote'],stored.decode()),'quote absent from stored copy'
   assert witness['http_status']==200 and witness['route']=='direct'
   refetch=[f for f in json.loads((P/'positive_refetch.json').read_text()) if f['url']==r['url'] and f['sha256']==witness['refetch_raw_sha256']]
   assert len(refetch)==1 and refetch[0]['status']=='ok' and refetch[0]['http_status']==200 and refetch[0]['route']=='direct'
   assert refetch[0]['text_sha256']==witness['text_sha256'] and witness['original_raw_sha256']==r['witness_sha256']
   assert hashlib.sha256((P/witness['refetch_cache']/witness['refetch_raw_file']).read_bytes()).hexdigest()==witness['refetch_raw_sha256'],'refetch raw changed'
   hit=[f for f in receipts if f.get('url')==r['url'] and f.get('sha256')==r['witness_sha256'] and f['status']=='ok'];assert hit,'missing fetched witness'
   f=hit[0];assert hashlib.sha256((P/'own_site'/f['raw_file']).read_bytes()).hexdigest()==f['sha256']
   assert hashlib.sha256((P/'own_site'/f['text_file']).read_bytes()).hexdigest()==f['text_sha256']
   assert on_page(r['quote'],(P/'own_site'/f['text_file']).read_text()),'quote absent'

def main():
 hashes=json.loads((HERE/'input_hashes.json').read_text())
 for name,digest in hashes.items():assert hashlib.sha256((P/name).read_bytes()).hexdigest()==digest, 'input changed: '+name
 receipt=json.loads((HERE/'source_receipt.json').read_text());assert hashlib.sha256((P/'ohio.csv').read_bytes()).hexdigest()==receipt['sha256'],'index changed'
 names=['crosswalk.csv','join_audit.csv','frame.csv','sample_frame.csv','metrics.json','source_receipt.json'];before={n:(HERE/n).read_bytes() for n in names};build();assert all((HERE/n).read_bytes()==b for n,b in before.items()),'non-idempotent packet'
 sql=f'''select count(*),count(distinct "eis facility id") from read_csv('{P}/ohio.csv',all_varchar=true);'''
 out=subprocess.check_output(['duckdb','-csv','-noheader','-c',sql],text=True).strip();n,f=map(int,out.split(','));m=json.loads((HERE/'metrics.json').read_text());assert n==m['ohio_index_rows']==receipt['ohio_distinct_projected_rows'];assert f==m['ohio_nei_facilities']
 frame=read(HERE/'frame.csv');sample=read(HERE/'sample_checks.csv');inspect(m,frame,sample)
 assert sum(r['verdict']=='VERIFIED' for r in sample)==2 and sum(r['verdict']=='STILL_UNCERTAIN' for r in sample)==18
 assert len(read(HERE/'crosswalk.csv'))==m['crosswalk_rows']
 assert len(read(HERE/'join_audit.csv'))==m['candidate_source_rows']
 assert len({r['scc'] for r in read(HERE/'crosswalk.csv')})==m['polymer_relevant_sccs']
 for label,rs in [('ohio',frame),('pic18',[r for r in frame if r['pic18']=='1'])]:
  assert m[label]==dict(matched_sites=len(rs),blank_processes=sum(not r['processes'] for r in rs),blank_materials=sum(not r['materials'] for r in rs),either_blank=sum(not r['processes'] or not r['materials'] for r in rs),tag_candidate_sites=sum(int(r['tag_candidate']) for r in rs))
 # Each defect must be rejected, not merely counted.
 badm=copy.deepcopy(m);badm['ohio']['matched_sites']+=1
 bads=copy.deepcopy(sample);next(r for r in bads if r['verdict']=='VERIFIED')['quote']='A fabricated sentence absent from the fetched witness'
 for label,args in [('duplicate site',(m,frame+[frame[0]],sample)),('wrong count',(badm,frame,sample)),('fabricated quote',(m,frame,bads))]:
  try:inspect(*args)
  except AssertionError:print('Rejected injected defect:',label)
  else:raise AssertionError('silent pass: '+label)
 witness=json.loads((HERE/'positive_witnesses.json').read_text())[0];path=P/witness['stored_text'];saved=path.read_bytes()
 try:
  path.write_bytes(saved+b'corruption')
  try:inspect(m,frame,sample)
  except AssertionError:print('Rejected injected defect: corrupted stored witness')
  else:raise AssertionError('silent pass: corrupted stored witness')
 finally:path.write_bytes(saved)
 print('PASS: replay, SQL census, seeded hand checks, 4/4 defects rejected')
if __name__=='__main__':main()
