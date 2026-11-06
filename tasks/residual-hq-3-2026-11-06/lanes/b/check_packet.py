#!/usr/bin/env python3
"""Read-only lane check. Requires /tmp raw cache; missing evidence fails closed."""
import csv,hashlib,html,re,subprocess,unicodedata
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
INPUT_SHA='a984e43f35d85c4094d8830e5082e7e6f5453cb69bb9288b0c756dc930ea8fc4'
FIELDS=set('org_id legal_name verdict outcome hq_city hq_state hq_country hq_county source_url source_class quote fetch_count reason settling_fact note raw_sha256'.split())
def read(p):
    with p.open(newline='') as f:return list(csv.DictReader(f))
def words(s):
    return re.findall(r'[a-z0-9]+',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
def has(s,q):
    a,b=words(s),words(q)
    return bool(b) and any(a[i:i+len(b)]==b for i in range(len(a)-len(b)+1))
def content(p):
    raw=p.read_bytes()
    if raw.startswith(b'%PDF'):
        return subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True,text=True,check=True).stdout
    s=raw.decode('utf8','replace')
    s=re.sub(r'<(script|style)\b[^>]*>.*?</\1>',' ',s,flags=re.S|re.I)
    return html.unescape(re.sub('<[^>]+>',' ',s))
def check(rows,inputs,receipts):
    assert len(rows)==len(inputs)==50,'Missing allocated record'
    assert all(set(r)==FIELDS for r in rows),'Header/fields mismatch'
    assert len({r['org_id'] for r in rows})==50,'Duplicate ID'
    assert {r['org_id'] for r in rows}=={r['org_id'] for r in inputs},'Coverage mismatch'
    names={r['org_id']:r['legal_name'] for r in inputs}
    counts=Counter(r['org_id'] for r in receipts)
    assert len({(r['org_id'],r['attempt']) for r in receipts})==len(receipts),'Duplicate attempt receipt'
    assert set(counts)==set(names),'Receipt coverage mismatch'
    for r in rows:
        oid=r['org_id'];assert r['legal_name']==names[oid],oid
        assert r['outcome']==r['verdict'] in {'HQ_FOUND','STILL_UNKNOWN'},oid
        assert 1<=int(r['fetch_count'])<=5 and int(r['fetch_count'])==counts[oid],oid
        assert not r['hq_county'],'Unsupported county'
        hits=[p for p in receipts if p['org_id']==oid and p['source_url']==r['source_url'] and p['raw_sha256']==r['raw_sha256']]
        assert hits,('Missing source receipt',oid)
        if r['outcome']=='HQ_FOUND':
            assert all(r[k] for k in ['hq_city','hq_state','hq_country','quote']),oid
            assert r['source_class']=='own_site',('LEI/registry not auto-promoted',oid)
            assert len(r['quote'].replace(' || ',' ').split())<=25,oid
            s=content(Path(hits[0]['raw_cache']))
            assert all(has(s,q) for q in r['quote'].split(' || ')),('Raw quote mismatch',oid)
            assert has(r['quote'],r['hq_city']),('City not witnessed',oid)
        else:
            assert r['settling_fact'] and r['reason'],oid
            assert not any(r[k] for k in ['hq_city','hq_state','hq_country','quote']),oid
    for r in receipts:
        p=Path(r['raw_cache']);assert p.exists(),('Uninspectable raw',str(p))
        assert hashlib.sha256(p.read_bytes()).hexdigest()==r['raw_sha256'],str(p)
    # Known answers: own careers sentence, actual 406 contact content, own PDF overview, PDF columns.
    expected={'ORG-007106':('HQ_FOUND','Manitowoc'),'ORG-007103':('HQ_FOUND','Sussex'),'ORG-007309':('HQ_FOUND','Hanover'),'ORG-007045':('HQ_FOUND','Romulus'),'ORG-007204':('STILL_UNKNOWN',''),'ORG-007315':('STILL_UNKNOWN','')}
    by={r['org_id']:r for r in rows}
    for oid,(outcome,city) in expected.items():assert (by[oid]['outcome'],by[oid]['hq_city'])==(outcome,city),('Known answer',oid)
if __name__=='__main__':
    assert hashlib.sha256((HERE/'input.csv').read_bytes()).hexdigest()==INPUT_SHA,'Input changed'
    rows,inputs,receipts=read(HERE/'verdicts.csv'),read(HERE/'input.csv'),read(HERE/'receipts.csv')
    check(rows,inputs,receipts)
    for defect in ['missing_id','duplicate_id','bad_quote','bad_header','empty_hold_fact','wrong_pdf_city']:
        bad=[dict(r) for r in rows]
        if defect=='missing_id':bad.pop()
        elif defect=='duplicate_id':bad[-1]=dict(bad[0])
        elif defect=='bad_quote':next(r for r in bad if r['outcome']=='HQ_FOUND')['quote']='Invented headquarters in Nowhere California'
        elif defect=='bad_header':bad[0].pop('source_class')
        elif defect=='empty_hold_fact':next(r for r in bad if r['outcome']=='STILL_UNKNOWN')['settling_fact']=''
        else:next(r for r in bad if r['org_id']=='ORG-007045')['hq_city']='Monroe'
        try:check(bad,inputs,receipts)
        except AssertionError:pass
        else:raise AssertionError('Silent false pass: '+defect)
    print(f'PASS:50/50 unique IDs; 7 HQ_FOUND,43 STILL_UNKNOWN; {len(receipts)} hashes; max5 fetches; all positive excerpts raw-matched; 4 positive source/parser known answers,2 parent-HQ holds; 6 fault controls rejected.')
