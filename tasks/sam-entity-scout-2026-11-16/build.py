"""Build a filtered discovery-only index and all-shard match frame offline."""
import csv, hashlib, json, re, sqlite3, sys, zipfile
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CACHE=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/sam-entity-scout')
sys.path.insert(0,str(ROOT/'scripts'))
from atlas import name_key,street_key,site_name_key,org_name_fields
from regions import PIC18


def excluded(r):
    assert len(r)==142
    date=r[9].strip()
    # shortcut: missing/malformed dates are held, never accepted as post-cutoff.
    if not re.fullmatch(r'\d{8}',date): return (True, False)
    return ('D&B' in r[121].upper() or r[23].upper()=='Y', date<'20220404')


def build():
    db=sqlite3.connect(CACHE/'sam.sqlite')
    db.execute('pragma journal_mode=off')
    if not db.execute("select count(*) from sqlite_master where name='sam'").fetchone()[0]:
        db.execute('create table sam(uei text,name,dba,street,city,state,zip,naics,listed_naics,cage,status,updated,activation,expiration,evs,nk,dk,sk,source_row integer primary key)')
        counts=Counter();evs=Counter();batch=[];markers=[]
        with zipfile.ZipFile(CACHE/'inner.zip') as z,z.open(z.namelist()[0]) as f:
            for line in f:
                r=line.decode('utf-8').rstrip('\r\n').split('|')
                if len(r)==1:
                    markers.append(r[0]);continue
                a,b=excluded(r);counts['input_records']+=1;evs[r[121]]+=1
                counts['missing_or_invalid_date']+=int(not bool(re.fullmatch(r'\d{8}',r[9].strip())))
                counts['drop_db_source']+=int('D&B' in r[121].upper() or r[23].upper()=='Y');counts['drop_legacy_date']+=int(b);counts['drop_overlap']+=int(a and b)
                if a or b:counts['dropped_union']+=1;continue
                row=[r[i].strip() for i in [0,11,12,15,17,18,19,32,34,3,5,9,10,8,121]]
                row += [name_key(row[1]),name_key(row[2]),street_key(row[3]),counts['input_records']]
                batch.append(row)
                if len(batch)==2000:db.executemany('insert into sam values('+','.join('?'*19)+')',batch);batch=[]
        db.executemany('insert into sam values('+','.join('?'*19)+')',batch)
        assert len(markers)==2 and markers[0].startswith('BOF ') and markers[1].startswith('EOF ')
        declared=int(markers[0].split()[5]);assert declared==int(markers[1].split()[5])==counts['input_records']
        counts['declared_record_count']=declared
        counts['indexed_records']=db.execute('select count(*) from sam').fetchone()[0]
        assert counts['input_records']==counts['indexed_records']+counts['dropped_union']
        db.execute('create table receipt(payload text)')
        db.execute('insert into receipt values(?)',(json.dumps(dict(counts=counts,evs_sources=evs)),))
        for col in ['nk','dk','sk']:db.execute('create index sam_'+col+' on sam('+col+')')
        db.commit()
    receipt=json.loads(db.execute('select payload from receipt').fetchone()[0])
    orgs={}
    for p in sorted((ROOT/'data').glob('organizations_*.csv')):
        for r in csv.DictReader(p.open()):
            assert r['org_id'] not in orgs
            orgs[r['org_id']]=r
    operators=dict(orgs)
    for r in csv.DictReader((ROOT/'data/ecosystem.csv').open()):operators[r['org_id']]=r
    sites={}
    for p in sorted((ROOT/'data').glob('sites_*.csv')):
        for r in csv.DictReader(p.open()):
            assert r['site_id'] not in sites
            sites[r['site_id']]=r
    db.executescript('drop table if exists matches; create table matches(record_id,uei,class,primary key(record_id,uei));')
    for rid,r in list(orgs.items())+list(sites.items()):
        issite=rid.startswith('SITE-');o=operators[r['org_id']] if issite else r
        names={name_key(n) for _,n in org_name_fields(o)}
        if issite:names.add(site_name_key(r['site_name'],r['city']))
        names.discard('');city=r['city'] if issite else r['hq_city'];state=r['state'] if issite else r['hq_state']
        sk=street_key(r.get('street_address','')) if issite else ''
        candidates=set()
        for n in names:
            for s in db.execute('select uei,nk,dk,sk,city,state from sam where nk=? or dk=?',(n,n)):candidates.add(s)
        if sk:
            for s in db.execute('select uei,nk,dk,sk,city,state from sam where sk=? and state=?',(sk,state)):candidates.add(s)
        for uei,nk,dk,ssk,scity,sstate in candidates:
            nm=bool(names & {nk,dk});street=bool(sk and sk==ssk and state==sstate)
            cls='name+street' if nm and street else 'name+city' if nm and city.casefold()==scity.casefold() and state==sstate else 'name-only' if nm else 'street-only different-name'
            db.execute("insert into matches values(?,?,?) on conflict(record_id,uei) do update set class=excluded.class where (case excluded.class when 'name+street' then 0 when 'name+city' then 1 when 'name-only' then 2 else 3 end)<(case matches.class when 'name+street' then 0 when 'name+city' then 1 when 'name-only' then 2 else 3 end)",(rid,uei,cls))
    db.execute('create index if not exists matches_uei on matches(uei)')
    db.commit()
    receipt.update(route='FILTERED_LEADS_ONLY',authenticated_requests=2,download_requests=1,
      extract_file='SAM_PUBLIC_MONTHLY_V2_20261101.ZIP',extract_date='2026-11-01',
      extract_sha256=json.loads((CACHE/'request2.json').read_text())['sha256'],
      atlas_organizations=len(orgs),atlas_sites=len(sites),
      match_pairs_by_class=dict(db.execute('select class,count(*) from matches group by class')),
      matched_atlas_records=db.execute('select count(distinct record_id) from matches').fetchone()[0])
    missing={rid for rid,r in sites.items() if r['state']=='OH' and r['county'] in PIC18 and not r['street_address'].strip()}
    candidates={rid for rid, in db.execute("select distinct record_id from matches join sam using(uei) where class='name+city' and street<>''") if rid in missing}
    receipt.update(streetless_pic18_sites=len(missing),streetless_pic18_address_lead_sites=len(candidates))
    samples=[]
    for cls in sorted(receipt['match_pairs_by_class']):
        pairs=list(db.execute('select record_id,uei from matches where class=?',(cls,)))
        pairs.sort(key=lambda x:hashlib.sha256(('20261116|'+cls+'|'+x[0]+'|'+x[1]).encode()).hexdigest())
        for rid,uei in pairs[:20]:samples.append(dict(record_id=rid,uei=uei,match_class=cls,verdict='UNREVIEWED',reason=''))
    samplefile=HERE/'sample.csv'
    if not samplefile.exists():
        with samplefile.open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(samples[0]));w.writeheader();w.writerows(samples)
    receipt['sample_pairs']=len(samples)
    (HERE/'metrics.json').write_text(json.dumps(receipt,indent=2)+'\n')
    assert (CACHE/'sam.sqlite').stat().st_size<1500000000
    db.close()
    return receipt

if __name__=='__main__':
    build()
    from summarize import summarize
    summarize()
