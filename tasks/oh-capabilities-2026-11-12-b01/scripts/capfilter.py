import csv,re,sys
CTX=re.compile(r'\b(we|our|us|offers?|provides?|providing|specializ\w*|capabilit\w*|services?|manufactur\w*|produc\w*|custom|in-house|supplier|compounder|molder|molds?|made|make|makes)\b',re.I)
fr=list(csv.DictReader(open('cap_frame.csv')))
lo,hi=int(sys.argv[1]),int(sys.argv[2])
ids=[r['site_id'] for r in fr[lo:hi]]
P=list(csv.DictReader(open('cap_props.csv'))); keep=[]
for p in P:
    q=p['quote']
    if p['site_id'] not in ids: continue
    if '?' in q or q.count(' , ')>=3 or not CTX.search(q): continue
    keep.append(p)
w=csv.DictWriter(open(sys.argv[3],'w'),fieldnames=list(P[0].keys())+['k']);w.writeheader()
for i,p in enumerate(keep): p['k']=i; w.writerow(p)
for sid in ids:
    ps=[p for p in keep if p['site_id']==sid]
    if not ps: continue
    f=[r for r in fr if r['site_id']==sid][0]
    print(f"## {sid} {f['site_name'][:34]}|{f['city']}|r{f['ring']}|p={f['site_proc'][:40]} m={f['site_mat'][:30]}|oth={ps[0]['other'][:30]} loc={ps[0]['loc']}")
    for p in ps: print(f"{p['k']} {p['term']}: {p['quote'][:150]} <{p['url'].split('/',3)[-1][:30]}>")
print(len(keep))
