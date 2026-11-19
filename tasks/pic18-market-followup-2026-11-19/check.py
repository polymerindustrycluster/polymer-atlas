"""Recompute every published count, reconcile the frame against independent inputs, prove the check fails on injected defects."""
import copy
import hashlib
import inspect
import shutil
import csv
import json
import re
import subprocess
import sys
import tempfile
from urllib.parse import urlparse
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as B
import fetch
from build import (HERE, ROOT, MKT3, CORPUS, LIVE, SNAPSHOT, BASE, FIRST_ID, LAST_ID, FRAME, BATCH, OWNER_M2, SUBJECTS, F, read, found, sha, locate, proposals,
                   shards, verdict_rows, counts_for, witness_class)

# Wording each applied tag needs in its own quote, after the legal name is stripped (MKT3's map, plus the words this batch needs).
# medical_device covers implants, stents and thrombectomy systems by meaning (the canary's Theken precedent); plastics_rubber_processors covers
# the rotomolding and molders' industries (rotational molding and injection molding are plastics processes).
WORDS = {
    'aerospace_defense': r'aerospace|aviation|defen[cs]e|military|aircraft|armed forces', 'automotive_unspecified': r'automotive', 'automotive_oem': r'\boem\b|tier ?[1i]\b|original equipment', 'automotive_aftermarket': r'after ?market',
    'electronics_electrical': r'electronic|electrical', 'medical_healthcare_general': r'medical|health ?care|doctors', 'medical_device': r'medical device|implant|stent|thrombectomy|fda[- ]approved|physicians during procedures',
    'pharmaceutical_biotech': r'pharmaceutical', 'construction_building_products': r'construction|building', 'energy_oil_gas': r'oil and gas|petroleum',
    'marine': r'marine|boat', 'chemical_mining_metals_processing': r'chemical|mining|metal ?forming|metal forging', 'water_wastewater': r'wastewater', 'industrial_machinery': r'manufacturing machinery|machine manufacturers|production equipment', 'rail_transportation': r'\brail\b|locomotive', 'agriculture': r'agricult|farm',
    'general_industrial': r'industrial', 'food_processing_foodservice': r'food processing|food ?service|catering', 'plastics_rubber_processors': r'plastic|rubber|rotomold|molders',
    'telecom_datacom': r'telecom', 'dental': r'dentist|dental|denture', 'toys_sporting_goods': r'toys|sporting|sports', 'lawn_garden_recreation': r'\blawn\b', 'tire_rubber_goods': r'\btire', 'appliances': r'appliance', 'consumer_goods_housewares': r'housewares|household', 'energy_renewables_battery': r'batter(y|ies)', 'rv_powersports_trailers': r'\brv\b'
}
HOLD_CLASSES = {'no_market_claim', 'scope_owner_ruling', 'no_vocab_market', 'off_vocabulary_or_ambiguous_market', 'menu_or_nav_only', 'group_or_redirect_attribution', 'list_item_only'}
READ_BASES = {'page_read', 'text_screened'}


def git_rows(path):
    return list(__import__('csv').DictReader(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True).splitlines()))


def base_orgs():
    names = subprocess.check_output(['git', 'ls-tree', '--name-only', BASE, 'data/'], cwd=ROOT, text=True).split()
    return {r['org_id']: r for f in names if re.fullmatch(r'data/organizations_[A-Za-z]+\.csv', f) for r in git_rows(f)}


def domain(u):
    return urlparse(u if '//' in u else '//' + u).netloc.lower().removeprefix('www.')


def registrable(u):
    return '.'.join(domain(u).split('.')[-2:])  # shortcut: last two labels, so co.uk-style hosts compare loosely; upgrade if a record needs it


def verify_frame(frame):
    """The frame is recomputed from the merged batches' verdicts and compared with the ruling's own ID list (two routes): count, identity, prior hold classes,
    the four out-of-scope holds untouched."""
    assert len(frame) == F.EXPECTED, ('frame count changed', len(frame))
    assert frame == F.frame(), 'frame differs from the group holds recomputed from the merged batch verdicts'
    assert frame[:-1] == sorted(o for o in F.RULING_GROUP if o not in F.OUT_OF_SCOPE) and frame[-1] == F.MYRAVA, 'frame differs from the ruling ID list (M1 minus out-of-scope, plus Myrava)'
    held = F.prior_holds()
    assert all(held[o][0] == 'group_or_redirect_attribution' for o in frame[:-1]), 'a frame organization was not held as group_or_redirect_attribution'
    assert held[F.MYRAVA][0] == 'scope_owner_ruling', 'Myrava was not held for the tier-cap note'
    assert not set(F.OUT_OF_SCOPE) & set(frame), 'an out-of-scope organization is in the frame'


