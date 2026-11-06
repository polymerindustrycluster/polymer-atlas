RE-REVIEW PR #137 L1: try to REFUTE correctness of a scoped preserved-quote audit + verified archive subset. No semantic claim verification or archive completeness is claimed. Current outputs: 3,683 evidence rows / 1,120 refs, 3,261 quote matches / 422 repair-availability leads (75 quote absent, 34 no-quote holds, 264 fetch failures, 49 redirect holds). 34 archive links / 11 freshly checked captures / 0 failures; 3,227 supported-row archive holds. Canonical data changes remain exactly 34 archive links; no evidence/tier/org/site changes.

Initial Codex and Grok councils REFUTED the earlier in-flight code. Fixes: parse archive URLs structurally (query trailing slash/case preserved), bind every verdict/input/quote to canonical evidence, exact disposition sets and unique leads, narrow HTML claim to text-node extraction rather than visibility, conservative redirect/wall/decoding posture, hold ambiguous quote spans, hash-frozen publication packet, fresh checked receipts required BEFORE builder application, default fresh checker covers whole canonical table, replay retry/backoff and deadline guards, worker aggregate regenerated on resume and filtered to current eligible IDs. SPN query submissions held until encoded route verified.

Ground-truth checks: known_answers.py PASS (4 inspected records + matcher/CDX/URL/posture adversarial fixtures); check_mutations.py PASS (forged quote, duplicate lead, unknown disposition ID, missing receipt each fail); check_archives.py --packet-only PASS 34/11/0; report.py PASS exact yields + exact generated README results; build.py rerun 0 additions; validate.py zero errors. Run from current worktree; caches under build/l1-cache, not committed. Worker writes ONLY build/ candidates; frozen PR files are not mutated by it.

Review all current files below and identify concrete defects, distinguishing the original in-flight code from current code. Return VERDICT APPROVE or REFUTE with inspected/uninspected scope. Original council findings are recorded in README; raw outputs remain worktree build/l1-refute-{codex,grok}.txt.

Latest correction: Codex3 proved a replay redirect query-value defect in the full-URL rstrip comparison. The new same_capture helper binds exact capture timestamp and structurally compares the captured original URL, preserving query values. It is used by collector, fresh checker and long worker. Actual gate regression tests exact success plus query/timestamp rejection and verifies failed receipts stay empty. No frozen frame/judgments/current34archive rows changed; current rows have no queries. Re-review this fix against 4ef764e.

--- README.md ---
# PIC-18 preserved-quote re-verification and archive links — 2026-11-06

L1 (`atlas-L1-reverify-archive`), controller-claimed; draft PR #137. Frame pinned to bd57a08: every OH site whose
physical county, stripping a trailing ` County`, is in `scripts/regions.py` PIC18, plus those sites' parent organizations,
regardless of HQ. No status/tier filter. Exactly 3,683 own_site evidence rows / 1,120 distinct cited references;
4 references (8 rows) are not bare URLs. This matches the controller's baseline. HQ-only and HQ-plus-footprint
alternatives are excluded. First users: Atlas integrator and evidence auditors, from PR review on 2026-11-06.

## Results (unit: evidence rows)

This measures **preserved quote presence**, not the semantic truth of a claim or site attribution. SUPPORTED requires
contiguous normalized words, using the unchanged `words`, `on_page`, and `wilson` functions from the calibrated
2026-11-03 audit. NOT_SUPPORTED means the preserved quote is absent from the readable returned text, not that the
underlying claim is false. PARTIAL is a no-preserved-quote/ambiguous-quote hold; it does not assert semantic partial
support. WRONG_PAGE holds a redirect to another host/path/query, even if the destination might be a valid successor.
FETCH_FAILED is transport, recognized wall, uncertain decoding, or unavailable source identity; never evidence of absence.
All unresolved records have lane posture STILL_UNCERTAIN; there are no organization REJECT/status decisions.

The 2026-11-03 audit's 142/191 (74%, Wilson 68–80%) assessed claim semantics on a different sampled frame, then checked
its selected quotes. The table below puts it beside the new quote-presence rates for context. These different
estimands do **not** demonstrate an improvement in semantic support. All-row denominators count availability/no-quote
holds against support. Readable denominators exclude FETCH_FAILED; redirect holds still count against support.
Wilson intervals are descriptive binomial reference intervals on a full frame, not sampling uncertainty.

