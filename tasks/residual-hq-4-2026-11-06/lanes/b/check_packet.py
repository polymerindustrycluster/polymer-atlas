#!/usr/bin/env python3
"""Read-only packet check; missing raw evidence fails closed."""
import csv,hashlib,html,re,subprocess,unicodedata
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
EXCLUDED={'ORG-009017','ORG-009026'}
INPUT_SHA='1715fc1c9a2afbc0787e63c778f3cee50b52eb7039c2689209e33c24a7ac1c37'
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
    assert len(rows)==len(inputs)==24,'Missing allocated record'
    assert all(set(r)==FIELDS for r in rows),'Header mismatch'
    assert len({r['org_id'] for r in rows})==24,'Duplicate ID'
    names={r['org_id']:r['legal_name'] for r in inputs}
    assert {r['org_id'] for r in rows}==set(names),'Coverage mismatch'
    counts=Counter(r['org_id'] for r in receipts)
    assert set(counts)==set(names)-EXCLUDED,'Eligible receipt coverage mismatch'
    assert len({(r['org_id'],r['attempt']) for r in receipts})==len(receipts),'Duplicate receipt attempt'
    for r in rows:
        oid=r['org_id'];assert r['legal_name']==names[oid],oid
        assert r['outcome']==r['verdict'] in {'HQ_FOUND','STILL_UNKNOWN'},oid
        assert not r['hq_county'],'Unsupported county'
        if oid in EXCLUDED:
            assert int(r['fetch_count'])==counts[oid]==0,('Excluded ID researched',oid)
            assert r['outcome']=='STILL_UNKNOWN' and r['settling_fact'] and 'Ownership hold' in r['reason'],oid
            assert not any(r[k] for k in ['hq_city','hq_state','hq_country','source_url','source_class','quote','raw_sha256']),oid
            continue
        assert 1<=int(r['fetch_count'])<=5 and int(r['fetch_count'])==counts[oid],oid
        hits=[p for p in receipts if p['org_id']==oid and p['source_url']==r['source_url'] and p['raw_sha256']==r['raw_sha256']]
        assert hits,('Missing source receipt',oid)
        if r['outcome']=='HQ_FOUND':
            assert all(r[k] for k in ['hq_city','hq_state','hq_country','quote']),oid
            assert r['source_class']=='own_site',oid
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
    known={'ORG-010003':('HQ_FOUND','Pomona'),'ORG-009034':('HQ_FOUND','Lafayette'),'ORG-010007':('HQ_FOUND','Lodi'),'ORG-010700':('STILL_UNKNOWN','')}
    by={r['org_id']:r for r in rows}
    for oid,answer in known.items():assert (by[oid]['outcome'],by[oid]['hq_city'])==answer,('Known answer',oid)
    alias=next(r for r in receipts if r['org_id']=='ORG-009031' and r['attempt']=='4')
    assert has(content(Path(alias['raw_cache'])),'SUN DRILLING PRODUCTS CORP. d/b/a SUN SPECIALTY PRODUCTS'),'Missing Sun identity bridge'
if __name__=='__main__':
    assert hashlib.sha256((HERE/'input.csv').read_bytes()).hexdigest()==INPUT_SHA,'Input changed'
    rows,inputs,receipts=read(HERE/'verdicts.csv'),read(HERE/'input.csv'),read(HERE/'receipts.csv')
    check(rows,inputs,receipts)
    for defect in ['missing_id','duplicate_id','bad_quote','bad_header','empty_hold_fact','excluded_fetch']:
        bad=[dict(r) for r in rows]
        if defect=='missing_id':bad.pop()
        elif defect=='duplicate_id':bad[-1]=dict(bad[0])
        elif defect=='bad_quote':next(r for r in bad if r['outcome']=='HQ_FOUND')['quote']='Invented headquarters in Nowhere California'
        elif defect=='bad_header':bad[0].pop('source_class')
        elif defect=='empty_hold_fact':next(r for r in bad if r['outcome']=='STILL_UNKNOWN')['settling_fact']=''
        else:next(r for r in bad if r['org_id']=='ORG-009017')['fetch_count']='1'
        try:check(bad,inputs,receipts)
        except AssertionError:pass
        else:raise AssertionError('Silent false pass: '+defect)
    assert Counter(r['outcome'] for r in rows)=={'HQ_FOUND':6,'STILL_UNKNOWN':18}
    print(f'PASS:24/24 unique IDs;6 HQ_FOUND;18 STILL_UNKNOWN incl2 zero-fetch ownership holds;{len(receipts)} raw hashes;max5 eligible fetches;all6 quotes;3 positive known answers+Sun PDF identity+parent HQ hold;6 fault controls rejected.')
