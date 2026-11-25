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
MODELS = {'astra': 'gpt-6.2-astra/max', 'hydrogen': 'Gemini 4 Hydrogen (High)', 'sonnet': 'claude-sonnet-5-5'}  # exact resolved identity; anything else is refused
GENERIC_FACT = re.compile(r'withheld|blindness|placeholder|redact|not available|unavailable|cannot (?:be )?(?:verif|confirm)', re.I)
SOURCE_SHARE_CAP, PROMPT_TEXT_CAP = 15000, 60000


def words(s):
    import unicodedata
    return re.findall(r'[a-z0-9]+', unicodedata.normalize('NFKD', re.sub(r'[‐-―−]', ' ', s or '')).encode('ascii', 'ignore').decode().lower())


def quote_in_order(text, quote):
    q, w = words(quote), words(text)
    return bool(q) and any(w[i:i + len(q)] == q for i in range(len(w) - len(q) + 1))


def name_key(s):
    s = re.sub(r'(?<![A-Za-z])((?:[A-Za-z]\.){2,})', lambda m: m[1].replace('.', ''), s or '')  # L.L.C. -> LLC
    return [w for w in words(s) if w not in LEGAL_FORM]


def name_equivalent(held, source):
    """A held name that differs from the source's only by a legal-form word or punctuation names the same entity (not a contradiction)."""
    return bool(name_key(held)) and name_key(held) == name_key(source)


# ---------------------------------------------------------------- packet checks
def dependency_check(row, depends):
    """PROTOCOL 'What goes to a reader': never mask a value needed to judge another field. A populated core field whose declared dependency is
    withheld or blank (the table DEPENDS says the reader needs it) cannot be judged and blocks."""
    values = json.loads(row['values_json'])
    for field, needs in depends.get(row['table'], {}).items():
        if values.get(field) and values[field] != WITHHELD:
            missing = [n for n in needs if not values.get(n) or values.get(n) == WITHHELD]
            if missing:
                raise ValueError(f'dependency: {field} needs {",".join(missing)} (withheld or blank)')


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


def targets_of(row, not_inspected=()):
    """Checklist keys a reader must assess: every populated judged value of the record, its polymer relevance, every populated child value,
    minus the filed values no replayer inspected (reported as NOT_INSPECTED, never judged and never unconfirmed)."""
    values = json.loads(row['values_json'])
    keys = [f for f in row['columns_under_audit'].split(';') if values.get(f)] + ['polymer_relevance']
    for i, ch in enumerate(json.loads(row['context_json']).get('children', []), 1):
        keys += [f'c{i}.{f}' for f, v in ch['values'].items() if v]
    return [k for k in keys if k not in set(not_inspected)]


def held_values(row):
    """target -> the value the record holds, for top-level and child targets."""
    held = dict(json.loads(row['values_json']))
    for i, ch in enumerate(json.loads(row['context_json']).get('children', []), 1):
        held.update({f'c{i}.{f}': v for f, v in ch['values'].items()})
    return held


NAICS_TARGETS = ('naics_primary', 'naics_primary_source_type', 'naics_primary_source_name', 'naics_confidence')
BAND_FIELDS = ('employee_band_site', 'employee_band_ohio')


def child_matches(ch, spec):
    """spec: {'table': t, 'match': {column: filed value}}. A child is the filed one when every identifying column equals the filed value
    (a withheld column cannot be judged either way, so it matches)."""
    return ch['table'] == spec['table'] and all(ch['values'].get(c) in (v, WITHHELD) for c, v in spec['match'].items())


def not_inspected_targets(row, ni):
    """ni = replays.coverage's per-record record of filed values with no replayer: {'fields': [...], 'children': [{'table', 'match'}]}. A NAICS value
    whose source name is blank or withheld cannot be attributed, so it is also not inspected (owner ruling 2026-11-24 15:15). Only the particular filed
    child is excluded, never its unrelated siblings of the same table."""
    values = json.loads(row['values_json'])
    out = set(f for f in (ni or {}).get('fields', []) if f in values and values[f])
    if row['table'] == 'organizations' and values.get('naics_primary') and values.get('naics_primary_source_name') in ('', WITHHELD, None):
        out |= {f for f in NAICS_TARGETS if values.get(f)}
    for i, ch in enumerate(json.loads(row['context_json']).get('children', []), 1):
        if any(child_matches(ch, spec) for spec in (ni or {}).get('children', [])):
            out |= {f'c{i}.{f}' for f, v in ch['values'].items() if v}
    return sorted(out)


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


LOCALITY_FIELDS = {'street_address', 'city', 'hq_city', 'county', 'hq_county', 'zip', 'state', 'hq_state'}


def contains(big, small):
    return any(big[i:i + len(small)] == small for i in range(len(big) - len(small) + 1))


def values_differ(held, source, field=''):
    """The source's stated value is incompatible with the held one: its words differ and are not a contiguous run of the held value's words.
    For an address or locality field the comparison also runs the other way (a source that adds the city or the county word to the held value
    agrees with it), and a street is compared by atlas.street_key (St = Street). Names and statuses get no reverse test: 'Acme Plastics' is not
    'Acme Plastics Division of Zeta Holdings'."""
    kh, ks = words(held), words(source)
    if not ks or ks == kh or contains(kh, ks):
        return False
    if field == 'street_address':
        from atlas import street_key
        if street_key(held) and street_key(held) == street_key(source):
            return False
    return not (field in LOCALITY_FIELDS and kh and contains(ks, kh))


def text_of(x):
    """A reader's field as text: anything but a string (a list, a number, null) is empty, never an exception."""
    return x if isinstance(x, str) else ''


def read_findings(answer, sources, targets, held, plant=None):
    """Normalise one reader's answer to {target: dict(status, reason, ...)}. sources: id -> text (S pages and R receipts). held: target -> held value.
    A contradiction counts only when it binds the incompatible fact, source and grain: a stated source_value that differs from the held value,
    a quote that replays in order against the cited source and contains that value. A verified claim needs a cited source that exists, and
    a quote it gives must replay. A missing assessment or an unserved REQUEST is unconfirmed. plant = dict(field, true, names) adds `plant_witness`
    to the planted field's finding ('' only when the contradiction names the record's true value from a clean witness). Typed garbage is empty text."""
    got = {}
    for f in answer.get('findings', []) if isinstance(answer.get('findings'), list) else []:
        if isinstance(f, dict) and isinstance(f.get('target'), str) and f['target'] in targets and f['target'] not in got:
            got[f['target']] = f
    out = {}
    for t in targets:
        f = got.get(t)
        if f is None:
            out[t] = dict(status='UNCONFIRMED', reason='missing_assessment')
            continue
        sid = f.get('source_id') if isinstance(f.get('source_id'), str) else None
        v, quote, sv, text = text_of(f.get('verdict')).upper(), text_of(f.get('quote')), text_of(f.get('source_value')), sources.get(sid)
        fact, effect, url = text_of(f.get('settling_fact')), text_of(f.get('core_effect')) or None, text_of(f.get('request_url'))
        base = dict(raw=v, source_id=sid, settling_fact=fact, core_effect=effect, source_value=sv, quote=quote)
        replays = bool(quote and text is not None and quote_in_order(text, quote))
        if v not in VERDICTS:
            out[t] = dict(base, status='UNCONFIRMED', reason='invalid_verdict')
        elif v == 'CONTRADICTED':
            if field_of(t) in NAME_FIELDS and name_equivalent(held.get(t, ''), sv):
                out[t] = dict(base, status='VERIFIED', reason='legal_form_name_only', note=True)
            elif text is None or not replays:
                out[t] = dict(base, status='UNCONFIRMED', reason='quote_not_replayed')
            elif not sv or not quote_in_order(quote, sv):
                out[t] = dict(base, status='UNCONFIRMED', reason='source_value_not_in_quote')
            elif not values_differ(held.get(t, ''), sv, field_of(t)):
                out[t] = dict(base, status='UNCONFIRMED', reason='source_value_equals_held')
            else:
                out[t] = dict(base, status='CONTRADICTED', reason='replayed')
        elif v == 'VERIFIED':
            if not text:  # a cited source that is missing or failed to load (empty text) supports nothing
                out[t] = dict(base, status='UNCONFIRMED', reason='verified_without_source')
            elif quote and not replays:
                out[t] = dict(base, status='UNCONFIRMED', reason='verified_quote_not_replayed')
            else:
                out[t] = dict(base, status='VERIFIED', reason='ok')
        elif v == 'REQUEST':
            out[t] = dict(base, status='UNCONFIRMED', reason='unserved_request', request_url=url)
        else:
            out[t] = dict(base, status='UNCONFIRMED', reason='unsettled' if specific_fact(fact) else 'unsettled_without_fact')
    if plant and plant['field'] in out:
        f = out[plant['field']]
        f['plant_witness'] = plant_witness(f, sources.get(f['source_id']) or '', plant) if f['status'] == 'CONTRADICTED' else 'not_contradicted'
    return out


