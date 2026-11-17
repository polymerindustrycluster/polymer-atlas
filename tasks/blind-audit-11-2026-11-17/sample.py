"""Blind audit 11: predeclared change-class-stratified draw, then blind inputs built from a WHITELIST at the pinned HEAD.

Adapted from tasks/blind-audit-10-2026-11-14/sample.py (allocation, leak scan and whitelist unchanged in kind).
Allocation: strata with fewer than CENSUS_BELOW record changes are taken whole; every other stratum gets at least FLOOR;
the rest of N is split in proportion to stratum size by largest remainder.
Run: python3 sample.py   (rewrites sample.csv, blind_a.csv, blind_b.csv, draw.json, freeze.json from frame.csv + pinned git)
"""
import csv, hashlib, json, random, re
from collections import Counter
from pathlib import Path
import frame as F

H = F.H
SEED = 'BLIND-AUDIT-11-2026-11-17-v1'
N, FLOOR, CENSUS_BELOW = 120, 3, 5
# Never shown to blind reviewers: they name a pass/lane/builder or date the pass, or are builder prose.
WITHHELD = {'created_by', 'notes', 'last_verified', 'as_of', 'observed_date', 'evidence_date', 'evidence_id', 'tier_effect', 'claim_detail', 'source_class', 'last_activity_evidence_date'}
CITED = {'sources', 'source_ref'}  # citation columns: shown as cited_sources, scrubbed like A10's sources
# Fields that identify the record for a reviewer, shown as context when they are not themselves under audit
LOCATOR = {'organizations': ['legal_name', 'website', 'hq_city', 'hq_state'], 'sites': ['site_name', 'street_address', 'city', 'state', 'zip', 'county'],
           'ecosystem': ['legal_name', 'website', 'city', 'state'], 'programs': ['program_name', 'url'],
           'members': ['display_name', 'member_tier', 'record_class', 'membership_source_url']}
# Words that would name a PR, pass, lane, packet, builder, tier ruling or owner decision in free text (A10 pattern; 'lane' narrowed to
# lowercase or 'Lane <ID>' after it hit the place name 'Green Lane, PA')
LEAK = re.compile(r'#\d+|\bEVD-\d+|\bPR\b|pull request|\bpass[- ]?\d*\b|packet|(?-i:\blanes?\b|\bLanes? [A-Z0-9]{2,}\b)|\bwave\b|integration pass|integrator|codex|claude|grok|gemini|spaghetti|\bmuse\b|\bowner\b|\brulings?\b|battery|council|refut|\bminted\b|staging|banked|\bnotes?\b|created_by|tier[ _]?effect|supports_[ABCU]', re.I)
# An archive_links record is keyed by its evidence_id: that one cell may carry EVD- (public key of the row under audit)
ARCHIVE_KEY = re.compile(r'EVD-\d{6}\|https://web\.archive\.org/web/\d{14}/\S+')
PASS_DATE = re.compile(r'\b2026-(?:10-[23]\d|11-\d\d)\b')
READ_DATE = re.compile(r'\s*\b(?:read|accessed|retrieved|checked|verified|fetched)\s+\d{4}-\d{2}-\d{2}\b[;,]?\s*', re.I)
URL = re.compile(r'https?://[^\s<>")\]]+')
BLIND_LABEL = {'rulings': 'program_status'}  # the frame's class name would tell a reviewer the value was already decided


def allocate(sizes):
    """class -> n. Census below CENSUS_BELOW; floor FLOOR; remainder proportional by largest remainder (ties: larger stratum)."""
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
    sizes = Counter(r['change_class'] for r in frame)
    alloc = allocate(sizes)
    out = []
    for cl in F.CLASSES:
        cands = sorted((r for r in frame if r['change_class'] == cl), key=lambda r: (r['table'], r['record_id']))
        rng = random.Random(int.from_bytes(hashlib.sha256((SEED + '|' + cl).encode()).digest(), 'big'))
        for r in sorted(rng.sample(cands, alloc[cl]), key=lambda r: (r['table'], r['record_id'])):
            out.append(dict(r, stratum_N=len(cands), stratum_n=alloc[cl], inclusion_probability=f'{alloc[cl] / len(cands):.12f}'))
    assert len(out) == len({(r['table'], r['record_id'], r['change_class']) for r in out}) == N
    return out, alloc


def urls(text):
    return sorted({u.rstrip('.,;:') for u in URL.findall(text or '')})