def verify(inputs, verdicts, frame=None, subjects=None):
    frame, subjects = frame or FRAME, SUBJECTS if subjects is None else subjects
    verify_frame(frame)
    base = base_orgs()
    vocab = json.loads((ROOT / 'docs/schema/vocab.json').read_text())['vocabularies']['MARKETS']['values']
    # input side, independently of the verdict table: frame orgs are blank at BASE, were not_adjudicated in MKT3, and hold a stored text page >= 1 KB
    mkt3_holds = {r['org_id']: r for r in read(MKT3 / 'holds.csv')}
    pages = [r for r in read(SNAPSHOT) if r['status'] == 'ok' and r['text_file']]
    for oid in frame:
        assert not base[oid]['markets_served'], ('frame org not blank at base', oid)
        assert mkt3_holds[oid]['hold_class'] == 'not_adjudicated', ('frame org was adjudicated by MKT3', oid)
        assert any(len((CORPUS / p['text_file']).read_text()) >= 1000 for p in pages if p['org_id'] == oid), ('no stored text page of 1 KB', oid)
    ids = [v['org_id'] for v in verdicts]
    assert sorted(ids) == sorted(frame) and len(set(ids)) == len(ids) == len(frame), 'frame ID with no verdict, or two'
    retired = {r['evidence_id'] for r in read(HERE / 'withdrawn.csv')}
    assert not retired & {r['evidence_id'] for r in inputs}, 'retired evidence ID reused'
    assert all(f'EVD-{FIRST_ID:06d}' <= i <= f'EVD-{LAST_ID}' for i in retired), 'retired ID outside the block'
    base_max = max(r['evidence_id'] for n in subprocess.check_output(['git', 'ls-tree', '--name-only', BASE, 'data/'], cwd=ROOT, text=True).split()
                   if re.fullmatch(r'data/evidence_[A-Za-z_]+\.csv', n) for r in git_rows(n))
    assert min((r['evidence_id'] for r in inputs), default='EVD-999999') > base_max, ('new evidence ID not above the merge-base maximum', base_max)
    seen = set()
    for r in inputs:
        assert not (r['value'] == 'automotive_unspecified' and re.search(WORDS['automotive_oem'], r['quote'], re.I)), 'automotive_unspecified on OEM or Tier 1 wording'
        key = (r['org_id'], r['value'])
        assert key not in seen, 'duplicate proposal'
        seen.add(key)
        org = base[r['org_id']]
        assert r['org_id'] in frame and r['field'] == 'markets_served' and not org['markets_served'], 'nonblank or outside frame'
        assert not re.search(r'carbon|graphite', ' '.join([org['legal_name'], org['notes']]), re.I), ('carbon/graphite or do-not-promote record applied', r['org_id'])
        assert r['org_id'] in OWNER_M2 or not re.search(r'do not promote', org['notes'], re.I), ('carbon/graphite or do-not-promote record applied', r['org_id'])  # M2 rules Myrava's note caps the tier only
        assert r['org_id'] not in OWNER_M2 or org['verification_tier'] == 'C', 'the M2 record tier changed'
        assert r['value'] in vocab, 'off vocabulary'
        assert r['value'] in WORDS and re.search(WORDS[r['value']], re.sub(re.escape(org['legal_name']), '', r['quote'], flags=re.I), re.I), ('tag wording absent from quote', r['value'])
        raw, text, recorded = locate(r['org_id'], r['source_kind'], r['source_url'])
        assert r['raw_sha256'] == recorded == sha(raw), 'raw hash mismatch'
        page = text.read_text()
        assert sha(text) == r['text_sha256'], 'text hash mismatch'  # bytes of the stored file, not read_text() output
        assert found(page, r['quote']), 'quote absent'
        assert not witness_class.nav_only(raw.read_text(errors='replace'), r['quote']), 'nav menu witness'
        assert not witness_class.article_url(r['source_url']), 'article source witness'
        parent = base.get(org['parent_org_id'])
        # M1: a group page counts only where it names the record, its brand or its plant as the subject of the claim (the subject names are in subjects.csv with their basis)
        assert not (parent and domain(parent['website']) == domain(r['source_url'])) or r['org_id'] in subjects, 'group domain witness'
        if r['org_id'] in subjects:
            assert any(found(r['quote'], n) for n in subjects[r['org_id']]), ('the quote does not name the subsidiary, its brand or its plant (group-wide claim)', r['org_id'])
        assert registrable(r['source_url']) == registrable(org['website']), ('source domain differs from the record website', r['org_id'])
        assert r['tier_effect'] == ('supports_U' if org['verification_tier'] == 'U' else 'supports_A'), 'strength'
    applied = {r['org_id'] for r in inputs}
    for v in verdicts:
        assert v['read_basis'] in READ_BASES, 'read basis missing'
        if v['org_id'] in applied:
            assert v['verdict'] == 'VERIFIED', 'applied org not VERIFIED'
        else:
            assert v['verdict'] == 'STILL_UNCERTAIN' and v['hold_class'] in HOLD_CLASSES, 'hold without verdict class'
            assert v['settling_fact'].strip(), 'hold without settling fact'
            assert len(v['settling_fact'].split()) >= 8, 'settling fact does not name the missing claim'
    expected = {o: ';'.join(sorted(r['value'] for r in inputs if r['org_id'] == o)) for o in frame}
    for v in verdicts:
        assert v['values'] == expected[v['org_id']], ('verdict values differ from the inputs', v['org_id'])  # holds must be empty
    assert applied <= set(frame) and {v['org_id'] for v in verdicts if v['verdict'] == 'VERIFIED'} == applied, 'verdict/applied mismatch'
    assert inputs == proposals({o: base[o]['verification_tier'] for o in frame}), 'selection mismatch'


