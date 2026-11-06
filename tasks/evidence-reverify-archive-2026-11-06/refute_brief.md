Try to REFUTE this partial PR for PIC18 preserved-quote audit and verified Wayback links. Return APPROVE or REFUTE for correctness of this scoped deliverable, with concrete reproducible findings. This is not full semantic claim re-verification or archive completeness; those limitations/holds must remain explicit. Controller authorized shipping verified subset while an 11-hour resumable CDX/SPN worker produces local candidates. Do not approve missing gates: identify pending checks as pending.

Ground truth frame at bd57a08: OH physical PIC18 sites plus their parent organizations regardless of HQ, no status filter. 3,683 own_site rows, 1,120 distinct references. 3,344 quote matches, 76 absent quotes, 35 readable/no preserved quote holds, 228 fetch failures. 339 repair/availability leads. We never change evidence or tiers. Only archive_links.csv is applied. archive packet is still growing during review; eventual check_archives.py must freshly re-fetch every included capture and match its quote before PR publication. validate.py must pass; report.py must reconcile all counts. Four real inspected known answers plus inserted/reversed quote mutations pass. Baseline validate passes. There is no claim that the earlier 74% semantic support rose to the new quote-presence percentage.

Inspect correctness, URL/capture binding, idempotence, quote extraction, skipped/uninspected cases, failure behavior, rate-limit handling, and whether README overclaims. New code is task-local, no scripts/ edits. Local raw pages are not committed. Optional replacements skipped. Scope holds and all archive unavailability must remain visible.

Named checks: python3 tasks/evidence-reverify-archive-2026-11-06/{known_answers,report,build,check_archives}.py and python3 scripts/validate.py. check_archives explicitly fails for a zero-row packet. All assertions are required. Data builder rerun must add zero rows.


Final snapshot update: 34 links / 11 captures, fresh re-fetch 0 failures after bounded retries. All rows supports_A already; no evidence or tier changes. 3,310 supported rows remain archive holds. validate.py zero errors; builder rerun zero additions. CDX worker is background/local-only. Controller 05:55 permits draft PR before two-family clerk reviews. Changes since the initial packet include global availability stop, shared rate-limit holds, bounded fresh transport retries, collision-safe raw/page cache writes, exponential replay backoff, deadline guard, and CDX known-answer fixtures. Review the current files below, not the initial in-flight snapshot.

--- README.md ---
# PIC-18 own-site quote re-verification and archive links, 2026-11-06

L1, claimed by controller thr_9i2c6byhcz for atlas-L1-reverify-archive. Source tree: bd57a08.
First users: Atlas integrator and evidence auditors, beginning with this PR on 2026-11-06; no operational UI is added.

Frame: every OH site whose physical county, after stripping a trailing ` County`, is in `scripts/regions.py` PIC18;
plus the organizations operating those sites, regardless of HQ. No status/tier filter. The union contributes
**3,683 own_site evidence rows / 1,120 distinct cited references**, exactly the controller's baseline. Four references
(8 rows) are not bare URLs. Organization HQ-only selection would instead yield 3,540 rows / 1,073 references;
including all PIC18 HQ organizations plus site parents would yield 3,765 / 1,149. Neither alternative is used.

## What the judgments mean

This pass tests **preserved quote presence**, using the unchanged `words`, `on_page`, and `wilson` implementations
loaded from the calibrated 2026-11-03 audit's `analyze.py` via AST (without executing its CLI). Contiguous normalized
words must match; punctuation and accents follow the original matcher. Quote extraction uses `notes`' `Quote: "..."`
format, then quoted `claim_detail`. No inference from a match to the underlying claim's truth is made.

Live URLs were fetched once per exact reference and cached (curl/browser UA, Jina raw fallback). Script/style/noscript
content is excluded; visible HTML text is used, Jina's response metadata is excluded. Raw responses and full page
text stay in ignored `build/l1-cache/`, never in the PR. No truncation. Fetch errors, unsupported PDF extraction,
challenge walls, non-URL references and insufficient readable content are availability failures, never evidence of absence.
A failed cached fetch is not silently retried. `fetched_at` and route metadata live in the local cache; verdicts carry checked_at.

**3,344 SUPPORTED** means the preserved quote's words occur in order. **76 NOT_SUPPORTED** means that exact quote is
absent from the readable cited page, not that the claim is false. **35 PARTIAL** rows are holds: readable page but no
preserved quote to test; no semantic partial-support assertion is intended. **228 FETCH_FAILED** rows are availability
holds. `repair_leads.csv` includes all 339 non-supported rows, including availability holds, and names the settling claim/page.
Lane-level posture for every unresolved row is STILL_UNCERTAIN; none is an organization rejection or status change.

