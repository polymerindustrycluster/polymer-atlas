"""Audit 13 smoke: the unit logic (what counts, when the stop fires), the reader calls and the fetch, run and score stages.
Pure functions come first so check.py can plant defects without a frame, a cache or a model."""
import hashlib, json, math, os, re, subprocess, sys, tempfile, threading, time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'scripts'))  # site_corpus.py
CORE_FIELDS = {'legal_name': 'name', 'site_name': 'name', 'status': 'status', 'operating_status': 'status', 'street_address': 'street',
               'county': 'county', 'hq_county': 'county', 'polymer_relevance': 'polymer_relevance'}
CORE_KINDS = set(CORE_FIELDS.values())
NAME_FIELDS = {'legal_name', 'site_name'}
LEGAL_FORM = {'inc', 'llc', 'corp', 'co', 'company', 'the'}  # AGENTS section 3's normalized-name rule, as the controller ruled 2026-11-24
VERDICTS = {'VERIFIED', 'CONTRADICTED', 'UNCONFIRMED', 'REQUEST'}
WITHHELD = '[withheld for blindness]'
CONTACT = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b')
FETCH_BUDGET = 6
MODELS = {'astra': 'gpt-6.2-astra', 'hydrogen': 'Gemini 4 Hydrogen (High)', 'sonnet': 'sonnet'}  # refused on any other resolved model
SOURCE_SHARE_CAP, PROMPT_TEXT_CAP = 15000, 60000


def words(s):
    import unicodedata
    return re.findall(r'[a-z0-9]+', unicodedata.normalize('NFKD', re.sub(r'[‐-―−]', ' ', s or '')).encode('ascii', 'ignore').decode().lower())


def quote_in_order(text, quote):
    q, w = words(quote), words(text)
    return bool(q) and any(w[i:i + len(q)] == q for i in range(len(w) - len(q) + 1))


def name_key(s):
    return [w for w in words(s) if w not in LEGAL_FORM]


def name_equivalent(held, source):
    """A held name that differs from the source's only by a legal-form word or punctuation names the same entity (not a contradiction)."""
    return bool(name_key(held)) and name_key(held) == name_key(source)


# ---------------------------------------------------------------- packet checks
def dependency_check(row, depends):
    """PROTOCOL 'What goes to a reader': a judged value must not reach a reader without what is needed to judge it."""
    values = json.loads(row['values_json'])
    for field, needs in depends.get(row['table'], {}).items():
        if values.get(field) and values[field] != WITHHELD:
            blank = [n for n in needs if not values.get(n)]
            held_back = [n for n in needs if values.get(n) == WITHHELD]
            if blank or held_back:
                raise ValueError(f'dependency: {field} needs {",".join(blank + held_back)} ({"blank" if blank else "withheld"})')


def drop_withheld_tokens(row, R):
    """SCHEMA 4.24: a not_found_pending_refetch process or market value is withheld from public display, so it is not published and not judged."""
    if 'value_basis' not in getattr(R, '_basis', {}) and not hasattr(R, '_basis'):
        try:
            R._basis = defaultdict(set)
            for r in R.rows('value_basis'):
                if r['basis'] == 'not_found_pending_refetch':
                    R._basis[r['record_table'], r['record_id'], r['field']].add(r['value'])
        except (KeyError, OSError, Exception):
            R._basis = defaultdict(set)
    hide = {f: R._basis[row['table'], row['record_id'], f] for f in ('processes', 'markets_served') if R._basis.get((row['table'], row['record_id'], f))}
    if not hide:
        return row
    values = json.loads(row['values_json'])
    for f, tokens in hide.items():
        if values.get(f):
            values[f] = ';'.join(t for t in values[f].split(';') if t not in tokens)
    return dict(row, values_json=json.dumps(values, ensure_ascii=False, sort_keys=True))


