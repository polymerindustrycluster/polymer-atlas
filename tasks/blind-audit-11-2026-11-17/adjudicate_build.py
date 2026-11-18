"""Phase 3 of blind audit 11 (adapted from blind audit 10): the lead's adjudication of every sampled record change that the
two blind reviewers did not both grade AGREE, plus the controller-directed lead check of the seven both-AGREE band rows
(controller note 2026-11-17: grade PPP bands against the owner's 2026-11-16 "Strict matches" ruling, not as inadmissible).
Every web receipt is re-verified here against the stored raw body (adjudication_receipts.jsonl):
- a quote must appear as a word sequence in order in the page text;
- an 'absent' term must have zero hits on an HTTP 200 page of more than 200 words;
- 'raw_re' must match the raw bytes and 'raw_not_re' must not.
A failed fetch is an availability signal, never evidence of absence. A 'git:' receipt is a repo file at the frame HEAD.
Band rows are re-derived condition by condition from git (blank at #348's step parent, the dated HEAD evidence row,
single-site Ohio-only PIC-18 organization) and from the fresh SBA PPP extract (borrower name, street, city; JobsReported band).
R-SAM (controller ruling 2026-11-17): no SAM name or address, and no per-row SAM match detail, enters a committed file. UEI rows
are decided against the stored SAM response in private/audit11; the per-row facts go to a private note whose sha256 is pinned
here, and the repo carries only each row's grade.
Output adjudication.json (committed, with a normalised word excerpt per quote so CI can re-check without the raw bodies).
Run: python3 adjudicate_build.py"""
import csv, functools, hashlib, io, json, re, sys
from datetime import date
import adjudicate_fetch as A
import frame as F
from copy_verdicts import PRIVATE

sys.path.insert(0, str(F.ROOT / 'scripts'))
from regions import PIC18  # noqa: E402

H = A.H
RECEIPTS = [json.loads(l) for l in (H / 'adjudication_receipts.jsonl').read_text().splitlines()] if (H / 'adjudication_receipts.jsonl').exists() else []
SAM_FILES = {'sam_uei_raw.json': '7debb1194d275e7e59e8eded2ec2b3a72d695bbcbdcc2542314348161a54eb8f',
             'sam_uei_raw_page1.json': 'a49df5c8b61a7f1cf66e1ee1e666fa0eccac1a55975f463630cd597e67f9e541'}
UEI_NOTE = PRIVATE / 'adjudication_uei_private.json'
UEI_DETAIL = PRIVATE / 'adjudication_uei_detail.json'
SBA = 'https://data.sba.gov/sites/default/files/distribution/SBA-OCA-2022-07-001/'
PPP_SHA = {SBA + 'public_150k_plus_240930.csv': '3760a581dc3fd7ca12d09996aa360d749e075bcac517e5a6f7e92ae447a1cb8c',  # #348 source_manifest.json
           SBA + 'public_up_to_150k_9_240930.csv': 'b5d091ac98ee177c1b749159dcbdc37716d8aa10f258dc316bb39b00c7c1d4f9'}
OSHA = 'https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv'
WAYBACK_PIC = 'https://web.archive.org/web/20261116234145/https://polymerindustrycluster.org/'
BANDS = [(1, 9, '1-9'), (10, 49, '10-49'), (50, 99, '50-99'), (100, 249, '100-249'), (250, 499, '250-499'), (500, 999, '500-999'),
         (1000, 4999, '1000-4999'), (5000, 10 ** 9, '5000+')]
DIRECTIONS = {'n', 's', 'e', 'w', 'ne', 'nw', 'se', 'sw', 'north', 'south', 'east', 'west'}
STRIP = {'inc', 'llc', 'corp', 'co', 'the', 'incorporated', 'corporation', 'company', 'ltd'}


def norm(name):
    """AGENTS §3 normalized name: lowercase, '&' as 'and', punctuation and Inc/LLC/Corp/Co/The (and their long forms) dropped."""
    return ' '.join(w for w in re.findall(r'[a-z0-9]+', (name or '').lower().replace('&', ' and ')) if w not in STRIP)


def street_key(street):
    """(house number, first street-name word that is not a direction): '60 S PARK ST' and '60 South Park Street' -> ('60', 'park')."""
    w = re.findall(r'[a-z0-9]+', (street or '').lower())
    return (w[0], next((x for x in w[1:] if x not in DIRECTIONS), '')) if w and w[0].isdigit() else None


