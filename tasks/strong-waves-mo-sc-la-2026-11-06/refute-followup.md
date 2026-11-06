LATEST CORRECTION: direct Codex initial REFUTE also required B-PARENT provenance for CMP. This is now fixed: ORG-009029 ultimate_parent_name=Chugoku Marine Paints, Ltd., sourced from the corporate group listing explicitly naming CMP Coatings + Belle Chasse address; group-domain notes flag added. New parent EVD-169900. No pre-existing org parent/ownership changes. Evidence total280. Alias issue already answered by source-specific government observations; original rows preserved per append-only rule. The original reviews are in review-codex-initial.txt and review-grok-initial.txt. Review current HEAD; included old copies of source files below may predate this last parent correction. Current build.py/check.py and README.md are authoritative.

Follow-up adversarial refute after initial Grok REFUTE. End APPROVE or REFUTE. Prior findings and corrections are in README.md final section and review-grok-initial.txt. This is PR #141 L3, same 36 STRONG clusters / 19 verified sites / 15 C organizations / 1 scope REJECT / 16 holds. Evidence is now 280 observations (210 original unchanged + 70 supplemental), append-only verified against previous commit. Original weak quotes retained as historical observations and answered by stronger witnesses. Five supplemental raw checks pass, including downloaded manufacturer's PDF via pdftotext -raw. Plant-only witnesses are allowed under merged Michigan recipe when federal manufacturing/activity record attests the establishment. New federal alias observations cite each actual ITA/OSHA/F5500 registrant source. Address equality asserted with house atlas.street_key, same state. Exact 15/19/280 counts, raw-verdict quote binding, supplemental-evidence binding, all-state replay byte-identical, zero validate errors. Created-site code table explicitly reconciles T3 +6/+3/+1; Ring1 is not equivalent to NAICS326. Input state/verdict grammar exact 36/36. Frozen order asserted for reserved IDs.
Scope/alias rulings AGENTS.md and owner battery B-SCOPE/B-ALIAS 2026-11-04. No existing record change besides four alias fields. No closure rejection. No registry links or qualifier edits. Review actual current PR where tools are available. Below is bounded evidence to permit a text-only verdict too.


FILE README.md
# L3 STRONG wave — Missouri, South Carolina, Louisiana

Scope: 36 lead-fusion STRONG establishment clusters, MO 15 / SC 14 / LA 7. `verdicts.csv` is exhaustive, not a sampling frame.
The original recipe is `../mi-strong-wave-2026-11-04/`; the binding lane acceptance criteria are in `LANE_BRIEF.md`.

Sources: public operator pages selected in `research.py`, re-fetched in `rawcheck.csv`; OSHA ITA CY2025 establishments,
OSHA inspection records and DOL EFAST2 sponsor packets already held under tasks/. ECHO/FRS identifiers are notes only;
no FRS REST requests were made (shared-IP restriction from controller 2026-11-06, recorded on BOARD).

`dedupe.json` records atlas.py's four steps, including domain, normalized legal/trade names, street and successor chains.
Street matching additionally ignores mailing-city and ZIP variations. JM Eagle ORG-002260 is tombstoned: Columbia attaches
to survivor ORG-002261. Insulfab uses held ORG-006173; Nike uses ORG-003555; Yokohama TWS uses ORG-001336.
The Aurora substring in Polyply notes is a lead, not proof of common legal identity; the Aurora cases remain held.
No organizations were merged, no ownership/status changes were applied, and no inclusion-log borderline create was made.

## Build and checks

Before applying: `python3 tasks/strong-waves-mo-sc-la-2026-11-06/prepare.py`, then `adjudicate.py` in that directory.
The three known published witnesses (TG Missouri, Manchester Packaging, Insulfab) passed 3/3; appending a nonexistent token
to each quote failed 3/3. Script/style content is excluded. Failed routes are not evidence of absence.

