"""Sample public US Manufacturer listings; discard all personal/contact fields."""
import json,csv,sys,random,re,html,subprocess,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'));import atlas
from build_cbp_size_classes import STATE_FIPS_TO_USPS
HERE=Path(__file__).parent

def frame(d):
 return sorted([r for r in d.values() if r['organization-type']=='Manufacturer' and r['state'] in set(STATE_FIPS_TO_USPS.values()) and r['opt'] is False],key=lambda r:r['recordId'])

def write(name,rows):
 with (HERE/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

# Discovery excerpts have no schema field for business contacts; omit the whole excerpt.
CONTACT=re.compile(r'@|\b(?:ph(?:one)?|fax|fx|tel(?:ephone)?)\s*:|(?<!\d)\+?\d[\d(). -]{5,}\d',re.I)

def excerpt(text):
 match=re.search(r'polymer|composite|fiberglass|reinforced plastic|carbon fiber',text,re.I)
 quote=text[max(0,match.start()-50):match.end()+150] if match else ''
 return '' if CONTACT.search(quote) else quote

def main():
 assert len(frame({'a':dict(recordId='1',state='OH',opt=False,**{'organization-type':'Manufacturer'}),'b':dict(recordId='2',state='ON',opt=False,**{'organization-type':'Manufacturer'}),'c':dict(recordId='3',state='OH',opt=True,**{'organization-type':'Manufacturer'})}))==1
 d=json.load(open(sys.argv[1]));rows=frame(d);assert len(d)==len({r['recordId'] for r in d.values()})==252
 tables=atlas.load_tables(ROOT/'data');sample=random.Random(20261106).sample(rows,20)
 def work(pair):
  i,r=pair;ded=atlas.dedupe(tables,domain=r['website'],name=r['name']);hits={h['id'] for s in ded['steps'] for h in s['hits']};exact={h['id'] for s in ded['steps'][:2] for h in s['hits']}
  p=Path('/tmp/l5b-acma-sample-'+str(i)+'.html');url=re.sub('^http:','https:',r['website'] or '')
  proc=subprocess.run(['curl','-LsS','--max-time','35','-A','Mozilla/5.0',url,'-o',str(p),'-w','%{http_code}'],capture_output=True,text=True)
  text=p.read_text(errors='replace') if p.exists() else '';text=html.unescape(re.sub('<[^>]+>',' ',re.sub(r'<(script|style)\b.*?</\1>','',text,flags=re.S)));text=re.sub(r'\s+',' ',text)
  quote=excerpt(text) if proc.stdout=='200' else ''
  return dict(record_id=r['recordId'],name=r['name'],website=r['website'],city=r['city'],state=r['state'],source_type=r['organization-type'],opt_out='false',source_url='https://acmanet.org/wp-json/mg/v1/content/directory?type=&state=',fetch_status=proc.stdout,scope_quote=quote,atlas_ids=';'.join(sorted(hits)),verdict='DUPLICATE_OF' if len(exact)==1 else 'STILL_UNCERTAIN',duplicate_of=next(iter(exact)) if len(exact)==1 else '',verified_new=0,street_check='not supplied by public list API; no site claim',reason='singleton domain/name candidate ends at held record; organization grain only' if len(exact)==1 else 'settling fact: primary current polymer-composite process, legal identity and US business address; ambiguous alias/parent candidates held')
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p:out=list(p.map(work,enumerate(sample)))
 write('sample.csv',out)
 counts=dict(public_listings=len(d),manufacturer_listings=sum(r['organization-type']=='Manufacturer' for r in d.values()),us_manufacturer_not_opted_out=len(rows),sampled=20)
 (HERE/'counts.json').write_text(json.dumps(counts,indent=2)+'\n');print(counts)
if __name__=='__main__':main()