class Head:
    """Pinned-HEAD reader (git show, never the working tree)."""
    def __init__(self):
        files = F.table_files(F.HEAD)
        self.t = {t: F.load(F.HEAD, files[t], t) for t in F.TABLES}
        ev = [p for p in F.git('ls-tree', '-r', '--name-only', F.HEAD, 'data/').splitlines() if re.fullmatch(r'data/evidence_[a-z_]+_[A-Z0-9]+\.csv', p)]
        self.evidence, self.ev_by_id = {}, {}
        for p in ev:
            for r in F.rows_at(F.HEAD, p):
                self.evidence.setdefault((r['record_table'], r['record_id']), []).append(r)
                self.ev_by_id[r['evidence_id']] = r
        self.orgs = {k: v[0] for tb in ('organizations', 'ecosystem') for k, v in self.t[tb].items()}

    def org(self, i):
        o = self.orgs.get(i)
        return f"{o['legal_name']} ({o.get('website', '')}; {o.get('hq_city') or o.get('city', '')}, {o.get('hq_state') or o.get('state', '')})" if o else None

    def site(self, i):
        s = self.t['sites'].get(i, [None])[0]
        return f"{s['site_name']}, {s['street_address']}, {s['city']}, {s['state']} {s['zip']}" if s else None

    def label(self, t, r):
        if t in ('organizations', 'ecosystem'):
            return r['legal_name']
        if t == 'sites':
            return f"{r['site_name']} ({self.orgs.get(r['org_id'], {}).get('legal_name', r['org_id'])})"
        if t == 'programs':
            return f"{r['program_name']} @ {self.orgs.get(r['institution_org_id'], {}).get('legal_name', r['institution_org_id'])}"
        if t == 'members':
            return r['display_name']
        if t == 'registry_links':
            return f"{r['registry']} link for {self.orgs.get(r['org_id'], {}).get('legal_name', r['org_id'])}"
        if t == 'site_capabilities':
            return f"{r['capability_type']} {r['term']} at {self.t['sites'][r['site_id']][0]['site_name']}"
        if t == 'archive_links':
            e = self.ev_by_id[r['evidence_id']]
            return f"archive capture of evidence for {e['record_table']} {e['record_id']}"
        raise KeyError(t)

    def context(self, t, r, audit):
        ctx = {c: r[c] for c in LOCATOR.get(t, []) if c not in audit and r.get(c)}
        for c, fn in (('org_id', self.org), ('parent_org_id', self.org), ('institution_org_id', self.org), ('site_id', self.site)):
            if (t, c) in (('organizations', 'org_id'), ('ecosystem', 'org_id'), ('sites', 'site_id')):
                continue  # the record itself: its locator fields are already shown, minus the columns under audit
            if r.get(c) and fn(r[c]):
                ctx[c + '_resolved'] = fn(r[c])
        if t == 'archive_links':  # the URL the capture should be of, and what it supports
            e = self.ev_by_id[r['evidence_id']]
            rec = self.t.get(e['record_table'], {}).get(e['record_id'], [None])[0]
            ctx.update(archived_evidence_claim_type=e['claim_type'], archived_evidence_source_urls=' '.join(urls(e['source_ref'])),
                       evidence_for=f"{e['record_table']} {e['record_id']} {self.label(e['record_table'], rec) if rec else ''}".strip())
        return ctx


def blind_row(h, s):
    t, k = s['table'], s['record_id']
    r = h.t[t][k][0]
    cols = [c for c in r if r[c] != '' and not F.DERIVED(c)] if s['change_kind'] == 'created' else s['changed_columns'].split(';')
    audit = [c for c in cols if c not in WITHHELD]
    values = {c: r.get(c, '') for c in audit if c not in CITED}
    cited = ' '.join(r[c] for c in CITED if r.get(c))
    evid = sorted({(e['claim_type'], u) for e in h.evidence.get((t, k), []) for u in urls(e['source_ref'])})
    nourl = sum(1 for e in h.evidence.get((t, k), []) if not urls(e['source_ref']))
    row = dict(table=t, record_id=k, record_label=h.label(t, r), change_class=BLIND_LABEL.get(s['change_class'], s['change_class']), change_kind=s['change_kind'], columns_under_audit=';'.join(audit),
               values_json=json.dumps(values, ensure_ascii=False, sort_keys=True), context_json=json.dumps(h.context(t, r, audit), ensure_ascii=False, sort_keys=True),
               evidence_json=json.dumps([dict(claim_type=c, url=u) for c, u in evid], ensure_ascii=False))
    cited = re.sub(r'\(\s+', '(', re.sub(r'\(\s*\)', '', READ_DATE.sub(' ', cited))).strip()  # drop source-read dates, keep the rest of the citation
    reduced = bool(LEAK.search(cited) or PASS_DATE.search(cited))
    row['cited_sources'] = ' '.join(urls(cited)) if reduced else cited  # prose that names a pass/lane/ruling: keep only its public URLs
    row['_no_public_url'] = not urls(cited) and not evid and not any(urls(str(v)) for v in values.values()) and not urls(row['context_json'])
    row['_evidence_rows_without_url'] = nourl
    row['_sources_scrubbed_to_urls'] = reduced
    return row


