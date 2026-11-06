"""Apply current institution-verified role/title pairs, preserving every other claim."""
import csv, json, re, sys
from pathlib import Path
from datetime import date
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from shard_io import append_sorted
from fetch import get, found

DATE = '2026-11-06'
FIELDS = {'role','role_as_published','sources','last_verified'}

def read(path):
    with open(path,newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))

def write(path,rows,columns):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=columns,lineterminator='\n')
        w.writeheader();w.writerows(rows)

def on_domain(url,domains):
    host=urlparse(url).hostname or ''
    return any(host==d or host.endswith('.'+d) for d in domains)

def require_pair(row,allowed_roles,is_lab=False):
    title=row['new_role_as_published']
    assert row['new_role'] in allowed_roles, (row['person_id'],'unknown role enum')
    assert title and not re.search(r'\b(is an?|joined|promoted|per page|listed as)\b|"',title,re.I), 'narrative title'
    primary=re.split(r'\s+and\s+Adjunct\s+',title,flags=re.I)[0]
    assert not re.search(r'emerit|adjunct|visiting|professor\s*(?:of\s+teaching|[-–]\s*educator)|teaching\s+professor|practice',primary,re.I), 'excluded primary appointment; HOLD'
    university_roles={'professor','associate_professor','assistant_professor','research_professor','center_director_professor','senior_lecturer'}
    assert row['new_role'] in (allowed_roles-university_roles if is_lab else university_roles), 'wrong institution-grain role'
    if not is_lab:
        text=primary.lower()
        if re.search(r'research\s+(?:(?:assistant|associate)\s+)?professor|(?:assistant|associate)\s+research\s+professor|professor\s+of\s+research',text):
            assert row['new_role']=='research_professor', 'research-rank mismatch'
        elif re.search(r'assistant\s+professor',text):
            assert row['new_role']=='assistant_professor', 'assistant-rank mismatch'
        elif re.search(r'associate\s+professor',text):
            assert row['new_role']=='associate_professor', 'associate-rank mismatch'
        elif re.search(r'\bprofessor\b',text):
            assert row['new_role'] in {'professor','center_director_professor'}, 'professor-rank mismatch'
        elif re.search(r'senior\s+lecturer',text):
            assert row['new_role']=='senior_lecturer', 'lecturer-rank mismatch'
        else:
            raise AssertionError('university title lacks explicit eligible professor/lecturer rank; HOLD')

