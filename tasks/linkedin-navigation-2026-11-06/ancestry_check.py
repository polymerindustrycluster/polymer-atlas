"""Actual Codex body-ancestry repros must fail both extraction and raw verification."""
from unittest.mock import patch
import discover as d
from rawcheck import verify

URL='https://www.linkedin.com/company/avient-corporation/'
A='<a href="'+URL+'">Company</a>'
NEGATIVES=[
 '<main><article><div class="article-header">'+A+'</div></article></main>',
 '<div class="site-header-footer"><main>'+A+'</main></div>',
 '<div class="site-header-footer">'+A+'<main>later body</main></div>',
 '<main><header>'+A+'</header></main>',
 '<article><footer>'+A+'</footer></article>',
 '<div class="article-header">'+A+'</div>',
]
POSITIVES=[
 '<header>'+A+'</header><main>body</main>',
 '<main>body</main><footer>'+A+'</footer>',
 '<div class="site-header-footer"><main>body</main><footer>'+A+'</footer></div>',
 '<div class="site-header-footer"><header>'+A+'</header><main>body</main></div>',
]
def main():
    row={'source_url':'https://www.avient.com','linkedin_url':URL,'href':URL}
    for i,body in enumerate(NEGATIVES):
        assert not d.Links(body).links,('body anchor admitted',i)
        with patch.object(d,'fetch',return_value={'body':body,'status':'200','raw_sha256':'0'*64,'url':'https://www.avient.com','attempts':[]}):
            result,_=verify(row)
            assert result['result']=='FAIL',('body raw proof passed',i)
    for body in POSITIVES:
        assert {x['linkedin_url'] for x in d.Links(body).links}=={URL}
    print('PASS six ancestry negatives reject in extractor and production raw verifier; four independent header/footer positives survive.')

if __name__=='__main__':
    main()
