"""Conservative identity binding; every frozen org receives a verdict."""
import collections
import csv
import json
from pathlib import Path
import build as b
import discover as d


def write(name,rows,fields=None):
    with (d.HERE/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]),lineterminator='\n')
        w.writeheader();w.writerows(rows)


def main():
    frame=b.read(d.HERE/'inputs.csv')
    pages={p['website']:p for p in json.loads((d.HERE/'discovery.json').read_text())}
    owners=d.domain_owners()
    verdicts,proposals=[],[]
    for row in frame:
        website=row['website']
        own=website if '://' in website else 'https://'+website
        page=pages.get(website)
        value=''
        if row['linkedin_url']:
            reason='Existing navigation retained; no change.'
        elif row['status']!='active':
            reason='Need current exact-entity own-site navigation; frozen operating status is not active.'
        elif not website:
            reason='Need a verified held own website before navigation discovery.'
        elif len(owners.get(d.domain(own),set()))!=1:
            reason='Need exact held-entity/parent identity bridge; multiple held entities share this website domain.'
        elif not page or page['status']!='200':
            reason='Need reachable own header/footer; route unavailable or external/unsafe redirect blocked. No absence inferred.'
        else:
            links=page['links'];values={x['linkedin_url'] for x in links}
            if len(values)!=1:
                reason='Need one unambiguous own header/footer company-page link; zero or multiple recognized company URLs.'
            else:
                value=next(iter(values))
                if not b.identity(row,value):
                    value=''
                    reason='Need exact held name/trade-name bridge to the published company slug; do not substitute a parent/brand.'
                else:
                    link=next(x for x in links if re_header_footer(x['location']))
                    proposals.append({'org_id':row['org_id'],'linkedin_url':value,'source_url':website,'final_url':page['url'],'href':link['href'],'location':link['location'],'observed_date':'2026-11-06','cohort':row['cohort'],'verification_tier':row['verification_tier']})
                    reason='One header/footer company anchor; slug matches held legal/trade name; website domain belongs to this one held entity.'
        verdicts.append({'org_id':row['org_id'],'cohort':row['cohort'],'verdict':'VERIFIED' if value else 'STILL_UNCERTAIN','linkedin_url':value,'settling_or_deciding_fact':reason,'source_url':website})
    write('verdicts.csv',verdicts)
    write('proposals.csv',proposals)
    print('Frame',len(frame),'=',dict(collections.Counter(r['verdict'] for r in verdicts)),'organization rows')
    print('Verified cohorts',dict(collections.Counter(r['cohort'] for r in proposals)))
    print('Hold reasons',dict(collections.Counter(r['settling_or_deciding_fact'] for r in verdicts if r['verdict']!='VERIFIED')))


def re_header_footer(location):
    return 'header' in location.lower() or 'footer' in location.lower()


if __name__=='__main__':
    main()
