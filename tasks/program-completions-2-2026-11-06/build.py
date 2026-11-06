"""Apply frozen completions edits; every preimage and evidence collision checked before writes."""
import argparse,csv,hashlib,io,json,sys
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'scripts'))
from shard_io import append_sorted
from build_ipeds_completions import DETAIL_LEVELS,LEVEL_MAP


def read(path):
    with open(path,newline='') as f:return list(csv.DictReader(f))


def activity_detail(join,total,caveat):
    return f"latest_completions {total}; completions_year 2024; last_year_awarded 2024 (last observed, not final). UNITID {join['ipeds_unitid']} x CIP {join['cip_code']}; MAJORNUM=1; sum CTOTALT across detail AWLEVELs, total {total}; all positive award levels covered by held level set {join['level']}. {caveat}"


def verified_numeric(joins,evidence):
    source=json.loads((HERE/'source.json').read_text())
    assert hashlib.sha256((HERE/'raw_2024.csv').read_bytes()).hexdigest()==source['raw_subset_sha256'],'raw subset hash conflict'
    raw=read(HERE/'raw_2024.csv');totals=Counter();perlevel=Counter()
    assert len(raw)==len({(r['unitid'],r['cip_code'],r['award_level_code'],r['completions_year']) for r in raw})==104
    for r in raw:
        assert r['completions_year']=='2024' and r['first_major_flag']=='R' and int(r['award_level_code']) in DETAIL_LEVELS
        value=int(r['completions_first_major']);assert value>=0
        totals[r['unitid'],r['cip_code']]+=value
        perlevel[r['unitid'],r['cip_code'],int(r['award_level_code'])]+=value
    proposals=read(HERE/'input.csv');numeric=[p for p in proposals if p['prop_latest_completions']]
    assert len(numeric)==44 and len({(p['ipeds_unitid'],p['cip_code']) for p in numeric})==len(totals)==43
    for p in numeric:assert totals[p['ipeds_unitid'],p['cip_code']]==int(p['prop_latest_completions']), 'proposal/source count conflict'
    inputs={p['program_id']:p for p in proposals};expected={}
    assert len(joins)==len({j['program_id'] for j in joins})==len({(j['ipeds_unitid'],j['cip_code']) for j in joins})==34
    for j in joins:
        assert j['program_type']=='degree'
        labels=j['level'].split(';');assert all(label in LEVEL_MAP for label in labels)
        levels={level for label in labels for level in LEVEL_MAP[label]}
        total=totals[j['ipeds_unitid'],j['cip_code']]
        assert total==sum(perlevel[j['ipeds_unitid'],j['cip_code'],level] for level in levels)>0,'source award-level conflict'
        expected[j['program_id']]={'latest_completions':str(total),'completions_year':'2024','last_year_awarded':'2024'}
        matched=[e for e in evidence if e['record_id']==j['program_id']]
        assert len(matched)==1,'source/evidence record coverage conflict'
        e=matched[0]
        assert e['claim_detail']==activity_detail(j,total,inputs[j['program_id']]['cip_scope_caveat']), 'source/evidence numeric conflict'
        assert (e['record_table'],e['claim_type'],e['source_class'],e['source_ref'],e['observed_date'],e['tier_effect'])==('programs','activity','registry',source['url'],source['fetched'],'supports_C'), 'source/evidence witness conflict'
    assert len(evidence)==len(expected)
    return expected


def apply(data):
    rows=read(data/'programs.csv');lookup={r['program_id']:r for r in rows};edits=read(HERE/'edits.csv')
    parents={r['org_id']:r for r in read(data/'ecosystem.csv')}
    joins=read(HERE/'joins.csv');evidence=read(HERE/'evidence_programs.csv')
    numeric=verified_numeric(joins,evidence)
    for j in joins:
        r=lookup[j['program_id']]
        assert all(r[k]==j[k] for k in ('institution_org_id','program_type','cip_code','level')),f"join conflict {j['program_id']}"
        assert parents[r['institution_org_id']]['ipeds_unitid']==j['ipeds_unitid'],f"UNITID conflict {j['program_id']}"
    assert len({(r['program_id'],r['column']) for r in edits})==len(edits)
    for e in edits:
        assert e['program_id'] in numeric, 'unverified edit target'
        if e['column'] in numeric[e['program_id']]:
            assert e['new_value']==numeric[e['program_id']][e['column']],f"source-derived numeric conflict {e['program_id']} {e['column']}"
        assert e['column'] in {'latest_completions','completions_year','last_year_awarded','sources','notes'}
        assert lookup[e['program_id']][e['column']] in (e['old_value'],e['new_value']),f"preimage conflict {e['program_id']} {e['column']}"
    for pid,values in numeric.items():
        for column,expected in values.items():
            projected=next((e['new_value'] for e in edits if e['program_id']==pid and e['column']==column),lookup[pid][column])
            assert projected==expected,f'source-derived final value conflict {pid} {column}'
    target={r['evidence_id']:r for r in read(data/'evidence_programs.csv')}
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
