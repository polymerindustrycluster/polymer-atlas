#!/usr/bin/env python3
"""Check the frozen 56-person title packet against sanitized temporary source text."""
import argparse, collections, copy, csv, hashlib, json, re
from pathlib import Path
from urllib.parse import urlparse

def norm(s): return re.sub(r'\s+', ' ', s).strip()
def words(s): return re.findall(r'[a-z0-9]+', s.lower())
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def contains(s,q): return bool(q) and norm(q) in norm(s)
def hits(s,q):
    a,b=words(s),words(q)
    return [i for i in range(len(a)-len(b)+1) if a[i:i+len(b)]==b]
def private_data(p,n): return json.loads((p/n).read_text())
def body(cache,u):
    p=cache/(hashlib.sha256(u.encode()).hexdigest()+'.json')
    assert p.exists(), f'uninspectable missing cache: {u}'
    r=json.loads(p.read_text());assert r['status'].startswith('ok'), f'uninspectable source: {u}'
    return r['text']
def formal_title(s,t,kind):
    if kind=='formal_header': return any(norm(l).strip('#* ') == t for l in s.splitlines())
    if kind=='catalog_appointment': return any(norm(x)==t for l in s.splitlines() for x in l.split(';'))
    if kind=='catalog_named_professor': return f'({t})' in s and bool(re.search(r'(?m)^Professors:',s))
    if kind=='named_roster_entry': return any(contains(l,t) and ',' in l for l in s.splitlines())
    return False

