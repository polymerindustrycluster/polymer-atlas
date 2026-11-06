"""Fresh own-page re-fetch of every candidate, without any LinkedIn request."""
import concurrent.futures
import csv
import json
import collections
import classify
import discover as d
import build as b


def verify(row):
    page=d.fetch(row['source_url'])
    matches=[x for x in d.Links(page['body']).links if x['linkedin_url']==row['linkedin_url'] and x['href']==row['href'] and classify.re_header_footer(x['location'])] if page['status']=='200' else []
    result={**row,'result':'PASS' if matches else 'FAIL','raw_sha256':page.get('raw_sha256',''),'fetch_status':page['status'],'request_count':len(page['attempts'])}
    if matches:
        result.update(final_url=page['url'],location=matches[0]['location'])
    return result,page['attempts']


def main():
    candidates=b.read(d.HERE/'proposals.csv')
    assert candidates
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        checked=list(pool.map(verify,candidates))
    outcomes=[r for r,_ in checked]
    classify.write('raw-outcomes.csv',outcomes)
    passed=[r for r in outcomes if r['result']=='PASS']
    classify.write('rawcheck.csv',passed)
    fields=list(candidates[0])
    classify.write('proposals.csv',[{k:r[k] for k in fields} for r in passed])
    verdicts=b.read(d.HERE/'verdicts.csv')
    failed={r['org_id'] for r in outcomes if r['result']!='PASS'}
    for row in verdicts:
        if row['org_id'] in failed:
            row.update(verdict='STILL_UNCERTAIN',linkedin_url='',settling_or_deciding_fact='Need a fresh exact own header/footer anchor; raw re-fetch failed or published anchor changed. No absence inferred.')
    classify.write('verdicts.csv',verdicts)
    (d.HERE/'raw-requests.json').write_text(json.dumps([{'org_id':r['org_id'],'attempts':attempts} for r,attempts in checked],indent=2)+'\n')
    print('Raw census:',len(candidates),'candidates =',len(passed),'PASS +',len(failed),'held organization rows; no skipped candidate.')
    print('Final',dict(collections.Counter(r['verdict'] for r in verdicts)))

if __name__=='__main__':
    main()
