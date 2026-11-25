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
sys.path.insert(0, str(ROOT / 'scripts'))  # atlas.street_key
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


def band_write_date(ev):
    """When the band was written (SCHEMA R13's cutoff is that date minus ten years): the date in the evidence note 'backfill of D band', else the date in
    the pass label of `created_by`, else '' (unknown: the band is UNRESOLVED, never dated from the snapshot). Git blame was tried and rejected: the
    2026-11-22 reshard collapsed 2,329 of 2,414 filing rows to one commit date."""
    m = re.search(r'backfill of (\d{4}-\d{2}-\d{2}) band', ev.get('notes', '')) or re.search(r'(\d{4}-\d{2}-\d{2})', ev.get('created_by', ''))
    return m[1] if m else ''


def ten_years_before(date):
    return f'{int(date[:4]) - YEARS_BACK}{date[4:]}'


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
    for r in R.rows('code_assignments'):
        for k in (('organizations', r['org_id']), ('ecosystem', r['org_id'])):
            if k in want and r['code_system'] == 'NAICS' and r['source_type'] == 'government_filing':
                out.append(dict(key=k, cls='naics:code_assignment', field='code_assignments', ev=r))
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


def scan(store, rels, specs):
    """One pass per verified file for several lookups at once (the inspection zip is 1.4 GB). specs: {name: (column name or row function, wanted keys)}.
    -> ({name: {key: [(row, file rel)]}}, problems per file)."""
    specs = {n: sp for n, sp in specs.items() if sp[1]}
    hits, problems = {n: defaultdict(list) for n in specs}, {}
    for rel in rels if specs else ():
        path, why = verified(store, rel)
        if not path:
            problems[rel] = why
            continue
        for r in csv_rows(path):
            for n, (col, wanted) in specs.items():
                v = col(r) if callable(col) else (r.get(col) or '').strip()
                if v in wanted:
                    hits[n][v].append((r, rel))
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
    return dict(status=status, reason=why, text=text, date=date)


REPLAYABLE = {'band:form5500', 'band:osha_ita', 'band:osha_inspection'}  # classes with a replayer: each expected claim of these is owed one receipt
NAICS_FIELDS = {'naics_primary', 'naics_primary_source_type', 'naics_primary_source_name', 'naics_confidence'}


def band_receipt(site, orgs, ev, ita, ita_hits, insp_hits, ita_problems, insp_problems, store, cutoff, held_band=None, others=()):
    """Locate the cited filing row, check it binds, then let the newest binding filing inside the cutoff decide (SCHEMA R13 precedence):
    an older different band under a newer supporting one is a match; a newer different band contradicts. `others` are the other filing rows (ITA and
    inspections) found at the same street, so a newer inspection can supersede an older ITA filing and the reverse; they bind or not like any row."""
    held = held_band or site['employee_band_site']
    ref = ev['source_ref'] + ' ' + ev['claim_detail']
    m = re.search(r'establishment_?id[ =:]*(\d+)' if ita else r'(?:id=|OSHA inspection )(\d{6,})', ref, re.I)
    hits = list((ita_hits if ita else insp_hits).get(m[1], [])) if m else []
    problems = ita_problems if ita else insp_problems
    loc = re.search(r'(raw/\S+?\.csv)@(\d+)', ev['source_ref'])
    if not m and loc:
        found, why = locator_row(store, loc[1], int(loc[2]))
        hits, problems = ([found] if found else []), ({loc[1]: why} if why else {})
    kind = 'osha_ita' if ita else 'osha_inspection'
    if not hits:
        why = next(iter(problems.values()), 'filing_row_not_found_in_store')
        return dict(status='UNRESOLVED', reason=why, text=f'The cited filing row was not located in the sealed store ({why}).')
    year = re.search(r'CY\s?(\d{4})|\b(20[12]\d)\b', ev['source_ref'])
    cited = [h for h in hits if year and str(h[0].get('year_filing_for', '')).split('.')[0] == (year[1] or year[2])] if ita and not loc else hits
    if len(cited) != 1:
        return dict(status='UNRESOLVED', reason='cited_row_not_identified', text='The cited filing year does not single out one row for this establishment ID.')
    cited_r = receipt(site, orgs, cited[0][0], kind, cited[0][1], cutoff, held)
    if cited_r['status'] not in ('MATCHES', 'CONTRADICTS') and cited_r['reason'] != 'stale_over_10_years':
        return cited_r
    binding = [r for r in [receipt(site, orgs, h[0], kind, h[1], cutoff, held) for h in hits] + [receipt(site, orgs, row, k2, rel, cutoff, held) for k2, row, rel in others]
               if r['status'] in ('MATCHES', 'CONTRADICTS')]
    if not binding:
        return cited_r
    newest = max(binding, key=lambda r: r['date'])
    return dict(newest, text=f"Cited row dated {cited_r['date']}. Newest binding filing: " + newest['text'])


def civic_key(addr):
    m = re.match(r'\s*(\d+)', addr or '')
    return m[1] if m else ''


def band_target(x, sites, orgs, org_sites):
    """-> (site row, held band, reason). A site-grain band is judged at its site. An organization-grain band is judged at the organization's only site, and
    only when it has exactly one site and that site is in Ohio (the PPP rule's single-site, Ohio-only test: a choice the protocol does not state)."""
    k = x['key']
    if k[0] == 'sites':
        site = sites.get(k[1])
        return (site, site[x['field']], '') if site else (None, None, 'site_row_not_found')
    only = org_sites.get(k[1], [])
    if len(only) == 1 and only[0]['state'] == 'OH':
        return only[0], orgs[k[1]][x['field']], ''
    return None, None, 'org_grain_not_single_site'


