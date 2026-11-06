"""L8-B packet coverage, availability, quotes and uncertainty check; read-only."""
import csv,json,re
from collections import Counter
from pathlib import Path
from research import found
HERE=Path(__file__).resolve().parent

def check(rows,inputs,logs):
    ids=[r['org_id'] for r in rows]
    assert len(rows)==len(inputs)==72,'count'
    assert len(set(ids))==len(ids),'uniqueness'
    assert ids==[r['org_id'] for r in inputs],'exact input IDs/rank order'
    assert [int(r['rank']) for r in rows]==list(range(83,155)),'ranks/no skips'
    allowed={'own_site','government_filing','registry','directory','press','platform_category','harvest_roster'}
    for r in rows:
        ls=[l for l in logs if l['org_id']==r['org_id']]
        assert 1<=len(ls)<=6 and len(ls)==int(r['fetch_count']),'fetch cap/accounting'
        assert r['source_class'] in allowed
        assert r['observed_date']=='2026-11-06'
        assert not r['source_date'] or re.fullmatch(r'\d{4}-\d{2}-\d{2}',r['source_date'])
        assert r['verdict'] in {'VERIFIED','STILL_UNCERTAIN','REJECT','DUPLICATE_OF'}
        assert not r['proposed_status'] and not r['successor_org_id'],'no status motions'
        if r['quote']:
            assert len(r['quote'].split())<=25,'quote length'
            assert r['raw_check']=='yes'
            assert found(Path(r['raw_cache_path']).with_suffix('.txt').read_text(),r['quote']),'raw quote'
        if r['verdict']=='VERIFIED':
            assert r['quote'] and r['raw_check']=='yes' and len(ls)<=5,'verified witness/reserve'
        elif r['verdict']=='STILL_UNCERTAIN':
            assert len(r['settling_fact'].split())>=12,'meaningful named settling fact'
            assert r['proposed_status']=='','no negative inference'
    return True

def main():
    rows=list(csv.DictReader(open(HERE/'verdicts.csv')));inputs=list(csv.DictReader(open(HERE/'input.csv')));logs=list(csv.DictReader(open(HERE/'fetch_log.csv')))
    # Known answers include a real primary success, absent quote and actual failed route.
    gf=Path('/tmp/atlas-L8-cont-B/ORG-003117-1.txt').read_text()
    pdf=Path('/tmp/atlas-L8-cont-B/ORG-003480-4.txt').read_text()
    assert found(gf,'Nobody is better equipped to custom fabricate fittings')
    assert not found(gf,'This company permanently closed on January 1 2026')
    assert found(pdf,'We manufacture a range of compostable products')
    assert found('Ritmo’s fusion — equipment','Ritmos fusion equipment')
    assert not found('','operating') and any(l['http']=='000' for l in logs)
    check(rows,inputs,logs)
    mutations=[]
    for name,edit in [('missing',lambda rs:rs.pop()),('duplicate',lambda rs:rs.__setitem__(1,rs[0])),('quote-absent',lambda rs:rs[0].update(quote='company definitely permanently closed forever')),('empty-settling',lambda rs:next(r for r in rs if r['verdict']=='STILL_UNCERTAIN').update(settling_fact=''))]:
        rs=[dict(r) for r in rows];edit(rs)
        try:check(rs,inputs,logs)
        except AssertionError:mutations.append(name)
        else:raise AssertionError('silent mutation pass: '+name)
    result={'check':'L8-B packet coverage/raw/uncertainty','inputs':len(inputs),'verdicts':dict(Counter(r['verdict'] for r in rows)),'organizations_attempted':len({l['org_id'] for l in logs}),'fetch_attempts':len(logs),'http200_responses':sum(l['http']=='200' for l in logs),'organizations_with_http200':len({l['org_id'] for l in logs if l['http']=='200'}),'raw_quote_rows':sum(r['raw_check']=='yes' for r in rows),'known_answers':5,'mutation_failures_expected':mutations,'result':'PASS'}
    print(json.dumps(result,indent=2));(HERE/'check-result.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
