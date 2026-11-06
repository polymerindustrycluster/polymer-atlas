from research import D,Text
import json,re,hashlib
for p in (D/'raw').glob('*/firecrawl-response.json'):
 saved=json.loads(p.read_text());res=saved['result'];x=res.get('structuredContent')
 if not x:
  s=res['content'][0]['text'];x=json.loads(s) if s.lstrip().startswith('{') else {'error':s}
 x=x.get('data',x);h=x.get('html') or '';html=Text();html.feed(h);t=' '.join(' '.join(html.parts).split());t=re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}','[contact redacted]',t);t=re.sub(r'(?:\+?1[\s.-]*)?\(?[2-9]\d{2}\)?[\s.-]*\d{3}[\s.-]*\d{4}','[phone redacted]',t);out=p.with_name('firecrawl.txt');out.write_text(t);m=x.get('metadata',{});code=str(m.get('statusCode',''));rp=p.with_name('routes.json');rr=json.loads(rp.read_text());rr=[r for r in rr if r['kind']!='NAS_Firecrawl_raw_HTML'];rr.append(dict(org_id=p.parent.name,kind='NAS_Firecrawl_raw_HTML',attempted_url=saved['requested_url'],final_url=m.get('url',saved['requested_url']),http_status=code,availability='available' if len(t)>100 and code.startswith('2') else 'failed_or_sparse',raw_path=str(out.relative_to(D)),observed_date='2026-11-06',notes='Fresh maxAge0 formats=html; lead Text, no summary. '+str(x.get('error',''))));rp.write_text(json.dumps(rr,indent=2));print(p.parent.name,code,len(t))
