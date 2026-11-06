"""Completions reconciliation and no-write failure checks, using frozen raw source subset."""
import csv,hashlib,json,shutil,tempfile
from collections import Counter,defaultdict
from pathlib import Path
from build import HERE,read,apply
from shard_io import append_sorted


def write(path,rows):
    with open(path,'w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def digest(data):return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}


def main():
    inputs=read(HERE/'input.csv');verdicts=read(HERE/'verdicts.csv');edits=read(HERE/'edits.csv');evidence=read(HERE/'evidence_programs.csv');raw=read(HERE/'raw_2024.csv')
    assert inputs==read(HERE.parent/'ipeds-completions-2026-11-01/program_proposals.csv')
    assert len(inputs)==len(verdicts)==len({v['program_id'] for v in verdicts})==147
    assert {v['program_id'] for v in inputs}=={v['program_id'] for v in verdicts}
    assert Counter(v['verdict'] for v in verdicts)=={'VERIFIED':34,'REJECT':81,'STILL_UNCERTAIN':32}
    assert len(edits)==112 and len(evidence)==len({r['evidence_id'] for r in evidence})==34
    assert {e['program_id'] for e in edits}=={v['program_id'] for v in verdicts if v['verdict']=='VERIFIED'}=={e['record_id'] for e in evidence}
    assert Counter(e['column'] for e in edits)=={'last_year_awarded':34,'sources':34,'notes':34,'latest_completions':5,'completions_year':5}
    totals=Counter();perlevel=Counter()
    assert len(raw)==len({(r['unitid'],r['cip_code'],r['award_level_code'],r['completions_year']) for r in raw})
    for r in raw:
        totals[r['unitid'],r['cip_code']]+=int(r['completions_first_major'])
        perlevel[r['unitid'],r['cip_code'],r['award_level_code']]+=int(r['completions_first_major'])
    for p in inputs:
        if p['prop_latest_completions']:assert totals[p['ipeds_unitid'],p['cip_code']]==int(p['prop_latest_completions']),p['program_id']
    assert totals['205443','15.0607']==6 and totals['169910','15.0607']==30 and totals['235149','15.0607']==56
    assert perlevel['235149','15.0607','3']==10 and totals['235149','15.0607']!=10
    # Known mixed/identity-sensitive proposals cannot slip into application.
    applied={v['program_id'] for v in verdicts if v['verdict']=='VERIFIED'}
    assert not applied.intersection({'PROG-000001','PROG-000003','PROG-000038','PROG-000057','PROG-000075','PROG-000076','PROG-000079','PROG-000084','PROG-000100','PROG-000143'})
    canonical=HERE.parents[1]/'data'
    with tempfile.TemporaryDirectory() as tmp:
        data=Path(tmp)/'data';shutil.copytree(canonical,data)
        old=read(data/'programs.csv');old_ev=read(data/'evidence_programs.csv')
        apply(data);once=digest(data);apply(data);assert once==digest(data),'replay changed bytes'
        expected={(r['program_id'],r['column']):r['new_value'] for r in edits}
        after={r['program_id']:r for r in read(data/'programs.csv')}
        assert len(after)==len(old)
        for r in old:
            assert after[r['program_id']]=={k:expected.get((r['program_id'],k),v) for k,v in r.items()},r['program_id']
        new_ev={r['evidence_id']:r for r in read(data/'evidence_programs.csv')}
        assert all(new_ev[r['evidence_id']]==r for r in old_ev),'old evidence edited'
        # Wrong current institutional key must fail before ANY data/evidence write.
        eco=read(data/'ecosystem.csv');j=read(HERE/'joins.csv')[0]
        for r in eco:
            if r['org_id']==j['institution_org_id']:r['ipeds_unitid']='999999'
        write(data/'ecosystem.csv',eco);before=digest(data)
        try:apply(data)
        except AssertionError as e:assert 'UNITID conflict' in str(e)
        else:raise AssertionError('wrong UNITID passed')
        assert digest(data)==before
        shutil.copyfile(canonical/'ecosystem.csv',data/'ecosystem.csv')
        extra=next(p for p in data.glob('evidence*.csv') if p.name!='evidence_programs.csv')
        append_sorted(extra,[evidence[0]],'evidence_id');before=digest(data)
        try:apply(data)
        except AssertionError as e:assert 'wrong-shard evidence collision' in str(e)
        else:raise AssertionError('wrong-shard evidence passed')
        assert digest(data)==before
    print('PASS147 proposals=34VERIFIED/81schemaREJECT/32holds;112cells on34programs (5new countpairs/29confirmed);34EVD;44raw totals+known answers;replay/preservation/wrong-UNITID+cross-shard no-write failures')


if __name__=='__main__':main()