def targets_of(row):
    """Checklist keys a reader must assess: every populated judged value of the record, its polymer relevance, every populated child value."""
    values = json.loads(row['values_json'])
    keys = [f for f in row['columns_under_audit'].split(';') if values.get(f)] + ['polymer_relevance']
    for i, ch in enumerate(json.loads(row['context_json']).get('children', []), 1):
        keys += [f'c{i}.{f}' for f, v in ch['values'].items() if v]
    return keys


def field_of(target):
    return target.split('.', 1)[-1]


# ---------------------------------------------------------------- reading a reader's answer
def parse_answer(text):
    """The first JSON object in a reader's output, or None."""
    text = (text or '').strip()
    m = re.search(r'```(?:json)?\s*(\{.*\})\s*```', text, re.S)
    for cand in ([m[1]] if m else []) + [text, text[text.find('{'):text.rfind('}') + 1] if '{' in text else '']:
        try:
            obj = json.loads(cand)
            if isinstance(obj, dict) and isinstance(obj.get('findings'), list):
                return obj
        except ValueError:
            pass
    return None


def read_findings(answer, sources, targets, held):
    """Normalise one reader's answer to {target: dict(status, reason, ...)}. sources: id -> full text. held: target -> held value.
    A contradiction counts only when its quote replays in order against the cited source; a verified claim that quotes
    a source must replay too; a missing assessment or an unserved REQUEST is unconfirmed."""
    got = {}
    for f in answer.get('findings', []):
        if isinstance(f, dict) and f.get('target') in targets and f['target'] not in got:
            got[f['target']] = f
    out = {}
    for t in targets:
        f = got.get(t)
        if f is None:
            out[t] = dict(status='UNCONFIRMED', reason='missing_assessment')
            continue
        v, quote, text = str(f.get('verdict', '')).upper(), f.get('quote') or '', sources.get(f.get('source_id'))
        base = dict(raw=v, source_id=f.get('source_id'), settling_fact=f.get('settling_fact'), core_effect=f.get('core_effect'), source_value=f.get('source_value'))
        replays = bool(quote and text is not None and quote_in_order(text, quote))
        if v not in VERDICTS:
            out[t] = dict(base, status='UNCONFIRMED', reason='invalid_verdict')
        elif v == 'CONTRADICTED':
            if field_of(t) in NAME_FIELDS and name_equivalent(held.get(t, ''), f.get('source_value') or ''):
                out[t] = dict(base, status='VERIFIED', reason='legal_form_name_only', note=True)
            elif not replays:
                out[t] = dict(base, status='UNCONFIRMED', reason='quote_not_replayed')
            else:
                out[t] = dict(base, status='CONTRADICTED', reason='replayed')
        elif v == 'VERIFIED':
            out[t] = dict(base, status='VERIFIED', reason='ok') if (not quote or replays) else dict(base, status='UNCONFIRMED', reason='verified_quote_not_replayed')
        elif v == 'REQUEST':
            out[t] = dict(base, status='UNCONFIRMED', reason='unserved_request', request_url=f.get('request_url'))
        else:
            out[t] = dict(base, status='UNCONFIRMED', reason='unsettled' if f.get('settling_fact') else 'unsettled_without_fact')
    return out


def is_core(target, finding):
    if '.' in target:  # child finding: gates only when the reader ties it to a core field and the contradiction replayed
        return finding.get('core_effect') in CORE_KINDS
    return field_of(target) in CORE_FIELDS


def combine(primary, second, second_independent=True):
    """Final status per target from the locked primary and the optional second read. A replayed contradiction from either read stands
    (a vote cannot erase it). An unconfirmed claim clears only when an independent second read verified it; the builder-family
    exception reader can object but never clear."""
    final = {}
    for t, p in primary.items():
        s = (second or {}).get(t)
        if 'CONTRADICTED' in (p['status'], s and s['status']):
            final[t] = (p if p['status'] == 'CONTRADICTED' else s) | dict(by='primary' if p['status'] == 'CONTRADICTED' else 'second')
        elif p['status'] == 'UNCONFIRMED' and not (s and second_independent and s['status'] == 'VERIFIED' and p['reason'] != 'missing_assessment'):
            final[t] = dict(p, by='primary')
        elif s and s['status'] == 'UNCONFIRMED':
            final[t] = dict(s, by='second')
        elif p['status'] == 'UNCONFIRMED':  # cleared by an independent verified second read
            final[t] = dict(s, by='second', cleared=True)
        else:
            final[t] = dict(p, by='primary')
    return final