HEDGE = re.compile(r'\b(?:former|formerly|previous|previously|prior|used to|moved|relocat\w*|supplier|suppliers|vendor|vendors|customer|customers|partner|partners|'
                   r'competitor|competitors|acquired|closed|sold|future|branch|affiliate|subsidiary|sister|'
                   r'headquarters|headquartered|hq|office|offices|'  # an address labelled headquarters or office only does not speak for the site (owner ruling 2026-11-25 11:27)

                   r'not|no|never|neither|nor|without|isn|aren|wasn|weren|doesn|didn|don|cannot)\b')  # another party, another time, another place, or a denial
WITNESS_WINDOW = 12  # words each side of the stated value that must be free of those
LEGAL_SUFFIX = {'inc', 'llc', 'corp', 'corporation', 'co', 'company', 'ltd', 'lp', 'llp'}
LOCATIVES = [('is', 'located', 'at'), ('is', 'at'), ('located', 'at')]  # the only locative verb phrases; 'headquartered at' is no longer one (owner ruling 2026-11-25 11:27)


def located_entity(ws, start, own, prev=None):
    """The strict rule (owner ruling 2026-11-25 07:41), not a word list. ws = the segment's words, `start` = where the address begins in it, `own` = the
    record's name and trade-name word lists. A location witness qualifies ONLY if
      (b) one clause whose subject is exactly the record's name (an optional legal suffix after it) opens the segment and is followed DIRECTLY by one of
          LOCATIVES and the address ('Acme Plastics, Inc. is located at 99 Oak Avenue'); or
      (a) an address block: the previous line is only the record's name (optional legal suffix) and this line is the address, optionally after the label
          'address' ('Acme Plastics' / '99 Oak Avenue, Akron').
    A preposition-led or modified subject ('the library next to Acme', 'Acme's customer at', 'Acme and Beta are at'), a first-person cue, a bare 'address'
    word and anything between the subject and the locative are held."""
    def bare(words_):
        words_ = list(words_)
        while words_ and words_[-1] in LEGAL_SUFFIX:
            words_.pop()
        return words_
    for k in own:
        if ws[:len(k)] == k:
            i = len(k)
            while i < start and ws[i] in LEGAL_SUFFIX:
                i += 1
            if tuple(ws[i:start]) in LOCATIVES:
                return True
    return prev is not None and bare(prev) in own and list(ws[:start]) in ([], ['address'])


LEGAL_ENTITY = re.compile(r"((?:[A-Z][\w&'.-]*\s+){0,3}[A-Z][\w&'.-]*)\s*,?\s+(?:LLC|L\.L\.C|Inc|Corp|Corporation|Ltd|LP|LLP|Co)\b")
SEGMENT_END = re.compile(r'(?<!\b[A-Za-z])(?<!\bInc)(?<!\bCo)(?<!\bCorp)(?<!\bLtd)(?<!\bLLC)(?<!\bSt)(?<!\bAve)(?<!\bRd)(?<!\bDr)(?<!\bNo)[.!?]\s+|\s\|\s|\n+')


def segments(text):
    """The page as sentence-like segments: [(raw, words)]. Abbreviations (Inc., St., initials) do not end one."""
    out, last = [], 0
    for m in list(SEGMENT_END.finditer(text)) + [None]:
        raw = text[last:m.start() if m else len(text)]
        out.append((raw, words(raw)))
        last = m.end() if m else last
    return out


def agrees(field, a, b):
    """The two stated values name the same thing: one contains the other, a street matches by street_key, a name differs only by legal form."""
    return bool(words(a) and words(b)) and (not values_differ(a, b, field) or not values_differ(b, a, field) or (field in NAME_FIELDS and name_equivalent(a, b)))


def witness_check(text, value, field, names, quote='', city=''):
    """'' when `text` positively attributes `value` to this record: in the segment holding the occurrence (inside the reader's quote, when given) the
    record's own name appears, or the page speaks in the first person for its own entity; no other party, time, place or denial is within
    WITNESS_WINDOW words; no other legal entity is named in the segment; and the page names no other street or county. Else the reason it is held."""
    segs = segments(text)
    tw = [w for _, ws in segs for w in ws]
    seg_of = [n for n, (_, ws) in enumerate(segs) for _ in ws]
    vw = words(value)
    occ = [i for i in range(len(tw) - len(vw) + 1) if vw and tw[i:i + len(vw)] == vw]
    if not occ:
        return 'true_value_not_stated', ''
    if quote:
        qw = words(quote)
        spans = [i for i in range(len(tw) - len(qw) + 1) if qw and tw[i:i + len(qw)] == qw]
        occ = [o for o in occ if any(sp <= o and o + len(vw) <= sp + len(qw) for sp in spans)]
        if not occ:
            return 'quote_does_not_hold_true_value', ''
    own = [k for n in names for k in (name_key(n), name_key(re.split(r'\s[-\u2013\u2014]\s', n)[0])) if k]  # a site name 'Acme - Akron' is also 'Acme'
    if not any(contains(tw, k) for k in own):
        return 'source_not_about_record', ''
    why, used = 'witness_hedged', ''
    for o in occ:
        if HEDGE.search(' '.join(tw[max(0, o - WITNESS_WINDOW):o + len(vw) + WITNESS_WINDOW])):
            continue
        n = seg_of[o]
        raw, ws = segs[n]
        first = next(i for i, g in enumerate(seg_of) if g == n)
        if not located_entity(ws, o - first, own, segs[n - 1][1] if n else None):
            why = 'witness_not_attributed'
            continue
        if any(not (name_key(m[1]) and any(contains(k, name_key(m[1])) or contains(name_key(m[1]), k) for k in own)) for m in LEGAL_ENTITY.finditer(raw)):
            why = 'witness_other_entity'
            continue
        why, used = '', ((segs[n - 1][0].strip() + '\n') if n else '') + raw.strip()[:400]  # the exact line and sentence this check accepted
        break
    if not why:
        if field == 'street_address':
            from atlas import NOTES_STREET_RE, notes_candidate_key, street_key
            # Several streets at the record's locality make the page ambiguous; a street in another city does not (a parent's or sister plant's address
            # elsewhere never speaks for this site). With no locality on the record every street on the page counts, as before.
            at_locality = lambda m: not words(city) or contains(words(text[m.end():m.end() + 80]), words(city))
            if {k for k in (notes_candidate_key(m[0]) for m in NOTES_STREET_RE.finditer(text) if at_locality(m)) if k} - {street_key(value)}:
                why = 'witness_ambiguous'
        if field in ('county', 'hq_county'):
            if {c.lower() for c in re.findall(r'\b([A-Z][a-z]+) County\b', text)} - {(words(value) or [''])[0]}:
                why = 'witness_ambiguous'
    return why, used or witness_context(text, value)


def witness_reason(text, value, field, names, quote='', city=''):
    return witness_check(text, value, field, names, quote, city)[0]


def witness_context(text, value):
    """The line before and the segment holding the first occurrence of `value`: what the hand-check reads to accept or reject a plant."""
    segs, vw = segments(text), words(value)
    for n, (raw, ws) in enumerate(segs):
        if vw and contains(ws, vw):
            return ((segs[n - 1][0].strip() + '\n') if n else '') + raw.strip()[:400]
    return ''


def plant_names(row, field, true_value):
    """The record's own names for the witness test: the unplanted name fields (or the true value when a name is what was planted)."""
    if field in NAME_FIELDS:
        return [true_value]
    values = json.loads(row['values_json'])
    return [v for f in NAME_FIELDS for v in [values.get(f)] if v and v != WITHHELD] + [t.strip() for t in (values.get('trade_names') or '').split(';') if t.strip() and t.strip() != WITHHELD]


