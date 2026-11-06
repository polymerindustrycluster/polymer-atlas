"""Named audit gate: exact sample/results, freezes, statistics/report and canonical read-only."""
import copy,csv,hashlib,json,subprocess
from collections import Counter
from frame import derive
from sample import draw,read
from lock import collected,digest,main as lockcheck
from stats import summarize,wilson
from write_report import H,REPORT,render

def frozen_ok(rows,freeze):
 assert len(rows)==len({r['site_id'] for r in rows})==50
 assert {r['site_id']:digest(r) for r in rows}==freeze['records'],'unreported frozen verdict change'
def main():
 meta=json.loads((H/'frame_provenance.json').read_text());frame=read(H/'frame.csv');sample=read(H/'sample.csv');receipt=json.loads((H/'draw.json').read_text())
 assert derive(meta)==frame
 expected=draw(frame)
 assert sample==[{k:str(v) for k,v in r.items()} for r in expected]
 for n in ['frame','sample']:assert hashlib.sha256((H/(n+'.csv')).read_bytes()).hexdigest()==receipt[n+'_sha256']
 assert Counter(r['creation_tier'] for r in sample)=={'C':44,'B':6}
 lockcheck();freeze=json.loads((H/'freeze.json').read_text());rows=collected();frozen_ok(rows,freeze)
 for name,sha in freeze['files'].items():assert hashlib.sha256((H/name).read_bytes()).hexdigest()==sha
 for bad in [rows[:-1],rows[:-1]+[rows[0]]]:
  try:frozen_ok(bad,freeze)
  except AssertionError:pass
  else:raise AssertionError('incomplete/duplicate frozen census accepted')
 bad=copy.deepcopy(rows);bad[0]['observations']+=' fabricated silent edit'
 try:frozen_ok(bad,freeze)
 except AssertionError:pass
 else:raise AssertionError('unreported edit accepted')
 adjudicated=json.loads((H/'adjudicated_verdicts.json').read_text());assert hashlib.sha256((H/'adjudicated_verdicts.json').read_bytes()).hexdigest()==freeze['adjudicated_sha256']
 assert Counter(r['grade'] for r in adjudicated)=={'agreement':32,'field_error':1,'creation_error':1,'unresolved':16}
 assert summarize(sample,adjudicated)==json.loads((H/'statistics.json').read_text())
 assert wilson(0,20)==[0,0.161125] and wilson(20,20)==[0.838875,1] and wilson(10,20)==[0.299298,0.700702]
 assert REPORT.read_text()==render(),'report no longer matches frozen counts'
 # Every fetch is counted, failed routes included; never silently omit a body/hash.
 attempts=[]
 for k in 'abc':attempts+=json.loads((H/f'receipts_{k}.json').read_text())
 assert len(attempts)==159 and {r['site_id'] for r in attempts}=={r['site_id'] for r in sample}
 assert max(Counter(r['site_id'] for r in attempts).values())<=6
 assert sum(len(r['sources']) for r in rows)==117
 assert sum(bool(s['raw_checked']) for r in rows for s in r['sources'])==115
 comp=json.loads((H/'original_evidence_comparison.json').read_text());assert comp['original_evidence_rows']==351
 assert json.loads((H/'comparison_start.json').read_text())['started_at_utc']>freeze['frozen_at_utc']
 for cached in (False,True):
  args=['git','diff']+(['--cached'] if cached else [])+['--exit-code','--quiet','--','data/'];subprocess.run(args,check=True)
 assert not subprocess.check_output(['git','diff',meta['pinned_main'],'--name-only','--','data/']).strip(),'canonical tree changed from pin'
 print('PASS audit9:110frame/50stratifiedsites/32A1F1C16U;115quoteobservations/159receipts;freeze+admitted2metadatafields;sample/stats/Wilson/report;3frozen-defectinjections;0canonicaldiff')
if __name__=='__main__':main()
