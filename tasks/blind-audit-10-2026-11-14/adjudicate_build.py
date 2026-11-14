"""Phase 3: the lead's adjudication of the 14 reviewer disagreements, built from fresh raw fetches (adjudication_receipts.jsonl).
Every receipt is re-verified here against the stored raw body: a quote must appear as a word sequence in order in the page text
(AGENTS/CONTRACT raw-check rule); an 'absent' term must have zero hits; 'raw_re' must match the raw bytes (a link in markup).
A failed fetch is an availability signal, never evidence of absence: absence receipts are only used on pages that returned HTTP 200.
Output adjudication.json (committed, with a normalised word excerpt per quote so CI can re-verify without the raw bodies).
Run: python3 adjudicate_build.py"""
import json, re
from pathlib import Path
import adjudicate_fetch as A

H = A.H
RECEIPTS = [json.loads(l) for l in (H / 'adjudication_receipts.jsonl').read_text().splitlines()]


def R(url, quote=None, absent=None, raw_re=None, note=''):
    return dict(url=url, quote=quote, absent=absent or [], raw_re=raw_re, note=note)


S3 = 'https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress?address='
GEO_NH = S3 + '10+Iron+Horse+Dr%2C+Bedford%2C+NH+03110&benchmark=Public_AR_Current&vintage=Current_Current&format=json'
GEO_MA = S3 + '135+South+Rd%2C+Bedford%2C+MA+01730&benchmark=Public_AR_Current&vintage=Current_Current&format=json'
GREG_POST = 'https://gregstrom.com/gregstrom-moves-rotomolding-business/'
LI = 'https://www.linkedin.com/feed/update/urn:li:activity:7394382058858434560/'
LI_Q = 'has relocated their corporate headquarters from Woburn, Massachusetts to 10 Iron Horse Drive, Bedford, New Hampshire'
MONET_TEAM = 'https://www.monetcci.org/our-team'

