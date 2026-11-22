#!/usr/bin/env python3
"""Reading aid: street-shaped strings in the gate's capture_text of every stored page of each frame site's organization (default canary; args = site_ids or 'all').
Writes screen.tsv to the store (outside the repo: its context windows can show names and phone numbers). The screen only finds candidates; the verdict is a reading of the displayed context."""
import csv, json, re, sys
from pathlib import Path
D = Path(__file__).resolve().parent; sys.path.insert(0, str(D.parents[1] / 'scripts')); sys.path.insert(0, str(D))
from atlas import NOTES_STREET_RE
from captext import capture_text
STORE = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/streets-2026-11-22')
frame = list(csv.DictReader(open(D / 'frame.csv')))
a = sys.argv[1:]
sel = frame if a == ['all'] else [r for r in frame if (r['site_id'] in a if a else r['canary'] == '1')]
fx = {}
for l in open(STORE / 'fetches.jsonl'):
    j = json.loads(l)
    if j.get('status') in ('ok', 'THIN_OR_EMPTY') and j['kind'] != 'robots': fx.setdefault(j['org_id'], {})[j['sha256']] = j['final_url']
LABEL = re.compile(r'(?i)headquarter|corporate|mailing|p\.?o\.?\s*box|sales office|regional|distribution|warehouse|office|shipping|manufactur|plant|facility|location')
out = []
for r in sel:
    for sh, url in fx.get(r['org_id'], {}).items():
        t = capture_text((STORE / 'raw' / (sh + '.raw')).read_bytes())
        for m in NOTES_STREET_RE.finditer(t):
            s, e = m.span(); ctx = t[max(0, s - 120): e + 120]
            out.append(dict(site_id=r['site_id'], url=url, capture_sha256=sh, offset=s, length=e - s, match=m.group(0), city_near=int(r['city'].lower() in ctx.lower()), labels=';'.join(sorted({x.lower() for x in LABEL.findall(ctx)})), context=ctx))
with open(STORE / 'screen.tsv', 'w', newline='') as f:
    w = csv.DictWriter(f, list(out[0]) if out else ['site_id'], delimiter='\t', lineterminator='\n'); w.writeheader(); w.writerows(out)
print(len(out), 'candidates over', len({o['site_id'] for o in out}), 'of', len(sel), 'sites')
