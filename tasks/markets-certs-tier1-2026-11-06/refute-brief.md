Review L10 Tier1 continuation, independent from PR136 (do not inspect PR136 data). Base main9489b60. Frozen30frame:12VERIFIED/18STILL_UNCERTAIN.60filledtags=58markets+2certs;12activeTier1 orgs,tiersA8/B3/C1;12marketcells+2certcells;60newEVD240100–159;25claim-org holds. Active4884:markets394→406,cert47→49;Tier1active1261:markets162→174,cert13→15. CertsNovagardIATF2016expiry2027-05-30 andDuracoteAS9100:2016expiry2027-04-19. No ISO9001/14001 superseded claims filled. Each rawquote identity/date guarded. Namedcheck commands README; all60raw and30freshsample0errors;4knownanswers/4mutants;duplicateIDinjection no-write;missingverdictinjection no-write;scope/replay/validate0errors;SQLrecountmatches. Adversarial semantic sourcegrain, suppliermarket mapping,certcurrencyscope,IDimmutability,exacttwo-columnboundary. APPROVE/REFUTE concrete findings; distinguish liveinspected.

FILE README.md
# L10 round 2 — Tier-1-qualified organizations

Controller 06:30 BOARD assignment; new branch agent/codex/markets-certs-tier1 off current main. Scope: markets_served and certifications only, plus append-only own_site evidence. First user PIC supplier-matching staff; use review due 2026-12-15. IDs EVD-240100 onward inside original L10 block (prior PR136 reserves through240063; never reuse).

Acceptance before application: own-site corporate markets using exact SCHEMA vocabulary; automotive unspecified stays unspecified, medical without devices stays medical_healthcare_general. No generic material uses treated as served markets. Current edition + current dates for certifications; identity and expiry quotes checked, no ISO9001:2015 until owner transition ruling. Every added value has its own evidence row; no other organization columns changed, no tier changes. validate0errors, known answers and defect rejection, fresh30-value sample with error count, replay identical, two-family clerks required. PR136 remains separate and draft pending its own reviewers.

Frozen frame: frame.csv selected30 from1261 active organizations with nonempty stored tier1_qualifier (no rederivation). First30 blank markets + HTTP website, PIC18 first then org_id; excludes two prior holds ORG62/101 without resolving evidence. frame.json records census and filters. Lower-priority unselected rows are unworked, never held or verified by implication.

Research underway; not completion-approved.

## Results and provenance

Unit/filter: all active organization rows, baseline main9489b60, 4,884. markets_served populated394→406 (+12 organizations); certifications47→49 (+2). Tier-1-filtered active organizations1,261: markets162→174, certifications13→15. These counts are this PR alone; do not add its baseline values to PR136 (separate proposals on main).

30 frozen-frame organizations =12 VERIFIED and18 STILL_UNCERTAIN; verdicts.csv covers all30 exactly once. The12 changed organizations retain tiers A8/B3/C1. inputs.csv contains60 VERIFIED value fills:58 market values and2 certifications, EVD240100–240159. Evidence shards OH42/US18. No organizations/sites created or status/tier/website/parent/newsroom/notes/source columns changed. No inclusion-log entries or dedupe/create needed.

Sources are corporate own-site markets/about/industry pages of LyondellBasell, Novagard, Goldsmith&Eggleton, Addipel, Advanced Polymer Coatings, American Wire&Cable, Architectural Fiberglass, Barentz North America, Blair Rubber, Duracote, Forest City Technologies and Garland. Every URL and exact quote is in inputs.csv. Broad branded-material application possibilities are not corporate market evidence. Provider-specific product applications are used only where they explicitly state that provider's own market or business (e.g. American Wire's core appliance-wire business and named automotive-wire manufacturing).

Certificates: Novagard Smithers04.293.1 / IATF0520614, IATF16949:2016 with Product Design, current2024-05-31 through2027-05-30, main Cleveland site plus named warehousing support only. Duracote Smithers19.018.1, AS9100:2016 with Design, current2024-04-20 through2027-04-19, Ravenna single-site laminates/coatings scope. Duracote home also states AS9100RevD. Original company-hosted PDFs quote identity/edition/expiry, date bounds checked; no ISO9001 component filled.

