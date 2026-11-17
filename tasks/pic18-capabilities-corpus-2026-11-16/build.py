"""Replay only CAP lane columns; reserved IDs, no organization writes."""
import csv, hashlib, html, io, json, re, subprocess, sys
from pathlib import Path
T = Path(__file__).resolve().parent
ROOT = T.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from shard_io import append_sorted
from regions import PIC18
CORPUS = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-corpus-2026-11-16')
BASE = (T / 'base.txt').read_text().strip()
WHO = 'atlas-w16-capabilities'
def read(p):
    return list(csv.DictReader(Path(p).open(newline='')))
def base(p):
    return list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',f'{BASE}:{p}'],cwd=ROOT,text=True))))
def write(p, rows):
    with Path(p).open('w', newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def norm(t):
    return ' '.join(t.split())
from functools import lru_cache
@lru_cache(maxsize=1)
def frame():
    sites=[r for p in sorted((ROOT/'data').glob('sites_*.csv')) if p.name!='sites_all.csv' for r in base(str(p.relative_to(ROOT)))]
    from collections import Counter
    n=Counter(s['org_id'] for s in sites if s['operating_status']=='active')
    excluded={r['site_id'] for b in ('01','02') for f in ('frame.csv','verdicts.csv') for r in read(ROOT/f'tasks/oh-capabilities-2026-11-12-b{b}/{f}')}
    orgs={r['org_id'] for r in read(CORPUS/'manifest.csv') if r['text_file']}
    return [s for s in sites if s['state']=='OH' and s['county'] in PIC18 and s['operating_status']=='active' and s['verification_tier'] in ('A','B','C') and (not s['processes'] or not s['materials']) and n[s['org_id']]==1 and s['site_id'] not in excluded and s['org_id'] in orgs]
def validate_decision(d):
    assert hashlib.sha256((CORPUS/d['raw_file']).read_bytes()).hexdigest()==d['sha256']
    raw=(CORPUS/d['raw_file']).read_text(errors='replace')
    plain=html.unescape(re.sub('<[^>]+>', ' ', raw))
    words=iter(re.findall(r'\w+', plain.lower()))
    assert all(any(w==q for w in words) for q in re.findall(r'\w+',d['quote'].lower())), 'raw quote absent'
    text=norm((CORPUS/d['text_file']).read_text())
    assert norm(d['quote']) in text, d
    assert norm(d['grain_quote']) in text, d
    assert len(d['quote'].split())<=25
    assert d['term'] in json.loads((ROOT/'docs/schema/vocab.json').read_text())['vocabularies'][d['field'].upper()]['values']
def outputs(decisions):
    sites={r['site_id']:dict(r) for r in frame()}
    vocab=json.loads((ROOT/'docs/schema/vocab.json').read_text())['vocabularies']
    caps=[];ev=[];verdicts=[]
    live={(c['site_id'],c['capability_type'],c['term']) for c in base('data/site_capabilities.csv') if not c['withdrawn_date']}
    for d in decisions:
        validate_decision(d)
        s=sites[d['site_id']];typ='process' if d['field']=='processes' else 'material'
        tag=not (d['basis']=='menu' and s['verification_tier'] in ('A','B'))
        if tag:
            vals=set(filter(None,s[d['field']].split(';')));vals.add(d['term']);s[d['field']]=';'.join(sorted(vals))
            ev.append(dict(evidence_id=f'EVD-{377000+len(ev):06d}',record_table='sites',record_id=s['site_id'],claim_type='scope',claim_detail=f"{d['field']}={d['term']}; quote: {d['quote']}",source_class='own_site',source_ref=d['url'],observed_date='2026-11-16',tier_effect='supports_C' if d['basis']=='menu' else 'supports_A',created_by=WHO,notes=f"{d['basis']}; raw SHA256 {d['sha256']}; single held active plant; locality witness in task decisions."))
        ct=d['term'] if d['term'] in vocab['CAP_'+typ.upper()]['values'] else None
        if ct and (s['site_id'],typ,ct) not in live:
            live.add((s['site_id'],typ,ct))
            caps.append(dict(capability_id=f'CAP-{1100+len(caps):06d}',site_id=s['site_id'],org_id=s['org_id'],capability_type=typ,term=ct,provenance='company_disclosed',source_ref=d['url'],observed_date='2026-11-16',withdrawn_date='',created_by=WHO,notes=f"Quote: {d['quote']} Basis: {d['basis']}. Raw SHA256 {d['sha256']}."+(' Section-3 tag held per owner ruling 2026-11-14; needs narrative plant evidence.' if not tag else '')))
        verdicts.append(dict(site_id=s['site_id'],term=d['term'],verdict='VERIFIED',disposition='applied' if tag else 'tag held; no new capability (existing or unmapped)',settling_fact='' if tag else 'Plant narrative stating this term, per owner ruling 2026-11-14'))
    for s in sites.values():
        if not any(d['site_id']==s['site_id'] for d in decisions):
            reason='An own-page narrative or capability list explicitly binding a governed process/material to this establishment; plant allocation remains unadjudicated.'
            if s['site_id']=='SITE-000266':reason='Allocate the disclosed capability to the Youngstown plant among Boardman Molded Locations.'
            if s['site_id']=='SITE-001731':reason='Bind material handling to the held plant rather than the separately disclosed headquarters or warehouse.'
            if s['site_id']=='SITE-001930':reason='Evidence that the Akron plant runs rotational molding; page currently describes making molds for other molders.'
            verdicts.append(dict(site_id=s['site_id'],term='',verdict='STILL_UNCERTAIN',disposition='held',settling_fact=reason))
    return sites,caps,ev,verdicts

def main():
    sites,caps,ev,verdicts=outputs(read(T/'decisions.csv'))
    path=ROOT/'data/sites_OH.csv';current=read(path)
    for s in current:
        if s['site_id'] in sites:
            for col in ('processes','materials'):
                initial=next(x for x in frame() if x['site_id']==s['site_id'])
                additions=set(filter(None,sites[s['site_id']][col].split(';')))-set(filter(None,initial[col].split(';')))
                if additions:s[col]=';'.join(sorted(set(filter(None,s[col].split(';')))|additions))
    write(path,current)
    for filename,rows,key in [('site_capabilities.csv',caps,'capability_id'),('evidence_sites_OH.csv',ev,'evidence_id')]:
        path=ROOT/'data'/filename;have={r[key]:r for r in read(path)}
        for r in rows:
            if r[key] in have:assert r==have[r[key]],r[key]
        append_sorted(path,[r for r in rows if r[key] not in have],key)
    write(T/'verdicts.csv',verdicts)
    summary=dict(frame_sites=len(sites),accepted_sites=len({d['site_id'] for d in read(T/'decisions.csv')}),applied_sites=len({r['site_id'] for r in caps}|{r['record_id'] for r in ev}),held_sites=len({v['site_id'] for v in verdicts if v['verdict']=='STILL_UNCERTAIN'}),term_decisions=len(read(T/'decisions.csv')),capability_rows=len(caps),evidence_rows=len(ev),changed_sites=sum(s!=next(x for x in frame() if x['site_id']==s['site_id']) for s in sites.values()))
    (T/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
if __name__=='__main__':main()