<!-- RESULTS BEGIN -->
PIC18 evidence rows: 3683 distinct cited refs: 1120
Judgments: {'SUPPORTED': 3261, 'PARTIAL': 34, 'NOT_SUPPORTED': 75, 'FETCH_FAILED': 264, 'WRONG_PAGE': 49}
Repair/availability leads: 422 / 3683
| Claim | Quote supported / all rows | Rate (Wilson 95% CI) | Supported / readable | Rate (Wilson 95% CI) | 2026-11-03 semantic audit |
|-|-:|-|-:|-|-|
| activity | 0/3 | 0.0% (0–56%) | 0/1 | 0.0% (0–79%) | not sampled |
| address | 19/37 | 51.4% (36–67%) | 19/28 | 67.9% (49–82%) | 7/13 (54%; 29–77%) |
| existence | 30/59 | 50.8% (38–63%) | 30/46 | 65.2% (51–77%) | 12/24 (50%; 31–69%) |
| liveness | 0/2 | 0.0% (0–66%) | 0/1 | 0.0% (0–79%) | not sampled |
| parent | 5/7 | 71.4% (36–92%) | 5/5 | 100.0% (57–100%) | 0/2 (0%; 0–66%) |
| scope | 3207/3575 | 89.7% (89–91%) | 3207/3338 | 96.1% (95–97%) | 122/151 (81%; 74–86%) |
Archive packet: 34 rows / 11 captures
Archive holds: {'CAPTURE_FETCH_FAILED': 82, 'NO_CAPTURE': 25, 'CAPTURE_REDIRECT_HOLD': 5, 'FRESH_RECHECK_FAILED': 50, 'CAPTURE_PENDING': 106, 'RATE_LIMIT_HOLD': 2959}
<!-- RESULTS END -->

## Method and artifact boundary

Fetch once per exact cited reference, curl/browser UA with Jina raw fallback, local cache in ignored `build/l1-cache/`.
HTML text nodes exclude script/style/noscript; this is **not** a browser visibility/rendering audit (hidden/template
nodes may remain). No truncation; undecodable cached text is held if replacement characters occur. Recognized
challenge walls are held; no fixed phrase list can identify every interstitial. Source-ref redirects are compared
structurally, preserving query values; Jina must supply a matching URL Source header. Unverifiable response identity
is held. Raw bodies, headers, effective URLs, hashes and timestamps are local; verdicts retain observation timestamps.
No private, licensed, CRM, vault or personal information is used. Data-estate lookup reported missing Windows-only
Documents catalogues on this Mac; repository references and the live public pages suffice for this pass.

Quote extraction uses the house `Quote: "..." | ...` notes format, then an unambiguous single quoted claim_detail span.
Multiple quoted fragments and punctuation-only quotes are held. Inputs, verdicts, and quotes are bound field-for-field
to the canonical evidence; a forged verdict quote fails. No evidence row, tier, org/site, inclusion decision or registry
link changes. No new EVD IDs are allocated. No dedupe/create procedure is triggered. All 34 archive links reference
existing supports_A evidence rows; the archive has no tier effect.

The controller delegated sole archive_links.csv application to L1 under AGENTS §2.7. Git bd57a08 is the pre-pass backup;
this README is the pass journal. An initially verified 101-row capture packet was reduced to 34 after fresh transport
failures. These are availability exclusions, not quote contradictions. The revised conservative live classification
changed the preliminary 3,344 matches to 3,261 (redirect/decoding/ambiguous-quote holds); no matching threshold changed.
Existing evidence and published archive facts remain append-only. All 34 included rows still pass the revised live posture.

## Archive discovery and holds

Legacy availability discovery hit sustained 429s after approximately 100 successful responses; the parallel batch
lacked shared backoff and was stopped. The snapshot collector now uses a shared global stop and labels rate-limit holds.
No unavailable capture ever becomes an archive link. Normal replay is required; a replay redirect is held. URL binding
is stricter than V-59 on query values: scheme/www/host case and a trailing **path** slash may differ; query case and
slashes must not. Raw metadata stay local. `archive_outcomes.csv` supplies exactly one outcome for every supported
row without a link. `repair_leads.csv` supplies exactly one settling-fact lead for every non-supported live row.

