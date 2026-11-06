"""Build the complete retry overlay and disjoint handoff packets; never write data/."""
import csv,hashlib,json,subprocess,tempfile
from collections import Counter
from pathlib import Path
from retry import P,ROOT,CACHE,l1,read,write,target,on_page
METHODS=['curl','curl_https','curl_http1','curl_www','curl_www_http1','jina','firecrawl','firecrawl_pdf_text']
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def frozen():
    rows=read(P/'input.csv');m=json.loads((P/'frame-manifest.json').read_text());src=ROOT/m['source_audit']
    assert digest(src)==m['source_audit_sha256']
    assert digest(src.parent/'repair_leads.csv')==m['source_leads_sha256']
    original=[e for e in read(src) if e['judgment']=='FETCH_FAILED'];assert rows==original
    assert len(rows)==len({e['evidence_id'] for e in rows})==264 and len({e['url'] for e in rows})==96
    canonical={e['evidence_id']:e for f in sorted((ROOT/'data').glob('evidence_*.csv')) for e in read(f)}
    for e in rows:
        assert all(e[k]==v for k,v in canonical[e['evidence_id']].items()),e['evidence_id']
        assert e['quote']==l1.quote(canonical[e['evidence_id']]),e['evidence_id']
    assert [e['evidence_id'] for e in rows]==m['evidence_ids']
    return rows,canonical

def receipts(rows):
    urls={target(e['url']) for e in rows}-{''};out=[]
    for p in sorted(CACHE.glob('*.json')):
        f=json.loads(p.read_text())
        if f.get('url') not in urls or f.get('route') not in METHODS:continue
        f={**f,'receipt_path':str(p.relative_to(ROOT)),'receipt_sha256':digest(p)}
        if f.get('raw_path'):assert digest(ROOT/f['raw_path'])==f['raw_sha256'],p
        if f.get('text_path'):assert digest(ROOT/f['text_path'])==f['text_sha256'],p
        if f.get('provider_response_path'):assert digest(ROOT/f['provider_response_path'])==f['provider_response_sha256'],p
        out.append(f)
    return sorted(out,key=lambda f:(f['url'],METHODS.index(f['route'])))

def decision(e,fs,manual):
    q=e['quote'];readable=[f for f in fs if f['posture']=='ok']
    hits=[f for f in readable if q and on_page(q,ROOT/f['text_path']) is True]
    if hits:return 'SUPPORTED','',hits[0],'Preserved quote occurs as contiguous normalized words on the readable exact source; claim semantics not independently rejudged.'
    pick=(readable or [f for f in fs if f.get('text_path')] or fs or [{}])[0]
    if not q:return 'HOLD','NO_PRESERVED_QUOTE',pick,'Supply an unambiguous preserved quote and attributable exact primary URL; the existing row contains no extracted quote. No quote absence or claim-falsity finding.'
    if e['evidence_id'] in manual:
        h=manual[e['evidence_id']];assert h['preserved_quote']==q and h['source_ref']==e['source_ref']
        assert any(f.get('text_sha256')==h['raw_text_sha256'] for f in fs),'manual hold witness drift'
        return 'HOLD',h['hold_reason'],pick,h['settling_fact']
    complete=[f for f in readable if f.get('document_complete',True)]
    if complete:return 'NOT_SUPPORTED','',complete[0],'Preserved quote absent from all readable exact-source text projections observed; L11 needs a current raw witness/replacement. This does not refute the underlying claim.'
    if readable:return 'HOLD','INCOMPLETE_SOURCE',pick,'Obtain a complete source projection before declaring quote absence; provider warns the returned source may be partial.'
    if any(f['posture']=='WRONG_PAGE' for f in fs):return 'HOLD','SOURCE_BINDING',pick,'Resolve the cited URL versus returned host/path/query or native redirect conflict before using the returned text; no replacement citation is silently adopted.'
    return 'HOLD','FETCH_FAILED',pick,'Obtain a readable correctly bound primary document after recorded curl/browser-UA, protocol/host-alias, Jina and NAS attempts; failed routes are availability only.'

