"""Named check for blind audit 11.
Phase 1: frame reproduces from git and reconciles with every PR's published counts, one hand-verified known answer per stratum
(value at BASE, at HEAD, and at the step that made it), the classifier and leak scan catch planted defects, the sample re-draws
from the seed, and the blind inputs are identical, frozen and leak-free.
Phase 3: reviewer locks and the R-SAM redaction, cross-tab, adjudication coverage, every receipt, the band rule and UEI results
recomputed, final grades, statistics and the report regenerated, an R-SAM scan of every committed output, planted defects.
Adapted from tasks/blind-audit-10-2026-11-14/check.py.
Run from anywhere: python3 tasks/blind-audit-11-2026-11-17/check.py [--require-private]   (needs full git history)
Without the private files (raw page bodies, stored SAM response, reviewer originals) the parts that need them are listed as
NOT CHECKED; --require-private turns any such gap into a failure.
"""
import ast, copy, csv, hashlib, json, re, sys, tempfile
from urllib.parse import urlsplit
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import adjudicate_build as AB
import adjudicate_fetch as AF
import copy_verdicts as CV
import frame as F
import sample as S
import stats as ST
import write_report as WR

H = F.H
sha = lambda p: hashlib.sha256((H / p).read_bytes()).hexdigest()
read = lambda p: list(csv.DictReader((H / p).open(newline='')))

# Published counts (AGENTS section 2 rule 10c), from each merged PR's body, or its task README where a replay superseded the body.
# (pr, table, class, kind) -> records
PUBLISHED = {
    (339, 'ecosystem', 'rulings', 'changed'): 1, (346, 'programs', 'rulings', 'changed'): 1,
    (341, 'registry_links', 'registry_federal_links', 'created'): 105, (341, 'sites', 'bands', 'changed'): 12,
    (340, 'members', 'members', 'changed'): 60, (340, 'members', 'members', 'created'): 1, (340, 'organizations', 'members', 'changed'): 1,
    (342, 'sites', 'zips', 'changed'): 348, (355, 'registry_links', 'uei_links', 'created'): 472, (353, 'sites', 'streets', 'changed'): 23,
    (350, 'organizations', 'navigation_links', 'changed'): 176, (349, 'organizations', 'markets', 'changed'): 16,
    (348, 'organizations', 'bands', 'changed'): 117,
    (348, 'sites', 'bands', 'changed'): 131,  # body says 137; tasks/ppp-size-bands-2026-11-16/README.md "Replay after PR #341": six #341 bands preserved, final 131
    (352, 'organizations', 'parents', 'changed'): 11, (351, 'sites', 'capabilities', 'changed'): 3, (351, 'site_capabilities', 'capabilities', 'created'): 8,
    (354, 'sites', 'tier_changes', 'changed'): 3, (344, 'organizations', 'markets', 'changed'): 31, (360, 'organizations', 'markets', 'changed'): 77,
    (361, 'sites', 'capabilities', 'changed'): 9, (361, 'site_capabilities', 'capabilities', 'created'): 4,
    (365, 'sites', 'capabilities', 'changed'): 14, (365, 'site_capabilities', 'capabilities', 'created'): 35,  # title says 45; body: 10 capability IDs retired, 35 rows
    (364, 'archive_links', 'archive_links', 'created'): 2188,
}
PUBLISHED_CELLS = {343: 58, 347: 63, 350: 234}  # "fill 58 / 63 ownership and founding fields"; "234 navigation cells"
PUBLISHED_337 = 3        # "All three material-filled records" (one organization, two sites)
PUBLISHED_336 = 1208     # "1,208 site coordinate pairs": all derived (coordinates), none in the frame