def identity(r,s):
    a=words(s); name=words(r.get('identity_alias') or r['full_name']); first,last=name[0],name[-1]
    for i in hits(s,r['new_role_as_published']):
        w=a[max(0,i-40):i+len(words(r['new_role_as_published']))+40]
        if any(x==first and any(y==last for y in w[max(0,j-8):j+9]) for j,x in enumerate(w)):
            if words(r['full_name'])[-1]!=last and words(r['full_name'])[-1] not in w: continue
            return True
    return False

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--private-root',required=True,type=Path);ap.add_argument('--cache-root',type=Path,default=next((x for x in [Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/people-titles-3-2026-11-06/pages')] if x.exists()),Path('/tmp/atlas-l12-titles3-pages')));args=ap.parse_args()
    p,c=args.private_root,args.cache_root;out=Path(__file__).resolve().parent;root=out.parents[3]
    a=private_data(p,'input_snapshot.json');d=private_data(p,'dispositions.json');m=private_data(p,'manifest.json');binding=private_data(p,'title_binding.json')
    assert len(a)==len(d)==56 and len({r['person_id'] for r in a})==56
    assert [r['person_id'] for r in a]==[r['person_id'] for r in d], 'full frame/order accounting'
    assert set(r['verdict'] for r in d)<= {'VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF'}
    assert digest(p/'input_snapshot.json')==m['input_sha256'] and digest(p/'dispositions.json')==m['outcomes_sha256']
    assert digest(out/'verified.csv')==m['public_csv_sha256']; assert b'\r' not in (out/'verified.csv').read_bytes(), 'LF required'
    rows=list(csv.DictReader((out/'verified.csv').open()));v={r['person_id']:r for r in d if r['verdict']=='VERIFIED'}
    assert len(rows)==len(v) and {r['person_id'] for r in rows}==set(v)
    held={r['person_id']:r for r in csv.DictReader((root/'data/people.csv').open())}
    af={r['person_id']:r for r in a}
    roles={'professor','associate_professor','assistant_professor','research_professor','center_director_professor','senior_lecturer','staff_scientist','group_leader'}
    expected={'professor':r'Professor','associate_professor':r'Associate Professor','assistant_professor':r'Assistant Professor','staff_scientist':r'Staff Scientist','group_leader':r'^Group Leader\b'}  # anchored: 'Deputy Group Leader' has no SCHEMA §4.9 fold
    def quotecheck(u,q):
        assert 0<len(q.split())<=25 and contains(body(c,u),q), 'raw quote mismatch'
    def validate(r):
        f=v[r['person_id']];old=af[r['person_id']]
        for k in r: assert r[k]==f[k], f'public/private parity {k}'
        for k in ['full_name','institution_org_id']: assert r[k]==old[k]==held[r['person_id']][k]
        assert (r['old_role'],r['old_role_as_published'])==(old['role'],old['role_as_published'])
        live=(held[r['person_id']]['role'],held[r['person_id']]['role_as_published'])
        assert live in {(r['old_role'],r['old_role_as_published']),(r['new_role'],r['new_role_as_published'])}, 'live pair is neither the baseline nor the applied proposal'
        assert r['new_role'] in roles and re.search(expected[r['new_role']],r['new_role_as_published'],re.I)
        assert not re.search(r'emeritus|adjunct|teaching|practice|postdoc',r['new_role_as_published'],re.I)
        domains={'.'.join(urlparse(u).hostname.split('.')[-2:]) for u in [old['public_profile_url'],*old['sources'].split(';')] if urlparse(u).hostname}
        if 'syr.edu' in domains: domains.add('syracuse.edu')
        if 'marquette.edu' in domains: domains.add('mcw.edu')
        if 'clarkson.us' in domains: domains.add('clarkson.edu')
        for gate in ['title','polymer']:
            u,q=r[gate+'_url'],r[gate+'_quote'];assert u.startswith('https://') and '.'.join(urlparse(u).hostname.split('.')[-2:]) in domains
            assert u in [s['url'] for s in f['sources']], 'candidate-bound source ownership'
            s=body(c,u); quotecheck(u,q)
            assert not re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|mailto:|tel:',q)
        s=body(c,r['title_url']);assert contains(s,r['new_role_as_published']), 'title punctuation/case changed'
        assert formal_title(s,r['new_role_as_published'],binding[r['person_id']]['title_kind']), 'title not a formal field/header'
        assert identity(f,s), 'wrong person or >40-word identity boundary'
        if (r['old_role'],r['old_role_as_published'])==(r['new_role'],r['new_role_as_published']):assert 'already exact' in r['verdict_note']
    # Actual institutional known answers precede trusting the field/identity checks.
    known=private_data(p,'calibration.json')['actual_known_answers'];assert len(known)==4
    for k in known:
        s=body(c,k['url']);assert formal_title(s,k['title'],'formal_header') and contains(s,k['polymer_quote'])
        assert identity({'full_name':k['identity'],'new_role_as_published':k['title']},s)
    assert not formal_title('Xiwen Gong\nAssistant Professorship','Assistant Professor','formal_header')
    assert not formal_title('Xiwen Gong\nAssociate Professor','Assistant Professor','formal_header')
    assert not identity({'full_name':'Xiwen Gong','new_role_as_published':'Assistant Professor'},body(c,known[0]['url']))
    assert not hits('Materials science','Ma') and not hits('polymers','polymer')
    # Parent (integrator) withdrawals after the 75cdeb5 refutes: live row stays at baseline and the proposal must fail.
    withdrawn={r['person_id'] for r in csv.DictReader((out.parents[1]/'withdrawn.csv').open())}
    for r in rows:
        if r['person_id'] not in withdrawn:validate(r);continue
        assert (held[r['person_id']]['role'],held[r['person_id']]['role_as_published'])==(r['old_role'],r['old_role_as_published']), 'withdrawn person not at baseline'
        try:validate(r)
        except AssertionError:pass
        else:raise AssertionError('withdrawn proposal still validates')
    assert re.search(expected['group_leader'],'Group Leader / Polymer Engineer') and not re.search(expected['group_leader'],'Deputy Group Leader')
    # Live-pair fixtures: baseline and applied pairs pass; a mixed pair fails.
    r0=next(r for r in rows if r['person_id'] not in withdrawn and (r['old_role'],r['old_role_as_published'])!=(r['new_role'],r['new_role_as_published']));keep=held[r0['person_id']]
    for pair,ok in [((r0['old_role'],r0['old_role_as_published']),True),((r0['new_role'],r0['new_role_as_published']),True),((r0['old_role'],r0['new_role_as_published']+' X'),False)]:
        held[r0['person_id']]=dict(keep,role=pair[0],role_as_published=pair[1])
        try:validate(r0);passed=True
        except AssertionError:passed=False
        assert passed==ok,('live-pair fixture',pair)
    held[r0['person_id']]=keep
    false=copy.deepcopy(rows[0]);false['polymer_quote']='Fabricated polymer claim never printed in this source'
    try:quotecheck(false['polymer_url'],false['polymer_quote'])
    except AssertionError:pass
    else:raise AssertionError('false-quote mutation escaped')
    # Wrong identity with a genuine shared rank is rejected by identity itself.
    assert not identity({'full_name':known[3]['identity'],'new_role_as_published':'Assistant Professor'},body(c,known[0]['url']))
    count=0
    for r in d:
        assert r['sources'] and r['primary_unique_url_count']==len(r['sources'])<=6
        assert r['primary_unique_url_count']==r['individual_route_count']+len(r['shared_page_urls'])
        if r['verdict']=='STILL_UNCERTAIN':assert r['settling_fact']
        if r['verdict']=='REJECT':assert r['deciding_fact'] and len(r['deciding_quote'].split())<=25 and contains(body(c,r['deciding_url']),r['deciding_quote'])
        for ob in r['sources']:
            f=c/(hashlib.sha256(ob['url'].encode()).hexdigest()+'.json')
            if f.exists():
                text=json.loads(f.read_text())['text'];assert hashlib.sha256(text.encode()).hexdigest()==ob['sanitized_text_sha256']==ob['sanitized_cache_after_redaction_sha256']
            else: assert 'untsystem.edu' in ob['url'] and ob['status'].startswith('unfetchable')
            assert ob['hash_basis'] and ob['inspected_scope'] and ob['cache_incident_note'];count+=1
    rr=list(csv.DictReader((out/'rank_resolution.csv').open()))
    assert {r['person_id'] for r in rr}=={r['person_id'] for r in d if r.get('rank_resolution')}
    for r in rr:
        z=v[r['person_id']]['rank_resolution'];assert r['url']==z['url'] and r['quote']==z['quote']
        assert len(r['quote'].split())<=25 and contains(body(c,r['url']),r['quote'])
        assert not r['observed_source_date'] or re.fullmatch(r'\d{4}-\d{2}-\d{2}',r['observed_source_date'])
        if z.get('date_quote'):assert contains(body(c,r['url']),z['date_quote'])
    assert count==m['source_observations'] and len({s['url'] for r in d for s in r['sources']})==m['unique_urls_fetched']
    for f in out.iterdir():
        if f.suffix in {'.csv','.md','.json'}:
            s=f.read_text();assert not re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|mailto:|tel:',s), f'privacy {f.name}'
    print(json.dumps({'result':'PASS','candidate_people':56,'verdicts':dict(collections.Counter(r['verdict'] for r in d)),'verified_rechecks':len(rows),'proposed_field_edits':sum((r['old_role'],r['old_role_as_published'])!=(r['new_role'],r['new_role_as_published']) for r in rows),'rank_resolution_witnesses':len(rr),'source_observations':count,'known_answers':4,'negative_fixtures':5,'false_quote_mutation':'REJECTED','wrong_identity_mutation':'REJECTED','current_sanitized_cache_hashes':'MATCH'},indent=2))
if __name__=='__main__':main()
