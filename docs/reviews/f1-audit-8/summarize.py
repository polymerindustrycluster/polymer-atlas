"""Reproduce Audit 8 rates from frozen sample metadata and post-freeze grades."""
import csv,json,collections,math
from pathlib import Path
P=Path(__file__).resolve().parent
GRADES=['agreement','field_error','creation_error','unresolved']
def read(n):return json.loads((P/n).read_text())
def main():
    s=read('sample_metadata.json'); rs=read('comparison.json')['records']; meta={r['record_id']:r for r in s['sample']}; byid={r['record_id']:r for r in rs}
    assert len(meta)==len(byid)==65 and set(meta)==set(byid)
    raw={g:sum(r['grade']==g for r in rs) for g in GRADES}
    weighted={g:sum(1/meta[r['record_id']]['inclusion_probability'] for r in rs if r['grade']==g) for g in GRADES}
    assert math.isclose(sum(weighted.values()),1972)
    detailed=[]
    for h in s['strata']:
        selected=[r for r in rs if meta[r['record_id']]['stratum']==h['key']]
        assert len(selected)==h['sample_n']
        row={'creation_tier':h['key'][0],'wave_class':h['key'][1],'record_table':h['key'][2],'single_facility_org':h['key'][3],'population_n':h['population_n'],'sample_n':h['sample_n'],'inclusion_probability':h['sample_n']/h['population_n']}
        for g in GRADES:row[g]=sum(r['grade']==g for r in selected);row[g+'_pct']=100*row[g]/len(selected)
        detailed.append(row)
    grouped=[]
    for tier in 'ABC':
        for wave in ['P1','P2','P3','P4']:
            ds=[r for r in detailed if r['creation_tier']==tier and r['wave_class']==wave]
            N=sum(r['population_n'] for r in ds);n=sum(r['sample_n'] for r in ds)
            r={'creation_tier':tier,'wave_class':wave,'population_n':N,'sample_n':n}
            for g in GRADES:
                r[g]=sum(x[g] for x in ds);r[g+'_raw_pct']=100*r[g]/n if n else None
                r[g+'_weighted_pct']=100*sum(x[g]*x['population_n']/x['sample_n'] for x in ds)/N if N else None
            grouped.append(r)
    for name,rows in [('stratum_rates.csv',detailed),('tier_wave_rates.csv',grouped)]:
        with (P/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    out={'unit':'distinct sampled organization or establishment creation record; not organizations alone','full_creation_frame':2199,'tri_eligible_population':1972,'sample_n':65,'raw_counts':raw,'raw_pct':{g:100*v/65 for g,v in raw.items()},'horvitz_thompson_weighted_counts':weighted,'weighted_pct':{g:100*v/1972 for g,v in weighted.items()},'resolved_only_n':55,'resolved_only_raw_field_error_pct':100*raw['field_error']/55,'weighted_resolved_field_error_pct':100*weighted['field_error']/(weighted['agreement']+weighted['field_error']),'singleton_sample_strata':sum(x['sample_n']==1 for x in detailed),'sampled_error_weights':[{'record_id':r['record_id'],'weight':1/meta[r['record_id']]['inclusion_probability']} for r in rs if r['grade']=='field_error'],'interpretation':'Descriptive observed-finding rates, not proof of whole-record correctness; unresolved and untested fields remain. No design-based confidence interval: 17 refined strata have one observation.','strata':detailed,'tier_wave':grouped}
    (P/'statistics.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['strata','tier_wave']},indent=2))
if __name__=='__main__':main()
