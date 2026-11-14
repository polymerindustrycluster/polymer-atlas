"""Phase 3 statistics for blind audit 10: final grade per sampled record, per-stratum and weighted rates, Wilson intervals, corrections.
Unit: sampled record (one row of sample.csv). Unresolved stays in every denominator and is never agreement.
Run: python3 stats.py   (writes final_grades.csv and statistics.json from sample.csv, verdicts_a/b.csv and adjudication.json)"""
import csv, json, math, subprocess
from collections import Counter
from pathlib import Path
import frame as F

H = Path(__file__).resolve().parent
GRADES = ('AGREE', 'FIELD_ERROR', 'CREATION_ERROR', 'UNRESOLVED')
Z = 1.959964
read = lambda p: list(csv.DictReader((H / p).open(newline='')))


def wilson(k, n, z=Z):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 6), round(min(1.0, c + h), 6)]


def final_grades():
    a, b = ({r['blind_id']: r for r in read(f'verdicts_{k}.csv')} for k in 'ab')
    adj = {e['id']: e for e in json.loads((H / 'adjudication.json').read_text())}
    out = []
    for s in read('sample.csv'):
        i = s['blind_id']
        assert a[i]['record_id'] == b[i]['record_id'] == s['record_id']
        if a[i]['verdict'] == b[i]['verdict']:
            assert i not in adj, f'{i} agreed but has an adjudication'
            assert a[i]['verdict'] == 'AGREE', f'{i}: both reviewers gave {a[i]["verdict"]}, not handled'
            grade, how = 'AGREE', 'both reviewers'
        else:
            assert i in adj and adj[i]['reviewer_a'] == a[i]['verdict'] and adj[i]['reviewer_b'] == b[i]['verdict'], f'{i} disagreement not adjudicated'
            grade, how = adj[i]['grade'], 'lead adjudication'
        out.append(dict(blind_id=i, table=s['table'], record_id=s['record_id'], prs=s['prs'], reviewer_a=a[i]['verdict'], reviewer_b=b[i]['verdict'], final_grade=grade, decided_by=how))
    assert len(out) == len({r['record_id'] for r in out}) == 50 and len(adj) == 14
    return out


def summarize(sample, final):
    by = {r['record_id']: r['final_grade'] for r in final}
    assert {r['record_id'] for r in sample} == set(by) and len(sample) == len(by) == len(final) == 50, 'incomplete, duplicated or wrong verdict census'
    strata, tot = [], Counter()
    for t in F.TABLES:
        rows = [r for r in sample if r['table'] == t]
        if not rows:
            continue
        N, n = int(rows[0]['stratum_N']), len(rows)
        assert n == int(rows[0]['stratum_n'])
        c = Counter(by[r['record_id']] for r in rows)
        tot.update(c)
        census = n == N
        row = dict(table=t, population_records=N, sampled_records=n, inclusion_probability=n / N, design_weight=N / n, census=census)
        for g in GRADES:
            row[g] = c[g]
            row[g + '_rate'] = c[g] / n
            row[g + '_wilson95'] = None if census else wilson(c[g], n)
        k = c['FIELD_ERROR'] + c['CREATION_ERROR']
        row.update(confirmed_error=k, confirmed_error_rate=k / n, confirmed_error_wilson95=None if census else wilson(k, n))
        strata.append(row)
    N_all = sum(r['population_records'] for r in strata)
    k_all = tot['FIELD_ERROR'] + tot['CREATION_ERROR']
    weights = [r['design_weight'] for r in strata for _ in range(r['sampled_records'])]
    n_eff = sum(weights) ** 2 / sum(w * w for w in weights)  # Kish effective sample size
    wt = {g: sum(r['population_records'] * r[g + '_rate'] for r in strata) / N_all for g in GRADES}
    w_err = wt['FIELD_ERROR'] + wt['CREATION_ERROR']
    return dict(unit='sampled record', sample_records=50, frame_records=N_all, strata=strata, unweighted_counts={g: tot[g] for g in GRADES},
                unweighted_rates={g: tot[g] / 50 for g in GRADES}, unweighted_confirmed_error=dict(count=k_all, rate=k_all / 50, wilson95=wilson(k_all, 50)),
                unweighted_note='simple pooled counts; the sample over-represents small strata (census sites and organizations), so use the weighted estimate for the frame',
                weighted_to_frame=dict(point=wt, confirmed_error_point=w_err, kish_effective_n=n_eff, confirmed_error_wilson95_at_effective_n=wilson(w_err * n_eff, n_eff) if w_err else [0.0, wilson(0, round(n_eff))[1]],
                                       note='design-weighted estimate for the 1,621-record frame; the interval is the Wilson interval at the Kish effective sample size, an approximation'),
                sensitivity_weighted=dict(confirmed_only=w_err, unresolved_counted_as_errors=w_err + wt['UNRESOLVED']))


