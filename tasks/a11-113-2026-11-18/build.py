"""Idempotent builder: retires the one registry link blind audit 11 graded CREATION_ERROR (id A11-113) by removing its row from
data/registry_links.csv and declaring it in REMOVALS.csv (table,key,reason; read by scripts/check_row_loss.py). Calls no SAM API; the key is read
from the adjudication, so no entity name or address appears in any file here."""
import csv, json
from pathlib import Path
T = Path(__file__).resolve().parent
ROOT = T.parents[1]
ADJ = ROOT / 'tasks/blind-audit-11-2026-11-17/adjudication.json'
LINKS = ROOT / 'data/registry_links.csv'
REASON = 'A11-113 UEI link graded CREATION_ERROR in the blind audit 11 adjudication (tasks/blind-audit-11-2026-11-17/adjudication.json); retired, basis held privately under R-SAM'
def a11_113():
    d = [x for x in json.loads(ADJ.read_text())['decisions'] if x['id'] == 'A11-113']
    assert len(d) == 1 and d[0]['grade'] == 'CREATION_ERROR' and d[0]['change_class'] == 'uei_links', d
    return d[0]['record_id']  # org_id|registry|registry_id|site_id
def link_key(r): return '|'.join(r[c] for c in ('org_id', 'registry', 'registry_id', 'site_id'))
def main():
    key = a11_113()
    rows = list(csv.DictReader(LINKS.open(newline='')))
    hit = [r for r in rows if link_key(r) == key]
    assert len(hit) <= 1, 'key is not unique'
    if hit:
        with LINKS.open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(r for r in rows if link_key(r) != key)
    with (T / 'REMOVALS.csv').open('w', newline='') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(['table', 'key', 'reason']); w.writerow(['registry_links', key, REASON])
    print(json.dumps(dict(removed=len(hit), links_left=len(rows) - len(hit))))
if __name__ == '__main__': main()
