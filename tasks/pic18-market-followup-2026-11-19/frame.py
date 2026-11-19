"""Market follow-up frame (owner rulings 2026-11-19 M1 and M2): the 17 organization records held as group_or_redirect_attribution in the market-scale batches
(10 in batch 1, 7 in batch 2) minus 4 that are not group-site cases (OUT_OF_SCOPE), plus Myrava (ORG-001558, held scope_owner_ruling). Two routes, compared by check.py: the ruling's own ID list, and the hold classes
in the two merged batches' verdicts.csv."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RULING_GROUP = ('ORG-000036 ORG-000119 ORG-000169 ORG-000438 ORG-000606 ORG-000752 ORG-001447 ORG-001461 ORG-001462 ORG-001513 '
                'ORG-001534 ORG-001949 ORG-002038 ORG-002047 ORG-003196 ORG-003771 ORG-004022').split()  # tasks/owner-rulings-2026-11-19 M1
MYRAVA = 'ORG-001558'  # M2
OUT_OF_SCOPE = 'ORG-000036 ORG-000169 ORG-001461 ORG-002038'.split()  # controller, from the Codex review of #401: not group-site cases (a directory, another maker's catalogue, pages of another entity)
EXPECTED = 14
BATCHES = ('tasks/pic18-market-scale-1-2026-11-18/verdicts.csv', 'tasks/pic18-market-scale-2-2026-11-18/verdicts.csv')


def prior_holds():
    """organization -> (hold class, batch file) for every organization still held in the merged batch verdicts."""
    out = {}
    for b in BATCHES:
        for r in csv.DictReader((ROOT / b).open()):
            if r['verdict'] == 'STILL_UNCERTAIN':
                out[r['org_id']] = (r['hold_class'], b)
    return out


def frame():
    held = prior_holds()
    group = sorted(o for o, (c, _) in held.items() if c == 'group_or_redirect_attribution' and o not in OUT_OF_SCOPE)
    assert all(held[o][0] == 'group_or_redirect_attribution' for o in OUT_OF_SCOPE), 'an out-of-scope organization is no longer held'
    assert held[MYRAVA][0] == 'scope_owner_ruling', 'Myrava is no longer held for the tier-cap note'
    return group + [MYRAVA]


if __name__ == '__main__':
    f = frame()
    assert len(f) == EXPECTED and f[:-1] == sorted(o for o in RULING_GROUP if o not in OUT_OF_SCOPE), (len(f), f)
    print(len(f), f[0], f[-1])