# Hand-verified from `git show` at BASE, HEAD and the merge step (class, table, record_id, step sha, pr, {col: (base, head)}); base None = created
KNOWN = [
    ('ownership_founding', 'organizations', 'ORG-000105', '20e87b3', 343, {'year_founded': ('', '1931'), 'ownership_type': ('', '')}),
    ('markets', 'organizations', 'ORG-000227', '45e184c', 360, {'markets_served': ('', 'aerospace_defense;appliances;automotive_unspecified;electronics_electrical;medical_healthcare_general')}),
    ('capabilities', 'site_capabilities', 'CAP-001106', 'b72f9df', 351, {'site_id': (None, 'SITE-001757'), 'capability_type': (None, 'material'), 'term': (None, 'polyurethane_pu'), 'provenance': (None, 'company_disclosed')}),
    ('streets', 'sites', 'SITE-000185', 'c7d606f', 353, {'street_address': ('', '300 Martinel Dr.')}),
    ('parents', 'organizations', 'ORG-000433', '915176b', 352, {'ultimate_parent_name': ('', 'HEXPOL Group'), 'parent_org_id': ('', '')}),
    ('registry_federal_links', 'registry_links', 'ORG-000038|FRS|110006267887|SITE-000038', '9bd1a8b', 341, {'match_basis': (None, 'echo_exporter_street_city_zip_name:SITE-000038')}),
    ('uei_links', 'registry_links', 'ORG-000889|UEI|SJZCEMGNC9D1|', 'd410968', 355, {'match_basis': (None, 'sam_exact_uei')}),
    ('bands', 'organizations', 'ORG-000478', '5b78ee7', 348, {'employee_band_ohio': ('', '1-9')}),
    ('members', 'members', 'MBR-000009', 'd18224a', 340, {'snapshot_date': ('2026-10-29', '2026-11-16'), 'display_name': ('Rubber Division', 'Rubber Division')}),
    ('zips', 'sites', 'SITE-000169', 'a66e2ae', 342, {'zip': ('', '44124')}),
    ('tier_changes', 'sites', 'SITE-000240', 'c958a8f', 354, {'verification_tier': ('C', 'B')}),
    ('archive_links', 'archive_links', 'EVD-013312|https://web.archive.org/web/20261104022108/https://www.avient.com/', '527ad21', 364, {'captured_at': (None, '2026-11-04')}),
    ('rulings', 'ecosystem', 'ORG-013503', '25e6f76', 339, {'polymer_program': ('true', '')}),
    ('rulings', 'programs', 'PROG-000329', 'ef32b5b', 346, {'status': ('active', 'tombstoned')}),
    ('navigation_links', 'organizations', 'ORG-000554', '23feb5c', 350, {'newsroom_url': ('', 'https://www.rpplusm.com/blog'), 'linkedin_url': ('', ''), 'newsroom_feed_url': ('', '')}),
]
A10_IS_ROLLUP_ONLY = lambda table, cols: table == 'ecosystem' and bool(set(cols) & {'polymer_program', 'polymer_program_name', 'polymer_program_url'}) and not set(cols) - {'last_verified', 'polymer_program', 'polymer_program_name', 'polymer_program_url'}  # A10 frame.py, verbatim logic


def check_frame():
    frame, prov = F.derive()
    assert read('frame.csv') == frame, 'frame.csv != git derivation'
    assert json.loads((H / 'frame_provenance.json').read_text()) == json.loads(json.dumps(prov)), 'provenance != git derivation'
    per = {(r['pr'], r['table'], r['change_class'], r['kind']): r['records'] for r in prov['per_pr']}
    for k, n in PUBLISHED.items():
        assert per.get(k) == n, f'PR #{k[0]} {k[1:]}: published {n}, git says {per.get(k)}'
    cells = Counter()
    for r in prov['cells_per_pr']:
        cells[r['pr']] += r['cells']
    for pr, n in PUBLISHED_CELLS.items():
        assert cells[pr] == n, f'PR #{pr}: published {n} cells, git says {cells[pr]}'
    assert sum(n for (pr, *_), n in per.items() if pr == 337) == PUBLISHED_337
    assert prov['derived_only_by_pr'] == [dict(pr=336, table='sites', records=PUBLISHED_336)]
    assert prov['generated_by_pr'] == [dict(pr=352, table='relationships', records=1)]  # "1 generated parent_of edge"
    assert set(per) == set(PUBLISHED) | {k for k in per if k[0] in (337, 343, 347)}, f'per-PR rows with no published count: {set(per) - set(PUBLISHED)}'
    for t, v in prov['tables'].items():  # per table: head = base + created; no deletions; nothing touched then reverted
        assert v['head_rows'] == v['base_rows'] + v['created'] and v['touched_then_reverted'] == 0, t
    assert prov['frame_total'] == len(frame) == sum(v['frame'] for v in prov['tables'].values()) == 3959
    assert dict(Counter(r['change_class'] for r in frame)) == prov['frame_by_class']
    assert sum(per.values()) == len(frame), 'every frame row is one per-PR record change (no record changed twice in one class)'
    assert len({(r['table'], r['record_id'], r['change_class']) for r in frame}) == len(frame), 'duplicate frame key'
    assert prov['trains'] == {'359': [353, 350, 349, 348, 356, 352, 351, 354], '363': [343, 347]}
    return frame, prov


