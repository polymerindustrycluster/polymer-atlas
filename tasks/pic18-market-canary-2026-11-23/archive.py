#!/usr/bin/env python3
"""Try recent Wayback id_ captures on the live canary misses, six attempts per organization."""
import csv
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from threading import Thread
from urllib.parse import urlencode, urljoin, urlsplit

from fetch import CLASS, D, MAX_PAGES, STORE, Fetcher, public_url, reg_domain
from screen import preserve, show

ARCHIVE = 'https://web.archive.org'
ARCHIVE_STORE = STORE / 'wayback'
FIRST, LAST = '20241123', '20261123'


def live_misses(store=STORE):
    live = [json.loads(line) for line in (store / 'fetches.jsonl').read_text().splitlines()]
    readable = {r['org_id'] for r in live if r.get('status') == 'ok' and 'text_sha256' in r}
    with (D / 'frame.csv').open() as f:
        return [r for r in csv.DictReader(f) if r['cohort'] == 'unknown' and r['org_id'] not in readable]


def own_url(url, website):
    parsed = urlsplit(url)
    host = parsed.hostname
    return (parsed.scheme in ('http', 'https') and host and not parsed.username
            and reg_domain(host) == reg_domain(urlsplit(website).hostname))


def replay_parts(url, website):
    outer = urlsplit(url)
    match = re.fullmatch(r'/web/(\d{14})id_/(https?://.+)', outer.path)
    if (outer.scheme, outer.netloc) != ('https', 'web.archive.org') or not match:
        return None
    timestamp, original = match.groups()
    try:
        datetime.strptime(timestamp, '%Y%m%d%H%M%S')
    except ValueError:
        return None
    if FIRST <= timestamp[:8] <= LAST and own_url(original, website):
        return timestamp, original


class Wayback(Fetcher):
    charge_robots = True

    def get_archive(self, url, kind):
        """Check Wayback robots and charge every request, including retries and redirects."""
        if (urlsplit(url).scheme, urlsplit(url).netloc) != ('https', 'web.archive.org'):
            return None, 'OFF_ARCHIVE'
        if not self.remaining:
            return None, 'BUDGET'
        if kind == 'wayback_capture' and not replay_parts(url, self.website):
            return None, 'STALE_OR_OFF_DOMAIN'
        allowed = self.allowed(url)
        if allowed is not True:
            return None, 'ROBOTS_BLOCKED' if allowed is False else 'ROBOTS_UNREADABLE'
        response = self.curl(url, kind)
        if response is None:
            return None, 'BUDGET'
        if response['exit']:
            return response, CLASS.get(response['exit'], f'CURL_{response["exit"]}')
        if response['decode_error']:
            return response, 'DECODE_ERROR'
        return response, 'ok' if response['code'] == 200 else f'HTTP_{response["code"]}'

    def cdx(self, domain_lookup=False):
        fields = {
            'url': self.website, 'from': FIRST, 'to': LAST, 'output': 'json',
            'fl': 'timestamp,original,statuscode,mimetype', 'limit': '-12',
        }
        if domain_lookup:
            fields.update(url=urlsplit(self.website).hostname.removeprefix('www.'), matchType='domain', limit='-40')
        filters = [('filter', r'original:https?://[^/]+/(?:$|(?:industr|market|application|capabilit|about|who-we-are|what-we-do)[A-Za-z0-9/_-]*/?$)'),
                   ('filter', 'mimetype:text/html'), ('filter', 'statuscode:200')] if domain_lookup else []
        query = urlencode([*fields.items(), *filters])
        response, status = self.get_archive(f'{ARCHIVE}/cdx/search/cdx?{query}', 'cdx')
        scope = 'domain' if domain_lookup else 'exact'
        if status != 'ok':
            self.record(dict(kind='lookup', scope=scope, status=status))
            return []
        try:
            table = json.loads(response['raw'] or b'[]')
            header = ['timestamp', 'original', 'statuscode', 'mimetype']
            if table and table[0] != header:
                raise ValueError('CDX header')
            captures = []
            for timestamp, url, code, kind in table[1:]:
                if code == '200' and kind == 'text/html' and replay_parts(f'{ARCHIVE}/web/{timestamp}id_/{url}', self.website):
                    captures.append((timestamp, url))
            self.record(dict(kind='lookup', scope=scope, status='CDX_OK' if captures else 'CDX_NO_QUALIFYING_HTML',
                             rows=len(table[1:]), qualifying=len(captures)))
            newest = sorted(set(captures), reverse=True)
            if not domain_lookup:
                return newest
            priority = r'industr|market|application|capabilit|about|what-we-do'
            return sorted(newest, key=lambda item: not re.search(priority, urlsplit(item[1]).path, re.I))
        except (ValueError, TypeError, IndexError, UnicodeError):
            self.record(dict(kind='lookup', scope=scope, status='CDX_UNREADABLE'))
            return []

    def replay(self, timestamp, original):
        url = f'{ARCHIVE}/web/{timestamp}id_/{original}'
        while self.remaining:
            response, status = self.get_archive(url, 'wayback_capture')
            if status in ('HTTP_301', 'HTTP_302', 'HTTP_303', 'HTTP_307', 'HTTP_308') and response['location']:
                url = urljoin(url, response['location'])
                continue
            parts = replay_parts(url, self.website)
            if status == 'ok' and response['memento']:
                try:
                    capture_time = parsedate_to_datetime(response['memento']).astimezone(timezone.utc).strftime('%Y%m%d%H%M%S')
                except (ValueError, TypeError):
                    capture_time = ''
                if capture_time != parts[0]:
                    status = 'MEMENTO_MISMATCH'
            if response is None or not parts:
                break
            capture_time, source = parts
            result, _, _, _ = self.capture(url, url, 'archive_page', status, response)
            self.record(dict(kind='archive_source', request=response['request'],
                             captured_at=capture_time, source=public_url(source), status=result))
            return result
        else:
            status = 'BUDGET'
        self.record(dict(kind='archive_outcome', status=status))
        return status