The prior audit judged **claim semantics**, then verified its newly chosen quotes. Its 74% support rate (142/191
readable sampled pages; 68–80% Wilson CI) is a different estimand, geography, and sampling design. The comparison
below is context, **not evidence that semantic support improved**. This pass does not independently validate that
site-level claims are locally attributable, or that a quoted capability maps to the claimed vocabulary term.
All-frame denominators count fetch/no-quote holds against support; readable denominators exclude FETCH_FAILED only.
Wilson intervals are descriptive binomial reference intervals on this full frame, not uncertainty from random sampling.
PIC18 evidence rows: 3683 distinct cited refs: 1120
Judgments: {'SUPPORTED': 3344, 'PARTIAL': 35, 'NOT_SUPPORTED': 76, 'FETCH_FAILED': 228}
Repair/availability leads: 339 / 3683
| Claim | Quote supported / all rows | Rate (Wilson 95% CI) | Supported / readable | Rate (Wilson 95% CI) | 2026-11-03 semantic audit |
|-|-:|-|-:|-|-|
| activity | 0/3 | 0.0% (0–56%) | 0/1 | 0.0% (0–79%) | not sampled |
| address | 19/37 | 51.4% (36–67%) | 19/28 | 67.9% (49–82%) | 7/13 (54%; 29–77%) |
| existence | 32/59 | 54.2% (42–66%) | 32/46 | 69.6% (55–81%) | 12/24 (50%; 31–69%) |
| liveness | 0/2 | 0.0% (0–66%) | 0/1 | 0.0% (0–79%) | not sampled |
| parent | 5/7 | 71.4% (36–92%) | 5/5 | 100.0% (57–100%) | 0/2 (0%; 0–66%) |
| scope | 3288/3575 | 92.0% (91–93%) | 3288/3374 | 97.5% (97–98%) | 122/151 (81%; 74–86%) |

## Archive snapshot and continuation

The snapshot currently applies **34 archive links / 11 captures**, each citing the same page under V-59's exact
normalization. All 34 referenced evidence rows already have `tier_effect=supports_A`; zero evidence rows, organizations,
sites, or verification tiers are created/changed. No replacement EVD IDs were minted. No inclusion decisions or
inclusion-log entries. No dedupe/create procedure is triggered. Existing evidence and links are immutable.
The controller designated L1 as sole archive-file writer under AGENTS §2.7; git bd57a08 is the pre-pass backup.
`build.py` uses `shard_io.append_sorted`, skips byte-equivalent existing rows and refuses conflicting links.

Discovery through `/wayback/available` hit sustained 429s after roughly 100 successful responses. The initial parallel
batch lacked shared backoff; it was stopped and replaced by a global API stop, then the controller's paced CDX worker.
Normal replay URLs work where `id_` replay was rate-limited. Every candidate requires readable normal replay, exact
capture/page binding (replay redirects held), and the same quote match before it is eligible. An initial 101-row packet
was reduced after fresh transport failures; exclusions are explicit, not claims of quote contradiction. Raw request
metadata are local. The full-frame yield check failed while the archive snapshot was incomplete, as intended.

`discovery.py` is a resumable local worker: CDX at most one call per five seconds, Save Page Now at most one per 20 seconds
when CDX returns no exact capture, exponential 429 backoff from 60 seconds. No link is added because SPN accepted a request:
it must appear in CDX, be readable, and contain the quote. A worker run has an 11-hour ceiling and resumes per-URL JSON
receipts from `build/l1-discovery/`. It writes only local `build/l1-cdx-links.csv`, never canonical or committed packet files.
A later top-up must apply the same strict re-fetch and review gates. Receipt files with transport errors are holds,
not absence findings. To retry those URLs on another run, move their receipts aside in the local cache first.

| Hold | Count (evidence rows) | Settling fact/action |
|-|-:|-|
| Preserved quote absent | 76 | Own-site page with the claimed words, or a separately reviewed fresher evidence row |
| No preserved quote on readable page | 35 | Manual semantic review and selection of a supporting quote |
| Live fetch failed | 228 | Readable cited primary page; no absence inference |
| Archive not in this snapshot | 3,310 | Exact readable capture with matching quote; includes rate-limit, pending, missing and failed re-fetch cases |

Rest-of-Ohio and PA continuation belongs to a second PR; this first snapshot does not include them. Semantic claim
re-judgment, replacements, owner/ring/vocabulary changes, PDF text extraction and site-attribution repair are not claimed.
The read-only data-estate lookup had Mac platform gaps in the Windows-only Documents catalogues; repository sources
and the live cited web pages suffice for this pass. No CRM, private vault, licensed sources or personal data were used.

