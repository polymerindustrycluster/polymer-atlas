"""Offline terms-stop receipt; intentionally performs no authenticated requests."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/sam-entity-scout')


def build():
    sources = json.loads((HERE / 'sources.json').read_text())
    assert len(sources) == 2
    assert any('shall not access, use or disseminate D&B Open Data in bulk' in e
               for s in sources for e in s['excerpts'])
    return dict(route='TERMS_HELD', sources_checked=len(sources),
                authenticated_requests=0, records_downloaded=0,
                extract_file=None, extract_date=None, extract_sha256=None,
                extract_record_count=None, indexed_records=None,
                precision_by_class=None, mintable_uei_links=None,
                streetless_pic18_address_candidates=None, unheld_pic18_polymer_leads=None)


if __name__ == '__main__':
    (HERE / 'metrics.json').write_text(json.dumps(build(), indent=2) + '\n')