Normative context, never organization evidence: [IATF current standard page](https://www.iatfglobaloversight.org/iatf-169492016/about/), [IAQG9100:2016 resources](https://iaqg.org/standard/9100-qms-requirements-for-aviation-space-and-defense-organizations/) and [IAQG/SAE standards register](https://brx-content.fullsight.org/site/binaries/content/assets/sae-org/content/landing-page/iaqg/2025-12-05-standards-register-for-publication.pdf) identify the accepted editions (register lists AS9100RevD2016-09-20). [ISO14001 current edition](https://www.iso.org/standard/14001) is2026, so Goldsmith's2015 claim stays held under R3c, alongside ISO9001:2015 candidates. The owner transition-window question remains the PR136 battery; no exception self-ruled.

## Holds and limits

holds.csv has25 claim/organization cases:18 organizations without a fill plus7 partial-field cases on filled organizations. Every row is STILL_UNCERTAIN with its settling fact. Availability failures prove nothing about operating status or absence of a market/certification. Ashtabularubber.com served ASC Engineered Solutions; attribution is held. Global Huntsman and LG Chem pages are not attributed to the named subsidiaries. Other holds include explicit end-market gaps, edition-less or superseded certifications, uninspected image certificate, and ambiguous/off-vocabulary categories. No markets_other_note org column exists, so no off-vocabulary tag is inserted. Unselected qualifying organizations remain unworked; no full Tier1 completion claim.

## Named checks

- `python3 tasks/markets-certs-tier1-2026-11-06/check.py`: four live known answers4/4, fabricated-quote defects refused4/4; all60 input quotes passed with no unavailable sources, including both certificate identity and expiry quotes. Fresh random30 VERIFIED value rows (seed20361106):0 quote errors. audit30.csv records values, retrieval routes and parsed-text hashes. This is a raw quote-support audit, not30 distinct organizations or an independent human semantic audit. fetched HTML has scripts/styles excluded; CSS visibility is not evaluated. Pages may change later.
- `python3 tasks/markets-certs-tier1-2026-11-06/build.py`: first run60 appends, second run byte-identical across affected shards. Tree-wide duplicate-ID defect was injected into read() before application: AssertionError before writes, all canonical CSV byte hashes unchanged. Vocabulary, active/storedTier1/frame membership, domain, unique values/recordIDs, certificate dates and immutable evidence collision conditions asserted. Existing observation equality checked.
- Parsed CSV before/after scope check:12 organizations,12 market fields,2 certification fields,60 evidence rows; zero missing keys, changed unrelated columns or edited existing evidence observations.
- `python3 scripts/validate.py`: OK validation passed,0errors,35,449 total evidence rows on this main baseline. Existing warnings remain. No scripts/ shared files changed, so shared-script pytest gate is not triggered.

Reuse: fetch.py/check.py/build.py carry forward the reviewed PR136 helper and guard fixes. Token normalization and contiguous-order matching are imported from the house tasks/evidence-repair-2-2026-11-04/prep.py. No dependency added. Research primary-page budget≤5 distinct own-site pages per organization; required live verification re-fetches are additional checks. Raw bodies lived temporarily under /tmp; only public quotes are committed.

Replay on newer main: restore main's organizations_OH.csv, organizations_US.csv, evidence_organizations_OH.csv and evidence_organizations_US.csv, rerun build.py and validate; never hand-merge CSVs. Preserve inputs order to preserve reserved evidence IDs. Branch base is the pre-pass backup; this README is the pass journal.

## Coordination and review

Controller06:30 assignment supersedes initial lane's lack of continuation. Branch/ID allocation/frame recorded in BOARD before application. Controller06:25 route supersedes old clerk pair for new requests: Codex4 thr_x5xruuutxp and Grok4 thr_95ffgh3rxy; queue exception applies to requests only. PR136 remains separate, Codex APPROVE recorded there; its Grok verdict is pending. This round's final two-family reviews are pending; no Done claim.

Additional controls: check.py reconciles30unique frame IDs against30unique verdict IDs; injected29/30 extraction fails before network or writes. Independent DuckDB1.5.6 SQL recount (`duckdb :memory: < tasks/markets-certs-tier1-2026-11-06/counts.sql`) confirms the active and storedTier1 filled counts above.

FILE build.py
"""Idempotently union the reviewed L10 values and append one immutable evidence row per value."""
import csv, json, sys
from datetime import date
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from shard_io import append_sorted

def read(path):
    with path.open(newline='') as f: return list(csv.DictReader(f))

def main():
    data = ROOT / 'data'
    shards = {p: read(p) for p in sorted(data.glob('organizations_*.csv')) if p.stem != 'organizations_all'}
    orgs = {r['org_id']: (p, r) for p, rows in shards.items() for r in rows}
    assert len(orgs) == sum(map(len, shards.values()))
    vocab = json.loads((ROOT / 'docs/schema/vocab.json').read_text())['vocabularies']
    allowed = {'markets_served': set(vocab['MARKETS']['values']), 'certifications': set(vocab['CERTS']['values'])}
    inputs = read(HERE / 'inputs.csv')
    assert len({(r['org_id'], r['field'], r['value']) for r in inputs}) == len(inputs)
    frame_ids = {r['org_id'] for r in read(HERE / 'frame.csv')}
    old_evidence = [r for p in data.glob('evidence_*.csv') for r in read(p)]
    evidence = {r['evidence_id']: r for r in old_evidence}
    assert len(evidence) == len(old_evidence), 'duplicate evidence IDs in current tree'
    append, touched = defaultdict(list), set()
    def counts():
        active = [r for _, r in orgs.values() if r['status'] == 'active']
        return {'active_organizations': len(active), **{f: sum(bool(r[f]) for r in active) for f in allowed}}
    before = counts()
    for i, v in enumerate(inputs):
        if v['verdict'] == 'STILL_UNCERTAIN': continue
        assert v['verdict'] == 'VERIFIED'
        field = v['field']; assert field in allowed and v['value'] in allowed[field]
        if field == 'certifications':
            assert v['cert_identity_quote'] and v['cert_expiry_quote']
            assert date.fromisoformat(v['cert_start']) <= date(2026, 11, 6) <= date.fromisoformat(v['cert_expiry'])
        path, row = orgs[v['org_id']]
        assert row['status'] == 'active' and bool(row['tier1_qualifier']) and row['org_id'] in frame_ids
        host = lambda u: urlparse(u if '://' in u else 'https://' + u).hostname.removeprefix('www.')
        assert host(v['source_url']) == host(row['website']), v
        values = row[field].split(';') if row[field] else []
        if v['value'] not in values:
            row[field] = ';'.join(sorted(values + [v['value']])); touched.add(path)
        eid = f'EVD-{240100+i:06d}'; assert int(eid[4:]) <= 259999
        ev = dict(evidence_id=eid, record_table='organizations', record_id=v['org_id'], claim_type='activity',
                  claim_detail=f'{field} {v["value"]}: "{v["quote"]}"', source_class='own_site',
                  source_ref=v['source_url'], observed_date='2026-11-06', tier_effect='supports_A',
                  created_by='codex atlas-L10-markets-certs-tier1', notes=v['note'] or 'Own-site corporate claim; raw quote checked 2026-11-06; record tier unchanged.')
        if eid in evidence: assert evidence[eid] == ev, ('ID collision or changed observation', eid)
        else: append[data / path.name.replace('organizations_', 'evidence_organizations_')].append(ev)
    for path in touched:
        with path.open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(shards[path][0]), lineterminator='\n'); w.writeheader(); w.writerows(shards[path])
    for path, rows in append.items(): append_sorted(path, rows, 'evidence_id')
    print(json.dumps({'before': before, 'after': counts(), 'packet_value_rows': len(inputs),
                      'packet_organizations': len({r['org_id'] for r in inputs if r['verdict'] == 'VERIFIED'}),
                      'tiers': dict(Counter(orgs[oid][1]['verification_tier'] for oid in {r['org_id'] for r in inputs if r['verdict'] == 'VERIFIED'})),
                      'new_evidence_rows': sum(map(len, append.values()))}, indent=2))