## Reproduce and gates

Run from repository root (Python 3.15, curl 8.7.1; standard library only):

```sh
python3 tasks/evidence-reverify-archive-2026-11-06/run.py
python3 tasks/evidence-reverify-archive-2026-11-06/known_answers.py
python3 tasks/evidence-reverify-archive-2026-11-06/archive.py --cached-only
python3 tasks/evidence-reverify-archive-2026-11-06/build.py
python3 tasks/evidence-reverify-archive-2026-11-06/check_archives.py
python3 tasks/evidence-reverify-archive-2026-11-06/report.py
python3 scripts/validate.py
```

The archive command regenerates from local discovery cache; a fresh machine must populate it using `archive.py` or
`discovery.py` first. It will not silently claim zero archives as a pass. `check_archives.py` independently refreshes
all distinct captures and fails on any unreadable or unmatched row, including an empty packet. It retries transient
failures at most twice and backs off on 429. Live cache reuse is intentional; remove only the relevant local cache
receipt to request a new live observation. Never commit raw caches.

Known-answer gate: EVD-013356, EVD-013357, EVD-013360 and EVD-013379 were inspected in raw fetched page text. All four
matched; inserting a unique absent token or reversing their word order failed. Empty quote returned None. V-59 binding
mutations reject a different path, path case, and query string; permitted scheme/www/host-case/trailing-slash changes pass.
`known_answers.py`: PASS. `build.py` rerun: zero additions, PASS. `report.py`: full frame/lead/archive counts reconcile,
PASS. Baseline `python3 scripts/validate.py`: zero errors, PASS. No `scripts/` files changed, so the scripts pytest gate
is not triggered. Fresh capture gate and two-family review results are recorded below when terminal.

Fresh archive gate: `python3 tasks/evidence-reverify-archive-2026-11-06/check_archives.py` —
**34 rows / 11 distinct captures / 0 failures**, PASS after bounded retry of transport failures. Earlier failed
101-row and 34-row checks were retained locally as diagnostics; this result follows exclusion of the first failing
candidates and retrying connection failures. No quote-match threshold was changed. Every row now included was freshly
re-fetched and its quote found. Validation after application: zero errors; builder idempotence: zero additions.

Controller 05:55 ruling supersedes the council-only ordering: draft PR publication may precede refutes; reviewer
threads are an approved alternative while council is saturated. Required families remain Codex + Grok. The original
deep council calls are still pending. Clerk reviews will be requested after branch publication; no Done claim.
Additional known-answer fixtures check CDX exact-page binding, another page, no captures, transport HTTP error and
invalid JSON, all PASS. Worker deadline handling and exponential replay backoff were tightened before restarting
from saved progress. The restarted worker uses the same local receipts and does not mutate the 34-row snapshot.

--- run.py ---
#!/usr/bin/env python3
"""PIC18 quote-presence audit; raw cache lives outside the shipped tree in build/."""
import ast
import concurrent.futures
import csv
import hashlib
import html.parser
import json
import os
import threading
import re
import subprocess
import sys
import time
import unicodedata
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from regions import PIC18

# Load the calibrated functions unchanged, without running analyze.py's CLI.
source = ast.parse((ROOT / 'tasks/evidence-audit-2026-11-03/analyze.py').read_text())
ns = dict(re=re, unicodedata=unicodedata, Path=Path, math=__import__('math'))
for node in source.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'words' for t in node.targets) or isinstance(node, ast.FunctionDef) and node.name in ('on_page', 'wilson'):
        exec(compile(ast.Module(body=[node], type_ignores=[]), '<calibrated-audit>', 'exec'), ns)
on_page, wilson = ns['on_page'], ns['wilson']
CACHE = ROOT / 'build/l1-cache'
CACHE.mkdir(parents=True, exist_ok=True)


def read(p):
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def write(p, rows, fields):
    with open(p, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fields, extrasaction='ignore', lineterminator='\n')
        w.writeheader(); w.writerows(rows)


class Text(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(); self.skip = 0; self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'noscript'): self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript'): self.skip = max(0, self.skip - 1)
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)


