import csv,sys
fr=list(csv.DictReader(open('cap_frame.csv')))
lo,hi=int(sys.argv[1]),int(sys.argv[2]); F={r['site_id']:r for r in fr[lo:hi]}
for i,m in enumerate(csv.DictReader(open('cap_menu.csv'))):
    if m['site_id'] not in F: continue
    f=F[m['site_id']]
    if f['site_mat' if m['type']=='material' else 'site_proc']: continue
    print(f"M{i} {m['site_id']} {f['site_name'][:28]}|r{f['ring']}| {m['term']}: {m['quote'][-140:]} <{m['url'].split('/',3)[-1][:30]}>")
