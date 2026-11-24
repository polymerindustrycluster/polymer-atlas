"""Filing replay receipts for the audit 13 smoke: one receipt per populated filing-backed band, filing NAICS and registry ID.

Follows tasks/pic18-size-10yr-2026-11-23/check.py's pattern (replay from the sealed raw snapshot in the shared store, store checksum
verified, the original filing row located, operator and street bound to the establishment, filing age applied) and reuses the size
sprint's matcher (held_names, name_class, street, city) rather than a new one.

Outcomes are kept apart on purpose:
  * a replayer RAN and could not settle (file missing, row absent, not bound, stale): an UNRESOLVED receipt; the reader sees it.
  * NO replayer exists for the class: nothing is issued and the class BLOCKS preflight, counted. It is never an UNRESOLVED receipt.
Built now: size bands from OSHA ITA and OSHA inspection filings; Form 5500 plan bands as LEAD_ONLY (plan participants cannot establish a headcount).
Not built (they block): PPP-URL bands, other band sources, filing NAICS, every registry ID.
"""
import csv, hashlib, importlib.util, io, re, sys, zipfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STORE = Path('/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store')
OSHA = 'raw/osha/2026-11-22-archive-snapshot/raw'
YEARS_BACK = 10  # SCHEMA R13 (owner ruling 2026-11-23): a band written on date D accepts filings dated on or after D minus ten years
csv.field_size_limit(10**9)
_M = None


def sprint():
    global _M
    if _M is None:
        sys.path.insert(0, str(ROOT / 'scripts'))
        spec = importlib.util.spec_from_file_location('size_sprint', ROOT / 'tasks/pic18-size-sprint-2026-11-22/build.py')
        _M = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_M)
    return _M


def band_kind(ev):
    ref = ev['source_ref']
    if 'sba.gov' in ref or 'PPP' in ref:
        return 'ppp'
    if '5500' in ref:
        return 'form5500'
    if re.search(r'inspection_detail\?id=\d+', ref) or 'OSHA inspection' in ref:
        return 'osha_inspection'
    if re.search(r'establishment_?id', ref, re.I) or ('raw/' in ref and 'ita' in ref.lower()):
        return 'osha_ita'
    return 'other'


def expected(R, keys):
    """-> list of dict(key, cls, field, ev). Every populated filing-backed band, filing NAICS and registry ID of the sampled records."""
    want = set(keys)
    rows = {t: {r[{'sites': 'site_id'}.get(t, 'org_id')]: r for r in R.rows(t)} for t in ('sites', 'organizations', 'ecosystem')}
    band_field = {'sites': 'employee_band_site', 'organizations': 'employee_band_ohio'}
    out = []
    for ev in R.rows('evidence'):
        k = (ev['record_table'], ev['record_id'])
        if k in want and ev['claim_type'] == 'size_band' and ev['source_class'] == 'government_filing':
            rec = rows[k[0]].get(k[1], {})
            if rec.get(band_field.get(k[0], ''), '') not in ('', 'unknown'):
                out.append(dict(key=k, cls='band:' + band_kind(ev), field=band_field[k[0]], ev=ev))
    for k in want:
        rec = rows[k[0]].get(k[1], {})
        if rec.get('naics_primary') and rec.get('naics_primary_source_type') == 'government_filing':
            out.append(dict(key=k, cls='naics:government_filing', field='naics_primary', ev=None))
    for r in R.rows('registry_links'):
        for k in ((('organizations', r['org_id']), ('ecosystem', r['org_id'])) if r['org_id'] else ()) + ((('sites', r['site_id']),) if r['site_id'] else ()):
            if k in want:
                out.append(dict(key=k, cls='registry:' + r['registry'], field='registry_id', ev=r))
    return out


def file_hash(path, cache={}):
    if path not in cache:
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(1 << 22), b''):
                h.update(chunk)
        cache[path] = h.hexdigest()
    return cache[path]


