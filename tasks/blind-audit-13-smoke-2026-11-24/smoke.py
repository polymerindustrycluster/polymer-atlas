#!/usr/bin/env python3
"""Audit 13 smoke harness: frame, preflight, draw (controller), fetch, run, score. PROTOCOL.md of
tasks/blind-audit-13-protocol-2026-11-24 says what each step means; README.md here says what is reused and forked.

    smoke.py frame     --at SHA --out DIR
    smoke.py preflight --at SHA --out DIR [--families CSV] [--approved CSV]... [--store PATH]
    smoke.py draw      --at SHA --preflight DIR --secret-file PATH --out DIR --cache DIR [--approved CSV]...   (the controller runs this)
    smoke.py draw      --at SHA --records CSV --secret-file PATH --out DIR        (explicit list: known-answer run, selftest)
    smoke.py fetch     --draw DIR --cache DIR
    smoke.py run       --draw DIR --cache DIR
    smoke.py handcheck --run DIR --list [--draw DIR]       (the controller: what each plant read shows, beside the script flag)
    smoke.py handcheck --run DIR --csv PATH                (the controller: seal handcheck.csv; score refuses without it)
    smoke.py score     --run DIR

Never run `draw` against the PIC-18 frame except as the controller. Tools only: no data/ writes anywhere.
"""
import argparse, csv, hashlib, hmac, io, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TOOL = ROOT / 'tasks/blind-audit-12-tooling-2026-11-23'
sys.path[:0] = [str(HERE)]
sys.path.insert(1, str(TOOL))  # packets.py puts audit 12's draw.py and audit 11's sample.py on the path itself
import packets  # noqa: E402
from packets import draw  # noqa: E402  (audit 12 draw.py: GitReader, build_frame, plants, FIELD_CLASS)
import reading  # noqa: E402
import replays  # noqa: E402

SMOKE_N = reading.SMOKE_N
PIC18 = 'PIC18_RECORDS'
PROVIDERS = ('astra', 'hydrogen', 'sonnet')
FAMILY_OF_PROVIDER = dict(astra='openai', hydrogen='google', sonnet='anthropic')
PLANTS_PER_PROVIDER = 3
CHECK_P = 0.15
FAMILIES = {'anthropic', 'openai', 'google', 'xai', 'uncertain'}  # uncertain: primary Astra, ALWAYS a Hydrogen second read, no check coin (controller 2026-11-24)
DEPENDS = {  # a populated core field needs the locality shown beside it (a missing one blocks). NAICS source gaps are NOT_INSPECTED, not blocks.
    'sites': {'street_address': ('city', 'state'), 'county': ('state',)},
    'organizations': {'hq_county': ('hq_city',)}}
SCRIPTS = ('smoke.py', 'reading.py', 'replays.py', 'READER_INSTRUCTIONS.md')
AUDIT12 = ROOT / 'tasks/blind-audit-12-protocol-2026-11-23'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def script_hashes():
    h = {n: sha((HERE / n).read_bytes()) for n in SCRIPTS}
    h.update({f'audit12/{p.name}': sha(p.read_bytes()) for p in (AUDIT12 / 'draw.py', TOOL / 'packets.py', TOOL / 'replay.py')})
    return h


# Field inventory updated for the current published facts (PROTOCOL: "including process and material other-notes"). A column that
# is neither in draw.py's table nor listed here still fails build_frame's classification assertion and blocks sampling.
FIELD_ADDITIONS = {('organizations', 'processes_other_note'): 'J', ('organizations', 'materials_other_note'): 'J'}


def load(at):
    """Pinned reader. Registers what draw.py predates: the derived table value_basis (SCHEMA 4.24, class D, generated from evidence and
    never read) and the FIELD_ADDITIONS columns, each only if the table or column exists at the SHA."""
    R = draw.GitReader(draw.require_ancestor(at))
    if 'data/value_basis.csv' in R.files and 'value_basis' not in draw.FIELD_CLASS:
        draw.TABLE_FILE['value_basis'] = r'data/value_basis\.csv'
        draw.FIELD_CLASS['value_basis'] = {c: 'D' for c in R.header('value_basis')}
    for (table, col), cls in FIELD_ADDITIONS.items():
        if col in R.header(table) and col not in draw.FIELD_CLASS[table]:
            draw.FIELD_CLASS[table][col] = cls
    return R