if __name__ == '__main__': main()

FILE fetch.py
"""Raw HTML fetch via curl; token matcher reused from the house evidence-repair prep."""
import importlib.util
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('repair_prep', ROOT / 'tasks/evidence-repair-2-2026-11-04/prep.py')
prep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prep)
W = prep.W

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.links = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.skip += 1
        if tag == 'a': self.links.extend(v for k, v in attrs if k == 'href')
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip = max(0, self.skip - 1)
    def handle_data(self, text):
        if not self.skip: self.parts.append(text)

def fetch(url):
    for route in (url, 'https://r.jina.ai/' + url):
        r = subprocess.run(['curl', '--compressed', '-fLsS', '--max-time', '35', '-A', 'Mozilla/5.0', route], capture_output=True)
        if r.returncode: continue
        if r.stdout.startswith(b'%PDF'):
            with tempfile.TemporaryDirectory() as d:
                path = Path(d) / 'certificate.pdf'; path.write_bytes(r.stdout)
                pdf = subprocess.run(['pdftotext', '-layout', str(path), '-'], capture_output=True, check=True)
                return pdf.stdout.decode('utf-8'), [], route
        raw = r.stdout.decode('utf-8', 'replace')
        p = Page(); p.feed(raw)
        text = ' '.join(' '.join(p.parts).split()) if route == url else raw
        if len(text) > 100 and 'Just a moment...' not in text[:500]: return text, p.links, route
    raise RuntimeError('unfetchable: ' + url)

def found(text, quote):
    p, q = W(text), W(quote)
    return bool(q) and any(p[i:i+len(q)] == q for i in range(len(p)-len(q)+1))

if __name__ == '__main__':
    import sys
    text, links, route = fetch(sys.argv[1]); print(route); print(text); print('\nLINKS', '\n'.join(links))

