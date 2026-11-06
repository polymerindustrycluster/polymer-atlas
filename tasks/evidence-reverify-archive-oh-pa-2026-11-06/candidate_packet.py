"""Find continuation witnesses in the shared cache without making any web/API requests."""
import hashlib
import json
import re
from urllib.parse import urlsplit
from shared import HERE,ROOT,BASE,house,bound_verdicts
from archive import FIELDS, same_capture


def key(url):
    p=urlsplit(url)
    return p.netloc.lower().removeprefix('www.'),p.path.rstrip('/'),p.query,p.fragment


def main():
    refs={r['archive_ref'] for r in house.read(ROOT/'data/archive_links.csv')}
    for p in house.CACHE.glob('*.available.json'):
        ref=json.loads(p.read_text()).get('archive_ref')
        if ref:refs.add(ref)
    for stream in (ROOT/'build').glob('l1-cdx-links*.csv'):
        refs.update(r['archive_ref'] for r in house.read(stream))
    captures={}
    for ref in sorted(refs,reverse=True):
        meta=house.CACHE/(hashlib.sha256(ref.encode()).hexdigest()+'.json')
        if not meta.exists():continue
        f=json.loads(meta.read_text())
        m=re.fullmatch(r'https://web\.archive\.org/web/(\d{14})/(https?://\S+)',ref)
        if m and f['status']=='ok' and same_capture(f['attempts'][-1]['effective_url'],ref):
            captures.setdefault(key(m[2]),[]).append((ref,m[1],f))
    inherited=house.read(BASE/'archive_links.csv')
    old_ids={r['evidence_id'] for r in house.read(BASE/'inputs.csv')}
    links=[]
    for eid,e in bound_verdicts().items():
        if eid in old_ids:continue
        if e['judgment']!='SUPPORTED':continue
        for ref,stamp,f in captures.get(key(e['url']),[]):
            if house.on_page(e['quote'],ROOT/f['page']):
                links.append(dict(evidence_id=eid,archive_ref=ref,captured_at=stamp[:4]+'-'+stamp[4:6]+'-'+stamp[6:8],created_by='atlas-L1-reverify-archive'))
                break
    house.write(HERE/'new_archive_links.csv',sorted(links,key=lambda r:r['evidence_id']),FIELDS)
    house.write(HERE/'archive_links.csv',sorted(inherited+links,key=lambda r:r['evidence_id']),FIELDS)
    eligible = {eid:e for eid,e in bound_verdicts().items() if eid not in old_ids and e['judgment']=='SUPPORTED'}
    linked = {r['evidence_id'] for r in links}
    outcomes = [dict(evidence_id=eid,url=e['url'],archive_ref='',status='PENDING_SERIALIZED_DISCOVERY') for eid,e in eligible.items() if eid not in linked]
    house.write(HERE/'archive_outcomes.csv',outcomes,['evidence_id','url','archive_ref','status'])
    leads = [r for state in ('OH','PA') for r in house.read(HERE/state/'repair_leads.csv')]
    house.write(HERE/'repair_leads.csv',leads,list(leads[0]))
    print('new candidate links',len(links),'inherited',len(inherited),flush=True)


if __name__=='__main__':main()
