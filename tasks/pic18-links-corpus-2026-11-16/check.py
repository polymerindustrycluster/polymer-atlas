"""Recompute packet, census, witnesses, scoped diff and three deliberate corruptions."""
import collections, copy, csv, io, json, subprocess
import build as b

def validate(packet, expected=None):
    if expected is None: expected=b.proposals(b.read(b.HERE/'inputs.csv'),b.read(b.HERE/'manifest.csv'))
    assert packet==expected,'packet differs from corpus recomputation'
    return collections.Counter((r['column'],r['applied']) for r in packet)
def main():
    packet=b.read(b.HERE/'proposals.csv');counts=validate(packet)
    base=(b.HERE/'base.txt').read_text().strip()
    def at(path):return list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',base+':'+str(path.relative_to(b.ROOT))],text=True))))
    pic={r['org_id'] for p in (b.ROOT/'data').glob('sites_*.csv') if p.name!='sites_all.csv' for r in at(p) if r['state']=='OH' and r['county'].removesuffix(' County') in b.PIC18}
    frozen=b.read(b.HERE/'inputs.csv');ts=b.tables()
    independent={r['org_id'] for p in ts for r in at(p) if r['org_id'] in pic and r['website']}
    assert len(frozen)==len({r['org_id'] for r in frozen}) and independent=={r['org_id'] for r in frozen},'input yield mismatch'
    assert len(packet)==sum(not r[c] for r in frozen for c in b.COLS),'blank-cell yield mismatch'
    accepted={(r['org_id'],r['column']):r['value'] for r in packet if r['applied']=='yes'}
    actualchanges={}
    for p,rows in ts.items():
        old={r['org_id']:r for r in at(p)};assert set(old)=={r['org_id'] for r in rows}
        for r in rows:
            for col,value in r.items():
                if old[r['org_id']][col]!=value:
                    assert not old[r['org_id']][col] and col in b.COLS,'nonblank or unrelated field changed'
                    actualchanges[r['org_id'],col]=value
    assert actualchanges==accepted,'applied cell delta differs'
    for mutate in ('value','missing','duplicate'):
        bad=copy.deepcopy(packet)
        if mutate=='value':next(r for r in bad if r['applied']=='yes')['value']='https://wrong.example/'
        elif mutate=='missing':bad.pop()
        else:bad.append(bad[0])
        try:validate(bad,packet)
        except AssertionError:pass
        else:raise AssertionError('missed injected '+mutate)
    before={p:p.read_bytes() for p in ts};assert b.apply(packet)==0
    assert all(p.read_bytes()==raw for p,raw in before.items()),'rerun not idempotent'
    summary={'input_organizations':len(frozen),'manifest_rows':len(b.read(b.HERE/'manifest.csv')),'proposal_cells':len(packet),'applied_cells':len(accepted),'applied_organizations':len({o for o,c in accepted}),'counts':{c:{s:counts[c,s] for s in ('yes','held')} for c in b.COLS},'tiers':dict(collections.Counter(r['verification_tier'] for r in frozen if r['org_id'] in {o for o,c in accepted})),'injected_defects_rejected':3}
    (b.HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
