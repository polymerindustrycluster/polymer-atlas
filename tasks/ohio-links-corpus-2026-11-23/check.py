"""Replay the pinned witnesses, reconcile the frame and prove the scoped apply."""
from collections import Counter
from contextlib import nullcontext
import json
from pathlib import Path
import re
import subprocess
import tempfile
from unittest.mock import patch

import build as b


def planted_defects():
    """Show each planted false positive being accepted with its guard disabled."""
    with tempfile.TemporaryDirectory() as directory, patch.object(b,'CORPUS',Path(directory)):
        org={k:'' for k in b.FIELDS}
        org.update(org_id='KNOWN',legal_name='Atlas Example LLC',status='active',website='https://example.org/')
        owners={'example.org':{'KNOWN'}}

        def pinned(path,kind,body):
            raw=body.encode()
            file=f'{kind}-{b.digest(raw)[:12]}.html'
            (b.CORPUS/file).write_bytes(raw)
            url='https://example.org'+path
            return dict(org_id='KNOWN',url=url,final_url=url,page_kind=kind,status='ok',
                        raw_file=file,witness_bytes=len(raw),witness_sha256=b.digest(raw))

        company='https://www.linkedin.com/company/atlas-example/'
        body_link=pinned('/','home',f'<main><a href="{company}">LinkedIn</a></main>')
        valid_link=pinned('/about','about',f'<footer><a href="{company}">LinkedIn</a></footer>')
        offsite=pinned('/','home','<nav><a href="https://other.org/news">News</a></nav>')
        valid_room=pinned('/news','news',
                          '<main><a href="https://witness.invalid/release"></a></main>'
                          '<link rel="alternate" type="application/rss+xml" href="/feed">')
        blog_feed=pinned('/feed','feed','<rss><channel><item>'
                         '<link>https://witness.invalid/blog</link></item></channel></rss>')
        overlap_feed=pinned('/feed','feed_ok','<rss><channel><item>'
                            '<link>https://witness.invalid/release</link></item></channel></rss>')
        overlap_feed['page_kind']='feed'

        def admitted(col,pages,guard=None):
            with guard or nullcontext():
                result=b.candidates(org,pages,owners)
                return next(p['applied']=='yes' for p in result if p['column']==col)

        original_own_url=b.own_url
        cases=[
            ('body-only LinkedIn','linkedin_url',[body_link],
             patch.object(b.li,'Links',return_value=type('AllAnchors',(),{
                 'links':[{'linkedin_url':company,'href':company}]})())),
            ('off-domain newsroom','newsroom_url',[offsite],
             patch.object(b,'own_url',side_effect=lambda url,owner:
                          url=='https://other.org/news' or original_own_url(url,owner))),
            ('blog feed with no newsroom item overlap','newsroom_feed_url',[valid_room,blog_feed],
             patch.object(b,'feed_overlaps',return_value=True)),
        ]
        for defect,col,pages,guard in cases:
            assert admitted(col,pages,guard), f'Planted {defect} did not reach admission before rule'
            assert not admitted(col,pages), f'Planted {defect} escaped its rule'
            print(f'PASS: {defect} accepted with rule disabled, held with rule enabled')
        assert admitted('linkedin_url',[valid_link])
        assert admitted('newsroom_url',[valid_room])
        assert admitted('newsroom_feed_url',[valid_room,overlap_feed])
        org['notes']="Website is the parent's."
        for col,pages in [('linkedin_url',[valid_link]),('newsroom_url',[valid_room]),
                          ('newsroom_feed_url',[valid_room,overlap_feed])]:
            assert admitted(col,pages,patch.object(b,'site_identity_hold',return_value=''))
            assert not admitted(col,pages),f'parent-site {col} escaped'
        print('PASS: unique parent site admitted with identity guard disabled and held with it enabled')

        org['notes']=''
        owners['example.org'].add('SIBLING')
        assert not admitted('newsroom_url',[valid_room])
        assert not admitted('newsroom_feed_url',[valid_room,overlap_feed])


def check_manifest(manifest,frozen):
    assert manifest==b.read(b.CORPUS/'manifest.csv'),'manifest differs from pinned crawl'
    ids={r['org_id'] for r in frozen}
    assert {r['org_id'] for r in manifest}==ids|{b.REPAIR}
    assert len({(r['org_id'],r['url']) for r in manifest})==len(manifest),'duplicate logical page'
    assert max(Counter(r['org_id'] for r in manifest).values())<=8
    usable=set()
    for p in manifest:
        if p['sha256']:
            assert re.fullmatch(r'[a-f0-9]{64}',p['sha256']) and int(p['bytes'])>0
        else:
            assert not int(p['bytes'])
        if p['status']=='ok':
            assert p['http_status']=='200' and p['sha256']
            content=(b.CORPUS/p['raw_file']).read_bytes()
            assert len(content)==int(p['witness_bytes']) and b.digest(content)==p['witness_sha256']
            if p['page_kind'] not in ('feed','repair_feed','repair_old_feed'):
                usable.add(p['org_id'])
        else:
            assert not p['raw_file']
    return usable & ids


