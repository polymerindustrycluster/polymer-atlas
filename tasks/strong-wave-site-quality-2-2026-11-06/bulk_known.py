"""Known-answer test for the T2 bulk ECHO index: three registry ids must reproduce the independently banked OSHA/ITA name and street."""
import json,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from atlas import name_key,street_key
from bulk_sources import frs_by_registry_id
from prep import read
KNOWN=['SITE-011166','SITE-011171','SITE-011302']  # Mercury Paint, Nortek Powder Coating, Master Bond
if __name__=='__main__':
 fed={r['site_id']:json.loads(r['chosen']) for r in read(H/'federal_review.csv') if r['chosen']};inp={r['site_id']:r for r in read(H/'input.csv')};out=[]
 for sid in KNOWN:
  rid=next(x for x in inp[sid]['sources_with_ids'].split(';') if x.startswith('ECHO:'))[5:];f=fed[sid];hits=frs_by_registry_id(rid)
  ok=len(hits)==1 and name_key(hits[0]['FAC_NAME'])==name_key(f['name']) and street_key(hits[0]['FAC_STREET'])==street_key(f['street']) and hits[0]['FAC_CITY'].lower()==f['city'].lower() and hits[0]['FAC_STATE']==f['state']
  out.append(dict(site_id=sid,registry_id=rid,expected_name=f['name'],expected_street=f['street'],bulk_name=hits[0]['FAC_NAME'] if hits else '',bulk_street=hits[0]['FAC_STREET'] if hits else '',result='PASS' if ok else 'FAIL'))
 (H/'bulk_known_answers.json').write_text(json.dumps(out,indent=2)+'\n');print([(o['site_id'],o['result']) for o in out]);assert all(o['result']=='PASS' for o in out)
