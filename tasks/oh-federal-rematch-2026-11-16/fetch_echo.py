"""Resumable download; stream ZIP member and persist only public Ohio identity fields."""
import csv, hashlib, io, json, subprocess, zipfile
from pathlib import Path
csv.field_size_limit(10**8)
P = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/oh-federal-rematch')
P.mkdir(parents=True, exist_ok=True)
URL = 'https://echo.epa.gov/files/echodownloads/echo_exporter.zip'
z = P/'echo.zip'
subprocess.run(['curl','-fL','--retry','4','-C','-','-o',str(z),URL],check=True)
sha = hashlib.file_digest(z.open('rb'),'sha256').hexdigest()
cols = ['REGISTRY_ID','FAC_NAME','FAC_STREET','FAC_CITY','FAC_STATE','FAC_ZIP','TRI_IDS']
with zipfile.ZipFile(z) as archive:
    member = next(n for n in archive.namelist() if n.upper().endswith('.CSV'))
    with archive.open(member) as raw, (P/'ohio.csv').open('w') as out:
        reader = csv.DictReader(io.TextIOWrapper(raw,encoding='utf-8-sig',errors='strict'))
        cols = [c for c in cols if c in reader.fieldnames]
        assert set(cols) >= set(['REGISTRY_ID','FAC_NAME','FAC_STREET','FAC_CITY','FAC_STATE','FAC_ZIP'])
        writer=csv.DictWriter(out,cols,lineterminator='\n'); writer.writeheader()
        total=oh=0
        for r in reader:
            total+=1
            if r['FAC_STATE']=='OH':
                oh+=1; writer.writerow({k:r[k] for k in cols})
(P/'receipt.json').write_text(json.dumps(dict(url=URL,sha256=sha,member=member,total=total,ohio=oh,columns=cols,retrieved='2026-11-16'),indent=2)+'\n')
print(total,oh,flush=True)