def prepare():
    people=read(ROOT/'data/people.csv');by={r['person_id']:r for r in people}
    expected=json.loads((HERE/'expected.json').read_text())
    packet=read(HERE/'reviewed.csv');raw={(r['person_id'],r['url'],r['quote']):r for r in read(HERE/'rawcheck.csv')}
    domains={r['institution_org_id']:set(r['domains'].split(';')) for r in read(HERE/'institution_domains.csv')}
    roles=set(json.loads((ROOT/'docs/schema/vocab.json').read_text())['vocabularies']['ROLES']['values'])
    labs={r['org_id'] for r in read(ROOT/'data/ecosystem.csv') if r['ecosystem_subtype']=='government_lab_agency'}
    assert len({r['person_id'] for r in packet})==len(packet), 'duplicate person proposal'
    evidence=[]
    for r in packet:
        pid=r['person_id'];current=by[pid];old=expected[pid]
        assert current['full_name']==r['full_name']==old['full_name']
        assert current['institution_org_id']==r['institution_org_id']==old['institution_org_id']
        assert (r['old_role'],r['old_role_as_published'])==(old['role'],old['role_as_published']), 'packet baseline mismatch'
        require_pair(r,roles,r['institution_org_id'] in labs)
        for gate in ('title','polymer'):
            u,q=r[f'{gate}_url'],r[f'{gate}_quote']
            assert u.startswith('https://') and '@' not in u and on_domain(u,domains[r['institution_org_id']]), (pid,'outside institution',u)
            ck=raw[(pid,u,q)]
            page=get(u)
            assert page['status'].startswith('ok') and found(page['text'],q), (pid,gate,'raw quote not found')
            assert ck['person_id']==pid and ck['found']==ck['entry_checked']=='yes'
            assert q and len(q.split())<=25 and re.fullmatch('[0-9a-f]{64}',ck['sanitized_text_sha256'])
            if gate=='title':
                assert ck['surname_near']==ck['title_exact']=='yes'
                assert r['new_role_as_published'] in ' '.join(page['text'].split()), (pid,'printed title mismatch')
            else:
                assert ck['current_person_scope']=='yes'
            eid=r[f'evidence_{gate}_id']
            assert 283000<=int(eid[4:])<=284999
            claim='existence' if gate=='title' else 'scope'
            detail=f"role {r['new_role']}; role_as_published {r['new_role_as_published']}" if gate=='title' else 'Current institution-owned polymer research for this held person; specialties unchanged'
            evidence.append(dict(evidence_id=eid,record_table='people',record_id=pid,claim_type=claim,claim_detail=detail,
                source_class='own_site',source_ref=u,observed_date=DATE,tier_effect='supports_A',
                created_by='codex atlas-L12-people-titles-3',notes='Raw words in order: '+q))
        desired={'role':r['new_role'],'role_as_published':r['new_role_as_published'],'last_verified':DATE}
        for k,v in desired.items():
            assert current[k] in (old[k],v),(pid,k,'main changed; reconcile before replay')
            current[k]=v
        assert set(old['sources'].split(';'))<=set(current['sources'].split(';')), (pid,'source removed since base')
        current['sources']=';'.join(dict.fromkeys(current['sources'].split(';')+[r['title_url'],r['polymer_url']]))
    for r in read(HERE/'rank_resolution.csv'):
        pid=r['person_id'];u,q=r['url'],r['quote'];eid=r['evidence_id']
        assert pid in {p['person_id'] for p in packet}, 'rank witness outside applied packet'
        assert on_domain(u,domains[by[pid]['institution_org_id']]) and u.startswith('https://')
        ck=raw[(pid,u,q)]
        assert ck['found']==ck['entry_checked']=='yes'
        if ck['surname_near']!='yes':
            assert u==next(p['title_url'] for p in packet if p['person_id']==pid), 'rank witness lacks bound person identity'
        assert len(q.split())<=25 and found(get(u)['text'],q), (pid,'dated rank quote')
        if r['observed_source_date']:
            assert date.fromisoformat(r['observed_source_date']).isoformat()==r['observed_source_date']<=DATE
        assert 283000<=int(eid[4:])<=284999
        by[pid]['sources']=';'.join(dict.fromkeys(by[pid]['sources'].split(';')+[u]))
        evidence.append(dict(evidence_id=eid,record_table='people',record_id=pid,claim_type='existence',
            claim_detail='Own-institution rank-resolution witness '+(r['observed_source_date'] or '(calendar date not published)')+': '+r['note'],
            source_class='own_site',source_ref=u,observed_date=DATE,tier_effect='supports_A',
            created_by='codex atlas-L12-people-titles-3',notes='Raw words in order: '+q))
    assert len({e['evidence_id'] for e in evidence})==len(evidence)
    have={r['evidence_id']:r for r in read(ROOT/'data/evidence_people.csv')}
    for e in evidence:
        if e['evidence_id'] in have:
            assert have[e['evidence_id']]==e, (e['evidence_id'],'evidence collision')
    foreign_ids={e['evidence_id'] for f in (ROOT/'data').glob('evidence_*.csv') if f.name!='evidence_people.csv' for e in read(f)}
    assert not foreign_ids & {e['evidence_id'] for e in evidence}, 'foreign evidence-shard ID collision'
    return people,[e for e in evidence if e['evidence_id'] not in have],len(packet),len(evidence)

def main():
    people,new_evidence,count,total=prepare()
    write(ROOT/'data/people.csv',people,list(people[0]))
    if new_evidence:
        append_sorted(ROOT/'data/evidence_people.csv',new_evidence,'evidence_id')
    print(f'{count} held people rechecked; {len(new_evidence)} evidence rows appended this replay; {total} packet evidence rows')

if __name__=='__main__':
    main()
