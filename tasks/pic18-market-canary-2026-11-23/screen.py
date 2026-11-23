#!/usr/bin/env python3
"""Adapted previous-canary keyword screen and privacy-safe excerpt writer."""
import csv
import json
import re

MKT = r'automotive|aerospace|defense|medical|pharma|dental|construction|building|infrastructure|packag|food|beverage|consumer|appliance|electronic|electrical|machinery|agricultur|marine|rail|oil|gas|energy|solar|battery|water|lawn|garden|toy|sport|footwear|apparel|furniture|telecom|cosmetic|tire|chemical|mining|industr|rv\b|trailer|market|serv(e|es|ing)|customers|supply|supplies'

CONTACT = re.compile(r'@|(?:\+?1[ .-]?)?(?:\(\d{3}\)|\d{3})[ .-]?\d{3}[ .-]\d{4}|founder|appointed|president|vice president|testimonial', re.I)


def show(pages, args):
    oid = args[0]
    pattern = re.compile(args[1] if len(args) > 1 else MKT, re.I)
    seen = set()
    for request, (row, lines) in pages.items():
        if row['org_id'] != oid or re.search(r'/leadership|/team|/staff|/directors|/management', row['final_url'], re.I):
            continue
        print(f"{request} {row['final_url']} {row['status']} fallback={row.get('class_fallback', False)}")
        offset = 0
        for line, kind in lines:
            if pattern.search(line) and not CONTACT.search(line) and (kind, line) not in seen:
                seen.add((kind, line))
                print(f"{request}:{offset} {kind} {line[:780]}")
            offset += len(line) + 1
    print('END SCREEN', flush=True)


def preserve(pages, selection, store=None):
    """Replay explicitly inspected sentences against volatile full text before saving."""
    if store is None:
        from fetch import STORE as store
    selected = {}
    for item in csv.DictReader(selection.read_text().splitlines(), delimiter='\t'):
        request, quote = int(item['request']), item['quote']
        row, lines = pages[request]
        matches = [(start, kind) for start, kind in offsets(lines, quote)]
        if not quote or not matches or CONTACT.search(quote):
            raise ValueError(f'capture {request} does not contain the privacy-safe exact quote')
        start, kind = matches[0]
        entry = dict(quote=quote, original_offset=start, kind=kind)
        excerpts = selected.setdefault(request, [])
        if entry not in excerpts:
            excerpts.append(entry)
    for request, (row, _) in pages.items():
        capture = dict(request=request, raw_sha256=row['sha256'], text_sha256=row['text_sha256'],
                       excerpts=selected.get(request, []))
        data = (json.dumps(capture, ensure_ascii=False, sort_keys=True) + '\n').encode()
        (store / 'captures' / f'{request}.json').write_bytes(data)
    print(f'PRESERVED {len(pages)} extracted captures, {sum(map(len, selected.values()))} excerpts', flush=True)


def offsets(lines, quote):
    offset = 0
    for line, kind in lines:
        start = line.find(quote)
        if start >= 0:
            yield offset + start, kind
        offset += len(line) + 1