def verified(store, rel):
    """The store file, only if its sha256 equals the checksum sidecar written when it was archived."""
    path = store / rel
    side = Path(str(path) + '.sha256')
    if not path.is_file() or not side.is_file():
        return None, 'source_file_not_in_store'
    if file_hash(path) != side.read_text().split()[0]:
        return None, 'store_checksum_mismatch'
    return path, ''


def csv_rows(path, member=None):
    if path.suffix == '.zip':
        with zipfile.ZipFile(path) as z:
            for name in ([member] if member else [n for n in z.namelist() if n.endswith('.csv')]):
                with z.open(name) as f:
                    yield from (dict((k.lower().lstrip('﻿'), v) for k, v in r.items()) for r in csv.DictReader(io.TextIOWrapper(f, 'utf-8-sig', errors='replace', newline='')))
    else:
        with open(path, newline='', encoding='utf-8-sig', errors='replace') as f:
            yield from (dict((k.lower(), v) for k, v in r.items()) for r in csv.DictReader(f))


def scan(store, rels, id_col, wanted):
    """One pass per verified file: rows whose id_col is in wanted. -> (hits {id: [row, file rel]}, problems per file)."""
    hits, problems = defaultdict(list), {}
    for rel in rels:
        path, why = verified(store, rel)
        if not path:
            problems[rel] = why
            continue
        for r in csv_rows(path):
            v = (r.get(id_col) or '').strip()
            if v in wanted:
                hits[v].append((r, rel))
    return hits, problems


def locator_row(store, rel, n):
    """Row n (1-based, header excluded) of a verified raw CSV, the `file@n` locator the size sprints wrote."""
    path, why = verified(store, rel)
    if not path:
        return None, why
    for i, r in enumerate(csv_rows(path), 1):
        if i == n:
            return (r, rel), ''
    return None, 'locator_row_beyond_file'


def ita_files(store):
    d = store / OSHA / 'ita'
    return sorted(str(p.relative_to(store)) for p in d.glob('*') if p.suffix in ('.zip', '.csv') and 'dictionary' not in p.name)


def inspection_files(store):
    return [str((store / OSHA / 'OSHA_inspection.zip').relative_to(store))]


def receipt(site, orgs, row, kind, rel, cutoff, held_band):
    """One filing row against the sampled record: operator, street and city bound, age, band. Only public filing values go in the text."""
    M = sprint()
    e = M.unify([row], 'ita' if kind == 'osha_ita' else 'insp')[0]
    if kind == 'osha_ita':
        e['names'] = [row['establishment_name']]
    held = M.held_names(site, orgs)
    cls, _ = M.name_class(held, e['names'])
    bound = M.RANK[cls] >= M.LEVELS['suffix'] and M.same_street(site['street_address'], e['st']) and M.city_ok(site, e['city'], e['zip'])
    date, count = M.source_date(e), M.count_of(e)
    band = M.band_of(count) if count else ''
    text = (f"{'OSHA ITA Form 300A' if kind == 'osha_ita' else 'OSHA inspection'} row in {Path(rel).name}: establishment {e['names'][0]!r}, street {e['st']!r}, "
            f"{e['city']}, {e['zip']}; dated {date}; employees {count} -> band {band or 'none'}. Held band {held_band}. "
            f"Operator and street {'BIND to this record' if bound else 'do NOT bind to this record'}; filing is {'on or after' if date >= cutoff else 'BEFORE'} the {cutoff} cutoff.")
    if not bound:
        status, why = 'UNRESOLVED', 'filing_does_not_bind_operator_and_street'
    elif date < cutoff:
        status, why = 'UNRESOLVED', 'stale_over_10_years'
    elif not band:
        status, why = 'UNRESOLVED', 'filing_has_no_count'
    else:
        status, why = ('MATCHES', 'band_equal') if band == held_band else ('CONTRADICTS', 'band_differs_same_establishment_within_cutoff')
    return dict(status=status, reason=why, text=text)


