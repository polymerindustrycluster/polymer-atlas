"""Apply/revise this PR's unmerged evidence and field edits; repeat runs are inert."""
import csv,io,json,sys,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
CACHE=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/integrator-backlog-4')
MATERIALS={'SITE-020001':'recycled_content_pcr_pir','SITE-020003':'','SITE-020005':'other_specified_in_notes','ORG-013801':'other_specified_in_notes'}
WITHDRAW={'EVD-369010','EVD-369011'}
def save(path,rows):
    backup=CACHE/'revision-backups'/path.name;backup.parent.mkdir(exist_ok=True)
    if not backup.exists():backup.write_bytes(path.read_bytes())
    buf=io.StringIO();w=csv.DictWriter(buf,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows);path.write_text(buf.getvalue())
def apply():
    evidence=json.loads((HERE/'evidence.json').read_text());journal=[]
    for pattern in ['organizations_*.csv','sites_*.csv']:
        for path in sorted((ROOT/'data').glob(pattern)):
            rows=list(csv.DictReader(path.open()));old=[r.copy() for r in rows]
            for row in rows:
                rid=row.get('site_id',row.get('org_id'))
                if rid not in MATERIALS:continue
                row['materials']=MATERIALS[rid]
                if rid=='SITE-020003':continue # Withdraw unmerged epoxy fill; original verification fields retained.
                selected=[e for e in evidence if e['record_id']==rid]
                for e in selected:
                    if e['source_ref'] not in [s.strip() for s in row['sources'].split(';')]:row['sources']+='; '+e['source_ref']
                row['last_verified']='2026-11-16'
                if rid in ['SITE-020005','ORG-013801']:
                    field='materials_other_note' if rid.startswith('SITE') else 'notes'
                    note='Polyiso insulation ISO GF, ISO CG, and ISO HD CG manufactured and shipping from Stillwater (Kingspan own site, read 2026-11-16).'
                    if note not in row[field]:row[field]=(row[field]+' '+note).strip()
            if rows!=old:save(path,rows);journal.append(path.name+' record correction')
    desired={e['evidence_id']:e for e in evidence}
    homes={r.get('site_id',r.get('org_id')):'evidence_'+p.name for pattern in ['organizations_*.csv','sites_*.csv'] for p in (ROOT/'data').glob(pattern) for r in csv.DictReader(p.open())}
    for path in sorted((ROOT/'data').glob('evidence_*.csv')):
        rows=list(csv.DictReader(path.open()));old=[r.copy() for r in rows]
        touched=[r for r in rows if r['evidence_id'] in WITHDRAW or r['evidence_id'] in desired and r!=desired[r['evidence_id']]]
        if touched:
            base=subprocess.check_output(['git','show','origin/main:data/'+path.name],cwd=ROOT,text=True)
            for r in touched:assert r['evidence_id'] not in base,'Cannot rewrite merged evidence'
        rows=[desired.get(r['evidence_id'],r) for r in rows if r['evidence_id'] not in WITHDRAW]
        if rows!=old:save(path,rows);journal.append(path.name+' unmerged evidence correction')
        have={r['evidence_id'] for r in rows}
        new=[e for e in evidence if e['evidence_id'] not in have and path.name==homes[e['record_id']]]
        if new:append_sorted(path,new,'evidence_id');journal.append(path.name+' append '+str(len(new)))
    if journal:
        with (HERE/'journal.txt').open('a') as f:f.write('\n'.join(journal)+'\n')
    print('changed operations:',len(journal))
if __name__=='__main__':
    if '--apply' in sys.argv:apply()
    else:print('13 evidence rows; 3 nonblank material fills, NOV fill withdrawn. Use --apply.')
