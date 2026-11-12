import csv,glob,json,sys,re,hashlib,os
from extract import text_of,cands,pobox,RAW
R='/workspace/atlas-ohio-nov12/repo/'
sites={};orgs={}
for f in glob.glob(R+'data/sites_*.csv'):
    for r in csv.DictReader(open(f)): sites[r['site_id']]=r
for f in glob.glob(R+'data/organizations_*.csv'):
    for r in csv.DictReader(open(f)): orgs[r['org_id']]=r
def nk(s):
    s=s.lower()
    for a,b in [('street','st'),('road','rd'),('avenue','ave'),('drive','dr'),('boulevard','blvd'),('parkway','pkwy'),('east','e'),('west','w'),('north','n'),('south','s'),('lane','ln'),('court','ct'),('highway','hwy'),('northwest','nw'),('northeast','ne'),('southwest','sw'),('southeast','se'),('circle','cir'),('place','pl')]:
        s=re.sub(r'\b'+a+r'\b',b,s)
    s=re.sub(r'\b(suite|ste|unit|bldg|building)\b.*$','',s); s=s.split('#')[0]
    return re.sub(r'[^a-z0-9]','',s)
bykey={}
for sid,r in sites.items():
    if r['street_address']: bykey.setdefault(nk(r['street_address']),set()).add(sid)
NOTE_ST=re.compile(r'\b(\d{1,6}[A-Z]?)\s+((?:[NSEW]\.?\s+)?[A-Z0-9][A-Za-z0-9\.\' ]{1,35}?\b(?:RD|ROAD|ST|STREET|AVE|AVENUE|DR|DRIVE|BLVD|BOULEVARD|PKWY|PARKWAY|WAY|LANE|LN|CT|COURT|CIR|CIRCLE|PL|PLACE|HWY|HIGHWAY|PIKE|TRAIL|TER|LOOP|RUN|ROUTE)\b\.?)',re.I)
def street_num(s):
    m=re.match(r'\s*(\d+)',s); return m.group(1) if m else ''