def corrections(adj):
    return [dict(blind_id=e['id'], record_id=e['record_id'], field=e['fields'], current_value=e['current_value'], correct_value=e['correct_value'],
                 sources=[r['url'] for r in e['receipts'] if r.get('quote') or r.get('raw_re')], rationale=e['rationale']) for e in adj if e['grade'] in ('FIELD_ERROR', 'CREATION_ERROR')]


def leads():
    """Unsampled, read-only: rows at the pinned HEAD sharing the confirmed-wrong value. No rate claim (AGENTS 7)."""
    ep = F.rows_at(F.HEAD, 'data/event_participation.csv')
    same = [r['participation_id'] for r in ep if r['event_id'] == 'EVT-000046' and r['edition_year'] == '2026' and r['edition_dates'] == '2026-09-28 to 2026-10-01']
    return dict(event_participation_rows_with_the_TPO_2026_end_date_2026_10_01=same, note='rows at HEAD 4ecc7cf (including the sampled one) with the same edition_dates value as the confirmed error; the rest are unsampled, a lead for the controller and not a measured rate')


MAIN_SHA = '304f50ed3060c1f1c1208402a4f76f46c69156a2'  # origin/main after #330, checked 2026-11-14


def repo_facts():
    """Repo facts the report states, recomputed at the pinned HEAD (reviewer A's copies came from a stale checkout)."""
    eco = F.rows_at(F.HEAD, 'data/ecosystem.csv')
    schema = subprocess.check_output(['git', 'show', f'{F.HEAD}:docs/SCHEMA.md'], cwd=F.ROOT).decode()
    s42 = schema.split('### 4.2 Status vocabulary')[1].split('### 4.3')[0]
    return dict(nonohio_university_polymer_program_false_rows=sum(1 for r in eco if r['ecosystem_subtype'] == 'university_college' and r['state'] != 'OH' and r['polymer_program'] == 'false'),
                schema_4_2_status_vocabulary_has_relocated_in_scope='relocated_in_scope' in s42,
                schema_v1_13_dated_2026_11_12_adds_fiber_formation='v1.13 \u2014 2026-11-12' in schema and '`fiber_formation`' in schema)


def main_recheck():
    """The two confirmed corrections' current values, re-read on the later main (#330 merged after the pin)."""
    ep = {r['participation_id']: r for r in F.rows_at(MAIN_SHA, 'data/event_participation.csv')}
    pg = {r['program_id']: r for r in F.rows_at(MAIN_SHA, 'data/programs.csv')}
    return dict(main_sha=MAIN_SHA, EVP_001297_edition_dates=ep['EVP-001297']['edition_dates'], PROG_000314_url=pg['PROG-000314']['url'],
                PROG_000314_public_door_url=pg['PROG-000314']['public_door_url'], PROG_000314_description_has_michigan='Michigan' in pg['PROG-000314']['description_1line'])


def main():
    final = final_grades()
    sample = read('sample.csv')
    adj = json.loads((H / 'adjudication.json').read_text())
    res = summarize(sample, final)
    a, b = ({r['blind_id']: r['verdict'] for r in read(f'verdicts_{k}.csv')} for k in 'ab')
    res.update(reviewer_a_counts=dict(Counter(a.values())), reviewer_b_counts=dict(Counter(b.values())),
               cross_tab={f'A {x} / B {y}': n for (x, y), n in sorted(Counter((a[i], b[i]) for i in a).items())},
               final_counts={g: sum(1 for r in final if r['final_grade'] == g) for g in GRADES}, corrections=corrections(adj), leads=leads(), repo_facts=repo_facts(), main_recheck=main_recheck())
    with (H / 'final_grades.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(final[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(final)
    (H / 'statistics.json').write_text(json.dumps(res, indent=1, sort_keys=True) + '\n')
    print(res['final_counts'], res['cross_tab'])


if __name__ == '__main__':
    assert wilson(0, 20) == [0, 0.161125] and wilson(20, 20) == [0.838875, 1] and wilson(10, 20) == [0.299298, 0.700702]  # known answers
    main()
