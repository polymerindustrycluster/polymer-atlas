#!/usr/bin/env python3
"""Assemble reviewed verdicts and rerun the house dedupe function against current shards."""
import csv, json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts')); import atlas
from research import SOURCES

def read(p):
    with open(p,newline='') as f:return list(csv.DictReader(f))
def write(p,rows,fields):
    with open(p,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
    tables={}
    for name in ('organizations','sites','ecosystem'):
        t=atlas.Table(name)
        for f in (sorted((ROOT/'data').glob(name+'_*.csv')) if name!='ecosystem' else [ROOT/'data/ecosystem.csv']):
            for r in read(f):r['__file__']=str(f.relative_to(ROOT));r['__line__']=0;t.rows.append(r)
        tables[name]=t
    raw={r['cluster_id']:r for r in read(HERE/'rawcheck.csv')}
    output=[]; logs={}
    for c in sorted(read(HERE/'input.csv'),key=lambda x:({'MO':0,'SC':1,'LA':2}[x['state']],x['cluster_id'])):
        key=c['cluster_id'][3:];url,quote,scope,held=SOURCES[key]
        d=atlas.dedupe(tables,domain=url,name=c['best_name'],street=c['street'],city=c['city'],state=c['state'],zip_=c['zip5'])
        # Address matching ignores mailing-city spelling and ZIP changes; these must not mint a duplicate.
        street_hits=[r for r in tables['sites'].rows if r['state']==c['state'] and atlas.street_key(r['street_address'])==atlas.street_key(c['street'])]
        logs[c['cluster_id']]=dict(dedupe=d,street_hits=[r['site_id'] for r in street_hits])
        hits=d['steps'][0]['hits']+d['steps'][1]['hits']
        if not held and hits:
            terminal={h.get('successor_chain',[h['id']])[-1] for h in hits}
            if len(terminal)==1:held=terminal.pop()
        verdict='VERIFIED';reason='Federal establishment corroborated by raw-checked operator page.';duplicate=''
        if street_hits:
            verdict='DUPLICATE_OF';duplicate=street_hits[0]['site_id'];reason='Same physical street already held.'
        elif scope not in ('1','2'):
            verdict=scope;reason=held;held=''
        elif raw[c['cluster_id']]['raw']!='yes':
            verdict='STILL_UNCERTAIN';reason='Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote.'
        elif not held and len(hits)>1:
            verdict='STILL_UNCERTAIN';reason='Need operator resolution among multiple domain/name matches.'
        # Exact registry names retained as aliases, never guessed from the fused plan-title best_name.
        output.append(dict(cluster_id=c['cluster_id'],state=c['state'],verdict=verdict,duplicate_of=duplicate,held_org_id=held if verdict=='VERIFIED' else '',ring=scope if scope in ('1','2') else '',own_url=url,own_quote=quote if raw[c['cluster_id']]['raw']=='yes' else '',deciding_fact=reason))
    write(HERE/'verdicts.csv',output,list(output[0]))
    holds=[{'cluster_id':r['cluster_id'],'reason':r['deciding_fact']} for r in output if r['verdict']=='STILL_UNCERTAIN']
    write(HERE/'holds.csv',holds,['cluster_id','reason'])
    (HERE/'dedupe.json').write_text(json.dumps(logs,indent=2)+'\n')
    from collections import Counter
    print(Counter((r['state'],r['verdict']) for r in output))
if __name__=='__main__':main()