FILE check.py
"""Fetch known answers, check every packet quote, then independently re-fetch a seeded 30-value sample."""
import csv, random, hashlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fetch import fetch, found
HERE = Path(__file__).resolve().parent

def main():
    frame = list(csv.DictReader((HERE / 'frame.csv').open()))
    verdicts = list(csv.DictReader((HERE / 'verdicts.csv').open()))
    assert len(frame) == len(verdicts) == 30, 'frame/verdict yield mismatch'
    assert len({r['org_id'] for r in frame}) == len({r['org_id'] for r in verdicts}) == 30
    assert {r['org_id'] for r in frame} == {r['org_id'] for r in verdicts}
    assert all(r['verdict'] in ('VERIFIED', 'STILL_UNCERTAIN') for r in verdicts)
    cases = [
        ('https://cimaplastics.com/markets.shtml', 'Markets Served Outdoor Power Equipment Medical', True),
        ('https://esterle.com/', 'ISO 9001:2015 certification', True),
        ('https://www.hudsonextrusions.com/', 'iso 9001:2015 Without Design', True),
        ('https://cimaplastics.com/quality.shtml', 'ISO 9001:2015 certified', False),
    ]
    for url, quote, expected in cases:
        text, _, _ = fetch(url)
        assert found(text, quote) == expected, (url, quote)
        assert not found(text, 'L10 deliberately fabricated defect phrase'), url
    print('known answers: 4/4; injected fabricated quotes refused: 4/4')
    rows = list(csv.DictReader((HERE / 'inputs.csv').open()))
    routes = {}
    def retrieve(url):
        text, _, route = fetch(url); routes[url] = route
        return url, text
    pages = dict(ThreadPoolExecutor(6).map(retrieve, sorted({r['source_url'] for r in rows})))
    for r in rows:
        assert found(pages[r['source_url']], r['quote']), r
        if r['verdict'] == 'VERIFIED' and r['field'] == 'certifications':
            assert found(pages[r['source_url']], r['cert_identity_quote']), r
            assert found(pages[r['source_url']], r['cert_expiry_quote']), r
    print('packet quotes:', len(rows), 'passed; zero unavailable pages')
    sample = random.Random(20361106).sample([r for r in rows if r['verdict'] == 'VERIFIED'], 30)
    pages = dict(ThreadPoolExecutor(6).map(retrieve, sorted({r['source_url'] for r in sample})))
    out = [{**r, 'raw': 'yes' if found(pages[r['source_url']], r['quote']) else 'no',
            'route': routes[r['source_url']], 'text_sha256': hashlib.sha256(pages[r['source_url']].encode()).hexdigest()} for r in sample]
    with (HERE / 'audit30.csv').open('w') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator='\n'); w.writeheader(); w.writerows(out)
    assert all(r['raw'] == 'yes' for r in out)
    print('random fresh raw re-check: 30 value rows; 0 errors; seed 20361106')

if __name__ == '__main__': main()