def plant_city(row):
    """The record's locality for the witness test: its site or HQ city when the cell is readable, else '' (every street on the page then counts)."""
    values = json.loads(row['values_json'])
    return next((v for v in (values.get('city'), values.get('hq_city')) if v and v != WITHHELD), '')


def plant_witness(f, text, plant):
    """'' only when the finding's source_value agrees with the record's true value and the quote's occurrence of it is a clean witness."""
    if not agrees(plant['field'], plant['true'], f['source_value']):
        return 'source_value_not_true_value'
    return witness_reason(text, plant['true'], plant['field'], plant['names'], f['quote'], plant.get('city', ''))


def specific_fact(fact):
    """A settling fact that names what would settle the claim: not empty, not a blindness or availability excuse."""
    return len(words(fact)) >= 4 and not GENERIC_FACT.search(fact or '')


def is_core(target, finding):
    if '.' in target:  # child finding: gates only when the reader ties it to a core field and the contradiction replayed
        return finding.get('core_effect') in CORE_KINDS
    return field_of(target) in CORE_FIELDS


def combine(primary, second, second_independent=True):
    """Final status per target from the locked primary and the optional second read. A replayed contradiction from either read stands
    (a vote cannot erase it) and is marked disputed when the other read verified the value. An unconfirmed claim clears only when an
    independent second read verified it; the builder-family exception reader can object but never clear."""
    final = {}
    for t, p in primary.items():
        s = (second or {}).get(t)
        if 'CONTRADICTED' in (p['status'], s and s['status']):
            win = p if p['status'] == 'CONTRADICTED' else s
            other = s if win is p else p
            final[t] = dict(win, by='primary' if win is p else 'second', disputed=bool(other and other['status'] == 'VERIFIED'))
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


def record_outcome(final, not_inspected=()):
    """-> dict: counts toward k when any core target is contradicted; descriptive contradictions and unconfirmed claims are tallied by field;
    the deciding source, value and quote of every contradiction is kept (private results)."""
    hits = {t: f for t, f in final.items() if f['status'] == 'CONTRADICTED' and is_core(t, f)}
    core = sorted({field_of(t) if '.' not in t else 'child:' + (f.get('core_effect') or '') for t, f in hits.items()})
    return dict(k=bool(core), contradicted_core=core, contradicted_core_fields=sorted(field_of(t) for t in hits),  # one entry per finding: two children on one field count twice, k counts the record once
                
                contradicted_desc=sorted(field_of(t) for t, f in final.items() if f['status'] == 'CONTRADICTED' and not is_core(t, f)),
                unconfirmed={t: f['reason'] for t, f in final.items() if f['status'] == 'UNCONFIRMED'},
                audited=sorted(final), notes=sorted(t for t, f in final.items() if f.get('note')), not_inspected=sorted(not_inspected),
                disputed=sorted(t for t, f in final.items() if f.get('disputed')),
                deciding={t: dict(source_id=f['source_id'], source_value=f['source_value'], quote=f['quote'], by=f['by']) for t, f in final.items() if f['status'] == 'CONTRADICTED'})


def distinct(field, a, b):
    """Two stated values no reader could reconcile: neither contains the other, a street differs under street_key, a name differs beyond a legal-form word.
    A plant is only worth drawing when its donor value is distinct from the true one."""
    if not a or not b or WITHHELD in (a, b) or (field in NAME_FIELDS and name_equivalent(a, b)):
        return False
    return values_differ(a, b, field) and values_differ(b, a, field)


def plant_detected(primary_raw, field):
    """A control passes only when the reader marks the planted field itself CONTRADICTED with a quote that replays on the cached bytes and a source_value
    that names the record's TRUE value from a clean witness (`plant_witness` == ''): a quote about another field, another party, another time or an
    ambiguous page is held. UNCONFIRMED never detects, whatever its settling fact."""
    f = primary_raw.get(field)
    return bool(f) and f['status'] == 'CONTRADICTED' and f.get('plant_witness') == ''


def plant_verdict(row, field, true_value, sources):
    """-> (reason, source id, quote). reason is '' when the ideal answer detects this plant on the excerpts the reader will see, else why it cannot be;
    source id and quote are the source and the exact line and sentence the check itself used (the accepting one when eligible; else the last source that
    states the value). The ideal answer is a CONTRADICTED finding quoting the record's true value, run through read_findings (witness test included) and
    plant_detected unchanged. sources: id -> {'excerpt': ...}."""
    held = held_values(row)
    if field not in targets_of(row):
        return 'field_not_on_checklist', '', ''
    if held.get(field) == WITHHELD:
        return 'planted_cell_withheld', '', ''
    texts = {sid: s['excerpt'] for sid, s in sources.items()}
    plant, why, at = dict(field=field, true=true_value, names=plant_names(row, field, true_value), city=plant_city(row)), 'no_source_states_true_value', ('', '')
    for sid, text in texts.items():
        if quote_in_order(text, true_value):
            ideal = dict(findings=[dict(target=field, verdict='CONTRADICTED', source_id=sid, quote=true_value, source_value=true_value)])
            got = read_findings(ideal, texts, [field], held, plant)[field]
            at = (sid, witness_check(text, true_value, field, plant['names'], true_value, plant['city'])[1])
            if plant_detected({field: got}, field):
                return '', sid, at[1]
            why = 'planted_value_not_distinguishable_from_true_value' if got['status'] != 'CONTRADICTED' else got.get('plant_witness') or 'witness_held'
    return why, at[0], at[1]


def plant_reason(row, field, true_value, sources):
    return plant_verdict(row, field, true_value, sources)[0]


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
        if rc or result.get('status') != 'SUCCESS' or result.get('denied_actions'):
            res['error'] = f'agy rc={rc} status={result.get("status")} {err[:120]}'
    else:
        lane = {'astra': 'codex', 'sonnet': 'claude'}[provider]
        rc, out, err = run_process(['council-run', '--providers', lane, '--effort', 'deep' if provider == 'astra' else 'standard', '--json'], prompt, timeout, procs, cwd)
        try:
            rec = json.loads(out)['providers'][0]
            res.update(model=rec.get('resolved_model') or rec.get('model') or '', text=rec.get('output') or '', usage=rec.get('usage'))
            if rec.get('status') != 'success':
                res['error'] = f'{rec.get("status")} {rec.get("failure_kind")} {str(rec.get("error"))[:120]}'
        except (ValueError, KeyError, IndexError):
            res['error'] = f'council-run rc={rc} unparseable: {(err or out)[:120]}'
    res['elapsed'] = round(time.time() - t0, 1)
    res['metered'] = input_tokens(res['usage']) > 0  # a present but null or zero input count is unmetered
    if not res['error']:
        if res['model'] != MODELS[provider]:
            res['error'] = f'refused: resolved model {res["model"]!r} is not {MODELS[provider]}'
        elif not res['text'].strip():
            res['error'] = 'no output'
        elif not res['metered']:
            res['error'] = 'unmetered call'
    return res


def input_tokens(usage):
    """Tokens the meter counts: fresh input plus cache reads and writes, per provider's own record. Codex's input_tokens already includes its cached share."""
    u = usage or {}
    if isinstance(u.get('modelUsage'), dict):  # claude
        return sum((m.get('inputTokens') or 0) + (m.get('cacheReadInputTokens') or 0) + (m.get('cacheCreationInputTokens') or 0) for m in u['modelUsage'].values())
    return (u.get('input_tokens') or 0) + (u.get('cache_read_tokens') or 0)


# ---------------------------------------------------------------- prompts
def instructions():
    return (HERE / 'READER_INSTRUCTIONS.md').read_text()


def excerpt(text, terms, cap=SOURCE_SHARE_CAP):
    """Sanitised excerpt: contact data redacted; long pages keep windows around the held name, street and locality, else the head."""
    text = '\n'.join(' '.join(l.split()) for l in CONTACT.sub('[contact redacted]', text or '').splitlines() if l.strip())  # lines kept: an address block is a line structure
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