def flagged(primary, receipts):
    """Second read is mandatory for any error, uncertainty, missing assessment or adverse replay."""
    return any(v['status'] != 'VERIFIED' for v in primary.values()) or any(r.get('status') in ('CONTRADICTS', 'UNRESOLVED') for r in receipts)


def record_outcome(final):
    """-> dict: counts toward k when any core target is contradicted; descriptive contradictions and unconfirmed claims are tallied by field."""
    core = sorted({field_of(t) if '.' not in t else 'child:' + (f.get('core_effect') or '') for t, f in final.items() if f['status'] == 'CONTRADICTED' and is_core(t, f)})
    return dict(k=bool(core), contradicted_core=core,
                contradicted_desc=sorted(field_of(t) for t, f in final.items() if f['status'] == 'CONTRADICTED' and not is_core(t, f)),
                unconfirmed={t: f['reason'] for t, f in final.items() if f['status'] == 'UNCONFIRMED'},
                audited=sorted(final), notes=sorted(t for t, f in final.items() if f.get('note')))


def plant_detected(primary_raw, field):
    """A control passes only when the reader marks the planted field itself CONTRADICTED or specifically unsettled (with the settling fact)."""
    f = primary_raw.get(field)
    return bool(f) and (f['status'] == 'CONTRADICTED' or (f['status'] == 'UNCONFIRMED' and f['reason'] == 'unsettled'))


class Board:
    """Sealed-order scoring. Feed items in sealed position order; the stop fires at `stop_at` records with a contradicted core field."""
    def __init__(self, stop_at=3):
        self.stop_at, self.k, self.real, self.plants, self.stopped_at, self.invalid = stop_at, 0, [], [], None, None

    def add(self, pos, kind, outcome=None, detected=None, provider=None):
        if self.stopped_at or self.invalid:
            return False
        if kind == 'plant':
            self.plants.append(dict(pos=pos, provider=provider, detected=bool(detected)))
            if not detected:
                self.invalid = f'plant at position {pos} ({provider}) was missed: stage invalid, suspend and diagnose'
                return False
        else:
            self.real.append(dict(pos=pos, **outcome))
            self.k += int(outcome['k'])
            if self.k >= self.stop_at:
                self.stopped_at = pos
        return not (self.stopped_at or self.invalid)


# ---------------------------------------------------------------- model calls
def run_process(cmd, text, timeout, procs, cwd):
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd, start_new_session=True)
    procs.add(p)
    try:
        out, err = p.communicate(text, timeout=timeout)
        return p.returncode, out, err
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, 9)
        return 124, '', 'timeout'
    finally:
        procs.discard(p)


