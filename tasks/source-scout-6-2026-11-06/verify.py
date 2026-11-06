"""Own-site verification of an unmatched sampled establishment: <=6 fetches (1 Bing search + <=5 pages). No closure inference: a failed fetch is only
an availability note. VERIFIED needs the street address, the entity name and a polymer word on the SAME own-site domain. Polymer word hits are a
scope LEAD only (ring/scope is an owner ruling); this verifies existence + address + liveness on the date fetched. The polymer-process wording must sit on the
same page that states the address: a parent's domain-wide wording is not a site source (Atlas rule: never push parent facts down to a site)."""
import base64,hashlib,html,re,subprocess,sys,time,urllib.parse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'));import atlas
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
SKIP=('linkedin.','facebook.','instagram.','twitter.','x.com','youtube.','bing.','google.','yelp.','mapquest.','dnb.com','zoominfo.','bloomberg.','crunchbase.','manta.','buzzfile.',
 'opencorporates.','bbb.org','yellowpages.','chamberofcommerce.','indeed.','glassdoor.','wikipedia.','usaspending.','sam.gov','fda.gov','epa.gov','thomasnet.','alibaba.','amazon.','ebay.','dol.gov','trade.gov',
 'gov/','.gov','datanyze.','rocketreach.','apollo.io','cylex','loc8nearme.','nearme','mapcarta','bizapedia','opengovus','corporationwiki','govtribe','highergov','govcb','sec.gov','pinterest.','tiktok.','reddit.','scribd.','issuu.','pdfslide','data.gov','data.world','mapcarta','cybo.')
POLY=re.compile(r'\b(plastics?|polymers?|polymeric|rubber|resins?|elastomers?|silicones?|thermoplastics?|thermoset|latex|polyethylene|polypropylene|pvc|nylon|polyurethane|ptfe|peek)\b',re.I)  # MATERIALS only (processes such as extrusion/thermoforming/injection molding live in PROC): coatings/adhesives/composites/foam/gaskets are not polymer evidence by themselves
PROC=r'(?:manufactur\w*|mold\w*|extru\w+|compound\w*|fabricat\w*|thermoform\w*|laminat\w*|formulat\w*|produc(?:e|es|ed|ing|tion)|process(?:ing|ed|or|ors))'  # real process terms only: the noun 'product(s)' is catalog text, not a process
SURG=re.compile(r'\bplastics?\s+(?:and\s+\w+\s+)?surg\w+',re.I)  # 'plastic surgery' is a medical specialty, not a polymer
ALT=POLY.pattern[3:-3]  # the alternatives inside \b( ... )\b; they MUST be grouped before being embedded (an ungrouped '|' made bare 'ptfe' inside 'ePTFE' a process hit)
PROCESS=re.compile(r'\b(?:'+ALT+r')\b.{0,80}?\b'+PROC+r'\b|\b'+PROC+r'\b.{0,80}?\b(?:'+ALT+r')\b',re.I)
def process_witness(page):
 """The matched polymer-word/process-word span (<=160 chars), committed so check.py can re-test it offline; '' if none."""
 m=PROCESS.search(page);return re.sub(r'\s+',' ',page[m.start():m.end()])[:160] if m else ''
def fetch(url,timeout=25):
 try:
  p=subprocess.run(['curl','-sL','-m',str(timeout),'-A',UA,'--max-filesize','3000000','-w','\n%{http_code} %{url_effective}',url],capture_output=True,timeout=timeout+10)
  body,_,tail=p.stdout.rpartition(b'\n');code,_,final=tail.decode('latin-1').partition(' ');return int(code or 0),final.strip(),body
 except Exception:return 0,url,b''
