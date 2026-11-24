#!/usr/bin/env python3
"""Audit 13 smoke harness: frame, preflight, draw (controller), fetch, run, score. PROTOCOL.md of
tasks/blind-audit-13-protocol-2026-11-24 says what each step means; README.md here says what is reused and forked.

    smoke.py frame     --at SHA --out DIR
    smoke.py preflight --at SHA --out DIR [--families CSV] [--approved CSV]... [--store PATH]
    smoke.py draw      --at SHA --preflight DIR --secret-file PATH --out DIR      (the controller runs this)
    smoke.py draw      --at SHA --records CSV --secret-file PATH --out DIR        (explicit list: known-answer run, selftest)
    smoke.py fetch     --draw DIR --cache DIR
    smoke.py run       --draw DIR --cache DIR
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

SMOKE_N = 40
PIC18 = 'PIC18_RECORDS'
PROVIDERS = ('astra', 'hydrogen', 'sonnet')
FAMILY_OF_PROVIDER = dict(astra='openai', hydrogen='google', sonnet='anthropic')
PLANTS_PER_PROVIDER = 3
CHECK_P = 0.15
FAMILIES = {'anthropic', 'openai', 'google', 'xai', 'uncertain'}  # uncertain: primary Astra, ALWAYS a Hydrogen second read, no check coin (controller 2026-11-24)
DEPENDS = {  # judged field -> fields a reader needs beside it (PROTOCOL: dependency inventory)
    'organizations': {'naics_primary': ('naics_primary_source_type', 'naics_primary_source_name')},
    'sites': {'naics_primary': ('naics_primary_source_type',)}}
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
    for r in R.rows('evidence'):
        if (r['record_table'], r['record_id']) in want:
            labels[r['record_table'], r['record_id']].add(r['created_by'])
    for t, parents in packets.CHILDREN.items():
        for r in R.rows(t):
            if 'created_by' not in r:
                continue
            for f in parents:
                if r[f]:
                    owner = 'sites' if f == 'site_id' else ('ecosystem' if r[f] in ecosystem else 'organizations') if f == 'org_id' else None
                    if owner and (owner, r[f]) in want:
                        labels[owner, r[f]].add(r['created_by'])
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
def packet_rows(R, entries, approved=frozenset(), ids=None):
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
    receipts, rblocks, rcounts = replays.coverage(R, keys, a.store)
    for reason, ks in rblocks.items():
        blocks[reason] += ks
    approved = read_approved(a.approved)
    built, problems = packet_rows(R, [dict(table=t, record_id=i) for t, i in keys], approved)
    for k, why in problems.items():
        blocks['packet:' + why].append(k)
    withheld = Counter(re.sub(r'.*/', '', c) for _, _, masked in built for c in masked)
    out = out_dir(a.out)
    put(out / 'frame.csv', text)
    put(out / 'routes.csv', draw.csv_text([dict(table=t, record_id=i, families=';'.join(sorted(fam_of[t, i])), route=route(fam_of[t, i])) for t, i in keys],
                                          ['table', 'record_id', 'families', 'route']))
    put(out / 'replay_receipts.json', jdump(receipts))
    put(out / 'blocks.csv', draw.csv_text([dict(reason=r, table=t, record_id=i) for r, ks in sorted(blocks.items()) for t, i in ks], ['reason', 'table', 'record_id']))
    summary = dict(at=R.at, frame_digest=receipt['frame_digest'], frame=receipt, routes=routes, unresolved_labels=dict(label_hits.most_common()),
                   families_file_sha256=sha(Path(a.families).read_bytes()) if a.families else None, approved_files=[sha(Path(p).read_bytes()) for p in a.approved],
                   replay_coverage=rcounts, packets_built=len(built), packets_blocked=len(problems), withheld_judged_cells=dict(withheld),
                   blocking_records_by_reason={r: len(set(ks)) for r, ks in sorted(blocks.items())}, blocking_records=len({k for ks in blocks.values() for k in ks}),
                   unplaced_could_be_pic18=len(unplaced), scripts=script_hashes())
    summary['status'] = 'PASS' if not summary['blocking_records'] and not unplaced else 'BLOCKED'
    put(out / 'preflight_receipt.json', jdump(summary))
    print(f"preflight at {R.at[:12]}: {len(keys)} records, digest {receipt['frame_digest'][:16]}")
    print('routes:', dict(routes), '| packets built', len(built), 'blocked', len(problems), '| withheld judged cells', dict(withheld))
    print('replay coverage (class: status counts):')
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
    secret = Path(a.secret_file).read_bytes().strip()
    assert len(secret) >= 32, 'secret file must hold at least 32 bytes'
    R = load(a.at)
    out = out_dir(a.out)
    if (out / 'draw_receipt.json').exists():
        sys.exit('refusing to draw: this folder already holds a draw (one binding draw per sealed attempt)')
    inputs = {}
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
        assert len(ids) >= SMOKE_N + 3 * PLANTS_PER_PROVIDER * 2, 'frame too small for the smoke and its plant pools'
        real = sorted(ids, key=lambda k: keyed(secret, 'smoke', '|'.join(k)))[:a.n]
        forced = {k: routes[k]['route'] for k in real}
        fam_of = {k: set(filter(None, routes[k]['families'].split(';'))) for k in ids}
        inputs.update(preflight_receipt_sha256=sha((pre / 'preflight_receipt.json').read_bytes()), frame_digest=receipt['frame_digest'],
                      routes_sha256=sha((pre / 'routes.csv').read_bytes()))
        pl = make_plants(R, secret, ids, set(real), fam_of)
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
                                              check_p=CHECK_P, method='HMAC-SHA256(secret, purpose|key): purposes smoke, plantpool|P, plant|P, order, coin; real = first n by smoke order',
                                              inputs=inputs, sample_sha256=sha((out / 'sample.csv').read_bytes()), scripts=script_hashes())))
    print(f'drew {len(real)} real + {len(pl)} plants at {R.at[:12]}; receipt written (the sample stays private)')
    return 0


def assert_unique(ids):
    dup = [k for k, n in Counter(ids).items() if n > 1]
    assert not dup, f'duplicate record ID refused: {dup[:3]}'


def make_plants(R, secret, ids, real, fam_of):
    """3 plants per participating reader provider, each from a record eligible for that provider and outside the real sample.
    Reuses draw.plants (a same-table, other-record value for one judged field) with a keyed seed per provider."""
    values = {(t, r[draw.ID_COL[t]]): r for t in ('organizations', 'ecosystem', 'sites') for r in R.rows(t)}
    used, out = set(real), []
    for p in PROVIDERS:
        eligible = [k for k in sorted(ids, key=lambda k: keyed(secret, 'plantpool|' + p, '|'.join(k))) if k not in used and FAMILY_OF_PROVIDER[p] not in fam_of[k]]
        pool = [dict(stratum=PIC18, table=t, record_id=i) for t, i in eligible[:60]]
        got = draw.plants(keyed(secret, 'plant', p), R.at, pool, values, per_stratum=PLANTS_PER_PROVIDER)
        assert len(got) == PLANTS_PER_PROVIDER, f'no usable plant pool for {p}'
        for g in got:
            used.add((g['table'], g['record_id']))
            out.append(dict(g, provider=p))
    return out


# ---------------------------------------------------------------- fetch / run / score
def cmd_fetch(a):
    return reading.fetch_stage(Path(a.draw), Path(a.cache), load, packet_rows, DEPENDS, a.skip_blocked)


def cmd_run(a):
    return reading.run_stage(Path(a.draw), Path(a.cache), a.out, a)


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
    f = s.add_parser('fetch'); f.add_argument('--draw', required=True); f.add_argument('--cache', required=True); f.add_argument('--skip-blocked', action='store_true', help='known-answer run only')
    f = s.add_parser('run'); f.add_argument('--draw', required=True); f.add_argument('--cache', required=True); f.add_argument('--out', required=True)
    f.add_argument('--stop-at', type=int, default=3); f.add_argument('--window', type=int, default=3); f.add_argument('--max-tokens-m', type=float, default=0)
    f = s.add_parser('score'); f.add_argument('--run', required=True)
    a = p.parse_args(argv)
    if a.cmd == 'draw' and bool(a.preflight) == bool(a.records):
        p.error('draw needs exactly one of --preflight (the frame) or --records (an explicit list)')
    return globals()['cmd_' + a.cmd](a)


if __name__ == '__main__':
    sys.exit(main())
