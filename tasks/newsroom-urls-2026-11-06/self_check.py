"""Defect injection: the URL/feed gate must reject HTTP failure, off-domain redirects and empty feeds."""
from unittest.mock import patch
from check import check
from discover import domain, feed_count, LABEL
assert LABEL.fullmatch('News + Events')
assert not LABEL.fullmatch('Some individual news article')
assert domain('https://news.example.co.uk/a')=='example.co.uk'
assert feed_count('<rss><channel><item/></channel></rss>')==1
row={'org_id':'test','website':'https://example.com','newsroom_url':'https://example.com/news','newsroom_feed_url':''}
for response in [{'status':'403','final':row['newsroom_url']},{'status':'200','final':'https://other.com'}]:
    with patch('check.fetch',return_value=response):
        try:check(row)
        except AssertionError:pass
        else:raise AssertionError('defect missed')
row.update(newsroom_url='',newsroom_feed_url='https://example.com/feed')
with patch('check.fetch',return_value={'status':'200','url':row['newsroom_feed_url'],'final':row['newsroom_feed_url'],'body':'<rss><channel/></rss>'}):
    try:check(row)
    except AssertionError:pass
    else:raise AssertionError('empty feed missed')
print('PASS: label/domain/feed checks; injected HTTP error, off-domain redirect and empty feed all rejected')
import json
from discover import HERE
known=json.loads((HERE/'known_answers.json').read_text())
assert {r['org_id']:r['newsroom_url'] for r in known}=={'Avient':'https://www.avient.com/company/news-events','RPM':'https://www.rpminc.com/news/','GEON':'https://www.geon.com/news'}
print('PASS: 3 saved live known-answer results match expected newsroom indexes')
import csv
inputs=list(csv.DictReader(open(HERE/'inputs.csv')))
verdicts=list(csv.DictReader(open(HERE/'verdicts.csv')))
discovery=json.loads((HERE/'discovery.json').read_text())
for rows in (inputs,verdicts,discovery):assert len({r['org_id'] for r in rows})==len(rows)==1049
assert {r['org_id'] for r in inputs}=={r['org_id'] for r in verdicts}=={r['org_id'] for r in discovery}
assert all(1<=len(r['attempts'])<=6 for r in discovery)
assert all(r['note'] for r in verdicts if r['verdict']=='STILL_UNCERTAIN')
print('PASS: 1049/1049 input IDs uniquely reconciled to discovery and verdicts; discovery fetch budget <=6; holds explicit')
row={'org_id':'test','website':'https://example.com','newsroom_url':'https://example.com/news','newsroom_feed_url':'https://example.com/feed'}
page={'status':'200','url':row['newsroom_url'],'final':row['newsroom_url'],'body':'<a href="/">Home</a>'}
feed={'status':'200','url':row['newsroom_feed_url'],'final':row['newsroom_feed_url'],'body':'<rss><channel><link>https://example.com/</link><item><link>https://example.com/unlisted</link></item></channel></rss>'}
with patch('check.fetch',side_effect=[page,feed]):
    try:check(row)
    except AssertionError:pass
    else:raise AssertionError('channel home link incorrectly accepted as item overlap')
page['body']='<a href="/unlisted">Actual release</a>'
with patch('check.fetch',side_effect=[page,feed]):assert check(row)['checks'][1]['linked_items']==1
print('PASS: channel metadata link cannot satisfy item overlap; actual item link does')
feed['final']='https://example.com/comments/feed/'
row['newsroom_feed_url']=feed['url']=feed['final']
with patch('check.fetch',side_effect=[page,feed]):
    try:check(row)
    except AssertionError:pass
    else:raise AssertionError('comments feed accepted')
print('PASS: comments feed rejected even when its item links overlap')

badrow={'org_id':'test','website':'https://example.com','newsroom_url':'https://example.com/news','newsroom_feed_url':''}
with patch('check.fetch',return_value={'status':'200','url':badrow['newsroom_url'],'final':'https://example.com/','body':'Home'}):
    try:check(badrow)
    except AssertionError:pass
    else:raise AssertionError('same-domain homepage redirect accepted')
print('PASS: same-domain homepage redirect rejected')
import sys
if '--live' in sys.argv:
    from discover import discover
    for saved in known:
        result=discover({'org_id':saved['org_id'],'website':saved['website']})
        assert result['newsroom_url']==saved['newsroom_url'],result
    print('PASS: 3 fresh live known-answer newsroom discoveries')

from discover import ROOT
import subprocess,io
snapshot='9d69978'
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',snapshot,'data'],cwd=ROOT,text=True).splitlines()
records=[r for path in paths if path.startswith('data/organizations_') and not path.endswith('_all.csv') for r in csv.DictReader(io.StringIO(subprocess.check_output(['git','show',snapshot+':'+path],cwd=ROOT,text=True)))]
eligible={r['org_id']:r for r in records if r['status']=='active' and r['tier1_qualifier'] and r['website']}
assert len(records)==len({r['org_id'] for r in records})==4945
def verify_snapshot_packet(candidate):
    assert set(eligible)=={r['org_id'] for r in candidate},'canonical eligible ID set mismatch'
    for r in candidate:
        url=eligible[r['org_id']]['website']; url=url if '://' in url else 'https://'+url
        assert r['website']==url,(r['org_id'],'snapshot website mismatch')
verify_snapshot_packet(inputs)
historical_omissions={'ORG-004065','ORG-004069','ORG-004079','ORG-004083','ORG-004084','ORG-004085'}
try:verify_snapshot_packet([r for r in inputs if r['org_id'] not in historical_omissions])
except AssertionError:pass
else:raise AssertionError('historical six-ID omission escaped canonical census')
print('PASS: injected historical six-ID omission rejected by canonical census')
assert len([r for r in records if r['status']=='active' and r['tier1_qualifier']])==1261
print('PASS: named canonical snapshot9d69978 has1261 active tier1,1049 websites,212 blank; input IDs and website values exactly match')

qrow={'org_id':'query-test','website':'https://example.com','newsroom_url':'https://example.com/?page_id=52','newsroom_feed_url':''}
qpage={'url':qrow['newsroom_url'],'final':qrow['newsroom_url']+'/','status':'200','body':'<h1>News</h1>'}
with patch('check.fetch',return_value=qpage):
    try:check(qrow)
    except AssertionError:pass
    else:raise AssertionError('query value52→52/ accepted')
qrow['newsroom_url']='https://example.com/news/?page_id=52'
qpage.update(url=qrow['newsroom_url'],final='https://example.com/news?page_id=52')
with patch('check.fetch',return_value=qpage):assert len(check(qrow)['checks'])==1
qrow.update(newsroom_url='https://example.com/news',newsroom_feed_url='https://example.com/feed')
qpage.update(url=qrow['newsroom_url'],final=qrow['newsroom_url'],body='<a href="/article?id=52">News release</a>')
qfeed={'url':qrow['newsroom_feed_url'],'final':qrow['newsroom_feed_url'],'status':'200','body':'<rss><channel><title>News</title><item><link>https://example.com/article?id=52/</link></item></channel></rss>'}
with patch('check.fetch',side_effect=[qpage,qfeed]):
    try:check(qrow)
    except AssertionError:pass
    else:raise AssertionError('different query article IDs falsely overlap')
print('PASS: changed query values rejected for redirects and feed articles; path-only slash normalization retained')
