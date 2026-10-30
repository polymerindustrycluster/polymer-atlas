"""Restore exact reviewed large artifacts from bounded transport parts; offline."""
import pathlib,json,hashlib,base64,shutil,sys
p=pathlib.Path(__file__).parent
dest=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'build/f4-reviewed');dest.mkdir(parents=True,exist_ok=True)
for f in p.iterdir():
 if f.is_file() and f.name not in json.loads((p/'transport-manifest.json').read_text()): shutil.copy2(f,dest/f.name)
for name,item in json.loads((p/'transport-manifest.json').read_text()).items():
 out=b''
 for part in item['parts']:
  raw=(p/part['path']).read_bytes()
  assert hashlib.sha256(raw).hexdigest()==part['sha256'],part['path']
  out+=base64.b64decode(raw,validate=False)
 assert len(out)==item['bytes'] and hashlib.sha256(out).hexdigest()==item['sha256'],name
 target=dest/name
 if target.exists(): assert target.read_bytes()==out, str(target)+' differs; refusing overwrite'
 else:target.write_bytes(out)
 print(name,len(out),item['sha256'])