def build_prompt(row, sources, receipts, requested=(), not_inspected=()):
    """One record, its scoped children, the cached excerpts and the replay receipts. No builder family, history, order or control label."""
    checklist = targets_of(row, not_inspected)
    packet = dict(record=row['record_label'], table=row['table'], judged_values=json.loads(row['values_json']), context=json.loads(row['context_json']),
                  cited_sources=row['cited_sources'], evidence=json.loads(row['evidence_json']))
    blocks = '\n\n'.join(f'[{sid}] {s["url"]} (fetched {s["fetched_at"]}; {s["availability"]})\n{s["excerpt"]}' for sid, s in sources.items()) or '(no source could be fetched)'
    rcpt = '\n'.join(f'[{r["id"]}] {r["text"]}' for r in receipts) or '(none)'
    return (f'{instructions()}\n\n=== RECORD ===\n{json.dumps(packet, ensure_ascii=False, indent=1)}\n\n=== SOURCES (fetched once by script; cite by id) ===\n{blocks}\n\n'
            f'=== REPLAY RECEIPTS (filing checks already run by script; cite by id) ===\n{rcpt}\n\n'
            f'=== NOT INSPECTED (filed values no script could replay; give no finding and do not judge them) ===\n{json.dumps(sorted(not_inspected))}\n\n'
            f'=== CHECKLIST: give exactly one finding per key ===\n{json.dumps(checklist)}\n'
            + (f'\nSources you requested were added above: {list(requested)}. Give final findings now; REQUEST is no longer available.\n' if requested else ''))


# ---------------------------------------------------------------- stages
SMOKE_N, PLANTS_EACH, STOP_AT = 40, 3, 3
CAPS_M = {'astra': 1.691, 'hydrogen': 1.923, 'sonnet': 0.535}  # sizes.py spend(SMOKE, 3) per provider (the protocol's stage budgets); a projected overrun halts for repricing


def read_csv(path):
    import csv
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def frame_mode(receipt):
    return 'preflight_receipt_sha256' in receipt['inputs']


def verify_seal(draw_dir, receipt, stop_at=None):
    """The sealed sample is what runs: digest, size, plant counts and stop count in frame mode (tunable only for explicit-list fixtures)."""
    if sha256((draw_dir / 'sample.csv').read_bytes()) != receipt['sample_sha256']:
        sys.exit('refusing: sample.csv differs from the draw receipt')
    if frame_mode(receipt):
        if receipt['n_real'] != SMOKE_N or receipt['plants'] != dict.fromkeys(CAPS_M, PLANTS_EACH):
            sys.exit('refusing: the sealed sample is not 40 real records and 3 plants per provider')
        if stop_at is not None and stop_at != STOP_AT:
            sys.exit(f'refusing: the stop count is {STOP_AT} in a frame run')


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


