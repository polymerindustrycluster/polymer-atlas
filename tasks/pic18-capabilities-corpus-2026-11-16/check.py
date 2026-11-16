"""Named gate: frame census, exact replay, column boundary, witnesses, mutation tests."""
import copy, hashlib, json
import build as b

def check(decisions):
    expected,caps,ev,verdicts=b.outputs(decisions)
    assert b.read(b.T/'frame.csv')==b.frame(), 'independent baseline frame differs'
    assert len(expected)==len({r['site_id'] for r in b.frame()})
    original={s['site_id']:s for s in b.base('data/sites_OH.csv')}
    current={s['site_id']:s for s in b.read(b.ROOT/'data/sites_OH.csv')}
    assert current.keys()==original.keys()
    for sid,s in current.items():
        assert s==expected.get(sid,original[sid]), ('unexpected cell',sid)
    for filename,rows,key in [('site_capabilities.csv',caps,'capability_id'),('evidence_sites_OH.csv',ev,'evidence_id')]:
        old={r[key]:r for r in b.base('data/'+filename)}
        now={r[key]:r for r in b.read(b.ROOT/'data'/filename)}
        assert all(now[k]==v for k,v in old.items())
        assert {k:v for k,v in now.items() if k not in old}=={r[key]:r for r in rows}
    assert b.read(b.T/'verdicts.csv')==verdicts
    summary=json.loads((b.T/'summary.json').read_text())
    observed=dict(frame_sites=len(expected),accepted_sites=len({d['site_id'] for d in decisions}),applied_sites=len({r['site_id'] for r in caps}|{r['record_id'] for r in ev}),held_sites=len({v['site_id'] for v in verdicts if v['verdict']=='STILL_UNCERTAIN'}),term_decisions=len(decisions),capability_rows=len(caps),evidence_rows=len(ev),changed_sites=sum(s!=original[sid] for sid,s in expected.items()))
    assert summary==observed
    return observed
if __name__=='__main__':
    decisions=b.read(b.T/'decisions.csv');print(check(decisions))
    for field,value in [('quote','INJECTED UNSUPPORTED QUOTE'),('term','injected_invalid_term'),('grain_quote','INJECTED WRONG PLANT')]:
        bad=copy.deepcopy(decisions);bad[0][field]=value
        try:check(bad)
        except AssertionError:print('detected injected',field)
        else:raise AssertionError('mutation survived: '+field)
    paths=[b.ROOT/'data'/n for n in ('sites_OH.csv','site_capabilities.csv','evidence_sites_OH.csv')]
    before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
    b.main()
    assert before==[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths], 'non-idempotent'
    print('PASS: CAP corpus replay / 3 mutations / idempotence')
