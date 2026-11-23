"""Named gate for the canary packet: python3 tasks/pic18-process-inhand-2026-11-22/check.py
Recomputes the frame and the seeded sample independently of the committed CSVs, then verifies every packet row against the stored corpus
(quote verbatim, raw hash, locality witness, record-cited page, vocabulary, sentence-not-menu) and runs planted defects, each of which must be rejected.
Fails (never skips) when the corpus is unreadable."""
import csv, hashlib, json, re, sys
import common as c

PROC = set(c.vocab()['vocabularies']['PROCESSES']['values'])

def read(n): return list(csv.DictReader(open(c.T / n, newline='')))

def verify_fill(p, frame_ids, manifest, hosts):
    """Return an error string, or '' when the row holds."""
    if p['site_id'] not in frame_ids: return 'site not in frame (a process already exists at site or organization grain)'
    if p['term'] not in PROC: return 'term not in SCHEMA 3.1 vocabulary'
    rows = [r for r in manifest if r['org_id'] == p['org_id'] and r['url'] == p['source_url'] and r['text_file'] == p['text_file']]
    if not rows: return 'page is not a stored page of this organization'
    host = re.sub(r'^www\.', '', re.sub(r'^https?://', '', p['source_url']).split('/')[0])
    if host not in hosts: return 'page host is not a source the record already cites'
    tf = c.CORPUS / p['text_file']; rf = c.CORPUS / p['raw_file']
    if not tf.exists() or not rf.exists(): return 'stored page unreadable'
    if hashlib.sha256(rf.read_bytes()).hexdigest() != p['raw_sha256'] or rows[0]['sha256'] != p['raw_sha256']: return 'raw hash differs from manifest'
    if hashlib.sha256(tf.read_bytes()).hexdigest() != p['text_sha256']: return 'text hash differs'
    text = c.norm(tf.read_text(errors='replace'))
    if c.norm(p['quote']) not in text: return 'quote not found verbatim in the stored page'
    w = c.norm(p['quote']).split()
    if len(w) < 8 or not p['quote'].rstrip().endswith('.'): return 'quote is not a sentence (menu or list line)'
    gt = c.norm((c.CORPUS / p['grain_text_file']).read_text(errors='replace'))
    if c.norm(p['grain_quote']) not in gt: return 'locality witness not found in the stored page'
    if c.norm(p['site_street']).lower() not in c.norm(p['grain_quote']).lower(): return 'locality witness does not print the site street'
    return ''

def main():
    d = c.load(); frame_ids = {s['site_id'] for s in d['frame']}; by = {s['site_id']: s for s in d['frame']}
    assert (len(d['frame']), len(d['unk'])) == (333, 322), 'frame size moved: rebaseline'
    smp = [s['site_id'] for s in c.sample(d['frame'])]
    packet, leads, holds = read('packet.csv'), read('leads.csv'), read('holds.csv')
    ids = sorted({p['site_id'] for p in packet} | {l['site_id'] for l in leads} | {h['site_id'] for h in holds})
    assert ids == sorted(smp) and len(smp) == 25, 'adjudicated sites differ from the seeded sample'
    assert not ({p['site_id'] for p in packet} & {l['site_id'] for l in leads}) and not ({p['site_id'] for p in packet} & {h['site_id'] for h in holds}) and not ({l['site_id'] for l in leads} & {h['site_id'] for h in holds}), 'a site appears in two files'
    assert (c.CORPUS / 'manifest.csv').exists(), 'corpus unreadable: gate fails rather than skips'
    manifest = [r for r in csv.DictReader(open(c.CORPUS / 'manifest.csv', newline='')) if r['text_file']]
    EVR = {}
    for e in c.rd('data/evidence_*.csv'): EVR.setdefault(e['record_id'], []).append(e['source_ref'])
    def hosts_for(s):
        o = d['orgs'].get(s['org_id']) or d['eco'].get(s['org_id']) or {}
        urls = re.findall(r'https?://[^\s;,|)\]"\']+', s['sources'] + ' ' + o.get('sources', '') + ' ' + o.get('website', '')) + [u for sid in (s['site_id'], s['org_id']) for u in EVR.get(sid, []) if u.startswith('http')]
        bare = [x for x in re.split(r'[;\s]+', s['sources']) if re.fullmatch(r'(?:www\.)?[a-z0-9-]+(?:\.[a-z0-9-]+)+/?', x.lower())]
        return {re.sub(r'^www\.', '', re.sub(r'^https?://', '', u).split('/')[0]).lower() for u in urls + bare}
    bad = [(p['site_id'], p['term'], verify_fill(p, frame_ids, manifest, hosts_for(by[p['site_id']]))) for p in packet]
    bad = [b for b in bad if b[2]]
    assert not bad, bad
    for l in leads: assert l['route'] in 'ABC' and l['candidate_term'] and l['statement_and_source_named']
    for l in leads:
        for t in l['candidate_term'].split(';'): assert t in PROC, ('lead term not in vocabulary', l['site_id'], t)
    # planted defects: each must be rejected
    p0 = dict(packet[0]); H = hosts_for(by[p0['site_id']])
    plants = {
        'paraphrase': {**p0, 'quote': 'Rotocast staff also rebuild and repair molds.'},
        'menu line as quote': {**p0, 'quote': 'Mold Repair & Modifications'},
        'invented term': {**p0, 'term': 'mold_repair'},
        'wrong locality': {**p0, 'grain_quote': 'Rotocast Technologies, Inc. 77 Elm St Akron, OH 44312'},
        'site not in frame': {**p0, 'site_id': 'SITE-000335'},
        'quote from another org page': {**p0, 'org_id': 'ORG-000001'},
    }
    for name, row in plants.items():
        err = verify_fill(row, frame_ids, manifest, H)
        assert err, f'planted defect passed: {name}'
    print('OK: frame 333 sites / 322 orgs; canary 25 = fills %d (sites %d), leads %d, holds %d; %d planted defects rejected' % (len(packet), len({p['site_id'] for p in packet}), len(leads), len(holds), len(plants)))
    return 0

if __name__ == '__main__':
    sys.exit(main())
