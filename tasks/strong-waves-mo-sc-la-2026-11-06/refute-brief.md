Adversarial completion review. Try to REFUTE this narrow lane packet; end APPROVE or REFUTE, with material findings and what you inspected. Do not demand that explicitly held candidates be created. All 36 must have a verdict, but uncertainty is valid. You may inspect the local worktree read-only if available. Do not edit files or run builders.
Task: create verified STRONG establishment clusters in MO (15), SC (14), LA (7); named exact census and T3 rise. IDs explicitly owner-reserved ORG9000..9499 SITE12000..12999 EVD160000..169999, superseding max-id default. New org C; federal plant + own raw witness site B, federal-only C. Existing federal packets permitted. ECHO/FRS identifiers only notes. No full raw pages committed (may contain contact data). Script/style excluded in matcher; 3 known answers and 3 inserted quote defects pass. Every cluster is in verdicts exactly once.
Result: 15 new orgs C; 19 new sites (18 B, 1 C), 210 evidence observations; 4 held-parent alias updates. 1 REJECT (PIDC alumina, B-SCOPE), 16 named holds. No closure REJECT. validate.py 0 errors. check.py all passes. Two pre-existing CRLF federal-frame files intentionally untouched/unstaged. Scope follows owner B-SCOPE 2026-11-04; precursor-only would be ring3 but Cornerstone held over current status. No registry/qualifier/status/ownership edits. Only held org edits = aliases. HQ/county left blank. Parent-held sites: Nike ORG003555, JM Eagle survivor ORG002261, Insulfab ORG006173, Yokohama TWS ORG001336.
Assess evidence fidelity, operator/site matching, scope, tier, dedupe, ID/replay safety, and count honesty. Broad public primary-site activity witnesses may be corroborated by site-specific federal records, per merged Michigan recipe; a plant-only own-site witness is allowed under that recipe. Flag unsupported inferences, not stylistic preferences.


FILE tasks/strong-waves-mo-sc-la-2026-11-06/LANE_BRIEF.md
# L3 STRONG waves — MO, SC, LA

Owner assignment 2026-11-06: atlas-L3-strong-mo-sc-la; branch agent/codex/strong-waves-mo-sc-la.
Reserved ORG-009000–009499, SITE-012000–012999, EVD-160000–169999 supersede ordinary max-ID allocation for this lane.
Integrator application delegated to this lane; controller thr_9i2c6byhcz alone merges and changes task status.

Acceptance: exactly one legal verdict for each lead-fusion STRONG cluster in MO/SC/LA (15/14/7 clusters); create verified
establishments under held operators where appropriate, with per-claim evidence. No existing evidence edits. No registry
links or derived qualifier edits. Raw-verified own-site + federal establishment = B; new org C; employer filings alone
never establish a plant. Unsettled scope/status/identity goes to holds. County and HQ remain blank without direct evidence.
B-ALIAS registrant names enter trade_names with a federal evidence observation. Follow successor chains to surviving records.
One commit per state; one PR; named check validate.py zero errors + check.py census/T3 checks. Both Codex and Grok deep refutes.

First user: controller/research integrator reviewing this PR. Intended first use: merge review on 2026-11-06; controller owns
any subsequent usage finding. This lane does not open or close tracker tasks.

Research follows the Michigan STRONG method, using the current AGENTS verdict grammar (VERIFIED with a held_org_id column,
not the older VERIFIED_NEW_ORG/VERIFIED_NEW_SITE spellings). Evidence-repair prep.py's token matcher is reused for raw quotes;
curl with browser UA, Jina fallback. Missing ownership-status-2 rawcheck_tool.py is replaced by the named evidence-repair fallback.


FILE tasks/strong-waves-mo-sc-la-2026-11-06/build.py
#!/usr/bin/env python3
"""Idempotent integrator application of reviewed L3 STRONG verdicts.
Run from repository root: python3 tasks/strong-waves-mo-sc-la-2026-11-06/build.py --state MO --apply
Stable IDs are input-index offsets within the owner's reserved block, never gap-filled.
"""
import argparse, csv, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
DATE='2026-11-06'; BY='atlas-L3-strong-mo-sc-la'

