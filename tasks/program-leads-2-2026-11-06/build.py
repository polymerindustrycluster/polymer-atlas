"""Apply the fixed L13 packet; rerun on fresh main rather than merging CSVs."""
import argparse, csv, io, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'scripts'))
from shard_io import append_sorted


def read(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def apply(data):
    packets = [('programs.csv','program_id'), ('evidence_programs.csv','evidence_id'), ('evidence_ecosystem.csv','evidence_id')]
    plans = []
    for filename, key in packets:
        old = {r[key]: r for r in read(data / filename)}
        new = read(HERE / filename)
        assert len({r[key] for r in new}) == len(new), 'duplicate packet id'
        for row in new:
            assert row[key] not in old or old[row[key]] == row, f'ID collision/drift: {row[key]}'
        plans.append((data / filename, [r for r in new if r[key] not in old], key))
    program = read(HERE / 'programs.csv')[0]
    eco = read(data / 'ecosystem.csv')
    assert sum(r['org_id'] == program['institution_org_id'] for r in eco) == 1
    programs = read(data / 'programs.csv') + plans[0][1]
    precedence = {v:i for i,v in enumerate(('degree','center','certificate','apprenticeship','training','lab_facility','course'))}
    linked = sorted((r for r in programs if r['institution_org_id'] == program['institution_org_id'] and r['status'] != 'tombstoned'),key=lambda r:(precedence[r['program_type']],r['program_name'].strip().lower()))
    for r in eco:
        if r['org_id'] == program['institution_org_id']:
            r['polymer_program_name'] = '; '.join(p['program_name'].strip() for p in linked)
            r['polymer_program_url'] = linked[0]['url'].strip()
    for path, rows, key in plans:
        if rows:
            append_sorted(path, rows, key)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(eco[0]), lineterminator='\n')
    writer.writeheader(); writer.writerows(eco)
    (data / 'ecosystem.csv').write_text(buf.getvalue())
    print('L13 applied: 1 program; 4 evidence rows; institution rollup regenerated (idempotent)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', type=Path, default=HERE.parents[1] / 'data')
    apply(parser.parse_args().data_dir)
