"""Blind audit 10: predeclared table-stratified draw, then blind inputs built from a WHITELIST at the pinned HEAD.

Allocation (assumption, see README): strata with fewer than CENSUS_BELOW records are taken whole; every other stratum
gets at least FLOOR records; the rest of the 50 is split in proportion to stratum size by largest remainder.
Run: python3 sample.py   (rewrites sample.csv, blind_a.csv, blind_b.csv, draw.json, freeze.json from frame.csv + pinned git)
"""
import csv, hashlib, json, random, re
from collections import Counter
from pathlib import Path
import frame as F

H = F.H
SEED = 'BLIND-AUDIT-10-2026-11-14-v1'
N, FLOOR, CENSUS_BELOW = 50, 3, 5
# Never shown to blind reviewers: they name a pass/lane/builder or date the pass, or are builder prose.
WITHHELD = {'created_by', 'notes', 'last_verified', 'as_of', 'observed_date', 'evidence_date', 'evidence_id', 'tier_effect', 'claim_detail', 'source_class', 'last_activity_evidence_date'}
# Foreign keys resolved to a name for the reviewer, by table
FK = {'people': ['institution_org_id', 'program_org_id'], 'programs': ['institution_org_id'], 'sites': ['org_id'],
      'event_participation': ['org_id', 'event_id'], 'people_identifiers': ['person_id'], 'organizations': ['parent_org_id', 'successor_org_id'],
      'ecosystem': ['parent_institution_org_id']}
# Words that would name a PR, pass, lane, packet, builder, tier ruling or owner decision in free text
LEAK = re.compile(r'#\d+|\bEVD-\d+|\bPR\b|pull request|\bpass[- ]?\d*\b|packet|\blane\b|\bwave\b|integrat|codex|claude|grok|gemini|spaghetti|\bmuse\b|\bowner\b|battery|council|refut|\bminted\b|staging|banked|\bnotes?\b|created_by|tier[ _]?effect|supports_[ABCU]', re.I)
# ISO dates that fall in the pass window (a source-read date names the pass); checked in citation/evidence/context cells only,
# because record content such as event dates may legitimately fall in November 2026
PASS_DATE = re.compile(r'\b2026-(?:10-[23]\d|11-\d\d)\b')
READ_DATE = re.compile(r'\s*\b(?:read|accessed|retrieved|checked|verified|fetched)\s+\d{4}-\d{2}-\d{2}\b[;,]?\s*', re.I)
URL = re.compile(r'https?://[^\s<>")\]]+')


def allocate(sizes):
    """table -> n. Census below CENSUS_BELOW; floor FLOOR; remainder proportional by largest remainder (ties: larger stratum)."""
    alloc = {t: s for t, s in sizes.items() if 0 < s < CENSUS_BELOW}
    pool = {t: s for t, s in sizes.items() if s >= CENSUS_BELOW}
    budget = N - sum(alloc.values())
    while True:  # pin strata whose proportional share is under the floor, re-proportion the rest
        total = sum(pool.values())
        low = [t for t, s in pool.items() if budget * s / total < FLOOR]
        if not low:
            break
        for t in low:
            alloc[t] = FLOOR
            budget -= FLOOR
            del pool[t]
    total = sum(pool.values())
    q = {t: budget * s / total for t, s in pool.items()}
    base = {t: int(v) for t, v in q.items()}
    for t in sorted(pool, key=lambda t: (-(q[t] - base[t]), -pool[t]))[:budget - sum(base.values())]:
        base[t] += 1
    alloc.update(base)
    assert sum(alloc.values()) == N and all(alloc[t] <= sizes[t] for t in alloc), alloc
    return alloc


def draw(frame):
    sizes = Counter(r['table'] for r in frame)
    alloc = allocate(sizes)
    out = []
    for t in F.TABLES:
        if t not in alloc:
            continue
        cands = sorted((r for r in frame if r['table'] == t), key=lambda r: r['record_id'])
        rng = random.Random(int.from_bytes(hashlib.sha256((SEED + '|' + t).encode()).digest(), 'big'))
        for r in sorted(rng.sample(cands, alloc[t]), key=lambda r: r['record_id']):
            out.append(dict(r, stratum_N=len(cands), stratum_n=alloc[t], inclusion_probability=f'{alloc[t] / len(cands):.12f}'))
    assert len(out) == len({(r['table'], r['record_id']) for r in out}) == N
    return out, alloc