The controller authorized a resumable `discovery.py` worker (11-hour run window): CDX at most once per five seconds,
Save Page Now at most once per 20 seconds when no exact capture is returned, 429 exponential backoff from 60 seconds.
Numeric Retry-After is honored. Accepted SPN is not evidence of a capture: CDX must expose a readable exact capture
containing the quote. Query-string SPN submissions are held until the encoded submit route is verified;
existing query-string captures can still qualify. Per-URL receipts under `build/l1-discovery/` support resume; the aggregate is rebuilt on restart.
The worker writes only local `build/l1-cdx-links.csv`, never canonical or frozen PR files. Restart errors are explicit
holds; move aside failed URL receipts locally to retry. The worker's deadline cannot reuse a preceding URL's replay.
No archive completeness is claimed. A later top-up requires fresh checks and review. Rest-OH then PA are a separate PR.

## Named checks and reproduction

```sh
python3 tasks/evidence-reverify-archive-2026-11-06/run.py
python3 tasks/evidence-reverify-archive-2026-11-06/known_answers.py
python3 tasks/evidence-reverify-archive-2026-11-06/check_mutations.py
# Discovery may regenerate a candidate packet; do not change the frozen packet during checking.
python3 tasks/evidence-reverify-archive-2026-11-06/check_archives.py --packet-only
python3 tasks/evidence-reverify-archive-2026-11-06/build.py
python3 tasks/evidence-reverify-archive-2026-11-06/report.py
python3 scripts/validate.py
```

Fresh `check_archives.py --packet-only`: **34 rows / 11 captures / 0 failures**, PASS. It binds canonical quotes,
re-fetches every capture, rejects any packet mutation, and writes per-row receipts bound to the packet/quote hashes.
Failures clear the receipts and fail closed. `build.py` refuses any row without that successful receipt; application
therefore follows the content gate. The default check also requires the whole canonical archive table to equal the
checked packet, so an earlier applied row cannot disappear from verification. Builder rerun: zero additions, PASS.
`report.py`: exact canonical/input/verdict binding, unique leads, exact disposition sets and README-result equality,
PASS. `validate.py`: zero errors after application, PASS. No scripts/ edits, so its pytest gate is not triggered.

Known answers: four inspected real records EVD-013356/013357/013360/013379; inserted words and reversed order fail,
empty quote returns None. URL mutations reject another path, path case, query value case and query trailing slash.
Controlled redirect, ASCII challenge-wall and decoding-error fixtures hold. CDX known answers cover exact/other/empty/
HTTP error/invalid JSON. All PASS. `check_mutations.py` injects forged verdict quote, duplicate repair lead and unknown
archive-outcome ID, plus a missing fresh-check receipt before application; every defect fails the named report check and all originals restore byte-for-byte.

## Independent refute record

Initial council Codex (gpt-6-astra/max, `--effort deep`): REFUTE. Valid findings: structural query URL binding;
canonical quote binding; missing exact disposition/lead uniqueness assertions; overclaim of visible text; packet freeze;
worker aggregate recovery. Fixed with structural URL parsing, canonical cross-checks, exact set/uniqueness checks,
narrowed text-extraction description, packet hash checks and restart aggregate regeneration. Ambiguous spans now hold.

Initial council Grok (grok-4.7/xhigh, `--effort deep`): REFUTE. Valid findings: unflagged final-page redirects, wall/
decoding ambiguity, quote extraction ambiguity, apply-before-fresh-check and canonical rows outside packet. Fixed with
conservative response posture, guarded quotes, mandatory fresh receipts and whole-table default archive check. Settling
page wording describes a future readable source, not an assertion that failed pages loaded. Sticky legacy cache is
explicit; the controller's paced CDX/SPN worker is the continuation route. Some review findings concerned the earlier
in-flight code and were already fixed before publication (429 label/backoff, terminal gates, deadline handling).

Controller 05:55 ruling supersedes council-only ordering and permits draft publication before refutes. Codex and Grok
clerk re-review of the corrected commit is pending; **no Done claim**. The original refute outputs are local, with the
verdicts and responses recorded here. No semantic claim re-verification, replacement evidence, scope/ring/vocabulary
ruling, rendered visibility audit or PDF text extraction is claimed.