BLOCK=r'a|li|ul|ol|p|div|br|h[1-6]|tr|td|th|table|nav|header|footer|section|article|aside|main|button|label|option|select|dt|dd|dl|figure|figcaption|blockquote|form|address|summary|title'
def text(b):
 """Page text with element boundaries (anchors, list items, block tags) turned into newlines. PROCESS never crosses a newline, so a witness can never join
 two elements ('KOVA Plastics' + 'Contract Manufacturing' navigation anchors); inline tags (b, span, em, ...) stay in the flow and source line wraps are spaces."""
 t=b.decode('utf-8','replace');t=re.sub(r'<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>',' ',t,flags=re.S|re.I)
 t=re.sub(r'\s+',' ',t);t=re.sub(r'</?(?:'+BLOCK+r')\b[^>]*>','\n',t,flags=re.I);t=re.sub(r'<[^>]+>',' ',t)
 return re.sub(r' *\n[ \n]*','\n',re.sub(r'[ \t]+',' ',html.unescape(t))).strip()
def bing(q):
 """Bing HTML results -> [(url,title,cite,snippet)]; the redirect carries the real URL as base64 after u=a1."""
 code,_,b=fetch('https://www.bing.com/search?q='+urllib.parse.quote_plus(q));out=[]
 for li in re.findall(r'<li class="b_algo".*?</li>',b.decode('utf-8','replace'),flags=re.S):
  m=re.search(r'<h2[^>]*><a[^>]*href="([^"]+)"[^>]*>(.*?)</a>',li,flags=re.S)
  if not m:continue
  u=html.unescape(m.group(1));e=re.search(r'[?&]u=a1([A-Za-z0-9_-]+)',u)
  if e:
   try:u=base64.urlsafe_b64decode(e.group(1)+'='*(-len(e.group(1))%4)).decode()
   except Exception:continue
  cp=re.search(r'<p[^>]*>(.*?)</p>',li,flags=re.S);clean=lambda x:html.unescape(re.sub(r'<[^>]+>','',x or ''))
  if u.startswith('http') and not any(x in u.lower().split('?')[0] for x in SKIP):out.append((u,clean(m.group(2)),'',clean(cp.group(1) if cp else '')))
 return code,out
def core_tokens(name):
 return [t for t in atlas.name_key(re.sub(r'\(.*?\)|\bd/?b/?a\b.*|,.*$','',name,flags=re.I)).split() if len(t)>1][:4]
def candidates(name,street,city,state):
 """<=2 searches. A result must carry the entity's first name token in its domain, title or snippet; score by domain/title/city/street-number hits."""
 toks=[t for t in core_tokens(name) if not t.isdigit()];searches=0;ranked={}
 if not toks:return 0,[]
 num=(street.split() or [''])[0]
 for q in (f'"{" ".join(toks)}" {city} {state}',f'{" ".join(toks)} {street} {city} {state}'):
  searches+=1;_,res=bing(q)
  for u,title,_,snip in res:
   host=urllib.parse.urlparse(u).netloc.lower().removeprefix('www.');hay=(title+' '+snip).lower();t0=toks[0]
   if len(t0)<3 or (t0 not in host.replace('-','').replace('.','') and t0 not in hay):continue
   sc=(2 if t0 in host.replace('-','') else 0)+(1 if t0 in title.lower() else 0)+(1 if city.lower() in hay else 0)+(2 if num.isdigit() and num in hay else 0)
   if sc>=2:ranked[u]=max(ranked.get(u,0),sc)
  if ranked:break
  time.sleep(1)
 return searches,[u for u,_ in sorted(ranked.items(),key=lambda x:-x[1])]
def addr_found(page,street):
 """street number + street name tokens contiguous in the page after the Atlas street normalisation; the trailing suffix may be absent."""
 K=atlas.street_key(street).split()
 if len(K)<2 or not K[0].isdigit():return False
 P=[atlas.SUFFIX.get(t,t) for t in atlas.squash(page).split()]
 for kk in (K,K[:-1] if len(K)>=3 else K):
  n=len(kk)
  if any(P[i:i+n]==kk for i in range(len(P)-n+1)):return True
 return False
GENERIC=set('inc llc co company corp corporation group holdings holding international industries products product'.split())
def name_found(page,name):
 """The entity's leading name tokens (up to 3, trailing generic words dropped) appear CONTIGUOUSLY on the page: 'FilmTec Water USA' is not satisfied by 'FilmTec Water Singapore'."""
 toks=[t for t in core_tokens(name) if not t.isdigit()][:3]
 while len(toks)>1 and toks[-1] in GENERIC:toks.pop()
 P=atlas.squash(page).split();n=len(toks)
 return bool(toks) and any(P[i:i+n]==toks for i in range(len(P)-n+1))
