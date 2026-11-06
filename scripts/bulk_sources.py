#!/usr/bin/env python3
"""Official bulk snapshots and exact local lookups. Cache artifacts never enter git."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
from datetime import datetime, timezone
from urllib.request import Request, urlopen
import uuid
import zipfile

try:
    from .build_echo_spine import squash
except ImportError:
    from build_echo_spine import squash

DEFAULT_CACHE = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/cache/bulk')
REPO = Path(__file__).resolve().parents[1]
URLS = {
    'frs': 'https://echo.epa.gov/files/echodownloads/echo_exporter.zip',
    'sec': 'https://www.sec.gov/Archives/edgar/daily-index/bulkdata/submissions.zip',
    'tickers': 'https://www.sec.gov/files/company_tickers.json',
}


def cache_dir(path=DEFAULT_CACHE):
    path = Path(path).expanduser().resolve()
    if path == REPO or REPO in path.parents or any(
            (parent / '.git').exists() for parent in (path, *path.parents)):
        raise ValueError('bulk cache must be outside the repository')
    path.mkdir(parents=True, exist_ok=True)
    return path


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def user_agent(contact):
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', contact):
        raise ValueError('supply a real contact email for the SEC User-Agent')
    return 'PolymerAtlas bulk research/1.0 ' + contact


def download(url, target, agent, expected_size=None):
    """Stream into a temporary file; verify length and ZIP CRC before publication."""
    target = Path(target)
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as out:
        tmp = Path(out.name)
        try:
            with urlopen(Request(url, headers={'User-Agent': agent}), timeout=120) as response:
                size = 0
                for block in iter(lambda: response.read(1024 * 1024), b''):
                    out.write(block)
                    size += len(block)
                length = response.headers.get('Content-Length')
                if not size or (length is not None and size != int(length)):
                    raise ValueError('empty or truncated download')
                if expected_size is not None and size != expected_size:
                    raise ValueError('published byte count mismatch')
            out.close()
            if target.suffix == '.zip':
                with zipfile.ZipFile(tmp) as z:
                    if z.testzip() is not None:
                        raise ValueError('ZIP CRC mismatch')
            digest = sha256(tmp)
            # Content-addressed files keep the old index tied to its original snapshot.
            final = target.with_name(digest + target.suffix)
            os.replace(tmp, final)
            return final, {'url': url, 'date': datetime.now(timezone.utc).isoformat(),
                           'size': size, 'sha256': digest, 'file': final.name}
        finally:
            tmp.unlink(missing_ok=True)


def csv_rows(z, member):
    with z.open(member) as raw:
        reader = csv.DictReader(io.TextIOWrapper(raw, encoding='utf-8-sig', newline=''), strict=True)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError('missing or duplicate CSV headers')
        for row in reader:
            if None in row or None in row.values():
                raise ValueError('ragged CSV row')
            yield row


def index_file(source, path, cache=DEFAULT_CACHE, metadata=None, expected_count=None):
    """Atomically build one source index. Every input row is accounted for."""
    cache = cache_dir(cache)
    path = Path(path)
    metadata = dict(metadata or {'url': path.as_uri(), 'date': datetime.now(timezone.utc).isoformat(),
                                 'size': path.stat().st_size, 'sha256': sha256(path), 'file': str(path)})
    fd, name = tempfile.mkstemp(dir=cache, suffix='.sqlite')
    os.close(fd)
    tmp = Path(name)
    db = sqlite3.connect(tmp)
    count = indexed = historical = 0
    try:
        db.execute('CREATE TABLE records (id TEXT, name TEXT, city TEXT, payload TEXT)')
        def add(key, label, city, row):
            nonlocal indexed
            db.execute('INSERT INTO records VALUES (?,?,?,?)',
                       (key, label.upper() if source == "tickers" else squash(label), squash(city),
                        json.dumps(row, ensure_ascii=False)))
            indexed += 1
        if source == 'tickers':
            rows = json.loads(path.read_text()).values()
            for row in rows:
                count += 1
                add(str(int(row['cik_str'])).zfill(10), row['ticker'].upper(), '', row)
            independent = len(json.loads(path.read_text()))
        else:
            with zipfile.ZipFile(path) as z:
                members = [m for m in z.namelist() if not m.endswith('/')]
                if len(members) != len(set(members)):
                    raise ValueError('duplicate archive members')
                if source == 'sec':
                    if not members or any(not re.fullmatch(r'CIK\d{10}(?:-submissions-\d+)?\.json', m) for m in members):
                        raise ValueError('unexpected SEC archive member')
                    for m in members:
                        row = json.loads(z.read(m))
                        count += 1
                        if '-submissions-' in m:
                            historical += 1
                            if not isinstance(row.get('accessionNumber'), list):
                                raise ValueError('invalid historical submissions')
                            continue
                        key = str(int(row['cik'])).zfill(10)
                        if m != 'CIK' + key + '.json':
                            raise ValueError('SEC member/CIK mismatch')
                        # Keep full filings in the verified archive, not a duplicate SQLite blob.
                        add(key, row['name'], '', {'member': m, 'name': row['name'], 'cik': key})
                    independent = len(members)
                elif source in ('frs', 'lei', 'rr'):
                    csvs = [m for m in members if m.lower().endswith('.csv')]
                    if len(csvs) != 1:
                        raise ValueError('expected exactly one national CSV')
                    m = csvs[0]
                    for row in csv_rows(z, m):
                        count += 1
                        if source == 'frs':
                            add(row['REGISTRY_ID'], row['FAC_NAME'], row['FAC_CITY'], row)
                        elif source == 'lei':
                            add(row['LEI'], row['Entity.LegalName'], row['Entity.LegalAddress.City'], row)
                        else:
                            add(row['Relationship.StartNode.NodeID'], row['Relationship.EndNode.NodeID'],
                                row['Relationship.RelationshipType'], row)
                    independent = sum(1 for _ in csv_rows(z, m))
                else:
                    raise ValueError('unknown source: ' + source)
        if not count or count != independent or indexed + historical != count:
            raise ValueError('input/index row reconciliation failed')
        if expected_count is not None and count != expected_count:
            raise ValueError(f'published record count mismatch: {count} != {expected_count}')
        if source in ('lei', 'sec'):
            db.execute('CREATE UNIQUE INDEX unique_id ON records(id)')
        else:
            db.execute('CREATE INDEX by_id ON records(id)')
        db.execute('CREATE INDEX by_name_city ON records(name, city)')
        if db.execute('SELECT count(*) FROM records').fetchone()[0] != indexed:
            raise ValueError('SQLite row count mismatch')
        metadata.update(row_count=count, indexed_rows=indexed, historical_members=historical,
                        independent_count=independent, published_count=expected_count)
        db.execute('CREATE TABLE manifest (json TEXT NOT NULL)')
        db.execute('INSERT INTO manifest VALUES (?)', (json.dumps(metadata),))
        db.commit()
        db.close()
        os.replace(tmp, cache / (source + '.sqlite'))
        return metadata
    finally:
        db.close()
        tmp.unlink(missing_ok=True)


def lookup(source, clause, args, cache=DEFAULT_CACHE):
    path = cache_dir(cache) / (source + '.sqlite')
    with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as db:
        return [json.loads(r[0]) for r in db.execute('SELECT payload FROM records WHERE ' + clause, args)]


def frs_by_registry_id(registry_id, cache=DEFAULT_CACHE):
    if not str(registry_id).strip():
        raise ValueError('blank FRS registry ID')
    return lookup('frs', 'id=?', (str(registry_id).strip(),), cache)


def frs_by_name_city(name, city, cache=DEFAULT_CACHE):
    return lookup('frs', 'name=? AND city=?', (squash(name), squash(city)), cache)


def sec_by_cik(cik, cache=DEFAULT_CACHE):
    value = str(cik).upper().removeprefix('CIK')
    if not value.isdigit() or len(value) > 10:
        raise ValueError('invalid CIK')
    matches = lookup('sec', 'id=?', (str(int(value)).zfill(10),), cache)
    if not matches:
        return None
    cache = cache_dir(cache)
    with sqlite3.connect((cache / 'sec.sqlite').as_uri() + '?mode=ro', uri=True) as db:
        manifest = json.loads(db.execute('SELECT json FROM manifest').fetchone()[0])
    with zipfile.ZipFile(cache / manifest['file']) as z:
        return json.loads(z.read(matches[0]['member']))


def sec_by_ticker(ticker, cache=DEFAULT_CACHE):
    matches = lookup('tickers', 'name=?', (ticker.strip().upper(),), cache)
    results = [sec_by_cik(row['cik_str'], cache) for row in matches]
    if any(row is None for row in results):
        raise ValueError('ticker CIK absent from submissions snapshot; refresh SEC cache')
    return results


def lei_by_lei(lei, cache=DEFAULT_CACHE):
    return lookup('lei', 'id=?', (lei.strip().upper(),), cache)


def lei_by_name(name, cache=DEFAULT_CACHE):
    return lookup('lei', 'name=?', (squash(name),), cache)


def lei_relationships(lei, cache=DEFAULT_CACHE):
    return lookup('rr', 'id=?', (lei.strip().upper(),), cache)


def build(sources, cache, contact):
    cache = cache_dir(cache)
    agent = user_agent(contact)
    for source in sources:
        expected_count = size = None
        if source in ('lei', 'rr'):
            kind = 'lei2' if source == 'lei' else 'rr'
            url = f'https://goldencopy.gleif.org/api/v2/golden-copies/publishes/{kind}/latest'
            with urlopen(Request(url, headers={'User-Agent': agent}), timeout=120) as r:
                release = json.load(r)['data']
            info = release['full_file']['csv']
            url, size, expected_count = info['url'], info['size'], info['record_count']
        else:
            url = URLS[source]
        path, meta = download(url, cache / (source + ('.json' if source == 'tickers' else '.zip')), agent, size)
        if source in ('lei', 'rr'):
            meta['publish_date'] = release['publish_date']
        result = index_file(source, path, cache, meta, expected_count)
        print(source, json.dumps(result), flush=True)
    manifests = {}
    for source in (*URLS, 'lei', 'rr'):
        path = cache / (source + '.sqlite')
        if path.exists():
            with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as db:
                manifests[source] = json.loads(db.execute('SELECT json FROM manifest').fetchone()[0])
    with tempfile.NamedTemporaryFile(mode='w', dir=cache, delete=False) as out:
        json.dump(manifests, out, indent=2)
    os.replace(out.name, cache / 'manifest.json')
    return manifests


def census_batch(rows, benchmark='Public_AR_Current'):
    """POST business addresses [id, street, city, state, zip], return raw CSV rows."""
    rows = list(rows)
    if not 1 <= len(rows) <= 10000:
        raise ValueError('Census batch requires 1–10,000 rows')
    if any(len(r) != 5 or not r[0] or not r[1] for r in rows):
        raise ValueError('expected id, street, city, state, zip; id and street required')
    ids = [str(r[0]) for r in rows]
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate input IDs')
    data = io.StringIO(newline='')
    csv.writer(data).writerows(rows)
    boundary = uuid.uuid4().hex
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="benchmark"\r\n\r\n{benchmark}\r\n'
            f'--{boundary}\r\nContent-Disposition: form-data; name="addressFile"; filename="addresses.csv"\r\n'
            f'Content-Type: text/csv\r\n\r\n{data.getvalue()}\r\n--{boundary}--\r\n').encode()
    request = Request('https://geocoding.geo.census.gov/geocoder/locations/addressbatch', data=body,
                      headers={'Content-Type': 'multipart/form-data; boundary=' + boundary})
    with urlopen(request, timeout=300) as response:
        results = list(csv.reader(io.StringIO(response.read().decode('utf-8-sig')), strict=True))
    if len(results) != len(rows) or {r[0] for r in results if r} != set(ids):
        raise ValueError('Census response ID/count mismatch')
    if any(len(r) < 3 or r[2] not in ('Match', 'No_Match', 'Tie') for r in results):
        raise ValueError('invalid Census response')
    for row in results:
        if row[2] == 'Match':
            if len(row) != 8:
                raise ValueError('invalid Census match fields')
            lon, lat = map(float, row[5].split(','))
            if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                raise ValueError('invalid Census coordinates')
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-dir', type=Path, default=DEFAULT_CACHE)
    parser.add_argument('--contact', required=True, help='contact email for descriptive SEC User-Agent')
    parser.add_argument('--sources', nargs='+', choices=[*URLS, 'lei', 'rr'], default=[*URLS, 'lei', 'rr'])
    args = parser.parse_args()
    build(args.sources, args.cache_dir, args.contact)


if __name__ == '__main__':
    main()