Codex3 clerk @4ef764e: REFUTE one remaining replay-query gate defect. Reproduced before editing with the clerk's
controlled fixture: a requested query value key=a/ redirected to key=a passed and wrote a receipt. Current 34 rows
have no queries; no bad current row was demonstrated. Fixed all three replay-effective-response comparisons via
same_capture: exact capture timestamp plus structural original-page comparison, preserving query case/slashes.
check_replay_binding.py exercises the actual receipt gate: exact replay passes; changed query and capture timestamp
fail and leave no successful receipt. PASS. The continuation cache collector receives the same shared guard.
Existing frame, judgments, quotes and canonical archive rows do not change. Corrected clerk re-review is required.

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
    if m: q = m.group(1).strip()
    else:
        spans = re.findall(r'["“]([^"“”]+)["”]', e['claim_detail'], re.S)
        q = spans[0].strip() if len(spans) == 1 else ''
    return q if ns['words'](q) else ''


def live_posture(f, url):
    if f['status'] != 'ok': return 'FETCH_FAILED'
    text = (ROOT / f['page']).read_text()
    lower = text.lower()
    if '\ufffd' in text or any(x in lower for x in ("this site can't be reached", 'enable javascript and cookies to continue', 'checking if the site connection is secure', 'access to this page has been denied', 'please complete the security check', 'request blocked')):
        return 'FETCH_FAILED'
    attempt = f['attempts'][-1]
    effective = attempt['effective_url']
    if attempt['route'] != url:
        # Jina's URL Source header, not its wrapper URL, identifies the returned page.
        key = hashlib.sha256(url.encode()).hexdigest()
        effective = ''
        for raw in CACHE.glob(key + '*.raw'):
            if hashlib.sha256(raw.read_bytes()).hexdigest() == f.get('sha256'):
                m = re.search(r'(?m)^URL Source:\s*(https?://\S+)', raw.read_text(errors='replace'))
                effective = m[1] if m else ''
                break
    if not effective: return 'FETCH_FAILED'
    from urllib.parse import urlsplit
    a,b = urlsplit(url),urlsplit(effective)
    norm = lambda x: (x.hostname.lower().removeprefix('www.') if x.hostname else '', x.path.rstrip('/'), x.query)
    return 'ok' if norm(a) == norm(b) else 'WRONG_PAGE'


def frame():
    sites = [r for p in sorted((ROOT / 'data').glob('sites_*.csv')) for r in read(p)]
    si = {r['site_id'] for r in sites if r['state'] == 'OH' and re.sub(r' County$', '', r['county']) in PIC18}
    oi = {r['org_id'] for r in sites if r['site_id'] in si}
    rows = [r for p in sorted((ROOT / 'data').glob('evidence_*.csv')) for r in read(p) if r['source_class'] == 'own_site' and ((r['record_table'] == 'organizations' and r['record_id'] in oi) or (r['record_table'] == 'sites' and r['record_id'] in si))]
    assert len({r['evidence_id'] for r in rows}) == len(rows)
    for r in rows: r.update(url=r['source_ref'], quote=quote(r))
    write(HERE / 'inputs.csv', rows, list(rows[0]))
    return rows


def bound_verdicts():
    canonical = {r['evidence_id']: r for p in sorted((ROOT/'data').glob('evidence_*.csv')) for r in read(p)}
    inputs, verdicts = read(HERE/'inputs.csv'), read(HERE/'verdicts.csv')
    assert len(inputs) == len({r['evidence_id'] for r in inputs})
    assert len(verdicts) == len({r['evidence_id'] for r in verdicts})
    indexed = {r['evidence_id']:r for r in inputs}
    assert set(indexed) == {r['evidence_id'] for r in verdicts}
    for v in verdicts:
        e, i = canonical[v['evidence_id']], indexed[v['evidence_id']]
        assert all(i[k] == v[k] == value for k,value in e.items()), v['evidence_id']
        assert i['quote'] == v['quote'] == quote(e), v['evidence_id']
        assert i['url'] == v['url'] == e['source_ref'], v['evidence_id']
    return {r['evidence_id']:r for r in verdicts}


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
        posture = live_posture(f,e['url'])
        if posture == 'FETCH_FAILED': judgment, reason = 'FETCH_FAILED', 'No unambiguous readable UTF-8 primary page; transport, decoding or challenge hold.'
        elif posture == 'WRONG_PAGE': judgment, reason = 'WRONG_PAGE', 'Cited URL redirects to a different host, path or query; identity/page review required.'
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
    from urllib.parse import urlsplit
    def norm(url):
        p = urlsplit(url.strip())
        return (p.netloc.lower().removeprefix('www.'), p.path.rstrip('/'), p.query, p.fragment)
    return norm(a) == norm(b)


