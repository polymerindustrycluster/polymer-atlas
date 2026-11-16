"""Verify source witnesses and fail-closed unmeasured metrics, including defects."""
import copy
import hashlib
import json
from html.parser import HTMLParser
from build import CACHE, HERE, build


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def verify(sources, metrics):
    assert len(sources) == len(list(CACHE.glob('*.html'))) == 2
    assert {s['cache_file'] for s in sources} == {'terms.html', 'api-docs.html'}
    for source in sources:
        raw = (CACHE / source['cache_file']).read_bytes()
        assert source['http_status'] == 200
        assert len(raw) == source['bytes']
        assert hashlib.sha256(raw).hexdigest() == source['sha256']
        parser = Text()
        parser.feed(raw.decode())
        text = ' '.join(' '.join(parser.parts).split())
        assert source['excerpts']
        assert all(e in text for e in source['excerpts'])
    assert metrics == build(), 'receipt drift or invented measurement'


def main():
    sources = json.loads((HERE / 'sources.json').read_text())
    metrics = json.loads((HERE / 'metrics.json').read_text())
    verify(sources, metrics)
    for defect in ('missing_source', 'invented_yield', 'false_hash'):
        s, m = copy.deepcopy(sources), copy.deepcopy(metrics)
        if defect == 'missing_source':
            s.pop()
        elif defect == 'invented_yield':
            m['mintable_uei_links'] = 0
        else:
            s[0]['sha256'] = '0' * 64
        try:
            verify(s, m)
        except AssertionError:
            print('caught:', defect)
        else:
            raise AssertionError('silent pass: ' + defect)
    print('PASS: 2 public source witnesses; 3 injected defects rejected; yield unmeasured')


if __name__ == '__main__':
    main()