def urls(text):
    return sorted({u.rstrip('.,;:') for u in URL.findall(text or '')})


class Head:
    """Pinned-HEAD reader (git show, never the working tree)."""
    def __init__(self):
        files = F.table_files(F.HEAD)
        self.t = {t: F.load(F.HEAD, files[t], t) for t in F.TABLES}
        self.events = {r['event_id']: r for r in F.rows_at(F.HEAD, 'data/events.csv')}
        ev = [p for p in F.git('ls-tree', '-r', '--name-only', F.HEAD, 'data/').splitlines() if re.fullmatch(r'data/evidence_[A-Za-z_]+\.csv', p)]
        self.evidence = {}
        for p in ev:
            for r in F.rows_at(F.HEAD, p):
                self.evidence.setdefault((r['record_table'], r['record_id']), []).append(r)
        self.orgs = {k: v[0]['legal_name'] for tb in ('organizations', 'ecosystem') for k, v in self.t[tb].items()}

    def name(self, i):
        if i in self.orgs:
            return self.orgs[i]
        if i in self.t['programs']:
            p = self.t['programs'][i][0]
            return f"{p['program_name']} @ {self.orgs.get(p['institution_org_id'], p['institution_org_id'])}"
        if i in self.t['people']:
            p = self.t['people'][i][0]
            return f"{p['full_name']} ({self.orgs.get(p['institution_org_id'], '')})"
        if i in self.events:
            return self.events[i]['name']
        return None

    def label(self, t, k, r):
        if t == 'people':
            return f"{r['full_name']} - {self.orgs.get(r['institution_org_id'], r['institution_org_id'])}"
        if t == 'programs':
            return f"{r['program_name']} @ {self.orgs.get(r['institution_org_id'], r['institution_org_id'])}"
        if t in ('ecosystem', 'organizations'):
            return r['legal_name']
        if t == 'sites':
            return f"{r['site_name']} ({self.orgs.get(r['org_id'], r['org_id'])})"
        if t == 'people_identifiers':
            return self.name(r['person_id'])
        if t == 'event_participation':
            return f"{self.orgs.get(r['org_id'], r['org_id'])} at {self.events.get(r['event_id'], {}).get('name', r['event_id'])} {r['edition_year']}"
        return k


def blind_row(h, s):
    t, k = s['table'], s['record_id']
    r = h.t[t][k][0]
    changed = s['changed_columns'].split(';')
    if s['change_kind'] == 'created':
        cols = [c for c in r if r[c] != '' and not F.DERIVED(c)]
    else:
        cols = changed
    audit = [c for c in cols if c not in WITHHELD]
    values = {c: r.get(c, '') for c in audit if c != 'sources'}
    cited = r.get('sources', '')
    ctx = {}
    for c in FK.get(t, []):
        for i in (r.get(c, '') or '').replace(',', ';').split(';'):
            i = i.strip()
            if i and h.name(i):
                ctx[i] = h.name(i)
    if t == 'people_identifiers':
        ctx['person_public_profile_url'] = h.t['people'][r['person_id']][0]['public_profile_url']
        ctx['person_institution'] = h.orgs.get(h.t['people'][r['person_id']][0]['institution_org_id'], '')
    evid = sorted({(e['claim_type'], u) for e in h.evidence.get((t, k), []) for u in urls(e['source_ref'])})
    nourl = sum(1 for e in h.evidence.get((t, k), []) if not urls(e['source_ref']))
    row: dict = dict(table=t, record_id=k, record_label=h.label(t, k, r), change_kind=s['change_kind'], columns_under_audit=';'.join(audit),
               values_json=json.dumps(values, ensure_ascii=False, sort_keys=True), context_json=json.dumps(ctx, ensure_ascii=False, sort_keys=True),
               cited_sources=cited, evidence_json=json.dumps([dict(claim_type=c, url=u) for c, u in evid], ensure_ascii=False))
    cited = re.sub(r'\(\s+', '(', re.sub(r'\(\s*\)', '', READ_DATE.sub(' ', cited))).strip()  # drop "read 2026-11-06" source-read dates, keep the rest of the citation
    row['cited_sources'] = cited
    reduced = bool(LEAK.search(cited) or PASS_DATE.search(cited))
    if reduced:
        # free text that still names a pass/lane/tier ruling: keep only the public URLs, drop the prose
        row['cited_sources'] = ' '.join(urls(cited))
    row['_no_public_url'] = not urls(cited) and not evid and not any(urls(str(v)) for v in values.values())
    row['_evidence_rows_without_url'] = nourl
    row['_sources_scrubbed_to_urls'] = reduced  # prose dropped, URLs kept (source-read dates alone are just removed)
    return row


