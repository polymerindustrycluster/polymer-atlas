"""Apply only blank LinkedIn navigation cells after complete packet/identity preflight."""
import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit
import discover as d

HERE, ROOT = d.HERE, d.ROOT
sys.path.insert(0,str(ROOT/'scripts'))
from atlas import name_key

IDENTITY = ['legal_name','trade_names','website','status','parent_org_id','successor_org_id']


def read(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))


def identity(row, url):
    slug = unquote(urlsplit(url).path.split('/')[2]).replace('-',' ')
    key = name_key(slug).replace(' ','')
    aliases = [row['legal_name'], *row['trade_names'].split(';')]
    return len(key)>=3 and any(name_key(n).replace(' ','')==key for n in aliases if n.strip())


def plan(data, proposals, inputs, rawchecks):
    frozen = {r['org_id']:r for r in inputs}
    assert len(frozen)==len(inputs), 'duplicate frozen org'
    assert len({r['org_id'] for r in proposals})==len(proposals), 'duplicate proposal'
    checks = {r['org_id']:r for r in rawchecks}
    assert len(checks)==len(rawchecks)==len(proposals), 'raw-check census differs'
    tables, held, owners = {}, {}, {}
    for p in [data/'ecosystem.csv', *sorted(data.glob('organizations_*.csv'))]:
        if p.name.endswith('_all.csv'):
            continue
        rows=read(p)
        if p.name!='ecosystem.csv':
            tables[p]=rows
            for row in rows:
                assert row['org_id'] not in held, 'cross-shard duplicate org'
                held[row['org_id']]=(p,row)
        for row in rows:
            if row.get('website'):
                u=row['website'] if '://' in row['website'] else 'https://'+row['website']
                owners.setdefault(d.domain(u),set()).add(row['org_id'])
    changes={}
    for proposal in proposals:
        oid=proposal['org_id']
        assert oid in held and oid in frozen, 'unheld or unfrozen org'
        p,row=held[oid]
        original=frozen[oid]
        assert all(row[k]==original[k] for k in IDENTITY), 'entity/website preimage changed'
        value=proposal['linkedin_url']
        assert original['status']=='active' and not original['linkedin_url'], 'not a blank active frozen row'
        assert d.canonical(value)==value and d.canonical(proposal['href'])==value, 'invalid company navigation URL'
        assert identity(original,value), 'company slug does not match held name/alias'
        own=original['website'] if '://' in original['website'] else 'https://'+original['website']
        assert owners[d.domain(own)]=={oid}, 'ambiguous shared website domain'
        assert proposal['source_url']==original['website'], 'source not held website'
        assert d.own_url(proposal['final_url'],d.domain(own)), 'source redirected outside own domain'
        witness=checks[oid]
        assert witness['result']=='PASS', 'raw navigation witness failed'
        for key in ['source_url','final_url','href','linkedin_url','location']:
            assert witness[key]==proposal[key], 'raw witness/proposal differs'
        assert re.fullmatch('[a-f0-9]{64}',witness['raw_sha256']), 'missing raw digest'
        assert re.search('header|footer',proposal['location'],re.I), 'missing header/footer witness'
        assert row['linkedin_url'] in {'',value}, 'existing navigation conflicts'
        if not row['linkedin_url']:
            changes[oid]=(p,row,value)
    for _,row,value in changes.values():
        row['linkedin_url']=value
    encoded={}
    for p in {p for p,_,_ in changes.values()}:
        buf=io.StringIO()
        w=csv.DictWriter(buf,fieldnames=list(tables[p][0]),lineterminator='\n')
        w.writeheader();w.writerows(tables[p])
        encoded[p]=buf.getvalue().encode()
    return encoded,len(changes)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--data-dir',type=Path,default=ROOT/'data')
    args=parser.parse_args()
    payloads,count=plan(args.data_dir,read(HERE/'proposals.csv'),read(HERE/'inputs.csv'),read(HERE/'rawcheck.csv'))
    if args.apply:
        for path,payload in payloads.items():
            path.write_bytes(payload)
    print('PASS complete preflight;',len(read(HERE/'proposals.csv')),'verified navigation proposals;',count,'blank cells to fill;',len(payloads),'shards; zero EVD/other fields')

if __name__=='__main__':
    main()