def known_answers(frame):
    by = {(r['table'], r['record_id'], r['change_class']): r for r in frame}
    files = F.table_files(F.HEAD)
    for cl, t, k, step, pr, cols in KNOWN:
        row = by[(t, k, cl)]
        assert row['prs'] == str(pr), (k, row['prs'])
        step = F.git('rev-parse', step).strip()
        shard = row['shard']
        assert shard in files[t]
        get = lambda ref: next((r for r in F.rows_at(ref, shard) if F.key_of(t, r) == k), None)
        b, h, sb, sa = get(F.BASE), get(F.HEAD), get(step + '^1'), get(step)
        for c, (old, new) in cols.items():
            assert h[c] == new and sa[c] == new, (k, c, 'head/step value')
            assert (b is None and sb is None) if old is None else (b[c] == old and sb[c] == old), (k, c, 'base/pre-step value')
        assert set(cols) - {'capability_type', 'provenance', 'site_id', 'term', 'match_basis', 'captured_at', 'display_name', 'linkedin_url', 'newsroom_feed_url', 'ownership_type', 'parent_org_id'} \
            <= set(row['changed_columns'].split(';')), (k, row['changed_columns'])
    assert {cl for cl, *_ in KNOWN} == set(F.CLASSES), 'a stratum has no known answer'
    # #339 is in the frame although A10's rollup rule would have dropped it: the controller named the rulings stratum
    assert A10_IS_ROLLUP_ONLY('ecosystem', ['polymer_program']) and ('ecosystem', 'ORG-013503', 'rulings') in by
    # coordinates are derived: a coordinate-only change is excluded, a content change is kept, a shard move alone is not a change
    row = lambda **kw: ({'site_id': 'S', 'zip': '', 'latitude': '', 'longitude': '', 'geocode_precision': '', **kw})
    old = {'S': (row(), 'a.csv')}
    assert F.diff(old, {'S': (row(latitude='41.1', longitude='-81.5', geocode_precision='address_interpolated'), 'a.csv')})[2] == ['S']
    assert F.diff(old, {'S': (row(zip='44305', latitude='41.1'), 'a.csv')})[1] == {'S': ['zip']}
    assert F.diff(old, {'S': (row(), 'b.csv')})[4] == ['S']
    # classifier: every column maps or the build fails; ride-along alone fails; class split for registry links; authored edges fail
    assert F.classes_of_change('sites', 'S', ['zip', 'sources']) == {'zips': {'zip', 'sources'}}
    for bad in (['website'], ['last_verified', 'notes'], ['status']):
        try:
            F.classes_of_change('organizations', 'X', bad)
        except AssertionError:
            continue
        raise AssertionError(f'classifier accepted {bad}')
    assert F.created_class('registry_links', {'registry': 'UEI'}) == 'uei_links' and F.created_class('registry_links', {'registry': 'TRI_TRIFID'}) == 'registry_federal_links'
    try:
        F.created_class('relationships', {'relationship_id': 'R', 'relationship_type': 'member_of', 'basis': 'directory'})
    except AssertionError:
        pass
    else:
        raise AssertionError('an authored member_of edge was not refused')


def check_sample(frame):
    sample, alloc = S.draw(frame)
    assert sum(alloc.values()) == S.N == 120
    sizes = Counter(r['change_class'] for r in frame)
    assert all(alloc[c] >= S.FLOOR for c in sizes if sizes[c] >= S.CENSUS_BELOW) and all(alloc[c] == sizes[c] for c in sizes if sizes[c] < S.CENSUS_BELOW)
    norm = lambda rows: [{k: str(r[k]) for k in sample[0]} for r in rows]  # csv reads strings; draw() holds ints
    assert norm(read('sample.csv')) == norm(sample), 'sample.csv != seeded re-draw'
    assert {(r['table'], r['record_id'], r['change_class']) for r in sample} <= {(r['table'], r['record_id'], r['change_class']) for r in frame}
    return sample


def check_header(fields):
    assert fields == S.BLIND_FIELDS, f'blind header must be exactly the whitelist, got {fields}'