def call_model(provider, prompt, procs, timeout=1500):  # the call timeout is the stall watchdog: a hung lane ends as a failed call, which suspends the run
    """One fresh call, from an empty directory. -> dict(text, model, usage, metered, elapsed, error). The resolved model is asserted:
    anything but the registry's deep Astra / Hydrogen / standard Sonnet is refused (never Neon or Argon)."""
    t0, cwd = time.time(), tempfile.mkdtemp(prefix='a13-call-')
    res = dict(provider=provider, text='', model='', usage=None, metered=False, error='', prompt_bytes=len(prompt.encode()))
    if provider == 'hydrogen':  # agy directly, so the stream's usage record survives (agy-headless keeps only the text)
        guard = '[Answer only from the material in this message. Do not search the web, fetch a URL, run a command or read a file.]\n\n'
        event = json.dumps({'event': 'user', 'message': {'content': guard + prompt}})
        rc, out, err = run_process(['agy', '--model', MODELS['hydrogen'], '--mode', 'plan', '--sandbox', '--input-format', 'stream-json', '--output-format', 'stream-json'], event, timeout, procs, cwd)
        events = [json.loads(l) for l in out.splitlines() if l.strip().startswith('{')]
        init = next((e['init'] for e in events if e.get('event') == 'init'), {})
        result = next((e['result'] for e in reversed(events) if e.get('event') == 'result'), {})
        res.update(model=init.get('model', ''), text=result.get('response', ''), usage=result.get('usage'))
        res['metered'] = bool(res['usage'] and 'input_tokens' in res['usage'])
        if rc or result.get('status') != 'SUCCESS' or result.get('denied_actions'):
            res['error'] = f'agy rc={rc} status={result.get("status")} {err[:120]}'
    else:
        lane = {'astra': 'codex', 'sonnet': 'claude'}[provider]
        rc, out, err = run_process(['council-run', '--providers', lane, '--effort', 'deep' if provider == 'astra' else 'standard', '--json'], prompt, timeout, procs, cwd)
        try:
            rec = json.loads(out)['providers'][0]
            res.update(model=rec.get('resolved_model') or rec.get('model') or '', text=rec.get('output') or '', usage=rec.get('usage'))
            res['metered'] = bool(res['usage'] and res['usage'].get('input_tokens') is not None)
            if rec.get('status') != 'success':
                res['error'] = f'{rec.get("status")} {rec.get("failure_kind")} {str(rec.get("error"))[:120]}'
        except (ValueError, KeyError, IndexError):
            res['error'] = f'council-run rc={rc} unparseable: {(err or out)[:120]}'
    res['elapsed'] = round(time.time() - t0, 1)
    if not res['error']:
        if MODELS[provider].lower() not in res['model'].lower():
            res['error'] = f'refused: resolved model {res["model"]!r} is not {MODELS[provider]}'
        elif not res['text'].strip():
            res['error'] = 'no output'
        elif not res['metered']:
            res['error'] = 'unmetered call'
    return res


def input_tokens(usage):
    """Tokens the meter counts: fresh input plus cache reads (the owner's meter charges both)."""
    u = usage or {}
    return (u.get('input_tokens') or 0) + (0 if u.get('cache_read_tokens') is None else u['cache_read_tokens'])


# ---------------------------------------------------------------- prompts
def instructions():
    return (HERE / 'READER_INSTRUCTIONS.md').read_text()


def excerpt(text, terms, cap=SOURCE_SHARE_CAP):
    """Sanitised excerpt: contact data redacted; long pages keep windows around the held name, street and locality, else the head."""
    text = CONTACT.sub('[contact redacted]', ' '.join((text or '').split()))
    if len(text) <= cap:
        return text
    spans = []
    for t in terms:
        for m in re.finditer(re.escape(t), text, re.I):
            spans.append((max(0, m.start() - 700), min(len(text), m.end() + 700)))
            if len(spans) > 40:
                break
    merged = []
    for a, b in sorted(spans):
        merged.append([a, b]) if not merged or a > merged[-1][1] else merged[-1].__setitem__(1, max(b, merged[-1][1]))
    body = ' … '.join(text[a:b] for a, b in merged)
    return (text[:2500] + ' … ' + body)[:cap] if merged else text[:cap]


def build_prompt(row, sources, receipts, requested=()):
    """One record, its scoped children, the cached excerpts and the replay receipts. No builder family, history, order or control label."""
    checklist = targets_of(row)
    packet = dict(record=row['record_label'], table=row['table'], judged_values=json.loads(row['values_json']), context=json.loads(row['context_json']),
                  cited_sources=row['cited_sources'], evidence=json.loads(row['evidence_json']))
    blocks = '\n\n'.join(f'[{sid}] {s["url"]} (fetched {s["fetched_at"]}; {s["availability"]})\n{s["excerpt"]}' for sid, s in sources.items()) or '(no source could be fetched)'
    rcpt = '\n'.join(f'[{r["id"]}] {r["text"]}' for r in receipts) or '(none)'
    return (f'{instructions()}\n\n=== RECORD ===\n{json.dumps(packet, ensure_ascii=False, indent=1)}\n\n=== SOURCES (fetched once by script; cite by id) ===\n{blocks}\n\n'
            f'=== REPLAY RECEIPTS (filing checks already run by script; cite by id) ===\n{rcpt}\n\n=== CHECKLIST: give exactly one finding per key ===\n{json.dumps(checklist)}\n'
            + (f'\nSources you requested were added above: {list(requested)}. Give final findings now; REQUEST is no longer available.\n' if requested else ''))


