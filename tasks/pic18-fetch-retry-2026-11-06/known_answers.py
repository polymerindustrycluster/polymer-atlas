"""Five previously verified real records, plus transport/quote/page-identity defects."""
import hashlib,json
from retry import P,ROOT,CACHE,fetch,assess,on_page,same_page,l1
cases=[
('SITE-014006','https://calspas.com/zp/albums/calspas/pdf/press-releases/PR-CalSpas-SantaCop2015.pdf','The company produces premium collections of lifestyle products from its headquarters in Pomona, California'),
('SITE-006049','https://www.jmeagle.com/sites/default/files/JM%20Eagle%20NMSDC%20MBE%20Certificate%204-30-2026.pdf','J-M Manufacturing Company, Inc Doing Business As JM Eagle'),
('SITE-001828','https://www.pexco.com/wp-content/uploads/2025/09/ISO9001-2015-certificate-Cincinnati.pdf','Performance Plastics Limited 4435 Brownway Avenue Cincinnati, OH 45209'),
('known-SSI','https://www.ssibio.com/contact-us','1310 Thurman Street Lodi, CA 95240'),
('known-Rubbercraft','https://www.rubbercraft.com/','co-molding')]
results=[]
for eid,url,q in cases:
 f=fetch(url,'curl');assert f['posture']=='ok',(eid,f)
 path=ROOT/f['text_path'];assert on_page(q,path) is True,(eid,q)
 assert on_page(q+' zzzcalibrationneedlezzz',path) is False
 assert on_page(' '.join(reversed(l1.ns['words'](q))),path) is False
 assert on_page('',path) is None
 wrong=assess(url,'curl',ROOT/f['raw_path'],f,source_url='https://example.com/wrong-page');assert wrong['posture']=='WRONG_PAGE',wrong
 results.append(dict(record_id=eid,url=url,known_quote=q,format=f['format'],text_path=f['text_path'],text_sha256=f['text_sha256'],fetched_at=f['fetched_at'],positive='PASS',false_tail='REJECTED',wrong_order='REJECTED',wrong_page='REJECTED'))
 print('PASS known',eid,f['format'],flush=True)
raw=CACHE/'known-wall.raw';raw.write_text('<html><body>Please verify you are human before accessing this website. This security challenge checks whether a browser is human and protects against automated requests.</body></html>')
f=assess('https://example.com/page','curl',raw,dict(http_status=200,effective_url='https://example.com/page',exit_code=0,fetched_at='fixture'));assert f['posture']=='FETCH_FAILED'
raw=CACHE/'known-empty.raw';raw.write_bytes(b'');assert assess('https://example.com/page','curl',raw,dict(http_status=200,effective_url='https://example.com/page',exit_code=0))['posture']=='FETCH_FAILED'
raw=CACHE/'known-jina-404.raw';raw.write_text('URL Source: https://example.com/page\nWarning: Target URL returned error 404: Not Found\nMarkdown Content:\nA normal looking company page with navigation and many ordinary words that could otherwise pass a superficial text length gate.')
assert assess('https://example.com/page','jina',raw,dict(http_status=200,effective_url='https://r.jina.ai/https://example.com/page',exit_code=0))['posture']=='FETCH_FAILED'
assert same_page('http://www.example.com/a/','https://EXAMPLE.com/a')
assert not same_page('https://example.com/a?x=A','https://example.com/a?x=a')
assert not same_page('https://example.com/a','https://example.com/b')
(P/'known-answers.json').write_text(json.dumps(dict(cases=results,wall='REJECTED',empty='REJECTED',query_case='REJECTED'),indent=2)+'\n')
print('PASS5actualknownrecords;false-tail/order/page/wall/empty/query controls;no canonical writes')
