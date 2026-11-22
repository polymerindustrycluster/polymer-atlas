#!/usr/bin/env python3
"""Cheap step: list main-text lines (>=40 chars) that hit a section 3.1 process or 3.3 market keyword family, per capture. Output is a READING AID
(stored outside the repo, with the page text): a hit is a lead to read, never a fill. Usage: python3 screen.py > screen.tsv"""
import csv, json, re
from pathlib import Path
S = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/web-canary-2026-11-22')
PROC = r'mold|extru|thermoform|rotation|rotomold|calender|foam|pultru|filament|lay-?up|spray-?up|\brtm\b|infusion|autoclave|prepreg|machin|cnc|weld|die[- ]?cut|convert|laminat|coat|print|assembl|recycl|regrind|pellet|compound|masterbatch|mixing|blend|polymeri|vulcani|cur(e|ing)|cast(ing)?\b|potting|encapsul|tooling|additive manuf|3d print|fabricat|slit|dip(ping)?|latex|fiber spin|dye|manufactur|we (make|produce|build|process)|in-house'
MKT = r'automotive|aerospace|defense|medical|pharma|dental|construction|building|infrastructure|packag|food|beverage|consumer|appliance|electronic|electrical|machinery|agricultur|marine|rail|oil|gas|energy|solar|battery|water|lawn|garden|toy|sport|footwear|apparel|furniture|telecom|cosmetic|tire|chemical|mining|industr|rv\b|trailer|market|serv(e|es|ing)|customers|supply|supplies'
rows = [json.loads(l) for l in open(S / 'fetches.jsonl')]
print('org_id\turl\ttext_sha256\toffset\tkind\tfamily\tline')
for r in rows:
    if not r.get('text_sha256'): continue
    t = (S / 'text' / (r['text_sha256'] + '.txt')).read_text(); meta = json.loads((S / 'text' / (r['text_sha256'] + '.lines.json')).read_text())
    for s, e, k in meta:
        ln = t[s:e]
        if len(ln) < 40: continue
        fam = ('P' if re.search(PROC, ln, re.I) else '') + ('M' if re.search(MKT, ln, re.I) else '')
        if fam: print('\t'.join([r['org_id'], r['url'], r['text_sha256'][:12], str(s), k, fam, ln[:400]]))