def write_private(path, obj_or_lines):
    path.unlink(missing_ok=True)
    with open(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w') as f:
        f.write(obj_or_lines)


def fetch_urls(cache_dir, urls):
    """Corpus.fetch once per distinct URL (a cached page is not fetched again). A fetch failure is availability, never evidence."""
    from site_corpus import Corpus
    corpus = Corpus(cache_dir)

    def one(u):
        try:
            r = corpus.fetch(u)
            return u, dict(status=r['status'], http=r['http_status'], final_url=r['final_url'], fetched_at=r['fetched_at'], sha256=r['sha256'], text_file=r['text_file'])
        except Exception as e:  # noqa: BLE001
            return u, dict(status='FETCH_FAILED', error=type(e).__name__)
    with ThreadPoolExecutor(4) as pool:
        return dict(pool.map(one, sorted(urls)))


def build_sources(pk, manifest, cache_dir, extra=()):
    """The bounded source set a reader gets for one packet: id -> url, fetch time, availability, full cached text and the redacted excerpt."""
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


def fetch_stage(draw_dir, cache_dir, load, packet_rows, approved=frozenset(), store=None, skip_blocked=False, true_of=None):
    import replays
    receipt = json.loads((draw_dir / 'draw_receipt.json').read_text())
    verify_seal(draw_dir, receipt)
    sample = read_csv(draw_dir / 'sample.csv')
    R = load(receipt['at'])
    entries = [dict(table=s['table'], record_id=s['record_id'], pos=s['pos'], **({'field': s['plant_field'], 'donor_record_id': s['donor_record_id']} if s['kind'] == 'plant' else {}),
                    stratum='PIC18_RECORDS') for s in sample]
    ids = {(s['table'], s['record_id']): s['blind_id'] for s in sample}
    built, problems = packet_rows(R, entries, approved, ids)
    if problems and (frame_mode(receipt) or not skip_blocked):
        sys.exit(f'refusing to fetch: {len(problems)} sampled packets fail the gate: {Counter(problems.values())}')
    if problems:  # explicit-list fixture only: the skipped records are listed, never silently dropped
        write_private(draw_dir / 'skipped.json', json.dumps({f'{t}|{i}': why for (t, i), why in problems.items()}, indent=1))
        print(f'SKIPPED {len(problems)} packets that fail the gate (known-answer run only): {Counter(problems.values())}')
    manifest = fetch_urls(cache_dir, {u for _, row, _ in built for u in urls_of(row)})
    plants = [(e, row) for e, row, _ in built if e.get('field')]
    if plants:  # draw-time bytes are not guaranteed to be run-time bytes: every sealed plant must still be detectable on what was fetched now
        assert true_of, 'plants need the true-value reader'
        bad = Counter(why for e, row in plants if (why := plant_reason(row, e['field'], true_of(R, e['table'], e['record_id'], e['field']),
                                                                       build_sources(dict(row=row, urls=urls_of(row)), manifest, cache_dir))))
        if bad:
            sys.exit(f'refusing to fetch: {sum(bad.values())} sealed plants are no longer detectable on the fetched pages: {dict(bad)}')
    keys = [(e['table'], e['record_id']) for e, _, _ in built]
    rcpts, ni_classes, rcounts, ni, due = replays.coverage(R, keys, store or replays.STORE)
    for t, i in keys:
        if len(rcpts.get(f'{t}|{i}', [])) != due.get(f'{t}|{i}', 0):
            sys.exit(f'refusing to fetch: {t}|{i} is due {due.get(f"{t}|{i}", 0)} filing receipts and was issued {len(rcpts.get(f"{t}|{i}", []))}')
    lines = []
    for e, row, masked in built:
        k = f"{e['table']}|{e['record_id']}"
        lines.append(json.dumps(dict(row=row, masked=masked, plant=e.get('field', ''), urls=urls_of(row), not_inspected=not_inspected_targets(row, ni.get(k)), due=due.get(k, 0),
                                     **({'plant_true': true_of(R, e['table'], e['record_id'], e['field'])} if e.get('field') else {}))))
    write_private(draw_dir / 'packets.jsonl', '\n'.join(lines) + '\n')
    (cache_dir / 'manifest.json').write_text(json.dumps(manifest, indent=1, sort_keys=True))
    write_private(draw_dir / 'receipts.json', json.dumps(dict(receipts=rcpts, due=due, counts=rcounts, not_inspected_classes={c: len(v) for c, v in ni_classes.items()}), indent=1, default=list))
    ok = sum(1 for m in manifest.values() if m['status'] == 'ok')
    print(f'fetched {len(manifest)} distinct sources once ({ok} ok, {len(manifest) - ok} unavailable); {len(built)} packets; replay classes {rcounts}; not inspected {dict((c, len(v)) for c, v in ni_classes.items())}')
    return 0


def write_new(path, text):
    """Create-exclusive, owner-only: a reader file is never overwritten and never group- or world-readable."""
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        sys.exit(f'refusing: {path.name} already exists (one run per output directory)')
    with os.fdopen(fd, 'w') as f:
        f.write(text)


def run_stage(draw_dir, cache_dir, out, a):
    receipt = json.loads((draw_dir / 'draw_receipt.json').read_text())
    verify_seal(draw_dir, receipt, a.stop_at)
    sample = read_csv(draw_dir / 'sample.csv')
    packets = {json.loads(l)['row']['blind_id']: json.loads(l) for l in open(draw_dir / 'packets.jsonl')}
    skipped = json.loads((draw_dir / 'skipped.json').read_text()) if (draw_dir / 'skipped.json').exists() else {}
    if frame_mode(receipt) and skipped:
        sys.exit('refusing: a frame run cannot skip packets')
    missing = [s['blind_id'] for s in sample if s['blind_id'] not in packets and f"{s['table']}|{s['record_id']}" not in skipped]
    if missing:
        sys.exit(f'refusing: {len(missing)} sealed items have no packet and are not on the fixture skip list')
    sample = [s for s in sample if s['blind_id'] in packets]
    for s in sample:  # each packet must be the sealed row: same blind ID, table, record ID and plant assignment
        row = packets[s['blind_id']]['row']
        if (row.get('blind_id'), row.get('table'), row.get('record_id'), packets[s['blind_id']].get('plant', '')) != (s['blind_id'], s['table'], s['record_id'], s['plant_field']):
            sys.exit(f"refusing: packet {s['blind_id']} is not its sealed row (blind ID, table, record ID or plant field differ)")
        if s['kind'] == 'plant' and not packets[s['blind_id']].get('plant_true'):
            sys.exit(f"refusing: plant packet {s['blind_id']} carries no true value for the witness test")
    manifest = json.loads((cache_dir / 'manifest.json').read_text())
    families = json.loads((draw_dir / 'families.json').read_text())
    rc_doc = json.loads((draw_dir / 'receipts.json').read_text())
    if not isinstance(rc_doc.get('receipts'), dict) or not isinstance(rc_doc.get('due'), dict):
        sys.exit('refusing: receipts.json lacks its receipts or due map')
    for s in sample:  # filing receipts: the packet, the due map and the issued list must agree; a missing receipt is never an empty list
        key = f"{s['table']}|{s['record_id']}"
        want, issued = packets[s['blind_id']].get('due'), len(rc_doc['receipts'].get(key, []))
        if want is None or not want == rc_doc['due'].get(key, 0) == issued:
            sys.exit(f"refusing: {s['blind_id']} expects {want} filing receipts, receipts.json says {rc_doc['due'].get(key, 0)} due and {issued} issued")
    out = Path(out)
    if (out / 'reads').exists():
        sys.exit('refusing: this output directory already holds a run (one run per output directory)')
    out.mkdir(parents=True, exist_ok=True, mode=0o700)
    (out / 'reads').mkdir(mode=0o700)
    ledger_path, procs, lock, stop = out / 'ledger.jsonl', set(), threading.Lock(), threading.Event()
    spent, reserved, n_calls, seq = Counter(), Counter(), Counter(), [0]
    total_cap = (getattr(a, 'max_tokens_m', 0) or 0) * 1e6  # the CLI's total token limit, 0 = none
    caps = {p: m * 1e6 for p, m in (CAPS_M if frame_mode(receipt) else getattr(a, 'caps_m', None) or {}).items()}
    halt = []

    def log(**kw):
        with lock:
            with open(ledger_path, 'a') as f:
                f.write(json.dumps(kw, sort_keys=True) + '\n')
    log(role='run', stop_at=a.stop_at, window=max(1, a.window), caps=caps, total_cap=(getattr(a, 'max_tokens_m', 0) or 0) * 1e6, sample_sha256=receipt['sample_sha256'],  # what score checks the run against
        sample=[dict(pos=int(s['pos']), blind_id=s['blind_id'], kind=s['kind'], provider=s['provider'], plant_field=s['plant_field']) for s in sample])

    def save_read(s, role, provider, round_, attempt, res, prompt, ans, found, error):
        """Every call's raw text, parsed answer, normalised findings, round and provider, in its own file (0600, create-exclusive)."""
        with lock:
            seq[0] += 1
            name = f"{seq[0]:04}-{s['blind_id']}-{role}-r{round_}-a{attempt}.json"
        text = json.dumps(dict(blind_id=s['blind_id'], kind=s['kind'], role=role, provider=provider, round=round_, attempt=attempt, model=res['model'], usage=res['usage'],
                               metered=res['metered'], error=error, prompt_sha256=sha256(prompt.encode()), plant_field=s['plant_field'], raw_text=res['text'],
                               parsed=ans, findings=found), sort_keys=True, indent=1)
        write_new(out / 'reads' / name, text)
        return name, sha256(text.encode())

    def read(provider, s, pk, role, extra=()):
        """One fresh call (plus at most one REQUEST round, for either reader). -> (findings, answer, extra, file) or None when the run must halt:
        any failed, unmetered, wrong-model or empty call halts at once; only an unparseable answer from a healthy call is retried, once."""
        row = pk['row']
        rc = rc_doc['receipts'].get(f"{s['table']}|{s['record_id']}", [])
        ni = pk.get('not_inspected', [])
        plant = dict(field=s['plant_field'], true=pk['plant_true'], names=plant_names(row, s['plant_field'], pk['plant_true']), city=plant_city(row)) if s['kind'] == 'plant' else None
        for round_ in (1, 2):
            sources = build_sources(pk, manifest, cache_dir, extra)
            prompt = build_prompt(row, sources, rc, extra if (round_ == 2 or extra) else (), ni)
            texts = {k: v['full'] for k, v in sources.items()} | {r['id']: r['text'] for r in rc}
            for attempt in (1, 2):
                if stop.is_set():
                    return None
                est = max(len(prompt) // 3, spent[provider] // max(1, n_calls[provider]))  # input tokens of this call: prompt bytes / 3 overstates, else the provider's mean so far
                with lock:
                    projected = provider in caps and spent[provider] + reserved[provider] + est > caps[provider]
                    if projected:
                        halt.append(f'{provider}: {spent[provider] / 1e6:.2f}M spent + {reserved[provider] / 1e6:.2f}M in flight + about {est / 1e6:.2f}M for the next call passes its {caps[provider] / 1e6:.2f}M stage budget: halt for repricing')
                        stop.set()
                    else:
                        reserved[provider] += est
                if projected:
                    log(role='halt', reason='budget: ' + halt[-1])
                    return None
                try:
                    res = call_model(provider, prompt, procs)
                except BaseException:
                    with lock:
                        reserved[provider] -= est
                    raise
                parsed = ans = parse_answer(res['text']) if not res['error'] else None
                found = bad = None
                if ans is not None:
                    try:
                        found = read_findings(ans, texts, targets_of(row, ni), held_values(row), plant)
                    except (TypeError, AttributeError, ValueError, KeyError) as exc:  # typed garbage: the raw call is still kept; retried once like an unparseable answer
                        bad, ans = f'malformed answer: {type(exc).__name__}', None
                error = res['error'] or bad or ('unparseable answer' if ans is None else '')
                with lock:  # settle the reservation and the actual charge together
                    reserved[provider] -= est
                    spent[provider] += input_tokens(res['usage'])
                    n_calls[provider] += 1
                    over = provider in caps and spent[provider] > caps[provider]
                    total_over = bool(total_cap) and sum(spent.values()) > total_cap
                    if over:
                        halt.append(f'{provider}: {spent[provider] / 1e6:.3f}M actual input tokens passed its {caps[provider] / 1e6:.3f}M stage budget: halt for repricing')
                    elif total_over:
                        halt.append(f'total: {sum(spent.values()) / 1e6:.4f}M actual input tokens passed the configured total cap {total_cap / 1e6:.4f}M: halt for repricing')
                    if over or total_over:
                        stop.set()
                        over_msg = halt[-1]
                    over = over or total_over
                fname, fsha = save_read(s, role, provider, round_, attempt, res, prompt, parsed, found, error)
                log(blind_id=s['blind_id'], kind=s['kind'], role=role, provider=provider, round=round_, attempt=attempt, model=res['model'], usage=res['usage'], metered=res['metered'],
                    elapsed=res['elapsed'], prompt_bytes=res['prompt_bytes'], error=error, forced=s['provider'] != provider, file=fname, file_sha256=fsha)
                if over:
                    log(role='halt', reason='budget: ' + over_msg)
                if res['error'] or over:
                    stop.set()  # a failed, unmetered or budget-passing call stops every later call now, not when the ordered collector reaches it
                    if res['error']:
                        return None
                if ans is not None:
                    break
            if ans is None:
                return None
            asks = [f['request_url'] for f in found.values() if f.get('raw') == 'REQUEST' and (f.get('request_url') or '').startswith('http')]
            if round_ == 1 and not extra and asks and len(sources) < FETCH_BUDGET:  # either reader may use the one request round
                extra = list(dict.fromkeys(asks))[:FETCH_BUDGET - len(sources)]
                manifest.update(fetch_urls(cache_dir, extra))
                continue
            return found, ans, extra, fname
        return None

    def other(provider, fams):
        fam = {'astra': 'openai', 'hydrogen': 'google', 'sonnet': 'anthropic'}
        if 'uncertain' in fams and provider == 'astra':  # controller: an uncertain record always gets a Hydrogen second read
            return 'hydrogen', fam['hydrogen'] not in fams
        order = ['hydrogen', 'astra', 'sonnet'] if provider == 'astra' else ['astra', 'sonnet']
        order = [p for p in order if p != provider]
        independent = [p for p in order if fam[p] not in fams]
        return (independent[0], True) if independent else (order[0], False)

    def work(s):
        if stop.is_set():
            return s, dict(status='INCOMPLETE')
        pk = packets[s['blind_id']]
        fams = set(families.get(f"{s['table']}|{s['record_id']}", []))
        first = read(s['provider'], s, pk, 'primary')
        if first is None:
            return s, dict(status='NO_OUTPUT')
        found, ans, extra, pfile = first
        lock_sha = sha256(json.dumps(found, sort_keys=True).encode())
        log(blind_id=s['blind_id'], role='lock', provider=s['provider'], sha256=lock_sha, file=pfile)  # first verdicts are locked before any other family sees the case
        item = dict(status='READ', primary=found, primary_file=pfile, lock=lock_sha, second=None, second_file=None, exception=False,
                    notes=Counter(text_of(n.get('kind')) or 'other' for n in (ans.get('notes') if isinstance(ans.get('notes'), list) else []) if isinstance(n, dict)))
        if s['kind'] == 'real':
            rc = rc_doc['receipts'].get(f"{s['table']}|{s['record_id']}", [])
            need = flagged(found, rc) or 'uncertain' in fams
            coin = s['check_coin'] == '1' and 'uncertain' not in fams
            if need or coin:
                prov, independent = other(s['provider'], fams)
                item.update(second_for='flag' if need else 'check', exception=not independent, second_provider=prov)
                if stop.is_set():
                    return s, dict(item, status='INCOMPLETE')
                sec = read(prov, s, pk, 'second', extra)
                if sec is None:
                    return s, dict(item, status='SECOND_MISSING')
                item['second'], item['second_file'] = sec[0], sec[3]
        return s, item

    board = Board(a.stop_at)
    results, status = [], 'COMPLETE'
    n, window = len(sample), max(1, a.window)
    with ThreadPoolExecutor(window) as pool:
        futs = {}
        for i in range(min(window, n)):  # dispatch is bounded to the unscored window: nothing later starts while an earlier item is open
            futs[i] = pool.submit(work, sample[i])
        try:
            for i, s in enumerate(sample):  # sealed order
                try:
                    _, item = futs[i].result()
                except Exception as exc:  # noqa: BLE001  an unexpected failure is a controlled suspension: results.json is always written
                    item = dict(status='NO_OUTPUT', crash=f'{type(exc).__name__}: {str(exc)[:80]}')
                if item['status'] == 'INCOMPLETE':  # a later failure or budget halt stopped this item: the run is not complete, and says why
                    status = 'HALTED_TOKEN_BUDGET' if halt else 'SUSPENDED_NO_OUTPUT'
                    break
                if item['status'] in ('NO_OUTPUT', 'SECOND_MISSING'):
                    status = 'HALTED_TOKEN_BUDGET' if halt else 'SUSPENDED_NO_OUTPUT'
                    log(blind_id=s['blind_id'], role='halt', reason=item.get('crash') or item['status'])
                    stop.set()
                    break
                ni = packets[s['blind_id']].get('not_inspected', [])
                if s['kind'] == 'plant':
                    ok = plant_detected(item['primary'], s['plant_field'])
                    board.add(int(s['pos']), 'plant', detected=ok, provider=s['provider'])
                    results.append(dict(pos=int(s['pos']), blind_id=s['blind_id'], kind='plant', provider=s['provider'], plant_field=s['plant_field'], detected=ok, table=s['table'], record_id=s['record_id'],
                                        primary_file=item['primary_file'], second_file=None))
                else:
                    final = combine(item['primary'], item['second'], not item['exception'])
                    outcome = record_outcome(final, ni)
                    board.add(int(s['pos']), 'real', outcome)
                    results.append(dict(pos=int(s['pos']), blind_id=s['blind_id'], kind='real', provider=s['provider'], table=s['table'], record_id=s['record_id'], coin=s['check_coin'],
                                        second_provider=item.get('second_provider'), second_for=item.get('second_for'), exception=item['exception'], lock=item['lock'], **outcome,
                                        primary_file=item['primary_file'], second_file=item['second_file'],
                                        primary_status={t: f['status'] for t, f in item['primary'].items()}, second_status={t: f['status'] for t, f in (item['second'] or {}).items()},
                                        note_kinds=dict(item['notes']), withheld=len(packets[s['blind_id']]['masked'])))
                if board.stopped_at or board.invalid:
                    status = 'STOPPED_AT_K' if board.stopped_at else 'SUSPENDED_PLANT_MISSED'
                    stop.set()
                    break
                if total_cap and sum(spent.values()) > total_cap and not any(h.startswith('total') for h in halt):  # backstop: the settle step normally recorded it
                    halt.append(f'total: {sum(spent.values()) / 1e6:.4f}M actual input tokens passed the configured total cap {total_cap / 1e6:.4f}M: halt for repricing')
                    log(role='halt', reason='budget: ' + halt[-1])
                if halt:
                    status = 'HALTED_TOKEN_BUDGET'
                    stop.set()
                    break
                if i + window < n and not stop.is_set():
                    futs[i + window] = pool.submit(work, sample[i + window])
        except Exception as exc:  # noqa: BLE001  scoring a record failed: a controlled suspension, results.json is still written
            status = 'SUSPENDED_NO_OUTPUT'
            log(role='halt', reason=f'crash: {type(exc).__name__}: {str(exc)[:80]}')
            stop.set()
        if status == 'COMPLETE' and (halt or len(results) != n):  # never COMPLETE with an unscored item or a passed budget
            status = 'HALTED_TOKEN_BUDGET' if halt else 'SUSPENDED_NO_OUTPUT'
        if stop.is_set():
            for p in list(procs):
                try:
                    os.killpg(p.pid, 9)
                except OSError:
                    pass
            for f in futs.values():
                f.cancel()
    done = {r['pos'] for r in results}
    incomplete = [dict(pos=int(s['pos']), kind=s['kind']) for s in sample if int(s['pos']) not in done]
    over_budget = sorted(p for p in caps if spent[p] > caps[p])
    summary = dict(status=status, k=board.k, stop_at=a.stop_at, stopped_at=board.stopped_at, invalid=board.invalid, halt=halt, budget_exceeded=over_budget, total_cap_exceeded=bool(total_cap and sum(spent.values()) > total_cap), results=results, incomplete_calls=incomplete,
                   input_tokens_spent=dict(spent), replay_coverage=rc_doc.get('counts', {}), not_inspected_classes=rc_doc.get('not_inspected_classes', {}))
    write_private(out / 'results.json', json.dumps(summary, indent=1, sort_keys=True))
    print(f'run {status}: k={board.k} real={len(board.real)} plants={len(board.plants)} incomplete={len(incomplete)} tokens={dict(spent)}')
    return 0 if status in ('COMPLETE', 'STOPPED_AT_K') and not halt else 1  # a terminal result that crossed its budget still says so


HANDCHECK_FIELDS = ['blind_id', 'quote', 'verdict', 'reviewer', 'time']
HANDCHECK_VERDICTS = ('CAUGHT', 'MISSED', 'INELIGIBLE')


def called_plants(ledger):
    """The plants of the sealed sample that were read at least once: each needs a hand-check record. A plant never called has nothing to check."""
    run = next(l for l in ledger if l.get('role') == 'run')
    called = {l['blind_id'] for l in ledger if l.get('role') in ('primary', 'second')}
    return {x['blind_id']: x for x in run['sample'] if x['kind'] == 'plant' and x['blind_id'] in called}


def handcheck_stage(run_dir, csv_path, now=None):
    """The controller's hand-check of every plant read in this run, sealed into the run folder: handcheck.csv (0600, create-exclusive) with one row per plant
    (blind_id, quote, verdict CAUGHT / MISSED / INELIGIBLE, reviewer, time) and a ledger line carrying its sha256. `score` refuses without it, and refuses
    if the file changed after it was sealed. The script's plant flag is shown beside the verdict; it never decides."""
    run_dir = Path(run_dir)
    ledger = [json.loads(l) for l in open(run_dir / 'ledger.jsonl')]
    plants = called_plants(ledger)
    if (run_dir / 'handcheck.csv').exists() or any(l.get('role') == 'handcheck' for l in ledger):
        sys.exit('refusing: this run already holds a sealed hand-check')
    rows = read_csv(csv_path)
    if not rows or list(rows[0]) != HANDCHECK_FIELDS:
        sys.exit(f'refusing: the hand-check CSV header must be {",".join(HANDCHECK_FIELDS)}')
    seen, stamp = set(), (now or time.strftime('%Y-%m-%dT%H:%M:%S%z'))
    for r in rows:
        if r['blind_id'] not in plants or r['blind_id'] in seen:
            sys.exit(f"refusing: {r['blind_id']!r} is not a plant read in this run, or appears twice")
        if r['verdict'] not in HANDCHECK_VERDICTS or not r['reviewer'].strip() or not r['quote'].strip():
            sys.exit(f"refusing: {r['blind_id']}: verdict must be one of {HANDCHECK_VERDICTS}, with a reviewer and the quote relied on")
        r['time'] = r['time'].strip() or stamp
        seen.add(r['blind_id'])
    if seen != set(plants):
        sys.exit(f'refusing: {len(set(plants) - seen)} plants read in this run have no hand-check row')
    import csv, io
    buf = io.StringIO()
    w = csv.DictWriter(buf, HANDCHECK_FIELDS, lineterminator='\n')
    w.writeheader(), w.writerows(rows)
    text = buf.getvalue()
    write_new(run_dir / 'handcheck.csv', text)
    st = (run_dir / 'handcheck.csv').stat()  # recorded at creation: a replacement with the same bytes has another inode and ctime
    with open(run_dir / 'ledger.jsonl', 'a') as f:
        f.write(json.dumps(dict(role='handcheck', file='handcheck.csv', file_sha256=sha256(text.encode()), n=len(rows), time=stamp, mode=st.st_mode & 0o777, inode=st.st_ino, ctime_ns=st.st_ctime_ns), sort_keys=True) + '\n')
    print(f'sealed {len(rows)} hand-check rows')
    return 0


def handcheck_list(run_dir, draw_dir=None):
    """What the controller needs to hand-check: per plant read, the script flag, what the reader quoted and, with the draw folder, the draw's eligibility quote."""
    run_dir = Path(run_dir)
    ledger = [json.loads(l) for l in open(run_dir / 'ledger.jsonl')]
    elig = {}
    if draw_dir:
        elig = {d['blind_id']: d for d in json.loads((Path(draw_dir) / 'draw_receipt.json').read_text()).get('plants_detail', [])}
    for bid, x in sorted(called_plants(ledger).items()):
        lock = next((l for l in ledger if l.get('role') == 'lock' and l.get('blind_id') == bid), None)  # the locked verdict only, never a pre-REQUEST answer
        f = json.loads((run_dir / 'reads' / lock['file']).read_text()) if lock else None
        got = ((f or {}).get('findings') or {}).get(x['plant_field'], {})
        print(json.dumps(dict(blind_id=bid, provider=x['provider'], field=x['plant_field'], script_flag=plant_detected((f or {}).get('findings') or {}, x['plant_field']),
                              reader=dict(verdict=got.get('raw'), source_value=got.get('source_value'), quote=got.get('quote'), plant_witness=got.get('plant_witness')),
                              draw_eligibility=elig.get(bid, {}).get('eligibility_quote')), ensure_ascii=False))
    return 0


def rederive(run_dir, doc, ledger):
    """Nothing score reports is taken from results.json alone. It rebuilds the run from the ledger and the persisted reader files and refuses (exit 1) on any
    disagreement: (1) the directory holds exactly the files the ledger's call lines name, each with its recorded hash, run, role, round and provider
    (retries, REQUEST rounds and calls on unscored records included); (2) every lock names a primary call file and equals its findings; (3) the scored
    positions are a prefix of the sealed order the run line recorded; (4) plant detection and each record's outcome are recomputed from the files;
    (5) the gate (k, stop position, invalidation) is replayed over a Board; (6) tokens are re-summed from the ledger; (7) the recorded status is the one
    the replay and the budgets imply, and COMPLETE needs every sealed item scored."""
    def fail(msg):
        sys.exit(f'score refuses: {msg}')
    runs = [l for l in ledger if l.get('role') == 'run']
    if len(runs) != 1 or ledger[0].get('role') != 'run':
        fail('the ledger does not open with exactly one run line')
    run = runs[0]
    calls = [l for l in ledger if l.get('role') in ('primary', 'second')]
    names = [l.get('file') for l in calls]
    on_disk = sorted(p.name for p in (run_dir / 'reads').iterdir())
    if sorted(names) != on_disk or len(set(names)) != len(names):
        fail(f'reads/ holds {len(on_disk)} files, the ledger names {len(names)} calls (missing: {sorted(set(names) - set(on_disk))[:3]}, stray: {sorted(set(on_disk) - set(names))[:3]})')
    files = {}
    for l in calls:
        raw = (run_dir / 'reads' / l['file']).read_bytes()
        if sha256(raw) != l.get('file_sha256'):
            fail(f"reader file {l['file']} does not match its ledger hash")
        d = files[l['file']] = json.loads(raw)
        if any(d.get(k) != l.get(k) for k in ('blind_id', 'role', 'provider', 'round', 'attempt', 'model')):
            fail(f"reader file {l['file']} disagrees with its ledger line")
    locks = {l['blind_id']: l for l in ledger if l.get('role') == 'lock'}
    sealed = run['sample']
    results = doc['results']
    if [(r['pos'], r['blind_id'], r['kind'], r['provider']) for r in results] != [(x['pos'], x['blind_id'], x['kind'], x['provider']) for x in sealed[:len(results)]]:
        fail('scored positions are not a prefix of the sealed order')
    board = Board(run['stop_at'])
    for r in results:
        lock = locks.get(r['blind_id'])
        prim = files.get(r.get('primary_file'))
        if not lock or not prim or lock['file'] != r['primary_file'] or prim['role'] != 'primary' or prim['findings'] is None or sha256(json.dumps(prim['findings'], sort_keys=True).encode()) != lock['sha256']:
            fail(f"{r['blind_id']}'s locked primary verdicts do not match its reader file")
        if r['kind'] == 'plant':
            if plant_detected(prim['findings'], r['plant_field']) != r['detected']:
                fail(f"plant {r['blind_id']}: the reader file says detected={not r['detected']}, results.json says {r['detected']}")
            board.add(r['pos'], 'plant', detected=r['detected'], provider=r['provider'])
        else:
            sec = files[r['second_file']]['findings'] if r.get('second_file') else None
            if r.get('second_file') and (files[r['second_file']]['role'] != 'second' or sec is None):
                fail(f"record {r['blind_id']}: its second-read file holds no findings")
            outcome = record_outcome(combine(prim['findings'], sec, not r['exception']), r['not_inspected'])
            bad = [k for k, v in outcome.items() if r.get(k) != v]
            if bad:
                fail(f"record {r['blind_id']}: results.json disagrees with its reader files on {bad}")
            board.add(r['pos'], 'real', outcome)
        if (board.stopped_at or board.invalid) and r is not results[-1]:
            fail('results continue after the stop or invalidation')
    spent = Counter()
    for l in calls:
        spent[l['provider']] += input_tokens(l.get('usage'))
    over = sorted(p for p, cap in run['caps'].items() if spent[p] > cap)
    over_total = bool(run.get('total_cap')) and sum(spent.values()) > run['total_cap']  # the CLI's total limit, reconciled against the aggregate ledger spend
    unscored = [dict(pos=x['pos'], kind=x['kind']) for x in sealed[len(results):]]
    halts = [l for l in ledger if l.get('role') == 'halt']
    budget = bool(over) or over_total or any(str(l.get('reason', '')).startswith('budget') for l in halts)
    if (doc['k'], doc['stopped_at'], doc['invalid'], doc['stop_at']) != (board.k, board.stopped_at, board.invalid, run['stop_at']):
        fail(f"gate totals: results.json says k={doc['k']} stopped_at={doc['stopped_at']} invalid={doc['invalid']}, the reader files give k={board.k} stopped_at={board.stopped_at} invalid={board.invalid}")
    if doc['input_tokens_spent'] != dict(spent) or doc['incomplete_calls'] != unscored:
        fail('input tokens or incomplete items differ from the ledger')
    # One precedence for the terminal reason, in run and here: a missed plant, then the k stop, then a budget halt, then another failure, else complete.
    # A passed budget never changes a gate result's status, but is kept as its own fact (halt list, budget_exceeded) and checked against the ledger.
    if board.invalid:
        expected = 'SUSPENDED_PLANT_MISSED'
    elif board.stopped_at:
        expected = 'STOPPED_AT_K'
    elif budget:
        expected = 'HALTED_TOKEN_BUDGET'
    elif unscored:
        expected = 'SUSPENDED_NO_OUTPUT'
        if not halts and not any(l.get('error') and l['error'] != 'unparseable answer' for l in calls):
            fail('the run stopped early but the ledger holds no failed call and no halt line')
    else:
        expected = 'COMPLETE'
    if doc['status'] != expected:
        fail(f"recorded status {doc['status']} but the ledger and reader files give {expected}")
    if bool(doc['halt']) != budget or doc.get('budget_exceeded') != over or bool(doc.get('total_cap_exceeded')) != over_total:
        fail(f"budget facts differ: halt={bool(doc['halt'])} budget_exceeded={doc.get('budget_exceeded')} total_cap_exceeded={doc.get('total_cap_exceeded')} against the ledger's {budget} / {over} / {over_total}")
    hc = {}
    need = called_plants(ledger)
    marks = [n for n, l in enumerate(ledger) if l.get('role') == 'handcheck']
    if need:
        if len(marks) != 1:
            fail(f'{len(need)} plants were read but the run holds {len(marks)} sealed hand-checks (smoke.py handcheck)')
        mark = ledger[marks[0]]
        path = run_dir / 'handcheck.csv'
        if not path.is_file() or sha256(path.read_bytes()) != mark['file_sha256']:
            fail('handcheck.csv is missing or was altered after it was sealed')
        st = path.stat()
        if (st.st_mode & 0o777) != 0o600:
            fail(f'handcheck.csv is mode {oct(st.st_mode & 0o777)}, not 0600')
        if (st.st_ino, st.st_ctime_ns) != (mark.get('inode'), mark.get('ctime_ns')) or mark.get('mode') != 0o600:
            fail('handcheck.csv was replaced or changed after it was sealed (its inode or ctime differs from the one recorded at creation; score the run folder in place)')
        if any(n > marks[0] for n, l in enumerate(ledger) if l.get('role') == 'lock' and l['blind_id'] in need) or any(n > marks[0] for n, l in enumerate(ledger) if l.get('role') in ('primary', 'second')):
            fail('the hand-check was sealed before the run finished')
        rows = read_csv(path)
        if not rows or list(rows[0]) != HANDCHECK_FIELDS or {r['blind_id'] for r in rows} != set(need) or len(rows) != len(need) or any(r['verdict'] not in HANDCHECK_VERDICTS or not r['reviewer'].strip() or not r['quote'].strip() for r in rows):
            fail('handcheck.csv does not hold exactly one valid row per plant read')
        hc = {r['blind_id']: r for r in rows}
    elif marks:
        fail('a hand-check is sealed for a run that read no plant')
    return len(calls), hc, need


def plant_report(doc, hc, called):
    """Published plant results come only from the controller's hand-check records. The script flag is shown beside them and never decides."""
    flags = {r['blind_id']: r['detected'] for r in doc['results'] if r['kind'] == 'plant'}
    by = defaultdict(lambda: dict(called=0, caught=0, missed=0, ineligible=0))
    pair = Counter()
    for bid, x in called.items():
        v = hc[bid]['verdict']
        row = by[x['provider']]
        row['called'] += 1
        row[{'CAUGHT': 'caught', 'MISSED': 'missed', 'INELIGIBLE': 'ineligible'}[v]] += 1
        pair[f"script_flag_{'detected' if flags.get(bid) else 'missed_or_unscored' if bid not in flags else 'missed'}|hand_check_{v}"] += 1
    return dict(by_provider={p: dict(v) for p, v in sorted(by.items())}, script_flag_vs_hand_check=dict(sorted(pair.items())), source='hand-check records (handcheck.csv)',
                stage_invalid_by_hand_check='a plant was MISSED at the hand-check' if any(r['verdict'] == 'MISSED' for r in hc.values()) else None,
                script_flag_suspended=doc['invalid'], ineligible_plants=sum(1 for r in hc.values() if r['verdict'] == 'INELIGIBLE'))


def score_stage(run_dir):
    doc = json.loads((run_dir / 'results.json').read_text())
    ledger = [json.loads(l) for l in open(run_dir / 'ledger.jsonl')]
    verified_files, hc, called = rederive(run_dir, doc, ledger)
    real = [r for r in doc['results'] if r['kind'] == 'real']
    plants = [r for r in doc['results'] if r['kind'] == 'plant']
    aud, unc, cd, cc, cf, ni, notes = Counter(), Counter(), Counter(), Counter(), Counter(), Counter(), Counter()
    reasons = Counter()
    for r in real:
        for t in r['audited']:
            aud[field_of(t)] += 1
        for t, why in r['unconfirmed'].items():
            unc[field_of(t)] += 1
            reasons[why] += 1
        for t in r.get('not_inspected', []):
            ni[field_of(t)] += 1
        cc.update(r['contradicted_core'])
        cf.update(r['contradicted_core_fields'])  # the actual field of every core-impacting finding, child fields included, so it meets its own denominator
        cd.update(r['contradicted_desc'])
        notes.update(r.get('note_kinds', {}))
    fields = sorted(set(aud) | set(ni))
    by_field = {f: dict(audited_values=aud[f], contradicted=cd[f] + cf[f], error_rate=round((cd[f] + cf[f]) / aud[f], 3) if aud[f] else None,
                        unconfirmed=unc[f], unconfirmed_share=round(unc[f] / aud[f], 3) if aud[f] else None, not_inspected=ni[f]) for f in fields}
    per = defaultdict(lambda: dict(requests=0, failed=0, completed_real=0, completed_control=0, input_tokens=0, tokens_on_failed=0))
    for l in ledger:
        if l.get('role') not in ('primary', 'second'):
            continue
        p = per[l['provider']]
        t = input_tokens(l.get('usage'))
        p['requests'] += 1
        p['input_tokens'] += t
        if l.get('error'):
            p['failed'] += 1
            p['tokens_on_failed'] += t
        else:
            p['completed_real' if l.get('kind') != 'plant' else 'completed_control'] += 1
    cost = {k: dict(v, total_input_m=round(v['input_tokens'] / 1e6, 3),
                    mean_input_per_completed_call=round(v['input_tokens'] / (v['completed_real'] + v['completed_control'])) if v['completed_real'] + v['completed_control'] else None) for k, v in sorted(per.items())}
    n = len(real)
    report = dict(status=doc['status'], audited_real_records=n, k=doc['k'], stop_at=doc['stop_at'], stopped_at_position=doc['stopped_at'], halt=doc.get('halt', []),
                  contradicted_core_fields=dict(cc), by_field=by_field, reader_files_verified=verified_files, budget_exceeded=doc.get('budget_exceeded', []), total_cap_exceeded=bool(doc.get('total_cap_exceeded')),
                  not_inspected_by_field={f: ni[f] for f in sorted(ni)}, not_inspected_filed_classes=doc.get('not_inspected_classes', {}), replay_coverage=doc.get('replay_coverage', {}),
                  unconfirmed_reasons=dict(reasons), omission_and_other_notes=dict(notes), disputed_findings=sum(len(r.get('disputed', [])) for r in real),
                  plants=plant_report(doc, hc, called),
                  routing_exceptions=sum(1 for r in real if r['exception']), second_reads=sum(1 for r in real if r.get('second_provider')),
                  check_only_discoveries=sum(1 for r in real if r.get('second_for') == 'check' and r['k']), incomplete_calls=len(doc['incomplete_calls']),
                  cost_by_provider=cost, cost_per_completed_real_record_input_m=round(sum(v['total_input_m'] for v in cost.values()) / n, 3) if n else None)
    write_private(run_dir / 'score.json', json.dumps(report, indent=1, sort_keys=True))
    print(json.dumps(report, indent=1, sort_keys=True))
    return 0
