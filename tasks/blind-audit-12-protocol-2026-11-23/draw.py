#!/usr/bin/env python3
"""Blind audit 12: frames, sealed deterministic stratified draw, defect plants. Stdlib only. PROTOCOL.md says what each step means.

    python3 draw.py frame --at <origin/main SHA>                                  frame counts + reconciliation; no seed, no draw
    python3 draw.py draw  --seed-file <path> --at <origin/main SHA> --out <DIR>   THE draw (once); refuses a seed file whose sha256 differs
    python3 draw.py fields-md                                                     the field-class table PROTOCOL.md embeds
    python3 draw.py --selftest                                                    synthetic fixtures only; no real people rows, no real seed

Draw is read-only on the repository: data comes from `git show <SHA>:`, never the working tree. The seed is never printed or written.
"""
import csv, hashlib, importlib.util, io, json, random, re, subprocess, sys, tempfile
from collections import Counter, defaultdict
from pathlib import Path

H = Path(__file__).resolve().parent
ROOT = H.parents[1]
sys.path.insert(0, str(H))
import sizes  # noqa: E402  (PLAN, the per-stratum sizes; one definition)

SEED_SHA256 = '5144840e29ac8aad7204812bf272282ffe0e39a2ce6bb6ba795d4d35f68d3df3'  # the controller's sealed seed; there is deliberately no override
STRATA = list(sizes.PLAN)
PLANT_POOL = 40  # records ranked just past n2 that may be turned into plants
TIERS_PUBLISHED = ('A', 'B', 'C')  # U is "not counted in headline totals" on the site (build_site TIERS); named exclusion, never silent

# ---- field classes (PROTOCOL.md section 2). Every column of every table below must be classified exactly once; draw.py fails otherwise.
#  J judged by readers | K shown as context, not judged | B judged by binding replay, withheld from readers | W withheld from readers, not judged | D derived or generated, recomputed by the integrator
#  R reference data (AGENTS section 1), not read | M machine-checked by the validator or binding gate, not read
FIELD_CLASS = {
    'organizations': {
        'K': 'org_id sources',
        'J': ('legal_name trade_names parent_org_id ultimate_parent_name entity_type ring_primary ring_secondary diversified_conglomerate hq_city hq_state hq_county hq_country '
              'hq_in_scope naics_primary naics_primary_source_type naics_primary_source_name naics_confidence naics_secondary processes materials markets_served employee_band_ohio '
              'website description_1line status status_date successor_org_id verification_tier year_founded stock_ticker ownership_type certifications pic_member member_since '
              'membership_source_url newsroom_url newsroom_feed_url linkedin_url'),
        'W': 'pic_relevance last_verified created_by notes last_activity_evidence_date liveness_signal monitor_watch',
        'D': 'tier1_qualifier tier1_qualifier_basis'},
    'sites': {
        'K': 'site_id org_id sources',
        'J': ('site_name site_type city state zip county ring_primary naics_primary naics_primary_source_type naics_confidence processes processes_other_note materials materials_other_note '
              'markets_served employee_band_site operating_status verification_tier street_address country site_group_id'),
        'W': 'last_verified created_by notes county_source',
        'D': 'last_activity_date last_activity_source',
        'R': 'latitude longitude geocode_precision'},
    'ecosystem': {
        'K': 'org_id sources',
        'J': ('legal_name ecosystem_subtype generalist services_offered geography_served city state county website description_1line status verification_tier record_grain '
              'parent_institution_org_id public_door_url office_name tto_url industry_partnership_modes technology_areas pic_member member_since membership_source_url ipeds_unitid ror_id'),
        'W': 'pic_relevance last_verified created_by notes',
        'D': 'polymer_program polymer_program_name polymer_program_url'},
    'people': {
        'K': 'person_id sources',
        'J': 'full_name institution_org_id program_org_id role role_as_published research_specialties public_profile_url lab_url verification_tier status status_date',
        'W': 'last_verified'},
    'programs': {
        'K': 'program_id institution_org_id sources',
        'J': ('program_name program_type credential_types level cip_code cip_source_type unit_department description_1line url public_door_url first_year_awarded last_year_awarded '
              'latest_completions completions_year specialty_processes specialty_materials research_areas engagement_modes apprenticeship_registered employer_custom_training '
              'admissions_status facilities_note scale_band geography_served city state county status verification_tier'),
        'W': 'last_verified pic_relevance created_by notes'},
    'events': {
        'K': 'event_id sources status_source',
        'J': ('name trade_names organizer_name organizer_org_id event_format cadence cadence_note typical_timing home_city home_state home_region geography_note subject_scope '
              'subject_note event_url status status_date verification_tier pic_events_slug'),
        'W': 'last_verified pic_relevance created_by notes'},
    'event_participation': {
        'K': 'participation_id sources',
        'J': ('event_id org_id edition_year edition_name role role_detail edition_dates edition_city edition_state evidence_source_name evidence_source_url verification_tier'),
        'W': 'evidence_date last_verified created_by notes'},
    # child rows: judged with the record they hang from (PROTOCOL.md section 2.4)
    'evidence': {
        'K': 'evidence_id record_table record_id claim_type source_ref', 'B': 'claim_detail source_class address_role',
        'M': 'tier_effect', 'W': 'observed_date created_by notes'},
    'registry_links': {'K': 'org_id site_id match_basis', 'J': 'registry registry_id', 'W': 'as_of'},
    'site_capabilities': {'K': 'capability_id site_id org_id source_ref', 'J': 'capability_type term provenance', 'W': 'observed_date withdrawn_date created_by notes'},
    'equipment': {'K': 'equipment_id host_org_id site_id program_id source_ref', 'J': 'name equipment_class access_mode', 'W': 'observed_date withdrawn_date created_by notes'},
    'people_identifiers': {'K': 'person_id identifier_type match_basis', 'J': 'identifier_id', 'W': 'as_of'},
    'people_engagement': {'K': 'engagement_id person_id source_ref', 'J': 'mode', 'W': 'observed_date withdrawn_date created_by notes'},
    'archive_links': {'K': 'evidence_id', 'J': 'archive_ref captured_at', 'W': 'created_by'},
    'members': {'K': 'member_row_id org_id', 'J': 'display_name member_tier record_class member_since membership_source_url snapshot_date', 'W': 'notes'},
    'relationships': {'K': 'relationship_id from_org_id to_org_id', 'M': 'relationship_type effective_from effective_to basis source_ref', 'W': 'created_by notes'},
}
FIELD_CLASS = {t: {c: k for k, cols in d.items() for c in cols.split()} for t, d in FIELD_CLASS.items()}
CLASS_NAME = dict(J='judged by readers', K='context, not judged', B='judged by binding replay (integrator)', W='withheld, not judged', D='derived/generated, recomputed', R='reference, not read', M='machine-checked')
TABLE_FILE = {  # table -> data/ path regex (shards are read as one table)
    'organizations': r'data/organizations_[A-Z0-9]+\.csv', 'sites': r'data/sites_[A-Z0-9]+\.csv', 'evidence': r'data/evidence_[a-z]+(?:_[A-Z0-9]+)?\.csv',
    **{t: rf'data/{t}\.csv' for t in FIELD_CLASS if t not in ('organizations', 'sites', 'evidence')}}
