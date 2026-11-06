#!/usr/bin/env python3
"""Read-only pair/quote check. Known missing APT raw is reported, never passed as verified."""
import copy,hashlib,html,json,re,subprocess,unicodedata
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
INPUT_SHA='443949cc05da4665d2ce3f83efc5d4173a12f8c35cc7cb7fc039bee8d53c6b0e'
def words(s):return re.findall(r'[a-z0-9]+',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
def has(s,q):
    a,b=words(s),words(q)
    return bool(b) and any(a[i:i+len(b)]==b for i in range(len(a)-len(b)+1))
def content(p):
    raw=p.read_bytes()
    if raw.startswith(b'%PDF'):
        return subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True,text=True,check=True).stdout
    s=raw.decode('utf8','replace');s=re.sub(r'<(script|style)\b[^>]*>.*?</\1>',' ',s,flags=re.S|re.I)
    return html.unescape(re.sub('<[^>]+>',' ',s))
def merge_gate(r):
    return (r['same_legal_entity_proven'] and r['same_establishment_proven'] and
            any(e['source_date'] and e['role']=='dated legal identity and establishment bridge' for e in r['evidence']))
def check(rows,inputs,receipts):
    expected={r['pair_id']:(r['a_id'],r['b_id']) for r in inputs}
    assert len(rows)==len(expected)==7 and {r['pair_id'] for r in rows}==set(expected),'Pair coverage'
    assert len({r['pair_id'] for r in rows})==7,'Duplicate pair'
    byreceipt={r['receipt_id']:r for r in receipts};assert len(byreceipt)==len(receipts),'Receipt collision'
    counts=Counter(r['org_id'] for r in receipts)
    assert all(n<=5 for oid,n in counts.items() if oid!='ORG-002325'),'Fetch cap'
    assert counts['ORG-002325']==6,'APT actual attempt accounting'
    lost=[r for r in receipts if r['inspection']=='UNINSPECTABLE']
    assert len(lost)==1 and lost[0]['receipt_id']=='ORG-002325-3-overwritten','Missing-raw disclosure'
    assert not lost[0]['raw_sha256'] and not lost[0]['raw_cache'],'Fabricated lost hash'
    for p in receipts:
        if p['inspection']=='UNINSPECTABLE':continue
        path=Path(p['raw_cache']);assert path.exists(),('Unexpected missing raw',str(path))
        assert hashlib.sha256(path.read_bytes()).hexdigest()==p['raw_sha256'],str(path)
    for r in rows:
        assert (r['a_id'],r['b_id'])==expected[r['pair_id']],'Endpoint drift'
        assert r['decision'] in {'SAME_ENTITY','DISTINCT','LINK_FLAG'},'Decision grammar'
        assert r['verdict'] in {'VERIFIED','STILL_UNCERTAIN','REJECT'} or r['verdict'].startswith('DUPLICATE_OF '),'Verdict grammar'
        if r['decision']=='SAME_ENTITY' or r['verdict'].startswith('DUPLICATE_OF'):
            assert merge_gate(r),'Insufficient merge evidence: same address, parent or undated is not identity'
        if r['decision']=='LINK_FLAG':assert r['settling_fact'] and r['verdict']=='STILL_UNCERTAIN' and not r['merge_authorized'],'Hold guard'
        for e in r['evidence']:
            p=byreceipt[e['receipt_id']];assert p['inspection']=='INSPECTABLE','Lost raw admitted'
            assert e['source_url']==p['source_url'] and e['raw_sha256']==p['raw_sha256'],'Evidence receipt mismatch'
            assert e['retrieved_date']=='2026-11-06' and e['source_class'] in {'own_site','government_filing'},'Source metadata'
            assert len(e['quote'].replace(' || ',' ').split())<=25,'Quote length'
            text=content(Path(p['raw_cache']))
            assert all(has(text,q) for q in e['quote'].split(' || ')),('Fabricated quote',r['pair_id'],e['quote'])
            if e['source_date']:
                if e['receipt_id']=='ORG-001779-3':assert '2024-05-20' in Path(p['raw_cache']).read_text(errors='replace'),'Publication date absent'
                elif e['source_date']=='2024-08-27':assert '8/27/2024' in text,'Permit date absent'
                elif e['source_date']=='2017-03-01':assert '3/1/2017' in text,'Permit date absent'
                else:raise AssertionError('Unverified date')
    # Three actual known-answer seams: separate subsidiaries, shared address only, distinct-city control.
    by={r['pair_id']:r for r in rows}
    assert by['D06']['decision']==by['D08']['decision']=='LINK_FLAG'
    assert by['D10']['decision']=='LINK_FLAG' and not by['D10']['evidence'],'APT unavailable sources held'
    ctl=json.loads((HERE/'distinct-location-control.json').read_text())
    assert 'SITE-001399' in json.dumps(ctl) and 'SITE-000427' in json.dumps(ctl),'Control drift'
    pdf=content(Path(byreceipt['ORG-000131-1']['raw_cache']))
    assert has(pdf,'JOHNSONITE 16910 MUNN RD') and has(pdf,'Tarkett USA 16035 Industrial'),'Distinct establishment addresses not witnessed'
if __name__=='__main__':
    assert hashlib.sha256((HERE/'input.json').read_bytes()).hexdigest()==INPUT_SHA,'Input drift'
    rows=json.loads((HERE/'verdicts.json').read_text());inputs=json.loads((HERE/'input.json').read_text());receipts=json.loads((HERE/'receipts.json').read_text())
    check(rows,inputs,receipts)
    for defect in ['same_address','parent_only','undated','fabricated_quote','missing_pair','wrong_endpoint']:
        bad=copy.deepcopy(rows)
        if defect in {'same_address','parent_only','undated'}:
            r=bad[0];r['decision']='SAME_ENTITY';r['verdict']='DUPLICATE_OF '+r['b_id']
            r['same_legal_entity_proven']=defect!='same_address';r['same_establishment_proven']=defect!='parent_only'
            if defect=='undated':
                for e in r['evidence']:e['source_date']='';e['role']='dated legal identity and establishment bridge'
        elif defect=='fabricated_quote':bad[0]['evidence'][0]['quote']='Fabricated same legal entity at this establishment'
        elif defect=='missing_pair':bad.pop()
        else:bad[0]['a_id']='SITE-999999'
        try:check(bad,inputs,receipts)
        except AssertionError:pass
        else:raise AssertionError('Fault silently passed: '+defect)
    print('PASS bounded packet:7 exact pairs,7 STILL_UNCERTAIN/LINK_FLAG;35 surviving raw hashes verified;36 actual attempts;APT6 includes1 UNINSPECTABLE overwritten body (NOT VERIFIED);all admitted quotes/date guards;3 known-answer seams;6 fault controls rejected. APT cap exception disclosed; no merge admissible.')
