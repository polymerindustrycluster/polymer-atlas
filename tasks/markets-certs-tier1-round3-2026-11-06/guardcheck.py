"""Inject builder defects in a temporary copy and assert rejection before any CSV writes."""
import csv, hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def write(path, rows):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader(); w.writerows(rows)

def main():
    with tempfile.TemporaryDirectory(prefix='l10-guards-') as directory:
        root = Path(directory)
        task = root / 'tasks' / HERE.name
        shutil.copytree(HERE, task, ignore=shutil.ignore_patterns('__pycache__'))
        house = root / 'tasks/evidence-repair-2-2026-11-04'
        house.mkdir()
        shutil.copy(ROOT / 'tasks/evidence-repair-2-2026-11-04/prep.py', house)
        shutil.copytree(ROOT / 'data', root / 'data')
        (root / 'scripts').mkdir()
        shutil.copy(ROOT / 'scripts/shard_io.py', root / 'scripts')
        (root / 'docs/schema').mkdir(parents=True)
        shutil.copy(ROOT / 'docs/schema/vocab.json', root / 'docs/schema')
        inputs = task / 'inputs.csv'
        original = inputs.read_bytes()
        def reject(expected):
            before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (root / 'data').glob('*.csv')}
            result = subprocess.run([sys.executable, str(task / 'build.py')], capture_output=True, text=True)
            assert result.returncode and expected in result.stderr, result.stderr
            assert all(hashlib.sha256(p.read_bytes()).hexdigest() == digest for p, digest in before.items()), 'failed guard wrote data'
        source = next(p for p in (root / 'data').glob('evidence_*.csv') if len(p.read_text().splitlines()) > 1)
        old = source.read_bytes()
        with source.open(newline='') as f: rows = list(csv.DictReader(f))
        write(source, rows + [rows[0]])
        reject('duplicate evidence IDs in current tree')
        source.write_bytes(old)
        for basis, field, value, expected in [
            ('current_edition_page', 'quote', 'IATF 16949:2015', 'page edition must be current IATF2016'),
            ('dated_certificate', 'cert_expiry', '2025-01-01', 'certificate outside observation date'),
        ]:
            with inputs.open(newline='') as f: rows = list(csv.DictReader(f))
            next(r for r in rows if r['cert_basis'] == basis)[field] = value
            write(inputs, rows)
            reject(expected)
            inputs.write_bytes(original)
        verdicts = task / 'verdicts.csv'
        with verdicts.open(newline='') as f: rows = list(csv.DictReader(f))
        write(verdicts, rows[:-1])
        result = subprocess.run([sys.executable, str(task / 'check.py')], capture_output=True, text=True)
        assert result.returncode and 'frame/verdict yield mismatch' in result.stderr, result.stderr
    print(json.dumps({'duplicate_id_no_write': 'PASS', 'page_edition_no_write': 'PASS',
                      'expired_certificate_no_write': 'PASS', 'verdict_yield': 'PASS'}))

if __name__ == '__main__': main()
