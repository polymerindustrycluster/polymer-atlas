#!/usr/bin/env python3
"""How many packet streets the size sprint could then match under its own rule: copies data/ and the sibling lane's tasks/pic18-size-sprint-2026-11-22 (branch
agent/claude-code/pic18-size-sprint-2026-11-22, worktree ../size-sprint) into a temp tree, writes the packet streets into that copy's sites_OH.csv, runs the sibling build.py over its cached
OSHA/Form 5500 extracts, and writes size_rerun.csv (site_id, result). Usage: python3 size_rerun.py SIZE_SPRINT_TASK_DIR CACHE_DIR. Needs the sibling worktree; not run by check.py."""
import csv, shutil, subprocess, sys, tempfile
from pathlib import Path
D = Path(__file__).resolve().parent; R = D.parents[1]
src, cache = Path(sys.argv[1]), sys.argv[2]
t = Path(tempfile.mkdtemp()); (t / 'tasks').mkdir(); (t / 'scripts').symlink_to(R / 'scripts'); shutil.copytree(R / 'data', t / 'data'); shutil.copytree(src, t / 'tasks' / src.name)
P = {r['site_id']: r for r in csv.DictReader(open(D / 'packet.csv'))}
f = t / 'data/sites_OH.csv'; rows = list(csv.DictReader(open(f, newline='', encoding='utf-8'))); cols = list(rows[0])
for r in rows:
    if r['site_id'] in P: r['street_address'] = P[r['site_id']]['proposed_street']
w = csv.DictWriter(open(f, 'w', newline='', encoding='utf-8'), cols, lineterminator='\n'); w.writeheader(); w.writerows(rows)
print(subprocess.run([sys.executable, str(t / 'tasks' / src.name / 'build.py'), '--cache', cache, '--out', str(t / 'out')], capture_output=True, text=True).stdout.splitlines()[1][:200])
H = {r['site_id']: r for r in csv.DictReader(open(t / 'out/holds.csv'))}; F = {r['site_id'] for r in csv.DictReader(open(t / 'out/packet.csv'))}
out = [dict(site_id=s, result='FILL' if s in F else H.get(s, {}).get('reason', '?'), detail=(H.get(s, {}).get('detail', '') or '')[:160]) for s in P]
with open(D / 'size_rerun.csv', 'w', newline='') as g:
    w = csv.DictWriter(g, ['site_id', 'result', 'detail'], lineterminator='\n'); w.writeheader(); w.writerows(out)
print(sum(o['result'] == 'FILL' for o in out), 'of', len(out), 'packet sites fill under the size sprint rule')