def fetch(url, refresh=False, fallback=True):
    key = hashlib.sha256(url.encode()).hexdigest()
    meta, page = [CACHE / (key + ext) for ext in ('.json', '.txt')]
    raw = CACHE / (key + f'.{os.getpid()}.{threading.get_ident()}.raw')
    if meta.exists() and not refresh:
        result = json.loads(meta.read_text())
        assert result['url'] == url
        return result
    attempts = []
    for route in [url] + (['https://r.jina.ai/' + url] if fallback else []):
        p = subprocess.run(['curl', '-L', '-sS', '-A', 'Mozilla/5.0 (Atlas evidence re-verification)', '--max-time', '25', '--max-filesize', '12000000', '-D', str(raw.with_suffix('.headers')), '-o', str(raw), '-w', '%{http_code}\n%{url_effective}', route], capture_output=True, text=True)
        code, _, effective = p.stdout.partition('\n')
        headers = raw.with_suffix('.headers').read_text(errors='replace') if raw.with_suffix('.headers').exists() else ''
        retry = re.findall(r'(?im)^retry-after:\s*(\d+)', headers)
        attempts.append(dict(route=route, status=code, exit=p.returncode, effective_url=effective, error=p.stderr.strip()[:300], retry_after=int(retry[-1]) if retry else 0))
        body = raw.read_bytes().decode('utf-8', errors='replace') if raw.exists() else ''
        if p.returncode == 0 and code == '200' and len(body) > 200 and not body.startswith('%PDF'):
            if route == url:
                parser = Text(); parser.feed(body); text = ' '.join(parser.parts)
            else:
                # Jina metadata is not page evidence.
                text = body.split('Markdown Content:', 1)[-1] if 'Markdown Content:' in body else ''
            lower = text.lower()
            wall = any(x in lower for x in ('just a moment...', 'verify you are human', 'attention required! | cloudflare', 'this site can’t be reached', 'checking your browser'))
            if len(ns['words'](text)) >= 15 and not wall:
                tmp_page = page.with_suffix(f'.{os.getpid()}.{threading.get_ident()}.txt.tmp')
                tmp_page.write_text(text); tmp_page.replace(page)
                result = dict(url=url, status='ok', page=str(page.relative_to(ROOT)), sha256=hashlib.sha256(raw.read_bytes()).hexdigest(), attempts=attempts, fetched_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
                tmp_meta = meta.with_suffix(f'.{os.getpid()}.{threading.get_ident()}.json.tmp')
                tmp_meta.write_text(json.dumps(result)); tmp_meta.replace(meta); return result
        if code == '429': break
    result = dict(url=url, status='FETCH_FAILED', page='', attempts=attempts, fetched_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    tmp_meta = meta.with_suffix(f'.{os.getpid()}.{threading.get_ident()}.json.tmp')
    tmp_meta.write_text(json.dumps(result)); tmp_meta.replace(meta); return result


def quote(e):
    m = re.search(r'Quote:\s*["“](.*?)["”](?:\s*\||\s*$)', e['notes'], re.S)
    if m: return m.group(1).strip()
    m = re.search(r'["“](.+)["”]', e['claim_detail'], re.S)
    return m.group(1).strip() if m else ''


def frame():
    sites = [r for p in sorted((ROOT / 'data').glob('sites_*.csv')) for r in read(p)]
    si = {r['site_id'] for r in sites if r['state'] == 'OH' and re.sub(r' County$', '', r['county']) in PIC18}
    oi = {r['org_id'] for r in sites if r['site_id'] in si}
    rows = [r for p in sorted((ROOT / 'data').glob('evidence_*.csv')) for r in read(p) if r['source_class'] == 'own_site' and ((r['record_table'] == 'organizations' and r['record_id'] in oi) or (r['record_table'] == 'sites' and r['record_id'] in si))]
    assert len({r['evidence_id'] for r in rows}) == len(rows)
    for r in rows: r.update(url=r['source_ref'], quote=quote(r))
    write(HERE / 'inputs.csv', rows, list(rows[0]))
    return rows


def audit():
    rows = frame()
    urls = sorted({r['url'] for r in rows})
    print('frame', len(rows), 'URLs', len(urls), flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        for i, result in enumerate(pool.map(fetch, urls), 1):
            if i % 50 == 0: print('fetched', i, '/', len(urls), flush=True)
    results = []
    for e in rows:
        f = fetch(e['url'])
        if f['status'] != 'ok': judgment, reason = 'FETCH_FAILED', 'No readable live page via direct or Jina route; availability only.'
        elif not e['quote']: judgment, reason = 'PARTIAL', 'No preserved verbatim quote: manual claim judgment needed; not an adverse claim verdict.'
        elif on_page(e['quote'], ROOT / f['page']): judgment, reason = 'SUPPORTED', 'Preserved quote occurs as contiguous normalized words; claim semantics not independently rejudged.'
        else: judgment, reason = 'NOT_SUPPORTED', 'Preserved quote not found as contiguous normalized words; claim itself may still be true.'
        results.append(dict(**e, judgment=judgment, reason=reason, page=f['page'], checked_at=f['fetched_at']))
    write(HERE / 'verdicts.csv', results, list(results[0]))
    leads = [dict(evidence_id=r['evidence_id'], record=r['record_id'], claim_type=r['claim_type'], url=r['url'], judgment=r['judgment'], settling_page='A readable own-site page stating: ' + r['claim_detail'], reason=r['reason']) for r in results if r['judgment'] != 'SUPPORTED']
    write(HERE / 'repair_leads.csv', leads, ['evidence_id','record','claim_type','url','judgment','settling_page','reason'])
    assert len(leads) + sum(r['judgment'] == 'SUPPORTED' for r in results) == len(rows)
    print(Counter(r['judgment'] for r in results), flush=True)


if __name__ == '__main__':
    audit()

--- archive.py ---
#!/usr/bin/env python3
"""Availability is discovery only; a paced readable replay must contain the quote."""
import concurrent.futures
import hashlib
import json
import re
import subprocess
import time
import threading
import sys
from run import HERE, ROOT, CACHE, read, write, fetch, on_page

FIELDS = ['evidence_id', 'archive_ref', 'captured_at', 'created_by']
AVAILABILITY_STOP = threading.Event()


def same_page(a, b):
    norm = lambda u: re.sub(r'^(https?://)?(www\.)?', '', u.strip()).rstrip('/')
    na, nb = norm(a), norm(b)
    ha, _, pa = na.partition('/'); hb, _, pb = nb.partition('/')
    return ha.lower() == hb.lower() and pa == pb


def available(url):
    path = CACHE / (hashlib.sha256(url.encode()).hexdigest() + '.available.json')
    if path.exists(): return json.loads(path.read_text())
    if AVAILABILITY_STOP.is_set(): return dict(url=url, archive_ref='', availability_status='RATE_LIMIT_HOLD')
    time.sleep(1)
    p = subprocess.run(['curl','-sS','--max-time','25','-G','https://archive.org/wayback/available','--data-urlencode','url='+url,'-w','\n%{http_code}'], capture_output=True, text=True)
    body, _, code = p.stdout.rpartition('\n')
    if code == '429': AVAILABILITY_STOP.set()
    try:
        d = json.loads(body) if code == '200' and p.returncode == 0 else {}
        c = d.get('archived_snapshots', {}).get('closest', {})
        ref = c.get('url', '').replace('http://web.archive.org/', 'https://web.archive.org/')
        m = re.fullmatch(r'https://web\.archive\.org/web/(\d{14})/(https?://\S+)', ref)
        if not (c.get('available') and c.get('status') == '200' and m and same_page(m[2], url)): ref = ''
        result = dict(url=url, archive_ref=ref, availability_status=code)
    except (ValueError, TypeError): result = dict(url=url, archive_ref='', availability_status='invalid_json')
    path.write_text(json.dumps(result)); return result


def main():
    verdicts = read(HERE / 'verdicts.csv')
    grouped = {}
    for r in verdicts:
        if r['judgment'] == 'SUPPORTED': grouped.setdefault(r['url'], []).append(r)
    if any(json.loads(p.read_text()).get('availability_status') == '429' for p in CACHE.glob('*.available.json')):
        AVAILABILITY_STOP.set()
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        availability = list(pool.map(available, sorted(grouped)))
    print('availability queried', len(availability), flush=True)
    links, outcomes = [], []
    consecutive_429 = 0
    for i, a in enumerate(availability, 1):
        ref = a['archive_ref']
        status = ('NO_CAPTURE' if a['availability_status'] == '200' else 'RATE_LIMIT_HOLD' if a['availability_status'] in ('429','RATE_LIMIT_HOLD') else 'AVAILABILITY_FAILED')
        if ref and '--cached-only' in sys.argv and not (CACHE / (hashlib.sha256(ref.encode()).hexdigest()+'.json')).exists():
            status = 'CAPTURE_PENDING'
        elif ref and consecutive_429 < 3:
            if '--cached-only' not in sys.argv: time.sleep(2)
            f = fetch(ref, fallback=False)
            code = f['attempts'][-1]['status']
            consecutive_429 = consecutive_429 + 1 if code == '429' else 0
            if code == '429': time.sleep(30)
            effective = f['attempts'][-1]['effective_url']
            # Redirecting to another capture/page cannot bind the discovered timestamp.
            if f['status'] == 'ok' and effective.rstrip('/') == ref.rstrip('/'):
                status = 'READABLE'
                for e in grouped[a['url']]:
                    if on_page(e['quote'], ROOT / f['page']):
                        stamp = re.search(r'/web/(\d{14})/', ref)[1]
                        links.append(dict(evidence_id=e['evidence_id'], archive_ref=ref, captured_at=stamp[:4]+'-'+stamp[4:6]+'-'+stamp[6:8], created_by='atlas-L1-reverify-archive'))
                    else: outcomes.append(dict(evidence_id=e['evidence_id'],url=a['url'],archive_ref=ref,status='QUOTE_ABSENT'))
            else: status = 'CAPTURE_FETCH_FAILED' if f['status'] != 'ok' else 'CAPTURE_REDIRECT_HOLD'
        elif ref: status = 'RATE_LIMIT_HOLD'
        if status != 'READABLE':
            outcomes.extend(dict(evidence_id=e['evidence_id'], url=a['url'],archive_ref=ref,status=status) for e in grouped[a['url']])
        write(HERE / 'archive_links.csv', sorted(links,key=lambda x:x['evidence_id']), FIELDS)
        write(HERE / 'archive_outcomes.csv', outcomes, ['evidence_id','url','archive_ref','status'])
        if i % 25 == 0: print('captures', i, '/',len(availability),'links',len(links), flush=True)
    assert len(links) + len(outcomes) == sum(len(v) for v in grouped.values())
    assert len({r['evidence_id'] for r in links+outcomes}) == len(links)+len(outcomes)
    print('archive links',len(links),'outcomes',len(outcomes),flush=True)


if __name__ == '__main__': main()

--- discovery.py ---
#!/usr/bin/env python3
"""Resumable CDX/SPN worker. Outputs stay in build/ until a reviewed top-up."""
import hashlib
import json
import re
import subprocess
import time
import urllib.parse
from run import CACHE, HERE, ROOT, read, write, fetch, on_page
from archive import FIELDS, same_page

END = time.monotonic() + 11 * 3600
LAST = {}


def request(url, bucket, interval):
    delay = 60
    while time.monotonic() < END:
        time.sleep(max(0, LAST.get(bucket, 0) + interval - time.monotonic()))
        header = CACHE/'discovery-headers.txt'
        p = subprocess.run(['curl','-sS','-L','-A','Mozilla/5.0 (Atlas evidence archive audit)','--max-time','45','-D',str(header),'-w','\n%{http_code}',url],capture_output=True,text=True)
        LAST[bucket] = time.monotonic()
        body, _, code = p.stdout.rpartition('\n')
        if code != '429': return body,code,header.read_text() if header.exists() else ''
        h = header.read_text() if header.exists() else ''
        retry = re.findall(r'(?im)^retry-after:\s*(\d+)',h)
        wait = max(delay,int(retry[-1]) if retry else 0)
        print('429',bucket,'backoff',wait,flush=True)
        time.sleep(min(wait,max(0,END-time.monotonic()))); delay = min(delay*2,1800)
    raise TimeoutError('11-hour worker window exhausted; resume from cache')


def cdx(url):
    query=urllib.parse.urlencode(dict(url=url,output='json',limit='-5',filter='statuscode:200'))
    body,code,_=request('https://web.archive.org/cdx/search/cdx?'+query,'cdx',5)
    if code != '200': return [],'CDX_FETCH_FAILED_'+code
    try:
        rows=json.loads(body)
        if not rows:return [],'NO_CAPTURE'
        header,*data=rows
        rows=[dict(zip(header,r)) for r in data]
        refs=['https://web.archive.org/web/'+r['timestamp']+'/'+r['original'] for r in rows if re.fullmatch(r'\d{14}',r.get('timestamp','')) and same_page(r.get('original',''),url)]
        return list(reversed(refs)),'FOUND' if refs else 'NO_EXACT_CAPTURE'
    except (ValueError,TypeError,KeyError):return [],'CDX_INVALID_RESPONSE'


def main():
    grouped={}
    for e in read(HERE/'verdicts.csv'):
        if e['judgment']=='SUPPORTED':grouped.setdefault(e['url'],[]).append(e)
    results=ROOT/'build/l1-discovery';results.mkdir(exist_ok=True)
    for i,(url,rows) in enumerate(sorted(grouped.items()),1):
        if time.monotonic() >= END: break
        path=results/(hashlib.sha256(url.encode()).hexdigest()+'.json')
        if path.exists():continue
        refs,status=cdx(url)
        if status in ('NO_CAPTURE','NO_EXACT_CAPTURE'):
            _,code,_=request('https://web.archive.org/save/'+url,'spn',20)
            if code in ('200','201','202','302'):
                time.sleep(20); refs,status=cdx(url)
            else:status='SPN_FETCH_FAILED_'+code
        links=[]
        for ref in refs:
            if len(links)==len(rows):break
            # Back off on replay 429 independently of CDX/SPN; retry only after the wait.
            replay_delay = 60
            f = None
            while time.monotonic()<END:
                time.sleep(2)
                f=fetch(ref,refresh=True,fallback=False)
                if f['attempts'][-1]['status']!='429':break
                print('429 replay backoff',replay_delay,flush=True);time.sleep(max(replay_delay,f['attempts'][-1].get('retry_after',0)));replay_delay=min(replay_delay*2,1800)
            if f is None: raise TimeoutError('Worker window exhausted during replay; resume this URL')
            if f['status']!='ok' or f['attempts'][-1]['effective_url'].rstrip('/')!=ref.rstrip('/'):continue
            for e in rows:
                if any(x['evidence_id']==e['evidence_id'] for x in links):continue
                if on_page(e['quote'],ROOT/f['page']):
                    stamp=re.search(r'/web/(\d{14})/',ref)[1]
                    links.append(dict(evidence_id=e['evidence_id'],archive_ref=ref,captured_at=stamp[:4]+'-'+stamp[4:6]+'-'+stamp[6:8],created_by='atlas-L1-reverify-archive'))
        path.write_text(json.dumps(dict(url=url,status=status,links=links)))
        all_links=[r for p in results.glob('*.json') for r in json.loads(p.read_text())['links']]
        write(ROOT/'build/l1-cdx-links.csv',sorted(all_links,key=lambda x:x['evidence_id']),FIELDS)
        print(i,'/',len(grouped),'CDX',status,'links',len(all_links),flush=True)


if __name__=='__main__':main()

--- build.py ---
#!/usr/bin/env python3
"""Apply the verified archive packet; existing links are immutable. Re-run after rebasing."""
import re
import sys
from archive import FIELDS, same_page
from run import HERE, ROOT, read
sys.path.insert(0, str(ROOT / 'scripts'))
from shard_io import append_sorted


def main():
    evidence = {r['evidence_id']:r for p in sorted((ROOT/'data').glob('evidence_*.csv')) for r in read(p)}
    packet = read(HERE/'archive_links.csv')
    assert len({r['evidence_id'] for r in packet}) == len(packet)
    target = ROOT/'data/archive_links.csv'
    old = {r['evidence_id']:r for r in read(target)}
    additions = []
    for r in packet:
        eid = r['evidence_id']
        match = re.fullmatch(r'https://web\.archive\.org/web/(\d{14})/(https?://\S+)',r['archive_ref'])
        assert match and eid in evidence and same_page(match[2],evidence[eid]['source_ref']),r
        stamp = match[1]
        assert r['captured_at'] == stamp[:4]+'-'+stamp[4:6]+'-'+stamp[6:8],r
        if eid in old: assert old[eid] == r, ('immutable link conflict',eid)
        else: additions.append(r)
    if additions: append_sorted(target,additions,'evidence_id')
    print('archive_links added',len(additions),'packet rows',len(packet))


if __name__ == '__main__': main()

--- check_archives.py ---
#!/usr/bin/env python3
"""Freshly fetch every packet capture and fail on missing/unreadable/mismatched content."""
import re
import time
from archive import same_page
from run import HERE, ROOT, read, fetch, on_page


def main():
    packet = read(HERE/'archive_links.csv')
    verdicts = {r['evidence_id']:r for r in read(HERE/'verdicts.csv')}
    canonical = {r['evidence_id']:r for r in read(ROOT/'data/archive_links.csv')}
    assert len({r['evidence_id'] for r in packet}) == len(packet)
    pages = {}; failures = []
    for r in packet:
        eid,ref = r['evidence_id'],r['archive_ref']
        v = verdicts[eid]
        assert canonical.get(eid) == r, ('packet not applied',eid)
        assert v['judgment'] == 'SUPPORTED' and v['quote'], eid
        match = re.fullmatch(r'https://web\.archive\.org/web/(\d{14})/(https?://\S+)',ref)
        assert match and same_page(match[2],v['source_ref']),eid
        if ref not in pages:
            time.sleep(2)
            for attempt in range(3):
                pages[ref] = fetch(ref,refresh=True,fallback=False)
                if pages[ref]['status'] == 'ok': break
                code = pages[ref]['attempts'][-1]['status']
                if attempt < 2: time.sleep(max(60 * 2**attempt, pages[ref]['attempts'][-1].get('retry_after',0)) if code == '429' else 10)
        f = pages[ref]
        if f['status'] != 'ok' or f['attempts'][-1]['effective_url'].rstrip('/') != ref.rstrip('/') or not on_page(v['quote'],ROOT/f['page']):
            failures.append(eid)
    print('archive fresh re-fetch:',len(packet),'rows;',len(pages),'captures;',len(failures),'failures',flush=True)
    assert not failures, failures
    assert packet, 'No archive rows verified: archive gate incomplete (not a vacuous pass)'


if __name__ == '__main__': main()

--- known_answers.py ---
"""Four inspected live-page examples plus adversarial matcher mutations."""
from run import HERE, ROOT, read, fetch, on_page
rows = {r['evidence_id']: r for r in read(HERE / 'inputs.csv')}
for eid in ('EVD-013356', 'EVD-013357', 'EVD-013360', 'EVD-013379'):
    e = rows[eid]; f = fetch(e['url'])
    assert f['status'] == 'ok', (eid, f)
    assert on_page(e['quote'], ROOT / f['page']) is True, eid
    assert on_page(e['quote'] + ' zzzcalibrationneedlezzz', ROOT / f['page']) is False, eid
    assert on_page(' '.join(reversed(e['quote'].split())), ROOT / f['page']) is False, eid
    assert on_page('', ROOT / f['page']) is None
    print(eid, 'positive + inserted-defect + reversed-order PASS')

from archive import same_page
assert same_page('http://www.example.com/path/', 'https://EXAMPLE.com/path')
assert not same_page('https://example.com/path', 'https://example.com/other')
assert not same_page('https://example.com/path?x=1', 'https://example.com/path?x=2')
assert not same_page('https://example.com/Path', 'https://example.com/path')
print('V-59 URL binding mutations PASS')

import json
from unittest.mock import patch
import discovery
valid = json.dumps([['timestamp','original'],['20260102030405','https://example.com/claim']])
wrong = json.dumps([['timestamp','original'],['20260102030405','https://example.com/other']])
for payload, code, expected in ((valid,'200','FOUND'), (wrong,'200','NO_EXACT_CAPTURE'),
                                 ('[]','200','NO_CAPTURE'), ('{}','500','CDX_FETCH_FAILED_500'),
                                 ('not json','200','CDX_INVALID_RESPONSE')):
    with patch.object(discovery, 'request', return_value=(payload, code, '')):
        refs, status = discovery.cdx('https://example.com/claim')
        assert status == expected, (status, expected)
        if refs: assert refs == ['https://web.archive.org/web/20260102030405/https://example.com/claim']
print('CDX known-answer exact-page/other-page/empty/error/invalid-response PASS')

--- report.py ---
"""Deterministic yield and per-claim rates; no skipped rows can pass reconciliation."""
from collections import Counter
from run import HERE, ROOT, read, wilson
r = read(HERE/'verdicts.csv'); inputs = read(HERE/'inputs.csv'); leads = read(HERE/'repair_leads.csv')
assert {x['evidence_id'] for x in inputs} == {x['evidence_id'] for x in r}
assert len(r) == len(inputs) == len({x['evidence_id'] for x in r}) == 3683
assert len({x['source_ref'] for x in inputs}) == 1120
assert {x['evidence_id'] for x in leads} == {x['evidence_id'] for x in r if x['judgment'] != 'SUPPORTED'}
print('PIC18 evidence rows:', len(r), 'distinct cited refs:',len({x['source_ref'] for x in r}))
print('Judgments:',dict(Counter(x['judgment'] for x in r)))
print('Repair/availability leads:',len(leads),'/',len(r))
print('| Claim | Quote supported / all rows | Rate (Wilson 95% CI) | Supported / readable | Rate (Wilson 95% CI) | 2026-11-03 semantic audit |')
print('|-|-:|-|-:|-|-|')
old={'scope':'122/151 (81%; 74–86%)','existence':'12/24 (50%; 31–69%)','address':'7/13 (54%; 29–77%)','parent':'0/2 (0%; 0–66%)'}
for kind in sorted({x['claim_type'] for x in r}):
 g=[x for x in r if x['claim_type']==kind];n=len(g);k=sum(x['judgment']=='SUPPORTED' for x in g);m=sum(x['judgment']!='FETCH_FAILED' for x in g)
 lo,hi=wilson(k,n);a,b=wilson(k,m)
 print(f'| {kind} | {k}/{n} | {100*k/n:.1f}% ({lo}–{hi}%) | {k}/{m} | {100*k/m:.1f}% ({a}–{b}%) | {old.get(kind,"not sampled")} |')
if (HERE/'archive_links.csv').exists():
 links=read(HERE/'archive_links.csv');out=read(HERE/'archive_outcomes.csv')
 assert len(links)+len(out)==sum(x['judgment']=='SUPPORTED' for x in r)
 assert len({x['evidence_id'] for x in links+out})==len(links)+len(out)
 print('Archive packet:',len(links),'rows /',len({x['archive_ref'] for x in links}),'captures')
 print('Archive holds:',dict(Counter(x['status'] for x in out)))