def check_blind(sample):
    assert (H / 'blind_a.csv').read_bytes() == (H / 'blind_b.csv').read_bytes(), 'blind_a != blind_b'
    check_header(list(csv.DictReader((H / 'blind_a.csv').open(newline='')).fieldnames))
    rows = read('blind_a.csv')
    key = lambda r: (r['table'], r['record_id'], S.BLIND_LABEL.get(r['change_class'], r['change_class']))
    assert len(rows) == 120 and {key(r) for r in rows} == {key(r) for r in sample}
    assert {r['blind_id']: key(r) for r in rows} == {r['blind_id']: key(r) for r in read('sample.csv')}, 'sample.csv blind_id map != blind file'
    assert 'rulings' not in {r['change_class'] for r in rows} and 'program_status' in {r['change_class'] for r in rows}
    assert not S.leak_scan(rows), S.leak_scan(rows)
    assert [r['record_id'] for r in rows] != sorted(r['record_id'] for r in rows), 'blind order follows ID order'
    assert not re.search(r'#\d+', (H / 'REVIEWER_INSTRUCTIONS.md').read_text()), 'reviewer instructions name a PR'
    freeze = json.loads((H / 'freeze.json').read_text())['sha256']
    assert set(freeze) >= {'blind_a.csv', 'blind_b.csv', 'REVIEWER_INSTRUCTIONS.md', 'frame.csv', 'sample.csv'}
    for p, h in freeze.items():
        assert sha(p) == h, f'{p} changed after freeze'
    return rows


def check_leak_scan_catches(rows):
    """Plant defects in a copy; every one must be caught (a gate that cannot fail is not a gate)."""
    plain = next(r for r in rows if r['table'] != 'archive_links')
    arch = next(r for r in rows if r['table'] == 'archive_links')
    for r, field, plant in [(plain, 'cited_sources', 'see PR #271'), (plain, 'evidence_json', 'EVD-333050'), (plain, 'values_json', 'minted in wave 3'),
                            (plain, 'cited_sources', 'verdict packet (staging working/x)'), (plain, 'context_json', '2026-11-16'),
                            (plain, 'cited_sources', 'Lane CAP2A'), (plain, 'values_json', 'per the 2026 ruling'), (plain, 'record_id', 'EVD-013312'), (arch, 'record_id', ' banked'),
                            (arch, 'values_json', 'EVD-013312')]:
        bad = [dict(x) for x in rows]
        i = rows.index(r)
        bad[i][field] = bad[i][field] + (' ' if field != 'record_id' or r is arch else '|') + plant
        assert S.leak_scan(bad), f'leak scan missed planted {plant!r} in {field}'
    assert not S.leak_scan([dict(plain, context_json='{"city": "Green Lane", "state": "PA"}')]), 'place name Green Lane must pass'
    try:
        check_header(S.BLIND_FIELDS + ['pr'])
    except AssertionError:
        return
    raise AssertionError('header check missed a planted pr column')


def verify_receipts(adj, gaps):
    """Each receipt: on the stored full body when present (hash, quote, absence, raw patterns); otherwise the quote on the committed
    excerpt only, and every check that needs the body is listed as a gap."""
    full = 0
    for e in adj:
        for r in e['receipts']:
            assert r['http_status'] == 200 or r['via'] == 'git', f"receipt on a page that did not load: {r['url']}"
            if r.get('quote'):
                assert AF.quote_in_order(r['excerpt_words'], r['quote']), f"excerpt lacks quote: {r['url']}"
            if r['via'] == 'git':
                _, ref, path = r['url'].split(':', 2)
                body = F.git('show', f'{ref}:{path}').encode()
            elif (AF.RAW / f"{r['sha256']}.bin").exists():
                body = (AF.RAW / f"{r['sha256']}.bin").read_bytes()
            else:
                if r.get('absent') or r.get('raw_re') or r.get('raw_not_re') or not r.get('quote'):
                    gaps.append(f"{e['id']} {r['url']}: stored body absent, raw checks not re-run")
                continue
            assert hashlib.sha256(body).hexdigest() == r['sha256'] and len(body) == r['bytes'], f"stored body hash mismatch: {r['url']}"
            text = AF.visible(body, r['url'])
            assert not r.get('quote') or AF.quote_in_order(text, r['quote']), f"quote not on stored page: {r['url']}"
            assert all(not re.search(re.escape(t), text, re.I) for t in r.get('absent', [])), f"absent term present: {r['url']}"
            assert not r.get('raw_re') or re.search(r['raw_re'].encode(), body), f"raw pattern missing: {r['url']}"
            assert not r.get('raw_not_re') or not re.search(r['raw_not_re'].encode(), body), f"forbidden raw pattern present: {r['url']}"
            if r.get('file_sha256'):
                assert r['url'] not in AB.PPP_SHA or AB.PPP_SHA[r['url']] == r['file_sha256'], f"PPP file is not #348's release: {r['url']}"
            full += 1
    return full


