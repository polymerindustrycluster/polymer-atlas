"""Reconcile frozen proposals against a fresh NCES pull using the existing IPEDS parser."""
import argparse,csv,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'scripts'))
import build_ipeds_completions as ipeds


def read(path):
    with open(path,newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))


def write(name,rows,header=None):
    with open(HERE/name,'w') as f:
        w=csv.DictWriter(f,fieldnames=header or list(rows[0]),lineterminator='\n');w.writeheader();w.writerows([{k:r.get(k,'') for k in w.fieldnames} for r in rows])


def main(raw_dir,data):
    proposals=read(HERE.parent/'ipeds-completions-2026-11-01/program_proposals.csv')
    assert len(proposals)==len({p['program_id'] for p in proposals})==147
    ipeds.FIRST_YEAR=ipeds.LAST_YEAR=2024
    comp,src=ipeds.load_completions(str(raw_dir),set(ipeds.CIP_SET)|{'40.0509'})
    total=lambda u,c:ipeds.sum_levels(comp,2024,u,c,ipeds.DETAIL_LEVELS)
    # Independent known answers from original NCES raw rows, not the selection branch.
    for unit,expect in [('205443',6),('169910',30),('235149',56)]:assert total(unit,'15.0607')==expect,(unit,total(unit,'15.0607'))
    assert ipeds.sum_levels(comp,2024,'235149','15.0607',[3])==10
    held={r['program_id']:r for r in read(data/'programs.csv')}
    eco={r['org_id']:r for r in read(data/'ecosystem.csv')}
    # Cross-check all44 numeric proposals against current raw, before deriving ANY edits.
    for p in proposals:
        if p['prop_latest_completions']:
            assert total(p['ipeds_unitid'],p['cip_code'])==int(p['prop_latest_completions']),f"raw/proposal conflict {p['program_id']}"
    selected=[];verdicts=[];edits=[];evidence=[]
    base='https://nces.ed.gov/ipeds/datacenter/data/C2024_A.zip'
    for p in proposals:
        r=held[p['program_id']];why='';verdict='STILL_UNCERTAIN'
        if r['program_type']!='degree':
            verdict='REJECT';why='Completions-field proposal only: SCHEMA4.11 permits degree rows only; held program_type '+r['program_type']+'. Programme inclusion/status remains unchanged.'
        elif p['proposal_status'] not in ('PROPOSE','CONFIRMS_HELD') or p['includes_postbacc_cert_2024']:
            why='Settle missing identity/CIP or owner award-level semantics before applying. Original proposal_status '+p['proposal_status']+'; positive postbacc/postmasters count '+(p['includes_postbacc_cert_2024'] or '0')+'. Existing values unchanged.'
        else:
            parent=eco.get(r['institution_org_id'],{})
            assert (r['institution_org_id'],r['cip_code'],r['program_type'],set(r['level'].split(';')))==(p['institution_org_id'],p['cip_code'],p['program_type'],set(p['level'].split(';'))),f"held join changed {r['program_id']}"
            assert parent.get('ipeds_unitid')==p['ipeds_unitid'],f"UNITID changed {r['program_id']}"
            levels={l for label in r['level'].split(';') for l in ipeds.LEVEL_MAP.get(label,())}
            all_n=total(p['ipeds_unitid'],p['cip_code']);row_n=ipeds.sum_levels(comp,2024,p['ipeds_unitid'],p['cip_code'],levels)
            assert all_n==row_n>0,f"mixed-level contamination {r['program_id']}"
            assert p['prop_last_year_awarded']=='2024' and p['prop_completions_year']=='2024'
            assert not r['latest_completions'] or (r['latest_completions']==str(all_n) and r['completions_year']=='2024'),f"held count conflict {r['program_id']}"
            citation=f"NCES IPEDS C2024_A, UNITID {p['ipeds_unitid']} x CIP {p['cip_code']}, first major, all detail award levels, {base}, fetched 2026-11-06"
            caveat=p['cip_scope_caveat']
            note='2026-11-06 IPEDS application: latest_completions is the entire institution x CIP count, not a polymer-track headcount. last_year_awarded=2024 means latest observed positive award year in the 2011–2024 pull window, never a final award or closure. '+caveat
            desired={'latest_completions':str(all_n),'completions_year':'2024','last_year_awarded':'2024','sources':r['sources']+'; '+citation,'notes':r['notes']+(' ' if r['notes'] else '')+note}
            for k,v in desired.items():
                if r[k]!=v:edits.append(dict(program_id=r['program_id'],column=k,old_value=r[k],new_value=v))
            selected.append(p)
            ev=f'EVD-{285100+len(evidence):06}'
            evidence.append(dict(evidence_id=ev,record_table='programs',record_id=r['program_id'],claim_type='activity',claim_detail=f"latest_completions {all_n}; completions_year 2024; last_year_awarded 2024 (last observed, not final). UNITID {p['ipeds_unitid']} x CIP {p['cip_code']}; MAJORNUM=1; sum CTOTALT across detail AWLEVELs, total {all_n}; all positive award levels covered by held level set {r['level']}. {caveat}",source_class='registry',source_ref=base,observed_date='2026-11-06',tier_effect='supports_C',created_by='atlas-L13-program-completions-2',notes='C2024_A fetched 2026-11-06; raw hash/rows in source.json/raw_2024.csv. Statistical completion observation only; no program existence, scope, liveness, tier or own-page verification-date assertion. First award year withheld as finite-window/coding seam.'))
            verdict='VERIFIED';why='Fresh raw first-major count reconciles proposal and held identity/CIP; all positive awards within held levels. '+('Blank count pair filled.' if not r['latest_completions'] else 'Held count pair confirmed.')+' Last-observed positive year filled; first-year field held.'
        verdicts.append(dict(program_id=r['program_id'],proposal_status=p['proposal_status'],verdict=verdict,reason_or_settling_fact=why))
    write('input.csv',proposals);write('edits.csv',edits);write('verdicts.csv',verdicts)
    write('joins.csv',[{k:(p[k] if k=='ipeds_unitid' else held[p['program_id']][k]) for k in ('program_id','institution_org_id','program_type','cip_code','level','ipeds_unitid')} for p in selected])
    write('evidence_programs.csv',evidence,next(csv.reader(open(data/'evidence_programs.csv'))))
    keys={(p['ipeds_unitid'],p['cip_code']) for p in proposals if p['prop_latest_completions']}
    raw_rows=[]
    for (year,u,c,l),(n,second,flag,secondflag) in sorted(comp.items()):
        if (u,c) in keys:raw_rows.append(dict(unitid=u,cip_code=c,award_level_code=str(l),completions_year='2024',completions_first_major=str(n),first_major_flag=flag,completions_second_major=str(second)))
    write('raw_2024.csv',raw_rows)
    file=raw_dir/'x_C2024_A'/src[2024][0]
    (HERE/'source.json').write_text(json.dumps(dict(url=base,fetched='2026-11-06',raw_member=file.name,raw_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),positive_numeric_proposals_reconciled=44,known_answers={'Shawnee_all':6,'Ferris_all':30,'Everett_all':56,'Everett_associate_only':10},source_vintage='C2024_A provisional as in original packet; collection year2024 = awards2023-07-01 through2024-06-30'),indent=2)+'\n')
    from collections import Counter
    print('147proposals',Counter(v['verdict'] for v in verdicts),'selected',len(selected),'edits',len(edits),'evidence',len(evidence))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--raw-dir',type=Path,required=True);p.add_argument('--data-dir',type=Path,default=HERE.parents[1]/'data');a=p.parse_args();main(a.raw_dir,a.data_dir)