DECISIONS = [
    dict(id='A10-003', grade='UNRESOLVED', fields='polymer_program;polymer_program_name;polymer_program_url',
         settling_fact='An owner scope ruling on whether a fiber/textile Manufacturing USA institute with no stated polymer program counts as polymer_program=true under SCHEMA 4.6, or an AFFOA page that names polymer fiber work.',
         rationale='Identity, Bedford MA headquarters, Middlesex county, national geography and test/prototype access are supported. The polymer scope claim is not: AFFOA\'s own home, about, technology and Manufacturing USA pages (HTTP 200) never state a polymer program; the only "polymer" on the home page is the name of an accelerator awardee (Z-Polymers). Scope is an owner ruling (AGENTS 2 rule 9), so it is held, not graded as an error and not counted as agreement.',
         receipts=[R('https://affoa.org/', quote='Four awardees will receive no-cost access to AFFOA’s expertise, prototyping, testing, and scale-up capabilities'),
                   R('https://affoa.org/', quote='AFFOA Celebrates Opening of New Headquarters with Ribbon-Cutting Ceremony in Bedford, Massachusetts'),
                   R('https://affoa.org/', quote='AFFOA Names Nuream and Z-Polymers the New Awardees of the Product Accelerator for Advanced Fabrics', note='the only polymer-bearing text on the home page is a company name'),
                   R('https://affoa.org/technology/', absent=['polymer']), R('https://affoa.org/about/', absent=['polymer']),
                   R('https://affoa.org/about/manufacturing-usa/', absent=['polymer']),
                   R(GEO_MA, quote='"matchedAddress":"135 SOUTH RD, BEDFORD, MA, 01730"'), R(GEO_MA, quote='"NAME":"Middlesex County"')]),
    dict(id='A10-007', grade='AGREE', fields='', settling_fact='',
         rationale='Reviewer A\'s field error (operated by FlexTech Alliance not on the cited pages) is overturned: the legal entity behind NextFlex is FlexTech Alliance, Inc. doing business as NextFlex (federal registration and trademark records, same San Jose address as the NextFlex footer), and the 2015 DoD award names FlexTech Alliance as the institute manager. The cited pages not naming it is a citation gap, not a wrong value. Polymer substrates, San Jose, Santa Clara county and the technology hub are supported.',
         receipts=[R('https://www.highergov.com/awardee/flextech-alliance-inc-10350446/', quote='Legal Name FLEXTECH ALLIANCE, INC. DBA NEXTFLEX'),
                   R('https://www.trademarkia.com/nextflex-88213201', quote='Last Applicant / Owned By FlexTech Alliance, Inc.'),
                   R('https://www.trademarkia.com/nextflex-88213201', quote='Owner Address Suite 150 2244 Blach Place San Jose CA 95131'),
                   R('https://www.nextflex.us/flextech-alliance-receives-75-million-department-defense-award-create-manage-flexible-hybrid-electronics-manufacturing-facility/', quote='awarded FlexTech Alliance a Cooperative Agreement to establish and manage a Manufacturing Innovation Institute'),
                   R('https://www.nextflex.us/', quote='2244 Blach Place Suite 150 San Jose, CA 95131'),
                   R('https://www.nextflex.us/technology-hub/', quote='NextFlex replaced the traditional circuit board with a thin, flexible plastic sheet'),
                   R('https://www.nextflex.us/technology-hub/', quote='including polyimide and thermoplastic polyurethane substrates'),
                   R('https://en.wikipedia.org/wiki/San_Jose,_California', quote='is the county seat of Santa Clara County')]),
    dict(id='A10-011', grade='AGREE', fields='', settling_fact='',
         rationale='The organizer\'s own roster endpoint (the JavaScript list on the exhibitor page) returns International Mold Steel for PTXPO 2028, read as raw JSON, so the roster claim is mechanically checked; Reviewer B could not see it because the static page is a shell. Dates and Rosemont IL are on the organizer\'s site.',
         receipts=[R('https://ptxpo28.mapyourshow.com/8_0/ajax/remote-proxy.cfm?action=search&searchtype=exhibitorgallery&search=International+Mold+Steel&searchsize=20&start=0', quote='International Mold Steel offers a unique line of pre-hardened mold steels, tool steels, and cold work die steels'),
                   R('https://www.ptxpo.com/', quote='March 21-23, 2028 ROSEMONT, ILLINOIS USA'),
                   R('https://ptxpo28.mapyourshow.com/8_0/explore/exhibitor-alphalist.cfm?alpha=*', quote='Plastics Technology Expo 2028 Map Your Show DOWNLOAD Mar. 21 - 23 Rosemont')]),
    dict(id='A10-015', grade='FIELD_ERROR', fields='edition_dates', current_value='2026-09-28 to 2026-10-01', correct_value='2026-09-28 to 2026-09-30', settling_fact='',
         rationale='The organizer\'s 2026 schedule has exactly three days: Monday 9/28 (exhibition set-up and reception), Tuesday 9/29, Wednesday 9/30, and no Thursday. October 1 is only the end of the hotel group-rate window. The 2027 conference is announced as Sept. 27-29 (Monday to Wednesday), the same pattern. Sponsor role (Magris Talc, Gold) is on the organizer\'s sponsor list.',
         receipts=[R('https://auto-tpo.com/wp-content/uploads/2026/09/TPOSchedule-rev2-9_15_26-FINAL.pdf', quote='MONDAY 9 | 28 12:00 - 6:00PM EXHIBITION SET-UP'),
                   R('https://auto-tpo.com/wp-content/uploads/2026/09/TPOSchedule-rev2-9_15_26-FINAL.pdf', quote='WEDNESDAY 9 | 30 All Times Shown in EDT USA'),
                   R('https://auto-tpo.com/wp-content/uploads/2026/09/TPOSchedule-rev2-9_15_26-FINAL.pdf', absent=['THURSDAY']),
                   R('https://auto-tpo.com/hotel-travel/', quote='Hotel Rate – End Date: Thursday, October 1, 2026'),
                   R('https://www.auto-tpo.com/', quote='Next Year\'s Conference Sept. 27-29, 2027'),
                   R('https://auto-tpo.com/wp-content/uploads/2026/09/2026-Sponsorship-Lay-out-Sept-14-2026-Rev3.pdf', quote='Magris Talc Gold 20')]),
    dict(id='A10-018', grade='AGREE', fields='', settling_fact='',
         rationale='Source-system checks Reviewer B asked for: IPEDS 199847 is Wake Forest University in Forsyth County NC (Urban Institute IPEDS directory), ROR 0207ad724 resolves to Wake Forest University in Winston-Salem, and the physics department states polymer research. Not graded: the record carries polymer_program=false for a non-Ohio university, which SCHEMA 4.6 text restricts to NE Ohio generalists while the data holds 134 such rows (schema/data tension for the owner).',
         receipts=[R('https://educationdata.urban.org/api/v1/college-university/ipeds/directory/2022/?unitid=199847', quote='"unitid":199847,"inst_name":"Wake Forest University"'),
                   R('https://educationdata.urban.org/api/v1/college-university/ipeds/directory/2022/?unitid=199847', quote='"city":"Winston-Salem","county_name":"Forsyth County"'),
                   R('https://api.ror.org/v2/organizations/0207ad724', quote='"value":"Wake Forest University"'),
                   R('https://physics.wfu.edu/research/condensed-matter/', quote='conjugated polymers for organic electronic devices')]),
    dict(id='A10-019', grade='AGREE', fields='', settling_fact='',
         rationale='The merged change asserts nothing about ownership: ultimate_parent_name is blank and the description says only that this is a US sales and distribution presence for OMG srl machines, which OMG srl\'s own agents-and-distributors page supports (3407 Avenue D, Arlington TX listed for USA agents, domain omgusa.net, which is OMG srl\'s own site). Reviewer A\'s unsettled question (subsidiary or independent distributor) is not asserted by the record, so it is not an error; it stays open and is not certified.',
         receipts=[R('https://www.omgitaly.com/agenti-e-distributori', quote='USA-South and Southwest 3407 Avenue D Arlington TX 76011'),
                   R('https://www.omgusa.net/', quote='Homepage - OMG Thermoforming'),
                   R('https://www.omgusa.net/', quote='Copyright © 2014 O.M.G. srl Via Morghen, 35 10143 - Torino')]),
    dict(id='A10-020', grade='AGREE', fields='', settling_fact='',
         rationale='The company\'s contact page gives the exact address and ZIP; its materials page names LLDPE, HDPE and PP rotomolding; the census geocoder matches the address in Hillsborough County; a dated 2025-11-12 report says the company relocated its corporate headquarters to this address. Bedford is the only address the company lists, so hq_and_plant and active are supported.',
         receipts=[R('https://gregstrom.com/contact/', quote='Gregstrom Corporation 10 Iron Horse Drive, Unit C, Bedford, NH 03110'),
                   R('https://gregstrom.com/rotational-molding-materials/', quote='PP Rotational Molding Polypropylene (PP) is a durable plastic'),
                   R('https://gregstrom.com/rotational-molding-materials/', quote='LLDPE Rotational Molding Linear low-density polyethylene (LLDPE)'),
                   R(GEO_NH, quote='"matchedAddress":"10 IRON HORSE DR, BEDFORD, NH, 03110"'), R(GEO_NH, quote='"NAME":"Hillsborough County"'),
                   R(LI, quote=LI_Q, note='LinkedIn post dated November 12, 2025, Bedford NH')]),
    dict(id='A10-032', grade='AGREE', fields='', settling_fact='',
         rationale='Harvard\'s profile gives the professor title and the Materials Science & Mechanical Engineering affiliation; his lab page, hosted on the SEAS domain, states his research areas include polymers (amorphous materials: metals, semiconductors, polymers), which meets Gate B as the schema words it (polymer research stated for the person on the institution\'s own pages). The witness is thin (polymers are one of three material classes); that is a scope-strength note, not an error.',
         receipts=[R('https://seas.harvard.edu/person/frans-spaepen', quote='Director of Undergraduate Studies, Materials Science & Mechanical Engineering Primary Teaching Area Materials Science & Mechanical Engineering'),
                   R('https://spaepen.seas.harvard.edu/', quote='Spaepen conducts research in the following areas: Amorphous materials (metals, semiconductors, polymers): structure, formation, stability, mechanical properties')]),
    dict(id='A10-033', grade='AGREE', fields='', settling_fact='',
         rationale='Reviewer B wanted the headquarters relocation stated outright and the county. The company contact page and the Association of Rotational Molders directory list only the Bedford address, a dated 2025-11-12 report says the corporate headquarters relocated from Woburn to 10 Iron Horse Drive, and the geocoder places the address in Hillsborough County.',
         receipts=[R('https://gregstrom.com/contact/', quote='Gregstrom Corporation 10 Iron Horse Drive, Unit C, Bedford, NH 03110'),
                   R('https://www.rotomolding.org/rotomolder-members/gregstrom-corporation', quote='Gregstrom Corporation 10 Iron Horse Drive Unit C, Bedford, NH 03110'),
                   R(GREG_POST, quote='is moving its rotomolding business from Woburn, Massachusetts to Bedford, New Hampshire'),
                   R(LI, quote=LI_Q), R(GEO_NH, quote='"NAME":"Hillsborough County"')]),
    dict(id='A10-037', grade='AGREE', fields='', settling_fact='',
         rationale='The UT pages Reviewer B found blocked return HTTP 200 on a plain fetch. They state the five IAMM research areas including Polymer Science, the Polymer Characterization Lab among the core facilities, the 140,000 sq ft Cherokee Farm headquarters, and the polymer-science topics behind the research_areas tags (gas separations, recycling and upcycling, 3D printing, characterization).',
         receipts=[R('https://research.utk.edu/iamm/about/core-facilities/', quote='Polymer Characterization Lab Premier global academic laboratory for characterizing polymers via molecular weight, molecular weight distribution, conformation, size, and thermal properties'),
                   R('https://research.utk.edu/iamm/about/iamm-hq/', quote='headquartered at the UT Research Park at Cherokee Farm . The 140,000 square-foot facility'),
                   R('https://research.utk.edu/iamm/research-areas/', quote='Advanced Materials , Advanced Manufacturing , Materials for Extremes , Polymer Science , & Quantum Materials'),
                   R('https://research.utk.edu/iamm/research-areas/polymer-science/', quote='from gas separations and carbon capture to 3D printing and plastics upcycling'),
                   R('https://research.utk.edu/iamm/research-areas/polymer-science/', quote='as external users from industry and national laboratories')]),
    dict(id='A10-038', grade='FIELD_ERROR', fields='url;public_door_url;description_1line',
         current_value='url and public_door_url https://monet.duke.edu/; description partners Columbia, Johns Hopkins, MIT, Northwestern, UC San Diego, UIUC, Michigan and Washington',
         correct_value='url and public_door_url https://www.monetcci.org/; partners per the current team page: Duke (lead), Columbia, Johns Hopkins, MIT, Northwestern, Morehouse College, UC San Diego, UIUC, University of Washington (no Michigan)', settling_fact='',
         rationale='The held URL is the one the NSF CCI page lists, but monet.duke.edu returns NXDOMAIN on two public resolvers, and Duke\'s own 2026 Phase II release links https://www.monetcci.org/ (HTTP 200). The partner list is the 2021 roster; the current official team page has no University of Michigan investigator and does list Morehouse College. Reviewer A\'s third claim (thermosets not stated anywhere) is withdrawn: the NSF CCI page says MONET makes low-flow structural thermosets recyclable and reprocessable, so specialty_materials=thermosets stands.',
         receipts=[R('dns://monet.duke.edu/A@8.8.8.8', quote='status: NXDOMAIN'), R('dns://monet.duke.edu/A@1.1.1.1', quote='status: NXDOMAIN'),
                   R('https://chem.duke.edu/news/monet-moves-phase-ii', raw_re=r'href="https://www\.monetcci\.org/"|https://www\.monetcci\.org/', note='Duke 2026 release links the live site'),
                   R('https://www.nsfcci.org/currentcenters-1', quote='Website: https://monet.duke.edu/'),
                   R('https://www.nsfcci.org/currentcenters-1', quote='making low-flow structural thermosets recyclable and reprocessable'),
                   R(MONET_TEAM, quote='Senior Investigator Juana Mendenhall Senior Investigator Morehouse College'),
                   R(MONET_TEAM, quote='Senior Investigator Nicole Steinmetz Senior Investigator University of California, San Diego'),
                   R(MONET_TEAM, absent=['Michigan']),
                   R('https://dmi.duke.edu/news/nsf-creates-polymer-chemistry-optimization-center-duke-future-materials', quote='University of Illinois Urbana–Champaign, University of Michigan and University of Washington', note='the 2021 roster the description copies')]),
    dict(id='A10-041', grade='UNRESOLVED', fields='program_org_id',
         settling_fact='A Brown page that lists Srivastava as faculty of the Materials Engineering concentration, or an owner ruling that a School of Engineering research-area listing (Materials Science) ties a person to the Materials Engineering concentration under SCHEMA 4.9.',
         rationale='Rank, polymer research (hydrogels, polymers) and identity are supported. The program link is indirect: the cited I-BEAM profile and his School of Engineering profile tie him to biomedical engineering and name no Materials Engineering link, the concentration page lists no faculty, and the only Brown tie is the research-interests page listing him under the Materials Science research area. SCHEMA 4.9 links a person to a program where the public page ties them to the held program, so the link is neither confirmed nor refuted.',
         receipts=[R('https://ibeam.brown.edu/people/vikas-srivastava', quote='Associate Professor of Engineering'),
                   R('https://ibeam.brown.edu/people/vikas-srivastava', quote='Research Interests Cell mechanics, Hydrogels, materials under extreme environment, Mechanobiology, Polymers, Solid mechanics'),
                   R('https://engineering.brown.edu/research/research-interests', quote='Materials Science Biomaterials Breuer , Coulombe , Dawson , Desai , Palmore , Raimondo , Shukla , Srivastava'),
                   R('https://engineering.brown.edu/undergraduate/concentrations/materials-engineering', absent=['Srivastava'])]),
    dict(id='A10-044', grade='AGREE', fields='', settling_fact='',
         rationale='Reviewer B asked for a dated outcome, not the 2025-07-30 plan. A dated 2025-11-12 report says the company relocated its corporate headquarters from Woburn to Bedford, the company contact page and the Association of Rotational Molders directory list only Bedford, and the company\'s own post says the rotomolding business is moving from Woburn. Together that supports closed for the Woburn plant. Note: SCHEMA 4.2 also offers relocated_in_scope; closed is not wrong.',
         receipts=[R(LI, quote=LI_Q), R(GREG_POST, quote='is moving its rotomolding business from Woburn, Massachusetts to Bedford, New Hampshire'),
                   R('https://gregstrom.com/contact/', absent=['Woburn']), R('https://www.rotomolding.org/rotomolder-members/gregstrom-corporation', absent=['Woburn'])]),
    dict(id='A10-048', grade='AGREE', fields='', settling_fact='',
         rationale='The organizer\'s speaker page lists the Dow speaker under The Dow Chemical Company (a trade name held on Dow Inc., ORG-002913), and the event page states Savannah, GA on December 7-9, 2026. A speaker is recorded as the employer organization (AGENTS 6).',
         receipts=[R('https://www.ami-events.com/event/4be30ecb-2ae0-4f40-a877-a38e69fed6f3/speakers', quote='Akanksha Garg TS&D/Research Scientist The Dow Chemical Company'),
                   R('https://www.ami-events.com/event/4be30ecb-2ae0-4f40-a877-a38e69fed6f3/home', quote='taking place in Savannah, GA, USA on December 7-9, 2026')]),
]


