"""L13B frame reconciliation, evidence, replay, row preservation, no-write collision checks."""
import csv, hashlib, json, shutil, tempfile
from collections import Counter
from pathlib import Path
from build import HERE,apply,read
from shard_io import append_sorted


def digest(data):
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}


def main():
    source=read(HERE.parent/'program-leads-2026-11-03/worklist.csv')
    fields=list(source[0]);prior={tuple(r[k] for k in fields) for r in read(HERE/'prior_input.csv')}
    pending=[(i,r) for i,r in enumerate(source,2) if r['state'] not in ('OH','PA') and r['held_same_name']=='False' and tuple(r[k] for k in fields) not in prior]
    assert len(prior)==6 and len(pending)==269
    inputs=read(HERE/'input.csv');verdicts=read(HERE/'verdicts.csv');quotes=read(HERE/'quotes.csv');raw=read(HERE/'rawcheck.csv')
    assert len(inputs)==100 and len({r['source_row'] for r in inputs})==100
    assert [(r['source_row'],tuple(r[k] for k in fields)) for r in inputs]==[(str(i),tuple(r[k] for k in fields)) for i,r in pending[:100]]
    assert len(verdicts)==len({r['lead_id'] for r in verdicts})==100
    assert {r['lead_id'] for r in inputs}=={r['lead_id'] for r in verdicts}
    assert Counter(r['verdict'] for r in verdicts)=={'VERIFIED':4,'DUPLICATE_OF':2,'STILL_UNCERTAIN':94}
    assert all(r['settling_fact_or_reason'] for r in verdicts)
    receipts=[r for p in HERE.glob('*fetches.json') for r in json.load(p.open())]
    assert {r['lead_id'] for r in inputs}<={i for r in receipts for i in r['lead_ids']},'unattempted lead'
    assert {(r['lead_id'],r['source_url'],r['quote']) for r in quotes}=={(r['lead_id'],r['source_url'],r['quote']) for r in raw}
    assert len(raw)==len(quotes)==16 and all(r['raw']=='yes' for r in raw)
    packets={f:read(HERE/f) for f in ('programs.csv','ecosystem.csv','evidence_programs.csv','evidence_ecosystem.csv')}
    assert list(map(len,packets.values()))==[4,2,13,7]
    assert {r['record_id'] for r in verdicts if r['verdict']=='VERIFIED'}=={r['program_id'] for r in packets['programs.csv']}
    evidence=packets['evidence_programs.csv']+packets['evidence_ecosystem.csv']
    assert len(evidence)==len({r['evidence_id'] for r in evidence})==20
    for f,key in (('programs.csv','program_id'),('ecosystem.csv','org_id')):
        for row in packets[f]:assert {'existence','scope'}<={r['claim_type'] for r in evidence if r['record_id']==row[key]}
    for r in packets['programs.csv']:
        assert all(r[k] for k in ('city','state','county')), 'required locality missing'
        assert not any(r[k] for k in ('cip_code','cip_source_type','latest_completions','completions_year','first_year_awarded','last_year_awarded'))
    canonical=HERE.parents[1]/'data'
    held={r['program_id'] for r in read(canonical/'programs.csv')}
    assert all(r['record_id'] in held for r in verdicts if r['verdict']=='DUPLICATE_OF')
    with tempfile.TemporaryDirectory() as tmp:
        data=Path(tmp)/'data';shutil.copytree(canonical,data)
        old={f:read(data/f) for f in packets}
        apply(data);once=digest(data);apply(data);assert once==digest(data),'non-idempotent replay'
        for f,rows in old.items():
            key='program_id' if f=='programs.csv' else 'org_id' if f=='ecosystem.csv' else 'evidence_id'
            now={r[key]:r for r in read(data/f)}
            for r in rows:
                want=dict(r)
                if f=='ecosystem.csv' and r[key]=='ORG-002844':
                    for col in ('polymer_program_name','polymer_program_url'):want[col]=now[r[key]][col]
                assert now[r[key]]==want,(f,r[key])
        # Wrong-shard collision must fail before ANY write, even if target shard itself is clean.
        extra=next(p for p in data.glob('evidence*.csv') if p.name not in ('evidence_programs.csv','evidence_ecosystem.csv'))
        append_sorted(extra,[packets['evidence_programs.csv'][0]],'evidence_id')
        before=digest(data)
        try:apply(data)
        except AssertionError as e:assert 'cross-table ID collision' in str(e)
        else:raise AssertionError('wrong-shard evidence collision passed')
        assert before==digest(data),'collision caused partial writes'
        # A changed packet row under its reserved id must also fail without touching other files.
        extra.write_bytes((canonical/extra.name).read_bytes())
        p=data/'programs.csv';text=p.read_text().replace('Paulson University Online Training','Injected Conflicting Program');p.write_text(text)
        before=digest(data)
        try:apply(data)
        except AssertionError as e:assert 'ID collision/drift' in str(e)
        else:raise AssertionError('occupied ID passed')
        assert before==digest(data),'conflict caused partial writes'
    print('PASS 100 exact next leads =4VERIFIED/2DUPLICATE_OF/94STILL_UNCERTAIN;4programs/2institutions/20evidence;16rawquotes;replay,prior-row preservation,two no-write defect injections')


if __name__=='__main__':main()
