#!/usr/bin/env python3
"""Continue L1 in order: rest of Ohio, then PA; reuse the PIC18 raw quote audit."""
import importlib.util
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT/'tasks/evidence-reverify-archive-2026-11-06'
spec = importlib.util.spec_from_file_location('pic18_audit',BASE/'run.py')
audit = importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)


def main():
    already = {r['evidence_id'] for r in audit.read(BASE/'inputs.csv')}
    sites = [r for p in sorted((ROOT/'data').glob('sites_*.csv')) for r in audit.read(p)]
    evidence = [r for p in sorted((ROOT/'data').glob('evidence_*.csv')) for r in audit.read(p) if r['source_class']=='own_site']
    assert len({r['evidence_id'] for r in evidence}) == len(evidence)
    for state in ('OH','PA'):
        phase = HERE/state; phase.mkdir(exist_ok=True)
        si = {r['site_id'] for r in sites if r['state']==state}
        oi = {r['org_id'] for r in sites if r['site_id'] in si}
        rows = [dict(r,url=r['source_ref'],quote=audit.quote(r)) for r in evidence if r['evidence_id'] not in already and ((r['record_table']=='sites' and r['record_id'] in si) or (r['record_table']=='organizations' and r['record_id'] in oi))]
        assert len({r['evidence_id'] for r in rows}) == len(rows)
        assert not ({r['evidence_id'] for r in rows} & already)
        audit.write(phase/'inputs.csv', rows, list(rows[0]))
        audit.HERE = phase
        audit.frame = lambda rows=rows: rows
        print(state,'rows',len(rows),'references',len({r['url'] for r in rows}),flush=True)
        audit.audit()
        already.update(r['evidence_id'] for r in rows)


if __name__=='__main__': main()
