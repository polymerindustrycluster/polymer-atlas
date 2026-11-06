"""Prove reconciliation fails on the defects found by the independent refute."""
import subprocess
import sys
from run import HERE, read, write


def reject(name, mutate, command="report.py"):
    p = HERE/name
    before = p.read_bytes()
    try:
        rows = read(p); fields = list(rows[0]); mutate(rows)
        write(p,rows,fields)
        r = subprocess.run([sys.executable,str(HERE/command)],capture_output=True,text=True)
        assert r.returncode != 0 and 'AssertionError' in r.stderr, (name,r.stdout,r.stderr)
        print(name,'injected defect rejected')
    finally: p.write_bytes(before)


reject('verdicts.csv', lambda rows: rows[0].update(quote='forged replacement quote'))
reject('repair_leads.csv', lambda rows: rows.append(dict(rows[0])))
reject('archive_outcomes.csv', lambda rows: rows[0].update(evidence_id='EVD-NOT-IN-FRAME'))
reject('archive_checks.csv', lambda rows: rows.pop(), 'build.py')
print('Mutation checks PASS; all originals restored byte-for-byte')
