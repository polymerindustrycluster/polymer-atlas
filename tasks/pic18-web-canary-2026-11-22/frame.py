#!/usr/bin/env python3
"""Frame for the 2026-11-22 web canary. Read-only. Writes frame_pool.csv (all candidates + exclusion flag) and frame.csv (first 25).
Unknown definition = S/harness/pic18_unknown.py (PIC-18 active tier A-C OH sites; processes empty at site union, then org cell)."""
import csv, glob, random, re, subprocess, sys
sys.path.insert(0, 'scripts'); from regions import PIC18
D = 'tasks/pic18-web-canary-2026-11-22/'
toks = lambda v: {t.strip() for t in (v or '').split(';') if t.strip() and t.strip() != 'unknown'}
rd = lambda f: list(csv.DictReader(open(f, newline='', encoding='utf-8')))
orgs = {r['org_id']: r for f in glob.glob('data/organizations_*.csv') for r in rd(f)}
eco = {r['org_id']: r for r in rd('data/ecosystem.csv')}
GT = {}
for f in glob.glob('data/sites_*.csv'):
    for s in rd(f):
        if s['state'] == 'OH' and s['county'] in PIC18 and s['operating_status'] == 'active' and s['verification_tier'] in ('A', 'B', 'C'):
            GT.setdefault(s['org_id'], []).append(s)
site2org = {s['site_id']: o for o, ss in GT.items() for s in ss}
rec = lambda o: orgs.get(o) or eco.get(o) or {}
unknown = sorted(o for o, ss in GT.items() if not (set().union(*(toks(s['processes']) for s in ss)) or toks(rec(o).get('processes'))))
def web(o):  # the record's own value; a bare domain gets https:// (normalisation, not a guess)
    v = rec(o).get('website', '').strip()
    if not v or v.lower() in ('none_found', 'none', 'n/a', 'unknown') or ' ' in v or '.' not in v: return ''
    return v if re.match(r'https?://', v, re.I) else 'https://' + v
with_web = [o for o in unknown if web(o)]

# prior holds that recorded a READ page with no process stated by the company (reason text classified by regex; reviewed by hand in README)
READ = re.compile(r'no process sentence|no stored page|describes customers|past roles|Equipment dealer|Distributor|Resin trader|service-menu|not stated as this plant|Product names|Services list only|menu', re.I)
NOT = re.compile(r'Cleveland plant|Kent plant|plant address|bridg|domain|solvent|rejected', re.I)  # locality/identity holds: the page was not judged to name no process
excl = {}  # org -> (lane, reason)
for r in rd('tasks/pic18-org-process-canary-2026-11-18/holds.csv'):
    if r['reason'] in ('no_process_named', 'equipment_maker_not_process'):
        excl[r['org_id']] = ('process-canary-2026-11-18', r['reason'])
for r in rd('tasks/pic18-capabilities-corpus-2b-2026-11-16/verdicts.csv'):
    o = site2org.get(r['site_id'])
    if o and r['verdict'] == 'STILL_UNCERTAIN' and r['disposition'] == 'held' and READ.search(r.get('reason', '')) and not NOT.search(r.get('reason', '')):
        excl.setdefault(o, ('capabilities-corpus-2b-2026-11-16', r['reason'][:140]))
for r in rd('tasks/pic18-record-health-6-2026-11-06/capability/classification_routes.csv'):
    if r['class'] in ('c', 'd') and r['org_id'] in with_web and not NOT.search(r['reason']):
        excl.setdefault(r['org_id'], ('record-health-6-2026-11-06', r['reason'][:140]))
# screen-only prior holds: recorded, NOT excluded (a regex term screen, not a page reading, per 2b README)
screen_only = {site2org[r['site_id']] for r in rd('tasks/pic18-capabilities-corpus-2b-2026-11-16/verdicts.csv') if r['disposition'] == 'nothing found' and r['site_id'] in site2org}

pool = [o for o in with_web if o not in excl]
order = sorted(pool); random.Random(20261122).shuffle(order)
pick = order[:25]
base = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
with open(D + 'frame_pool.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['org_id', 'website', 'excluded', 'excl_lane', 'excl_reason', 'prior_screen_only', 'shuffle_rank'])
    for o in with_web:
        w.writerow([o, web(o), o in excl, *(excl.get(o, ('', ''))), o in screen_only, order.index(o) + 1 if o in order else ''])
with open(D + 'frame.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['rank', 'org_id', 'legal_name', 'website', 'ring_primary', 'tier', 'prior_screen_only', 'base_commit'])
    for i, o in enumerate(pick, 1):
        r = rec(o); w.writerow([i, o, r.get('legal_name'), web(o), r.get('ring_primary'), r.get('verification_tier'), o in screen_only, base[:8]])
print(f'base {base[:8]} PIC-18 orgs {len(GT)} unknown {len(unknown)} with_web {len(with_web)} excluded {len(excl)} (of which in with_web {len([o for o in excl if o in with_web])}) pool {len(pool)} screen_only_in_pool {len([o for o in pool if o in screen_only])}')
