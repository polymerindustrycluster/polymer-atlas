"""Append-only follow-up statistics on the unchanged original stratified sample."""
import hashlib,json,sys
from pathlib import Path
H=Path(__file__).resolve().parent
OLD=H.parent/'blind-audit-9-2026-11-06'
sys.path.insert(0,str(OLD))
from stats import summarize,read
from freeze import collected,digest

def combine(baseline,followup,selected):
 assert len(baseline)==len({r['site_id'] for r in baseline})==50
 assert len(followup)==len({r['site_id'] for r in followup})==16
 assert {r['site_id'] for r in followup}==selected=={r['site_id'] for r in baseline if r['grade']=='unresolved'},'follow-up population drift'
 revised={r['site_id']:r for r in followup}
 return [revised.get(r['site_id'],r) for r in baseline]

def main():
 pin=json.loads((H/'baseline.json').read_text())
 assert hashlib.sha256((OLD/'adjudicated_verdicts.json').read_bytes()).hexdigest()==pin['original_adjudicated_sha256'],'old results changed'
 baseline=json.loads((OLD/'adjudicated_verdicts.json').read_text())
 frozen=json.loads((H/'freeze.json').read_text());fresh=collected()
 assert {r['site_id']:digest(r) for r in fresh}==frozen['records'],'follow-up verdicts changed after freeze'
 merged=combine(baseline,fresh,set(pin['followup_ids']))
 result=summarize(read(OLD/'sample.csv'),merged)
 result['followup_sites']=16
 result['design_note']='Additional effort targets the original16unresolved cases. These updated observed-category rates reuse the original50site sample and strata; unequal verification effort means they are not an independently drawn second survey or causal accuracy improvement.'
 (H/'updated_statistics.json').write_text(json.dumps(result,indent=2)+'\n')
 (H/'updated_50_verdicts.json').write_text(json.dumps(merged,indent=2)+'\n')
 # The 34 originally resolved records cannot be rewritten by this continuation.
 orig={r['site_id']:r for r in baseline}
 assert all(r==orig[r['site_id']] for r in merged if r['site_id'] not in pin['followup_ids'])
 for bad in [fresh[:-1],fresh[:-1]+[fresh[0]]]:
  try:combine(baseline,bad,set(pin['followup_ids']))
  except AssertionError:pass
  else:raise AssertionError('incomplete/duplicate follow-up accepted')
 print('PASS unchangedoriginal50/16exactfollowup/34resolvedpreserved/same8strataweights; missing+duplicate followup defects rejected')
if __name__=='__main__':main()