# ---------------------------------------------------------------- frame
def pic18_frame(R):
    """-> (rows, receipt dict, unplaced). Records: orgs/ecosystem owning an active tier A-C PIC-18 site, and those sites. draw.py's
    PIC18_RECORDS stratum also admits owners whose HQ alone is in PIC-18; those are excluded by reason here (controller decision)."""
    frame, rec, bad = draw.build_frame(R, R.regions())
    sites = {s['site_id']: s for s in R.rows('sites')}
    stratum = [f for f in frame if f['stratum'] == PIC18]
    owners = {sites[f['record_id']]['org_id'] for f in stratum if f['table'] == 'sites'}
    rows = [f for f in stratum if f['table'] == 'sites' or f['record_id'] in owners]
    hq_only = [f for f in stratum if f not in rows]
    by_table = Counter(f['table'] for f in rows)
    uniq = {(f['table'], f['record_id']) for f in rows}
    assert len(uniq) == len(rows), 'duplicate record in the PIC-18 frame'
    assert by_table['sites'] == rec['published_site_counts']['pic18'], 'PIC-18 site count differs from the site builder'
    text = draw.csv_text(sorted(rows, key=lambda f: (f['table'], f['record_id'])), ['stratum', 'table', 'record_id', 'basis', 'region_basis'])
    unplaced_pic = [b for b in bad if 'PIC-18' in b[2]]
    receipt = dict(at=R.at, frame_digest=sha(text.encode()), records=len(rows), by_table=dict(by_table), owners_with_pic18_site=len(owners),
                   owner_added_basis=Counter(f['basis'] for f in rows if f['table'] != 'sites'),
                   excluded=dict(hq_in_pic18_without_pic18_site=Counter(f['table'] for f in hq_only), other_strata=Counter(f['stratum'] for f in frame if f['stratum'] != PIC18),
                                 per_table_by_reason={t: rec[t]['excluded_by_reason'] for t in ('organizations', 'ecosystem', 'sites')}),
                   unplaced=Counter(b[2] for b in bad), unplaced_could_be_pic18=len(unplaced_pic),
                   reconciliation={t: {k: v for k, v in rec[t].items() if k != 'excluded_by_reason'} for t in ('organizations', 'ecosystem', 'sites')})
    return text, rows, json.loads(json.dumps(receipt)), unplaced_pic