ID_COL = dict(organizations='org_id', ecosystem='org_id', sites='site_id', people='person_id', programs='program_id', events='event_id', event_participation='participation_id')


def fields_md():
    rows = ['| table | ' + ' | '.join(f'`{k}` {CLASS_NAME[k]}' for k in 'JKBWDRM') + ' |', '|---|' + '---|' * 7]
    for t, cols in FIELD_CLASS.items():
        by = defaultdict(list)
        for c, k in cols.items():
            by[k].append(c)
        rows.append(f'| `{t}` | ' + ' | '.join(' '.join(f'`{c}`' for c in by[k]) or '—' for k in 'JKBWDRM') + ' |')
    return '\n'.join(rows)


# ---- readers: the only place data enters. Real = git show at a pinned SHA; the selftest swaps in an in-memory reader.
class GitReader:
    def __init__(self, at, root=ROOT):
        self.at, self.root = at, root
        self.files = self.git('ls-tree', '-r', '--name-only', at, 'data/').splitlines()
        self.pic18 = None

    def git(self, *a):
        return subprocess.check_output(['git', *a], cwd=self.root).decode('utf-8')

    def paths(self, table):
        return [p for p in self.files if re.fullmatch(TABLE_FILE[table], p)]

    def rows(self, table):
        out = []
        for p in self.paths(table):
            out += list(csv.DictReader(io.StringIO(self.git('show', f'{self.at}:{p}'), newline='')))
        return out

    def header(self, table):
        hs = {tuple(next(csv.reader(io.StringIO(self.git('show', f'{self.at}:{p}'), newline='')))) for p in self.paths(table)}
        assert len(hs) == 1, f'{table}: shard headers differ'
        return list(hs.pop())

    def regions(self):
        ns = {}
        exec(self.git('show', f'{self.at}:scripts/regions.py'), ns)  # the one county definition at the pinned SHA (AGENTS section 8)
        return set(ns['PIC18'])

    def published_site_counts(self, sites):
        """Run the site builder's own active_ab / pic18_active_sites (scripts/build_site.py at the pinned SHA) on these rows."""
        with tempfile.TemporaryDirectory() as td:
            tar = subprocess.run(['git', 'archive', self.at, 'scripts'], cwd=self.root, check=True, capture_output=True).stdout
            subprocess.run(['tar', '-x', '-C', td], input=tar, check=True)
            sys.path.insert(0, f'{td}/scripts')
            try:
                spec = importlib.util.spec_from_file_location('build_site_at_sha', f'{td}/scripts/build_site.py')
                bs = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(bs)
                return dict(active_ab=len(bs.active_ab(sites)), pic18=len(bs.pic18_active_sites(sites)),
                            ohio=len(bs.active_ab([s for s in sites if s.get('state') == 'OH'])))
            finally:
                sys.path.remove(f'{td}/scripts')