FILE inputs.csv
org_id,field,value,source_url,quote,verdict,note,cert_identity_quote,cert_start,cert_expiry,cert_expiry_quote
ORG-000033,markets_served,agriculture,https://www.lyondellbasell.com/en/our-solutions/markets/,Agriculture From films that optimize plant growth to high-performance irrigation systems and heavy equipment in the field,VERIFIED,,,,,
ORG-000033,markets_served,construction_building_products,https://www.lyondellbasell.com/en/our-solutions/markets/,"Building & construction Our innovative products and technologies enable stronger, safer, more energy-efficient and sustainable structures",VERIFIED,,,,,
ORG-000033,markets_served,consumer_goods_housewares,https://www.lyondellbasell.com/en/our-solutions/markets/,"Consumer goods & lifestyle Our solutions deliver everyday convenience, comfort, safety and performance",VERIFIED,,,,,
ORG-000033,markets_served,appliances,https://www.lyondellbasell.com/en/our-solutions/markets/,"powering products like household appliances, electronics, sports and recreational gear",VERIFIED,,,,,
ORG-000033,markets_served,electronics_electrical,https://www.lyondellbasell.com/en/our-solutions/markets/,"powering products like household appliances, electronics, sports and recreational gear",VERIFIED,,,,,
ORG-000033,markets_served,toys_sporting_goods,https://www.lyondellbasell.com/en/our-solutions/markets/,"powering products like household appliances, electronics, sports and recreational gear",VERIFIED,,,,,
ORG-000033,markets_served,packaging_consumer,https://www.lyondellbasell.com/en/our-solutions/markets/,"Consumer packaging We deliver lightweight, durable solutions",VERIFIED,,,,,
ORG-000033,markets_served,medical_healthcare_general,https://www.lyondellbasell.com/en/our-solutions/markets/,Our broad range of products and technologies empower the healthcare and pharmaceutical industries,VERIFIED,,,,,
ORG-000033,markets_served,pharmaceutical_biotech,https://www.lyondellbasell.com/en/our-solutions/markets/,Our broad range of products and technologies empower the healthcare and pharmaceutical industries,VERIFIED,,,,,
ORG-000033,markets_served,general_industrial,https://www.lyondellbasell.com/en/our-solutions/markets/,"Industrial Our innovative, high-performance solutions enable more efficient and sustainable operations while meeting the industrial sector’s complex demands",VERIFIED,,,,,
ORG-000033,markets_served,infrastructure_civil,https://www.lyondellbasell.com/en/our-solutions/markets/,"Infrastructure Our broad product portfolio helps improve the performance, efficiency, reliability and sustainability of critical infrastructure applications",VERIFIED,,,,,
ORG-000033,markets_served,footwear_apparel,https://www.lyondellbasell.com/en/our-solutions/markets/,Textile & apparel With applications ranging from woven and nonwoven fabrics,VERIFIED,,,,,
ORG-000033,markets_served,aerospace_defense,https://www.lyondellbasell.com/en/our-solutions/markets/transportation/,"Our solutions enhance safety, comfort, and convenience in applications ranging from passenger vehicle component s to solutions in the aerospace, rail, marine and recreational markets.",VERIFIED,,,,,
ORG-000033,markets_served,rail_transportation,https://www.lyondellbasell.com/en/our-solutions/markets/transportation/,"Our solutions enhance safety, comfort, and convenience in applications ranging from passenger vehicle component s to solutions in the aerospace, rail, marine and recreational markets.",VERIFIED,,,,,
ORG-000033,markets_served,marine,https://www.lyondellbasell.com/en/our-solutions/markets/transportation/,"Our solutions enhance safety, comfort, and convenience in applications ranging from passenger vehicle component s to solutions in the aerospace, rail, marine and recreational markets.",VERIFIED,,,,,
ORG-000033,markets_served,automotive_unspecified,https://www.lyondellbasell.com/en/our-solutions/markets/transportation/,Engineered composites Premium thermoset solutions deliver superior durability with luxury aesthetics for automotive and aerospace applications,VERIFIED,,,,,
ORG-000033,markets_served,rv_powersports_trailers,https://www.lyondellbasell.com/en/our-solutions/markets/transportation/,which are ideal for under-hood components and recreational vehicles in demanding environments.,VERIFIED,,,,,
ORG-000033,markets_served,energy_renewables_battery,https://www.lyondellbasell.com/en/our-solutions/markets/transportation/,EV battery components & charging equipment,VERIFIED,,,,,
ORG-000134,markets_served,electronics_electrical,https://novagard.com/about/,"Founded in 1977, Novagard is an innovator and manufacturer of silicone sealants, coatings, lubricants, and foams for the electronics, transportation/automotive, manufacturing, construction, medical, and military markets.",VERIFIED,,,,,
ORG-000134,markets_served,automotive_unspecified,https://novagard.com/about/,"Founded in 1977, Novagard is an innovator and manufacturer of silicone sealants, coatings, lubricants, and foams for the electronics, transportation/automotive, manufacturing, construction, medical, and military markets.",VERIFIED,,,,,
ORG-000134,markets_served,general_industrial,https://novagard.com/about/,"Founded in 1977, Novagard is an innovator and manufacturer of silicone sealants, coatings, lubricants, and foams for the electronics, transportation/automotive, manufacturing, construction, medical, and military markets.",VERIFIED,,,,,
ORG-000134,markets_served,construction_building_products,https://novagard.com/about/,"Founded in 1977, Novagard is an innovator and manufacturer of silicone sealants, coatings, lubricants, and foams for the electronics, transportation/automotive, manufacturing, construction, medical, and military markets.",VERIFIED,,,,,
ORG-000134,markets_served,aerospace_defense,https://novagard.com/about/,"Founded in 1977, Novagard is an innovator and manufacturer of silicone sealants, coatings, lubricants, and foams for the electronics, transportation/automotive, manufacturing, construction, medical, and military markets.",VERIFIED,,,,,
ORG-000134,markets_served,medical_device,https://novagard.com/markets/,"Medical Electronics-grade silicones, tested to ISO 10993, that protect wearable, monitoring, and diagnostic devices",VERIFIED,,,,,
ORG-000134,markets_served,energy_renewables_battery,https://novagard.com/markets/,"Power Technologies Durable silicones delivering dielectric insulation and thermal management that outlast solar, grid, and storage assets outdoors for decades.",VERIFIED,,,,,
ORG-000196,markets_served,plastics_rubber_processors,https://www.goldsmith-eggleton.com/,"What this partnership brings to the rubber industry is total coast-to-coast coverage by an experienced sales force, comprehensive technical and customer support services and an unparalleled portfolio of product offerings.",VERIFIED,,,,,
ORG-000210,markets_served,plastics_rubber_processors,https://www.barentz-na.com/addipel,Markets We Serve Polymer Compounders Polymer Compounders Resin Producers Resin Producers Pre-Blends for Masterbatch Pre-Blends for Masterbatch Rubber Compounders,VERIFIED,,,,,
ORG-000215,markets_served,marine,https://www.adv-polymer.com/industries-applications,Industries We Serve Built Around Real Operating Environments Marine Cargo Tank Coating Systems,VERIFIED,,,,,
ORG-000215,markets_served,rail_transportation,https://www.adv-polymer.com/industries-applications,Rail Proven interior and exterior coating systems for rail tank cars and hopper cars,VERIFIED,,,,,
ORG-000215,markets_served,chemical_mining_metals_processing,https://www.adv-polymer.com/industries-applications,"Industrial Lining systems for chemical storage, containment, and processing environments",VERIFIED,,,,,
ORG-000215,markets_served,general_industrial,https://www.adv-polymer.com/industries-applications,"Industrial Lining systems for chemical storage, containment, and processing environments",VERIFIED,,,,,
ORG-000230,markets_served,appliances,https://www.americanwireandcable.com/about-us.html,While the core business remains appliance wire the product line has been expanded.,VERIFIED,,,,,
ORG-000230,markets_served,automotive_unspecified,https://www.americanwireandcable.com/about-us.html,"Automotive and SAE type wires are manufactured to J-1128, J-1127, and J-378 standards.",VERIFIED,,,,,
ORG-000234,markets_served,construction_building_products,https://www.fiberglass-afi.com/,"Architectural Fiberglas, Inc. is the largest custom fabricator of architectural fiberglass products such as domes, cupolas, columns, cornices, balusters, and custom specialty products.",VERIFIED,,,,,
ORG-000242,markets_served,pharmaceutical_biotech,https://www.barentz-na.com/us,Pharmaceuticals World-class ingredients alongside our deep technical knowledge and highest quality standards,VERIFIED,,,,,
ORG-000242,markets_served,cosmetics_personal_care,https://www.barentz-na.com/us,"Personal Care Creativity differentiates the way we source, formulate and deliver the right ingredients",VERIFIED,,,,,
ORG-000242,markets_served,agriculture,https://www.barentz-na.com/us,Adhesives Agriculture Animal Nutrition Bakery,VERIFIED,,,,,
ORG-000242,markets_served,food_processing_foodservice,https://www.barentz-na.com/us,Plastics Polyurethanes Prepared Foods Printing Inks,VERIFIED,,,,,
ORG-000242,markets_served,plastics_rubber_processors,https://www.barentz-na.com/us,Plastics Polyurethanes Prepared Foods Printing Inks Renewables / Sustainable Rubber / Elastomers,VERIFIED,,,,,
ORG-000242,markets_served,energy_oil_gas,https://www.barentz-na.com/us,Oil & Gas Paper Parts Cleaning,VERIFIED,,,,,
ORG-000242,markets_served,water_wastewater,https://www.barentz-na.com/us,Vehicle Care Wastewater Browse By Product Class,VERIFIED,,,,,
ORG-000242,markets_served,electronics_electrical,https://www.barentz-na.com/us,Drilling Electronics Emulsion Polymers,VERIFIED,,,,,
ORG-000242,markets_served,construction_building_products,https://www.barentz-na.com/us,Composites Confectionery Construction Consumer & Professional Laundry,VERIFIED,,,,,
ORG-000242,markets_served,energy_renewables_battery,https://www.barentz-na.com/us,Bakery Bath & Shower Batteries Beverage Biopharmaceuticals,VERIFIED,,,,,
ORG-000248,markets_served,chemical_mining_metals_processing,https://blairrubber.com/,"Blair Rubber is the only U.S.-based manufacturer with a complete line of corrosion-resistant rubber linings and conveyor belt splice products, offering unparalleled knowledge of chemicals, applications and successful installation procedures, ready for the toughest jobs in the mining, water treatment, chemical and oil/gas industries.",VERIFIED,,,,,
ORG-000248,markets_served,energy_oil_gas,https://blairrubber.com/,"ready for the toughest jobs in the mining, water treatment, chemical and oil/gas industries.",VERIFIED,,,,,
ORG-000248,markets_served,water_wastewater,https://blairrubber.com/,Blair Rubber has developed specialized elastomeric linings for a wide range of water and wastewater treatment equipment,VERIFIED,,,,,
ORG-000248,markets_served,rail_transportation,https://blairrubber.com/,Blair Rubber has over 25 years of experience in rail car and OTR trailer linings,VERIFIED,,,,,
ORG-000316,markets_served,aerospace_defense,https://www.duracote.com/,We have created material solutions to serve the following: Aircraft Interior Products,VERIFIED,,,,,
ORG-000316,markets_served,automotive_unspecified,https://www.duracote.com/,OEM Certified Aviation Products Automotive Interior Materials,VERIFIED,,,,,
ORG-000316,markets_served,construction_building_products,https://www.duracote.com/,"Whether you require automotive coatings, aircraft coating or architectural interior products, Duracote can get the job done.",VERIFIED,,,,,
ORG-000316,markets_served,general_industrial,https://www.duracote.com/,Industrial & Architectural Interior Products,VERIFIED,,,,,
ORG-000345,markets_served,automotive_unspecified,https://www.forestcitytech.com/about/,Who We Serve Automotive Aerospace Lighting & Electronics Industrial Machinery & Equipment Recreational & Consumer,VERIFIED,,,,,
ORG-000345,markets_served,aerospace_defense,https://www.forestcitytech.com/about/,Who We Serve Automotive Aerospace Lighting & Electronics Industrial Machinery & Equipment Recreational & Consumer,VERIFIED,,,,,
ORG-000345,markets_served,electronics_electrical,https://www.forestcitytech.com/about/,Who We Serve Automotive Aerospace Lighting & Electronics Industrial Machinery & Equipment Recreational & Consumer,VERIFIED,,,,,
ORG-000345,markets_served,industrial_machinery,https://www.forestcitytech.com/about/,Who We Serve Automotive Aerospace Lighting & Electronics Industrial Machinery & Equipment Recreational & Consumer,VERIFIED,,,,,
ORG-000345,markets_served,consumer_goods_housewares,https://www.forestcitytech.com/about/,Who We Serve Automotive Aerospace Lighting & Electronics Industrial Machinery & Equipment Recreational & Consumer,VERIFIED,,,,,
ORG-000350,markets_served,construction_building_products,https://www.garlandco.com/,"With the industry's most comprehensive range of high-performance building envelope solutions, you're sure to find options to fit your facility.",VERIFIED,,,,,
ORG-000134,certifications,iatf_16949,https://novagard.com/download/iatf-169492016-with-product-design-certificate/,IATF 16949:2016 with Product Design,VERIFIED,"Smithers04.293.1/IATF0520614, current2024-05-31 through2027-05-30; Novagard Cleveland main site and named distribution support location only; observed2026-11-06.",Novagard Solutions Inc.,2024-05-31,2027-05-30,"May 30, 2027"
ORG-000316,certifications,as9100,https://www.duracote.com/wp-content/uploads/2026/01/AS-Certificate-Duracote-2025.pdf,AS9100:2016 with Design,VERIFIED,"Smithers19.018.1, AS9100:2016 with Design (own home page also styles AS9100RevD); current2024-04-20 through2027-04-19; Ravenna single site polymer reinforced laminates/coatings scope only.",Duracote Corporation,2024-04-20,2027-04-19,"April 19, 2027"