def same_capture(a, b):
    pattern = r'https://web\.archive\.org/web/(\d{14})/(https?://\S+)'
    left, right = re.fullmatch(pattern, a), re.fullmatch(pattern, b)
    return bool(left and right and left[1] == right[1] and same_page(left[2], right[2]))


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
            if f['status'] == 'ok' and same_capture(effective, ref):
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
from archive import FIELDS, same_page, same_capture

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
    supported_ids = {e['evidence_id'] for rows in grouped.values() for e in rows}
    results=ROOT/'build/l1-discovery';results.mkdir(exist_ok=True)
    all_links=[r for p in results.glob('*.json') for r in json.loads(p.read_text())['links'] if r['evidence_id'] in supported_ids]
    write(ROOT/'build/l1-cdx-links.csv',sorted(all_links,key=lambda x:x['evidence_id']),FIELDS)
    for i,(url,rows) in enumerate(sorted(grouped.items()),1):
        if time.monotonic() >= END: break
        path=results/(hashlib.sha256(url.encode()).hexdigest()+'.json')
        if path.exists():continue
        refs,status=cdx(url)
        if status in ('NO_CAPTURE','NO_EXACT_CAPTURE') and urllib.parse.urlsplit(url).query:
            # shortcut: query-string SPN targets held until an encoded submit route is verified.
            status = 'SPN_QUERY_HOLD'
        elif status in ('NO_CAPTURE','NO_EXACT_CAPTURE'):
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
            if f['status']!='ok' or not same_capture(f['attempts'][-1]['effective_url'],ref):continue
            for e in rows:
                if any(x['evidence_id']==e['evidence_id'] for x in links):continue
                if on_page(e['quote'],ROOT/f['page']):
                    stamp=re.search(r'/web/(\d{14})/',ref)[1]
                    links.append(dict(evidence_id=e['evidence_id'],archive_ref=ref,captured_at=stamp[:4]+'-'+stamp[4:6]+'-'+stamp[6:8],created_by='atlas-L1-reverify-archive'))
        path.write_text(json.dumps(dict(url=url,status=status,links=links)))
        all_links=[r for p in results.glob('*.json') for r in json.loads(p.read_text())['links'] if r['evidence_id'] in supported_ids]
        write(ROOT/'build/l1-cdx-links.csv',sorted(all_links,key=lambda x:x['evidence_id']),FIELDS)
        print(i,'/',len(grouped),'CDX',status,'links',len(all_links),flush=True)


if __name__=='__main__':main()

--- build.py ---
#!/usr/bin/env python3
"""Apply the verified archive packet; existing links are immutable. Re-run after rebasing."""
import re
import hashlib
import sys
from archive import FIELDS, same_page
from run import HERE, ROOT, read, bound_verdicts
sys.path.insert(0, str(ROOT / 'scripts'))
from shard_io import append_sorted


def main():
    evidence = {r['evidence_id']:r for p in sorted((ROOT/'data').glob('evidence_*.csv')) for r in read(p)}
    packet = read(HERE/'archive_links.csv')
    verdicts = bound_verdicts()
    receipts = {r['evidence_id']:r for r in read(HERE/'archive_checks.csv')}
    assert set(receipts) == {r['evidence_id'] for r in packet}, 'Run fresh packet check before application'
    digest = hashlib.sha256((HERE/'archive_links.csv').read_bytes()).hexdigest()
    assert len({r['evidence_id'] for r in packet}) == len(packet)
    target = ROOT/'data/archive_links.csv'
    old = {r['evidence_id']:r for r in read(target)}
    additions = []
    for r in packet:
        eid = r['evidence_id']
        v, receipt = verdicts[eid], receipts[eid]
        assert v['judgment'] == 'SUPPORTED' and v['quote'], eid
        assert receipt['archive_ref'] == r['archive_ref'] and receipt['packet_sha256'] == digest, eid
        assert receipt['quote_sha256'] == hashlib.sha256(v['quote'].encode()).hexdigest(), eid
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
import sys
import hashlib
import time
from archive import same_page, same_capture
from run import HERE, ROOT, read, fetch, on_page, bound_verdicts, write