class Unassignable(Exception):
    """A record that cannot be placed in exactly one stratum. The draw refuses rather than guess (fail closed)."""


# ---- frame
def build_frame(R, pic18, check_published=True):
    """-> (frame rows, reconciliation dict, unassignable list). Asserts everything AGENTS section 2 rule 10 asks for."""
    T = {t: R.rows(t) for t in ('organizations', 'ecosystem', 'sites', 'people', 'programs', 'events', 'event_participation')}
    for t in FIELD_CLASS:  # every column classified exactly once, none unclassified, none missing: a new column cannot slip past the audit
        h = R.header(t)
        assert len(h) == len(set(h)) and set(h) == set(FIELD_CLASS[t]), (t, sorted(set(h) ^ set(FIELD_CLASS[t])))
    for t, idc in ID_COL.items():  # 10b: record-ID uniqueness, in every table and across the two org tables
        ids = [r[idc] for r in T[t]]
        assert all(ids) and len(ids) == len(set(ids)), f'{t}: blank or duplicate {idc}'
    assert not {r['org_id'] for r in T['organizations']} & {r['org_id'] for r in T['ecosystem']}, 'org_id in both organizations and ecosystem'
    orgs = {r['org_id'] for t in ('organizations', 'ecosystem') for r in T[t]}
    assert all(s['org_id'] in orgs for s in T['sites']), 'site with no owner record'
    assert all(p['event_id'] in {e['event_id'] for e in T['events']} and p['org_id'] in orgs for p in T['event_participation']), 'participation row with a dangling FK'
    ok = lambda r, st: r[st] == 'active' and r['verification_tier'] in TIERS_PUBLISHED
    inc, excl = {}, defaultdict(Counter)  # table -> {id: basis}; table -> reason counts
    for t, st in (('sites', 'operating_status'), ('organizations', 'status'), ('ecosystem', 'status'), ('programs', 'status'), ('events', 'status')):
        for r in T[t]:
            if t == 'programs':
                keep = r['status'] == 'active' and r['verification_tier'] in TIERS_PUBLISHED
            else:
                keep = ok(r, st)
            if keep:
                inc.setdefault(t, {})[r[ID_COL[t]]] = 'published_headline'
            else:
                excl[t][f"status={r[st] or '(blank)'}; tier={r['verification_tier'] or '(blank)'}"] += 1
    for r in T['people']:
        if r['status'] in ('', 'active') and r['verification_tier'] in TIERS_PUBLISHED:
            inc.setdefault('people', {})[r['person_id']] = 'published_headline'
        else:
            excl['people'][f"status={r['status'] or '(blank)'}; tier={r['verification_tier']}"] += 1
    ev_in = inc.get('events', {})
    for r in T['event_participation']:
        if r['event_id'] in ev_in and r['verification_tier'] in TIERS_PUBLISHED:
            inc.setdefault('event_participation', {})[r['participation_id']] = 'published_headline'
        else:
            excl['event_participation'][f"event_in_frame={r['event_id'] in ev_in}; tier={r['verification_tier']}"] += 1
    # owners of a frame site are in the frame even when their own record is not active A-C (the outcome frame of 794 includes them; PROTOCOL.md B2)
    owner_sites = defaultdict(list)
    sites_by_id = {s['site_id']: s for s in T['sites']}
    for sid in inc.get('sites', {}):
        owner_sites[sites_by_id[sid]['org_id']].append(sites_by_id[sid])
    added = Counter()
    for t in ('organizations', 'ecosystem'):
        for r in T[t]:
            if r['org_id'] in owner_sites and r['org_id'] not in inc.get(t, {}):
                inc.setdefault(t, {})[r['org_id']] = 'owner_of_frame_site'
                added[t] += 1
    # region, fail closed
    def site_region(s):
        if s['country'] not in ('', 'US'):
            return 'REST'
        if not s['state']:
            raise Unassignable('blank state')
        if s['state'] != 'OH':
            return 'REST'
        if not s['county']:
            raise Unassignable('Ohio site with blank county')
        return 'PIC18' if s['county'] in pic18 else 'OHIO'

    def org_region(r, state, county, country):
        own = owner_sites.get(r['org_id'], [])
        regs = {site_region(s) for s in own}
        if 'PIC18' in regs or (state == 'OH' and county in pic18):
            return 'PIC18'
        if 'OHIO' in regs or state == 'OH':
            if state == 'OH' and not county and 'OHIO' not in regs:
                raise Unassignable('Ohio HQ with blank county and no frame site: could be PIC-18')
            return 'OHIO'
        if not state and country in ('', 'US', 'USA', 'United States') and not own:
            raise Unassignable('blank HQ state, no frame site')
        return 'REST'
    stratum_of = {'PIC18': 'PIC18_RECORDS', 'OHIO': 'REST_OHIO_RECORDS', 'REST': 'REST_US_RECORDS'}
    frame, bad = [], []
    def put(stratum, t, rid, basis, region_basis=''):
        frame.append(dict(stratum=stratum, table=t, record_id=rid, basis=basis, region_basis=region_basis))
    for t, idc in (('sites', 'site_id'), ('organizations', 'org_id'), ('ecosystem', 'org_id')):
        for r in T[t]:
            if r[idc] not in inc.get(t, {}):
                continue
            try:
                if t == 'sites':
                    reg = site_region(r)
                elif t == 'organizations':
                    reg = org_region(r, r['hq_state'], r['hq_county'], r['hq_country'])
                else:
                    reg = org_region(r, r['state'], r['county'], 'US')
            except Unassignable as e:
                bad.append((t, r[idc], str(e)))
                continue
            put(stratum_of[reg], t, r[idc], inc[t][r[idc]], reg)
    for t, stratum in (('people', 'RESEARCHERS'), ('programs', 'PROGRAMS'), ('events', 'EVENTS'), ('event_participation', 'EVENTS')):
        for rid, basis in inc.get(t, {}).items():
            put(stratum, t, rid, basis)
    # 10c: every row of every sampled table is included or excluded for a named reason; nothing is lost
    rec = {}
    for t in T:
        n_in = len(inc.get(t, {}))
        n_ex = sum(excl[t].values())
        n_added = added.get(t, 0)
        assert n_in - n_added + n_ex == len(T[t]), f'{t}: {n_in} - {n_added} + {n_ex} != {len(T[t])}'
        rec[t] = dict(rows=len(T[t]), in_frame=n_in, of_which_owner_added=n_added, excluded=sum(excl[t].values()), excluded_by_reason=dict(sorted(excl[t].items())))
    assert len({(f['table'], f['record_id']) for f in frame}) == len(frame) == sum(rec[t]['in_frame'] for t in T) - len(bad), 'frame rows lost or duplicated'
    if check_published and hasattr(R, 'published_site_counts'):  # the site builder's own counts must equal ours
        pub = R.published_site_counts(T['sites'])
        got = dict(active_ab=len(inc.get('sites', {})), pic18=sum(1 for f in frame if f['table'] == 'sites' and f['region_basis'] == 'PIC18') + sum(1 for b in bad if b[0] == 'sites'),
                   ohio=sum(1 for f in frame if f['table'] == 'sites' and f['region_basis'] in ('PIC18', 'OHIO')) + sum(1 for b in bad if b[0] == 'sites'))
        assert not bad or all(b[0] != 'sites' for b in bad), f'unassignable sites make the published-count check impossible: {bad}'
        assert pub == got, f'published site counts {pub} != frame {got}'
        n_org = len([1 for r in T['organizations'] if ok(r, 'status')]); n_eco = len([1 for r in T['ecosystem'] if ok(r, 'status')])
        assert n_org + added['organizations'] == len(inc.get('organizations', {})) and n_eco + added['ecosystem'] == len(inc.get('ecosystem', {}))
        rec['published_site_counts'] = pub
    rec['frame_by_stratum'] = dict(Counter(f['stratum'] for f in frame))
    return frame, rec, bad


