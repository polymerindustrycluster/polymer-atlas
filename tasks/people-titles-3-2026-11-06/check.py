"""Exact title-pass yield, bounded claim changes, raw witnesses and replay oracle."""
import csv, hashlib, io, json, re, subprocess, sys
from unittest.mock import patch
from build import HERE, ROOT, FIELDS, read, require_pair, on_domain, prepare
from fetch import found, get, words


def near(text, quote, surname):
    t,q,s=words(text),words(quote),words(surname)
    return bool(s) and any(t[i:i+len(q)]==q and any(t[j:j+len(s)]==s for j in range(max(0,i-40),min(len(t),i+len(q)+40))) for i in range(len(t)-len(q)+1))


def main():
    packet=read(HERE/'reviewed.csv'); verdicts=read(HERE/'verdicts.csv')
    expected=json.loads((HERE/'expected.json').read_text())
    assert len(expected)==len(verdicts)==len({v['person_id'] for v in verdicts})==184
    assert set(expected)=={v['person_id'] for v in verdicts}
    assert all(v['verdict'] in {'VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF'} and v['settling_fact'] for v in verdicts)
    assert {r['person_id'] for r in packet}=={v['person_id'] for v in verdicts if v['verdict']=='VERIFIED'}
    origins={'atlas-cleanup':ROOT/'tasks/atlas-cleanup-2026-11-03/holds.csv',
             'role-title-recheck-2':ROOT/'tasks/role-title-recheck-2-2026-11-03/holds.csv'}
    source_ids={name:{r['record'] for r in read(path) if r['record'].startswith('PERSON-')} for name,path in origins.items()}
    assert len(set.union(*source_ids.values()))==214
    assert len(set.union(*source_ids.values())-set(expected))==30
    for v in verdicts:
        assert set(v['source_lists'].split(';'))=={name for name,ids in source_ids.items() if v['person_id'] in ids}
    for s in read(HERE/'source_counts.csv'):
        assert int(s['raw_candidate_people'])==len(source_ids[s['source_list']])
        assert int(s['deferred_pr149_people'])==len(source_ids[s['source_list']]-set(expected))
        members=[v for v in verdicts if s['source_list'] in v['source_lists'].split(';')]
        assert int(s['raw_candidate_people'])==int(s['deferred_pr149_people'])+len(members)
        for verdict in ('VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF'):
            assert int(s[verdict])==sum(v['verdict']==verdict for v in members)
    for row in read(HERE/'rawcheck.csv'):
        text=get(row['url'])['text'];assert found(text,row['quote']),(row['person_id'],'quote')
        if row['surname_witness']:assert near(text,row['quote'],row['surname_witness']),(row['person_id'],'surname')
    roles=set(json.loads((ROOT/'docs/schema/vocab.json').read_text())['vocabularies']['ROLES']['values'])
    for a,q in [('depolymerization','polymer'),('polymers','polymer'),('biomaterials','materials'),('polymer advanced synthesis','polymer synthesis'),('Associate Professor','Assistant Professor')]:
        assert not found(a,q),(a,q)
    assert not near('Professor Kumar studies polymers. Wang studies metals.','Professor','Smith')
    assert on_domain('https://profile.example.edu/person',{'example.edu'})
    assert not on_domain('https://example.edu.evil.example/person',{'example.edu'})
    base=(HERE/'base_commit.txt').read_text().strip()
    def before(name):
        return list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',f'{base}:data/{name}'],cwd=ROOT,text=True))))
    old=before('people.csv'); now=read(ROOT/'data/people.csv')
    oldby={r['person_id']:r for r in old};nowby={r['person_id']:r for r in now}
    assert oldby.keys()<=nowby.keys(),'people removed'
    pids={r['person_id'] for r in packet}
    assert not(set(nowby)-set(oldby)),'title pass created people'
    for pid,r in oldby.items():
        for k,v in r.items():
            if pid not in pids or k not in FIELDS:assert nowby[pid][k]==v,(pid,k,'unowned change')
    for r in packet:
        p=nowby[r['person_id']]
        assert (p['role'],p['role_as_published'])==(r['new_role'],r['new_role_as_published'])
        assert set(oldby[r['person_id']]['sources'].split(';'))<=set(p['sources'].split(';'))
    oldev=before('evidence_people.csv');ev=read(ROOT/'data/evidence_people.csv');evby={e['evidence_id']:e for e in ev}
    assert len(evby)==len(ev)
    assert all(evby.get(e['evidence_id'])==e for e in oldev),'old evidence changed'
    rank_rows=read(HERE/'rank_resolution.csv')
    ownids={r[k] for r in packet for k in ('evidence_title_id','evidence_polymer_id')}|{r['evidence_id'] for r in rank_rows}
    assert set(evby)-{e['evidence_id'] for e in oldev}==ownids
    assert len(ownids)==2*len(packet)+len(rank_rows)
    for r in packet:
        assert {evby[r[k]]['claim_type'] for k in ('evidence_title_id','evidence_polymer_id')}=={'existence','scope'}
    # Exercise production guards without writing either canonical CSV.
    sample=packet[0];files=[ROOT/'data/people.csv',ROOT/'data/evidence_people.csv']
    hashes=[hashlib.sha256(f.read_bytes()).hexdigest() for f in files]
    for changes in [{'new_role':'invented_rank'},{'new_role':'professor' if sample['new_role']!='professor' else 'assistant_professor'},{'new_role_as_published':'Assistant Professor FICTITIOUS RANK'}, {'polymer_quote':'FICTITIOUS POLYMER PROJECT'}]:
        bad=[dict(r,**changes) if r['person_id']==sample['person_id'] else r for r in packet]
        def altered(path):
            if path==HERE/'reviewed.csv':return bad
            rows=read(path)
            if path==HERE/'rawcheck.csv' and 'polymer_quote' in changes:
                rows.append(dict(next(r for r in rows if r['person_id']==sample['person_id'] and r['gate']=='polymer'),quote=changes['polymer_quote']))
            return rows
        try:
            with patch('build.read',side_effect=altered):prepare()
        except (AssertionError,KeyError):pass
        else:raise AssertionError(('production guard accepted mutation',changes))
    foreign=next(f for f in (ROOT/'data').glob('evidence_*.csv') if f.name!='evidence_people.csv')
    def collide(path):
        rows=read(path)
        if path==foreign:rows.append(dict(evby[sample['evidence_title_id']]))
        return rows
    try:
        with patch('build.read',side_effect=collide):prepare()
    except AssertionError:pass
    else:raise AssertionError('late foreign-shard collision accepted')
    for title in ['Adjunct Professor','Professor Emeritus','Associate Professor of Practice']:
        try:require_pair(dict(sample,new_role='professor',new_role_as_published=title),roles)
        except AssertionError:pass
        else:raise AssertionError(('excluded title accepted',title))
    assert hashes==[hashlib.sha256(f.read_bytes()).hexdigest() for f in files]
    for f in HERE.rglob('*'):
        if f.is_file() and f.suffix in {'.csv','.json','.md'}:
            assert not re.search(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}|mailto:|tel:',f.read_text()),(f,'contact leak')
    subprocess.run([sys.executable,str(HERE/'build.py')],cwd=ROOT,check=True)
    assert hashes==[hashlib.sha256(f.read_bytes()).hexdigest() for f in files],'replay changed bytes'
    counts={v:sum(r['verdict']==v for r in verdicts) for v in ['VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF']}
    print(f'PASS184 candidate people; {counts}; {len(packet)} existing people/0creates/{len(ownids)}append-only evidence; exact titles/own domains/rawquotes/7matcher negatives/8production mutations/pre-pass preservation/byte-identical replay')

if __name__=='__main__':main()
