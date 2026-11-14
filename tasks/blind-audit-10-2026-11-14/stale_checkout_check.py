"""Reviewer A disclosed early notes from a stale checkout. Re-run the checks that depend on repo state (duplicates) for all 50 sampled
records at the pinned HEAD (git show, never a working tree). Vocabulary is covered by scripts/validate.py passing at HEAD (V-rules).
Returns {record: [other record ids that duplicate it]}; an empty dict means no duplicate was found."""
import csv, re
import frame as F
import sample as S

H = F.H
norm = lambda s: re.sub(r'[^a-z0-9]+', ' ', (s or '').lower()).strip()
dom = lambda u: re.sub(r'^(https?://)?(www\.)?', '', (u or '').lower()).split('/')[0]


def duplicates():
    h = S.Head()
    rows = list(csv.DictReader((H / 'sample.csv').open(newline='')))
    out = {}
    for s in rows:
        t, k = s['table'], s['record_id']
        r = h.t[t][k][0]
        others = [(kk, v[0]) for kk, v in h.t[t].items() if kk != k]
        if t == 'people':
            hit = [kk for kk, o in others if norm(o['full_name']) == norm(r['full_name']) and o['institution_org_id'] == r['institution_org_id']]
        elif t == 'programs':
            hit = [kk for kk, o in others if o['institution_org_id'] == r['institution_org_id'] and norm(o['program_name']) == norm(r['program_name'])]
        elif t in ('ecosystem', 'organizations'):
            pool = [(kk, o) for tb in ('ecosystem', 'organizations') for kk, v in h.t[tb].items() for o in [v[0]] if kk != k]
            hit = [kk for kk, o in pool if norm(o['legal_name']) == norm(r['legal_name'])
                   or (r.get('ror_id') and o.get('ror_id') == r['ror_id']) or (r.get('ipeds_unitid') and o.get('ipeds_unitid') == r['ipeds_unitid'])]
        elif t == 'sites':
            hit = [kk for kk, o in others if r['street_address'] and norm(o['street_address']) == norm(r['street_address']) and o['zip'][:5] == r['zip'][:5]]
        elif t == 'event_participation':
            hit = [kk for kk, o in others if (o['event_id'], o['org_id'], o['edition_year'], o['role']) == (r['event_id'], r['org_id'], r['edition_year'], r['role'])]
        else:  # people_identifiers: one row per identifier value (V-54)
            hit = [kk for kk, o in others if o['identifier_id'] == r['identifier_id']]
        if hit:
            out[k] = hit
    return out, len(rows)


if __name__ == '__main__':
    d, n = duplicates()
    print(n, 'sampled records checked at pinned HEAD; duplicates:', d)