# ---- the draw
def permutation(seed, at, stratum, ids):
    """One seeded permutation of the sorted IDs per stratum. Stage 1 is its first n1 entries, stage 2 its first n2: a prefix, so extending never re-draws."""
    rng = random.Random(int.from_bytes(hashlib.sha256(seed + b'|' + at.encode() + b'|' + stratum.encode()).digest(), 'big'))
    ids = sorted(ids)
    rng.shuffle(ids)
    return ids


def plants(seed, at, pool, values, per_stratum=3):
    """Defect plants (PROTOCOL.md section 6). `pool` = frame records ranked just past n2 in each stratum's permutation, so no plant ever
    stands in for a sampled record. Per stratum, `per_stratum` of them get one judged field swapped, in the READING PACKET ONLY, for the same
    field of another pool record of the same table whose value differs. Readers must flag them; plants never enter a rate."""
    out = []
    for s in STRATA:
        cand = [r for r in pool if r['stratum'] == s]
        rng = random.Random(int.from_bytes(hashlib.sha256(seed + b'|' + at.encode() + b'|plant|' + s.encode()).digest(), 'big'))
        rng.shuffle(cand)
        for r in cand:
            if sum(1 for p in out if p['stratum'] == s) >= per_stratum:
                break
            row = values[(r['table'], r['record_id'])]
            fields = sorted(c for c, k in FIELD_CLASS[r['table']].items() if k == 'J' and row.get(c) and c not in ('status', 'verification_tier'))
            rng.shuffle(fields)
            donors = [d for d in cand if d['table'] == r['table'] and d['record_id'] != r['record_id']]
            for f in fields:
                d = next((d for d in donors if values[(d['table'], d['record_id'])].get(f) not in ('', row[f])), None)
                if d:
                    out.append(dict(stratum=s, table=r['table'], record_id=r['record_id'], field=f, donor_record_id=d['record_id']))
                    break
    return out