BLIND_FIELDS = ['blind_id', 'table', 'record_id', 'record_label', 'change_kind', 'columns_under_audit', 'values_json', 'context_json', 'cited_sources', 'evidence_json']


def leak_scan(rows):
    """Every blind cell that matches LEAK, as (blind_id, field, text)."""
    return [(r['blind_id'], f, r[f]) for r in rows for f in BLIND_FIELDS if f != 'blind_id'
            and (LEAK.search(str(r[f])) or (f in ('cited_sources', 'evidence_json', 'context_json') and PASS_DATE.search(str(r[f]))))]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    with (H / 'frame.csv').open(newline='') as f:
        frame = list(csv.DictReader(f))
    sample, alloc = draw(frame)
    h = Head()
    rows = [blind_row(h, s) for s in sample]
    order = list(range(N))
    random.Random(int.from_bytes(hashlib.sha256((SEED + '|order').encode()).digest(), 'big')).shuffle(order)  # row order must not follow PR/ID order
    blind = []
    for n, i in enumerate(order, 1):
        blind.append(dict({f: rows[i][f] for f in BLIND_FIELDS if f != 'blind_id'}, blind_id=f'A10-{n:03d}'))
    hits = leak_scan(blind)
    assert not hits, hits
    internal = [dict(s, no_public_url=str(r['_no_public_url']).lower(), evidence_rows_without_url=r['_evidence_rows_without_url'], sources_scrubbed_to_urls=str(r['_sources_scrubbed_to_urls']).lower(),
                     blind_id=next(b['blind_id'] for b in blind if (b['table'], b['record_id']) == (s['table'], s['record_id']))) for s, r in zip(sample, rows)]
    F.write_csv(H / 'sample.csv', internal, list(internal[0]))
    for name in ('blind_a.csv', 'blind_b.csv'):
        F.write_csv(H / name, blind, BLIND_FIELDS)
    draw_receipt = dict(seed=SEED, rng='Python random.Random seeded by int(SHA256(seed|table)), rng.sample over record_ids sorted ascending; blind row order = shuffle seeded by SHA256(seed|order)',
                        n=N, floor=FLOOR, census_below=CENSUS_BELOW, allocation=alloc, frame_sizes=dict(Counter(r['table'] for r in frame)),
                        sample_by_table=dict(Counter(s['table'] for s in sample)), sample_by_change_kind=dict(Counter(s['change_kind'] for s in sample)),
                        base=F.BASE, head=F.HEAD, blind_whitelist_withheld=sorted(WITHHELD), blind_fields=BLIND_FIELDS,
                        event_participation_frame_rows_without_http_evidence_url=sum(1 for r in frame if r['table'] == 'event_participation' and not URL.search(h.t['event_participation'][r['record_id']][0]['evidence_source_url'])),
                        no_public_url_records=sum(1 for r in internal if r['no_public_url'] == 'true'),
                        sources_scrubbed_to_urls=sum(1 for r in internal if r['sources_scrubbed_to_urls'] == 'true'))
    (H / 'draw.json').write_text(json.dumps(draw_receipt, indent=1, sort_keys=True) + '\n')
    freeze = {p: sha(H / p) for p in ('frame.csv', 'frame_provenance.json', 'sample.csv', 'draw.json', 'blind_a.csv', 'blind_b.csv', 'frame.py', 'sample.py')}
    assert freeze['blind_a.csv'] == freeze['blind_b.csv'], 'blind_a and blind_b must be identical'
    (H / 'freeze.json').write_text(json.dumps(dict(sha256=freeze, blind_is_protocol_not_access_control='frame.csv and sample.csv carry PR attribution; hand reviewers only their blind file',
                                                   leak_scan_pattern=LEAK.pattern), indent=1, sort_keys=True) + '\n')
    print(draw_receipt)


if __name__ == '__main__':
    main()
