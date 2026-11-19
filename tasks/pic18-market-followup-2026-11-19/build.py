"""Replay the market-scale packet, market follow-up (idempotent): 13 group-site holds re-screened under owner ruling M1, plus Myrava under M2, ordered-word quote check, fill only a blank markets_served cell.
Reused from the market canary (tasks/pic18-market-canary-2026-11-18/build.py) with the frame parameterised, tier-dependent tier_effect, and pinned evidence IDs."""
import csv
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPO = ROOT  # the real checkout; ROOT is patched to a temp tree by check.py's builder tests, REPO is not
MKT3 = ROOT / 'tasks/pic18-markets-3-2026-11-16'
STORE = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist')
CORPUS, LIVE = STORE / 'pic18-corpus-2026-11-16', STORE / 'pic18-market-followup-2026-11-19'
SNAPSHOT = STORE / 'pic18-markets-3/manifest.snapshot.csv'
BASE = '55ab601a'  # merge-base this packet was built on; backups, row-count asserts and the new-ID check use it
FIRST_ID, LAST_ID = 397377, 397476  # owner ruling 2026-11-19 E1: one above the maximum evidence ID across data/evidence_*.csv at the base (EVD-397376)
BATCH = 'followup'
import frame as F  # the frame is recomputed from the merged batches' verdicts (check.py compares it with the ruling's ID list)
FRAME = F.frame()
assert len(FRAME) == F.EXPECTED, ('frame count changed', len(FRAME))
OWNER_M2 = {F.MYRAVA}  # owner ruling M2: the do-not-promote note caps the tier only
SUBJECTS = {r['org_id']: [n.strip() for n in r['names'].split(';')] for r in csv.DictReader((HERE / 'subjects.csv').open())} if (HERE / 'subjects.csv').exists() else {}
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(MKT3))  # witness_class is reused from MKT3, not copied
from shard_io import append_sorted
import witness_class

_spec = importlib.util.spec_from_file_location('mkt3_build', MKT3 / 'build.py')
_mkt3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mkt3)
read, found = _mkt3.read, _mkt3.found  # MKT3's csv reader and ordered-word quote matcher
shards = lambda: sorted(p for p in (ROOT / 'data').glob('organizations_*.csv') if p.stem != 'organizations_all')