Apply each state: `python3 tasks/strong-waves-mo-sc-la-2026-11-06/build.py --state MO --apply` (then SC, LA).
IDs are deterministic input-index offsets in the reserved block. `append_sorted` is used for every append. Reapplication
asserts exact equality for held IDs instead of overwriting evidence. On fresh main, re-run adjudication and inspect new
dedupe hits before re-running the builder; do not merge CSV conflicts by hand.

Named checks: `python3 scripts/validate.py`; `python3 tasks/strong-waves-mo-sc-la-2026-11-06/check.py`.
`check.py` injects three missing/duplicate census defects and requires all three to fail. It also checks exact creates,
unique IDs and the per-state NAICS 326 strict-site/QCEW rise using `scripts/build_qcew_denominators.py::atlas_numerators`.
Denominator = QCEW 2023 private establishments, NAICS 326: MO 368, SC 406, LA 117; held official-source denominator file.
A ratio is not matched establishment coverage. No QCEW downloads or denominator changes are needed.

## Holds

`holds.csv` is the holds table: one cluster and named settling fact per row. Fetch availability holds remain explicit.
Agfa is held pending dated closure outcome + address-matched EFAST2, never rejected solely on a closure headline.
PIDC is excluded under owner B-SCOPE (2026-11-04), inorganic alumina output; deciding regulator source is in its verdict.
County/HQ are not inferred from postal city or plant location. Blank fields remain honest unknowns.

## Pass journal and reviews

Application counts, before/after ratios and independent review verdicts are appended below before PR publication.

- Missouri application: 7 new organizations (tier C), 9 new establishments {'C': 1, 'B': 8}; 98 evidence observations. `validate.py`: zero errors. Builder replay: passed.
- South Carolina application: 4 new organizations (tier C), 6 new establishments (tier B); 64 evidence observations; 2 held-parent alias updates. `validate.py`: zero errors. Builder replay: passed.
- Louisiana application: 4 new organizations (tier C), 4 new establishments (tier B); 48 evidence observations. `validate.py`: zero errors. Builder replay: passed.

Final census: {'STILL_UNCERTAIN': 16, 'VERIFIED': 19, 'REJECT': 1} across the 36 STRONG establishment clusters. Creates: 15 organizations (C), 19 establishments (18 B / 1 C), 280 evidence rows (210 original + 70 supplemental); 4 held-parent alias additions.

| State | QCEW 2023 NAICS 326 private establishments | Atlas strict before | Atlas strict after | Strict/QCEW before → after |
|---|---:|---:|---:|---:|
| MO | 368 | 37 | 43 | 10.05% → 11.68% |
| SC | 406 | 49 | 52 | 12.07% → 12.81% |
| LA | 117 | 6 | 7 | 5.13% → 5.98% |

`check.py`: PASS, exact 36/36 verdict census, 3/3 injected census defects caught, 19 applied sites, unique IDs, T3 rises in all states. Prior-row comparison against pre-pass commit: every old evidence row preserved; only four old organization trade_names fields gained aliases. All three builder replays are byte-identical across 16 changed data files.

### Held clusters and settling facts

| Cluster | Settling fact |
|---|---|
| LF-MO-00006 | Need a polymer formulation or captive shaping witness; contract filling alone does not settle scope. |
| LF-MO-00018 | Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote. |
| LF-MO-00053 | Need polymer-binder formulation at Clifton Avenue; broad chemical blending and distribution does not settle site scope. |
| LF-MO-00120 | Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote. |
| LF-MO-00165 | Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote. |
| LF-MO-00289 | Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote. |
| LF-SC-00047 | Need polymer-specific production or qualifying polymer value-chain focus at Rock Hill; metal finishing alone is insufficient. |
| LF-SC-00129 | Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote. |
| LF-SC-00198 | Closure reporting found; need dated primary outcome and address-matched EFAST2 check before any closure REJECT. No active create. |
| LF-SC-00206 | Need a raw-verifiable polymer activity witness and operator/site identity; available fetch routes did not verify the selected quote. |
| LF-SC-00302 | Need Laurens foam-control product binder/composition; silicone/polymer formulation versus nonpolymer defoamer not settled. |
| LF-SC-00326 | Need primary operator identity linking Curd Enterprises to Multiplastics and current manufacturing at 476 Long Point Road. |
| LF-SC-00358 | Need captive polymer processing or site-grain Ring 4 two-of-three test; chlorination equipment alone is insufficient. |
| LF-LA-00029 | Need dedicated polymer line or polymer-specific value-chain witness; sulfuric acid regeneration alone is insufficient. |
| LF-LA-00183 | Need current operator/site identity after Berry/Amcor transaction, and plant-specific polymer scope at 4611 Central Avenue. |
| LF-LA-00234 | Precursor-only Ring 3 precedent applies, but dated current operating outcome and operator after restructuring must be settled before active create. |

