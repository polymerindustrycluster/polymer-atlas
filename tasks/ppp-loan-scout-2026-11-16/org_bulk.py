"""Bulk historical borrower-band comparison; no new fetches or canonical edits."""
import csv,json
from collections import defaultdict,Counter
from datetime import datetime
from decimal import Decimal,InvalidOperation
from build import ROOT,D,P,read,common,atlas
from build_form5500_spine import band_of,BANDS
ORDER=[b[2] for b in BANDS]+['5000+']

def loan_band(value):
 try:n=Decimal(value)
 except InvalidOperation:return ''
 if not n.is_finite() or n<1 or n!=n.to_integral_value():return ''
 return band_of(int(n))

def latest(rows):
 return max(rows,key=lambda r:(datetime.strptime(r['DateApproved'],'%m/%d/%Y'),r['LoanNumber']))

def classify(a,b):
 if a not in ORDER or b not in ORDER:return 'uncomparable'
 distance=abs(ORDER.index(a)-ORDER.index(b))
 return 'exact' if distance==0 else 'adjacent' if distance==1 else 'off_two_plus'

def public(name,rows,fields):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)

def compute():
 orgs={r['org_id']:r for p in (ROOT/'data').glob('organizations_*.csv') for r in read(p)}
 sites={r['site_id']:r for p in (ROOT/'data').glob('sites_*.csv') for r in read(p)}
 byorg=defaultdict(list)
 for r in sites.values():byorg[r['org_id']].append(r)
 single={oid for oid,ss in byorg.items() if sum(s['operating_status']=='active' for s in ss)==1 and all(s['state']=='OH' and s['country'] in ('','US','USA') for s in ss)}
 matches=read(P/'matches.csv');usable=[r for r in matches if loan_band(r['JobsReported'])]
 output=[];summary=[]
 for grain,idkey,field,table in [('organizations','org_id','employee_band_ohio',orgs),('sites','site_id','employee_band_site',sites)]:
  groups=defaultdict(dict)
  for r in usable:groups[r[idkey]][r['LoanNumber']]=r
  for key,loans in sorted(groups.items()):
   r=latest(list(loans.values()));old=table[key][field];new=loan_band(r['JobsReported'])
   output.append(dict(grain=grain,record_id=key,org_id=r['org_id'],single_site_ohio=str(r['org_id'] in single),loan_id=r['LoanNumber'],loan_date=datetime.strptime(r['DateApproved'],'%m/%d/%Y').date().isoformat(),loan_band=new,atlas_band=old,comparison=classify(new,old)))
  for cohort in ['all_matches','single_site_ohio']:
   rr=[r for r in output if r['grain']==grain and (cohort=='all_matches' or r['single_site_ohio']=='True')]
   counts=Counter(r['comparison'] for r in rr);den=len(rr)-counts['uncomparable']
   summary.append(dict(grain=grain,cohort=cohort,matched_records=len(rr),comparable=den,uncomparable=counts['uncomparable'],**{k:dict(n=counts[k],wilson95=common.wilson(counts[k],den)) for k in ['exact','adjacent','off_two_plus']},within_one=dict(n=counts['exact']+counts['adjacent'],wilson95=common.wilson(counts['exact']+counts['adjacent'],den))))
 # Broad match requires name plus borrower city and a supplied address; exact street is a separately exposed sensitivity.
 names={oid:{atlas.name_key(n) for _,n in atlas.org_name_fields(o)}|{atlas.site_name_key(s['site_name'],s['city']) for s in byorg[oid]} for oid,o in orgs.items()}
 broad=[r for r in usable if atlas.name_key(r['BorrowerName']) in names[r['org_id']] and r['BorrowerAddress'].strip()]
 strict=[r for r in broad if any(s['street_address'] and s['city'].casefold()==r['BorrowerCity'].casefold() and atlas.street_key(s['street_address'])==atlas.street_key(r['BorrowerAddress']) for s in byorg[r['org_id']])]
 fills=[];fill_rows=[]
 for match_rule,rows in [('name_city_address_present',broad),('name_street_city_exact',strict)]:
  for rule in ['a','b','c']:
   rr=[r for r in rows if (rule=='a' or r['org_id'] in single) and (rule!='c' or r['NAICSCode'].startswith(('325','326')))]
   org_ids={r['org_id'] for r in rr};blank_orgs={oid for oid in org_ids if not orgs[oid]['employee_band_ohio'].strip()}
   blank_sites={r['site_id'] for r in rr if r['org_id'] in single and not sites[r['site_id']]['employee_band_site'].strip()}
   fills.append(dict(match_rule=match_rule,rule=rule,eligible_organizations=len(org_ids),blank_org_bands=len(blank_orgs),blank_single_site_bands=len(blank_sites)))
   for grain,ids in [('organizations',blank_orgs),('sites',blank_sites)]:
    for key in sorted(ids):
     r=latest([r for r in rr if r['org_id' if grain=='organizations' else 'site_id']==key])
     fill_rows.append(dict(match_rule=match_rule,rule=rule,grain=grain,record_id=key,loan_id=r['LoanNumber'],loan_date=datetime.strptime(r['DateApproved'],'%m/%d/%Y').date().isoformat(),loan_band=loan_band(r['JobsReported']),applied='held'))
 return dict(matched_organizations=len({r['org_id'] for r in matches}),matched_sites=len({r['site_id'] for r in matches}),usable_loan_site_pairs=len(usable),unusable_loan_site_pairs=len(matches)-len(usable),comparisons=summary,fills=fills,loan_years=dict(Counter(r['loan_date'][:4] for r in output))),output,fill_rows

