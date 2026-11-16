"""Apply the fixed evidence manifest. Run with --apply; repeat runs are inert."""
import csv, io, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
CACHE=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/integrator-backlog-4')
MATERIALS={'SITE-020001':'recycled_content_pcr_pir','SITE-020003':'epoxy'}
def apply():
    evidence=json.loads((HERE/'evidence.json').read_text()); pending={}; journal=[]
    for pattern in ['organizations_*.csv','sites_*.csv']:
        for path in sorted((ROOT/'data').glob(pattern)):
            rows=list(csv.DictReader(path.open())); changed=False
            for row in rows:
                rid=row.get('site_id',row.get('org_id')); selected=[e for e in evidence if e['record_id']==rid]
                if not selected: continue
                ep=path.with_name('evidence_'+path.name)
                have={e['evidence_id']:e for e in csv.DictReader(ep.open())}
                for e in selected:
                    if e['evidence_id'] in have: assert have[e['evidence_id']]==e
                    else: pending.setdefault(ep,[]).append(e)
                if rid in MATERIALS and row['materials']!=MATERIALS[rid]:
                    assert not row['materials'],(rid,'unexpected existing materials')
                    row['materials']=MATERIALS[rid];changed=True;journal.append(rid+' materials='+MATERIALS[rid])
            if changed:
                backup=CACHE/'backups'/path.name;backup.parent.mkdir(exist_ok=True)
                if not backup.exists(): backup.write_bytes(path.read_bytes())
                buf=io.StringIO();w=csv.DictWriter(buf,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows);path.write_text(buf.getvalue())
    for path,rows in pending.items():
        backup=CACHE/'backups'/path.name;backup.parent.mkdir(exist_ok=True)
        if not backup.exists():backup.write_bytes(path.read_bytes())
        append_sorted(path,rows,'evidence_id');journal.append(path.name+': appended '+str(len(rows)))
    if journal:(HERE/'journal.txt').write_text('\n'.join(journal)+'\n')
    print('changed operations:',len(journal))
if __name__=='__main__':
    if '--apply' in sys.argv:apply()
    else: print('Fixed manifest: 15 evidence rows; materials on 2 site records. Use --apply.')