def resolve(url):
    ok = [r for r in RECEIPTS if r['url'] == url and (r['http_status'] == 200 or r['via'] == 'dig')]
    assert ok, f'no usable receipt for {url}'
    return max(ok, key=lambda r: r['fetched_at'])


def verify(rc):
    rec = resolve(rc['url'])
    body = (A.RAW / f"{rec['sha256']}.bin").read_bytes()
    text = A.visible(body, rec['url'])
    out = dict(url=rc['url'], via=rec['via'], http_status=rec['http_status'], bytes=rec['bytes'], sha256=rec['sha256'], fetched_at=rec['fetched_at'], note=rc['note'])
    if rc['quote']:
        assert A.quote_in_order(text, rc['quote']), f"quote not in order on page: {rc['url']} :: {rc['quote']}"
        # AGENTS 6: no individual emails or direct-dial numbers in the repo, so mask them before the word excerpt is committed
        masked = re.sub(r'(?<!\d)(?:\+?\d[\s().-]{0,3}){9,}\d(?!\d)', ' PHONE ', re.sub(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+', ' EMAIL ', text))
        w, q = A.WORDS(masked), A.WORDS(rc['quote'])
        i = next(i for i in range(len(w) - len(q) + 1) if w[i:i + len(q)] == q)
        out.update(quote=rc['quote'], excerpt_words=' '.join(w[max(0, i - 25):i + len(q) + 25]))
    for t in rc['absent']:
        assert not re.search(re.escape(t), text, re.I), f'absent term present: {t} on {rc["url"]}'
        assert rec['http_status'] == 200 and len(w := A.WORDS(text)) > 200, f'absence on a page that did not load: {rc["url"]}'
        out.setdefault('absent', []).append(t)
        out['page_words'] = len(A.WORDS(text))
    if rc['raw_re']:
        assert re.search(rc['raw_re'].encode(), body), f'raw pattern missing: {rc["url"]}'
        out['raw_re'] = rc['raw_re']
    return out


def build():
    verdicts = {}
    for f in ('a', 'b'):
        import csv
        verdicts[f] = {r['blind_id']: r for r in csv.DictReader((H / f'verdicts_{f}.csv').open(newline=''))}
    out = []
    for d in DECISIONS:
        a, b = verdicts['a'][d['id']], verdicts['b'][d['id']]
        assert a['verdict'] != b['verdict'], f"{d['id']} is not a disagreement"
        assert d['grade'] in ('AGREE', 'FIELD_ERROR', 'CREATION_ERROR', 'UNRESOLVED')
        if d['grade'] == 'UNRESOLVED':
            assert d['settling_fact']
        if d['grade'] == 'FIELD_ERROR':
            assert d.get('current_value') and d.get('correct_value')
        e = dict(d, record_id=a['record_id'], reviewer_a=a['verdict'], reviewer_b=b['verdict'], receipts=[verify(r) for r in d['receipts']])
        out.append(e)
    assert len(out) == 14 and len({e['id'] for e in out}) == 14
    (H / 'adjudication.json').write_text(json.dumps(out, indent=1, ensure_ascii=False) + '\n')
    return out


if __name__ == '__main__':
    o = build()
    from collections import Counter
    print(Counter(e['grade'] for e in o), sum(len(e['receipts']) for e in o), 'receipts verified')
