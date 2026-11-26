#!/usr/bin/env python3
"""Move each proof to its Wayback id_ capture (immutable: a live page can change before the gate replays it at merge). For every PACKET row:
fetch the archive snapshot made by archive.py with the gate's fetcher, find the quote in capture_text, store the bytes, and rewrite the
capture fields. Rows whose archived text lacks the quote are dropped and named. Usage: archive_proof.py"""
import csv, hashlib, sys, time
from pathlib import Path
D = Path(__file__).parent; ROOT = D.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import check_evidence_binding as g  # noqa: E402

STORE = Path('/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store/provenance/site-name-repair-2026-11-26/captures')


def main():
    packet = list(csv.DictReader(open(D / 'PACKET.csv', newline='', encoding='utf-8')))
    arch = {r['evidence_id']: r for r in csv.DictReader(open(ROOT / 'data/archive_links.csv', newline='', encoding='utf-8')) if r['created_by'].endswith('site-name-repair-2026-11-26')}
    ev = {r['record_id']: r for r in csv.DictReader(open(ROOT / 'data/evidence_sites_OH.csv', newline='', encoding='utf-8')) if r['created_by'] == 'site-name-repair-2026-11-26'}
    utc = time.strftime('%Y-%m-%d', time.gmtime()); out = []
    for r in packet:
        a = arch[ev[r['site_id']]['evidence_id']]; ref = a['archive_ref']; ts = ref.split('/web/')[1][:14]
        cap = ref.replace(f'/web/{ts}/', f'/web/{ts}id_/', 1)
        data = g.fetch_url(cap); time.sleep(2)
        if g.fetch_url(cap) != data: print(r['site_id'], 'archive bytes unstable'); continue
        off = g.capture_text(data).find(r['quote'])
        if off < 0: print(r['site_id'], 'quote not in the archived main text, dropped'); continue
        sha = hashlib.sha256(data).hexdigest(); (STORE / f'{sha}.html').write_bytes(data)
        day = f'{ts[:4]}-{ts[4:6]}-{ts[6:8]}'
        out.append(dict(r, proof_capture=cap, capture_sha256=sha, quote_offset=off, capture_date=day, observed_date=max(day, r['capture_date']), reader_date=max(day, utc),
                        archive_ref=ref, archive_captured_at=a['captured_at']))
        print(r['site_id'], 'ok', cap[-60:], off, flush=True)
    with open(D / 'PACKET.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, list(out[0]), lineterminator='\n'); w.writeheader(); w.writerows(out)
    print(len(out), 'of', len(packet), 'rows moved to archive captures')


if __name__ == '__main__': main()