def main():
    frozen = (HERE/'archive_links.csv').read_bytes()
    packet = read(HERE/'archive_links.csv')
    verdicts = bound_verdicts()
    receipts = []
    fields = ['evidence_id','archive_ref','quote_sha256','packet_sha256','checked_at']
    write(HERE/'archive_checks.csv',[],fields)
    canonical = {r['evidence_id']:r for r in read(ROOT/'data/archive_links.csv')}
    assert len({r['evidence_id'] for r in packet}) == len(packet)
    pages = {}; failures = []
    for r in packet:
        eid,ref = r['evidence_id'],r['archive_ref']
        v = verdicts[eid]
        if '--packet-only' not in sys.argv:
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
        if f['status'] != 'ok' or not same_capture(f['attempts'][-1]['effective_url'], ref) or not on_page(v['quote'],ROOT/f['page']):
            failures.append(eid)
        else:
            receipts.append(dict(evidence_id=eid,archive_ref=ref,quote_sha256=hashlib.sha256(v['quote'].encode()).hexdigest(),packet_sha256=hashlib.sha256(frozen).hexdigest(),checked_at=f['fetched_at']))
    print('archive fresh re-fetch:',len(packet),'rows;',len(pages),'captures;',len(failures),'failures',flush=True)
    assert (HERE/'archive_links.csv').read_bytes() == frozen, 'packet changed during check'
    if '--packet-only' not in sys.argv:
        assert set(canonical) == {r['evidence_id'] for r in packet}, 'canonical rows outside checked packet'
    assert not failures, failures
    assert packet, 'No archive rows verified: archive gate incomplete (not a vacuous pass)'
    write(HERE/'archive_checks.csv',receipts,fields)


if __name__ == '__main__': main()

--- check_replay_binding.py ---
"""Gate-level regression for Codex3's redirected replay-query finding."""
import csv
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch
import check_archives as checker
from archive import same_capture

SOURCE = 'https://example.test/page?key=a/'
REF = 'https://web.archive.org/web/20260102030405/' + SOURCE
QUOTE = 'This known preserved quote names the actual manufacturing activity stated in the evidence record'


def gate_case(effective, expected):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);(root/'data').mkdir()
        row=dict(evidence_id='EVD-TEST',archive_ref=REF,captured_at='2026-01-02',created_by='test')
        for target in (root/'archive_links.csv',root/'data/archive_links.csv'):
            with target.open('w') as f:
                w=csv.DictWriter(f,fieldnames=list(row));w.writeheader();w.writerow(row)
        (root/'page.txt').write_text(QUOTE)
        verdict=dict(judgment='SUPPORTED',quote=QUOTE,source_ref=SOURCE)
        response=dict(status='ok',page='page.txt',attempts=[dict(effective_url=effective,status='200')],fetched_at='2026-11-06T11:00:00Z')
        with patch.object(checker,'HERE',root),patch.object(checker,'ROOT',root),patch.object(checker,'bound_verdicts',return_value={'EVD-TEST':verdict}),patch.object(checker,'fetch',return_value=response),patch.object(checker.time,'sleep',return_value=None),patch.object(sys,'argv',['check_archives.py']):
            try:
                checker.main()
            except AssertionError as e:
                assert not expected and e.args == (['EVD-TEST'],), e
            else:
                assert expected, 'redirected capture incorrectly passed fresh gate'
        receipts=list(csv.DictReader((root/'archive_checks.csv').open()))
        assert len(receipts) == int(expected)


assert same_capture(REF,REF)
assert not same_capture(REF,REF[:-1])
assert not same_capture(REF,REF.replace('key=a/','key=A/'))
assert not same_capture(REF,REF.replace('20260102030405','20260102030406'))
assert same_capture('https://web.archive.org/web/20260102030405/https://www.example.test/page/', 'https://web.archive.org/web/20260102030405/http://example.test/page')
gate_case(REF,True)
gate_case(REF[:-1],False)
gate_case(REF.replace('20260102030405','20260102030406'),False)
print('Replay binding PASS: exact positive, redirected query and different timestamp rejected; no failed receipts')