PHONE=re.compile(r'\(?\b\d{3}\)?[-. ]?\d{3}[-. ]\d{4}\b|\+\d[\d .()-]{7,}\d');EMAIL=re.compile(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+')
def address_quote(page,street):
 """<=110 characters around the street address, phone numbers and e-mail addresses redacted (AGENTS section 6: business address only)."""
 w=[x for x in re.findall(r'[A-Za-z]+',street) if len(x)>1];num=street.split()[0]
 m=re.search(rf'{re.escape(num)}\s+(?:[NSEWnsew]\.?\s+)?(?:\w+\s+){{0,2}}?{re.escape(w[0]) if w else ""}',page) or re.search(rf'\b{re.escape(num)}\b',page)
 if not m:return ''
 q=re.sub(r'\s+',' ',page[max(0,m.start()-25):m.end()+60]);return EMAIL.sub('[email]',PHONE.sub('[phone]',q)).strip()
def verify(name,street,city,state,seed_urls=(),max_fetch=6):
 """Returns dict(fetches,url,status,sha256,address_found,name_found,polymer_words,process_hit,quote,note). process_hit = a polymer word within 80 chars of a process word on the visited pages of that domain."""
 used=0;pages=[];out=dict(fetches=0,url='',status='',sha256='',address_found=0,name_found=0,polymer_words='',process_hit=0,process_witness='',quote='',note='')
 urls=list(seed_urls)
 if not urls:
  n,urls=candidates(name,street,city,state);used+=n
  if not urls:out.update(fetches=used,note='no search result carried the entity name');return out
 seen=set();queue=urls[:2]+[f'{urllib.parse.urlparse(urls[0]).scheme}://{urllib.parse.urlparse(urls[0]).netloc}/'] if urls else []
 while queue and used<max_fetch:
  u=queue.pop(0)
  if u in seen:continue
  seen.add(u);used+=1;code,final,b=fetch(u)
  if code!=200 or not b:out['note']+=f'{u} http {code}; ';continue
  t=text(b);host=urllib.parse.urlparse(final).netloc.lower().removeprefix('www.')
  pages.append((final,code,hashlib.sha256(b).hexdigest(),t))
  if used<max_fetch-1 and len(pages)<=2:  # follow own-domain contact/location links once
   for h in re.findall(r'href="([^"#]+)"',b.decode('utf-8','replace')):
    h=urllib.parse.urljoin(final,html.unescape(h))
    if urllib.parse.urlparse(h).netloc.lower().removeprefix('www.')==host and re.search(r'contact|location|about|facilit|plant|where',h,re.I) and h not in seen and h not in queue:queue.append(h)
 for final,code,sha,t in pages:
  t=SURG.sub(' ',t);a,n=addr_found(t,street),name_found(t,name);w=sorted({m.group(1).lower() for m in POLY.finditer(t)})[:6]
  if a and n:
   out.update(url=final,status=code,sha256=sha,address_found=1,name_found=1,polymer_words=';'.join(w),process_hit=int(bool(PROCESS.search(t))),process_witness=process_witness(t),quote=address_quote(t,street),
    note=(out['note']+' domain-wide process wording on another visited page; not the address page; ' if PROCESS.search('\n'.join(p[3] for p in pages)) and not PROCESS.search(t) else out['note']));break
 else:
  if pages:final,code,sha,t=pages[0];out.update(url=final,status=code,sha256=sha,name_found=int(name_found(t,name)),polymer_words=';'.join(sorted({m.group(1).lower() for m in POLY.finditer(t)})[:6]))
 out['fetches']=used;return out
def offline_known_answers():
 """No network. Regex, matcher and element-boundary known answers; check.py calls this on every run."""
 assert not PROCESS.search('ePTFE membranes are made worldwide. Our manufacturing sites are listed below')  # word-internal match (the original ungrouped-alternation bug)
 assert not PROCESS.search('We manufacture speakers and peeking devices') and not PROCESS.search('Plastic bags for sale '+'x '*60+'manufacturing sites')  # bare alternative / out of range
 assert not PROCESS.search('Extruded Dense Extruded') and not PROCESS.search('Contact us about injection molding and extrusion')  # a process word is not a polymer word
 assert PROCESS.search('Rubber extrusion and plastic injection molding')
 assert not PROCESS.search('Plastic and Cosmetic Surgery Products') and not PROCESS.search(SURG.sub(' ','plastic and cosmetic surgery manufacturing'))  # plastic surgery
 assert not PROCESS.search('Products Anti-Static Bags, Poly / Plastic') and not PROCESS.search('Products AllStock Yorker Packaging KOVA Plastics')  # catalog / nav text
 assert PROCESS.search('We manufacture custom rubber and plastic parts') and PROCESS.search('Injection molding of thermoplastic resins') and not PROCESS.search('Contact us about our supply of office products')
 # element boundaries: the Alltrista nav (two anchors) must not join into a witness; one anchor 'Rubber Molding' and inline tags still match
 nav=text(b'<ul><li><a href="/kova-plastics">KOVA Plastics</a></li><li><a href="/contract-manufacturing">Contract Manufacturing</a></li></ul>')
 assert not PROCESS.search(nav) and PROCESS.search(text(b'<a href="/custom-rubber-molding">Rubber Molding</a>')) and PROCESS.search(text(b'<p>We manufacture\n<b>rubber</b> parts</p>'))
 assert not PROCESS.search(text(b'<a href="/a">Extruded Sponge</a><a href="/b">Floor Mats</a><a href="/c">Rubber</a>'))
 assert name_found('FilmTec Water Singapore Pte','FilmTec Water USA, LLC')==False and name_found('Ebco Inc Elgin','Ebco, Inc.') and name_found('visit forbo siegling llc','Forbo Siegling LLC')
 assert '[phone]' in address_quote('Contact 1330 Holmes Road Elgin IL 60123 Phone: 847-531-9500 x','1330 Holmes Road') and '[email]' in address_quote('1330 Holmes Road info@ebcoinc.com','1330 Holmes Road')
 assert addr_found('Visit us at 33587 Walker Rd., Avon Lake','33587 Walker Road') and not addr_found('33587 Walter Rd','33587 Walker Road') and not addr_found('Suite 5587 Walker','33587 Walker Road')
def live_known_answers():
 """Network: records whose answer we hold: two held sites with their own-site address, a wrong-street control, a no-site control."""
 a=verify('Eptam Plastics','2 Riverside Business Park','Northfield','NH');assert a['address_found']==1 and a['name_found']==1,a
 b=verify('Eptam Plastics','999 Nowhere Boulevard','Northfield','NH');assert b['address_found']==0,b
 c=verify('Avient Corporation','33587 Walker Road','Avon Lake','OH');assert c['address_found']==1,c
 return [a['fetches'],b['fetches'],c['fetches']]
CORPUS=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/cache/site_corpus')
def corpus_hit(street):
 """T1 shared site corpus (own sites of held Atlas organizations): does any cached page state this street address? -> source URL or ''."""
 K=atlas.street_key(street).split()
 if len(K)<2 or not K[0].isdigit():return ''
 pat=rf'\b{K[0]}\s+(?:[nsew]\.?\s+)?{re.escape(K[1])}\b'
 r=subprocess.run(['rg','-l','-i','-m1','--glob','*.txt',pat,str(CORPUS)],capture_output=True,text=True)
 for f in r.stdout.split()[:1]:
  h=subprocess.run(['rg','-l','-F',f'"text_file": "{Path(f).name}"','--glob','*.json',str(CORPUS)],capture_output=True,text=True).stdout.split()
  if h:return json.loads(Path(h[0]).read_text())['final_url']
 return ''
if __name__=='__main__':offline_known_answers();print('known answers PASS; live fetches',live_known_answers())
