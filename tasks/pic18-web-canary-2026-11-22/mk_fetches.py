#!/usr/bin/env python3
"""fetches.csv from the capture log (URL, status, sha256; no page text). Pass 1 = first run; pass 2 = 5 orgs re-run after the robots-redirect fix; pass 3 = CF Extrusion meta-refresh follow; pass 4 = the 7 unreadable organizations re-run with the HTTP/1.1 retry and classified failures."""
import csv, json
S = '/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/web-canary-2026-11-22/'
n1, n2, n3 = (sum(1 for _ in open(S + f)) for f in ('fetches.pass1.jsonl', 'fetches.pass2.jsonl', 'fetches.pass3.jsonl'))
LABEL = {'CURL_52': 'EMPTY_REPLY', 'CURL_56': 'RECV_ERROR', 'CURL_92': 'HTTP2_ERROR'}
rows = [json.loads(l) for l in open(S + 'fetches.jsonl')]
for i, r in enumerate(rows):
    r['pass'] = 1 if i < n1 else 2 if i < n2 else 3 if i < n3 else 4
    r['status'] = LABEL.get(r.get('status'), r.get('status'))
    r.setdefault('status', 'ok' if r['kind'] == 'robots' and r['http'] == 200 else 'robots_' + str(r['http']))
cols = ['org_id', 'pass', 'kind', 'url', 'final_url', 'http', 'status', 'sha256', 'text_sha256', 'chars', 'fetched_at', 'note']
with open('tasks/pic18-web-canary-2026-11-22/fetches.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, cols, extrasaction='ignore'); w.writeheader(); w.writerows(rows)
print(len(rows), 'rows;', sum(r['kind'] != 'robots' for r in rows), 'page requests;', sum(r['kind'] == 'robots' for r in rows), 'robots.txt requests')