def coverage(R, keys, store=STORE):
    """-> (receipts {'table|id': [receipt]}, not_inspected classes {class: [keys]}, counts {class: {status: n}}, ni {'table|id': {fields, children}},
    due {'table|id': receipts the record must be issued}).
    A class with no replayer is NOT_INSPECTED (owner ruling 2026-11-24 15:15): counted, never a receipt, never unconfirmed."""
    from atlas import street_key
    exp = expected(R, keys)
    sites = {r['site_id']: r for r in R.rows('sites')}
    org_sites = defaultdict(list)
    for r in sites.values():
        org_sites[r['org_id']].append(r)
    orgs = {r['org_id']: r for t in ('organizations', 'ecosystem') for r in R.rows(t)}
    bands = [x for x in exp if x['cls'] in ('band:osha_ita', 'band:osha_inspection')]
    target = {id(x): band_target(x, sites, orgs, org_sites) for x in bands}
    ita_ids = {m[1] for x in bands if x['cls'] == 'band:osha_ita' and (m := re.search(r'establishment_?id[ =:]*(\d+)', x['ev']['source_ref'], re.I))}
    insp_ids = {m[1] for x in bands if x['cls'] == 'band:osha_inspection' and (m := re.search(r'(?:id=|OSHA inspection )(\d{6,})', x['ev']['source_ref'] + ' ' + x['ev']['claim_detail']))}
    streets = {street_key(t[0]['street_address']) for t in target.values() if t[0] and civic_key(t[0]['street_address'])}  # every other filing at a replayed band's street can supersede the cited one; a street with no number matches nothing
    civics = {civic_key(st) for st in streets}
    street_of = lambda col: (lambda r: (street_key(r.get(col, '')) if civic_key(r.get(col, '')) in civics else ''))
    ita, ita_problems = scan(store, ita_files(store), dict(id=('establishment_id', ita_ids), street=(street_of('street_address'), streets)))
    insp, insp_problems = scan(store, inspection_files(store), dict(id=('activity_nr', insp_ids), street=(street_of('site_address'), streets)))
    ita_hits, ita_by_street, insp_hits, insp_by_street = ita.get('id', {}), ita.get('street', {}), insp.get('id', {}), insp.get('street', {})
    scan_problems = {**ita_problems, **insp_problems}
    receipts, ni_classes, counts, ni = defaultdict(list), defaultdict(list), defaultdict(Counter), defaultdict(lambda: dict(fields=set(), children=[]))
    for x in exp:
        cls, k, ev = x['cls'], x['key'], x['ev']
        rid = f'R{len(receipts[f"{k[0]}|{k[1]}"]) + 1}'
        out = None
        if cls == 'band:form5500':
            out = dict(status='LEAD_ONLY', reason='plan_participants_cannot_establish_a_headcount', text='Form 5500 plan-year participant count: a lead only; it cannot establish an employee band.')
        elif cls in ('band:osha_ita', 'band:osha_inspection'):
            site, held, why = target[id(x)]
            written = band_write_date(ev)
            if site is None:
                out = dict(status='UNRESOLVED', reason=why, text='This band is held at the organization and cannot be tied to one establishment (it needs exactly one Ohio site); a single establishment filing cannot settle it.' if why == 'org_grain_not_single_site' else 'The band\'s site row was not found.')
            elif not written:
                out = dict(status='UNRESOLVED', reason='band_write_date_unknown', text='The date this band was written is not recorded, so the ten-year filing cutoff cannot be applied.')
            elif scan_problems:
                out = dict(status='UNRESOLVED', reason='filing_scan_incomplete', text=f'Other filings at this street could not all be searched ({next(iter(scan_problems.values()))}).')
            else:
                sk = street_key(site['street_address']) if civic_key(site['street_address']) else None  # no street number: no other filing can be bound by street
                others = [('osha_ita', r, rel) for r, rel in ita_by_street.get(sk, [])] + [('osha_inspection', r, rel) for r, rel in insp_by_street.get(sk, [])]
                out = band_receipt(site, orgs, ev, cls == 'band:osha_ita', ita_hits, insp_hits, ita_problems, insp_problems, store, ten_years_before(written), held, others)
        if out is None:  # no replayer for this class: reported as not inspected, never as a receipt and never as unconfirmed
            ni_classes[cls].append(k)
            counts[cls]['not_inspected'] += 1
            key = f'{k[0]}|{k[1]}'
            if cls.startswith('registry:'):  # only the filed child is not inspected, matched on its own identifying values
                ni[key]['children'].append(dict(table='registry_links', match=dict(registry=ev['registry'], registry_id=ev['registry_id'])))
            elif cls == 'naics:code_assignment':
                ni[key]['children'].append(dict(table='code_assignments', match=dict(code_system='NAICS', source_type='government_filing', code_value=ev['code_value'])))
            elif cls.startswith('naics'):
                ni[key]['fields'].update(NAICS_FIELDS)
            else:
                ni[key]['fields'].add(x['field'])
            continue
        receipts[f'{k[0]}|{k[1]}'].append(dict(out, id=rid, cls=cls, field=x['field']))
        counts[cls][out['status']] += 1
    ni = {k: dict(fields=sorted(v['fields']), children=v['children']) for k, v in ni.items()}
    due = Counter(f'{x["key"][0]}|{x["key"][1]}' for x in exp if x['cls'] in REPLAYABLE)  # counted from expected() alone, not from the loop above
    return dict(receipts), dict(ni_classes), {c: dict(v) for c, v in sorted(counts.items())}, ni, dict(due)