def fetch_misses(fetcher, prior):
    misses = live_misses()
    assert len(misses) == 12
    used = Counter(r['org_id'] for r in prior if r['kind'] == 'request')
    visited = {r['url'] for r in prior if r.get('request_kind') == 'wayback_capture'}
    refused = {r['org_id'] for r in prior if r['kind'] == 'lookup' and r['status'] == 'CONN_REFUSED'}
    misses.sort(key=lambda row: row['org_id'] not in refused)
    for row in misses:
        fetcher.org, fetcher.website = row['org_id'], row['website']
        fetcher.remaining = MAX_PAGES - used[fetcher.org]
        if fetcher.remaining < 2:
            continue
        captures = fetcher.cdx(domain_lookup=bool(prior))
        for stamp, url in captures:
            if public_url(f'{ARCHIVE}/web/{stamp}id_/{url}') in visited:
                continue
            if not fetcher.remaining or fetcher.replay(stamp, url) == 'ok':
                break
        print(f'{fetcher.org} CDX HTML rows={len(captures)} requests so far={fetcher.n}', flush=True)
    print(f'ARCHIVE FETCH COMPLETE, {fetcher.n} HTTP attempts', flush=True)


if __name__ == '__main__':
    prior_rows = [json.loads(line) for line in (ARCHIVE_STORE / 'fetches.jsonl').read_text().splitlines()] if '--supplement' in sys.argv else []
    assert not any(r.get('scope') == 'domain' for r in prior_rows), 'supplement already attempted'
    fetcher = Wayback(ARCHIVE_STORE, start=sum(r['kind'] == 'request' for r in prior_rows))
    worker = Thread(target=fetch_misses, args=(fetcher, prior_rows))
    worker.start()
    for line in sys.stdin:
        args = line.split(maxsplit=2)
        if args and args[0] == 'show':
            show(fetcher.pages.copy(), [x.strip() for x in args[1:]])
        if args and args[0] == 'preserve':
            preserve(fetcher.pages.copy(), D / 'archive_selection.tsv', ARCHIVE_STORE)
        if args and args[0] == 'quit':
            break
    worker.join()