def cell_writes(before, after, values):
    """Every changed organization row differs only in a blank markets_served cell, and only for a proposed org."""
    changed = 0
    for oid, a in after.items():
        b = before[oid]
        if a == b:
            continue
        diff = {k for k in a if a[k] != b[k]}
        assert diff == {'markets_served'}, ('write outside markets_served', oid, diff)
        assert not b['markets_served'], ('write to a non-blank cell', oid)
        assert oid in values and a['markets_served'] == ';'.join(sorted(values[oid])), ('unproposed write', oid)
        changed += 1
    assert changed == len(values), 'application yield'
    return changed


def derived_evidence(inputs, tiers):
    """Every applied evidence row, rebuilt from inputs.csv and the stored page bytes (sha256 recomputed here), never from the editable evidence packet."""
    out = []
    for r in inputs:
        raw, _, _ = locate(r['org_id'], r['source_kind'], r['source_url'])
        out.append(dict(evidence_id=r['evidence_id'], record_table='organizations', record_id=r['org_id'], claim_type='activity',
                        claim_detail=f'markets_served {r["value"]}: "{r["quote"]}"', source_class='own_site', source_ref=r['source_url'],
                        observed_date='2026-11-18', tier_effect='supports_U' if tiers[r['org_id']] == 'U' else 'supports_A',
                        created_by='claude atlas-w19-mktfollow', notes='Own-company source; field witness retained, SHA256 ' + sha(raw)))
    return out


def packet_matches(packet, derived):
    assert packet == derived, 'evidence packet differs from the rows derived from inputs.csv and the stored pages'


def evidence_delta(before, after, add):
    """The canonical shard is the base rows plus exactly the derived rows, every field equal (source_class, date, digest note, strength)."""
    assert not {r['evidence_id'] for r in add} & {r['evidence_id'] for r in before}, 'reused evidence ID'
    assert after == sorted(before + add, key=lambda r: r['evidence_id']), 'evidence delta mismatch (a field differs from the value derived from inputs.csv and the stored page)'


def boundary(inputs, evidence):
    values = {}
    for r in inputs:
        values.setdefault(r['org_id'], []).append(r['value'])
    before_o = base_orgs()
    after_o = {r['org_id']: r for p in shards() for r in read(p)}
    assert set(before_o) == set(after_o), 'organization rows added or removed'
    cells = cell_writes(before_o, after_o, values)
    new_evs, home = 0, {r['org_id']: p.name for p in shards() for r in read(p)}
    for p in sorted((ROOT / 'data').glob('*.csv')):
        if p.name.endswith('_all.csv') or p.name.startswith('organizations_'):
            continue
        before, after = git_rows(f'data/{p.name}'), read(p)
        if p.name.startswith('evidence_organizations_'):
            add = [r for r in evidence if home[r['record_id']].replace('organizations_', 'evidence_organizations_') == p.name]
            evidence_delta(before, after, add)
            new_evs += len(add)
        else:
            assert before == after, ('out of scope data change', p.name)
    assert new_evs == len(evidence), 'evidence yield'
    print('BOUNDARY PASS:', cells, 'market cells;', new_evs, 'new evidence rows; all other data unchanged')


