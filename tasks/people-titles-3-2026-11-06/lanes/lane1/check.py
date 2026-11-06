"""Check this frozen56-person packet; missing private inputs/raw cache fail explicitly."""
import copy,csv,hashlib,json,re,sys
from pathlib import Path
from urllib.parse import urlparse
P=Path('/Users/johnswanson/.bb/thread-storage/thr_mcdghpxw8c/people-titles-3-private/lane1')
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'tools'));import fetch
COLS='person_id full_name institution_org_id old_role old_role_as_published new_role new_role_as_published title_url title_quote polymer_url polymer_quote verdict_note'.split()
PHONE=r'(?<![A-Za-z0-9])(?:\+?1[ ./-]*)?\(?\d{3}\)?[ ./-]*\d{3}[ ./-]*\d{4}(?![A-Za-z0-9])'
def sha(b):return hashlib.sha256(b).hexdigest()
def plain(s):
 s=re.sub(r'!?\[([^\]]*)\]\([^)]*\)',r'\1',s)
 return re.sub(r'^Position title:\s*','',s.strip('#*_ \t')).strip()
def folded(s):return ' '.join(s.split())
def title_spans(lines,title):
 for i in range(len(lines)):
  for n in range(1,4):
   if folded(' '.join(plain(x) for x in lines[i:i+n]))==title:yield i,n

def rank_entry(lines,identity,title):
 text='\n'.join(plain(l) for l in lines);assert fetch.found(text,identity),'wrong identity in bound entry'
 ids=fetch.words(identity)
 for i,n in title_spans(lines,title):
  before=fetch.words(' '.join(plain(x) for x in lines[:i]));positions=[j for j in range(len(before)-len(ids)+1) if before[j:j+len(ids)]==ids]
  if any(0<=len(before)-j-len(ids)<=40 for j in positions):return True
 raise AssertionError('exact title/identity-before-title40word binding failed')

def doc(url):
 f=fetch.CACHE/(sha(url.encode())+'.json');assert f.exists(),f'missing raw cache: {url}'
 d=json.loads(f.read_text());assert d['status'].startswith('ok'),f'uninspectable raw cache: {url}';return d['text']

def privacy(row):
 for k,v in row.items():
  assert not re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|mailto:|tel:',v,re.I),(k,'contact')
  assert not re.search(PHONE,v),(k,'phone-like value')
  if k.endswith('_url'):assert urlparse(v).scheme in ('http','https') and '@' not in v,(k,'URL')

def role_for(title):
 primary=title.split(' and Adjunct ')[0]
 assert not re.search(r'emerit|adjunct|teaching|practice|lecturer',primary,re.I),'excluded primary rank'
 if re.search(r'\bResearch (?:Assistant |Associate )?Professor|\b(?:Assistant |Associate )Research Professor',primary,re.I):return 'research_professor'
 if re.search(r'\bAssociate Professor\b',primary,re.I):return 'associate_professor'
 if re.search(r'\bAssistant Professor\b',primary,re.I):return 'assistant_professor'
 assert re.search(r'\bProfessor\b',primary,re.I),'no eligible rank';return 'professor'

def validate_row(r,frame,certs,manifest):
 privacy(r);pid=r['person_id'];assert pid in frame and pid in certs,'unapproved identity'
 f=frame[pid];c=certs[pid]
 for k in ['full_name','institution_org_id']:assert r[k]==f[k],('frozen identity',pid,k)
 assert (r['old_role'],r['old_role_as_published'])==(f['role'],f['role_as_published'])
 assert r['new_role']==role_for(r['new_role_as_published']),(pid,'rank enum')
 assert r['new_role_as_published']==c['title'],(pid,'approved exact title')
 for kind in ['title','polymer']:
  u=r[kind+'_url'];host=urlparse(u).hostname or '';assert any(host==d or host.endswith('.'+d) for d in c['institution_domains']),(pid,'institution domain')
  text=doc(u);assert fetch.found(text,r[kind+'_quote']),(pid,'false raw quote',kind)
  assert 0<len(fetch.words(r[kind+'_quote']))<=25,(pid,'quote word budget')
  assert u==c[kind+'_url'] and r[kind+'_quote']==c[kind+'_quote'],(pid,'person-scoped quote certificate',kind)
  assert sha(text.encode())==manifest[u]['current_redacted_cache_text_sha256'],(pid,'current cache certificate changed')
 lines=doc(r['title_url']).splitlines()[c['entry_start_line']:c['entry_end_line']]
 assert fetch.found('\n'.join(lines),r['title_quote']),(pid,'title quote outside entry')
 rank_entry(lines,c['published_identity'],r['new_role_as_published'])
 assert fetch.found(doc(r['polymer_url']),c['scope_owner']),(pid,'scope owner absent')
 if c.get('ownership_url'):assert fetch.found(doc(c['ownership_url']),c['ownership_quote']),(pid,'lab PI attribution')
 if (r['new_role'],r['new_role_as_published'])==(f['role'],f['role_as_published']):assert 'already exact' in r['verdict_note'],pid