Controller 2026-11-06 authorized merge of origin/main instead of rebase to preserve the two pre-existing CRLF-dirty federal-frame files; this supersedes the lane rebase-only route for this integration. Controller also authorized publishing draft for queued refute-clerk review while saturated council calls remain pending; two-family approval is still required. Reviews pending at this checkpoint.

### Grok initial REFUTE and correction

The initial Grok 4.7 deep review REFUTED four weak scope/plant witnesses, own-site attribution of new-org federal aliases,
and missing address/count-composition checks. All original evidence rows remain untouched. Five raw-checked supplemental
quotes in `supplements.csv` now provide Davis coating activity, CMP's Louisiana address, Hahl's Lexington address, Sun's
Belle Chasse manufacturing location, and its own Lubra-Glide copolymer manufacturing technical sheet. The PDF was freshly
fetched with curl and extracted with pdftotext 26.10.0; its manufacturer sentence is verbatim. Government filing activity
descriptions complement plant-only own-site witnesses. Every federal alias group now has a source-specific government
observation (including the actual EFAST2 sponsor filing); these answer the earlier weak own-site attribution. Supplemental
IDs occupy 165000+ within the lane block. Total evidence observations are now 279 (69 appended); creates unchanged.

The builder now asserts every used federal street matches the input physical street using atlas.street_key and the same
state, and refuses changed verdict order. `check.py` ties raw quote/URL to verdicts, supplements to evidence, checks exact
15/19/279 counts, and reconciles each state's strict 326 increment against the actual created-site codes: MO +6, SC +3,
LA +1. Ring 1 counts differ because federal NAICS codes outside 326 remain as filed; no count is hidden or relabelled.
The reviewer had only a text packet and explicitly did not inspect federal data. Follow-up review includes the resolved
federal witness metadata and created-site code composition.

Corrected validation: `validate.py` zero errors; `check.py` PASS; `prepare.py --supplements-only` 5/5 raw quotes, PDF mutation rejected. Every prior evidence row byte-for-field identical across 8 supplemental shards; all-state builder replay byte-identical. Corrected re-review pending.

### Codex initial REFUTE and parent correction

Codex independently confirmed the census, source quotes, dedupe, prior-row preservation and T3, but REFUTED alias source
attribution (answered above) and CMP's group-domain classification without a recorded parent. The source explicitly identifies
Chugoku Marine Paints and lists CMP Coatings with its Louisiana address. The builder now records `ultimate_parent_name`
Chugoku Marine Paints, Ltd. on the new CMP organization, adds the B-PARENT-WEB group-domain notes flag, and appends parent
observation EVD-169900. No pre-existing organization parent or ownership field changes. This satisfies B-PARENT's documented
relationship condition; CMP's federal marine-paint manufacturing witness and raw group-page plant address supply activity/city.
Evidence final total: 280 = 210 original + 70 append-only supplements. Corrected validation and replay pass; re-review pending.


