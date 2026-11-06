"""NLR title packet: exact old inputs, current raw quotes and owner grade rule."""
import csv, json, hashlib, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PRIVATE = Path('/Users/johnswanson/.bb/thread-storage/thr_mcdghpxw8c/people-titles-3-private')
sys.path.insert(0, str(PRIVATE/'tools'))
from fetch import get, found, words

inputs = json.loads((PRIVATE/'root16.json').read_text())
dispositions = json.loads((PRIVATE/'root16/dispositions.json').read_text())
assert len(inputs) == len(dispositions) == len({r['person_id'] for r in dispositions}) == 16
assert [r['person_id'] for r in inputs] == [r['person_id'] for r in dispositions]
assert sum(r['verdict']=='VERIFIED' for r in dispositions) == 5
assert sum(r['verdict']=='STILL_UNCERTAIN' for r in dispositions) == 11
packet = list(csv.DictReader((Path(__file__).parent/'verified.csv').open()))
assert {r['person_id'] for r in packet} == {r['person_id'] for r in dispositions if r['verdict']=='VERIFIED'}
old = {r['person_id']:r for r in inputs}
for r in packet:
    assert r['institution_org_id'] == 'ORG-002815'
    assert r['new_role'] == r['old_role'] == old[r['person_id']]['role'], 'B-NLR-1(a) grade KEEP'
    for urlkey, quotekey in [('title_url','title_quote'),('polymer_url','polymer_quote')]:
        u,q = r[urlkey],r[quotekey]
        assert u.startswith('https://') and (u.split('/')[2]=='nlr.gov' or u.split('/')[2].endswith('.nlr.gov'))
        d=get(u)
        assert d['status'].startswith('ok') and found(d['text'],q) and len(q.split())<=25
        if quotekey=='title_quote':
            assert found(d['text'],r['new_role_as_published'])
            t,a,s = words(d['text']),words(q),words(r['full_name'])[-1]
            assert any(t[i:i+len(a)]==a and s in t[max(0,i-40):i+len(a)+40] for i in range(len(t)-len(a)+1)), 'wrong person rank'
    assert not re.search(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}|mailto:|tel:', ' '.join(r.values()))
calibration=json.loads((PRIVATE/'calibration.json').read_text())
assert len(calibration['cases'])==3 and calibration['result']=='PASS'
for text,q in [('depolymerization','polymer'),('Associate Professor','Assistant Professor'),
               ('Professor Kumar studies polymers. Wang studies metals.','Wang studies polymers')]:
    assert not found(text,q)
assert not found(get(packet[0]['title_url'])['text'],'FICTITIOUS RANK'), 'false rank accepted'
print('PASS16 exact NLR identities:5VERIFIED/11STILL_UNCERTAIN;10rawquotes;gradeKEEP ruling;title/surname/own-domain/privacy;3knownanswers+4negativecontrols')