--- known_answers.py ---
"""Four inspected live-page examples plus adversarial matcher mutations."""
from pathlib import Path
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
assert not same_page('https://example.com/page?key=a/','https://example.com/page?key=a')
assert not same_page('https://example.com?key=A','https://example.com?key=a')
from run import quote
assert quote(dict(notes='',claim_detail='Uses "metal forming" and "laser cutting"')) == ''
assert quote(dict(notes='',claim_detail='"!!!"')) == ''
print('Query-value and ambiguous/empty-token quote mutations PASS')
from run import CACHE, live_posture
import tempfile
with tempfile.NamedTemporaryFile(mode='w+',dir=CACHE,suffix='.txt') as page:
    page.write('Known raw company page with ordinary readable text and a complete quoted activity statement.'); page.flush()
    state = dict(status='ok',page=str(Path(page.name).relative_to(ROOT)),attempts=[dict(route='https://example.com/page',effective_url='https://www.example.com/page/')])
    assert live_posture(state,'https://example.com/page') == 'ok'
    state['attempts'][0]['effective_url'] = 'https://example.com/other'
    assert live_posture(state,'https://example.com/page') == 'WRONG_PAGE'
    page.seek(0);page.truncate();page.write("this site can't be reached");page.flush()
    assert live_posture(state,'https://example.com/page') == 'FETCH_FAILED'
    page.seek(0);page.truncate();page.write('invalid decoding \ufffd');page.flush()
    assert live_posture(state,'https://example.com/page') == 'FETCH_FAILED'
print('Redirect, recognized wall and undecodable-text mutations PASS')

--- check_mutations.py ---
"""Prove reconciliation fails on the defects found by the independent refute."""
import subprocess
import sys
from run import HERE, read, write


def reject(name, mutate, command="report.py"):
    p = HERE/name
    before = p.read_bytes()
    try:
        rows = read(p); fields = list(rows[0]); mutate(rows)
        write(p,rows,fields)
        r = subprocess.run([sys.executable,str(HERE/command)],capture_output=True,text=True)
        assert r.returncode != 0 and 'AssertionError' in r.stderr, (name,r.stdout,r.stderr)
        print(name,'injected defect rejected')
    finally: p.write_bytes(before)


reject('verdicts.csv', lambda rows: rows[0].update(quote='forged replacement quote'))
reject('repair_leads.csv', lambda rows: rows.append(dict(rows[0])))
reject('archive_outcomes.csv', lambda rows: rows[0].update(evidence_id='EVD-NOT-IN-FRAME'))
reject('archive_checks.csv', lambda rows: rows.pop(), 'build.py')
print('Mutation checks PASS; all originals restored byte-for-byte')

--- report.py ---
"""Deterministic yield and per-claim rates; no skipped rows can pass reconciliation."""
from collections import Counter
import io, sys
real_print = print
buffer = io.StringIO()
def print(*args, **kwargs):
 kwargs["file"] = buffer
 real_print(*args, **kwargs)
from run import HERE, ROOT, read, wilson, bound_verdicts
r = list(bound_verdicts().values()); inputs = read(HERE/'inputs.csv'); leads = read(HERE/'repair_leads.csv')
assert {x['evidence_id'] for x in inputs} == {x['evidence_id'] for x in r}
assert len(r) == len(inputs) == len({x['evidence_id'] for x in r}) == 3683
assert len({x['source_ref'] for x in inputs}) == 1120
assert len(leads) == len({x['evidence_id'] for x in leads})
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
 assert {x['evidence_id'] for x in links+out} == {x['evidence_id'] for x in r if x['judgment']=='SUPPORTED'}
 print('Archive packet:',len(links),'rows /',len({x['archive_ref'] for x in links}),'captures')
 print('Archive holds:',dict(Counter(x['status'] for x in out)))

text = buffer.getvalue()
real_print(text,end='')
if '--emit' not in sys.argv:
 document = (HERE/'README.md').read_text()
 rendered = document.split('<!-- RESULTS BEGIN -->\n',1)[1].split('<!-- RESULTS END -->',1)[0]
 assert rendered == text, 'README result block differs from recomputed results'