def check_delta(accepted):
    ref=subprocess.check_output(['git','merge-base','HEAD','origin/main'],cwd=b.ROOT,text=True).strip()
    def git_diff(*args):
        return subprocess.check_output(['git','diff','--name-only',ref,*args],cwd=b.ROOT,text=True).splitlines()
    ts=b.tables()
    paths={str(p.relative_to(b.ROOT)) for p in ts}
    assert paths=={str(p) for p in b.shards('organizations',ref)},'organization shard set changed'
    assert set(git_diff('--','data'))<=paths,'non-organization data changed'
    actual={}
    for path,rows in ts.items():
        before=b.snapshot(path.relative_to(b.ROOT),ref)
        assert [r['org_id'] for r in before]==[r['org_id'] for r in rows],'organization IDs or row order changed'
        for old,new in zip(before,rows):
            assert old.keys()==new.keys()
            for col,value in new.items():
                if old[col]==value:continue
                repair=(old['org_id']==b.REPAIR and col=='newsroom_feed_url' and old[col]==b.OLD_FEED)
                assert col in b.COLS and (not old[col] or repair),'nonblank or unrelated field changed'
                actual[old['org_id'],col]=value
    assert actual==accepted,'applied cells differ from replay'


def main():
    planted_defects()
    assert (b.HERE/'base.txt').read_text().strip()==b.BASE
    frozen=b.frame()
    assert [{k:r[k] for k in b.PUBLIC_FIELDS} for r in frozen]==b.read(b.HERE/'inputs.csv')
    manifest=b.read(b.HERE/'manifest.csv')
    usable=check_manifest(manifest,frozen)
    packet=b.read(b.HERE/'proposals.csv')
    repair=b.repair_row(manifest)
    assert [repair]==b.read(b.HERE/'repair.csv')
    assert len(packet)==sum(not r[c] for r in frozen for c in b.COLS)
    assert all(r['settling_fact'] and not r['value'] for r in packet if r['applied']=='held')
    with tempfile.TemporaryDirectory() as scratch:
        with patch.object(b,'HERE',Path(scratch)):
            b.freeze()
        outputs=('base.txt','inputs.csv','manifest.csv','proposals.csv','repair.csv','sample.csv')
        for name in outputs:
            assert (b.HERE/name).read_bytes()==(Path(scratch)/name).read_bytes(),f'replay differs: {name}'
    accepted={(r['org_id'],r['column']):r['value'] for r in [*packet,repair] if r['applied']=='yes'}
    check_delta(accepted)
    before={p:p.read_bytes() for p in b.tables()}
    assert b.apply(packet+[repair])==0
    assert all(p.read_bytes()==raw for p,raw in before.items()),'second apply changed bytes'

    filled={r['org_id'] for r in packet if r['applied']=='yes'}
    held=usable-filled
    no_page={r['org_id'] for r in frozen}-usable
    assert filled<=usable and len(filled)+len(held)+len(no_page)==748
    summary={
        'frame':{'filled_any':len(filled),'held_all_with_page':len(held),'no_page':len(no_page)},
        'filled_cells':{c:sum(r['column']==c and r['applied']=='yes' for r in packet) for c in b.COLS},
        'holds_by_reason':dict(sorted(Counter(r['settling_fact'] for r in packet if r['applied']=='held').items())),
        'tiers_of_organizations_with_fills':dict(sorted(Counter(r['verification_tier'] for r in frozen if r['org_id'] in filled).items())),
        'page_attempts_including_provia':len(manifest),
        'page_transport_calls_excluding_robots':sum(int(p['requests']) for p in manifest),
        'page_holds_by_fetch_status':dict(sorted(Counter(p['status'] for p in manifest if p['status']!='ok').items())),
        'stratified_sample_cells':dict(Counter(r['column'] for r in b.read(b.HERE/'sample.csv'))),
        'A11-047':repair['settling_fact'],
    }
    print(json.dumps(summary,indent=2))
    print('PASS: replay, frame reconciliation, exclusively scoped cell delta, sample and byte-identical second apply')


if __name__=='__main__':
    import sys
    if '--known-answers' in sys.argv:planted_defects()
    else:main()
