"""Idempotent builder: retires the one registry link blind audit 11 graded CREATION_ERROR (id A11-113) by removing its row from
data/registry_links.csv and declaring it in REMOVALS.csv (table,key,reason; read by scripts/check_row_loss.py). Calls no SAM API; the key is read
from the adjudication, so no entity name or address appears in any file here."""
import csv, io, json, os, subprocess
from pathlib import Path
T = Path(__file__).resolve().parent
ROOT = T.parents[1]
ADJ = ROOT / 'tasks/blind-audit-11-2026-11-17/adjudication.json'
LINKS = ROOT / 'data/registry_links.csv'
BASE = (Path(__file__).resolve().parent / 'base.txt').read_text().strip()
REASON = 'A11-113 UEI link graded CREATION_ERROR in the blind audit 11 adjudication (tasks/blind-audit-11-2026-11-17/adjudication.json); retired, basis held privately under R-SAM'
def a11_113():
    d = [x for x in json.loads(ADJ.read_text())['decisions'] if x['id'] == 'A11-113']
    assert len(d) == 1 and d[0]['grade'] == 'CREATION_ERROR' and d[0]['change_class'] == 'uei_links', d
    return d[0]['record_id']  # org_id|registry|registry_id|site_id
def write_atomic(path, header, rows):
    """Temp file in the same directory, flush + fsync, then os.replace: an interrupted write never leaves a truncated target."""
    tmp = path.with_name(path.name + '.tmp')
    try:
        with tmp.open('w', newline='') as f:
            w = csv.writer(f, lineterminator='\n'); w.writerow(header); w.writerows(rows); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)
def base_count():
    return len(list(csv.DictReader(io.StringIO(subprocess.check_output(['git', 'show', f'{BASE}:data/registry_links.csv'], cwd=ROOT, text=True), newline=''))))
def link_key(r): return '|'.join(r[c] for c in ('org_id', 'registry', 'registry_id', 'site_id'))
def main():
    key = a11_113()
    rows = list(csv.DictReader(LINKS.open(newline='')))
    hit = [r for r in rows if link_key(r) == key]
    assert len(hit) <= 1, 'key is not unique'
    keep = [r for r in rows if link_key(r) != key]
    assert len(keep) == base_count() - 1, f'expected {base_count() - 1} links after the removal, have {len(keep)}: the file is not the base minus one row'
    if hit: write_atomic(LINKS, list(rows[0]), ([r[c] for c in rows[0]] for r in keep))
    write_atomic(T / 'REMOVALS.csv', ['table', 'key', 'reason'], [['registry_links', key, REASON]])
    print(json.dumps(dict(removed=len(hit), links_left=len(keep))))
if __name__ == '__main__': main()