def rsam_hits(texts, ents):
    """SAM-only words in committed text: any SAM street line; any SAM name that is not also an Atlas name of the linked organization;
    any SAM entity URL host that is not the organization's Atlas website host; any host on the private R-SAM host list."""
    orgs = {k: r for k, (r, _) in F.load(F.HEAD, F.table_files(F.HEAD)['organizations'], 'organizations').items()}
    words = {p: ' ' + ' '.join(AF.WORDS(t)) + ' ' for p, t in texts.items()}
    host = lambda u: (urlsplit(u if '://' in (u or '') else 'https://' + (u or '')).hostname or '').removeprefix('www.')
    private_hosts = json.loads((CV.PRIVATE / 'rsam_redact_hosts.json').read_text())['hosts']
    hits = [(p, h) for h in private_hosts for p, w in words.items() if f" {' '.join(AF.WORDS(h))} " in w]
    for rid in [r['record_id'] for r in read('sample.csv') if r['change_class'] == 'uei_links']:
        org_id, _, uei, _ = rid.split('|')
        e, o = ents[uei], orgs[org_id]
        atlas = {AB.norm(o['legal_name'])} | {AB.norm(t) for t in o['trade_names'].split(';') if t.strip()}
        bad = [' '.join(AF.WORDS(e['coreData']['physicalAddress']['addressLine1']))]
        bad += [' '.join(AF.WORDS(e['entityRegistration'].get(k) or '')) for k in ('legalBusinessName', 'dbaName') if AB.norm(e['entityRegistration'].get(k)) not in atlas | {''}]
        eu = host(e['coreData']['entityInformation'].get('entityURL'))
        bad += [' '.join(AF.WORDS(eu))] if eu and eu != host(o['website']) else []
        hits += [(p, b) for b in bad if b for p, w in words.items() if f' {b} ' in w]
    return hits


RESULT_WORD = re.compile(r'(?<![\w-])(?:no[ _-]?)?match(?![\w-])', re.I)  # a match/no-match result word; 'matcher', 'name_match' are not
# The old adjudicate_build.py lines 99-104 (bc26e0f), result words as placeholders so this file pairs none: the planted leak.
OLD_UEI_LINES = """    *[dict(id=i, grade='AGREE', fields='registry_id', sam_expect='{m}',
           key_fact='Decided against the stored SAM response; the per-row basis is held privately under R-SAM.', receipts=[])
      for i in ('A11-033', 'A11-040', 'A11-051', 'A11-052', 'A11-071', 'A11-081', 'A11-083', 'A11-094', 'A11-101', 'A11-103', 'A11-109', 'A11-114')],
""", """    dict(id='A11-113', grade='CREATION_ERROR', fields='registry_id', sam_expect='{n}', current_value='UEI SJZCEMGNC9D1 linked to ORG-000889',
         correct_value='retire UEI link SJZCEMGNC9D1 on ORG-000889',
         key_fact='Retire UEI link SJZCEMGNC9D1 on ORG-000889; basis held privately under R-SAM (see follow-ups 1 and 2).', receipts=[]),
"""


def uei_id_re():
    """The identifiers of the 13 sampled UEI rows: blind ID, record ID, and the record ID's organization ID and UEI."""
    ids = set()
    for r in read('sample.csv'):
        if r['change_class'] == 'uei_links':
            org_id, _, uei, _ = r['record_id'].split('|')
            ids |= {r['blind_id'], r['record_id'], org_id, uei}
    return re.compile('|'.join(re.escape(i) for i in sorted(ids, key=len, reverse=True)))


def paired(strings, ids):
    return any(ids.search(s) for s in strings) and any(RESULT_WORD.search(s) for s in strings)