# ---------------------------------------------------------------- stages
def read_csv(path):
    import csv
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def urls_of(row, limit=FETCH_BUDGET):
    """Fetch list for one record: its own website, then evidence and cited URLs in order. http(s) only, never LinkedIn, at most six."""
    seen = []
    values = json.loads(row['values_json'])
    cands = [values.get('website', '')] + [e['url'] for e in json.loads(row['evidence_json'])] + re.findall(r'https?://[^\s;,)\]>"]+', row['cited_sources'])
    for u in cands:
        u = (u or '').strip().rstrip('.')
        if u.startswith(('http://', 'https://')) and 'linkedin.com' not in u and u not in seen:
            seen.append(u)
    return seen[:limit]


def fetch_stage(draw_dir, cache_dir, load, packet_rows, depends, skip_blocked=False):
    import smoke, replays
    from site_corpus import Corpus
    receipt = json.loads((draw_dir / 'draw_receipt.json').read_text())
    sample = read_csv(draw_dir / 'sample.csv')
    R = load(receipt['at'])
    entries = [dict(table=s['table'], record_id=s['record_id'], pos=s['pos'], **({'field': s['plant_field'], 'donor_record_id': s['donor_record_id']} if s['kind'] == 'plant' else {}),
                    stratum='PIC18_RECORDS') for s in sample]
    ids = {(s['table'], s['record_id']): s['blind_id'] for s in sample}
    built, problems = packet_rows(R, entries, frozenset(), ids)
    if problems and not skip_blocked:
        sys.exit(f'refusing to fetch: {len(problems)} sampled packets fail the gate: {Counter(problems.values())}')
    if problems:  # known-answer run only: the skipped records are listed, never silently dropped
        (draw_dir / 'skipped.json').write_text(json.dumps({f'{t}|{i}': why for (t, i), why in problems.items()}, indent=1))
        print(f'SKIPPED {len(problems)} packets that fail the gate (known-answer run only): {Counter(problems.values())}')
    corpus = Corpus(cache_dir)
    want = {u for _, row, _ in built for u in urls_of(row)}
    def one(u):
        try:
            r = corpus.fetch(u)
            return u, dict(status=r['status'], http=r['http_status'], final_url=r['final_url'], fetched_at=r['fetched_at'], sha256=r['sha256'], text_file=r['text_file'])
        except Exception as e:  # noqa: BLE001  a fetch failure is availability, never evidence
            return u, dict(status='FETCH_FAILED', error=type(e).__name__)
    with ThreadPoolExecutor(4) as pool:
        manifest = dict(pool.map(one, sorted(want)))
    keys = [(e['table'], e['record_id']) for e, _, _ in built]
    rcpts, rblocks, rcounts = replays.coverage(R, keys, replays.STORE)
    (draw_dir / 'packets.jsonl').unlink(missing_ok=True)
    with open(os.open(draw_dir / 'packets.jsonl', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w') as f:
        for e, row, masked in built:
            f.write(json.dumps(dict(row=row, masked=masked, plant=e.get('field', ''), urls=urls_of(row))) + '\n')
    (cache_dir / 'manifest.json').write_text(json.dumps(manifest, indent=1, sort_keys=True))
    (draw_dir / 'receipts.json').unlink(missing_ok=True)
    with open(os.open(draw_dir / 'receipts.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w') as f:
        json.dump(dict(receipts=rcpts, no_replayer=rblocks, counts=rcounts), f, indent=1, default=list)
    ok = sum(1 for m in manifest.values() if m['status'] == 'ok')
    print(f'fetched {len(manifest)} distinct sources once ({ok} ok, {len(manifest) - ok} unavailable); {len(built)} packets; replay classes {rcounts}')
    return 0


def run_stage(draw_dir, cache_dir, out, a):
    sample = read_csv(draw_dir / 'sample.csv')
    packets = {json.loads(l)['row']['blind_id']: json.loads(l) for l in open(draw_dir / 'packets.jsonl')}
    sample = [s for s in sample if s['blind_id'] in packets]
    manifest = json.loads((cache_dir / 'manifest.json').read_text())
    families = json.loads((draw_dir / 'families.json').read_text())
    rc_doc = json.loads((draw_dir / 'receipts.json').read_text())
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True, mode=0o700)
    ledger_path, procs, lock, stop = out / 'ledger.jsonl', set(), threading.Lock(), threading.Event()
    spent = Counter()

    def log(**kw):
        with lock:
            with open(ledger_path, 'a') as f:
                f.write(json.dumps(kw, sort_keys=True) + '\n')

    def source_set(pk, extra=()):
        urls = list(dict.fromkeys(list(pk['urls']) + list(extra)))[:FETCH_BUDGET]
        row = pk['row']
        terms = [v for f, v in json.loads(row['values_json']).items() if f in ('legal_name', 'site_name', 'street_address', 'city', 'hq_city') and v]
        sources = {}
        for n, u in enumerate(urls, 1):
            m = manifest.get(u, {})
            text = (cache_dir / m['text_file']).read_text() if m.get('status') == 'ok' and (cache_dir / m['text_file']).exists() else ''
            sources[f'S{n}'] = dict(url=m.get('final_url') or u, fetched_at=m.get('fetched_at', 'not fetched'), availability=m.get('status', 'NOT_FETCHED'), full=text,
                                    excerpt=excerpt(text, terms) if text else '(unavailable: a failed fetch is not evidence about the claim)')
        return sources

    def read(provider, s, pk, role, extra=()):
        """One fresh call (plus at most one REQUEST round). -> (findings, receipts used, answer) or None when the call produced no usable output."""
        row, rc = pk['row'], [r for r in rc_doc['receipts'].get(f"{s['table']}|{s['record_id']}", [])]
        for round_ in (1, 2):
            sources = source_set(pk, extra)
            prompt = build_prompt(row, {k: v for k, v in sources.items()}, rc, extra if round_ == 2 else ())
            res = None
            for attempt in (1, 2):
                if stop.is_set():
                    return None
                res = call_model(provider, prompt, procs)
                ans = parse_answer(res['text']) if not res['error'] else None
                log(blind_id=s['blind_id'], role=role, provider=provider, round=round_, attempt=attempt, model=res['model'], usage=res['usage'], metered=res['metered'],
                    elapsed=res['elapsed'], prompt_bytes=res['prompt_bytes'], error=res['error'] or ('unparseable answer' if ans is None else ''), forced=s['provider'] != provider)
                if res['usage']:
                    spent[provider] += input_tokens(res['usage'])
                if ans is not None or res['error'].startswith(('refused', 'unmetered')):
                    break
            if ans is None:
                return None
            targets, held = targets_of(row), {}
            vals = json.loads(row['values_json'])
            held = {t: vals.get(t) for t in targets if '.' not in t}
            found = read_findings(ans, {k: v['full'] for k, v in sources.items()}, targets, held)
            asks = [f['request_url'] for f in found.values() if f.get('raw') == 'REQUEST' and (f.get('request_url') or '').startswith('http')]
            if round_ == 1 and asks and len(sources) < FETCH_BUDGET:
                want = [u for u in dict.fromkeys(asks)][:FETCH_BUDGET - len(sources)]
                from site_corpus import Corpus
                corpus = Corpus(cache_dir)
                for u in want:
                    r = corpus.fetch(u)
                    manifest[u] = dict(status=r['status'], http=r['http_status'], final_url=r['final_url'], fetched_at=r['fetched_at'], sha256=r['sha256'], text_file=r['text_file'])
                extra = want
                continue
            return found, rc, ans
        return None

    def other(provider, fams):
        order = [p for p in ('hydrogen', 'astra', 'sonnet') if p != provider] if provider == 'astra' else [p for p in ('astra', 'sonnet') if p != provider]
        fam = {'astra': 'openai', 'hydrogen': 'google', 'sonnet': 'anthropic'}
        independent = [p for p in order if fam[p] not in fams]
        return (independent[0], True) if independent else (order[0], False)

    def work(s):
        if stop.is_set():
            return s, None
        pk = packets[s['blind_id']]
        fams = set(families.get(f"{s['table']}|{s['record_id']}", []))
        first = read(s['provider'], s, pk, 'primary')
        if first is None:
            return s, dict(status='NO_OUTPUT')
        found, rc, ans = first
        lock_sha = hashlib.sha256(json.dumps(found, sort_keys=True).encode()).hexdigest()
        log(blind_id=s['blind_id'], role='lock', provider=s['provider'], sha256=lock_sha)  # first verdicts are locked before any other family sees the case
        item = dict(status='READ', primary=found, lock=lock_sha, second=None, exception=False, plant=s['kind'] == 'plant')
        if s['kind'] == 'real':
            need = flagged(found, rc) or 'uncertain' in fams
            coin = s['check_coin'] == '1' and 'uncertain' not in fams
            if need or coin:
                prov, independent = other(s['provider'], fams)
                item.update(second_for='flag' if need else 'check', exception=not independent, second_provider=prov)
                if stop.is_set():
                    return s, dict(status='INCOMPLETE')
                sec = read(prov, s, pk, 'second')
                if sec is None:
                    return s, dict(status='SECOND_MISSING', **item)
                item['second'] = sec[0]
        return s, item

    board = Board(a.stop_at)
    results, pending, status = [], {}, 'COMPLETE'
    with ThreadPoolExecutor(a.window) as pool:
        futs = {s['pos']: (s, pool.submit(work, s)) for s in sample}
        for s in sample:  # sealed order
            _, fut = futs[s['pos']]
            s, item = fut.result()
            if item is None or item['status'] in ('INCOMPLETE',):
                continue
            if item['status'] in ('NO_OUTPUT', 'SECOND_MISSING'):
                status = 'SUSPENDED_NO_OUTPUT'
                log(blind_id=s['blind_id'], role='halt', reason=item['status'])
                stop.set()
                break
            if s['kind'] == 'plant':
                ok = plant_detected(item['primary'], s['plant_field'])
                board.add(int(s['pos']), 'plant', detected=ok, provider=s['provider'])
                results.append(dict(pos=int(s['pos']), blind_id=s['blind_id'], kind='plant', provider=s['provider'], plant_field=s['plant_field'], detected=ok, table=s['table'], record_id=s['record_id']))
            else:
                final = combine(item['primary'], item['second'], not item['exception'])
                outcome = record_outcome(final)
                board.add(int(s['pos']), 'real', outcome)
                results.append(dict(pos=int(s['pos']), blind_id=s['blind_id'], kind='real', provider=s['provider'], table=s['table'], record_id=s['record_id'], coin=s['check_coin'],
                                    second_provider=item.get('second_provider'), second_for=item.get('second_for'), exception=item['exception'], lock=item['lock'], **outcome,
                                    primary_status={t: f['status'] for t, f in item['primary'].items()}, second_status={t: f['status'] for t, f in (item['second'] or {}).items()},
                                    withheld=len(packets[s['blind_id']]['masked'])))
            if board.stopped_at or board.invalid:
                status = 'STOPPED_AT_K' if board.stopped_at else 'SUSPENDED_PLANT_MISSED'
                stop.set()
                break
            if a.max_tokens_m and sum(spent.values()) > a.max_tokens_m * 1e6:
                status = 'HALTED_TOKEN_BUDGET'
                stop.set()
                break
        if stop.is_set():
            for p in list(procs):
                try:
                    os.killpg(p.pid, 9)
                except OSError:
                    pass
            for _, f in futs.values():
                f.cancel()
    done = {r['pos'] for r in results}
    incomplete = [dict(pos=int(s['pos']), kind=s['kind']) for s in sample if int(s['pos']) not in done]
    summary = dict(status=status, k=board.k, stop_at=a.stop_at, stopped_at=board.stopped_at, invalid=board.invalid, results=results, incomplete_calls=incomplete,
                   input_tokens_spent=dict(spent))
    (out / 'results.json').write_text(json.dumps(summary, indent=1, sort_keys=True))
    print(f'run {status}: k={board.k} real={len(board.real)} plants={len(board.plants)} incomplete={len(incomplete)} tokens={dict(spent)}')
    return 0 if status in ('COMPLETE', 'STOPPED_AT_K') else 1


def score_stage(run_dir):
    doc = json.loads((run_dir / 'results.json').read_text())
    ledger = [json.loads(l) for l in open(run_dir / 'ledger.jsonl')]
    real = [r for r in doc['results'] if r['kind'] == 'real']
    plants = [r for r in doc['results'] if r['kind'] == 'plant']
    aud, unc, cc, cd = Counter(), Counter(), Counter(), Counter()
    reasons = Counter()
    for r in real:
        for t in r['audited']:
            aud[field_of(t)] += 1
        for t, why in r['unconfirmed'].items():
            unc[field_of(t)] += 1
            reasons[why] += 1
        cc.update(r['contradicted_core'])
        cd.update(r['contradicted_desc'])
    calls = [l for l in ledger if l.get('role') in ('primary', 'second') and 'usage' in l]
    per = defaultdict(lambda: dict(calls=0, metered=0, input_m=0.0, input_tokens=[]))
    for l in calls:
        p = per[l['provider']]
        p['calls'] += 1
        p['metered'] += int(bool(l['metered']))
        if l['metered']:
            p['input_tokens'].append(input_tokens(l['usage']))
    cost = {k: dict(calls=v['calls'], metered_calls=v['metered'], mean_input_tokens=round(sum(v['input_tokens']) / len(v['input_tokens'])) if v['input_tokens'] else None,
                    total_input_m=round(sum(v['input_tokens']) / 1e6, 3)) for k, v in per.items()}
    n = len(real)
    report = dict(status=doc['status'], audited_real_records=n, k=doc['k'], stop_at=doc['stop_at'], stopped_at_position=doc['stopped_at'],
                  contradicted_core_fields=dict(cc), contradicted_descriptive_fields=dict(cd),
                  unconfirmed_by_field={f: dict(unconfirmed=unc[f], audited_values=aud[f], share=round(unc[f] / aud[f], 3)) for f in sorted(aud) if unc[f]},
                  descriptive_error_rate_by_field={f: dict(contradicted=cd[f], audited_values=aud[f], rate=round(cd[f] / aud[f], 3)) for f in sorted(cd)},
                  unconfirmed_reasons=dict(reasons),
                  plants=dict(by_provider={p: dict(planted=sum(1 for x in plants if x['provider'] == p), detected=sum(1 for x in plants if x['provider'] == p and x['detected'])) for p in sorted({x['provider'] for x in plants})},
                              stage_invalid=doc['invalid']),
                  routing_exceptions=sum(1 for r in real if r['exception']), second_reads=sum(1 for r in real if r.get('second_provider')), check_only_discoveries=sum(1 for r in real if r.get('second_for') == 'check' and r['k']),
                  incomplete_calls=len(doc['incomplete_calls']), cost_per_call_by_provider=cost,
                  cost_per_record_input_m=round(sum(v['total_input_m'] for v in cost.values()) / n, 3) if n else None)
    (run_dir / 'score.json').write_text(json.dumps(report, indent=1, sort_keys=True))
    print(json.dumps(report, indent=1, sort_keys=True))
    return 0