FILE holds.csv
org_id,field,source_url,verdict,settling_fact
ORG-000011,both,https://bridgestoneamericas.com,STILL_UNCERTAIN,"Reviewed corporate home/business page has generic tires/mobility/fleet claims, not an explicit automotive OEM/aftermarket or other end market; need narrower own-site customer/market page."
ORG-000035,both,https://saint-gobain.com,STILL_UNCERTAIN,Own-site direct/Jina route unavailable. Need retrievable own-site industries/quality page; no absence or closure inference.
ORG-000038,both,https://pioneerplasticscorp.com,STILL_UNCERTAIN,Own home/about describe molding and assembly but no explicit end markets; ISO9001:2015 held per superseded-edition/owner-transition battery. Need explicit markets and current eligible certificate.
ORG-000043,both,https://alterra360.com/,STILL_UNCERTAIN,Own-site direct/Jina route unavailable. Need retrievable own-site industries/quality page; no absence or closure inference.
ORG-000052,both,https://harwickstandard.com,STILL_UNCERTAIN,Own-site direct/Jina route unavailable. Need retrievable own-site industries/quality page; no absence or closure inference.
ORG-000103,both,https://hexpolcompounding.com,STILL_UNCERTAIN,Own-site direct/Jina route unavailable. Need retrievable own-site industries/quality page; no absence or closure inference.
ORG-000131,both,https://www.tarkett.com,STILL_UNCERTAIN,Own-site direct/Jina route unavailable. Need retrievable own-site industries/quality page; no absence or closure inference.
ORG-000142,both,https://www.nordson.com,STILL_UNCERTAIN,Own-site direct/Jina route unavailable. Need retrievable own-site industries/quality page; no absence or closure inference.
ORG-000154,both,https://www.lincolnelectric.com,STILL_UNCERTAIN,Own-site direct/Jina route unavailable. Need retrievable own-site industries/quality page; no absence or closure inference.
ORG-000155,both,https://www.eaton.com,STILL_UNCERTAIN,Own-site direct/Jina route unavailable. Need retrievable own-site industries/quality page; no absence or closure inference.
ORG-000157,both,https://www.graftech.com,STILL_UNCERTAIN,Own-site direct/Jina route unavailable. Need retrievable own-site industries/quality page; no absence or closure inference.
ORG-000201,both,http://www.ashtabularubber.com,STILL_UNCERTAIN,Stored ashtabularubber.com returned ASC Engineered Solutions content. Need own-site legal/operator linkage before attributing any ASC market/certificate to Ashtabula Rubber. No website/status edits.
ORG-000207,both,https://realtruck.com/,STILL_UNCERTAIN,Own-site direct/Jina route unavailable. Need retrievable own-site industries/quality page; no absence or closure inference.
ORG-000271,both,https://www.chemtechnologiesltd.com/,STILL_UNCERTAIN,"Home/about describe custom mixing, dispersions and product applications; no explicit customer end-market statement. Need own-site markets/customers page. ISO9001:2015 held pending owner transition ruling."
ORG-000325,both,https://www.huntsman.com/,STILL_UNCERTAIN,"Stored domain serves Huntsman Corporation parent-wide markets, not the specific Advanced Materials Americas subsidiary. Need subsidiary-specific corporate claim before copying parent tags."
ORG-000366,both,https://hc-companies.com/,STILL_UNCERTAIN,Own-site direct/Jina route unavailable. Need retrievable own-site industries/quality page; no absence or closure inference.
ORG-000419,both,https://www.lgchem.com/,STILL_UNCERTAIN,Global LG Chem page not America-entity scoped; need LG Chem America specific claim before corporate market union.
ORG-000438,both,https://www.vestolit.com/,STILL_UNCERTAIN,USA page verifies Mexichem Specialty Resins locations/products but lacks explicit customer end markets; global Vestolit markets must not be copied to subsidiary without attribution.
ORG-000134,certifications,https://novagard.com/about/quality-compliance-and-ehs/,STILL_UNCERTAIN,ISO9001:2015 held under R3c; owner transition-window battery unresolved. IATF16949 current certificate accepted separately.
ORG-000196,certifications,https://goldsmith-eggleton.com/quality/,STILL_UNCERTAIN,ISO9001:2015 and ISO14001:2015 editions superseded; owner transition-window ruling required. ISO45001:2018 claim links image certificate not inspected in this batch; need dated current original with identity/expiry before fill.
ORG-000230,certifications,https://www.americanwireandcable.com/about-us.html,STILL_UNCERTAIN,"UL/CSA product wire approvals are product compliance, never facility certification (R3c). Need current facility certificate; no product approval filled."
ORG-000345,certifications,https://www.forestcitytech.com/,STILL_UNCERTAIN,ISO9001/ISO14001 edition-less claims; R12 bars filling. Need current original certificate with edition/dates.
ORG-000345,markets_served,https://www.forestcitytech.com/about/,STILL_UNCERTAIN,"Recreational category does not specify lawn/garden, sports/toys or RV. Need narrower own statement/owner mapping; only explicit Consumer and other market labels filled."
ORG-000215,markets_served,https://www.adv-polymer.com/industries-applications,STILL_UNCERTAIN,Unqualified Energy and ISO tank-container labels do not establish oil/gas or a precise controlled end market. Need narrower own statement; no invented tag.
ORG-000242,markets_served,https://www.barentz-na.com/us,STILL_UNCERTAIN,"Animal Nutrition, industrial cleaning, paper, printing and other own selector categories not mapped unless a precise existing controlled term; need narrower source or owner vocabulary ruling. No note column for off-vocabulary org markets."

FILE counts.json
{
  "before": {
    "active_organizations": 4884,
    "markets_served": 394,
    "certifications": 47
  },
  "after": {
    "active_organizations": 4884,
    "markets_served": 406,
    "certifications": 49
  },
  "packet_value_rows": 60,
  "packet_organizations": 12,
  "tiers": {
    "A": 8,
    "B": 3,
    "C": 1
  },
  "new_evidence_rows": 60
}

FILE frame.json
{
  "active_tier1_organizations": 1261,
  "markets_populated": 162,
  "certifications_populated": 13,
  "eligible_blank_markets_with_website_excluding_two_prior_holds": 860,
  "selected": 30,
  "selection": "PIC18 first, then org_id ascending; first30 blank-markets, website HTTP; excludes ORG62/101 prior holds without new evidence"
}
