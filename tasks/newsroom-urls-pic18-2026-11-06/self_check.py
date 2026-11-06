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
for rows in (inputs,verdicts,discovery):assert len({r['org_id'] for r in rows})==len(rows)==772
assert {r['org_id'] for r in inputs}=={r['org_id'] for r in verdicts}=={r['org_id'] for r in discovery}
assert all(1<=len(r['attempts'])<=6 for r in discovery)
assert all(r['note'] for r in verdicts if r['verdict']=='STILL_UNCERTAIN')
print('PASS: 772/772 input IDs uniquely reconciled to discovery and verdicts; discovery fetch budget <=6; holds explicit')
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
sys.path.insert(0,str(ROOT/'scripts'))
from regions import PIC18
import subprocess,io
snapshot='9d69978'
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',snapshot,'data'],cwd=ROOT,text=True).splitlines()
def snapshot_rows(prefix):
    return [r for path in paths if path.startswith('data/'+prefix+'_') and not path.endswith('_all.csv') for r in csv.DictReader(io.StringIO(subprocess.check_output(['git','show',snapshot+':'+path],cwd=ROOT,text=True)))]
pic={r['org_id'] for r in snapshot_rows('sites') if r['state']=='OH' and r['county'].removesuffix(' County') in PIC18}
frame={r['org_id'] for r in snapshot_rows('organizations') if r['status']=='active' and r['website'] and not r['tier1_qualifier'] and r['org_id'] in pic}
assert frame=={r['org_id'] for r in inputs}
print('PASS: independent frozen9d69978 active/PIC18/non-tier1/website frame matches inputs; current accepted eligibility checked by builder/check')

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