def coverage(R, keys, store=STORE):
    """-> (receipts {'table|id': [receipt]}, blocks {reason: [keys]}, counts {class: {status: n}})."""
    exp = expected(R, keys)
    cutoff = f"{int(R.git('show', '-s', '--format=%cs', R.at).strip()[:4]) - YEARS_BACK}{R.git('show', '-s', '--format=%cs', R.at).strip()[4:]}"
    sites = {r['site_id']: r for r in R.rows('sites')}
    orgs = {r['org_id']: r for t in ('organizations', 'ecosystem') for r in R.rows(t)}
    ita_ids = {m[1] for x in exp if x['cls'] == 'band:osha_ita' and (m := re.search(r'establishment_?id[ =:]*(\d+)', x['ev']['source_ref'], re.I))}
    insp_ids = {m[1] for x in exp if x['cls'] == 'band:osha_inspection' and (m := re.search(r'(?:id=|OSHA inspection )(\d{6,})', x['ev']['source_ref'] + ' ' + x['ev']['claim_detail']))}
    ita_hits, ita_problems = scan(store, ita_files(store), 'establishment_id', ita_ids) if ita_ids else ({}, {})
    insp_hits, insp_problems = scan(store, inspection_files(store), 'activity_nr', insp_ids) if insp_ids else ({}, {})
    receipts, blocks, counts = defaultdict(list), defaultdict(list), defaultdict(Counter)
    for x in exp:
        cls, k, ev = x['cls'], x['key'], x['ev']
        rid = f'R{len(receipts[f"{k[0]}|{k[1]}"]) + 1}'
        out = None
        if cls == 'band:form5500':
            out = dict(status='LEAD_ONLY', reason='plan_participants_cannot_establish_a_headcount', text='Form 5500 plan-year participant count: a lead only; it cannot establish an employee band.')
        elif cls in ('band:osha_ita', 'band:osha_inspection'):
            site = sites.get(k[1]) if k[0] == 'sites' else None
            if site is None:
                out = dict(status='UNRESOLVED', reason='org_grain_band_not_replayable', text='This band is held at the organization; a single establishment filing cannot settle it.')
            else:
                ita = cls == 'band:osha_ita'
                m = re.search(r'establishment_?id[ =:]*(\d+)' if ita else r'(?:id=|OSHA inspection )(\d{6,})', ev['source_ref'] + ' ' + ev['claim_detail'], re.I)
                hits = (ita_hits if ita else insp_hits).get(m[1], []) if m else []
                problems = ita_problems if ita else insp_problems
                loc = re.search(r'(raw/\S+?\.csv)@(\d+)', ev['source_ref'])
                if not m and loc:
                    found, why = locator_row(store, loc[1], int(loc[2]))
                    hits, problems = ([found] if found else []), ({loc[1]: why} if why else {})
                if not hits:
                    why = next(iter(problems.values()), 'filing_row_not_found_in_store') if problems and not hits else 'filing_row_not_found_in_store'
                    out = dict(status='UNRESOLVED', reason=why, text=f'The cited filing row was not located in the sealed store ({why}).')
                else:
                    best = max(hits, key=lambda h: h[0].get('year_filing_for') or h[0].get('open_date') or '')
                    out = receipt(site, orgs, best[0], 'osha_ita' if ita else 'osha_inspection', best[1], cutoff, site['employee_band_site'])
        if out is None:  # no replayer for this class: block, never an UNRESOLVED receipt
            blocks[cls].append(k)
            counts[cls]['no_replayer'] += 1
            continue
        receipts[f'{k[0]}|{k[1]}'].append(dict(out, id=rid, cls=cls, field=x['field']))
        counts[cls][out['status']] += 1
    return dict(receipts), {'no_replayer:' + c: v for c, v in blocks.items()}, {c: dict(v) for c, v in sorted(counts.items())}
