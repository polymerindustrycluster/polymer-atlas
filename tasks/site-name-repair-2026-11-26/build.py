#!/usr/bin/env python3
"""Apply the frozen PACKET.csv: rename site_name (owner ruling 2026-11-25 20:12, "Name on the door"), keep the old name in the site's
notes, append one own-site evidence row per rename, write BINDING_PROOF.csv and INPUTS.sha256. Refuses a second run.
Usage: build.py --apply   (--claims rewrites CLAIMS_CHECKED.csv only)"""
import csv, hashlib, io, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; D = Path(__file__).parent
sys.path.insert(0, str(ROOT / 'scripts'))
import check_evidence_binding as g  # noqa: E402

LABEL = 'site-name-repair-2026-11-26'; FIRST_EVD = 483144; RULING = 'owner ruling 2026-11-25 20:12, "Name on the door"'


def read(p):
    with open(p, newline='', encoding='utf-8') as f: return list(csv.reader(f))


def write(p, rows):
    buf = io.StringIO(newline=''); csv.writer(buf, lineterminator='\n').writerows(rows)
    Path(p).write_bytes(buf.getvalue().encode('utf-8'))


HELD_EXTRA = ('SITE-001778', 'SITE-000439')  # known answer whose held website redirects (the gate's own-domain test); a block naming two entities


def claims_rows():
    """Corrected rows from the evidence this PR appended, then every other site judged (the pilot reads and the two above) as held."""
    mine = [r for r in read(ROOT / 'data/evidence_sites_OH.csv')[1:] if r[9] == LABEL]
    rows = [['table', 'record_id', 'field', 'verdict', 'evidence_id']] + [['sites', r[2], 'site_name', 'corrected', r[0]] for r in sorted(mine, key=lambda r: r[2])]
    done = {r[2] for r in mine}
    judged = sorted({r[0] for r in read(D / 'PILOT.csv')[1:]} | set(HELD_EXTRA))
    return rows + [['sites', sid, 'site_name', 'held', ''] for sid in judged if sid not in done]


def main():
    if '--claims' in sys.argv: write(D / 'CLAIMS_CHECKED.csv', claims_rows()); return print('claims rewritten')
    if '--apply' not in sys.argv: sys.exit(__doc__)
    packet = [dict(zip(read(D / 'PACKET.csv')[0], r)) for r in read(D / 'PACKET.csv')[1:]]
    shards = {}  # sites shard path -> rows
    for r in packet:
        path = next(p for p in sorted((ROOT / 'data').glob('sites_*.csv')) if any(x[0] == r['site_id'] for x in read(p)[1:]))
        shards.setdefault(path, read(path))
    ev_path = ROOT / 'data/evidence_sites_OH.csv'; ev = read(ev_path); eh = ev[0]
    proof = [['evidence_id', 'record_id', 'claim_sha256', 'capture', 'capture_date', 'capture_sha256', 'quote_offset', 'verdict', 'reader_family', 'reader_date']]
    claims = [['table', 'record_id', 'field', 'verdict', 'evidence_id']]; inputs = []
    for i, r in enumerate(packet):
        rows = shards[next(p for p, rs in shards.items() if any(x[0] == r['site_id'] for x in rs[1:]))]
        h = rows[0]; row = next(x for x in rows[1:] if x[0] == r['site_id'])
        assert row[h.index('site_name')] == r['old_site_name'], f"{r['site_id']}: already applied or held name differs"
        row[h.index('site_name')] = r['new_site_name']
        n = h.index('notes'); row[n] = (row[n] + ' ' if row[n] else '') + f"Former site_name (renamed by {LABEL}, {RULING}): {r['old_site_name']}."
        e = dict(evidence_id=f'EVD-{FIRST_EVD + i}', record_table='sites', record_id=r['site_id'], claim_type='existence',
                 claim_detail=f"site_name '{r['new_site_name']}' as printed at the recorded address; quote: {r['quote']}", source_class='own_site',
                 source_ref=r['capture_url'], observed_date=r['capture_date'], tier_effect='supports_A', created_by=LABEL,
                 notes=f"Name on the door ({RULING}). The operator's own page prints this name at the held street. Former site_name: {r['old_site_name']}.", address_role='')
        ev.append([e[k] for k in eh])
        proof.append([e['evidence_id'], r['site_id'], g.claim_sha256(e), r['capture_url'], r['capture_date'], r['capture_sha256'], r['quote_offset'], 'VERIFIED', r['reader_family'], r['reader_date']])
        claims.append(['sites', r['site_id'], 'site_name', 'corrected', e['evidence_id']])
        inputs.append(f"{r['capture_sha256']}  provenance/{LABEL}/captures/{r['capture_sha256']}.html")
    for p, rows in shards.items(): write(p, rows)
    write(ev_path, ev); write(D / 'BINDING_PROOF.csv', proof)
    (D / 'INPUTS.sha256').write_text('\n'.join(sorted(set(inputs))) + '\n')
    write(D / 'CLAIMS_CHECKED.csv', claims_rows())
    print(len(packet), 'renames applied')


if __name__ == '__main__': main()