def public_leaks(texts):
    """Codex-21 gates: a SAM URL in any public file (the one exception is sam_batch.py's endpoint constant, the code that makes
    the call); any record-level sam_result in a public JSON, JSONL or CSV file; and (Codex-21 on bc26e0f) any pairing of a sampled
    UEI row's identifier with a match/no-match word: within one line of any file, one JSON object (its keys and scalar values),
    or one dict literal, dict() call or comprehension in Python (its string constants)."""
    hits, ids = [], uei_id_re()
    for name, t in texts.items():
        hits += [(name, f'UEI result paired on line {n}') for n, line in enumerate(t.splitlines(), 1) if paired([line], ids)]
        if name.endswith('.py'):
            for node in ast.walk(ast.parse(t)):
                if isinstance(node, (ast.Dict, ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)) or (isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'dict'):
                    if paired([c.value for c in ast.walk(node) if isinstance(c, ast.Constant) and isinstance(c.value, str)], ids):
                        hits.append((name, f'UEI result paired in the expression at line {node.lineno}'))
        for m in CV.SAM_URL.finditer(t):
            line = t[t.rfind('\n', 0, m.start()) + 1:t.find('\n', m.start())]
            if not (name == 'sam_batch.py' and line.startswith('URL = ')):
                hits.append((name, 'SAM URL'))
        if name.endswith(('.json', '.jsonl')):
            docs = [json.loads(l) for l in t.splitlines() if l.strip()] if name.endswith('.jsonl') else [json.loads(t)]
            stack = list(docs)
            while stack:
                x = stack.pop()
                if isinstance(x, dict):
                    hits += [(name, 'sam_result')] if 'sam_result' in x else []
                    hits += [(name, f"UEI result paired in object {x.get('id', '')}")] if paired([str(k) for k in x] + [str(v) for v in x.values() if not isinstance(v, (dict, list))], ids) else []
                    stack += list(x.values())
                elif isinstance(x, list):
                    stack += x
        elif name.endswith('.csv') and 'sam_result' in t.split('\n', 1)[0]:
            hits.append((name, 'sam_result column'))
    return hits