def sha(b):
    return hashlib.sha256(b).hexdigest()


def csv_text(rows, cols):
    f = io.StringIO()
    w = csv.DictWriter(f, fieldnames=cols, lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
    return f.getvalue()


def run_draw(R, at, seed, expected_seed_sha, out, plan=None, pic18=None, protocol_path=None, check_published=True):
    """The whole draw. `plan` is overridable only here (the selftest); the CLI always uses sizes.PLAN."""
    plan = plan or sizes.PLAN
    if sha(seed) != expected_seed_sha:
        sys.exit('refusing to draw: the seed file does not match the sealed sha256')
    out = Path(out)
    if (out / 'draw_receipt.json').exists():
        sys.exit('refusing to draw: this output folder already holds a draw (there is one binding draw)')
    pic18 = pic18 or R.regions()
    frame, rec, bad = build_frame(R, pic18, check_published)
    if bad:
        sys.exit('refusing to draw: records that fit no stratum (fix the data or get an owner ruling; never defaulted):\n' + '\n'.join(map(str, bad)))
    by = defaultdict(list)
    for f in frame:
        by[f['stratum']].append(f)
    sample, pool = [], []
    for s in STRATA:
        key = {(f['table'], f['record_id']): f for f in by[s]}
        full = permutation(seed, at, s, [f"{t}|{i}" for t, i in key])
        order = full[:plan[s]['n2']]
        pool += [dict(stratum=s, table=k.split('|', 1)[0], record_id=k.split('|', 1)[1]) for k in full[plan[s]['n2']:plan[s]['n2'] + PLANT_POOL]]
        for rank, k in enumerate(order, 1):
            t, i = k.split('|', 1)
            sample.append(dict(stratum=s, rank=rank, stage=1 if rank <= plan[s]['n1'] else 2, table=t, record_id=i, region_basis=key[(t, i)]['region_basis'],
                               basis=key[(t, i)]['basis'], stratum_N=len(by[s]), census='true' if len(by[s]) <= plan[s]['n2'] else 'false'))
    vals = {(t, r[ID_COL[t]]): r for t in ID_COL for r in R.rows(t)}
    pl = plants(seed, at, pool, vals)
    out.mkdir(parents=True, exist_ok=True)
    texts = {'frame.csv': csv_text(sorted(frame, key=lambda f: (f['stratum'], f['table'], f['record_id'])), ['stratum', 'table', 'record_id', 'basis', 'region_basis']),
             'sample.csv': csv_text(sample, list(sample[0])), 'plants.csv': csv_text(pl, ['stratum', 'table', 'record_id', 'field', 'donor_record_id'])}
    for n, t in texts.items():
        (out / n).write_text(t, encoding='utf-8')
    me = Path(__file__).resolve()
    receipt = dict(at=at, seed_sha256=sha(seed), draw_py_sha256=sha(me.read_bytes()), sizes_json_sha256=sha((H / 'sizes.json').read_bytes()),
                   protocol_md_sha256=sha(Path(protocol_path or H / 'PROTOCOL.md').read_bytes()) if (protocol_path or (H / 'PROTOCOL.md').exists()) else None,
                   rng='random.Random(int(SHA256(seed|at|stratum))).shuffle over the table|id keys sorted ascending; stage 1 = first n1, stage 2 = first n2 (prefix)',
                   plan={s: plan[s] for s in STRATA}, reconciliation=rec, files={n: sha(t.encode()) for n, t in texts.items()})
    (out / 'draw_receipt.json').write_text(json.dumps(receipt, indent=1, sort_keys=True) + '\n')
    return sample, pl, receipt


def require_ancestor(sha_, root=ROOT):
    """`--at` must be a full SHA that is an ancestor of (or equal to) origin/main: no branch tip, no local commit."""
    full = subprocess.check_output(['git', 'rev-parse', '--verify', sha_ + '^{commit}'], cwd=root).decode().strip()
    if full != sha_:
        sys.exit(f'--at must be the full 40-hex SHA ({full})')
    if subprocess.run(['git', 'merge-base', '--is-ancestor', full, 'origin/main'], cwd=root).returncode:
        sys.exit('refusing: --at is not an ancestor of origin/main')
    return full


# ---- selftest: synthetic fixtures only
class MemReader:
    def __init__(self, tables):
        self.t = tables
    def rows(self, t):
        return [dict(r) for r in self.t.get(t, [])]
    def header(self, t):
        return list(FIELD_CLASS[t])
    def regions(self):
        return {'Cuyahoga', 'Summit'}


def fixture():
    def row(t, **kw):
        r = dict.fromkeys(FIELD_CLASS[t], '')
        r.update(kw)
        return r
    org = lambda i, st='OH', co='Cuyahoga', status='active', tier='A', **kw: row('organizations', org_id=f'ORG-{i:06d}', legal_name=f'Fixture Org {i}', hq_state=st, hq_county=co, hq_country='US', status=status, verification_tier=tier, **kw)
    site = lambda i, o, st='OH', co='Cuyahoga', status='active', tier='A': row('sites', site_id=f'SITE-{i:06d}', org_id=f'ORG-{o:06d}', site_name=f'Fixture Site {i}', state=st, county=co, country='US', operating_status=status, verification_tier=tier, city=f'City{i}', street_address=f'{i} Fixture Way')
    t = dict(organizations=[], sites=[], ecosystem=[], people=[], programs=[], events=[], event_participation=[], evidence=[])
    for i in range(1, 121):  # 120 orgs, each with one site: 40 PIC-18, 40 rest of Ohio, 40 elsewhere
        st, co = ('OH', 'Cuyahoga') if i <= 40 else ('OH', 'Franklin') if i <= 80 else ('TX', '')
        t['organizations'].append(org(i, st, co, trade_names=f'Fixture Trade {i}'))
        t['sites'].append(site(i, i, st, co))
    t['organizations'].append(org(200, 'TX', '', status='unknown', tier='U'))  # owner of a PIC-18 site although its own record is not active A-C
    t['sites'].append(site(200, 200))
    t['organizations'].append(org(201, 'TX', '', status='closed'))  # excluded, named
    t['ecosystem'].append(row('ecosystem', org_id='ORG-000300', legal_name='Fixture Institute', state='OH', county='Summit', status='active', verification_tier='A', website='https://example.org'))
    for i in range(1, 91):
        t['people'].append(row('people', person_id=f'PERSON-{i:06d}', full_name=f'Fixture Person {i}', institution_org_id='ORG-000300', role_as_published='Professor', research_specialties=f'topic{i % 7}', verification_tier='A'))
        t['programs'].append(row('programs', program_id=f'PROG-{i:06d}', institution_org_id='ORG-000300', program_name=f'Fixture Program {i}', status='active', verification_tier='A', level=f'lvl{i % 5}'))
    t['people'].append(row('people', person_id='PERSON-009999', full_name='Fixture Person U', institution_org_id='ORG-000300', verification_tier='U'))
    for i in range(1, 11):
        t['events'].append(row('events', event_id=f'EVT-{i:06d}', name=f'Fixture Event {i}', status='active', verification_tier='A', home_city=f'Town{i}'))
    for i in range(1, 121):
        t['event_participation'].append(row('event_participation', participation_id=f'EVP-{i:06d}', event_id=f'EVT-{(i % 10) + 1:06d}', org_id=f'ORG-{i:06d}', edition_year='2025', role='exhibitor', verification_tier='A', edition_city=f'Place{i % 9}'))
    return t


TINY = {s: dict(a, n1=n1, n2=n2) for (s, a), (n1, n2) in zip(sizes.PLAN.items(), [(10, 20), (8, 12), (8, 12), (10, 20), (10, 20), (10, 20)])}


def selftest():
    import copy, shutil
    seed = b'THROWAWAY SEED, NOT THE SEALED ONE\n'
    tmp = Path(tempfile.mkdtemp(prefix='a12-selftest-'))
    try:
        R = MemReader(fixture())
        run = lambda name, reader=R, sd=seed, exp=None, plan=TINY: run_draw(reader, 'a' * 40, sd, exp or sha(seed), tmp / name, plan=plan, pic18={'Cuyahoga', 'Summit'}, protocol_path=H / 'PROTOCOL.md', check_published=False)
        s1, p1, r1 = run('one')
        # same input, same bytes; and the draw has the sizes the plan names
        s2, p2, r2 = run('two')
        for f in ('frame.csv', 'sample.csv', 'plants.csv', 'draw_receipt.json'):
            assert (tmp / 'one' / f).read_bytes() == (tmp / 'two' / f).read_bytes(), f
        counts = Counter(r['stratum'] for r in s1)
        assert counts == Counter({s: TINY[s]['n2'] for s in STRATA}), counts
        # stage 2 contains stage 1 as a prefix, and a different n2 changes nothing before rank n1
        for s in STRATA:
            a = [r['record_id'] for r in s1 if r['stratum'] == s and r['stage'] == 1]
            b = [r['record_id'] for r in s1 if r['stratum'] == s][:len(a)]
            assert a == b
        big = {s: dict(v, n2=v['n2'] + 4) for s, v in TINY.items()}
        s3, _, _ = run('three', plan=big)
        for s in STRATA:
            assert [r['record_id'] for r in s3 if r['stratum'] == s][:TINY[s]['n2']] == [r['record_id'] for r in s1 if r['stratum'] == s]
        # a different seed gives a different draw; same seed different SHA too
        s4, _, _ = run('four', sd=b'ANOTHER THROWAWAY\n', exp=sha(b'ANOTHER THROWAWAY\n'))
        assert [r['record_id'] for r in s4] != [r['record_id'] for r in s1]
        # the sealed hash is enforced: a seed with the wrong hash is refused, and so is a second draw into the same folder
        for bad_call in (lambda: run_draw(R, 'a' * 40, b'wrong seed', SEED_SHA256, tmp / 'five', plan=TINY, pic18={'Cuyahoga', 'Summit'}, check_published=False),
                         lambda: run('one')):
            try:
                bad_call()
                raise AssertionError('draw accepted what it must refuse')
            except SystemExit:
                pass
        assert not (tmp / 'five').exists()
        # the seed text appears in no output
        for p in (tmp / 'one').iterdir():
            assert seed.strip() not in p.read_bytes() and b'THROWAWAY' not in p.read_bytes(), p
        # frame reconciliation: the owner of a PIC-18 site is in the PIC-18 frame though its own record is not active A-C; closed org is excluded, named
        fr = {(f['table'], f['record_id']): f for f in csv.DictReader((tmp / 'one' / 'frame.csv').open())}
        assert fr[('organizations', 'ORG-000200')]['stratum'] == 'PIC18_RECORDS' and fr[('organizations', 'ORG-000200')]['basis'] == 'owner_of_frame_site'
        assert ('organizations', 'ORG-000201') not in fr and ('people', 'PERSON-009999') not in fr
        rec = r1['reconciliation']
        assert rec['organizations']['excluded_by_reason'] == {'status=closed; tier=A': 1, 'status=unknown; tier=U': 1} and rec['people']['excluded'] == 1 and rec['organizations']['of_which_owner_added'] == 1
        assert rec['frame_by_stratum']['PIC18_RECORDS'] == 40 + 40 + 1 + 1 + 1 + 0, rec['frame_by_stratum']  # 40 orgs + 40 sites + owner org + its site + ecosystem record in Summit
        # plants: three per stratum with a usable donor, in stage 1, fields judged, value differs
        for s in STRATA:
            ps = [p for p in p1 if p['stratum'] == s]
            assert 1 <= len(ps) <= 3, (s, len(ps))
        assert p1 == p2 and all(FIELD_CLASS[p['table']][p['field']] == 'J' for p in p1)
        sampled = {(r['table'], r['record_id']) for r in s1}
        assert not any((p['table'], p['record_id']) in sampled for p in p1), 'a plant stands in for a sampled record'
        # refusals: duplicate ID, FK break, unclassified column, region-less record
        def refuses(mutate, what):
            t = copy.deepcopy(fixture())
            mutate(t)
            try:
                _, _, bad = build_frame(MemReader(t), {'Cuyahoga', 'Summit'}, False)
                if bad:  # unassignable records: the frame reports them and run_draw refuses (below)
                    try:
                        run_draw(MemReader(t), 'a' * 40, seed, sha(seed), tmp / ('refused-' + what.replace(' ', '-')), plan=TINY, pic18={'Cuyahoga', 'Summit'}, check_published=False)
                    except SystemExit:
                        return
                    raise AssertionError(f'drew despite an unassignable record: {what}')
            except (AssertionError, SystemExit, KeyError) as e:
                if str(e).startswith('drew despite'):
                    raise
                return
            raise AssertionError(f'accepted: {what}')
        refuses(lambda t: t['organizations'].append(dict(t['organizations'][0])), 'duplicate organization id')
        refuses(lambda t: t['ecosystem'].append(dict(t['ecosystem'][0], org_id='ORG-000001')), 'id in both org tables')
        refuses(lambda t: t['sites'].append(dict(t['sites'][0], site_id='SITE-777777', org_id='ORG-999999')), 'site with no owner')
        refuses(lambda t: t['sites'][0].update(county=''), 'Ohio site with blank county')
        refuses(lambda t: t['organizations'].append(dict(t['organizations'][0], org_id='ORG-000500', hq_state='', hq_county='')), 'org with no state and no site')
        class BadHeader(MemReader):
            def header(self, t):
                return FIELD_CLASS[t] and list(FIELD_CLASS[t]) + (['new_column'] if t == 'people' else [])
        try:
            build_frame(BadHeader(fixture()), {'Cuyahoga'}, False)
            raise AssertionError('accepted an unclassified column')
        except AssertionError as e:
            assert 'new_column' in str(e)
        # count reconciliation breaks when a published count differs
        class WrongPublished(MemReader):
            def published_site_counts(self, sites):
                return dict(active_ab=1, pic18=1, ohio=1)
        try:
            build_frame(WrongPublished(fixture()), {'Cuyahoga', 'Summit'}, True)
            raise AssertionError('accepted a published-count mismatch')
        except AssertionError as e:
            assert 'published site counts' in str(e)
        # --at must be an ancestor of origin/main
        g = tmp / 'gitfix'
        g.mkdir()
        sh = lambda *a: subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@example.org', *a], cwd=g, check=True, capture_output=True).stdout.decode().strip()
        sh('init', '-q'); (g / 'a').write_text('1'); sh('add', 'a'); sh('commit', '-qm', 'one'); c1 = sh('rev-parse', 'HEAD')
        sh('update-ref', 'refs/remotes/origin/main', c1); (g / 'a').write_text('2'); sh('commit', '-qam', 'two'); c2 = sh('rev-parse', 'HEAD')
        assert require_ancestor(c1, g) == c1
        for bad_at in (c2, c1[:10]):
            try:
                require_ancestor(bad_at, g)
                raise AssertionError('accepted an --at that is not a full ancestor SHA')
            except SystemExit:
                pass
        # field-class table in PROTOCOL.md is exactly what draw.py generates
        proto = (H / 'PROTOCOL.md').read_text()
        assert '<!-- FIELDS:BEGIN -->\n' + fields_md() + '\n<!-- FIELDS:END -->' in proto, 'PROTOCOL.md field table differs from draw.py: run draw.py fields-md'
        assert SEED_SHA256 in proto and sha(b'') != SEED_SHA256
        # against the real repository at origin/main: columns all classified, IDs unique, counts reconciled to the site builder's own
        try:
            at = subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=ROOT).decode().strip()
        except subprocess.CalledProcessError:
            at = None
        if at:
            real, rec, bad = build_frame(GitReader(at), GitReader(at).regions())
            assert sum(rec['frame_by_stratum'].values()) == len(real) and set(rec['frame_by_stratum']) <= set(STRATA)
            print('real-data frame check at origin/main', at[:8], rec['frame_by_stratum'], f'{len(bad)} unassignable records (the draw would refuse)')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print('draw selftest: PASS')


if __name__ == '__main__':
    a = sys.argv[1:]
    arg = lambda n: a[a.index(n) + 1] if n in a else None
    if '--selftest' in a:
        selftest()
    elif a[:1] == ['fields-md']:
        print(fields_md())
    elif a[:1] == ['frame']:
        at = require_ancestor(arg('--at'))
        R = GitReader(at)
        frame, rec, bad = build_frame(R, R.regions())
        print(json.dumps(dict(at=at, reconciliation=rec, unassignable=bad), indent=1, sort_keys=True))
    elif a[:1] == ['draw']:
        at = require_ancestor(arg('--at'))
        seed = Path(arg('--seed-file')).read_bytes()
        s, p, r = run_draw(GitReader(at), at, seed, SEED_SHA256, arg('--out'))
        print(json.dumps(dict(at=at, drawn=dict(Counter(x['stratum'] for x in s)), stage1=dict(Counter(x['stratum'] for x in s if x['stage'] == 1)), plants=len(p)), sort_keys=True))
    else:
        sys.exit(__doc__)
