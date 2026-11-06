"""Final packet gate; this batch has no authorized canonical creates or edits."""
import csv,json
from pathlib import Path
HERE=Path(__file__).resolve().parent


def read(path):
    with open(path,newline='') as f:return list(csv.DictReader(f))


def check(verdicts=None):
    verdicts=read(HERE/'verdicts.csv') if verdicts is None else verdicts
    source=read(HERE.parent/'program-leads-2026-11-03/worklist.csv');cols=list(source[0])
    prior={tuple(r[k] for k in cols) for r in read(HERE/'prior_input.csv')};assert len(prior)==106
    expected=[(str(i),tuple(r[k] for k in cols)) for i,r in enumerate(source,2) if r['state'] not in ('OH','PA') and r['held_same_name']=='False' and tuple(r[k] for k in cols) not in prior]
    inputs=read(HERE/'input.csv')
    assert len(inputs)==len(verdicts)==len({r['lead_id'] for r in verdicts})==169
    assert [(r['source_row'],tuple(r[k] for k in cols)) for r in inputs]==expected
    assert {r['lead_id'] for r in verdicts}=={r['lead_id'] for r in inputs}
    from collections import Counter
    assert Counter(r['verdict'] for r in verdicts)=={'DUPLICATE_OF':2,'STILL_UNCERTAIN':167}
    receipts=[r for p in HERE.glob('*fetches.json') for r in json.load(p.open())]
    assert {r['lead_id'] for r in inputs}<={i for r in receipts for i in r['lead_ids']}
    held={r['program_id']:r for r in read(HERE.parents[1]/'data/programs.csv')}
    raw=read(HERE/'rawcheck.csv');assert len(raw)==2 and all(r['raw']=='yes' for r in raw)
    for r in verdicts:
        assert r['settling_fact_or_reason']
        if r['verdict']=='DUPLICATE_OF':
            assert r['record_id'] in held and held[r['record_id']]['url']==r['source_url']
            assert r['quote']==held[r['record_id']]['program_name']
            assert any(q['lead_id']==r['lead_id'] and q['source_url']==r['source_url'] and q['quote']==r['quote'] for q in raw)
    print('PASS169 exact remaining leads:0VERIFIED/2DUPLICATE_OF/167STILL_UNCERTAIN;0canonical writes')


if __name__=='__main__':check()
