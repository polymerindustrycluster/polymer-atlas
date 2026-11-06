"""Apply frozen completions edits; every preimage and evidence collision checked before writes."""
import argparse,csv,io,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'scripts'))
from shard_io import append_sorted


def read(path):
    with open(path,newline='') as f:return list(csv.DictReader(f))


def apply(data):
    rows=read(data/'programs.csv');lookup={r['program_id']:r for r in rows};edits=read(HERE/'edits.csv')
    parents={r['org_id']:r for r in read(data/'ecosystem.csv')}
    for j in read(HERE/'joins.csv'):
        r=lookup[j['program_id']]
        assert all(r[k]==j[k] for k in ('institution_org_id','program_type','cip_code','level')),f"join conflict {j['program_id']}"
        assert parents[r['institution_org_id']]['ipeds_unitid']==j['ipeds_unitid'],f"UNITID conflict {j['program_id']}"
    assert len({(r['program_id'],r['column']) for r in edits})==len(edits)
    for e in edits:
        assert e['column'] in {'latest_completions','completions_year','last_year_awarded','sources','notes'}
        assert lookup[e['program_id']][e['column']] in (e['old_value'],e['new_value']),f"preimage conflict {e['program_id']} {e['column']}"
    evidence=read(HERE/'evidence_programs.csv');target={r['evidence_id']:r for r in read(data/'evidence_programs.csv')}
    assert len({r['evidence_id'] for r in evidence})==len(evidence)
    for r in evidence:
        assert 285100<=int(r['evidence_id'][4:])<=289999
        assert r['evidence_id'] not in target or target[r['evidence_id']]==r,f"evidence conflict {r['evidence_id']}"
    ids={r['evidence_id'] for r in evidence}
    for p in data.glob('evidence*.csv'):
        if p.name!='evidence_programs.csv':assert not ids.intersection(r['evidence_id'] for r in read(p)),f'wrong-shard evidence collision {p}'
    for e in edits:lookup[e['program_id']][e['column']]=e['new_value']
    buf=io.StringIO();w=csv.DictWriter(buf,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    new=[r for r in evidence if r['evidence_id'] not in target]
    if new:append_sorted(data/'evidence_programs.csv',new,'evidence_id')
    (data/'programs.csv').write_text(buf.getvalue())
    print('Completions apply:',len(edits),'declared cells;',len(new),'new evidence rows')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data-dir',type=Path,default=HERE.parents[1]/'data');apply(p.parse_args().data_dir)
