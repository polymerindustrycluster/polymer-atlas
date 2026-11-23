"""Blind audit 12: sample sizes, acceptance numbers and the pre-registered two-stage rule. Stdlib only.

Everything in PROTOCOL.md section 7 is computed here, not typed. Unit: sampled record; k = records graded wrong.
The bound is the two-sided 95% Wilson interval's upper end, z = 1.959964 (the value audit 11's stats.py uses).

Run:  python3 sizes.py             print the tables
      python3 sizes.py --write     rewrite sizes.json (PROTOCOL.md quotes it; the selftest compares)
      python3 sizes.py --selftest  known answers, ruling reproduction, rule properties
"""
import json, math, sys
from math import comb
from pathlib import Path

H = Path(__file__).resolve().parent
Z = 1.959964
Z_EARLY = 2.326     # stage-1 early PASS needs the 99%-level bound, so the second look cannot inflate the false-pass chance
P_FUTILE = 0.02     # planning rate for the futility rule
FUTILE_BELOW = 0.05  # stop for futility when P(stage 2 passes | stage-1 errors, rate 2%) is below this
# Owner ruling 2026-11-23 round 17 (DECISIONS.md): effective n at an assumed true rate (continuous Wilson bound), quoted, then recomputed below.
RULING = {0.05: {0.02: 205, 0.03: 460}, 0.10: {0.02: 55, 0.03: 71}}  # DECISIONS.md says 'about 55 to 71' for 10%; it states no figure at 1%
BRIEF_FIGURE = {'target': 0.10, 'true_rate': 0.01, 'brief_n': 35}  # the lane brief's '35 at 1%': not in DECISIONS.md; 35 is the zero-error size
# Pre-registered plan. n1 = the ruling's size at 2% true error; n2 = the ruling's size at 3%. Battery item B-POWER may raise a 10% stratum's n2.
PLAN = {
    'PIC18_RECORDS':     dict(target=0.05, n1=205, n2=460),
    'REST_OHIO_RECORDS': dict(target=0.10, n1=55, n2=71),
    'REST_US_RECORDS':   dict(target=0.10, n1=55, n2=71),
    'RESEARCHERS':       dict(target=0.10, n1=55, n2=71),
    'PROGRAMS':          dict(target=0.10, n1=55, n2=71),
    'EVENTS':            dict(target=0.10, n1=55, n2=71),
}