def read(p):
    with open(p,newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def write(p,rows,fields):
    with open(p,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--state',choices=['MO','SC','LA'],required=True);ap.add_argument('--apply',action='store_true');a=ap.parse_args()
    inputs={r['cluster_id']:r for r in read(HERE/'input.csv')};vs=read(HERE/'verdicts.csv')
    assert len(inputs)==len(vs)==36 and Counter(r['cluster_id'] for r in vs)==Counter(inputs.keys()), 'verdict census mismatch'
    raw={r['cluster_id']:r for r in read(HERE/'rawcheck.csv')}
    ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
    osha={r['est_key']:r for r in read(ROOT/'tasks/osha-spine-2026-11-01/establishments.csv')}
    plans={r['ein']:r for r in read(ROOT/'tasks/form5500-spine-2026-11-01/sponsors.csv')}
    orgs={r['org_id']:(p,r) for p in (ROOT/'data').glob('organizations_*.csv') for r in read(p)}
    additions=defaultdict(list);alias_updates={};alloc=[]
    for idx,v in enumerate(vs):
        if v['state']!=a.state or v['verdict']!='VERIFIED':continue
        c=inputs[v['cluster_id']];assert raw[v['cluster_id']]['raw']=='yes' and v['own_quote']
        fed=[];aliases=[];code='';last=''
        for token in c['sources_with_ids'].split(';'):
            family,ident=token.split(':',1)
            if family=='ITA':
                r=ita[ident];ref=f"OSHA ITA Form 300A CY{r['year_filing_for']} establishment {ident} ({r['establishment_name']})"
                fed.append((ref,r['date_submitted'][:10]));aliases += [r['establishment_name'],r['company_name']]
                if not code:code=r['naics_code']
            elif family=='OSHA':
                r=osha[ident];ref=f"OSHA inspection {r['latest_activity_nr']} ({r['name']}), https://www.osha.gov/ords/imis/establishment.inspection_detail?id={r['latest_activity_nr']}"
                fed.append((ref,r['latest_inspection'][:10]));aliases.append(r['name'])
                if not code:code=r['naics_latest']
            elif family=='F5500':aliases.append(plans[ident]['sponsor_name'])
        assert not code or re.fullmatch(r'\d{6}',code), (v['cluster_id'],code)
        aliases=list(dict.fromkeys(x.strip() for x in aliases if x.strip()))
        own=v['own_url'];quote=v['own_quote'];ring=v['ring']
        # Employer filings do not attest plant operations. Without ITA/OSHA the own-site record stays C.
        tier='B' if fed else 'C';eff='supports_'+tier
        oid=v['held_org_id'] or f'ORG-{9000+idx:06d}';sid=f'SITE-{12000+idx:06d}';eid=160000+idx*100
        assert 9000<=int(oid[4:])<=9499 or v['held_org_id']
        assert 12000<=int(sid[5:])<=12999
        if oid.startswith('NEW:'):raise AssertionError('cross-state parent requires resolved ID')
        name=orgs[oid][1]['legal_name'] if oid in orgs else c['best_name']
        source='; '.join([own]+[f[0] for f in fed]);last=max([f[1] for f in fed]+[DATE])
        note=f"L3 STRONG {v['cluster_id']}; held federal packet identifiers (not fresh registry evidence): {c['sources_with_ids']}."
        def E(table,rid,claim,detail,ref=own,cls='own_site',date=DATE,effect=eff,shard=a.state):
            nonlocal eid
            assert 160000<=eid<=169999
            additions[f'evidence_{table}_{shard}.csv'].append(dict(evidence_id=f'EVD-{eid:06d}',record_table=table,record_id=rid,claim_type=claim,claim_detail=detail,source_class=cls,source_ref=ref,observed_date=date,tier_effect=effect,created_by=BY,notes=f'Reviewed {DATE}; '+note));eid+=1
        if not v['held_org_id']:
            aliases=[x for x in aliases if x!=name]
            org=dict(org_id=oid,legal_name=name,trade_names='; '.join(aliases),entity_type='unknown',ring_primary=ring,hq_country='',hq_in_scope='national_us',naics_primary=code,naics_primary_source_type='government_filing' if code else '',naics_primary_source_name=fed[0][0] if code else '',naics_confidence='medium' if code else '',website=own,description_1line=f"Polymer establishment operator in {c['city']}, {a.state}.",pic_relevance='potential_member',status='active',sources=source,verification_tier='C',last_verified=DATE,created_by=BY,notes=note+' HQ not independently established; left blank.',last_activity_evidence_date=DATE,liveness_signal='operating_evidence',monitor_watch='false')
            additions['organizations_US.csv'].append(org)
            for claim,detail in [('existence',f"legal_name {name}; website {own}; federal registrant aliases {'; '.join(aliases)}"),('scope',f"ring_primary {ring}: {quote}"),('activity',f"operator of polymer establishment: {quote}"),('liveness','Live operator page checked '+DATE)]:E('organizations',oid,claim,detail,effect='supports_C',shard='US')
            if code:E('organizations',oid,'code',f'naics_primary {code}; establishment filing, not company disclosure',fed[0][0],'government_filing',fed[0][1],'supports_C',shard='US')
        else:
            assert oid in orgs and not orgs[oid][1]['successor_org_id'], oid
            p,r=orgs[oid];old=[x.strip() for x in r['trade_names'].split(';') if x.strip()]
            new=[x for x in aliases if x!=name and x not in old]
            if new:
                alias_updates.setdefault(p,{})[oid]='; '.join(old+new)
            # Alias observations cite the federal registrant, not the own-site brand.
            alias_ref=fed[0][0] if fed else own
            if any(x!=name for x in aliases):
                E('organizations',oid,'existence','Federal registrant aliases: '+'; '.join(x for x in aliases if x!=name),alias_ref,'government_filing' if fed else 'own_site',fed[0][1] if fed else DATE,'supports_C',shard=p.stem.split('_')[-1])
        site=dict(site_id=sid,org_id=oid,site_name=f"{name} - {c['city']}",site_type='manufacturing_plant',street_address=c['street'],city=c['city'],state=a.state,zip=c['zip5'],country='US',ring_primary=ring,naics_primary=code,naics_primary_source_type='government_filing' if code else '',naics_confidence='medium' if code else '',operating_status='active',sources=source,verification_tier=tier,last_verified=DATE,created_by=BY,notes=note+' County not settled from physical-address evidence; left blank.')
        additions[f'sites_{a.state}.csv'].append(site)
        for claim,detail in [('existence',f"{name} establishment"),('scope',f"ring_primary {ring}: {quote}"),('activity',quote),('parent',f'org_id {oid}: federal registrant/own-site operator linkage'),('liveness','Live operator witness checked '+DATE)]:E('sites',sid,claim,detail)
        if fed:
            E('sites',sid,'address',f"{c['street']}, {c['city']}, {a.state} {c['zip5']}",fed[0][0],'government_filing',fed[0][1])
            E('sites',sid,'code',f'naics_primary {code}',fed[0][0],'government_filing',fed[0][1])
        else:
            E('sites',sid,'address',f"{c['street']}, {c['city']}, {a.state} {c['zip5']}")
        alloc.append(dict(cluster_id=v['cluster_id'],org_id=oid,new_org=str(not bool(v['held_org_id'])).lower(),site_id=sid,tier=tier))
    if a.apply:
        for filename,rows in additions.items():
            path=ROOT/'data'/filename;pk=next(iter(rows[0]));old={r[pk]:r for r in read(path)}
            fresh=[]
            for r in rows:
                if r[pk] in old:
                    # Re-running must be a no-op; a changed packet is a conflict, never an evidence rewrite.
                    assert all(old[r[pk]].get(k,'')==val for k,val in r.items()), (filename,r[pk])
                else:fresh.append(r)
            if fresh:append_sorted(path,fresh,pk)
        for p,changes in alias_updates.items():
            rows=read(p)
            for r in rows:
                if r['org_id'] in changes:r['trade_names']=changes[r['org_id']]
            write(p,rows,list(rows[0]))
        write(HERE/f'allocations_{a.state}.csv',alloc,['cluster_id','org_id','new_org','site_id','tier'])
    print(a.state,dict(Counter({f:len(r) for f,r in additions.items()})), 'alias updates',sum(len(x) for x in alias_updates.values()))
if __name__=='__main__':main()


FILE tasks/strong-waves-mo-sc-la-2026-11-06/check.py
#!/usr/bin/env python3
"""Named L3 completion check: exact census, applied creates, raw quotes, T3 and unique reserved IDs."""
import csv, hashlib, importlib.util, json
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def read(p):
    with open(p,newline='') as f:return list(csv.DictReader(f))
def census(source,verdicts):
    assert Counter(r['cluster_id'] for r in verdicts)==Counter(r['cluster_id'] for r in source), 'missing/duplicated verdict'
    assert len({r['cluster_id'] for r in verdicts})==len(verdicts)
    assert all(r['verdict'] in {'VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF'} and r['deciding_fact'] for r in verdicts)
def main():
    source=[r for r in read(ROOT/'tasks/lead-fusion-2026-11-01/clusters.csv') if r['state'] in ('MO','SC','LA') and r['class']=='STRONG']
    verdicts=read(HERE/'verdicts.csv');census(source,verdicts)
    assert Counter(r['cluster_id'] for r in read(HERE/'input.csv'))==Counter(r['cluster_id'] for r in source)
    for defect in (verdicts[:-1],verdicts+[verdicts[0]],verdicts[:-1]+[verdicts[0]]):
        try:census(source,defect)
        except AssertionError:pass
        else:raise AssertionError('census gate failed injected defect')
    raw={r['cluster_id']:r for r in read(HERE/'rawcheck.csv')}
    allocations=[r for st in ('MO','SC','LA') for r in read(HERE/f'allocations_{st}.csv')]
    assert Counter(r['cluster_id'] for r in allocations)==Counter(r['cluster_id'] for r in verdicts if r['verdict']=='VERIFIED')
    sites={r['site_id']:r for p in (ROOT/'data').glob('sites_*.csv') for r in read(p)}
    for r in allocations:
        s=sites[r['site_id']];assert s['org_id']==r['org_id'] and s['verification_tier']==r['tier']
        assert raw[r['cluster_id']]['raw']=='yes'
        assert 12000<=int(r['site_id'][5:])<=12999
    for pattern,key in [('organizations_*.csv','org_id'),('sites_*.csv','site_id'),('evidence_*.csv','evidence_id')]:
        ids=[r[key] for p in (ROOT/'data').glob(pattern) for r in read(p)]
        assert len(ids)==len(set(ids)),(pattern,'duplicate ids')
    spec=importlib.util.spec_from_file_location('qcew',ROOT/'scripts/build_qcew_denominators.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    nums=m.atlas_numerators(str(ROOT));before=json.loads((HERE/'qcew-before.json').read_text());after={}
    for st,b in before.items():
        n=nums[(st,'326')][1];assert n>b['strict_before'],(st,n,b)
        after[st]={**b,'strict_after':n,'share_before':b['strict_before']/float(b['qcew_2023']),'share_after':n/float(b['qcew_2023'])}
    (HERE/'qcew-after.json').write_text(json.dumps(after,indent=2)+'\n')
    print('PASS: 36/36 exact STRONG verdicts; census defects 3/3 caught;',len(allocations),'applied sites; IDs unique; NAICS 326 strict/QCEW rises in MO/SC/LA')
    print(json.dumps(after,indent=2))
if __name__=='__main__':main()


FILE tasks/strong-waves-mo-sc-la-2026-11-06/prepare.py
#!/usr/bin/env python3
"""Raw-check sources using the evidence-repair token matcher and curl/Jina routes.
No data writes. Known answers run before fetching the wave.
"""
import csv, importlib.util, json, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from research import SOURCES
spec = importlib.util.spec_from_file_location('repair', ROOT/'tasks/evidence-repair-2-2026-11-04/prep.py')
repair = importlib.util.module_from_spec(spec); spec.loader.exec_module(repair)
W = repair.W

class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip = max(0, self.skip - 1)
    def handle_data(self, s):
        if not self.skip: self.parts.append(s)

def contains(text, quote):
    words, q = W(text), W(quote)
    return bool(q) and any(words[i:i+len(q)] == q for i in range(len(words)-len(q)+1))

def fetch(pair):
    key, (url, quote, *_) = pair
    attempts = []
    for route in (url, 'https://r.jina.ai/'+url):
        r = subprocess.run(['curl', '-fLsS', '--max-time', '35', '-A', 'Mozilla/5.0', route], capture_output=True, text=True)
        attempts.append(f'{route}: curl={r.returncode}')
        if r.returncode: continue
        t = Text(); t.feed(r.stdout); text = ' '.join(t.parts)
        if contains(text, quote):
            # Cache only outside the repository: pages may contain personal contact details.
            Path('/tmp/l3-'+key+'.txt').write_text(text)
            return dict(cluster_id='LF-'+key, url=url, quote=quote, raw='yes', route=route, attempts='; '.join(attempts))
    return dict(cluster_id='LF-'+key, url=url, quote=quote, raw='not_verified', route='', attempts='; '.join(attempts))

def main():
    # Three known published scope witnesses, independently inspected before using this matcher.
    answers = [('MO-00088', 'We manufacture FDA approved polyethylene blown film using prime resins.'),
               ('MO-00023', 'Steering wheels, Airbags, Side Molding, Interior & Exterior plastic trim components for automobiles.'),
               ('SC-00082', 'precision machining and stamping of engineering and high-performance plastic materials')]
    for key, quote in answers:
        r = fetch((key, SOURCES[key])); assert r['raw'] == 'yes', (key, r)
        text = Path('/tmp/l3-'+key+'.txt').read_text()
        assert contains(text, quote), key
        assert not contains(text, quote+' nonexistentdefect7731'), key
    with ThreadPoolExecutor(max_workers=6) as ex: rows = list(ex.map(fetch, SOURCES.items()))
    with (HERE/'rawcheck.csv').open('w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=rows[0], lineterminator='\n'); w.writeheader(); w.writerows(rows)
    print('known answers 3/3; injected quote defects rejected 3/3; raw checks', len(rows))
if __name__ == '__main__': main()


FILE tasks/strong-waves-mo-sc-la-2026-11-06/verdicts.csv
cluster_id,state,verdict,duplicate_of,held_org_id,ring,own_url,own_quote,deciding_fact
LF-MO-00006,MO,STILL_UNCERTAIN,,,,https://www.aerofil.com/about-us/facility/,"14 packaging lines that support high speed aerosol, liquid and three stage filling",Need a polymer formulation or captive shaping witness; contract filling alone does not settle scope.
LF-MO-00017,MO,VERIFIED,,,2,https://watsoncoatings.com/,Your Trusted Coating Manufacturer.,Federal establishment corroborated by raw-checked operator page.
LF-MO-00018,MO,STILL_UNCERTAIN,,,2,https://www.sterlinglacquer.com/,,Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote.
LF-MO-00023,MO,VERIFIED,,,1,https://www.tgmissouri.com/profile/,"Steering wheels, Airbags, Side Molding, Interior & Exterior plastic trim components for automobiles.",Federal establishment corroborated by raw-checked operator page.
LF-MO-00031,MO,VERIFIED,,,2,https://www.davispaint.com/,Private Labeling & Custom Manufacturing,Federal establishment corroborated by raw-checked operator page.
LF-MO-00053,MO,STILL_UNCERTAIN,,,,https://www.chemispherecorp.com/,,Need polymer-binder formulation at Clifton Avenue; broad chemical blending and distribution does not settle site scope.
LF-MO-00088,MO,VERIFIED,,,1,https://manchesterpkg.com/,We manufacture FDA approved polyethylene blown film using prime resins.,Federal establishment corroborated by raw-checked operator page.
LF-MO-00100,MO,VERIFIED,,,1,https://www.tntplastics.com/,Custom Polyethylene Bags & Film Manufacturer,Federal establishment corroborated by raw-checked operator page.
LF-MO-00120,MO,STILL_UNCERTAIN,,,1,https://ati-1.com/,,Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote.
LF-MO-00121,MO,VERIFIED,,ORG-003555,1,https://careers.nike.com/engineer-ii-product-development-design-air-manufacturing-innovation/job/R-96474,commercializing and manufacturing Nike Air products,Federal establishment corroborated by raw-checked operator page.
LF-MO-00153,MO,VERIFIED,,,2,https://www.uspaint.com/about-us/,"U.S. Paint has delivered vibrant, ultra-high-quality paints and coatings to manufacturers and applicators around the world.",Federal establishment corroborated by raw-checked operator page.
LF-MO-00165,MO,STILL_UNCERTAIN,,,1,https://silgandispensing.com/our-locations/,,Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote.
LF-MO-00241,MO,VERIFIED,,ORG-002261,1,https://jmeagle.com/locations,"Columbia, MO 65202",Federal establishment corroborated by raw-checked operator page.
LF-MO-00286,MO,VERIFIED,,,1,https://www.koller-craft.com/about,A family owned and operated full service provider of injection molded plastic components.,Federal establishment corroborated by raw-checked operator page.
LF-MO-00289,MO,STILL_UNCERTAIN,,,1,https://investors.atkore.com/investors/news/news-details/2022/Atkore-Inc.-Announces-Acquisition-of-United-Poly-Systems/default.aspx,,Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote.
LF-SC-00047,SC,STILL_UNCERTAIN,,,,https://www.atotech.com/usa/,"Our history in the USA encompasses decades of advancements in metal finishing, electronics and industrial specialty chemicals.",Need polymer-specific production or qualifying polymer value-chain focus at Rock Hill; metal finishing alone is insufficient.
LF-SC-00082,SC,VERIFIED,,ORG-006173,1,https://insulfab.com/about,precision machining and stamping of engineering and high-performance plastic materials,Federal establishment corroborated by raw-checked operator page.
LF-SC-00113,SC,VERIFIED,,,1,https://www.emsgrivory.com/en/ems-grivory/about-ems-grivory/company-history/,EMS starts production of polyamide materials in Sumter,Federal establishment corroborated by raw-checked operator page.
LF-SC-00129,SC,STILL_UNCERTAIN,,,2,https://www.mocom.eu/en/about/who-we-are,,Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote.
LF-SC-00147,SC,VERIFIED,,,2,https://wikoff.com/company/,Wikoff began as a small ink and coatings manufacturer,Federal establishment corroborated by raw-checked operator page.
LF-SC-00198,SC,STILL_UNCERTAIN,,,,https://www.agfa.com/corporate/news-item/agfa-shuts-down-its-bushy-park-site-as-part-of-its-plan-to-optimize-the-global-cost-base-of-its-film-activities/,,Closure reporting found; need dated primary outcome and address-matched EFAST2 check before any closure REJECT. No active create.
LF-SC-00206,SC,STILL_UNCERTAIN,,,1,https://ati-1.com/,,Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote.
LF-SC-00214,SC,VERIFIED,,,1,https://cr.rebuildmanufacturing.com/,"Our thermoset composites provide superior strength, corrosion-resistance, and durability for demanding industrial applications",Federal establishment corroborated by raw-checked operator page.
LF-SC-00253,SC,VERIFIED,,ORG-001336,1,https://www.yokohama-tws.com/en/news/trelleborg-tires-news/trelleborg-tires-manufacturing-spartanburg,from the preparation of semi-finished products through tire building and curing,Federal establishment corroborated by raw-checked operator page.
LF-SC-00258,SC,REJECT,,,,https://www.pidc.com/company/history,PIDC launches Alumax,SC regulator identifies Spartanburg output as alumina-based products; B-SCOPE 2026-11-04 excludes inorganic oxide additives. https://des.sc.gov/sites/des/files/media/document/FINAL%20Board%20June%202018.pdf
LF-SC-00302,SC,STILL_UNCERTAIN,,,,https://www.hydrite.com/Contact/Locations.htm,"Our Laurens, SC plant manufacturers foam control products",Need Laurens foam-control product binder/composition; silicone/polymer formulation versus nonpolymer defoamer not settled.
LF-SC-00313,SC,VERIFIED,,,1,https://www.perlon.com/en/portrait-perlon/current-vacancies-2/,EXTRUSION OPERATOR,Federal establishment corroborated by raw-checked operator page.
LF-SC-00326,SC,STILL_UNCERTAIN,,,,https://www.multiplastics.com/,plastics,Need primary operator identity linking Curd Enterprises to Multiplastics and current manufacturing at 476 Long Point Road.
LF-SC-00358,SC,STILL_UNCERTAIN,,,,https://www.puraquaproducts.com/about-us,"Today, the chlorinators and pH systems manufactured at PurAqua are seen in facilities around the globe.",Need captive polymer processing or site-grain Ring 4 two-of-three test; chlorination equipment alone is insufficient.
LF-LA-00001,LA,VERIFIED,,,2,https://www.cmp.co.jp/en/company/group_western-countries/,"CMP COATINGS, INC.",Federal establishment corroborated by raw-checked operator page.
LF-LA-00029,LA,STILL_UNCERTAIN,,,,https://www.ecovyst.com/ecoservices/,sulfuric acid,Need dedicated polymer line or polymer-specific value-chain witness; sulfuric acid regeneration alone is insufficient.
LF-LA-00054,LA,VERIFIED,,,1,https://sunspecialtyproducts.com/about-us/,Advanced manufacturing methodology patent issued for thermoset polymer processes and nanocomposites.,Federal establishment corroborated by raw-checked operator page.
LF-LA-00183,LA,STILL_UNCERTAIN,,,,https://www.berryglobal.com/,Berry,"Need current operator/site identity after Berry/Amcor transaction, and plant-specific polymer scope at 4611 Central Avenue."
LF-LA-00234,LA,STILL_UNCERTAIN,,,,https://cornerstonechemco.com/acrylonitrile,,"Precursor-only Ring 3 precedent applies, but dated current operating outcome and operator after restructuring must be settled before active create."
LF-LA-00264,LA,VERIFIED,,,1,https://www.ashindustries.com/,"Plastic, metal, and silicone injection molding—all in one facility.",Federal establishment corroborated by raw-checked operator page.
LF-LA-00305,LA,VERIFIED,,,1,https://www.indplastics.com/en/,"national supplier of stock and custom molded PTFE rod, tube, plate, sheets, gaskets and machined parts",Federal establishment corroborated by raw-checked operator page.


FILE tasks/strong-waves-mo-sc-la-2026-11-06/rawcheck.csv
cluster_id,url,quote,raw,route,attempts
LF-MO-00006,https://www.aerofil.com/about-us/facility/,"14 packaging lines that support high speed aerosol, liquid and three stage filling",yes,https://www.aerofil.com/about-us/facility/,https://www.aerofil.com/about-us/facility/: curl=0
LF-MO-00017,https://watsoncoatings.com/,Your Trusted Coating Manufacturer.,yes,https://watsoncoatings.com/,https://watsoncoatings.com/: curl=0
LF-MO-00018,https://www.sterlinglacquer.com/,Sterling,not_verified,,https://www.sterlinglacquer.com/: curl=35; https://r.jina.ai/https://www.sterlinglacquer.com/: curl=56
LF-MO-00023,https://www.tgmissouri.com/profile/,"Steering wheels, Airbags, Side Molding, Interior & Exterior plastic trim components for automobiles.",yes,https://www.tgmissouri.com/profile/,https://www.tgmissouri.com/profile/: curl=0
LF-MO-00031,https://www.davispaint.com/,Private Labeling & Custom Manufacturing,yes,https://www.davispaint.com/,https://www.davispaint.com/: curl=0
LF-MO-00053,https://www.chemispherecorp.com/,From straight paints and coatings to custom blended industrial degreasers,not_verified,,https://www.chemispherecorp.com/: curl=56; https://r.jina.ai/https://www.chemispherecorp.com/: curl=56
LF-MO-00088,https://manchesterpkg.com/,We manufacture FDA approved polyethylene blown film using prime resins.,yes,https://manchesterpkg.com/,https://manchesterpkg.com/: curl=0
LF-MO-00100,https://www.tntplastics.com/,Custom Polyethylene Bags & Film Manufacturer,yes,https://www.tntplastics.com/,https://www.tntplastics.com/: curl=0
LF-MO-00120,https://ati-1.com/,"fabricator, distributor and manufacturer of thermosets, thermoplastics and other non-metallic materials",not_verified,,https://ati-1.com/: curl=60; https://r.jina.ai/https://ati-1.com/: curl=56
LF-MO-00121,https://careers.nike.com/engineer-ii-product-development-design-air-manufacturing-innovation/job/R-96474,commercializing and manufacturing Nike Air products,yes,https://careers.nike.com/engineer-ii-product-development-design-air-manufacturing-innovation/job/R-96474,https://careers.nike.com/engineer-ii-product-development-design-air-manufacturing-innovation/job/R-96474: curl=0
LF-MO-00153,https://www.uspaint.com/about-us/,"U.S. Paint has delivered vibrant, ultra-high-quality paints and coatings to manufacturers and applicators around the world.",yes,https://www.uspaint.com/about-us/,https://www.uspaint.com/about-us/: curl=0
LF-MO-00165,https://silgandispensing.com/our-locations/,"Silgan Dispensing Systems Corporation 11901 Grandview Road Grandview, MO 64030 USA",not_verified,,https://silgandispensing.com/our-locations/: curl=56; https://r.jina.ai/https://silgandispensing.com/our-locations/: curl=56
LF-MO-00241,https://jmeagle.com/locations,"Columbia, MO 65202",yes,https://jmeagle.com/locations,https://jmeagle.com/locations: curl=0
LF-MO-00286,https://www.koller-craft.com/about,A family owned and operated full service provider of injection molded plastic components.,yes,https://www.koller-craft.com/about,https://www.koller-craft.com/about: curl=0
LF-MO-00289,https://investors.atkore.com/investors/news/news-details/2022/Atkore-Inc.-Announces-Acquisition-of-United-Poly-Systems/default.aspx,"United Poly Systems has manufacturing locations in Springfield, Missouri, and Albuquerque, New Mexico",not_verified,,https://investors.atkore.com/investors/news/news-details/2022/Atkore-Inc.-Announces-Acquisition-of-United-Poly-Systems/default.aspx: curl=56; https://r.jina.ai/https://investors.atkore.com/investors/news/news-details/2022/Atkore-Inc.-Announces-Acquisition-of-United-Poly-Systems/default.aspx: curl=56
LF-SC-00047,https://www.atotech.com/usa/,"Our history in the USA encompasses decades of advancements in metal finishing, electronics and industrial specialty chemicals.",yes,https://www.atotech.com/usa/,https://www.atotech.com/usa/: curl=0
LF-SC-00082,https://insulfab.com/about,precision machining and stamping of engineering and high-performance plastic materials,yes,https://insulfab.com/about,https://insulfab.com/about: curl=0
LF-SC-00113,https://www.emsgrivory.com/en/ems-grivory/about-ems-grivory/company-history/,EMS starts production of polyamide materials in Sumter,yes,https://www.emsgrivory.com/en/ems-grivory/about-ems-grivory/company-history/,https://www.emsgrivory.com/en/ems-grivory/about-ems-grivory/company-history/: curl=0
LF-SC-00129,https://www.mocom.eu/en/about/who-we-are,manufacturer of high-performance polymers and innovative compounds for the plastics-processing industry,not_verified,,https://www.mocom.eu/en/about/who-we-are: curl=0; https://r.jina.ai/https://www.mocom.eu/en/about/who-we-are: curl=56
LF-SC-00147,https://wikoff.com/company/,Wikoff began as a small ink and coatings manufacturer,yes,https://wikoff.com/company/,https://wikoff.com/company/: curl=0
LF-SC-00198,https://www.agfa.com/corporate/news-item/agfa-shuts-down-its-bushy-park-site-as-part-of-its-plan-to-optimize-the-global-cost-base-of-its-film-activities/,Bushy Park,not_verified,,https://www.agfa.com/corporate/news-item/agfa-shuts-down-its-bushy-park-site-as-part-of-its-plan-to-optimize-the-global-cost-base-of-its-film-activities/: curl=0; https://r.jina.ai/https://www.agfa.com/corporate/news-item/agfa-shuts-down-its-bushy-park-site-as-part-of-its-plan-to-optimize-the-global-cost-base-of-its-film-activities/: curl=56
LF-SC-00206,https://ati-1.com/,"fabricator, distributor and manufacturer of thermosets, thermoplastics and other non-metallic materials",not_verified,,https://ati-1.com/: curl=60; https://r.jina.ai/https://ati-1.com/: curl=56
LF-SC-00214,https://cr.rebuildmanufacturing.com/,"Our thermoset composites provide superior strength, corrosion-resistance, and durability for demanding industrial applications",yes,https://cr.rebuildmanufacturing.com/,https://cr.rebuildmanufacturing.com/: curl=0
LF-SC-00253,https://www.yokohama-tws.com/en/news/trelleborg-tires-news/trelleborg-tires-manufacturing-spartanburg,from the preparation of semi-finished products through tire building and curing,yes,https://www.yokohama-tws.com/en/news/trelleborg-tires-news/trelleborg-tires-manufacturing-spartanburg,https://www.yokohama-tws.com/en/news/trelleborg-tires-news/trelleborg-tires-manufacturing-spartanburg: curl=0
LF-SC-00258,https://www.pidc.com/company/history,PIDC launches Alumax,yes,https://www.pidc.com/company/history,https://www.pidc.com/company/history: curl=0
LF-SC-00302,https://www.hydrite.com/Contact/Locations.htm,"Our Laurens, SC plant manufacturers foam control products",yes,https://www.hydrite.com/Contact/Locations.htm,https://www.hydrite.com/Contact/Locations.htm: curl=0
LF-SC-00313,https://www.perlon.com/en/portrait-perlon/current-vacancies-2/,EXTRUSION OPERATOR,yes,https://www.perlon.com/en/portrait-perlon/current-vacancies-2/,https://www.perlon.com/en/portrait-perlon/current-vacancies-2/: curl=0
LF-SC-00326,https://www.multiplastics.com/,plastics,yes,https://www.multiplastics.com/,https://www.multiplastics.com/: curl=0
LF-SC-00358,https://www.puraquaproducts.com/about-us,"Today, the chlorinators and pH systems manufactured at PurAqua are seen in facilities around the globe.",yes,https://www.puraquaproducts.com/about-us,https://www.puraquaproducts.com/about-us: curl=0
LF-LA-00001,https://www.cmp.co.jp/en/company/group_western-countries/,"CMP COATINGS, INC.",yes,https://www.cmp.co.jp/en/company/group_western-countries/,https://www.cmp.co.jp/en/company/group_western-countries/: curl=0
LF-LA-00029,https://www.ecovyst.com/ecoservices/,sulfuric acid,yes,https://www.ecovyst.com/ecoservices/,https://www.ecovyst.com/ecoservices/: curl=0
LF-LA-00054,https://sunspecialtyproducts.com/about-us/,Advanced manufacturing methodology patent issued for thermoset polymer processes and nanocomposites.,yes,https://sunspecialtyproducts.com/about-us/,https://sunspecialtyproducts.com/about-us/: curl=0
LF-LA-00183,https://www.berryglobal.com/,Berry,yes,https://www.berryglobal.com/,https://www.berryglobal.com/: curl=0
LF-LA-00234,https://cornerstonechemco.com/acrylonitrile,essential monomer in the production of various polymers and copolymers,not_verified,,https://cornerstonechemco.com/acrylonitrile: curl=56; https://r.jina.ai/https://cornerstonechemco.com/acrylonitrile: curl=56
LF-LA-00264,https://www.ashindustries.com/,"Plastic, metal, and silicone injection molding—all in one facility.",yes,https://www.ashindustries.com/,https://www.ashindustries.com/: curl=0
LF-LA-00305,https://www.indplastics.com/en/,"national supplier of stock and custom molded PTFE rod, tube, plate, sheets, gaskets and machined parts",yes,https://www.indplastics.com/en/,https://www.indplastics.com/en/: curl=0


FILE tasks/strong-waves-mo-sc-la-2026-11-06/qcew-after.json
{
  "MO": {
    "strict_before": 37,
    "qcew_2023": "368",
    "strict_after": 43,
    "share_before": 0.10054347826086957,
    "share_after": 0.11684782608695653
  },
  "SC": {
    "strict_before": 49,
    "qcew_2023": "406",
    "strict_after": 52,
    "share_before": 0.1206896551724138,
    "share_after": 0.12807881773399016
  },
  "LA": {
    "strict_before": 6,
    "qcew_2023": "117",
    "strict_after": 7,
    "share_before": 0.05128205128205128,
    "share_after": 0.05982905982905983
  }
}
