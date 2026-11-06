"""Compare canonical row keys and fields against a specified integration base, then replay."""
import csv, hashlib, io, json, subprocess, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def keyed(text):
    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows: return {}
    key = next(iter(rows[0]))
    result = {r[key]: r for r in rows}
    assert len(result) == len(rows), ('duplicate key', key)
    return result

def main():
    base = sys.argv[1]
    git = lambda *args: subprocess.check_output(['git', *args], cwd=ROOT).decode()
    paths = git('ls-tree', '-r', '--name-only', base, 'data/').splitlines()
    changes, evidence, orgs = Counter(), Counter(), set()
    for name in paths:
        if not name.endswith('.csv'): continue
        path = ROOT / name
        assert path.exists(), ('missing file', name)
        old_text, new_text = git('show', f'{base}:{name}'), path.read_text()
        if old_text == new_text: continue
        assert path.name.startswith(('organizations_', 'evidence_organizations_')), ('unrelated file', name)
        old, new = keyed(old_text), keyed(new_text)
        assert old.keys() <= new.keys(), ('row loss', name, old.keys() - new.keys())
        for key, row in old.items():
            changed = {f for f in row if row[f] != new[key][f]}
            assert not changed or (path.name.startswith('organizations_') and changed <= {'markets_served', 'certifications'}), (name, key, changed)
            for field in changed:
                assert set(row[field].split(';')) - {''} <= set(new[key][field].split(';')), ('lost value', key, field)
                changes[field] += 1
                orgs.add(key)
        added = new.keys() - old.keys()
        assert not added or path.name.startswith('evidence_organizations_'), ('unexpected rows', name)
        if added:
            assert all(240160 <= int(key[4:]) <= 259999 for key in added)
            evidence[path.name] = len(added)
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT / 'data').glob('*.csv')}
    subprocess.run([sys.executable, str(HERE / 'build.py')], check=True, stdout=subprocess.DEVNULL)
    assert all(hashlib.sha256(p.read_bytes()).hexdigest() == digest for p, digest in before.items()), 'replay changed bytes'
    report = dict(base=git('rev-parse', base).strip(), organizations=len(orgs), changed_cells=dict(changes),
                  new_evidence_by_shard=dict(evidence), new_evidence_rows=sum(evidence.values()),
                  existing_row_loss=0, changed_unrelated_columns=0, edited_existing_evidence=0, replay_changed_bytes=False)
    (HERE / 'boundary.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__': main()
