"""Idempotently assemble all 144 reviewed verdicts; no canonical writes without a dated status decision."""
import csv
from pathlib import Path
from check import read,validate

HERE=Path(__file__).resolve().parent

def main():
    queue=read(HERE/'queue.csv')
    rows=[r for lane in ('A','B') for r in read(HERE/'lanes'/lane/'verdicts.csv')]
    validate(queue,rows)
    decisions=read(HERE/'lead_decisions.csv')
    assert len(decisions)==len({r['org_id'] for r in decisions})
    overrides={r['org_id']:r for r in decisions}
    assert set(overrides)<={r['org_id'] for r in rows}
    audit=read(HERE/'lead_rawcheck.csv')
    raw={(r['org_id'],r['source_url'],r['quote']):r for r in audit}
    for r in rows:
        r['helper_verdict']=r['verdict']
        receipt=raw.get((r['org_id'],r['source_url'],r['quote']),{})
        r['lead_raw_check']=receipt.get('raw_check','not_refetched_hold')
        r['lead_review_note']='Manually reviewed identity and operating-offer finding; helper raw quote remains a research witness'
        if r['org_id'] in overrides:
            d=overrides[r['org_id']]
            r['verdict']=d['lead_verdict'];r['finding']=d['lead_finding'];r['settling_fact']=d['lead_settling_fact']
            r['lead_review_note']='Lead withheld integration; see specific settling fact'
        if r['verdict']=='VERIFIED':
            assert receipt.get('raw_check')=='yes',r['org_id']
        assert not r['proposed_status'] and not r['successor_org_id'], 'A dated status-application builder is required before any status mutation'
    rows.sort(key=lambda r:int(r['rank']))
    validate(queue,rows)
    with open(HERE/'verdicts.csv','w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    print('144 complete verdicts; VERIFIED',sum(r['verdict']=='VERIFIED' for r in rows),'STILL_UNCERTAIN',sum(r['verdict']=='STILL_UNCERTAIN' for r in rows),'canonical/status changes 0')

if __name__=='__main__':main()