def band_of(n):
    return next(b for lo, hi, b in BANDS if lo <= n <= hi)


def R(url, quote=None, absent=None, raw_re=None, note='', raw_not_re=None):
    return dict(url=url, quote=quote, absent=absent or [], raw_re=raw_re, raw_not_re=raw_not_re, note=note)


OWN = 'own-site witness re-fetched; quote in order'
DECISIONS = [
    # --- members (#340): A AGREE (live list), B UNRESOLVED (wanted a dated 2026-11-16 receipt) ---
    *[dict(id=i, grade='AGREE', fields='snapshot_date',
           key_fact=f'A Wayback capture of the public PIC member list made 2026-11-16 23:41 UTC lists "{n}" under Investing Partners, so the list showed this member on the recorded snapshot_date (2026-11-16).',
           receipts=[R(WAYBACK_PIC, 'Members Investing Partners Ace Laboratories ACESS ACS Local Section - Akron AES AMLCI ARDL Aropha Alterra Rubber Division Amware '
                                    'Aries Science and Technology LLC Avient BioVerde Bounce Innovation Hub Bridgestone', note='dated public witness for the 2026-11-16 list')])
      for i, n in (('A11-004', 'Rubber Division'), ('A11-058', 'Avient'), ('A11-072', 'Bounce Innovation Hub'))],
    # --- tier changes (#354): A AGREE, B UNRESOLVED (needed the OSHA filing) ---
    dict(id='A11-005', grade='AGREE', fields='verification_tier',
         key_fact='All seven site must-have claims carry evidence at supports_B or stronger, so §4.13 restates tier B. The OSHA ITA CY2025 row for establishment 818456 matches the existence, address, code and parent rows (ALTTRAN, INC., 5285 HUDSON DR., Hudson OH 44236, NAICS 326299, filed 2026-02-25); the own-site activity, scope and liveness quote is on the page.',
         receipts=[R(OSHA, raw_re=r'(?m)^\d+,"Alttran, Inc\.",818456,\d*,"ALTTRAN, INC\.",5285 HUDSON DR\.,HUDSON,OH,44236,326299,[^\n]*,2/25/2026,,2025', note='fresh full-file read; extract of the establishment row'),
                   R('https://alttran.com/rubber-mixing-capabilities/', 'We provide custom rubber mixing for manufacturers that need consistent compounds', note=OWN)]),
    dict(id='A11-076', grade='AGREE', fields='verification_tier',
         key_fact='All seven site must-have claims carry evidence at supports_B or stronger, so §4.13 restates tier B. The OSHA ITA CY2025 row for establishment 1258989 matches the existence, address, code and parent rows (FabOhio Inc, 521 E 7th St, Uhrichsville OH 44683, NAICS 326111, filed 2026-01-29); the own-site quote is on the page.',
         receipts=[R(OSHA, raw_re=r'(?m)^\d+,FabOhio Inc,1258989,\d*,FabOhio Inc,521 E 7th St,Uhrichsville,OH,44683,326111,[^\n]*,1/29/2026,,2025', note='fresh full-file read; extract of the establishment row'),
                   R('https://fabohio.com/about-us/history/', 'FabOhio, Inc. opened for business in 1963 and continues to operate at the same facility in Uhrichsville, Ohio', note=OWN)]),
    dict(id='A11-112', grade='AGREE', fields='verification_tier',
         key_fact='All seven site must-have claims carry evidence at supports_B or stronger, so §4.13 restates tier B. The OSHA ITA CY2025 row for establishment 519774 matches the existence, address, code and parent rows (Dreco Inc, 7887 Root Road, North Ridgeville OH 44039, NAICS 326199, filed 2026-01-22); the own-site quote is on the page.',
         receipts=[R(OSHA, raw_re=r'(?m)^\d+,Dreco Inc,519774,\d*,Dreco Inc,7887 Root Road,North Ridgeville,OH,44039,326199,[^\n]*,1/22/2026,,2025', note='fresh full-file read; extract of the establishment row'),
                   R('https://drecoinc.com/', 'From initial prototype to full-scale production, we deliver uncompromising quality and technical expertise in thermoplastic manufacturing', note=OWN)]),
    # --- navigation links (#350): A FIELD_ERROR, B AGREE ---
    dict(id='A11-047', grade='FIELD_ERROR', fields='newsroom_feed_url', current_value='https://www.provia.com/feed/', correct_value='https://www.provia.com/feed/?post_type=article',
         key_fact='§4.4 requires a feed "of the same newsroom". The newsroom page lists only article-type items (/article/), while the recorded feed carries only blog posts (/blog/) and no /article/ item, so no feed item is a newsroom item. The newsroom\'s own article feed carries its items, including the 2026-11-05 Request Quote release.',
         receipts=[R('https://www.provia.com/feed/', raw_re=r'<link>https://www\.provia\.com/blog/', raw_not_re=r'provia\.com/article/', note='recorded feed: blog items only'),
                   R('https://www.provia.com/newsroom', raw_re=r'"postType":"article"', raw_not_re=r'"postType":"(?!article")', note='newsroom item list: article type only'),
                   R('https://www.provia.com/feed/?post_type=article', 'Request Quote Feature Streamlines Quoting Process for Doors and Windows https://www.provia.com/article/request-quote-feature/', note='the newsroom\'s own feed')]),
    dict(id='A11-073', grade='AGREE', fields='newsroom_url;newsroom_feed_url',
         key_fact='The news page is the organization\'s own; the recorded feed is the site-wide feed, and one of its eight items (the 2023 PMA approval release) is linked from the news page. That meets the item-overlap test the earlier newsroom passes used for "of the same newsroom" (§4.4); the other seven items are forms and policies, a weak but not wrong navigation aid. The site\'s news-category feed is empty.',
         receipts=[R('https://www.synapsebiomedical.com/feed/', raw_re=r'<link>https://www\.synapsebiomedical\.com/synapse-biomedical-wins-new-pma-approval/</link>', note='recorded feed'),
                   R('https://www.synapsebiomedical.com/resources-2/news', raw_re=r'href="https://www\.synapsebiomedical\.com/synapse-biomedical-wins-new-pma-approval/"', note='news page links the same item'),
                   R('https://www.synapsebiomedical.com/category/news/feed/', raw_re=r'<title>News \| Synapse Biomedical Inc\.</title>', raw_not_re=r'<item>', note='the category feed exists but has no items')]),
    # --- rulings (#339): A FIELD_ERROR (blank is not a §4.6 value), B AGREE ---
    dict(id='A11-118', grade='AGREE', fields='polymer_program',
         key_fact='The value is the owner\'s ruling R-AFFOA (2026-11-16): set polymer_program back to blank until an AFFOA page states a polymer program. Neither reviewer found such a page. That §4.6 lists polymer_program as a MUST boolean is a schema-text question for the owner, not an error in this record (AGENTS §2 rule 9).',
         receipts=[R('git:4182519:tasks/owner-rulings-2026-11-16/README.md', "Ruled (a): clear the flag. Keep the record; set polymer_program back to blank until one of AFFOA's own pages states a polymer or fiber-polymer program", note='owner ruling of record')]),
    # --- UEI links (#355): decided against the stored SAM response; per-row facts are private (R-SAM) ---
    *[dict(id=i, grade='AGREE', fields='registry_id', sam_expect='match',
           key_fact='Match: the stored SAM response returns an active registration for this UEI whose name and location match this organization (per-row detail held privately under R-SAM).', receipts=[])
      for i in ('A11-033', 'A11-040', 'A11-051', 'A11-052', 'A11-071', 'A11-081', 'A11-083', 'A11-094', 'A11-101', 'A11-103', 'A11-109', 'A11-114')],
    dict(id='A11-113', grade='CREATION_ERROR', fields='registry_id', sam_expect='no_match', current_value='UEI link on ORG-000889 (ITW Tomco)',
         correct_value='retire the link; any re-link is the integrator\'s call',
         key_fact='No match: the stored SAM response\'s registration for this UEI is not ITW Tomco\'s. The per-row detail and two related leads are in the private note (R-SAM).', receipts=[]),
    # --- bands (#348): both AGREE; controller-directed lead check against the "Strict matches" ruling ---
    *[dict(id=i, grade='AGREE', fields='employee_band_ohio;employee_band_site', lead_check=True, ppp_url=SBA + f,
           key_fact='Passes all five conditions of the owner\'s 2026-11-16 "Strict matches" ruling (recomputed below from git and a fresh read of the SBA file #348 cites).',
           receipts=[R(SBA + f, raw_re=rf'(?m)^{loan},', note='fresh full-file read; extract of the loan row')])
      for i, f, loan in (('A11-006', 'public_150k_plus_240930.csv', '8191017006'), ('A11-035', 'public_up_to_150k_9_240930.csv', '2464008510'),
                         ('A11-067', 'public_150k_plus_240930.csv', '6217178505'), ('A11-091', 'public_150k_plus_240930.csv', '3091617205'),
                         ('A11-098', 'public_150k_plus_240930.csv', '6820187702'), ('A11-100', 'public_150k_plus_240930.csv', '6102237002'),
                         ('A11-107', 'public_up_to_150k_9_240930.csv', '4057067109'))],
]
LEAD_CHECK_CLASS = 'bands'  # controller note 2026-11-17: the only both-AGREE rows the lead re-checks