BLIND_FIELDS = ['blind_id', 'change_class', 'table', 'record_id', 'record_label', 'change_kind', 'columns_under_audit', 'values_json', 'context_json', 'cited_sources', 'evidence_json']


def leak_scan(rows):
    """Every blind cell that matches LEAK, as (blind_id, field, text). The archive_links key cell is exempt only when it is exactly a key."""
    def hit(r, f):
        v = str(r[f])
        if f == 'record_id' and r['table'] == 'archive_links' and ARCHIVE_KEY.fullmatch(v):
            return False
        return LEAK.search(v) or (f in ('cited_sources', 'evidence_json', 'context_json') and PASS_DATE.search(v))
    return [(r['blind_id'], f, r[f]) for r in rows for f in BLIND_FIELDS if f != 'blind_id' and hit(r, f)]


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
    blind = [dict({f: rows[i][f] for f in BLIND_FIELDS if f != 'blind_id'}, blind_id=f'A11-{n:03d}') for n, i in enumerate(order, 1)]
    hits = leak_scan(blind)
    assert not hits, hits
    bid = {(b['table'], b['record_id'], b['change_class']): b['blind_id'] for b in blind}
    internal = [dict(s, no_public_url=str(r['_no_public_url']).lower(), evidence_rows_without_url=r['_evidence_rows_without_url'],
                     sources_scrubbed_to_urls=str(r['_sources_scrubbed_to_urls']).lower(), blind_id=bid[(s['table'], s['record_id'], BLIND_LABEL.get(s['change_class'], s['change_class']))]) for s, r in zip(sample, rows)]
    F.write_csv(H / 'sample.csv', internal, list(internal[0]))
    for name in ('blind_a.csv', 'blind_b.csv'):
        F.write_csv(H / name, blind, BLIND_FIELDS)
    draw_receipt = dict(seed=SEED, rng='Python random.Random seeded by int(SHA256(seed|change_class)), rng.sample over (table, record_id) sorted ascending; blind row order = shuffle seeded by SHA256(seed|order)',
                        n=N, floor=FLOOR, census_below=CENSUS_BELOW, allocation={cl: alloc[cl] for cl in F.CLASSES}, frame_sizes=dict(Counter(r['change_class'] for r in frame)),
                        sample_by_table=dict(Counter(s['table'] for s in sample)), sample_by_change_kind=dict(Counter(s['change_kind'] for s in sample)),
                        base=F.BASE, head=F.HEAD, blind_whitelist_withheld=sorted(WITHHELD), blind_fields=BLIND_FIELDS,
                        no_public_url_records=sum(1 for r in internal if r['no_public_url'] == 'true'),
                        sources_scrubbed_to_urls=sum(1 for r in internal if r['sources_scrubbed_to_urls'] == 'true'))
    (H / 'draw.json').write_text(json.dumps(draw_receipt, indent=1, sort_keys=True) + '\n')
    freeze = {p: sha(H / p) for p in ('frame.csv', 'frame_provenance.json', 'sample.csv', 'draw.json', 'blind_a.csv', 'blind_b.csv', 'frame.py', 'sample.py', 'REVIEWER_INSTRUCTIONS.md')}
    assert freeze['blind_a.csv'] == freeze['blind_b.csv'], 'blind_a and blind_b must be identical'
    (H / 'freeze.json').write_text(json.dumps(dict(sha256=freeze, blind_is_protocol_not_access_control='frame.csv and sample.csv carry PR attribution; hand reviewers only their blind file and REVIEWER_INSTRUCTIONS.md',
                                                   leak_scan_pattern=LEAK.pattern), indent=1, sort_keys=True) + '\n')
    print(draw_receipt)


if __name__ == '__main__':
    main()