def write(name, rows):
    with (HERE / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def locate(oid, kind, url):
    """The stored or live page for a quote: (raw path, text path, recorded raw sha256). Hash is checked by the caller."""
    if kind == 'stored':
        r = next(r for r in read(SNAPSHOT) if r['org_id'] == oid and r['url'] == url and r['status'] == 'ok' and r['text_file'])
        return CORPUS / (r['raw_file'] or r['text_file']), CORPUS / r['text_file'], r['sha256']
    assert kind == 'live', kind
    r = next(r for r in read(HERE / 'fetches.csv') if r['org_id'] == oid and r['url'] == url and r['status'] == 'ok' and r['retained'] == 'yes')
    return LIVE / r['raw_file'], LIVE / r['text_file'], r['sha256']


def witness_date(oid, kind, url):
    """The observation date of a witness, from its journal: the pinned corpus manifest's fetched_at for a stored page, the fetch journal's fetched_at for a live page (SCHEMA 4.13)."""
    if kind == 'stored':
        r = next(r for r in read(SNAPSHOT) if r['org_id'] == oid and r['url'] == url and r['status'] == 'ok' and r['text_file'])
    else:
        r = next(r for r in read(HERE / 'fetches.csv') if r['org_id'] == oid and r['url'] == url and r['status'] == 'ok' and r['retained'] == 'yes')
    return r['fetched_at'][:10]


def proposals(tiers):
    """selection.tsv columns: org, tags (;), pinned evidence IDs (;, one per tag), source kind, url, quote. IDs are pinned so a withdrawal never renumbers later rows."""
    vocab = json.loads((ROOT / 'docs/schema/vocab.json').read_text())['vocabularies']['MARKETS']['values']
    out = []
    for line in (HERE / 'selection.tsv').read_text().splitlines():
        oid, tags, ids, kind, url, quote = line.split('\t')
        assert oid in FRAME, ('outside frame', oid)
        values, evs = tags.split(';'), ids.split(';')
        assert len(values) == len(evs), ('one evidence ID per tag', oid)
        raw, text, recorded = locate(oid, kind, url)
        assert sha(raw) == recorded, ('raw hash mismatch', oid)
        page = text.read_text()
        assert found(page, quote), ('quote absent', oid)
        for value, evid in zip(values, evs):
            assert value in vocab, ('off vocabulary', value)
            out.append(dict(org_id=oid, field='markets_served', value=value, verdict='VERIFIED', source_kind=kind, source_url=url, quote=quote,
                            raw_sha256=recorded, text_sha256=sha(text),  # digest of the stored file's bytes, not of read_text() output
                            raw_file=str(raw.relative_to(STORE)), text_file=str(text.relative_to(STORE)), evidence_id=evid,
                            tier_effect='supports_U' if tiers[oid] == 'U' else 'supports_A'))  # narrative sentence on the company's own page; tier U banks supports_U (SCHEMA 4.13)
    assert len({(r['org_id'], r['value']) for r in out}) == len(out), 'duplicate proposal'
    ids = [r['evidence_id'] for r in out]
    assert len(set(ids)) == len(ids) and out and all(f'EVD-{FIRST_ID:06d}' <= i <= f'EVD-{LAST_ID}' for i in ids), 'evidence IDs duplicated or outside the assigned block'
    retired = {r['evidence_id'] for r in read(HERE / 'withdrawn.csv')} if (HERE / 'withdrawn.csv').exists() else set()  # withdrawn after review: never reused or renumbered
    assert not retired & set(ids), 'retired evidence ID reused'
    return out


def apply(inputs, evidence):
    """Stage every changed shard as a temp sibling, then os.replace each. Before replacing, each staged shard's row count must equal its row
    count at BASE (git show BASE:data/<shard>) plus the rows this packet adds to it: organization shards +0 (cell fills only), evidence
    shards + the packet's evidence rows for that shard. A truncated input shard therefore fails, whatever the current file holds. No market
    cell is written if any allocated evidence ID is occupied by different content or a different home shard."""
    rows = {p: read(p) for p in shards()}
    orgs = {r['org_id']: (p, r) for p, rs in rows.items() for r in rs}
    have = {r['evidence_id']: (p, r) for p in (ROOT / 'data').glob('evidence_*.csv') for r in read(p)}
    values = {}
    for r in inputs:
        values.setdefault(r['org_id'], []).append(r['value'])
    add = {}
    for ev in evidence:
        home = orgs[ev['record_id']][0]
        target = home.with_name(home.name.replace('organizations_', 'evidence_organizations_'))
        if ev['evidence_id'] in have:
            path, old = have[ev['evidence_id']]
            assert path == target and old == ev, ('evidence ID occupied by different content or shard', ev['evidence_id'])
        else:
            add.setdefault(target, []).append(ev)
    touched = {}
    for oid, tags in values.items():
        path, row = orgs[oid]
        expected = ';'.join(sorted(tags))
        assert row['markets_served'] in ('', expected), ('target cell is not blank', oid)  # the only write is into a blank cell
        if row['markets_served'] != expected:
            row['markets_served'] = expected
            touched[path] = rows[path]
    def base_count(path):
        return len(list(csv.DictReader(io.StringIO(subprocess.check_output(['git', 'show', f'{BASE}:data/{path.name}'], cwd=REPO, text=True)))))
    packet_rows = {}
    for ev in evidence:
        home = orgs[ev['record_id']][0]
        shard = home.with_name(home.name.replace('organizations_', 'evidence_organizations_')).name
        packet_rows[shard] = packet_rows.get(shard, 0) + 1
    staged = {}
    for path, rs in touched.items():
        tmp = path.with_name(path.name + '.tmp')
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=list(rs[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rs)
        tmp.write_bytes(buf.getvalue().encode('utf-8'))
        assert len(read(tmp)) == base_count(path), ('organization row count differs from base', path.name)
        staged[path] = tmp
    for path, evs in add.items():
        tmp = path.with_name(path.name + '.tmp')
        shutil.copyfile(path, tmp)
        append_sorted(tmp, evs, 'evidence_id')
        assert len(read(tmp)) == base_count(path) + packet_rows[path.name], ('evidence row count differs from base + packet rows', path.name)
        staged[path] = tmp
    # Backup only now, after every input check has passed. Each backup is written from `git show <merge-base>:<file>` into a directory named for the merge-base SHA
    # (so a new merge-base never reuses an older base's files), recorded in SHA256SUMS.json against the git blob, verified before it is trusted, and rewritten on mismatch
    # (a stale base or a truncated copy).
    backup = LIVE / f'pre-application-batch{BATCH}-{BASE}'
    backup.mkdir(parents=True, exist_ok=True)
    sums = {}
    packet_shards = set()  # every shard the packet touches (organization and evidence), whether or not it still needs a data write: a replay or retry re-verifies all of them
    for oid in values:
        home = orgs[oid][0]
        packet_shards |= {home, home.with_name(home.name.replace('organizations_', 'evidence_organizations_'))}
    for path in sorted(packet_shards, key=lambda p: p.name):
        blob = subprocess.check_output(['git', 'show', f'{BASE}:data/{path.name}'], cwd=REPO)
        want = hashlib.sha256(blob).hexdigest()
        dst = backup / path.name
        if not (dst.exists() and hashlib.sha256(dst.read_bytes()).hexdigest() == want):
            tmp = dst.with_name(dst.name + '.tmp')
            tmp.write_bytes(blob)
            os.replace(tmp, dst)
            assert hashlib.sha256(dst.read_bytes()).hexdigest() == want, ('backup does not match the git blob', path.name)
        sums[path.name] = dict(sha256=want, git_blob=subprocess.check_output(['git', 'rev-parse', f'{BASE}:data/{path.name}'], cwd=REPO, text=True).strip(), base=BASE)
    (backup / 'SHA256SUMS.json').write_text(json.dumps(sums, indent=2, sort_keys=True) + '\n')
    # Publish the evidence shards first, then the organization shards: an interruption can leave evidence rows without a cell, never a cell without its rows.
    for path in sorted(staged, key=lambda p: (not p.name.startswith('evidence_'), p.name)):
        os.replace(staged[path], path)


def verdict_rows(inputs):
    applied = {}
    for r in inputs:
        applied.setdefault(r['org_id'], []).append(r['value'])
    return [dict(v, values=';'.join(sorted(applied.get(v['org_id'], [])))) for v in read(HERE / 'verdicts.csv')]


def counts_for(tiers, inputs, verdicts):
    ap = {r['org_id'] for r in inputs}
    return dict(batch=BATCH, frame_organizations=len(FRAME), frame_out_of_scope=len(F.OUT_OF_SCOPE), applied_organizations=len(ap), applied_values=len(inputs),
                applied_by_source=dict(Counter(next(r['source_kind'] for r in inputs if r['org_id'] == o) for o in ap)),
                held_organizations=sum(v['verdict'] == 'STILL_UNCERTAIN' for v in verdicts),
                held_by_class=dict(Counter(v['hold_class'] for v in verdicts if v['verdict'] == 'STILL_UNCERTAIN')),
                applied_tiers=dict(Counter(tiers[o] for o in ap)), frame_tiers=dict(Counter(tiers[o] for o in FRAME)),
                read_basis=dict(Counter(v['read_basis'] for v in verdicts)),
                live_fetches=len(read(HERE / 'fetches.csv')) if (HERE / 'fetches.csv').exists() else 0)


def renumber(old_first, new_first):
    """The only way pinned evidence IDs change (never sed): a fixed offset over every ID in selection.tsv. Idempotent by refusal: a source ID already inside the
    allocated block (FIRST_ID..LAST_ID) means a replay and is refused; every new ID must fall inside the block; the number renumbered must equal the number matched.
    The file is written only after every check passes."""
    path = HERE / 'selection.tsv'
    lines = [l.split('\t') for l in path.read_text().splitlines()]
    src = [int(i[4:]) for l in lines for i in l[2].split(';')]
    assert not any(FIRST_ID <= n <= LAST_ID for n in src), 'a source ID is already inside the allocated block (already converted)'
    assert all(n >= old_first for n in src), 'a source ID is below the old block start'
    new = [n - old_first + new_first for n in src]
    assert all(FIRST_ID <= n <= LAST_ID for n in new), 'a new ID falls outside the allocated block'
    it = iter(new)
    done = 0
    for l in lines:
        ids = l[2].split(';')
        l[2] = ';'.join(f'EVD-{next(it):06d}' for _ in ids)
        done += len(ids)
    assert done == len(src), 'renumbered differs from matched'
    path.write_text('\n'.join('\t'.join(l) for l in lines) + '\n')
    print(f'renumbered {done} of {len(src)} matched IDs: EVD-{old_first:06d}.. to EVD-{new_first:06d}..')


def main():
    if '--renumber' in sys.argv:
        i = sys.argv.index('--renumber')
        return renumber(int(sys.argv[i + 1]), int(sys.argv[i + 2]))
    orgs = {r['org_id']: (p, r) for p in shards() for r in read(p)}
    tiers = {o: orgs[o][1]['verification_tier'] for o in FRAME}
    inputs = proposals(tiers)
    evidence = [dict(evidence_id=r['evidence_id'], record_table='organizations', record_id=r['org_id'], claim_type='activity',
                     claim_detail=f'markets_served {r["value"]}: "{r["quote"]}"', source_class='own_site', source_ref=r['source_url'],
                     observed_date=witness_date(r['org_id'], r['source_kind'], r['source_url']), tier_effect=r['tier_effect'], created_by='claude atlas-w19-mktfollow',
                     notes='Own-company source; field witness retained, SHA256 ' + r['raw_sha256']) for r in inputs]
    if '--packet-only' not in sys.argv:  # packet-only builds the CSVs without touching data/ (used until the size lane's PR has merged)
        apply(inputs, evidence)
    verdicts = verdict_rows(inputs)
    write('inputs.csv', inputs)
    write('evidence_packet.csv', evidence)
    write('verdicts.csv', verdicts)
    counts = counts_for(tiers, inputs, verdicts)
    (HERE / 'counts.json').write_text(json.dumps(counts, indent=2, sort_keys=True) + '\n')
    print(json.dumps(counts))


if __name__ == '__main__':
    main()