def resolve(url):
    ok = [r for r in RECEIPTS if r['url'] == url and (r['http_status'] == 200 or r['via'] == 'dig')]
    assert ok, f'no usable receipt for {url}'
    return max(ok, key=lambda r: r['fetched_at'])


def verify(rc):
    if rc['url'].startswith('git:'):
        _, ref, path = rc['url'].split(':', 2)
        body = F.git('show', f'{ref}:{path}').encode()
        rec = dict(url=rc['url'], via='git', http_status=None, bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), fetched_at=None)
    else:
        rec = resolve(rc['url'])
        body = (A.RAW / f"{rec['sha256']}.bin").read_bytes()
    text = A.visible(body, rec['url'])
    out = dict(url=rc['url'], via=rec['via'], http_status=rec['http_status'], bytes=rec['bytes'], sha256=rec['sha256'], fetched_at=rec['fetched_at'], note=rc['note'])
    if rec.get('file_sha256'):  # a stream extract: tie it to the whole file
        out.update(file_sha256=rec['file_sha256'], file_bytes=rec['file_bytes'])
    if rc['quote']:
        assert A.quote_in_order(text, rc['quote']), f"quote not in order on page: {rc['url']} :: {rc['quote']}"
        # AGENTS 6: no individual emails or direct-dial numbers in the repo, so mask them before the word excerpt is committed
        masked = re.sub(r'(?<!\d)(?:\+?\d[\s().-]{0,3}){9,}\d(?!\d)', ' PHONE ', re.sub(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+', ' EMAIL ', text))
        w, q = A.WORDS(masked), A.WORDS(rc['quote'])
        i = next(i for i in range(len(w) - len(q) + 1) if w[i:i + len(q)] == q)
        out.update(quote=rc['quote'], excerpt_words=' '.join(w[max(0, i - 25):i + len(q) + 25]))
    for t in rc['absent']:
        assert not re.search(re.escape(t), text, re.I), f'absent term present: {t} on {rc["url"]}'
        assert rec['http_status'] == 200 and len(A.WORDS(text)) > 200, f'absence on a page that did not load: {rc["url"]}'
        out.setdefault('absent', []).append(t)
        out['page_words'] = len(A.WORDS(text))
    if rc['raw_re']:
        assert re.search(rc['raw_re'].encode(), body), f'raw pattern missing: {rc["url"]} :: {rc["raw_re"]}'
        out['raw_re'] = rc['raw_re']
    if rc['raw_not_re']:
        assert not re.search(rc['raw_not_re'].encode(), body), f'raw pattern present that must not be: {rc["url"]} :: {rc["raw_not_re"]}'
        out['raw_not_re'] = rc['raw_not_re']
    return out


def head_tables():
    files = F.table_files(F.HEAD)
    orgs = {k: r for k, (r, _) in F.load(F.HEAD, files['organizations'], 'organizations').items()}
    sites = [r for r, _ in F.load(F.HEAD, files['sites'], 'sites').values()]
    ev = [r for p in F.git('ls-tree', '-r', '--name-only', F.HEAD, 'data/').split() if re.fullmatch(r'data/evidence_[^/]*\.csv', p) for r in F.rows_at(F.HEAD, p)]
    return orgs, sites, ev


@functools.lru_cache(maxsize=None)
def at_348_parent(table):
    step = next(sha for sha, pr, _ in F.steps()[0] if pr == 348)
    return F.load(step + '^1', F.table_files(step + '^1')[table], table)


def band_facts(s, ppp_url, orgs, sites, ev, ppp_row=None):
    """The five "Strict matches" conditions for one sampled band record change, each recomputed. ppp_row (the committed copy) stands in
    for the fresh SBA extract only where the raw extract is absent; check.py reports that as a gap."""
    table, rid = s['table'], s['record_id']
    col = 'employee_band_ohio' if table == 'organizations' else 'employee_band_site'
    before = at_348_parent(table)[rid][0][col]
    head = (orgs[rid] if table == 'organizations' else next(r for r in sites if r['site_id'] == rid))[col]
    org_id = rid if table == 'organizations' else next(r for r in sites if r['site_id'] == rid)['org_id']
    org, held = orgs[org_id], [r for r in sites if r['org_id'] == org_id]
    rows = [e for e in ev if e['record_id'] == rid and e['claim_type'] == 'size_band' and 'SBA PPP LoanNumber' in e['source_ref']]
    assert len(rows) == 1, f'{rid}: expected one PPP size_band evidence row at HEAD, found {len(rows)}'
    e = rows[0]
    loan = re.search(r'LoanNumber (\d+)', e['source_ref']).group(1)
    if ppp_row is None:
        rec = resolve(ppp_url)
        assert rec['file_sha256'] == PPP_SHA[ppp_url], f'{ppp_url}: fresh file is not the release #348 cites'
        p = next(r for r in csv.DictReader(io.StringIO((A.RAW / f"{rec['sha256']}.bin").read_text(), newline='')) if r['LoanNumber'] == loan)
    else:
        p = ppp_row
        assert p['LoanNumber'] == loan, f'{rid}: committed PPP row is not the evidence row\'s loan'
    approved = date(int(p['DateApproved'][6:]), int(p['DateApproved'][:2]), int(p['DateApproved'][3:5])).isoformat()
    names = {norm(org['legal_name'])} | {norm(t) for t in org['trade_names'].split(';') if t.strip()}
    site = held[0] if len(held) == 1 else None
    facts = dict(
        filled_blank_cell=before == '' and head != '',
        labelled_with_2020_or_2021_loan_date=approved[:4] in ('2020', '2021') and e['observed_date'] == approved and f'historical {approved[:4]} ' in e['claim_detail'] and e['source_ref'].startswith(ppp_url),
        single_site_ohio_only_active_in_pic18=bool(site) and org['hq_state'] == 'OH' and site['state'] == 'OH' and site['operating_status'] == 'active' and site['county'] in PIC18,
        borrower_name_street_city_match=bool(site) and norm(p['BorrowerName']) in names and street_key(p['BorrowerAddress']) == street_key(site['street_address']) and p['BorrowerCity'].casefold() == site['city'].casefold(),
        band_equals_jobs_reported_band=band_of(int(p['JobsReported'])) == head,
    )
    ppp = {k: p[k] for k in ('LoanNumber', 'DateApproved', 'BorrowerName', 'BorrowerAddress', 'BorrowerCity', 'BorrowerState', 'BorrowerZip', 'JobsReported')}
    return dict(conditions=facts, ppp_row=ppp, band=head, value_at_348_step_parent=before, evidence_id=e['evidence_id'], site_id=site and site['site_id'],
                site_county=site and site['county'], held_sites=len(held))


def sam_entities():
    ents = {}
    for name, h in SAM_FILES.items():
        raw = (PRIVATE / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == h, f'{name}: stored SAM response changed'
        ents.update({e['entityRegistration']['ueiSAM']: e for e in json.loads(raw)['entityData']})
    return ents


def sam_facts(orgs, sites, uei_rows, write=True):
    """Private: per-UEI match facts from the stored SAM response. Returns ({blind_id: 'match'|'no_match'}, private note text)."""
    ents = sam_entities()
    note, verdict = {}, {}
    for i, rid in uei_rows.items():
        org_id, _, uei, _ = rid.split('|')
        o, e = orgs[org_id], ents.get(uei)
        if not e:
            note[i], verdict[i] = dict(returned=False), 'no_match'
            continue
        pa = e['coreData']['physicalAddress']
        names = {norm(o['legal_name'])} | {norm(t) for t in o['trade_names'].split(';') if t.strip()}
        held = [s for s in sites if s['org_id'] == org_id and street_key(s['street_address']) == street_key(pa['addressLine1'])
                and s['city'].casefold() == pa['city'].casefold() and s['state'] == pa['stateOrProvinceCode']]
        f = dict(returned=True, active=e['entityRegistration']['registrationStatus'] == 'Active',
                 name_match=bool(names & {norm(e['entityRegistration'].get(k)) for k in ('legalBusinessName', 'dbaName')} - {''}),
                 hq_city_state_match=(o['hq_city'].casefold(), o['hq_state']) == (pa['city'].casefold(), pa['stateOrProvinceCode']),
                 held_site_match=[s['site_id'] for s in held], entity_url=e['coreData']['entityInformation'].get('entityURL'))
        note[i] = f
        # a match needs an active registration, a name match, and the organization's own HQ locality (a held site alone can be mis-parented)
        verdict[i] = 'match' if f['active'] and f['name_match'] and f['hq_city_state_match'] else 'no_match'
    note.update(json.loads(UEI_DETAIL.read_text()))  # the lead's hand-written finding and leads for the no-match row (private, R-SAM)
    text = json.dumps(note, indent=1, sort_keys=True) + '\n'
    if write:
        UEI_NOTE.write_text(text)
    return verdict, text


def build():
    v = {f: {r['blind_id']: r for r in csv.DictReader((H / f'verdicts_{f}.csv').open(newline=''))} for f in 'ab'}
    sample = {r['blind_id']: r for r in csv.DictReader((H / 'sample.csv').open(newline=''))}
    disputed = {i for i in v['a'] if not (v['a'][i]['verdict'] == v['b'][i]['verdict'] == 'AGREE')}
    lead = {i for i, s in sample.items() if s['change_class'] == LEAD_CHECK_CLASS}
    assert not disputed & lead, 'a band row is disputed: adjudicate it as such, not as a lead check'
    orgs, sites, ev = head_tables()
    uei = {d['id']: sample[d['id']]['record_id'] for d in DECISIONS if 'sam_expect' in d}
    sam, _ = sam_facts(orgs, sites, uei)
    out = []
    for d in DECISIONS:
        a, b, s = v['a'][d['id']], v['b'][d['id']], sample[d['id']]
        assert d['id'] in (lead if d.get('lead_check') else disputed), f"{d['id']}: not a disputed row or a lead-check row"
        assert d['grade'] in ('AGREE', 'FIELD_ERROR', 'CREATION_ERROR', 'UNRESOLVED') and d['key_fact'].strip()
        assert d['grade'] != 'UNRESOLVED' or d['settling_fact']
        assert d['grade'] not in ('FIELD_ERROR', 'CREATION_ERROR') or ('current_value' in d and 'correct_value' in d)
        e = {k: x for k, x in d.items() if k not in ('ppp_url', 'sam_expect')}
        if 'sam_expect' in d:
            assert sam[d['id']] == d['sam_expect'] and (d['grade'] == 'AGREE') == (d['sam_expect'] == 'match'), f"{d['id']}: SAM facts disagree with the decision"
            e['sam_result'] = d['sam_expect']
        if d.get('lead_check'):
            bf = band_facts(s, d['ppp_url'], orgs, sites, ev)
            assert (d['grade'] == 'AGREE') == all(bf['conditions'].values()), f"{d['id']}: band conditions {bf['conditions']} disagree with the grade"
            e['band_check'] = bf
        out.append(dict(e, record_id=a['record_id'], change_class=s['change_class'], reviewer_a=a['verdict'], reviewer_b=b['verdict'], receipts=[verify(r) for r in d['receipts']]))
    ids = [e['id'] for e in out]
    assert len(ids) == len(set(ids)) and set(ids) == disputed | lead, f'adjudication must cover exactly the disputed and lead-check rows: missing {sorted((disputed | lead) - set(ids))}'
    meta = dict(sam_files_sha256=SAM_FILES, uei_private_note_sha256=hashlib.sha256(UEI_NOTE.read_bytes()).hexdigest())
    (H / 'adjudication.json').write_text(json.dumps(dict(meta=meta, decisions=out), indent=1, ensure_ascii=False) + '\n')
    return out


if __name__ == '__main__':
    o = build()
    from collections import Counter
    print(Counter(e['grade'] for e in o), Counter(e['change_class'] for e in o), sum(len(e['receipts']) for e in o), 'receipts verified')