def check_phase3(require_private):
    gaps = []
    locks = json.loads((H / 'locks.json').read_text())
    sample = read('sample.csv')
    uei_ids = {r['blind_id'] for r in sample if r['change_class'] == 'uei_links'}
    for k in 'ab':
        assert locks[k]['locked_sha256'] == CV.LOCKED[k], f'{k}: lock hash in locks.json is not the BOARD lock'
        assert sha(f'verdicts_{k}.csv') == locks[k]['committed_sha256'] and sha(f'receipts_{k}.json') == locks[k]['receipts_sha256'], f'{k}: committed copy changed'
        rows = read(f'verdicts_{k}.csv')
        assert all(not r[c] for r in rows if r['blind_id'] in uei_ids for c in CV.FREE), f'{k}: a UEI row keeps a free-text cell (R-SAM)'
        orig, orig_r = CV.PRIVATE / f'out_{k}/verdicts.csv', CV.PRIVATE / f'out_{k}/receipts.json'
        if orig.exists():
            assert hashlib.sha256(orig.read_bytes()).hexdigest() == CV.LOCKED[k] and CV.redact(orig.read_bytes()) == (H / f'verdicts_{k}.csv').read_bytes(), f'{k}: committed copy is not the redacted original'
            pub, priv = CV.redact_receipts(orig_r.read_bytes(), k)
            assert hashlib.sha256(orig_r.read_bytes()).hexdigest() == locks[k]['receipts_original_sha256'] and pub == (H / f'receipts_{k}.json').read_bytes(), f'{k}: receipts copy is not the redacted original'
            assert priv is None or (CV.PRIVATE / f'receipts_{k}_sam_private.json').read_bytes() == priv, f'{k}: private SAM receipts file differs'
        else:
            gaps.append(f'reviewer {k} original absent: lock hash and redaction not re-derived')
    a, b = ({r['blind_id']: r['verdict'] for r in read(f'verdicts_{k}.csv')} for k in 'ab')
    assert len(a) == len(b) == 120 and a.keys() == b.keys() == {r['blind_id'] for r in sample}
    assert Counter(a.values()) == {'AGREE': 116, 'FIELD_ERROR': 3, 'CREATION_ERROR': 1} and Counter(b.values()) == {'AGREE': 101, 'UNRESOLVED': 19}
    assert Counter((a[i], b[i]) for i in a) == {('AGREE', 'AGREE'): 98, ('AGREE', 'UNRESOLVED'): 18, ('CREATION_ERROR', 'UNRESOLVED'): 1, ('FIELD_ERROR', 'AGREE'): 3}
    doc = json.loads((H / 'adjudication.json').read_text())
    adj = doc['decisions']
    disputed = {i for i in a if not (a[i] == b[i] == 'AGREE')}
    bands = {r['blind_id'] for r in sample if r['change_class'] == 'bands'}
    assert [e['id'] for e in adj if not e.get('lead_check')] and {e['id'] for e in adj if not e.get('lead_check')} == disputed and len(disputed) == 22
    assert {e['id'] for e in adj if e.get('lead_check')} == bands and len(bands) == 7 and len(adj) == 29, 'adjudication does not cover exactly the disputed rows and the band lead checks'
    for e in adj:
        assert e['grade'] in ST.GRADES and e['key_fact'] and (e['grade'] != 'UNRESOLVED' or e['settling_fact'])
        assert e['grade'] not in ('FIELD_ERROR', 'CREATION_ERROR') or (e['current_value'] and e['correct_value'])
        assert e['reviewer_a'] == a[e['id']] and e['reviewer_b'] == b[e['id']]
    full = verify_receipts(adj, gaps)
    # band rule: recomputed from git, and from the fresh SBA extract when it is present
    orgs, sites, ev = AB.head_tables()
    srow = {r['blind_id']: r for r in sample}
    for e in adj:
        if e.get('lead_check'):
            url = e['receipts'][0]['url']
            have = any((AF.RAW / f"{r['sha256']}.bin").exists() for r in AB.RECEIPTS if r['url'] == url)
            got = AB.band_facts(srow[e['id']], url, orgs, sites, ev, None if have else e['band_check']['ppp_row'])
            assert got == e['band_check'] and all(got['conditions'].values()) == (e['grade'] == 'AGREE'), f"{e['id']}: band check differs from recomputation"
            if not have:
                gaps.append(f"{e['id']}: SBA extract absent, PPP row taken from the committed copy")
    # UEI results and the R-SAM scan need the stored SAM response
    ueis = {e['id']: e['record_id'] for e in adj if e['id'] in uei_ids}
    assert len(ueis) == 13 and doc['meta']['sam_files_sha256'] == AB.SAM_FILES
    assert doc['meta']['uei_counts'] == {'match': 12, 'no_match': 1} == {'match': sum(e['grade'] == 'AGREE' for e in adj if e['id'] in ueis), 'no_match': sum(e['grade'] != 'AGREE' for e in adj if e['id'] in ueis)}
    committed = {p.name: p.read_text() for p in sorted(H.iterdir()) if p.suffix in ('.py', '.csv', '.json', '.jsonl', '.md')}  # every text file in the folder
    committed['report'] = WR.OUT.read_text()
    assert not public_leaks(committed), f'public leak: {public_leaks(committed)}'
    planted_adj = json.loads(committed['adjudication.json'])
    planted_adj['decisions'][0]['sam_result'] = 'match'
    for plant in (dict(committed, report=committed['report'] + ' https://api.sam' + '.gov/entity-information/v3/entities?ueiSAM=X'),
                  dict(committed, **{'write_report.py': committed['write_report.py'] + '\n# https://sam' + '.gov/entity/X\n'}),
                  dict(committed, **{'adjudication.json': json.dumps(planted_adj)})):
        assert public_leaks(plant), 'public-leak gate missed a planted SAM URL or record-level sam_result'
    # the old builder lines, whole and in parts (the comprehension pairs only through its ID tuple), and paired JSON and report text
    marker = '    # --- UEI links (#355)'
    comp, single = (s.format(m='match', n='no_match') for s in OLD_UEI_LINES)
    assert committed['adjudicate_build.py'].count(marker) == 1
    u = sorted(ueis)  # IDs taken from the sample, so this file pairs no ID with a result word
    pair_adj, prose_adj = json.loads(committed['adjudication.json']), json.loads(committed['adjudication.json'])
    next(e for e in pair_adj['decisions'] if e['id'] == u[0])['result'] = 'match'
    next(e for e in prose_adj['decisions'] if e['id'] == u[1])['key_fact'] += ' Stratum result: 12 match, 1 no-match.'
    for plant, where in [(dict(committed, **{'adjudicate_build.py': committed['adjudicate_build.py'].replace(marker, block + marker)}), 'adjudicate_build.py')
                         for block in (comp + single, comp, single)] + [(dict(committed, **{'adjudication.json': json.dumps(j, indent=1)}), 'adjudication.json') for j in (pair_adj, prose_adj)] + [
                         (dict(committed, report=committed['report'] + f'\n| {u[2]} | no-match |\n'), 'report')]:
        assert any(n == where and 'UEI result paired' in w for n, w in public_leaks(plant)), f'public-leak gate missed a planted UEI result pairing in {where}'
    if all((CV.PRIVATE / n).exists() for n in AB.SAM_FILES):
        verdict, note = AB.sam_facts(orgs, sites, ueis, write=False)
        assert all((e['grade'] == 'AGREE') == (verdict[e['id']] == 'match') for e in adj if e['id'] in ueis), 'UEI grades differ from the stored SAM response'
        assert hashlib.sha256(note.encode()).hexdigest() == doc['meta']['uei_private_note_sha256'], 'private UEI note changed'
        if AB.SAM_EXPECT.exists():
            assert json.loads(AB.SAM_EXPECT.read_text()) == verdict, "the lead's private per-row SAM decisions differ from the stored SAM response"
        else:
            gaps.append("the lead's private per-row SAM decisions absent: not compared with the stored SAM response")
        ents = AB.sam_entities()
        assert not rsam_hits(committed, ents), f'R-SAM: SAM-only words in committed output: {rsam_hits(committed, ents)}'
        e113 = ents[ueis['A11-113'].split('|')[2]]['coreData']
        for plant in (e113['physicalAddress']['addressLine1'], e113['entityInformation']['entityURL']):
            assert rsam_hits(dict(committed, report=committed['report'] + ' ' + plant), ents), 'R-SAM scan missed a planted SAM street line or entity URL'
    else:
        gaps.append('stored SAM response absent: UEI results, private-note hash and R-SAM scan not re-run')
    # final grades, statistics, report
    final = ST.final_grades()
    assert read('final_grades.csv') == [{k: str(v) for k, v in r.items()} for r in final], 'final_grades.csv != recomputation'
    res = ST.summarize(sample, final)
    stored = json.loads((H / 'statistics.json').read_text())
    for k, v in res.items():
        assert json.loads(json.dumps(v)) == stored[k], f'statistics.json {k} != recomputation'
    assert stored['final_counts'] == {'AGREE': 118, 'FIELD_ERROR': 1, 'CREATION_ERROR': 1, 'UNRESOLVED': 0} and stored['uei_rows'] == {'AGREE': 12, 'CREATION_ERROR': 1}
    assert stored['corrections'] == ST.corrections(adj) and len(stored['corrections']) == 2
    assert ST.wilson(0, 20) == [0, 0.161125] and ST.wilson(20, 20) == [0.838875, 1] and ST.wilson(10, 20) == [0.299298, 0.700702]
    assert WR.render() == WR.OUT.read_text(), 'docs/reviews report differs from the regenerated text'
    # planted defects: each must be rejected
    for bad in (final[:-1], final + [final[0]]):
        try:
            ST.summarize(sample, bad)
        except AssertionError:
            continue
        raise AssertionError('summarize accepted an incomplete or duplicated verdict census')
    real = AF.RAW
    AF.RAW = Path(tempfile.mkdtemp())
    try:
        g = []
        verify_receipts(adj, g)
        assert g, 'receipts with raw checks passed without any stored body'
    finally:
        AF.RAW = real
    e0 = copy.deepcopy(next(e for e in adj if e['id'] == 'A11-098'))
    e0['band_check']['ppp_row']['JobsReported'] = '60'
    assert AB.band_facts(srow['A11-098'], e0['receipts'][0]['url'], orgs, sites, ev, e0['band_check']['ppp_row'])['conditions']['band_equals_jobs_reported_band'] is False, 'band check accepted a wrong JobsReported'
    assert not AF.quote_in_order('nothing relevant', adj[0]['receipts'][0]['quote']), 'excerpt check accepted a quote that is not there'
    if gaps and require_private:
        raise AssertionError('NOT CHECKED with --require-private: ' + '; '.join(gaps))
    return full, gaps, stored


if __name__ == '__main__':
    frame, prov = check_frame()
    known_answers(frame)
    sample = check_sample(frame)
    rows = check_blind(sample)
    check_leak_scan_catches(rows)
    print(f"PASS blind-audit-11 phase 1: {len(frame)} frame record changes {prov['frame_by_class']}; published counts reconcile for {len(PUBLISHED)} "
          f"(PR, table, class) pairs + cells for #343/#347/#350; {len(KNOWN)} known answers ({len(F.CLASSES)} strata); sample {len(sample)} re-draws; "
          f"blind files identical, frozen, leak-free; planted defects caught")
    full, gaps, st = check_phase3('--require-private' in sys.argv)
    print(f"PASS blind-audit-11 phase 3: locks and R-SAM redaction, cross-tab 98/18/1/3, 29 adjudications (22 disputed + 7 band lead checks), "
          f"{full} receipts re-verified on stored bodies, band rule and UEI results recomputed, final grades {st['final_counts']}, statistics and report regenerate identically, planted defects rejected")
    for g in gaps:
        print('NOT CHECKED:', g)