def builder_tests(inputs, evidence):
    """Interrupted write, occupied evidence ID, and scrub replay, on temporary copies only."""
    home = {r['org_id']: p.name for p in shards() for r in read(p)}
    org_shards = sorted({home[r['org_id']] for r in inputs})
    names = tuple(org_shards + [n.replace('organizations_', 'evidence_organizations_') for n in org_shards])
    assert 'organizations_OH.csv' in names, 'the truncation test below needs the OH shard in the packet'
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / 'data').mkdir()

        def reset(preoccupy=None):
            for n in names:
                (root / 'data' / n).write_bytes(subprocess.check_output(['git', 'show', f'{BASE}:data/{n}'], cwd=ROOT))
            if preoccupy:
                p = root / 'data/evidence_organizations_OH.csv'
                rows = read(p)
                rows.append(dict(rows[0], evidence_id=preoccupy, record_id='ORG-999999'))
                with p.open('w', newline='') as f:
                    w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
                    w.writeheader()
                    w.writerows(sorted(rows, key=lambda r: r['evidence_id']))

        def snapshot():
            return {n: (root / 'data' / n).read_bytes() for n in names}
        with patch.object(B, 'ROOT', root), patch.object(B, 'LIVE', root / 'backup'):
            reset()
            before, original = snapshot(), csv.DictWriter.writerows

            def cut(writer, rows):
                original(writer, list(rows)[:100])
                raise OSError('interrupted')
            try:
                with patch.object(csv.DictWriter, 'writerows', cut):
                    B.apply(inputs, evidence)
            except OSError:
                pass
            else:
                raise AssertionError('silent pass: interrupted write')
            assert snapshot() == before, 'interrupted write damaged a shard'
            B.apply(inputs, evidence)  # retry succeeds from the intact state
            B.apply(inputs, evidence)  # replay is a no-op
            assert all(not (root / 'data' / n).with_name(n + '.tmp').exists() for n in names), 'temp sibling left behind'
            print('REFUSED: interrupted write leaves shards intact; retry and replay succeed')
            reset()
            B.apply(inputs, evidence)
            final = snapshot()
            by_org = {}
            for e in evidence:
                by_org.setdefault(e['record_id'], set()).add(e['evidence_id'])
            real_replace = B.os.replace
            canonical = {root / 'data' / n for n in names}

            def unbacked_after_interruptions():
                """Interrupt at every canonical destination write (staging replacements inside append_sorted are not counted) and list any market cell published without its rows."""
                leaks = []
                for k in range(1, len(names) + 1):
                    reset()
                    seen = []

                    def cut_replace(src, dst, _k=k):
                        if Path(dst) in canonical:
                            seen.append(dst)
                            if len(seen) == _k:
                                raise OSError('interrupted between canonical replacements')
                        return real_replace(src, dst)
                    try:
                        with patch.object(B.os, 'replace', cut_replace):
                            B.apply(inputs, evidence)
                    except OSError:
                        pass
                    else:
                        raise AssertionError('silent pass: interruption at canonical write %d' % k)
                    have = {r['evidence_id'] for n in names if n.startswith('evidence_') for r in read(root / 'data' / n)}
                    for n in names:
                        if n.startswith('organizations_'):
                            for r in read(root / 'data' / n):
                                if r['org_id'] in by_org and r['markets_served'] and not by_org[r['org_id']] <= have:
                                    leaks.append((k, r['org_id']))
                    B.apply(inputs, evidence)  # retry
                    assert snapshot() == final, 'retry after an interruption did not reproduce the canonical shards'
                return leaks
            assert not unbacked_after_interruptions(), 'a market cell was published without its evidence rows'
            # injection (Codex round 2): an unsafe order, one organization shard written before its own evidence shard, must be detected
            src = inspect.getsource(B.apply)
            old_key = "key=lambda p: (not p.name.startswith('evidence_'), p.name)"
            assert src.count(old_key) == 1, 'write-order line not found'
            eo, oo = sorted(n for n in names if n.startswith('evidence_')), sorted(n for n in names if n.startswith('organizations_'))
            assert len(eo) >= 2, 'the unsafe-order injection needs two shards'
            unsafe = [eo[0], oo[-1]] + eo[1:] + oo[:-1]
            original_apply = B.apply
            try:
                exec(src.replace(old_key, 'key=lambda p: ' + repr(unsafe) + '.index(p.name)'), B.__dict__)
                leaks = unbacked_after_interruptions()
            finally:
                B.apply = original_apply
            assert leaks, 'silent pass: the unsafe write order was not detected'
            print('REFUSED: unsafe write order (an organization shard before its own evidence shard) is detected by the canonical-write interruption test')
            print('REFUSED: interruption between canonical replacements (every position): no cell without its evidence rows; retry reproduces the shards')
            reset(preoccupy=evidence[0]['evidence_id'])
            before = snapshot()
            try:
                B.apply(inputs, evidence)
            except AssertionError as e:
                assert 'occupied' in str(e), str(e)
            else:
                raise AssertionError('silent pass: occupied evidence ID')
            assert snapshot() == before, 'a market cell was written despite an occupied ID'
            print('REFUSED: occupied evidence ID (no market cell written)')
            shutil.rmtree(root / 'backup', ignore_errors=True)
            backups = root / 'backup' / f'pre-application-batch{B.BATCH}-{B.BASE}'

            def base_blob(n):
                return subprocess.check_output(['git', 'show', f'{BASE}:data/{n}'], cwd=ROOT)

            def backups_are_base():
                for n in names:
                    if (backups / n).exists():
                        assert (backups / n).read_bytes() == base_blob(n), ('a backup differs from the merge-base bytes', n)
            for n in ('organizations_OH.csv', 'evidence_organizations_OH.csv'):  # truncated input shard: one row removed
                reset()
                p = root / 'data' / n
                lines = p.read_bytes().split(b'\n')
                p.write_bytes(b'\n'.join(lines[:5] + lines[6:]))  # drop one data row (the 4th)
                before = snapshot()
                try:
                    B.apply(inputs, evidence)
                except AssertionError as e:
                    assert 'differs from base' in str(e), str(e)
                else:
                    raise AssertionError('silent pass: truncated ' + n)
                assert snapshot() == before, 'a shard changed despite a truncated input'
                backups_are_base()  # a refused apply must not leave a truncated backup
                reset()
                B.apply(inputs, evidence)  # restore the input and retry
                backups_are_base()
                assert all((backups / m).exists() for m in names if (root / 'data' / m).read_bytes() != subprocess.check_output(['git', 'show', f'{BASE}:data/{m}'], cwd=ROOT)), 'a changed shard has no backup'
                shutil.rmtree(backups, ignore_errors=True)
            print('REFUSED: truncated input shard (organization and evidence), nothing replaced')
            # Codex round 3 probes: a stale-base backup and a 128-byte truncated backup are never trusted; they are rewritten from the merge-base blob
            for label, corrupt in (('stale base', lambda n: subprocess.check_output(['git', 'show', f'e1df30e4:data/{n}'], cwd=ROOT)),
                                   ('128-byte truncated backup', lambda n: base_blob(n)[:128])):
                reset()
                shutil.rmtree(backups, ignore_errors=True)
                backups.mkdir(parents=True)
                for n in names:
                    (backups / n).write_bytes(corrupt(n))
                B.apply(inputs, evidence)
                backups_are_base()
                sums = json.loads((backups / 'SHA256SUMS.json').read_text())
                assert set(sums) == set(names), ('manifest key set is not the four packet shards', sorted(sums))
                for n in sums:
                    assert sums[n]['sha256'] == hashlib.sha256((backups / n).read_bytes()).hexdigest() == hashlib.sha256(base_blob(n)).hexdigest(), ('backup manifest', n)
                    assert sums[n]['base'] == BASE
                shutil.rmtree(backups, ignore_errors=True)
                print('REFUSED: ' + label + ' backup is not trusted (rewritten from the merge-base blob, sha256 recorded)')
            # Codex round 4 probes: every apply and retry verifies and records all four packet-shard backups, whether or not a shard still needs a data write
            def manifest_is_exact():
                sums = json.loads((backups / 'SHA256SUMS.json').read_text())
                assert set(sums) == set(names), ('manifest key set is not the four packet shards', sorted(sums))
                for n in names:
                    want = hashlib.sha256(base_blob(n)).hexdigest()
                    assert sums[n]['sha256'] == want == hashlib.sha256((backups / n).read_bytes()).hexdigest() and sums[n]['base'] == BASE, ('backup or manifest entry wrong', n)
            reset()
            shutil.rmtree(backups, ignore_errors=True)
            B.apply(inputs, evidence)
            manifest_is_exact()
            B.apply(inputs, evidence)  # replay after success: nothing needs a data write, all four backups are still verified and recorded
            manifest_is_exact()
            (backups / 'organizations_OH.csv').write_bytes(base_blob('organizations_OH.csv')[:128])
            B.apply(inputs, evidence)  # third apply with a 128-byte backup: rewritten from the blob
            manifest_is_exact()
            print('REFUSED: replay after success and a damaged backup on the third apply (all four backups verified and recorded each time)')
            reset()
            shutil.rmtree(backups, ignore_errors=True)
            canonical_first = []
            real_replace_b = B.os.replace

            def cut_first_evidence(src, dst):
                if Path(dst) in {root / 'data' / m for m in names}:
                    canonical_first.append(dst)
                    if len(canonical_first) == 2:  # after the first canonical evidence write, before the second
                        raise OSError('interrupted after the first canonical evidence write')
                return real_replace_b(src, dst)
            try:
                with patch.object(B.os, 'replace', cut_first_evidence):
                    B.apply(inputs, evidence)
            except OSError:
                pass
            else:
                raise AssertionError('silent pass: interruption after the first canonical evidence write')
            B.apply(inputs, evidence)  # retry
            manifest_is_exact()
            assert snapshot() == final, 'retry after the first canonical evidence write did not reproduce the shards'
            print('REFUSED: retry after the first canonical evidence write (manifest holds all four shards; shards reproduced)')
            shutil.rmtree(backups, ignore_errors=True)
    with tempfile.TemporaryDirectory() as td:  # scrub: purge then a lookup must refetch, not raise
        c = fetch.Corpus(td)
        url = 'https://example.test/page'
        r = c.save(url, dict(raw=b'<html><body>Sales: jane.doe@example.test a long enough page body about nothing in particular</body></html>',
                             code=200, content_type='text/html', exit=0), 'ok', url, 'direct')
        assert fetch.scrub(c, r, url), 'scrub missed a personal address'
        assert c.cached(url) is None and not any(row['url'] == url for row in csv.DictReader((Path(td) / 'index.csv').open())), 'scrub left a record behind'
        print('REFUSED: scrub leaves no per-URL record or index row')


