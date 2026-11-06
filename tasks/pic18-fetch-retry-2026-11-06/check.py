"""Independent frame/partition/raw-binding checks and adversarial packet mutations."""
import csv,hashlib,json,subprocess,tempfile
from collections import Counter
from pathlib import Path
import build
from retry import P,ROOT,CACHE,l1,on_page,target,read,write,same_page

def check(folder=P):
    source=read(ROOT/'tasks/evidence-reverify-archive-2026-11-06/verdicts.csv');ids={r['evidence_id'] for r in source if r['judgment']=='FETCH_FAILED'};assert len(ids)==264
    inputs=read(folder/'input.csv');out=read(folder/'verdicts.csv');assert len(out)==len(inputs)==len({r['evidence_id'] for r in out})==264
    assert {r['evidence_id'] for r in inputs}=={r['evidence_id'] for r in out}==ids
    old={r['evidence_id']:r for r in inputs};canonical={r['evidence_id']:r for f in (ROOT/'data').glob('evidence_*.csv') for r in read(f)}
    expected={'reverification.csv':'SUPPORTED','repair_leads.csv':'NOT_SUPPORTED','holds.csv':'HOLD'}
    for name,value in expected.items():
        rows=read(folder/name);assert len(rows)==len({r['evidence_id'] for r in rows})
        assert rows==[r for r in out if r['quote_verdict']==value],('wrong partition',name)
    assert sum(len(read(folder/name)) for name in expected)==264
    counts=Counter(r['quote_verdict'] for r in out);assert counts=={'SUPPORTED':195,'HOLD':69},counts
    assert Counter(r['hold_reason'] for r in out if r['quote_verdict']=='HOLD')=={'NO_PRESERVED_QUOTE':22,'FETCH_FAILED':27,'SOURCE_BINDING':10,'PDF_WORD_BOUNDARY_HOLD':10}
    receipts={r['receipt_path']:r for r in read(folder/'fetch_receipts.csv')}
    for r in out:
        e=canonical[r['evidence_id']];assert all(r[k]==v for k,v in e.items()),r['evidence_id']
        assert r['preserved_quote']==old[r['evidence_id']]['quote']==l1.quote(e),r['evidence_id']
        assert r['original_url']==e['source_ref'] and r['fetch_url']==target(e['source_ref'])
        fs=[]
        for path in filter(None,r['receipt_paths'].split(';')):
            proof=receipts[path];assert proof['url']==r['fetch_url'];assert build.digest(ROOT/path)==proof['receipt_sha256']
            f=json.loads((ROOT/path).read_text());fs.append(f)
            if f.get('raw_path'):assert build.digest(ROOT/f['raw_path'])==f['raw_sha256']
            if f.get('text_path'):assert build.digest(ROOT/f['text_path'])==f['text_sha256']
            if f.get('provider_response_path'):
                assert build.digest(ROOT/f['provider_response_path'])==f['provider_response_sha256']
                d=json.loads((ROOT/f['provider_response_path']).read_text());assert d['_requested_url']==r['fetch_url']
            if f['posture']=='ok':
                assert f['http_status']==200 and f.get('exit_code',0)==0 and f.get('text_path')
                assert same_page(r['fetch_url'],f['effective_source_url']),('wrong page admitted',r['evidence_id'])
                p=l1.live_posture(dict(status='ok',page=f['text_path'],attempts=[dict(route=r['fetch_url'],effective_url=f['effective_source_url'])]),r['fetch_url']);assert p=='ok'
        if r['raw_text_path']:assert build.digest(ROOT/r['raw_text_path'])==r['raw_text_sha256']
        if r['quote_verdict']=='SUPPORTED':
            assert r['lane_verdict']=='VERIFIED' and r['page_binding']=='EXACT_URL' and r['preserved_quote']
            assert on_page(r['preserved_quote'],ROOT/r['raw_text_path']) is True
            assert any(f['posture']=='ok' and f.get('text_path')==r['raw_text_path'] and f.get('text_sha256')==r['raw_text_sha256'] and f['route']==r['route'] for f in fs)
        else:
            assert r['lane_verdict']=='STILL_UNCERTAIN' and r['deciding_or_settling_fact']
            assert r['preserved_quote'] or r['hold_reason']=='NO_PRESERVED_QUOTE'
        if r['quote_verdict']=='NOT_SUPPORTED':
            assert r['preserved_quote'] and r['page_binding']=='EXACT_URL'
            assert all(on_page(r['preserved_quote'],ROOT/f['text_path']) is False for f in fs if f['posture']=='ok')
        if not r['preserved_quote']:assert r['quote_verdict']=='HOLD'
    assert len(receipts)==227
    known=json.loads((folder/'known-answers.json').read_text());assert len(known['cases'])==5 and len(known['NAS_live_known'])==3
    assert not subprocess.check_output(['git','diff','--name-only','HEAD','--','data/'],text=True).strip(),'working-tree canonical edits'
    base=subprocess.check_output(['git','merge-base','origin/main','HEAD'],text=True).strip();assert not subprocess.check_output(['git','diff','--name-only',base,'HEAD','--','data/'],text=True).strip(),'committed canonical edits'
    return dict(frozen_rows=264,supported=195,not_supported=0,holds=69,raw_receipts=227,canonical_changes=0)

def main():
    result=check();paths=[P/name for name in ['verdicts.csv','reverification.csv','repair_leads.csv','holds.csv','fetch_receipts.csv','result.json']];before={p.name:build.digest(p) for p in paths}
    subprocess.run(['python3',str(P/'build.py')],check=True);assert before=={p.name:build.digest(p) for p in paths},'packet rebuild not byte-identical'
    with tempfile.TemporaryDirectory(prefix='l6-fetchretry-negative-') as tmp:
        d=Path(tmp)
        for p in P.glob('*.csv'):(d/p.name).write_bytes(p.read_bytes())
        (d/'known-answers.json').write_bytes((P/'known-answers.json').read_bytes())
        def reject(name,mutate):
            path=d/name;raw=path.read_bytes();rows=read(path);mutate(rows);write(path,rows)
            try:check(d)
            except (AssertionError,KeyError):pass
            else:raise AssertionError('mutation accepted: '+name)
            path.write_bytes(raw)
        reject('verdicts.csv',lambda rows:rows.pop())
        reject('verdicts.csv',lambda rows:rows.append(dict(rows[0])))
        reject('verdicts.csv',lambda rows:rows[0].update(preserved_quote='forged quote'))
        reject('reverification.csv',lambda rows:rows[0].update(raw_text_sha256='0'*64))
        # Insert an actual still-unavailable row as a supported re-verification: partition and binding must fail.
        held=next(r for r in read(P/'holds.csv') if r['hold_reason']=='FETCH_FAILED')
        reject('reverification.csv',lambda rows:rows.append({**held,'quote_verdict':'SUPPORTED','lane_verdict':'VERIFIED'}))
        print('PASS missing/duplicate/forged quote/forged raw hash/unavailable-as-supported defects rejected')
    (P/'check-result.json').write_text(json.dumps({**result,'replay':'byte-identical','adversarial_controls':5},indent=2)+'\n')
    print('PASS264/264 exact census;195supported/0not-supported/69typedholds;227rawreceipts;no data edits')
if __name__=='__main__':main()
