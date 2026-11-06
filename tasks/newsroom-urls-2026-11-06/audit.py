"""Fetch candidate indexes for review; do not infer activity from copyright years."""
import concurrent.futures, json, re
from discover import HERE, Links, fetch
DATE=re.compile(r'\b(?:20\d\d-\d\d-\d\d|\d{1,2}/\d{1,2}/20\d\d|(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?\s+\d{1,2},?\s+20\d\d|\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+20\d\d)\b',re.I)
def audit(r):
    p=fetch(r['newsroom_url']);body=re.sub(r'<(script|style)\b.*?</\1>','',p['body'],flags=re.I|re.S)
    parsed=Links(body);text=' '.join(' '.join(parsed.text).split());dates=list(dict.fromkeys(m[0] for m in DATE.finditer(text)))
    return {'org_id':r['org_id'],'status':p['status'],'final':p['final'],'dates':dates[:12],'title':r['title'],'newsroom_url':r['newsroom_url']}
if __name__=='__main__':
    rows=[r for r in json.loads((HERE/'discovery.json').read_text()) if r['newsroom_url']]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:result=list(pool.map(audit,rows))
    (HERE/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(len(result),'candidate indexes inspected for actual text dates')
