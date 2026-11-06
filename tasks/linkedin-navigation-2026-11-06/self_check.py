"""Three independently read real anchors and boundary negatives, before bulk discovery."""
import hashlib
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import discover as d

known = {
 'https://www.avient.com': 'https://www.linkedin.com/company/avient-corporation/',
 'https://www.rtpcompany.com/': 'https://www.linkedin.com/company/rtp-company/',
 'https://www.averydennison.com/': 'https://www.linkedin.com/company/avery-dennison/',
}
def main():
    results=[]
    for url, expected in known.items():
        page=d.fetch(url)
        assert page['status']=='200'
        links=d.Links(page['body']).links
        assert {r['linkedin_url'] for r in links}=={expected},(url,links)
        results.append({'source_url':url,'final_url':page['url'],'expected':expected,'raw_sha256':page['raw_sha256'],'locations':sorted({r['location'] for r in links}),'check':'PASS'})
    for bad in ['https://www.linkedin.com/in/private-person/','https://www.linkedin.com/shareArticle?url=x','https://evil-linkedin.com/company/foo/','https://www.linkedin.com/company/../','https://www.linkedin.com/company/%2e%2e/','https://user@www.linkedin.com/company/foo/','javascript:https://www.linkedin.com/company/foo/']:
        assert not d.canonical(bad),bad
    assert d.canonical('https://uk.linkedin.com/company/avient-corporation/?trk=footer')==known['https://www.avient.com']
    assert not d.Links('<body class="theme-header-footer"><main><a href="'+known['https://www.avient.com']+'">body partner</a></main></body>').links
    assert not d.Links('<main><a href="'+known['https://www.avient.com']+'">article partner</a></main>').links
    assert not d.Links('<footer><a href>empty</a></footer>').links
    assert d.Links('<footer><a href="'+known['https://www.avient.com']+'">LinkedIn</a></footer>').links
    for bad in ['https://www.linkedin.com/company/foo/','https://x.linkedin.com/company/foo/','https://www.avient.com.evil.test/','file:///tmp/secret']:
        assert not d.own_url(bad,'avient.com')
    with patch.object(d.subprocess,'run') as run:
        page=d.fetch('https://www.linkedin.com/company/foo/')
        assert page['status']=='blocked_external_or_unsafe' and not run.called
    for unsafe in ['https://www.linkedin.com%2e/company/fabricated/','https://www.%6cinkedin.com/company/fabricated/','https://www.ℓinkedin.com/company/fabricated/']:
        with patch.object(d.subprocess,'run') as run:
            page=d.fetch(unsafe)
            assert page['status']=='blocked_external_or_unsafe' and not run.called
    calls=[]
    def redirect(cmd,**kwargs):
        calls.append(cmd[-1])
        Path(cmd[cmd.index('-D')+1]).write_text('HTTP/1.1 302 Found\nLocation: https://www.linkedin.com/company/foo/\n')
        Path(cmd[cmd.index('-o')+1]).write_text('')
        return type('Result',(),{'stdout':'302','returncode':0})()
    with patch.object(d.subprocess,'run',side_effect=redirect):
        page=d.fetch('https://www.avient.com/redirect-negative')
        assert page['status']=='blocked_external_or_unsafe' and calls==['https://www.avient.com/redirect-negative']
    from rawcheck import verify
    row={'source_url':'https://www.avient.com','linkedin_url':'https://www.linkedin.com/company/fabricated/','href':'https://www.linkedin.com/company/fabricated/'}
    with patch.object(d,'fetch',return_value={'body':'<footer><a href="https://www.linkedin.com/company/avient-corporation/">LinkedIn</a></footer>','status':'200','raw_sha256':'0'*64,'url':'https://www.avient.com','attempts':[]}):
        outcome,_=verify(row)
        assert outcome['result']=='FAIL'
    (d.HERE/'known-answers.json').write_text(json.dumps(results,indent=2)+'\n')
    print('PASS realknown3/3; personal/share/body/unsafeURL/encoded-dot negatives; direct and redirectedLinkedIn blocked before request.')

if __name__=='__main__':
    main()