MAILCTX=re.compile(r'mail(ing)? (address|to|at)|by mail|remit|p\.?\s*o\.?\s*box|billing address|warehous|showroom|sales office',re.I)
def run(framefile,fetchfile,outfile):
    frame=[r for r in csv.DictReader(open(framefile))]
    fetch=json.load(open(fetchfile))
    out=[]
    for fr in frame:
        sid=fr['site_id']; s=sites[sid]; log=fetch.get(sid,[])
        found=[]; ok=0; tried=len(log); unavailable=0
        for m in log:
            if not m['code'].startswith('2'): unavailable+=1; continue
            p=RAW+hashlib.sha1(m['url'].encode()).hexdigest()[:16]+'.html'
            if not os.path.exists(p): continue
            ok+=1; t=text_of(open(p,'rb').read())
            for c in cands(t,s['city']):
                if pobox(c['street']): continue
                pre=t[max(0,t.find(c['quote'][:40])-0):][:0]
                c['url']=m['url']; c['sha256']=m['sha256']; c['ctx']=c['quote'][:80]
                found.append(c)
        groups={}
        for c in found: groups.setdefault(nk(c['street']),[]).append(c)
        for k1 in sorted(list(groups),key=len):
            for k2 in list(groups):
                if k1!=k2 and k1 in groups and k2.startswith(k1) and re.match(r'(dr|rd|st|ave|ct|ln|way|n|s|e|w|ne|nw|se|sw)$',k2[len(k1):]):
                    groups[k2]+=groups.pop(k1); break
        notes_streets=set(nk(a+' '+b) for a,b in NOTE_ST.findall(s['notes']))
        notes_nums=set(street_num(a) for a,b in NOTE_ST.findall(s['notes']))
        v=dict(site_id=sid,org_id=s['org_id'],site_name=s['site_name'],site_type=s['site_type'],city=s['city'],zip=s['zip'],tier=s['verification_tier'],website=fr['website'],pages_tried=tried,pages_ok=ok,verdict='STILL_UNCERTAIN',street='',url='',sha256='',quote='',page_zip='',reason='',flags='')
        flags=[]
        if not fr['website'] or fr['website'] in ('none_found',):
            v['reason']='no held operator website; need an own-site or filing witness of the physical street at the recorded city'
        elif ok==0:
            v['reason']=f'own-site fetch unavailable ({tried} attempts, route failure, not absence); need a readable own-site page with the physical street at the recorded city'
        elif not groups:
            v['reason']=f'{ok} own-site pages read, no street at recorded city {s["city"]}; need own-page physical street block at the recorded city'
        else:
            # choose
            keys=list(groups)
            # drop candidates whose all contexts are mailing/warehouse
            phys=[k for k in keys if not all(MAILCTX.search(c['quote'][:62]) for c in groups[k])]
            if len(keys)>1 and int(fr['org_sites_same_city'])>=1:
                # if notes agree with exactly one, pick it
                agree=[k for k in phys if k in notes_streets or any(street_num(groups[k][0]['street'])==n and n for n in notes_nums)]
                if len(agree)==1: phys=agree
            allz=set(c['zip'] for k in keys for c in groups[k] if c['zip'])
            if s['zip'] and allz and s['zip'] not in allz:
                v['street']=groups[keys[0]][0]['street']; v['url']=groups[keys[0]][0]['url']; v['quote']=groups[keys[0]][0]['quote']
                v['reason']=f'own-page ZIP {"/".join(sorted(allz))} conflicts with recorded ZIP {s["zip"]}; need integrator ruling on the ZIP before the street is applied'
            elif not phys:
                v['reason']='own-page street appears only in mailing/warehouse/PO context; need a physical-location statement'
                v['street']=groups[keys[0]][0]['street']
            elif len(phys)>1:
                v['reason']='own pages show several streets at the recorded city ('+' || '.join(groups[k][0]['street'] for k in phys)+'); need site-specific binding'
            else:
                k=phys[0]; cs=groups[k]
                best=sorted(cs,key=lambda c:(1 if MAILCTX.search(c['quote'][:62]) else 0, 1 if re.search(r'granting|permission|submitting|copyright|©|p\.?\s*o\.?\s*box',c['quote'],re.I) else 0, 0 if c['zip'] else 1, 0 if re.search('contact|location',c['url'],re.I) else 1))[0]
                v.update(street=best['street'],url=best['url'],sha256=best['sha256'],quote=best['quote'],page_zip=best['zip'])
                suites=set(re.sub(r'[^a-z0-9]','',c['street'].split(',',1)[1].lower()) if ',' in c['street'] else '' for c in cs)
                if len(suites-{''})>1:
                    flags.append('SUITE-CONFLICT on own pages: '+'; '.join(sorted(set(c['street'] for c in cs)))+' (manual pick required)')
                pz=set(c['zip'] for c in cs if c['zip'])
                if s['zip'] and pz and s['zip'] not in pz:
                    v['reason']=f'own-page ZIP {"/".join(sorted(pz))} conflicts with recorded ZIP {s["zip"]}; need integrator ruling on the ZIP before the street is applied'
                elif notes_nums and street_num(best['street']) not in notes_nums:
                    v['reason']='own-page street disagrees with the street recorded in notes ('+';'.join(sorted(notes_nums))+'); need dated address adjudication'
                elif int(fr['org_sites_same_city'])>1:
                    v['reason']=f'operator holds {fr["org_sites_same_city"]} sites in {s["city"]}; need site-specific binding'
                    oth=[x for x in bykey.get(k,set()) if x!=sid]
                    if oth: flags.append('SAME-ADDRESS sites: '+';'.join(f'{x} ({sites[x]["org_id"]} {sites[x]["site_name"][:40]})' for x in oth))
                else:
                    v['verdict']='VERIFIED'; v['reason']=''
                    oth=[x for x in bykey.get(k,set()) if x!=sid]
                    if oth: flags.append('ADDRESS-OVERLAP: '+';'.join(f'{x} ({sites[x]["org_id"]} {sites[x]["site_name"][:40]})' for x in oth))
        v['flags']=' | '.join(flags)
        out.append(v)
    pend={}
    for pf in glob.glob('b*_verdicts.csv'):
        if pf.startswith(outfile[:3]): continue
        for x in csv.DictReader(open(pf)):
            if x['verdict']=='VERIFIED': pend.setdefault(nk(x['street']),[]).append(x['site_id']+' ('+x['org_id']+' '+x['site_name'][:40]+', pending '+pf[:3]+')')
    ver=[o for o in out if o['verdict']=='VERIFIED']
    for o in ver:
        k=nk(o['street']); others=[f"{x['site_id']} ({x['org_id']} {x['site_name'][:40]}, this batch)" for x in ver if x is not o and nk(x['street'])==k]+[p for p in pend.get(k,[]) if p.split(' ')[0] not in o['flags']]
        if others:
            o['flags']=(o['flags']+' | ' if o['flags'] else '')+('ADDRESS-OVERLAP: ' if not o['flags'] else '')+';'.join(others)
    w=csv.DictWriter(open(outfile,'w'),fieldnames=list(out[0].keys()));w.writeheader();w.writerows(out)
    import collections
    print(collections.Counter(o['verdict'] for o in out))
if __name__=='__main__': run(*sys.argv[1:4])
