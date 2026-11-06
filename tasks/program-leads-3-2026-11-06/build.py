"""Apply L13B frozen packets, preflight every collision before writes, regenerate rollups."""
import argparse, csv, io, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'scripts'))
from shard_io import append_sorted


def read(path):
    with open(path,newline='') as f:return list(csv.DictReader(f))


def apply(data):
    tables={'programs.csv':'program_id','ecosystem.csv':'org_id','evidence_programs.csv':'evidence_id','evidence_ecosystem.csv':'evidence_id'}
    packets={f:read(HERE/f) for f in tables}
    for f,rows in packets.items():
        key=tables[f]
        assert len({r[key] for r in rows})==len(rows),f'duplicate packet id {f}'
        for r in rows:
            low,high=(301,499) if key=='program_id' else (13000,13199) if key=='org_id' else (285010,289999)
            assert low<=int(r[key].split('-')[1])<=high,r[key]
    packet_eids=[r['evidence_id'] for f,rows in packets.items() if tables[f]=='evidence_id' for r in rows]
    assert len(packet_eids)==len(set(packet_eids)), 'cross-packet evidence ID collision'
    pending={}
    for f,key in tables.items():
        old={r[key]:r for r in read(data/f)}
        for r in packets[f]:
            assert r[key] not in old or old[r[key]]==r,f'ID collision/drift {r[key]}'
        pending[f]=[r for r in packets[f] if r[key] not in old]
        others=list(data.glob('organizations_*.csv'))+[data/'ecosystem.csv'] if key=='org_id' else list(data.glob('evidence*.csv')) if key=='evidence_id' else []
        for path in others:
            if path.name==f or path.name.endswith('_all.csv'):continue
            ids={r[key] for r in read(path)}
            assert not ids.intersection(r[key] for r in packets[f]),f'cross-table ID collision {path.name}'
    programs=read(data/'programs.csv')+pending['programs.csv']
    eco=read(data/'ecosystem.csv')+pending['ecosystem.csv']
    owners={r['org_id'] for r in eco}|{r['org_id'] for p in data.glob('organizations_*.csv') if not p.name.endswith('_all.csv') for r in read(p)}
    assert all(p['institution_org_id'] in owners for p in packets['programs.csv']), 'unheld institution'
    precision={v:i for i,v in enumerate(('degree','center','certificate','apprenticeship','training','lab_facility','course'))}
    for r in eco:
        if r['org_id'] not in {p['institution_org_id'] for p in packets['programs.csv']}:continue
        linked=sorted((p for p in programs if p['institution_org_id']==r['org_id'] and p['status']!='tombstoned'),key=lambda p:(precision[p['program_type']],p['program_name'].strip().lower()))
        r['polymer_program_name']='; '.join(p['program_name'].strip() for p in linked)
        r['polymer_program_url']=linked[0]['url'].strip()
    for f,key in tables.items():
        if f!='ecosystem.csv' and pending[f]:append_sorted(data/f,pending[f],key)
    # append_sorted also owns the header/order rules for newly created institutions.
    if pending['ecosystem.csv']:append_sorted(data/'ecosystem.csv',pending['ecosystem.csv'],'org_id')
    buf=io.StringIO();w=csv.DictWriter(buf,fieldnames=list(eco[0]),lineterminator='\n');w.writeheader();w.writerows(sorted(eco,key=lambda r:r['org_id']))
    (data/'ecosystem.csv').write_text(buf.getvalue())
    print('L13B apply:',{f:len(rs) for f,rs in pending.items()})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data-dir',type=Path,default=HERE.parents[1]/'data');apply(p.parse_args().data_dir)
