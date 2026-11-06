"""L13 packet accounting, replay, and deliberate defect checks."""
import shutil, tempfile
from pathlib import Path
from build import HERE, apply, read


def main():
    inputs, verdicts, raw = [read(HERE / f) for f in ('input.csv','verdicts.csv','rawcheck.csv')]
    ids = [r['lead_id'] for r in inputs]
    assert len(ids) == len(set(ids)) == 6
    calibration = read(HERE / 'calibration.csv')
    calibration_ids = {r['lead_id'] for r in calibration}
    assert len(calibration_ids) == 4 and not calibration_ids.intersection(ids)
    assert all(r['held_same_name'] == 'False' and r['state'] not in ('OH','PA') for r in inputs)
    assert set(ids) == {r['lead_id'] for r in verdicts}
    assert set(ids) | calibration_ids == {r['lead_id'] for r in raw}
    assert len(verdicts) == 6 and len(raw) == 10
    assert all(r['raw'] == 'yes' and r['observed_date'] == '2026-11-06' for r in raw)
    programs = read(HERE / 'programs.csv'); evidence = read(HERE / 'evidence_programs.csv')
    assert len(programs) == 1 and programs[0]['program_id'] == 'PROG-000300'
    assert {r['claim_type'] for r in evidence if r['record_id'] == 'PROG-000300'} == {'existence','scope'}
    assert len({r['evidence_id'] for f in ('evidence_programs.csv','evidence_ecosystem.csv') for r in read(HERE/f)}) == 3
    canonical = {r['program_id']:r for r in read(HERE.parents[1] / 'data/programs.csv')}
    for r in verdicts + calibration:
        assert r['verdict'] in ('VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF')
        if r['verdict'] == 'DUPLICATE_OF':
            assert r['record_id'] in canonical, r
    # Preserve all old rows, replay identically, and fail closed on occupied reserved IDs.
    names = ('programs.csv','evidence_programs.csv','evidence_ecosystem.csv','ecosystem.csv')
    with tempfile.TemporaryDirectory() as tmp:
        data = Path(tmp)
        for f in names: shutil.copyfile(HERE.parents[1]/'data'/f,data/f)
        before = {f:read(data/f) for f in names}
        apply(data)
        first = {f:(data/f).read_bytes() for f in names}
        apply(data)
        assert first == {f:(data/f).read_bytes() for f in names}, 'replay changed bytes'
        for f in names:
            key = 'evidence_id' if f.startswith('evidence') else 'program_id' if f == 'programs.csv' else 'org_id'
            after = {r[key]:r for r in read(data/f)}
            for old in before[f]:
                expected = dict(old)
                if f == 'ecosystem.csv' and old['org_id'] == 'ORG-002846':
                    expected['polymer_program_name'] = after[old[key]]['polymer_program_name']
                    expected['polymer_program_url'] = after[old[key]]['polymer_program_url']
                assert after[old[key]] == expected, (f,old[key])
        text=(data/'programs.csv').read_text().replace('Plastics Engineering Seminars,training','Fabricated Collision,training')
        (data/'programs.csv').write_text(text)
        try: apply(data)
        except AssertionError as e: assert 'ID collision/drift' in str(e)
        else: raise AssertionError('occupied ID was silently accepted')
    print('PASS: 6 pending input leads = 1 VERIFIED + 4 DUPLICATE_OF + 1 STILL_UNCERTAIN; 4 separate calibration leads; 1 program / 3 evidence rows; replay and collision injection passed')


if __name__ == '__main__': main()
