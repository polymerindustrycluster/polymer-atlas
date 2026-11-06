"""Observed-finding rates, lane×tier Wilson intervals and explicit design weights."""
import csv,json,runpy
from collections import Counter
from pathlib import Path
from sample import ALLOCATION,read
H=Path(__file__).resolve().parent
wilson=runpy.run_path(str(H.parents[1]/'tasks/source-scout-3-2026-11-06/build.py'))['wilson']
GRADES=('agreement','field_error','creation_error','unresolved')
def summarize(sample,verdicts):
 assert len(sample)==len(verdicts)==len({r['site_id'] for r in verdicts})==50,'incomplete/duplicate verdict census'
 assert {r['site_id'] for r in sample}=={r['site_id'] for r in verdicts},'wrong sample result'
 by={r['site_id']:r for r in verdicts};out=[]
 assert all(r['grade'] in GRADES for r in verdicts)
 for (lane,tier),n in sorted(ALLOCATION.items()):
  rows=[r for r in sample if (r['lane'],r['creation_tier'])==(lane,tier)];assert len(rows)==n
  N=int(rows[0]['stratum_N']);counts=Counter(by[r['site_id']]['grade'] for r in rows)
  row=dict(lane=lane,creation_tier=tier,population_sites=N,sampled_sites=n,inclusion_probability=n/N,census=n==N)
  for grade in GRADES:
   k=counts[grade];row[grade]=k;row[grade+'_rate']=k/n;row[grade+'_wilson95']=wilson(k,n)
  k=counts['field_error']+counts['creation_error'];row['confirmed_error']=k;row['confirmed_error_rate']=k/n;row['confirmed_error_wilson95']=wilson(k,n)
  out.append(row)
 assert sum(r['population_sites'] for r in out)==110
 counts=Counter(r['grade'] for r in verdicts)
 weighted={g:sum(r['population_sites']*r[g]/r['sampled_sites'] for r in out)/110 for g in GRADES}
 return {'sample_sites':50,'population_sites':110,'strata':out,'unweighted_counts':dict(counts),'unweighted_observed_rates':{g:counts[g]/50 for g in GRADES},'design_weighted_observed_points':weighted,'weighted_unresolved_sensitivity':[weighted['field_error']+weighted['creation_error'],weighted['field_error']+weighted['creation_error']+weighted['unresolved']],'interval_note':'Wilson binary intervals per observed finding category, denominator all sampled in stratum incl unresolved. Not latent-error confidence bounds; no pooled iid CI or population-wide accuracy claim. Census strata Wilson shown as requested binomial reference, not sampling uncertainty.'}
def main():
 assert wilson(0,20)==[0,0.161125] and wilson(20,20)==[0.838875,1] and wilson(10,20)==[0.299298,0.700702]
 sample=read(H/'sample.csv');verdicts=json.loads((H/'adjudicated_verdicts.json').read_text());result=summarize(sample,verdicts)
 (H/'statistics.json').write_text(json.dumps(result,indent=2)+'\n')
 # A missing/duplicated record must never look like a clean smaller sample.
 for bad in [verdicts[:-1],verdicts[:-1]+[verdicts[0]]]:
  try:summarize(sample,bad)
  except AssertionError:pass
  else:raise AssertionError('silent incomplete sample acceptance')
 print('PASS full50 /8strata /4grade rates; Wilson3knownanswers; missing+duplicate defects rejected')
if __name__=='__main__':main()
