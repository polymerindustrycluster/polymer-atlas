"""Recompute frame, matches, payload and counts; exercise three actual corruptions."""
import copy, csv, io, json, subprocess
import build as b

def verify(frame,edits,links,evidence):
    expected=b.frame()
    assert len(frame)==len({r['site_id'] for r in frame})
    assert frame==expected, 'frame drift/loss'
    current={r['site_id']:r for r in b.read(b.ROOT/'data/sites_OH.csv')}
    witnesses=b.read(b.HERE/'witnesses.csv')
    for e in edits:
        assert current[e['site_id']]['employee_band_site']==e['new_value']
        raw=[json.loads(w['raw']) for w in witnesses if w['site_id']==e['site_id'] and w['kind']=='ITA']
        assert len(raw)==1 and raw[0]['reliability']=='ok'
        assert b.fusion.band_of(raw[0]['annual_average_employees'])==e['new_value']
        assert any(v['record_id']==e['site_id'] and v['claim_type']=='size_band' and f"employee_band_site={e['new_value']}" in v['claim_detail'] for v in evidence)
    for link in links:
        raw=[json.loads(w['raw']) for w in witnesses if w['site_id']==link['site_id'] and w['kind']=='ECHO']
        assert len(raw)==1
        assert link['registry_id'] in (raw[0]['REGISTRY_ID'].split(';') if link['registry']=='FRS' else __import__('re').split(r'[;,\s]+',raw[0].get('TRI_IDS','')))
        assert link in b.read(b.ROOT/'data/registry_links.csv')
    assert len({e['evidence_id'] for e in evidence})==len(evidence)
    assert all(360000<=int(e['evidence_id'][4:])<=363999 for e in evidence)
    held=b.read(b.ROOT/'data/evidence_sites_OH.csv')
    assert all(e in held for e in evidence)

f=b.read(b.HERE/'frame.csv');e=b.read(b.HERE/'band_edits.csv');l=b.read(b.HERE/'registry_proposals.csv');v=b.read(b.HERE/'evidence.csv')
verify(f,e,l,v)
# Independent Git diff line count, separate from builder historical join.
diff=subprocess.check_output(['git','diff','--unified=0','91cd1a8',b.BASE,'--','data/sites_OH.csv'],cwd=b.ROOT,text=True)
a={next(csv.reader([x[1:]]))[0]:next(csv.reader([x[1:]])) for x in diff.splitlines() if x.startswith('+SITE-')}
z={next(csv.reader([x[1:]]))[0]:next(csv.reader([x[1:]])) for x in diff.splitlines() if x.startswith('-SITE-')}
cols=list(b.at(b.BASE,'data/sites_OH.csv')[0]); street=cols.index('street_address');status=cols.index('operating_status');state=cols.index('state')
independent={k for k in a.keys()&z.keys() if not z[k][street].strip() and a[k][street].strip() and a[k][status]=='active' and a[k][state]=='OH'}
assert independent=={r['site_id'] for r in f}
receipt=json.loads((b.CACHE/'receipt.json').read_text());assert len(b.read(b.CACHE/'ohio.csv'))==receipt['ohio']
summary=json.loads((b.HERE/'summary.json').read_text());_,src,p,w=b.plan()
assert b.read(b.HERE/'witnesses.csv')==[dict(site_id=s['site_id'],kind=r['kind'],source_id=r['id'],raw=json.dumps(r['raw'],sort_keys=True)) for s,r in w]
assert summary['frame']==len(f) and summary['proposals']==len(p) and summary['source_rows']==dict(b.Counter(r['kind'] for r in src))
assert (summary['band_fills'],summary['registry_links'],summary['evidence'])==(len(e),len(l),len(v))
for kind in ('duplicate frame','lost frame','phantom registry'):
    ff=copy.deepcopy(f);ll=copy.deepcopy(l)
    if kind=='duplicate frame':ff.append(ff[0])
    if kind=='lost frame':ff.pop()
    if kind=='phantom registry':
        assert ll,'need real link to mutate';ll[0]['registry_id']='PHANTOM'
    try:verify(ff,e,ll,v)
    except AssertionError:print('Rejected injected defect:',kind)
    else:raise AssertionError('Silent pass: '+kind)
# Rebuild packet byte equality proves determinism/idempotence after application.
paths=['frame.csv','proposals.csv','registry_proposals.csv','band_edits.csv','evidence.csv','witnesses.csv','alias_followups.csv','summary.json']
before={p:(b.HERE/p).read_bytes() for p in paths}
b.main()
assert all((b.HERE/p).read_bytes()==before[p] for p in paths)
print('PASS: independent Git frame, source yield, payload, counts, 3 defects, deterministic rebuild')
