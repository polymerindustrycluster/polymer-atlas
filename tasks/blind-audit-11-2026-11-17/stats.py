"""Phase 3 statistics for blind audit 11 (adapted from blind audit 10): final grade per sampled record change, per-stratum and
design-weighted rates with Wilson intervals, the like-for-like content rate, corrections.
Unit: sampled record change (one row of sample.csv). Unresolved stays in every denominator and is never agreement.
A row is AGREE only when both reviewers said AGREE; every other row needs the lead's adjudication (disagreements and agreed
non-AGREE verdicts alike). The one exception is the controller-directed lead check of the both-AGREE band rows (2026-11-17):
those carry an adjudication with lead_check=True, and its grade is final.
Run: python3 stats.py   (writes final_grades.csv and statistics.json from sample.csv, verdicts_a/b.csv and adjudication.json)"""
import csv, json, math
from collections import Counter
from pathlib import Path
import frame as F

H = Path(__file__).resolve().parent
GRADES = ('AGREE', 'FIELD_ERROR', 'CREATION_ERROR', 'UNRESOLVED')
Z = 1.959964
NOT_CONTENT = ('archive_links', 'zips', 'navigation_links')  # controller ruling 2026-11-17: the content rate leaves these out, for comparison with A10
READABLE_MAX_UPPER = 0.25  # a sampled stratum is "too small to read" when its Wilson upper bound at zero errors exceeds this (n < 12)
read = lambda p: list(csv.DictReader((H / p).open(newline='')))
decisions = lambda: json.loads((H / 'adjudication.json').read_text())['decisions']


def wilson(k, n, z=Z):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 6), round(min(1.0, c + h), 6)]


def final_grades():
    a, b = ({r['blind_id']: r for r in read(f'verdicts_{k}.csv')} for k in 'ab')
    adj = {e['id']: e for e in decisions()}
    out = []
    for s in read('sample.csv'):
        i = s['blind_id']
        assert a[i]['record_id'] == b[i]['record_id'] == s['record_id'], i
        if a[i]['verdict'] == b[i]['verdict'] == 'AGREE' and i not in adj:
            grade, how = 'AGREE', 'both reviewers'
        elif a[i]['verdict'] == b[i]['verdict'] == 'AGREE':
            assert adj[i].get('lead_check') and s['change_class'] == 'bands', f'{i} agreed AGREE but has an adjudication that is not a band lead check'
            grade, how = adj[i]['grade'], 'both reviewers, then lead check (PPP ruling)'
        else:
            assert i in adj and adj[i]['reviewer_a'] == a[i]['verdict'] and adj[i]['reviewer_b'] == b[i]['verdict'], f'{i} not adjudicated'
            grade, how = adj[i]['grade'], 'lead adjudication'
        out.append(dict(blind_id=i, change_class=s['change_class'], table=s['table'], record_id=s['record_id'], prs=s['prs'],
                        reviewer_a=a[i]['verdict'], reviewer_b=b[i]['verdict'], final_grade=grade, decided_by=how))
    assert len(out) == len({r['blind_id'] for r in out}) == 120 and set(adj) <= {r['blind_id'] for r in out}
    return out


def weighted(strata, n_rows):
    """Design-weighted rates over the given strata, with the Wilson interval at the Kish effective sample size (an approximation)."""
    N = sum(r['population'] for r in strata)
    w = [r['design_weight'] for r in strata for _ in range(r['sampled'])]
    n_eff = sum(w) ** 2 / sum(x * x for x in w)
    pt = {g: sum(r['population'] * r[g] / r['sampled'] for r in strata) / N for g in GRADES}
    err = pt['FIELD_ERROR'] + pt['CREATION_ERROR']
    return dict(frame_record_changes=N, sampled=n_rows, point=pt, confirmed_error=err, kish_effective_n=n_eff,
                confirmed_error_wilson95_at_effective_n=wilson(err * n_eff, n_eff) if err else [0.0, wilson(0, round(n_eff))[1]],
                unresolved_counted_as_errors=err + pt['UNRESOLVED'])


def summarize(sample, final):
    by = {r['blind_id']: r['final_grade'] for r in final}
    assert {r['blind_id'] for r in sample} == set(by) and len(sample) == len(by) == len(final) == 120, 'incomplete, duplicated or wrong verdict census'
    strata = []
    for cl in F.CLASSES:
        rows = [r for r in sample if r['change_class'] == cl]
        N, n = int(rows[0]['stratum_N']), len(rows)
        assert n == int(rows[0]['stratum_n'])
        c = Counter(by[r['blind_id']] for r in rows)
        census = n == N
        k = c['FIELD_ERROR'] + c['CREATION_ERROR']
        row = dict(change_class=cl, population=N, sampled=n, design_weight=N / n, census=census, **{g: c[g] for g in GRADES},
                   confirmed_error=k, confirmed_error_rate=k / n, confirmed_error_wilson95=None if census else wilson(k, n),
                   unresolved_rate=c['UNRESOLVED'] / n,
                   readable='census (exact count of every record change)' if census else ('yes' if wilson(0, n)[1] <= READABLE_MAX_UPPER else 'too small to read'))
        strata.append(row)
    content = [r for r in strata if r['change_class'] not in NOT_CONTENT]
    tot = Counter(by.values())
    return dict(unit='sampled record change', sample_record_changes=120, frame_record_changes=sum(r['population'] for r in strata), strata=strata,
                unweighted_counts={g: tot[g] for g in GRADES},
                overall_weighted=weighted(strata, 120),
                content_weighted=dict(weighted(content, sum(r['sampled'] for r in content)), excludes=list(NOT_CONTENT),
                                      note='like-for-like with blind audit 10 (4.6%): record content only, without archive links, ZIP fills and navigation links'),
                readable_max_upper_at_zero_errors=READABLE_MAX_UPPER)


def corrections(adj):
    return [dict(blind_id=e['id'], record_id=e['record_id'], change_class=e['change_class'], field=e['fields'], current_value=e['current_value'],
                 correct_value=e['correct_value'], sources=[r['url'] for r in e['receipts'] if r.get('quote') or r.get('raw_re')], rationale=e['key_fact'])
            for e in adj if e['grade'] in ('FIELD_ERROR', 'CREATION_ERROR')]


def main():
    final = final_grades()
    sample = read('sample.csv')
    adj = decisions()
    res = summarize(sample, final)
    a, b = ({r['blind_id']: r['verdict'] for r in read(f'verdicts_{k}.csv')} for k in 'ab')
    res.update(reviewer_a_counts=dict(Counter(a.values())), reviewer_b_counts=dict(Counter(b.values())),
               cross_tab={f'A {x} / B {y}': n for (x, y), n in sorted(Counter((a[i], b[i]) for i in a).items())},
               final_counts={g: sum(1 for r in final if r['final_grade'] == g) for g in GRADES}, corrections=corrections(adj),
               uei_rows=dict(Counter(r['final_grade'] for r in final if r['change_class'] == 'uei_links')))  # R-SAM: counts only
    with (H / 'final_grades.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(final[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(final)
    (H / 'statistics.json').write_text(json.dumps(res, indent=1, sort_keys=True) + '\n')
    print(res['final_counts'], res['cross_tab'])


if __name__ == '__main__':
    assert wilson(0, 20) == [0, 0.161125] and wilson(20, 20) == [0.838875, 1] and wilson(10, 20) == [0.299298, 0.700702]  # known answers
    main()
