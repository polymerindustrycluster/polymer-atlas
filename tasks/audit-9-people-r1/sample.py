"""Evidence-blind claim whitelist extraction; never exports URLs/notes/evidence."""
import csv, json, random, hashlib
from pathlib import Path
SEED=2026103109
ROOT=Path(__file__).resolve().parents[2]
out=Path('/workspace/shared/audit9-blind'); out.mkdir(exist_ok=True)
rows=list(csv.DictReader((ROOT/'data/people.csv').open()))
byid={r['person_id']:r for r in rows}
assert len(rows)==len(byid)==476
frame=[f'PERSON-{i:06d}' for i in range(74,477)]
assert len(frame)==403 and all(x in byid for x in frame)
sample=sorted(random.Random(SEED).sample(frame,50))
judgment=['PERSON-000476','PERSON-000448','PERSON-000409','PERSON-000084']
mini=[f'PERSON-{i:06d}' for i in [3,41,42,52,54,56,60]]
inst={}
for p in [ROOT/'data/ecosystem.csv',*sorted((ROOT/'data').glob('organizations_*.csv'))]:
 for r in csv.DictReader(p.open()): inst[r['org_id']]=r['legal_name']
def claim(i):
 r=byid[i]
 return {**{k:r[k] for k in ['person_id','full_name','institution_org_id','role','role_as_published','verification_tier']},'institution':inst[r['institution_org_id']], 'frames':';'.join(k for k,v in [('random',sample),('judgment',judgment),('held_correction',mini)] if i in v)}
ids=sorted(set(sample+judgment+mini))
claims=[claim(i) for i in ids]
held=[{k:claim(i)[k] for k in ['person_id','full_name','institution_org_id','institution']} for i in sorted(byid) if int(i.split('-')[1])<=73]
(out/'held_names.json').write_text(json.dumps(held,indent=2)+'\n')
(out/'claims.json').write_text(json.dumps(claims,indent=2)+'\n')
for n in range(5): (out/f'batch{n+1}.json').write_text(json.dumps(claims[n::5],indent=2)+'\n')
manifest={'data_pin':'604fea8ef1d9fe3f17049aeb053d157345a61de5','seed':SEED,'method':'CPython random.Random(seed).sample(sorted PERSON-000074..000476 IDs, 50), sort sampled IDs for presentation; no replacement of overlap','frame_n':403,'random_ids':sample,'judgment_ids':judgment,'held_correction_ids':mini,'random_judgment_overlap':sorted(set(sample)&set(judgment)),'unique_audited_n':len(ids),'claim_file_sha256':hashlib.sha256((out/'claims.json').read_bytes()).hexdigest()}
(ROOT/'tasks/audit-9-people-r1/sample_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2)); print('Batches', [len(claims[n::5]) for n in range(5)])