FILE build.py
#!/usr/bin/env python3
"""Idempotent integrator application of reviewed L3 STRONG verdicts.
Run from repository root: python3 tasks/strong-waves-mo-sc-la-2026-11-06/build.py --state MO --apply
Stable IDs are frozen-verdict-order offsets within the owner's reserved block, never gap-filled.
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
    supplements=read(HERE/'supplements.csv')
    inputs={r['cluster_id']:r for r in read(HERE/'input.csv')};vs=read(HERE/'verdicts.csv')
    assert [v['cluster_id'] for v in vs]==sorted(inputs,key=lambda k:({'MO':0,'SC':1,'LA':2}[inputs[k]['state']],k)), 'verdict order changed'
    assert len(inputs)==len(vs)==36 and Counter(r['cluster_id'] for r in vs)==Counter(inputs.keys()), 'verdict census mismatch'
    raw={r['cluster_id']:r for r in read(HERE/'rawcheck.csv')}
    ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
    osha={r['est_key']:r for r in read(ROOT/'tasks/osha-spine-2026-11-01/establishments.csv')}
    plans={r['ein']:r for r in read(ROOT/'tasks/form5500-spine-2026-11-01/sponsors.csv')}
    orgs={r['org_id']:(p,r) for p in (ROOT/'data').glob('organizations_*.csv') for r in read(p)}
    additions=defaultdict(list);alias_updates={};alloc=[]
    cmp_flag=' Group domain used as website; ultimate parent documented by the Chugoku Marine Paints group-company listing (B-PARENT/B-PARENT-WEB).'
    for idx,v in enumerate(vs):
        if v['state']!=a.state or v['verdict']!='VERIFIED':continue
        c=inputs[v['cluster_id']];assert raw[v['cluster_id']]['raw']=='yes' and v['own_quote']
        fed=[];aliases=[];alias_sources=[];code='';last='';industry=''
        fed_streets=[]
        for token in c['sources_with_ids'].split(';'):
            family,ident=token.split(':',1)
            if family=='ITA':
                r=ita[ident];ref=f"OSHA ITA Form 300A CY{r['year_filing_for']} establishment {ident} ({r['establishment_name']})"
                fed.append((ref,r['date_submitted'][:10]));aliases += [r['establishment_name'],r['company_name']]
                alias_sources.append(([r['establishment_name'],r['company_name']],ref,r['date_submitted'][:10]))
                fed_streets.append((r['street'],r['city'],r['state'],r['zip5']))
                if not industry:industry=r['industry_description']
                if not code:code=r['naics_code']
            elif family=='OSHA':
                r=osha[ident];ref=f"OSHA inspection {r['latest_activity_nr']} ({r['name']}), https://www.osha.gov/ords/imis/establishment.inspection_detail?id={r['latest_activity_nr']}"
                fed.append((ref,r['latest_inspection'][:10]));aliases.append(r['name'])
                alias_sources.append(([r['name']],ref,r['latest_inspection'][:10]))
                fed_streets.append((r['street'],r['city'],r['state'],r['zip'][:5]))
                if not code:code=r['naics_latest']
            elif family=='F5500':
                r=plans[ident];aliases.append(r['sponsor_name'])
                alias_sources.append(([r['sponsor_name']],f"DOL EFAST2 Form 5500 EIN {ident}, sponsor {r['sponsor_name']}, PY{r['plan_year']}, plan {r['plan_number']}, acknowledgement {r['ack_id']}",r['plan_year']+'-12-31'))
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
        # Supplement, never replace, the original own-site attribution and weak quotations.
        eid=165000+idx*100
        org_shard=orgs[oid][0].stem.split('_')[-1] if v['held_org_id'] else 'US'
        for names,ref,asof in alias_sources:
            values=[n for n in names if n and n!=name]
            if values:E('organizations',oid,'existence','Federal registrant aliases: '+'; '.join(values),ref,'government_filing',asof,'supports_C',shard=org_shard)
        for extra in supplements:
            if extra['cluster_id']!=v['cluster_id']:continue
            assert extra['raw']=='yes'
            kind=extra['claim_type'];detail=f"Raw-checked supplemental witness: {extra['quote']}"
            E('sites',sid,kind,detail,extra['source_url'])
            E('organizations',oid,kind,detail,extra['source_url'],effect='supports_C',shard=org_shard)
            if kind=='scope':
                E('sites',sid,'activity',detail,extra['source_url'])
                E('organizations',oid,'activity',detail,extra['source_url'],effect='supports_C',shard=org_shard)
        if industry:
            # The filing's own activity description complements plant-only own-site witnesses.
            for kind in ('scope','activity'):E('sites',sid,kind,'Filed establishment activity: '+industry,fed[0][0],'government_filing',fed[0][1])
        import atlas
        assert all(atlas.street_key(street)==atlas.street_key(c['street']) and state==c['state'] for street,city,state,zip_ in fed_streets), ('federal street mismatch',v['cluster_id'],fed_streets)
        if v['cluster_id']=='LF-LA-00001':
            eid=169900
            E('organizations',oid,'parent','ultimate_parent_name Chugoku Marine Paints, Ltd.; CMP Coatings, Inc. is named with its Belle Chasse address on the corporate group-company listing',own,effect='supports_C',shard='US')
        alloc.append(dict(cluster_id=v['cluster_id'],org_id=oid,new_org=str(not bool(v['held_org_id'])).lower(),site_id=sid,tier=tier))
    if a.apply:
        for filename,rows in additions.items():
            path=ROOT/'data'/filename;pk=next(iter(rows[0]));old={r[pk]:r for r in read(path)}
            fresh=[]
            for r in rows:
                if r[pk] in old:
                    # Re-running must be a no-op; a changed packet is a conflict, never an evidence rewrite.
                    assert all(old[r[pk]].get(k,'')==val or (r[pk]=='ORG-009029' and k=='notes' and old[r[pk]][k]==val+cmp_flag) for k,val in r.items()), (filename,r[pk])
                else:fresh.append(r)
            if fresh:append_sorted(path,fresh,pk)
        for p,changes in alias_updates.items():
            rows=read(p)
            for r in rows:
                if r['org_id'] in changes:r['trade_names']=changes[r['org_id']]
            write(p,rows,list(rows[0]))
        if a.state=='LA':
            p=ROOT/'data/organizations_US.csv';rows=read(p)
            r=next(r for r in rows if r['org_id']=='ORG-009029')
            assert r['ultimate_parent_name'] in ('','Chugoku Marine Paints, Ltd.'), 'unexpected CMP parent'
            r['ultimate_parent_name']='Chugoku Marine Paints, Ltd.'
            if not r['notes'].endswith(cmp_flag):r['notes']+=cmp_flag
            write(p,rows,list(rows[0]))
        write(HERE/f'allocations_{a.state}.csv',alloc,['cluster_id','org_id','new_org','site_id','tier'])
    print(a.state,dict(Counter({f:len(r) for f,r in additions.items()})), 'alias updates',sum(len(x) for x in alias_updates.values()))
if __name__=='__main__':main()


FILE check.py
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
    assert {r['cluster_id']:r for r in read(HERE/'input.csv')}=={r['cluster_id']:r for r in source}, 'input facts changed'
    for defect in (verdicts[:-1],verdicts+[verdicts[0]],verdicts[:-1]+[verdicts[0]]):
        try:census(source,defect)
        except AssertionError:pass
        else:raise AssertionError('census gate failed injected defect')
    raw={r['cluster_id']:r for r in read(HERE/'rawcheck.csv')}
    for v in verdicts:
        if v['verdict']=='VERIFIED':assert v['own_quote']==raw[v['cluster_id']]['quote'] and v['own_url']==raw[v['cluster_id']]['url']
    evidence=[r for p in (ROOT/'data').glob('evidence_*.csv') for r in read(p)]
    lane=[r for r in evidence if r['created_by']=='atlas-L3-strong-mo-sc-la']
    assert len(lane)==280, ('lane evidence total',len(lane))
    cmp=next(r for r in read(ROOT/'data/organizations_US.csv') if r['org_id']=='ORG-009029')
    assert cmp['ultimate_parent_name']=='Chugoku Marine Paints, Ltd.' and 'Group domain used as website' in cmp['notes']
    assert any(e['evidence_id']=='EVD-169900' and e['claim_type']=='parent' for e in lane)
    for extra in read(HERE/'supplements.csv'):
        assert extra['raw']=='yes'
        assert any(extra['quote'] in e['claim_detail'] and extra['source_url']==e['source_ref'] for e in lane),extra

    allocations=[r for st in ('MO','SC','LA') for r in read(HERE/f'allocations_{st}.csv')]
    assert Counter(r['cluster_id'] for r in allocations)==Counter(r['cluster_id'] for r in verdicts if r['verdict']=='VERIFIED')
    assert len(allocations)==19 and sum(r['new_org']=='true' for r in allocations)==15
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
        delta=sum(sites[r['site_id']]['naics_primary'].startswith('326') for r in allocations if sites[r['site_id']]['state']==st)
        assert n-b['strict_before']==delta,(st,'unreconciled numerator delta',delta)
        after[st]={**b,'strict_after':n,'share_before':b['strict_before']/float(b['qcew_2023']),'share_after':n/float(b['qcew_2023'])}
    (HERE/'qcew-after.json').write_text(json.dumps(after,indent=2)+'\n')
    print('PASS: 36/36 exact STRONG verdicts; census defects 3/3 caught;',len(allocations),'applied sites; IDs unique; NAICS 326 strict/QCEW rises in MO/SC/LA')
    print(json.dumps(after,indent=2))
if __name__=='__main__':main()


FILE supplements.csv
cluster_id,claim_type,source_url,quote,raw,route,note
LF-MO-00031,scope,https://www.davispaint.com/,From high-performance industrial coatings to custom products and creative partnerships,yes,https://www.davispaint.com/,Supplement after Grok refute; original evidence retained.
LF-LA-00001,existence,https://www.cmp.co.jp/en/company/group_western-countries/,"CMP COATINGS, INC. 1610 Engineers Road, Belle Chasse, Louisiana, 70037, U.S.A",yes,https://www.cmp.co.jp/en/company/group_western-countries/,Supplement after Grok refute; original evidence retained.
LF-SC-00313,existence,https://www.perlon.com/en/portrait-perlon/current-vacancies-2/,"Hahl Inc. 126 Glassmaster Road 29072 Lexington, S.C.",yes,https://www.perlon.com/en/portrait-perlon/current-vacancies-2/,Supplement after Grok refute; original evidence retained.
LF-LA-00054,existence,https://sunspecialtyproducts.com/about-us/,"manufacturing facility in Belle Chasse, Louisiana",yes,https://sunspecialtyproducts.com/about-us/,Supplement after Grok refute; original evidence retained.
LF-LA-00054,scope,https://sunspecialtyproducts.com/wp-content/uploads/2024/09/Lubra-Glide-Beads-Technical-Data-Sheet-2018-August-06.pdf,Lubra-Glide® copolymer beads are manufactured by SUN Specialty Products,yes,curl / pdftotext -raw,Supplement after Grok refute; original evidence retained.


FILE federal-witnesses.csv
cluster_id,family,source_id,registrant,company,street,city,state,zip,naics,industry,date
LF-MO-00023,ITA,1303906,T G MISSOURI CORPORATION - PERRYVILLE,T G MISSOURI CORPORATION - PERRYVILLE - 01 | 2200 PLATTIN ROAD,2200 PLATTIN ROAD,PERRYVILLE,MO,63775,326299,Interior/Exterior Automotive Parts,2026-02-17
LF-MO-00023,OSHA,345256077,TG MISSOURI,,2200 PLATTIN ROAD,PERRYVILLE,MO,63775,326199,,2021-04-15
LF-MO-00031,ITA,903477,Davis Paint Co,Davis Paint Company,1311 Iron St.,North Kansas City,MO,64116,325510,"Architectural coatings (i.e., paint) manufacturing",2026-01-06
LF-MO-00088,ITA,1425708,Manchester Packaging Company,Manchester Packaging Company,2000 East James Boulevard,St. James,MO,65559,326112,"Packaging film, plastics, single-web or multiweb, manufacturing",2026-01-08
LF-MO-00088,OSHA,343786869,MANCHESTER PACKAGING COMPANY,,2000 E. JAMES BLVD.,SAINT JAMES,MO,65559,326111,,2019-02-19
LF-MO-00100,OSHA,344706106,"T-N-T PLASTICS, INC.",,701 INDUSTRIAL DR.,PERRYVILLE,MO,63775,326111,,2020-03-11
LF-MO-00121,ITA,572867,004-Nike Air Manufacturing Missouri,Nike IHM,8 Research Park Drive,St. Charles,MO,63304,326199,"Footwear parts (e.g., heels, soles), plastics, manufacturing",2026-03-13
LF-MO-00121,OSHA,347479073,NIKE IHM INC.,,8 RESEARCH PARK DRIVE,SAINT CHARLES,MO,63304,326199,,2024-05-14
LF-MO-00153,ITA,1428874,U.S. Paint Corporation,U.S. Paint Corporation,831 S. 21st Street,St. Louis,MO,63103,325510,Paints (except artist's) manufacturing,2026-01-28
LF-MO-00241,ITA,548398,JM Eagle PCO,JM Eagle,6500 N. Brown Station Rd,Columbia,MO,65202,326122,PVC pipe manufacturing,2026-02-11
LF-MO-00241,OSHA,345012629,JM EAGLE,,6500 N BROWN STATION RD,COLUMBIA,MO,65202,326122,,2020-11-04
LF-MO-00286,OSHA,347593280,KOLLER-CRAFT PLASTIC PRODUCTS,,1400 OLD HIGHWAY 141,FENTON,MO,63026,326199,,2024-07-02
LF-SC-00082,OSHA,348160078,INSULFAB PLASTICS INC,,834 HAYNE STREET,SPARTANBURG,SC,29305,326121,,2025-04-02
LF-SC-00113,OSHA,344027743,EMS-CHEMIE NORTH AMERICA INC,,2060 CORPORATE WAY,SUMTER,SC,29154,325211,,2019-05-21
LF-SC-00147,ITA,53682,Wikoff Color Corp. - Fort Mill - Plant,Wikoff Color Corp.,1886 Merritt Rd,Fort Mill,SC,29715,325910,Printing inks manufacturing,2026-01-27
LF-SC-00147,ITA,558589,Wikoff Color Corporation - Fort Mill - Admin,Wikoff Color Corporation,1886 Merritt Rd.,Fort Mill,SC,29715,325910,"Inks, printing, manufacturing",2026-01-27
LF-SC-00147,OSHA,345036172,WIKOFF COLOR CORPORATION,,1886 MERRITT ROAD,FORT MILL,SC,29715,325910,,2020-11-20
LF-SC-00214,ITA,1250716,Re:Build Composite Resources,Re:Build Composite Resources,485 Lakeshore Parkway,Rock Hill,SC,29730,326130,"Laminated plastics plate, rod, and sheet, manufacturing",2026-01-09
LF-SC-00253,ITA,1059636,Yokohama TWS - Spartanburg,"Yokohama TWS North America, INC",570 Trelleborg Drive,Spartanburg,SC,29301,326211,"Tires (e.g., pneumatic, semi-pneumatic, solid rubber) manufacturing",2026-02-09
LF-SC-00253,OSHA,347711939,YOKOHAMA TWS NORTH AMERICA INC,,570 TRELLEBORG DRIVE,SPARTANBURG,SC,29301,326211,,2024-08-19
LF-SC-00313,ITA,1328552,Hahl Inc,Hahl Inc.,126 Glassmaster Road,Lexington,SC,29072,325211,"Resins, plastics (except custom compounding purchased resins), manufacturing",2026-01-29
LF-SC-00313,OSHA,348842915,HAHL INC,,126 GLASSMASTER RD,LEXINGTON,SC,29072,326199,,2026-03-25
LF-LA-00001,ITA,647354,Belle Chasse Facility,"CMP Coatings, Inc.",1610 Engineers Road,Belle Chasse,LA,70037,325510,Marine paints manufacturing,2026-02-04
LF-LA-00054,ITA,1067928,Sun Drilling Products Corp.,Sun Drilling Products Corp.,503 Main Street,Belle Chasse,LA,70037,325998,"Drilling mud compounds, conditioners, and additives (except bentonites) manufacturing",2026-01-16
LF-LA-00264,ITA,57635,"ASH Industries, Inc.","ASH Industries, Inc.",1330 W. Willow Street,Lafayette,LA,70506,326199,"Coolers or ice chests, plastics (except foam), manufacturing",2026-01-26
LF-LA-00264,OSHA,345487128,"ASH INDUSTRIES, INC.",,1330 WEST WILLOW ST.,LAFAYETTE,LA,70506,326199,,2021-08-19
LF-LA-00305,ITA,280605,Industrial Plastics & Machine,INDUSTRIAL PLASTICS AND MACHINE,6829 South Choctaw Drive,Baton Rouge,LA,70806,325211,Fluoro-polymer resins manufacturing,2026-03-20
LF-LA-00305,OSHA,347202467,INDUSTRIAL PLASTICS & MACHINE,,6829 SOUTH CHOCTAW DRIVE,BATON ROUGE,LA,70806,326112,,2024-01-10


FILE created-site-codes.csv
cluster_id,site_id,org_id,state,ring,naics_primary,tier,street,included_326
LF-MO-00017,SITE-012001,ORG-009001,MO,2,,C,325 PAUL AVE,false
LF-MO-00023,SITE-012003,ORG-009003,MO,1,326299,B,2200 PLATTIN ROAD,true
LF-MO-00031,SITE-012004,ORG-009004,MO,2,325510,B,1311 Iron St.,false
LF-MO-00088,SITE-012006,ORG-009006,MO,1,326112,B,2000 East James Boulevard,true
LF-MO-00100,SITE-012007,ORG-009007,MO,1,326111,B,701 INDUSTRIAL DR.,true
LF-MO-00121,SITE-012009,ORG-003555,MO,1,326199,B,8 Research Park Drive,true
LF-MO-00153,SITE-012010,ORG-009010,MO,2,325510,B,831 S. 21st Street,false
LF-MO-00241,SITE-012012,ORG-002261,MO,1,326122,B,6500 N. Brown Station Rd,true
LF-MO-00286,SITE-012013,ORG-009013,MO,1,326199,B,1400 OLD HIGHWAY 141,true
LF-SC-00082,SITE-012016,ORG-006173,SC,1,326121,B,834 HAYNE STREET,true
LF-SC-00113,SITE-012017,ORG-009017,SC,1,325211,B,2060 CORPORATE WAY,false
LF-SC-00147,SITE-012019,ORG-009019,SC,2,325910,B,1886 Merritt Rd,false
LF-SC-00214,SITE-012022,ORG-009022,SC,1,326130,B,485 Lakeshore Parkway,true
LF-SC-00253,SITE-012023,ORG-001336,SC,1,326211,B,570 Trelleborg Drive,true
LF-SC-00313,SITE-012026,ORG-009026,SC,1,325211,B,126 Glassmaster Road,false
LF-LA-00001,SITE-012029,ORG-009029,LA,2,325510,B,1610 Engineers Road,false
LF-LA-00054,SITE-012031,ORG-009031,LA,1,325998,B,503 Main Street,false
LF-LA-00264,SITE-012034,ORG-009034,LA,1,326199,B,1330 W. Willow Street,true
LF-LA-00305,SITE-012035,ORG-009035,LA,1,325211,B,6829 South Choctaw Drive,false


FILE verdicts.csv
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


FILE qcew-after.json
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