def renumber_replay_test():
    """A renumber replay must change nothing: the second run is refused (its source IDs are already inside the allocated block) and the file is untouched."""
    old_first = 396750
    original = (HERE / 'selection.tsv').read_text()
    lines = [l.split('\t') for l in original.splitlines()]
    for l in lines:
        l[2] = ';'.join(f'EVD-{int(i[4:]) - FIRST_ID + old_first:06d}' for i in l[2].split(';'))
    with tempfile.TemporaryDirectory() as td, patch.object(B, 'HERE', Path(td)):
        p = Path(td) / 'selection.tsv'
        p.write_text('\n'.join('\t'.join(l) for l in lines) + '\n')
        import contextlib
        import io as _io
        with contextlib.redirect_stdout(_io.StringIO()):
            B.renumber(old_first, FIRST_ID)
        assert p.read_text() == original, 'renumber did not reproduce the allocated IDs'
        try:
            with contextlib.redirect_stdout(_io.StringIO()):
                B.renumber(old_first, FIRST_ID)
        except AssertionError as e:
            assert 'already converted' in str(e), str(e)
        else:
            raise AssertionError('silent pass: renumber replay')
        assert p.read_text() == original, 'a refused renumber replay changed the file'
    print('REFUSED: renumber replay (source IDs already inside the allocated block); the selection is unchanged')