def page_numbers(q,f):
    if not q or not f.get('text_path'):return ''
    if f.get('format')!='pdf':return 'PDF parser text; page boundaries unavailable' if f.get('format')=='nas_pdf_text' else ''
    pages=(ROOT/f['text_path']).read_text().split('\f');hits=[]
    with tempfile.NamedTemporaryFile(mode='w+',encoding='utf-8',dir=CACHE,suffix='.page.txt') as tmp:
        for i,text in enumerate(pages,1):
            tmp.seek(0);tmp.truncate();tmp.write(text);tmp.flush()
            if on_page(q,Path(tmp.name)) is True:hits.append(str(i))
    return ';'.join(hits) or 'full PDF text; page not isolated'

def build_rows():
    rows,canonical=frozen();all_receipts=receipts(rows);manual={e['evidence_id']:e for e in read(P/'manual-holds.csv')};assert len(manual)==10 and set(manual)<={e['evidence_id'] for e in rows}
    result=[]
    for e in rows:
        fs=[f for f in all_receipts if f['url']==target(e['url'])];v,hold,f,reason=decision(e,fs,manual)
        binding='EXACT_URL' if f.get('posture')=='ok' else ('WRONG_PAGE' if f.get('posture')=='WRONG_PAGE' else ('NO_CITABLE_URL' if not target(e['url']) else 'UNAVAILABLE'))
        result.append({**canonical[e['evidence_id']],'prior_judgment':'FETCH_FAILED','preserved_quote':e['quote'],'original_url':e['url'],'fetch_url':target(e['url']),'quote_verdict':v,'lane_verdict':'VERIFIED' if v=='SUPPORTED' else 'STILL_UNCERTAIN','hold_reason':hold,'deciding_or_settling_fact':reason,'page_binding':binding,'effective_source_url':f.get('effective_source_url',f.get('effective_url','')),'route':f.get('route',''),'fetch_date':f.get('fetched_at',''),'http_status':f.get('http_status',''),'raw_text_path':f.get('text_path',''),'raw_text_sha256':f.get('text_sha256',''),'raw_body_path':f.get('raw_path',''),'raw_body_sha256':f.get('raw_sha256',''),'document_format':f.get('format',''),'quote_match_on_selected_text':('yes' if on_page(e['quote'],ROOT/f['text_path']) is True else 'no') if e['quote'] and f.get('text_path') else 'not_judged','pdf_pages':page_numbers(e['quote'],f),'receipt_paths':';'.join(x['receipt_path'] for x in fs)})
    return result,all_receipts

def main():
    before={p.name:digest(p) for p in (ROOT/'data').glob('*.csv')}
    result,rs=build_rows();fields=list(result[0])
    for name,rows in [('verdicts.csv',result),('reverification.csv',[e for e in result if e['quote_verdict']=='SUPPORTED']),('repair_leads.csv',[e for e in result if e['quote_verdict']=='NOT_SUPPORTED']),('holds.csv',[e for e in result if e['quote_verdict']=='HOLD'])]:
        if rows:write(P/name,rows)
        else:
            with open(P/name,'w',newline='') as f:csv.DictWriter(f,fieldnames=fields,lineterminator='\n').writeheader()
    cols=['url','route','http_status','effective_source_url','posture','reason','fetched_at','request_performed','document_complete','format','raw_path','raw_sha256','text_path','text_sha256','receipt_path','receipt_sha256','provider_response_path','provider_response_sha256','provider_warning']
    with open(P/'fetch_receipts.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols,lineterminator='\n',extrasaction='ignore');w.writeheader();w.writerows(rs)
    stats=dict(frozen_evidence_rows=264,cited_references=96,explicit_fetch_urls=len({e['fetch_url'] for e in result}-{''}),judgments={v:sum(e['quote_verdict']==v for e in result) for v in ['SUPPORTED','NOT_SUPPORTED','HOLD']},holds_by_reason=dict(Counter(e['hold_reason'] for e in result if e['quote_verdict']=='HOLD')),transport_receipts=len(rs),supplemental_inspections=len(read(P/'supplemental_fetches.csv')),canonical_changes=0,new_EVD_ids=0)
    (P/'result.json').write_text(json.dumps(stats,indent=2)+'\n');assert before=={p.name:digest(p) for p in (ROOT/'data').glob('*.csv')},'canonical data changed'
    print(json.dumps(stats))
if __name__=='__main__':main()