def wilson_upper(k, n, z=Z):
    """Upper end of the Wilson interval; k may be fractional (continuous bound used for planning)."""
    p, d = k / n, 1 + z * z / n
    return min(1.0, ((p + z * z / (2 * n)) + z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / d)


def n_needed(p, target, z=Z):
    """Smallest n whose continuous Wilson upper bound at k = p*n is at most target (the ruling's 'effective records read')."""
    n = 2
    while wilson_upper(p * n, n, z) > target:
        n += 1
    return n


def accept_k(n, target, z=Z):
    """Largest whole error count whose Wilson upper bound is at most target; -1 when even zero errors fails."""
    k = -1
    while k + 1 <= n and wilson_upper(k + 1, n, z) <= target:
        k += 1
    return k


def cdf(n, k, p):
    return 0.0 if k < 0 else 1.0 if k >= n else sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def rule(n1, n2, target, z1=Z_EARLY):
    """The two-stage rule as numbers. After stage 1 (k1 wrong of n1):
       k1 <= early_k            PASS at stage 1 (bound at z1 <= target);
       k1 >= futile_k           FAIL, stop (P(stage 2 passes | k1, 2% rate) < 5%);
       otherwise                read to n2 and PASS iff k2 <= final_k (standard 95% Wilson bound <= target). No third look."""
    early_k, final_k = accept_k(n1, target, z1), accept_k(n2, target)
    futile_k = next((k for k in range(n1 + 1) if cdf(n2 - n1, final_k - k, P_FUTILE) < FUTILE_BELOW), n1 + 1)
    return dict(n1=n1, n2=n2, target=target, early_k=early_k, final_k=final_k, futile_k=futile_k)


def p_outcomes(r, p):
    """Exact probabilities of PASS at stage 1, FAIL by futility, PASS overall, and of reading stage 2, at true error rate p."""
    n1, n2 = r['n1'], r['n2']
    pm = [comb(n1, i) * p ** i * (1 - p) ** (n1 - i) for i in range(n1 + 1)]
    early = sum(pm[:r['early_k'] + 1])
    futile = sum(pm[r['futile_k']:])
    extend = 1 - early - futile
    passed = early + sum(pm[k1] * cdf(n2 - n1, r['final_k'] - k1, p) for k1 in range(r['early_k'] + 1, min(r['futile_k'], n1 + 1)))
    return dict(p=p, pass_stage1=early, fail_futility=futile, read_stage2=extend, pass_overall=passed,
                pass_if_single_look_at_n2=cdf(n2, r['final_k'], p))


def tables():
    rep = {'wilson_z': Z, 'z_early': Z_EARLY, 'futility_rate': P_FUTILE, 'futility_below': FUTILE_BELOW, 'effective_n_recomputed': {}, 'ruling_vs_recomputed': [], 'strata': {}}
    for t, ps in RULING.items():
        rep['effective_n_recomputed'][str(t)] = {str(p): n_needed(p, t) for p in (0.0, *ps)}
        for p, said in ps.items():
            got = n_needed(p, t)
            rep['ruling_vs_recomputed'].append(dict(target=t, true_rate=p, ruling_n=said, recomputed_n=got, difference=got - said))
    for s, a in PLAN.items():
        r = rule(a['n1'], a['n2'], a['target'])
        rep['strata'][s] = dict(r, outcomes={str(p): p_outcomes(r, p) for p in (0.01, 0.02, 0.03, a['target'])},
                                false_pass_at_target=p_outcomes(r, a['target'])['pass_overall'],
                                single_stage_acceptance={str(n): accept_k(n, a['target']) for n in (a['n1'], a['n2'])})
    b = BRIEF_FIGURE
    rep['brief_figure_vs_recomputed'] = dict(b, recomputed_n=n_needed(b['true_rate'], b['target']), zero_error_n=n_needed(0.0, b['target']))
    rep['alternatives_10pct_n2'] = {str(n2): {pp: p_outcomes(rule(55, n2, 0.10), p)['pass_overall'] for pp, p in (('0.02', 0.02), ('0.03', 0.03))} | {'final_k': rule(55, n2, 0.10)['final_k']} for n2 in (71, 110, 150)}
    return rep


def selftest():
    # known answers (same as audit 11's stats.py)
    assert round(wilson_upper(0, 20), 6) == 0.161125 and round(wilson_upper(20, 20), 6) == 1.0 and round(wilson_upper(10, 20), 6) == 0.700702
    # the ruling's 55 and 71 reproduce exactly; 205 and 460 within 3 records; the brief's 35 is the ZERO-error size, the 1% size is 43
    got = {(t, p): n_needed(p, t) for t, ps in RULING.items() for p in ps}
    assert got[(0.10, 0.02)] == 55 and got[(0.10, 0.03)] == 71 and got[(0.05, 0.02)] == 203 and got[(0.05, 0.03)] == 457, got
    assert n_needed(0.01, 0.10) == 43 and n_needed(0.0, 0.10) == BRIEF_FIGURE['brief_n'] == 35, 'the brief\'s 35 is the zero-error size, not the 1% size'
    # acceptance numbers and monotonicity
    assert [accept_k(205, 0.05), accept_k(460, 0.05), accept_k(55, 0.10), accept_k(71, 0.10)] == [4, 13, 1, 2]
    assert all(accept_k(n, 0.10) <= accept_k(n + 1, 0.10) for n in range(5, 400))
    # exact binomial identities
    assert abs(cdf(10, 10, 0.3) - 1) < 1e-12 and abs(cdf(2, 0, 0.5) - 0.25) < 1e-12 and cdf(5, -1, 0.5) == 0
    for s, a in PLAN.items():
        r = rule(a['n1'], a['n2'], a['target'])
        assert r['early_k'] < r['futile_k'] and r['early_k'] <= r['final_k'] and r['n1'] < r['n2'], (s, r)
        o = p_outcomes(r, a['target'])
        assert abs(o['pass_stage1'] + o['fail_futility'] + o['read_stage2'] - 1) < 1e-9
        # no false-pass inflation: at a true error rate equal to the target, the whole two-look rule passes < 2.5% (one-sided level of a 95% bound)
        assert o['pass_overall'] < 0.025, (s, o)
        # a stricter early look never passes more than the fixed stage-2 look would have ... and never fewer than zero
        assert 0 <= o['pass_stage1'] <= o['pass_overall']
    # Monte Carlo cross-check of the exact enumeration for PIC-18 at 3%
    import random
    rng, r, hits, N = random.Random(7), rule(205, 460, 0.05), 0, 20000
    for _ in range(N):
        k1 = sum(rng.random() < 0.03 for _ in range(205))
        if k1 <= r['early_k']:
            hits += 1
        elif k1 < r['futile_k']:
            hits += k1 + sum(rng.random() < 0.03 for _ in range(255)) <= r['final_k']
    assert abs(hits / N - p_outcomes(r, 0.03)['pass_overall']) < 0.015, (hits / N, p_outcomes(r, 0.03)['pass_overall'])
    # sizes.json on disk equals what this file computes
    assert json.loads((H / 'sizes.json').read_text()) == json.loads(json.dumps(tables())), 'sizes.json is stale: run sizes.py --write'
    print('sizes selftest: PASS')


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        selftest()
    elif '--write' in sys.argv:
        (H / 'sizes.json').write_text(json.dumps(tables(), indent=1, sort_keys=True) + '\n')
    else:
        print(json.dumps(tables(), indent=1, sort_keys=True))