def main():
    packet_only = '--packet-only' in sys.argv  # data/ not yet written: skip the boundary and application-state checks, loudly
    inputs, verdicts = read(HERE / 'inputs.csv'), read(HERE / 'verdicts.csv')
    verify(inputs, verdicts)
    first = inputs[0]['org_id']
    held = lambda v: next(x for x in v if x['verdict'] == 'STILL_UNCERTAIN')
    cases = [
        ('term not in the vocabulary', 'off vocabulary', lambda i, v: i[0].update(value='consumer_goods')),
        ('quote not found in its stored page', 'quote absent', lambda i, v: i[0].update(quote=i[0]['quote'] + ' fabricated violet elephant')),
        ('frame ID with no verdict', 'frame ID with no verdict', lambda i, v: v.pop()),
        ('frame ID with two verdicts', 'frame ID with no verdict, or two', lambda i, v: v.append(copy.deepcopy(v[0]))),
        ('hold with a blank settling fact', 'hold without settling fact', lambda i, v: held(v).update(settling_fact=' ')),
        ('tag broader than the words', 'tag wording', lambda i, v: i[0].update(value='aerospace_defense' if i[0]['value'] != 'aerospace_defense' else 'marine')),
        ('raw hash tampering', 'raw hash mismatch', lambda i, v: i[0].update(raw_sha256='0' * 64)),
        ('duplicate proposal', 'duplicate proposal', lambda i, v: i.append(i[0].copy())),
        ('text digest of the wrong bytes', 'text hash mismatch', lambda i, v: i[0].update(text_sha256='f' * 64)),
        ('tampered verdict value', 'verdict values differ', lambda i, v: next(x for x in v if x['org_id'] == first).update(values='aerospace_defense;marine')),
        ('value on a hold', 'verdict values differ', lambda i, v: held(v).update(values='aerospace_defense')),
        ('automotive_unspecified on OEM wording', 'automotive_unspecified on OEM', lambda i, v: next(x for x in i if re.search(WORDS['automotive_oem'], x['quote'], re.I)).update(value='automotive_unspecified')),
        ('new evidence ID not above the merge-base maximum', 'not above the merge-base maximum', lambda i, v: i[0].update(evidence_id='EVD-000001')),
        ('read basis missing', 'read basis missing', lambda i, v: v[0].update(read_basis='')),
        ('wrong tier effect for the record tier', 'strength', lambda i, v: i[0].update(tier_effect='supports_C' if i[0]['tier_effect'] == 'supports_A' else 'supports_A')),
    ]
    if read(HERE / 'withdrawn.csv'):
        cases.append(('retired evidence ID reused', 'retired evidence ID reused', lambda i, v: i[0].update(evidence_id=read(HERE / 'withdrawn.csv')[0]['evidence_id'])))
    for name, expect, mutate in cases:
        args = copy.deepcopy((inputs, verdicts))
        mutate(*args)
        try:
            verify(*args)
        except AssertionError as e:
            assert expect in str(e), ('refused for the wrong reason', name, str(e))
            print('REFUSED:', name)
        else:
            raise AssertionError('silent pass: ' + name)
    frame_cases = [  # frame-level injections: the recomputed frame and the packet frame must agree
        ('frame count change (one organization added)', 'frame count changed', lambda a: a + ['ORG-999999']),
        ('frame count change (one organization dropped)', 'frame count changed', lambda a: a[:-1]),
        ('frame order or identity change', 'frame differs', lambda a: a[:3] + [a[4], a[3]] + a[5:]),
        ('an out-of-scope organization swapped into the frame', 'frame differs', lambda a: a[:2] + ['ORG-000169'] + a[3:]),
    ]
    for name, expect, mutate in frame_cases:
        try:
            verify(inputs, verdicts, frame=mutate(list(FRAME)))
        except AssertionError as e:
            assert expect in str(e), ('refused for the wrong reason', name, str(e))
            print('REFUSED:', name)
        else:
            raise AssertionError('silent pass: ' + name)
    group_row = next(r for r in inputs if r['org_id'] in SUBJECTS)
    try:  # M1 injection: a group-wide claim attributed to a subsidiary (the quote does not name the subsidiary, its brand or its plant)
        verify(inputs, verdicts, subjects={**SUBJECTS, group_row['org_id']: ['Unrelated Group Name']})
    except AssertionError as e:
        assert 'does not name the subsidiary' in str(e), str(e)
        print('REFUSED: a group-wide claim attributed to a subsidiary (the page does not name the subsidiary, its brand or its plant)')
    else:
        raise AssertionError('silent pass: group-wide claim attributed to a subsidiary')
    base = base_orgs()
    attribution = [  # records patched in memory: a parent on the source domain (a record with no named subject); a different record website; do-not-promote; carbon; the Myrava tier
        ('group domain witness without a named subject', 'group domain witness', lambda b, o: b[o].update(parent_org_id='ORG-PARENT') or b.update({'ORG-PARENT': dict(b[o], website=b[o]['website'])}), F.MYRAVA),
        ('source domain differs from the record website', 'source domain differs', lambda b, o: b[o].update(website='https://unrelated-example.test/'), first),
        ('do-not-promote note on an applied record other than the M2 record', 'do-not-promote', lambda b, o: b[o].update(notes=b[o]['notes'] + ' Do not promote.'), first),
        ('carbon or graphite record applied', 'do-not-promote', lambda b, o: b[o].update(legal_name='Example Graphite Corp'), first),
        ('the Myrava tier changed (M2: the note caps the tier only)', 'the M2 record tier changed', lambda b, o: b[o].update(verification_tier='B'), F.MYRAVA),
    ]
    for name, expect, mutate, target in attribution:
        patched = copy.deepcopy(base)
        mutate(patched, target)
        with patch(__name__ + '.base_orgs', lambda: patched):
            try:
                verify(inputs, verdicts)
            except AssertionError as e:
                assert expect in str(e), ('refused for the wrong reason', name, str(e))
                print('REFUSED:', name)
            else:
                raise AssertionError('silent pass: ' + name)
    builder_tests(inputs, read(HERE / 'evidence_packet.csv'))
    renumber_replay_test()
    if packet_only:
        cells = {r['org_id']: r['markets_served'] for p in shards() for r in read(p)}
        assert not any(cells[o] for o in {r['org_id'] for r in inputs}), 'packet-only mode but a frame cell is already written: run check.py without --packet-only'
        print('PACKET ONLY: data/ is not written; boundary and counts-after-application checks were skipped')
    # a write to a non-blank cell, and a write to any other column, on the real organization rows
    values = {}
    for r in inputs:
        values.setdefault(r['org_id'], []).append(r['value'])
    before, after = base_orgs(), {r['org_id']: r for p in shards() for r in read(p)}
    for name, expect, mutate in [('write to a non-blank cell', 'non-blank cell', lambda b, a: b[next(iter(values))].update(markets_served='aerospace_defense')),
                                 ('write to the Myrava tier (M2)', 'outside markets_served', lambda b, a: a[F.MYRAVA].update(verification_tier='B')),
                                 ('write to another column', 'outside markets_served', lambda b, a: a[next(iter(values))].update(notes='edited'))]:
        b, a = copy.deepcopy(before), copy.deepcopy(after)
        mutate(b, a)
        try:
            cell_writes(b, a, values)
        except AssertionError as e:
            assert expect in str(e), ('refused for the wrong reason', name, str(e))
            print('REFUSED:', name)
        else:
            raise AssertionError('silent pass: ' + name)
    tiers = {o: base[o]['verification_tier'] for o in base}
    expected = counts_for(tiers, inputs, verdict_rows(inputs))
    assert json.loads((HERE / 'counts.json').read_text()) == expected, 'counts.json stale'
    evidence = derived_evidence(inputs, tiers)
    packet_matches(read(HERE / 'evidence_packet.csv'), evidence)
    assert len(evidence) == expected['applied_values']
    assert all(f'EVD-{FIRST_ID:06d}' <= e['evidence_id'] <= f'EVD-{LAST_ID}' for e in evidence), 'evidence ID outside block'
    # falsified provenance, in the packet and in the canonical shard, must both be refused
    home_shard = {r['org_id']: p.name for p in shards() for r in read(p)}
    first_shard = home_shard[inputs[0]['org_id']].replace('organizations_', 'evidence_organizations_')
    base_ev = git_rows(f'data/{first_shard}')
    mine = [e for e in evidence if home_shard[e['record_id']].replace('organizations_', 'evidence_organizations_') == first_shard]
    good = sorted(base_ev + mine, key=lambda r: r['evidence_id'])
    evidence_delta(base_ev, good, mine)
    for field, bad in [('source_class', 'government_filing'), ('observed_date', '2020-01-01'), ('notes', 'unsupported digest'), ('tier_effect', 'supports_C')]:
        forged = copy.deepcopy(good)
        next(r for r in forged if r['evidence_id'] == mine[0]['evidence_id'])[field] = bad
        try:
            evidence_delta(base_ev, forged, mine)
        except AssertionError as e:
            assert 'evidence delta mismatch' in str(e), str(e)
            print('REFUSED: falsified', field, 'in the canonical evidence shard')
        else:
            raise AssertionError('silent pass: falsified ' + field)
    forged_packet = copy.deepcopy(evidence)
    forged_packet[0]['source_class'] = 'government_filing'
    try:
        packet_matches(forged_packet, evidence)
    except AssertionError as e:
        assert 'evidence packet differs' in str(e), str(e)
        print('REFUSED: falsified source_class in the evidence packet (packet must equal the derived rows)')
    else:
        raise AssertionError('silent pass: falsified packet')
    if not packet_only:
        boundary(inputs, evidence)
    print('PASS:', json.dumps(expected))


if __name__ == '__main__':
    main()