def main():
 frame_list=json.loads((P.parent/'lane1.json').read_text());assert len(frame_list)==56 and len({r['person_id'] for r in frame_list})==56
 assert sha((P.parent/'lane1.json').read_bytes())=='4b247bcd5dee38664e5188734fed5b24b36595f7930f0a872d1f1d17f6cfca6c'
 assert len({(re.sub(r'\W+','',r['full_name'].casefold()),r['institution_org_id']) for r in frame_list})==56
 frame={r['person_id']:r for r in frame_list};disp=json.loads((P/'dispositions.json').read_text());assert [r['person_id'] for r in disp]==[r['person_id'] for r in frame_list]
 assert all(r['verdict'] in ('VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF') and r['review_stage']=='adjudicated' and r['fact'] and r['source_observations'] for r in disp)
 assert all(s['status'] and s['inspected_scope'] and s['hash_basis'] for r in disp for s in r['source_observations'])
 with (OUT/'verified.csv').open(newline='') as f:
  rd=csv.DictReader(f);assert rd.fieldnames==COLS;rows=list(rd)
 assert len({r['person_id'] for r in rows})==len(rows)==27
 assert {r['person_id'] for r in rows}=={r['person_id'] for r in disp if r['verdict']=='VERIFIED'}
 certs={r['person_id']:r for r in json.loads((P/'certificates.json').read_text())};manifest={r['url']:r for r in json.loads((P/'source_manifest.json').read_text())}
 assert len(manifest)==128 and sum(len(s['person_ids']) for s in manifest.values())==132
 for u,s in manifest.items():
  f=fetch.CACHE/(sha(u.encode())+'.json');assert f.exists(),('missing source observation',u);d=json.loads(f.read_text())
  assert sha(d['text'].encode())==s['current_redacted_cache_text_sha256'] and d['status']==s['status'],('changed source observation',u)
  assert not s['actual_review'] or s['status'].startswith('ok')
 for r in disp:
  expected={u for u,s in manifest.items() if r['person_id'] in s['person_ids']};assert expected=={s['url'] for s in r['source_observations']} and 1<=len(expected)<=6
  assert r['has_actual_target_body_review']==any(s['actual_review'] for s in r['source_observations'])
  assert all('pending' not in s['inspected_scope'].lower() for s in r['source_observations'])
 for r in rows:validate_row(r,frame,certs,manifest)
 # Three actual bound title records, then defects that must fail.
 calibration=json.loads((P/'calibration_final.json').read_text())
 for c in calibration['actual_records']:rank_entry(doc(c['url']).splitlines()[c['start']:c['end']],c['identity'],c['title'])
 assert not fetch.found('depolymerization copolymer polymeric','polymer')
 bad=copy.deepcopy(rows[0]);bad['polymer_quote']='ZZZ invented false statement not present'
 try:validate_row(bad,frame,certs,manifest)
 except AssertionError:pass
 else:raise AssertionError('falsequote mutation survived')
 katz=certs['PERSON-000864'];page=doc(katz['title_url']);assert fetch.found(page,'Michael Kessler') and fetch.found(page,'Professor')
 try:rank_entry(page.splitlines()[katz['entry_start_line']:katz['entry_end_line']],'Michael Kessler','Professor')
 except AssertionError:pass
 else:raise AssertionError('wrongperson neighboring-PI mutation survived')
 try:rank_entry(['Target Person','Adjunctive Professor'],'Target Person','Adjunct Professor')
 except AssertionError:pass
 else:raise AssertionError('rank-affix mutation survived')
 with (OUT/'rank_resolution.csv').open(newline='') as f:
  rd=csv.DictReader(f);assert rd.fieldnames==['person_id','url','observed_source_date','quote','note'];res=list(rd)
 for r in res:
  privacy(r);assert r['person_id'] in frame and fetch.found(doc(r['url']),r['quote']) and len(fetch.words(r['quote']))<=25;assert re.fullmatch(r'\d{4}-\d{2}-\d{2}',r['observed_source_date'])
 print(json.dumps({'result':'PASS','input_people':56,'dispositions':len(disp),'verified':len(rows),'uncertain':sum(r['verdict']=='STILL_UNCERTAIN' for r in disp),'quotes':len(rows)*2,'rank_resolution_witnesses':len(res),'actual_rank_calibrations':3,'falsequote_rejected':True,'wrongperson_neighbor_rejected':True,'rank_affix_rejected':True,'unreviewed_candidates':0,'source_manifest_urls':len(manifest)},indent=2))
if __name__=='__main__':main()