def main():
 m,rows,fills=compute();(D/'org_bulk.json').write_text(json.dumps(m,indent=2)+'\n')
 public('org_bulk_comparisons.csv',rows,list(rows[0]));public('org_bulk_fills.csv',fills,list(fills[0]))

def render(m):
 text='\n## B-PPP bulk organization-grain addendum (2026-11-16)\n\n'
 text+='No hand checks or new downloads. The original provisional match found **415 organizations / 424 active PIC-18 sites**. All 606 loan–site pairs have positive integral JobsReported and map to the existing eight Atlas bands (`1-9` through `5000+`) using the held Form 5500 band helper. Each organization/site contributes once: choose the latest loan date, break ties by loan number, never sum draws. Rows and full-precision intervals are in `org_bulk_comparisons.csv` and `org_bulk.json`.\n\n'
 text+='Single-site Ohio-only means **exactly one active site across all held site shards, and every held site (including inactive) is in Ohio/US**. There are 392 such organizations among the matches. This is the requested operational proxy for borrower = organization = plant; unrecorded sites and mismatched borrowers remain a limitation of the held data. No subsidiary headcount is rolled up to a parent.\n\n'
 text+='Comparison categories are disjoint: exact band, exactly one band away, two or more bands away. “Within one” additionally includes exact matches. Denominator is records with an in-vocabulary held band; blank/unknown/off-vocabulary values are uncomparable and excluded, not silently normalized (e.g. 100–199 is not the adopted 100–249). CIs are descriptive Wilson 95% intervals, not causal accuracy or a census sampling error.\n\n'
 text+='| Unit / cohort | Matched | Comparable | Uncomparable | Exact n (%; 95% CI) | Adjacent only n (%; 95% CI) | Off ≥2 n (%; 95% CI) | Within one n (%; 95% CI) |\n|---|---:|---:|---:|---|---|---|---|\n'
 for r in m['comparisons']:
  cells=[]
  for k in ['exact','adjacent','off_two_plus','within_one']:
   x=r[k];lo,hi=x['wilson95'];cells.append(f"{x['n']} ({100*x['n']/r['comparable']:.1f}%; {100*lo:.1f}–{100*hi:.1f}%)")
  text+=f"| {r['grain']} / {r['cohort']} | {r['matched_records']} | {r['comparable']} | {r['uncomparable']} | "+' | '.join(cells)+' |\n'
 text+='\n### Potential blank-band fills (every proposal held, zero applied)\n\n'
 text+='For the requested rules, **name+address** is the strict case: borrower name matches an organization legal/trade/parenthetical name or one of its site names, and the borrower street+city matches a held street+city of that organization. Rule (b) additionally requires the single-site Ohio-only proxy; rule (c) additionally requires that same qualifying loan’s NAICS to start 325 or 326. If several loans qualify, choose the latest qualifying loan. This differs from the original scout’s weaker name-or-street plus city screen. We report the weaker name+city with a supplied borrower street separately, so it cannot be mistaken for exact street matching. Blank means empty, not `unknown` or off-vocabulary.\n\n'
 text+='| Match evidence | Rule | Eligible organizations | Blank organization Ohio bands | Blank site bands on single-site Ohio-only orgs | Applied / held |\n|---|---|---:|---:|---:|---|\n'
 for r in m['fills']:
  text+=f"| {r['match_rule']} | {r['rule']} | {r['eligible_organizations']} | {r['blank_org_bands']} | {r['blank_single_site_bands']} | 0 / all |\n"
 text+='\nRules (a) and (b) have equal single-site site counts because that column already restricts to single-site organizations. Fill counts are candidate record counts, not mutually exclusive additions: (c) is nested in (b), nested in (a). `org_bulk_fills.csv` carries deduplicated rule/grain/record keys, dated source loan IDs and mapped bands, with no borrower streets.\n\n'
 text+='### Updated owner recommendation and dating\n\n'
 text+='**B-PPP: recommend conditional GO for historical organization Ohio-band candidates under strict rule (b): 117 blank organization bands, plus 137 blank site-band candidates at the same operational grain.** If the owner wants a polymer-NAICS restriction, strict rule (c) narrows these to **47 organizations / 62 sites**; NAICS is an extra filter, never scope proof. The broader rule (a) yields 124 blank organization bands but includes multi-site borrowers, so Ohio allocation is unresolved and it is not recommended for automatic filling. Weak locality-only candidates (260 organizations / 294 sites under b) remain discovery-only. All remain HELD pending owner admission, exact borrower/operator adjudication and source precedence; canonical values are not changed.\n\n'
 text+='The bulk comparison supports a historical band witness more than the small hand sample alone: for the single-site proxy, 104/106 comparable organization bands and 70/72 comparable site bands are within one band. This does not establish that the missing-band population has the same agreement, that adjacent bands are exact, or that the matching is correct. Existing disagreements go to review per R13; PPP must not overwrite OSHA/other preferred sources.\n\n'
 text+='**Vintage: loan approval date (the release column `DateApproved`, called “Loan Funded Date” in the SBA dictionary), 2020 or 2021.** Across selected comparison observations there are '+str(m['loan_years'].get('2020',0))+' dated 2020 and '+str(m['loan_years'].get('2021',0))+' dated 2021; these count organization and site observations separately, so the same loan can occur at both grains. Label any admitted band “historical borrower-reported employment band, SBA PPP, loan date YYYY-MM-DD (2020/2021); underlying employment reference period unspecified; retrieved 2026-11-16.” Use that exact source date in the existing BAND-SOURCE notes convention (and employee_count_source_date if adopted/exported), not the 2024 release or 2026 retrieval as employment vintage. Evidence observed_date carries the source period/date where force depends on it, with retrieval in notes. Never label it a current 2026 band or infer 2026 liveness. Owner must decide whether historic values may populate the undated band columns with explicit notes, or stay research-only; recommend historical-labelled fills only under the strict single-site rule and after the gate above.\n'
 return text

# Keep the README tables and source counts synchronized on every rebuild.
if __name__=='__main__':
 main()
 m=json.loads((D/'org_bulk.json').read_text())
 p=D/'README.md';base=p.read_text().split('\n## B-PPP bulk organization-grain addendum')[0]
 p.write_text(base+render(m))