def out_dir(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.chmod(0o700)
    return path


def put(path, text):
    if path.exists():
        path.unlink()
    draw.write_private(path, text)


def jdump(obj):
    return json.dumps(obj, indent=1, sort_keys=True) + '\n'


def cmd_frame(a):
    R = load(a.at)
    text, rows, receipt, unplaced = pic18_frame(R)
    out = out_dir(a.out)
    put(out / 'frame.csv', text)
    put(out / 'frame_receipt.json', jdump(dict(receipt, scripts=script_hashes())))
    print(f"PIC-18 frame at {R.at[:12]}: {receipt['records']} records {receipt['by_table']}, digest {receipt['frame_digest'][:16]}")
    print('excluded (HQ in PIC-18, no PIC-18 site):', receipt['excluded']['hq_in_pic18_without_pic18_site'])
    if unplaced:
        print('BLOCK: records that could be PIC-18 and fit no stratum:', unplaced, file=sys.stderr)
        return 1
    return 0


# ---------------------------------------------------------------- builder families
def label_map(path):
    if not path:
        return []
    rows = list(csv.DictReader(open(path, newline='')))
    assert rows and {'label_prefix', 'family'} <= set(rows[0]) <= {'label_prefix', 'family', 'evidence'} and all(r['family'] in FAMILIES for r in rows), 'families CSV: header label_prefix,family; family one of ' + ','.join(sorted(FAMILIES))
    return sorted(((r['label_prefix'], r['family']) for r in rows), key=lambda x: -len(x[0]))


def builder_labels(R, keys):
    """record key -> set of provenance labels: the record's own created_by, its evidence rows', its scoped children's, and 'repair:<folder>'
    for every task folder whose CLAIMS_CHECKED.csv lists it (the repo's own repair ledger)."""
    want = set(keys)
    labels = defaultdict(set)
    ecosystem = {r['org_id'] for r in R.rows('ecosystem')}
    for t in ('organizations', 'ecosystem', 'sites'):
        for r in R.rows(t):
            k = (t, r[draw.ID_COL[t]])
            if k in want:
                labels[k].add(r['created_by'])
    ev_key = {}
    for r in R.rows('evidence'):
        ev_key[r['evidence_id']] = (r['record_table'], r['record_id'])
        if ev_key[r['evidence_id']] in want:
            labels[ev_key[r['evidence_id']]].add(r['created_by'])
    for t, parents in packets.CHILDREN.items():
        for r in R.rows(t):
            if 'created_by' not in r:
                continue
            for f in parents:
                if r[f]:
                    owner = packets.LINKS[f]
                    owner = 'ecosystem' if owner == 'organizations' and r[f] in ecosystem else owner
                    if (owner, r[f]) in want:
                        labels[owner, r[f]].add(r['created_by'])
    for r in R.rows('archive_links'):
        if ev_key.get(r['evidence_id']) in want:
            labels[ev_key[r['evidence_id']]].add(r['created_by'])
    for path in R.git('ls-tree', '-r', '--name-only', R.at, 'tasks/').splitlines():
        if path.endswith('/CLAIMS_CHECKED.csv'):
            folder = path.split('/')[1]
            for r in csv.DictReader(io.StringIO(R.git('show', f'{R.at}:{path}'), newline='')):
                if (r.get('table'), r.get('record_id')) in want:
                    labels[r['table'], r['record_id']].add('repair:' + folder)
    return labels


def families_of(labels, gate, readme_of, lmap):
    """-> (set of families, unresolved labels). An empty or unmapped label is unresolved, never a guess."""
    fams, unresolved = set(), set()
    for lab in labels:
        f = ''
        if lab.startswith('repair:'):
            f = gate.builder_family(readme_of(lab[7:]))
        elif lab.strip():
            f = gate.family_of_text(lab)
            folder = gate.label_folder(lab)
            f = f or (gate.builder_family(readme_of(folder)) if folder else '')
        f = f or next((fam for p, fam in lmap if lab.startswith(p)), '')
        (fams.add(f) if f else unresolved.add(lab or '(blank)'))
    return fams, unresolved


def block_reason(labels, fams, unresolved):
    """Why a record cannot be read, or ''. An unknown or unmapped label blocks; so does a record whose builders leave no independent primary."""
    if not labels or unresolved:
        return 'unknown_builder_family'
    return '' if route(fams) else 'no_eligible_primary_reader'


def route(fams):
    """Primary reader: Astra when OpenAI did not build the record, else Hydrogen when Google did not, else none (blocks)."""
    return 'astra' if 'openai' not in fams else 'hydrogen' if 'google' not in fams else ''


# ---------------------------------------------------------------- label -> family evidence (controller ruling 2026-11-24)
HARNESS_FAMILY = {'codex': 'openai', 'claude-code': 'anthropic', 'claude': 'anthropic', 'antigravity': 'google', 'gemini': 'google', 'agy': 'google', 'grok': 'xai'}
TRAILER = re.compile(r'^Co-Authored-By:\s*(.+)$', re.M | re.I)


def label_evidence(label, at, root=ROOT):
    """-> (family, evidence). The first commit under data/ (or, for a repair folder, under its tasks/ folder) that added the label; its PR's head
    branch agent/<harness>/...; else a Co-Authored-By trailer naming one family; else `uncertain`. Never a guess."""
    import os, subprocess
    env = {k: v for k, v in os.environ.items() if k not in ('GH_TOKEN', 'GITHUB_TOKEN')}
    git = lambda *a: subprocess.run(['git', *a], cwd=root, capture_output=True, text=True).stdout
    if label.strip().lower() == 'unknown':
        return 'uncertain', 'the label is the word unknown: no commit can be traced to it'
    where = ('tasks/' + label[7:]) if label.startswith('repair:') else 'data'
    needle = '' if label.startswith('repair:') else label
    out = (git('log', '--reverse', '--format=%H%x09%ad%x09%s', '--date=short', '--', where) if not needle else git('log', '-S' + needle, '--reverse', '--format=%H%x09%ad%x09%s', '--date=short', '--', where)).splitlines()
    out = [l for l in out if l]
    if not out:
        return 'uncertain', 'no commit under data/ adds this label'
    sha_, date, subject = out[0].split('\t', 2)
    pr = re.search(r'\(#(\d+)\)\s*$', subject)
    if pr:
        view = subprocess.run(['gh', 'pr', 'view', pr[1], '--json', 'headRefName'], cwd=root, capture_output=True, text=True, env=env)
        try:
            branch = json.loads(view.stdout)['headRefName']
        except ValueError:
            branch = ''
        harness = branch.split('/')[1] if branch.startswith('agent/') and branch.count('/') >= 2 else ''
        if harness in HARNESS_FAMILY:
            return HARNESS_FAMILY[harness], f'commit {sha_[:9]} {date} PR #{pr[1]} branch {branch}'
        pr_note = f'PR #{pr[1]} branch {branch or "unreadable"} names no harness'
    else:
        pr_note = 'direct push, no PR; journal not consulted'
    names = {HARNESS_FAMILY[w] for t in TRAILER.findall(git('show', '-s', '--format=%B', sha_)) for w in re.findall(r'[a-z]+', t.lower()) if w in HARNESS_FAMILY}
    if len(names) == 1:
        return names.pop(), f'commit {sha_[:9]} {date} Co-Authored-By trailer; {pr_note}'
    return 'uncertain', f'commit {sha_[:9]} {date}; {pr_note}'


def cmd_labels(a):
    from concurrent.futures import ThreadPoolExecutor
    labels = sorted(json.loads((Path(a.preflight) / 'preflight_receipt.json').read_text())['unresolved_labels'])
    labels = [l for l in labels if not l.startswith('(')]
    with ThreadPoolExecutor(4) as pool:
        found = list(pool.map(lambda l: label_evidence(l, a.at), labels))
    rows = [dict(label_prefix=l, family=f, evidence=e) for l, (f, e) in zip(labels, found)]
    Path(a.out).write_text(draw.csv_text(rows, ['label_prefix', 'family', 'evidence']))
    print(f'{len(rows)} labels -> {a.out}; sha256 {sha(Path(a.out).read_bytes())}; families {dict(Counter(r["family"] for r in rows))}')
    return 0


# ---------------------------------------------------------------- packets
def packet_rows(R, entries, approved=frozenset(), ids=None, candidates=None):
    """Render and scan one packet per entry with audit 12's own builder. -> (rows, masked cells per row, problems per entry)."""
    head = packets.Head(R)
    out, problems = [], {}
    for n, e in enumerate(entries, 1):
        bid = (ids or {}).get((e['table'], e['record_id'])) or f'A13-{n:04}'
        try:
            row, masked, allowed = packets.render_row(head, dict(e, stratum=e.get('stratum', PIC18)), bid, approved)
            row = reading.drop_withheld_tokens(row, R)
            reading.dependency_check(row, DEPENDS)
            packets.leak_scan([row], {bid: allowed}, approved=approved)
            out.append((e, row, masked))
        except (ValueError, KeyError) as exc:
            if candidates is not None and 'row' in locals() and isinstance(exc, ValueError):
                hits = set()
                try:
                    packets.leak_scan([row], {bid: allowed}, approved=approved, context_candidates=hits)
                except ValueError:
                    pass
                candidates.update(hits)
            problems[(e['table'], e['record_id'])] = re.sub(r'A13-\d+|[A-Z]+-\d{4,}', '#', str(exc))[:90] or type(exc).__name__
    return out, problems


def read_approved(paths):
    approved = set()
    for p in paths:
        rows = list(csv.DictReader(open(p, newline='')))
        assert tuple(rows and rows[0] or ()) == packets.CANDIDATE_FIELDS, 'approval CSV header must match the candidate inventory'
        approved.update(tuple(r[k] for k in packets.CANDIDATE_FIELDS) for r in rows)
    return approved


# ---------------------------------------------------------------- preflight
def cmd_preflight(a):
    from replay import pinned_gate
    R = load(a.at)
    text, rows, receipt, unplaced = pic18_frame(R)
    keys = [(f['table'], f['record_id']) for f in rows]
    gate = pinned_gate(R.at)
    readme_cache = {}
    def readme_of(folder):
        if folder not in readme_cache:
            readme_cache[folder] = gate.tasks_file(R.at, f'tasks/{folder}/README.md') or b''
        return readme_cache[folder]
    lmap = label_map(a.families)
    labels = builder_labels(R, keys)
    blocks, fam_of, routes, label_hits = defaultdict(list), {}, Counter(), Counter()
    for k in keys:
        fams, unresolved = families_of(labels[k], gate, readme_of, lmap)
        if not labels[k]:
            unresolved = {'(no provenance label on the record, its evidence or its children)'}
        fam_of[k] = fams
        for lab in unresolved:
            label_hits[lab] += 1
        why = block_reason(labels[k], fams, unresolved)
        if why:
            blocks[why].append(k)
        routes[route(fams) or 'blocked'] += 1
    receipts, ni_classes, rcounts, _, _ = replays.coverage(R, keys, a.store)
    approved = read_approved(a.approved)
    leak_candidates = set()
    built, problems = packet_rows(R, [dict(table=t, record_id=i) for t, i in keys], approved, candidates=leak_candidates)
    for k, why in problems.items():
        blocks['packet:' + why].append(k)
    withheld = Counter(re.sub(r'.*/', '', c) for _, _, masked in built for c in masked)
    out = out_dir(a.out)
    put(out / 'frame.csv', text)
    put(out / 'routes.csv', draw.csv_text([dict(table=t, record_id=i, families=';'.join(sorted(fam_of[t, i])), route=route(fam_of[t, i])) for t, i in keys],
                                          ['table', 'record_id', 'families', 'route']))
    put(out / 'replay_receipts.json', jdump(receipts))
    put(out / 'leak_candidates.csv', draw.csv_text([dict(zip(packets.CANDIDATE_FIELDS, c)) for c in sorted(leak_candidates)], packets.CANDIDATE_FIELDS))
    put(out / 'blocks.csv', draw.csv_text([dict(reason=r, table=t, record_id=i) for r, ks in sorted(blocks.items()) for t, i in ks], ['reason', 'table', 'record_id']))
    summary = dict(at=R.at, frame_digest=receipt['frame_digest'], frame=receipt, routes=routes, unresolved_labels=dict(label_hits.most_common()),
                   families_file_sha256=sha(Path(a.families).read_bytes()) if a.families else None, approved_files=[sha(Path(p).read_bytes()) for p in a.approved],
                   replay_coverage=rcounts, not_inspected_filed_claims={c: len(v) for c, v in sorted(ni_classes.items())}, store=str(a.store), routes_sha256=sha((out / 'routes.csv').read_bytes()),
                   leak_candidate_cells=len(leak_candidates), packets_built=len(built), packets_blocked=len(problems), withheld_judged_cells=dict(withheld),
                   blocking_records_by_reason={r: len(set(ks)) for r, ks in sorted(blocks.items())}, blocking_records=len({k for ks in blocks.values() for k in ks}),
                   unplaced_could_be_pic18=len(unplaced), scripts=script_hashes())
    summary['status'] = 'PASS' if not summary['blocking_records'] and not unplaced else 'BLOCKED'
    put(out / 'preflight_receipt.json', jdump(summary))
    print(f"preflight at {R.at[:12]}: {len(keys)} records, digest {receipt['frame_digest'][:16]}")
    print('routes:', dict(routes), '| packets built', len(built), 'blocked', len(problems), '| withheld judged cells', dict(withheld))
    print('replay coverage (class: status counts; not_inspected = no replayer, reported not blocked):')
    for c, v in sorted(rcounts.items()):
        print(f'  {c}: {v}')
    if label_hits:
        print('unresolved builder labels (label: records):')
        for lab, n in label_hits.most_common(25):
            print(f'  {n:5d}  {lab[:80]}')
    for r, n in summary['blocking_records_by_reason'].items():
        print(f'BLOCK {n:5d} records: {r}')
    print(summary['status'], f"({summary['blocking_records']} blocking records)")
    return 0 if summary['status'] == 'PASS' else 1


# ---------------------------------------------------------------- draw (controller)
def keyed(secret, purpose, ident):
    return hmac.new(secret, f'{purpose}|{ident}'.encode(), hashlib.sha256).digest()


def cmd_draw(a):
    assert a.pool >= 1, '--pool must be at least 1'
    globals()['PLANT_POOL'] = a.pool
    secret = Path(a.secret_file).read_bytes().strip()
    assert len(secret) >= 32, 'secret file must hold at least 32 bytes'
    R = load(a.at)
    out = out_dir(a.out)
    if (out / 'draw_receipt.json').exists():
        sys.exit('refusing to draw: this folder already holds a draw (one binding draw per sealed attempt)')
    inputs, plant_report, rejects = {}, {}, read_rejects(a.reject_plants)
    if a.reject_plants and a.records: sys.exit('refusing: --reject-plants applies to a frame draw; an explicit-list draw has no plants')
    if a.records:  # explicit list: no sampling, no plants. Used by the known-answer run and the selftest.
        recs = list(csv.DictReader(open(a.records, newline='')))
        ids = [(r['table'], r['record_id']) for r in recs]
        assert_unique(ids)
        forced = {(r['table'], r['record_id']): r.get('provider', '') for r in recs}
        real = sorted(ids, key=lambda k: keyed(secret, 'smoke', '|'.join(k)))
        pl, fam_of = [], {k: set() for k in ids}
        inputs['records_sha256'] = sha(Path(a.records).read_bytes())
        for k in ids:
            if forced[k] and forced[k] not in PROVIDERS:
                sys.exit(f'unknown provider {forced[k]}')
    else:
        pre = Path(a.preflight)
        receipt = json.loads((pre / 'preflight_receipt.json').read_text())
        assert receipt['status'] == 'PASS' and receipt['at'] == R.at, 'preflight must PASS at this exact SHA before a draw'
        frame_text = (pre / 'frame.csv').read_text()
        assert sha(frame_text.encode()) == receipt['frame_digest'], 'frame.csv differs from the preflight receipt'
        routes = {(r['table'], r['record_id']): r for r in csv.DictReader(open(pre / 'routes.csv', newline=''))}
        ids = sorted(routes)
        assert sha((pre / 'routes.csv').read_bytes()) == receipt['routes_sha256'], 'routes.csv differs from the preflight receipt'
        assert set(ids) == {(r['table'], r['record_id']) for r in csv.DictReader(io.StringIO(frame_text))} and len(ids) == receipt['frame']['records'], 'routes.csv does not cover exactly the sealed frame'
        assert a.n == SMOKE_N, 'the sealed smoke is 40 records'
        assert len(ids) >= SMOKE_N + 3 * PLANTS_PER_PROVIDER * 2, 'frame too small for the smoke and its plant pools'
        real = sorted(ids, key=lambda k: keyed(secret, 'smoke', '|'.join(k)))[:a.n]
        forced = {k: routes[k]['route'] for k in real}
        fam_of = {k: set(filter(None, routes[k]['families'].split(';'))) for k in ids}
        inputs.update(preflight_receipt_sha256=sha((pre / 'preflight_receipt.json').read_bytes()), frame_digest=receipt['frame_digest'], routes_sha256=receipt['routes_sha256'],
                      families_file_sha256=receipt['families_file_sha256'], approved_files=sorted(receipt['approved_files']), store=receipt['store'])
        assert a.cache, 'a frame draw needs --cache: plants are drawn only from records whose cached pages state the true value'
        assert sorted(sha(Path(p).read_bytes()) for p in a.approved) == sorted(receipt['approved_files']), 'approval files differ from the sealed preflight'
        chk, memo = plant_checker(R, Path(a.cache), read_approved(a.approved)), {}

        def eligible(cands):  # the cached-page check runs once per candidate set, however many times the sealed order is walked
            key = tuple((c['table'], c['record_id'], c['field']) for c in cands)
            memo[key] = memo[key] if key in memo else chk(cands)
            return memo[key]
        eligible.quotes = chk.quotes
        try:
            done = []
            for rej in rejects:  # a reject must name a plant of the draw made with the rejects before it
                base = make_plants(R, secret, ids, set(real), fam_of, eligible, None, {(x['record_id'], x['field']) for x in done})
                if (rej['record_id'], rej['field']) not in {(p['record_id'], p['field']) for p in base}:
                    raise ValueError(f"reject {rej['record_id']}/{rej['field']} is not a drawn plant")
                done.append(rej)
            pl = make_plants(R, secret, ids, set(real), fam_of, eligible, plant_report, {(x['record_id'], x['field']) for x in rejects})
        except ValueError as exc:
            sys.exit(f'refusing to draw (nothing written): {exc}')
        if a.reject_plants: inputs['plant_rejects_sha256'] = sha(Path(a.reject_plants).read_bytes())
    sample = [dict(kind='real', table=t, record_id=i, provider=forced[t, i], plant_field='', donor_record_id='') for t, i in real]
    sample += [dict(kind='plant', table=p['table'], record_id=p['record_id'], provider=p['provider'], plant_field=p['field'], donor_record_id=p['donor_record_id']) for p in pl]
    assert len({(s['table'], s['record_id']) for s in sample}) == len(sample), 'a plant overlaps a real record or another plant'
    sample.sort(key=lambda s: keyed(secret, 'order', f"{s['table']}|{s['record_id']}"))
    for pos, s in enumerate(sample, 1):
        c = int.from_bytes(keyed(secret, 'coin', f"{s['table']}|{s['record_id']}")[:8], 'big') / 2**64
        s.update(pos=pos, blind_id=f'A13-{pos:04}', check_coin='1' if s['kind'] == 'real' and c < CHECK_P else '0')
    cols = ['pos', 'blind_id', 'kind', 'table', 'record_id', 'provider', 'check_coin', 'plant_field', 'donor_record_id']
    put(out / 'sample.csv', draw.csv_text(sample, cols))
    put(out / 'families.json', jdump({f'{t}|{i}': sorted(f) for (t, i), f in fam_of.items() if any(s['record_id'] == i and s['table'] == t for s in sample)}))
    put(out / 'draw_receipt.json', jdump(dict(at=R.at, secret_sha256=sha(secret), n_real=len(real), plants={p: sum(1 for s in pl if s['provider'] == p) for p in PROVIDERS},
                                              check_p=CHECK_P, method='HMAC-SHA256(secret, purpose|key): purposes smoke, plantpool|P, order, coin; real = first n by smoke order; plants = first 3 per provider in plantpool order whose cached pages pass reading.plant_reason',
                                              inputs=inputs, **({'plant_rejects': rejects} if a.reject_plants else {}), plant_eligibility=plant_report, plants_detail=plant_details(sample, plant_report.pop('plants', [])), sample_sha256=sha((out / 'sample.csv').read_bytes()), scripts=script_hashes())))
    print(f'drew {len(real)} real + {len(pl)} plants at {R.at[:12]}; receipt written (the sample stays private)')
    return 0


def read_rejects(path):
    """--reject-plants FILE: a CSV `record_id,field,reason`, in the order the controller refused them. Every row names a pair and says why."""
    if not path: return []
    rows = list(csv.DictReader(open(path, newline='')))
    assert rows and set(rows[0]) == {'record_id', 'field', 'reason'}, '--reject-plants needs the columns record_id,field,reason and at least one row'
    assert all(r['record_id'] and r['field'] and r['reason'].strip() for r in rows), 'every reject needs a record_id, a field and a reason'
    return [dict(record_id=r['record_id'], field=r['field'], reason=r['reason'].strip()) for r in rows]


def sealed_rejects(receipt):
    """A draw made with --reject-plants carries the reject file's sha256; without it fetch and run refuse the draw."""
    if 'plant_rejects' in receipt and not receipt['inputs'].get('plant_rejects_sha256'):
        sys.exit('refusing: this draw used --reject-plants but its receipt carries no sha256 of the reject file')


def assert_unique(ids):
    dup = [k for k, n in Counter(ids).items() if n > 1]
    assert not dup, f'duplicate record ID refused: {dup[:3]}'


PLANT_PREFERRED = ('street_address', 'county', 'hq_county', 'legal_name', 'site_name', 'hq_city', 'city', 'zip')  # core and locality fields first
PLANT_POOL = 40  # records tried per provider before the draw gives up; the draw receipt counts how many were eligible
FIELDS_PER_RECORD = 4  # (record, field) pairs tried per pool record: a page may state the county but not the street


def plant_candidates(values, order, p):
    """Pool for provider p in sealed order: per record, up to FIELDS_PER_RECORD populated judged fields (core and locality first) each with a donor
    whose value is distinct from the true one (reading.distinct), never `status` or `verification_tier`."""
    pool, recs = [], set()
    for k in order:
        if len(recs) == PLANT_POOL:
            break
        row = values[k]
        cols = [c for c in PLANT_PREFERRED if c in row] + sorted(c for c, kind in draw.FIELD_CLASS[k[0]].items() if kind == 'J' and c not in ('status', 'verification_tier') and c not in PLANT_PREFERRED)
        for f in cols:
            donor = next((d for d in order if d[0] == k[0] and d != k and reading.distinct(f, row.get(f), values[d].get(f))), None) if row.get(f) else None
            if donor and sum(1 for c in pool if (c['table'], c['record_id']) == k) < FIELDS_PER_RECORD:
                pool.append(dict(stratum=PIC18, table=k[0], record_id=k[1], field=f, donor_record_id=donor[1], provider=p, true_value=row[f]))
                recs.add(k)
    return pool


def make_plants(R, secret, ids, real, fam_of, eligible=None, report=None, rejects=()):
    """3 plants per participating reader provider, each from a record eligible for that provider (its family did not build it) and outside the real
    sample, with one judged field swapped for another record's distinct value, in the packet only. The sealed HMAC order (plantpool|P) fixes the pool.
    `eligible(candidates) -> {(table, record_id, field): reason or ''}` is draw-time proof that the ideal answer detects the plant on the cached pages
    the reader will see (reading.plant_reason): plants are the first 3 records in sealed order with an eligible field. `rejects` = (record_id, field) pairs the controller's hand-check refused:
    each is skipped and the next eligible pair in the same sealed order is taken. No eligible 3 -> ValueError with counts."""
    values = {(t, r[draw.ID_COL[t]]): r for t in ('organizations', 'ecosystem', 'sites') for r in R.rows(t)}
    used, out = set(real), []
    for p in PROVIDERS:
        order = [k for k in sorted(ids, key=lambda k: keyed(secret, 'plantpool|' + p, '|'.join(k))) if k not in used and FAMILY_OF_PROVIDER[p] not in fam_of[k]]
        cands = plant_candidates(values, order, p)
        checked = eligible(cands) if eligible else {}
        why = {(c['table'], c['record_id'], c['field']): checked.get((c['table'], c['record_id'], c['field']), 'not_checked' if eligible else '') for c in cands}  # a pair the checker never answered is not eligible
        why = {k: ('rejected_by_controller' if (k[1], k[2]) in rejects else v) for k, v in why.items()}
        got, seen = [], set()
        for c in cands:
            key = (c['table'], c['record_id'])
            if len(got) < PLANTS_PER_PROVIDER and key not in seen and not why.get((c['table'], c['record_id'], c['field'])):
                got.append({k: v for k, v in c.items() if k != 'true_value'})
                seen.add(key)
        counts = dict(pool_records=len({(c['table'], c['record_id']) for c in cands}), pairs=len(cands), eligible_records=len({(c['table'], c['record_id']) for c in cands if not why.get((c['table'], c['record_id'], c['field']))}),
                      reasons=dict(Counter(why.get((c['table'], c['record_id'], c['field'])) or 'eligible' for c in cands)), checked=eligible is not None)
        if report is not None:
            report[p] = counts
            quotes = getattr(eligible, 'quotes', {})
            report.setdefault('plants', []).extend(dict(provider=p, table=g['table'], record_id=g['record_id'], field=g['field'], planted_value=values[(g['table'], g['donor_record_id'])][g['field']],
                                                        true_value=next(c['true_value'] for c in cands if (c['table'], c['record_id'], c['field']) == (g['table'], g['record_id'], g['field'])),
                                                        **quotes.get((g['table'], g['record_id'], g['field']), {})) for g in got)
        if len(got) != PLANTS_PER_PROVIDER:
            raise ValueError(f'plant pool exhausted for {p}: {counts}')
        used |= {(g['table'], g['record_id']) for g in got}
        out += got
    return out


def plant_checker(R, cache_dir, approved):
    """The draw-time eligibility test: build each candidate's planted packet exactly as fetch will, fetch its sources into the cache (the same cache the
    fetch stage reuses), and ask reading.plant_reason whether the ideal answer detects it on the excerpts a reader would see."""
    def check(cands):
        entries = [dict(table=c['table'], record_id=c['record_id'], field=c['field'], donor_record_id=c['donor_record_id'], stratum=PIC18) for c in cands]
        built, problems = packet_rows(R, entries, approved)
        manifest = reading.fetch_urls(cache_dir, {u for _, row, _ in built for u in reading.urls_of(row)})
        true = {(c['table'], c['record_id'], c['field']): c['true_value'] for c in cands}
        why = {(t, i, f): 'packet_gate' for (t, i) in problems for f in {c['field'] for c in cands if (c['table'], c['record_id']) == (t, i)}}
        for e, row, _ in built:
            key = (e['table'], e['record_id'], e['field'])
            sources = reading.build_sources(dict(row=row, urls=reading.urls_of(row)), manifest, cache_dir)
            why[key], sid, quote = reading.plant_verdict(row, e['field'], true[key], sources)
            check.quotes[key] = dict(source_id=sid, source_url=sources[sid]['url'] if sid else '', eligibility_quote=quote)  # exactly what the check used; the draw receipt lists it
        return why
    check.quotes = {}
    return check


def plant_details(sample, details):
    """The draw receipt's per-plant list: each chosen plant with its blind ID, provider, planted and true value, source and eligibility quote (controller-private)."""
    ids = {(s['table'], s['record_id']): s['blind_id'] for s in sample if s['kind'] == 'plant'}
    return [dict(d, blind_id=ids[d['table'], d['record_id']]) for d in details]


def true_value(R, table, record_id, field, _cache={}):
    if (R.at, table) not in _cache:
        _cache[R.at, table] = {r[draw.ID_COL[table]]: r for r in R.rows(table)}
    return _cache[R.at, table][record_id][field]


# ---------------------------------------------------------------- fetch / run / score
def cmd_fetch(a):
    receipt = json.loads((Path(a.draw) / 'draw_receipt.json').read_text())
    sealed_rejects(receipt)
    inputs = receipt['inputs']
    if 'preflight_receipt_sha256' in inputs:  # the sealed inputs carry forward: same approvals, same store
        assert sorted(sha(Path(p).read_bytes()) for p in a.approved) == inputs['approved_files'], 'approval files differ from the sealed preflight'
        assert str(a.store) == inputs['store'], 'store path differs from the sealed preflight'
    return reading.fetch_stage(Path(a.draw), Path(a.cache), load, packet_rows, read_approved(a.approved), a.store, a.skip_blocked, true_value)


def cmd_run(a):
    sealed_rejects(json.loads((Path(a.draw) / 'draw_receipt.json').read_text()))
    return reading.run_stage(Path(a.draw), Path(a.cache), a.out, a)


def cmd_handcheck(a):
    if a.list:
        return reading.handcheck_list(a.run, a.draw)
    if not a.csv:
        sys.exit('handcheck needs --csv (to seal) or --list')
    return reading.handcheck_stage(a.run, a.csv)


def cmd_score(a):
    return reading.score_stage(Path(a.run))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest='cmd', required=True)
    f = s.add_parser('frame'); f.add_argument('--at', required=True); f.add_argument('--out', required=True)
    f = s.add_parser('preflight'); f.add_argument('--at', required=True); f.add_argument('--out', required=True)
    f.add_argument('--families'); f.add_argument('--approved', action='append', default=[]); f.add_argument('--store', type=Path, default=replays.STORE)
    f = s.add_parser('labels'); f.add_argument('--at', required=True); f.add_argument('--preflight', required=True); f.add_argument('--out', required=True)
    f = s.add_parser('draw'); f.add_argument('--at', required=True); f.add_argument('--out', required=True); f.add_argument('--secret-file', required=True)
    f.add_argument('--preflight'); f.add_argument('--records'); f.add_argument('--n', type=int, default=SMOKE_N)
    f.add_argument('--cache'); f.add_argument('--approved', action='append', default=[]); f.add_argument('--pool', type=int, default=PLANT_POOL, help='plant pool records per provider (the draw receipt reports how many were eligible)')
    f.add_argument('--reject-plants', help='CSV record_id,field,reason: plants the controller hand-check refused; the draw skips each and takes the next eligible pair in the same sealed order')
    f = s.add_parser('fetch'); f.add_argument('--draw', required=True); f.add_argument('--cache', required=True); f.add_argument('--skip-blocked', action='store_true', help='explicit-list fixture only')
    f.add_argument('--approved', action='append', default=[]); f.add_argument('--store', type=Path, default=replays.STORE)
    f = s.add_parser('run'); f.add_argument('--draw', required=True); f.add_argument('--cache', required=True); f.add_argument('--out', required=True)
    f.add_argument('--stop-at', type=int, default=reading.STOP_AT); f.add_argument('--window', type=int, default=3); f.add_argument('--max-tokens-m', type=float, default=0)
    f = s.add_parser('handcheck'); f.add_argument('--run', required=True); f.add_argument('--csv'); f.add_argument('--list', action='store_true'); f.add_argument('--draw')
    f = s.add_parser('score'); f.add_argument('--run', required=True)
    a = p.parse_args(argv)
    if a.cmd == 'draw' and bool(a.preflight) == bool(a.records):
        p.error('draw needs exactly one of --preflight (the frame) or --records (an explicit list)')
    return globals()['cmd_' + a.cmd](a)


if __name__ == '__main__':
    sys.exit(main())
