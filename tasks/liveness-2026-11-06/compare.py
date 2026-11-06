"""Compare observed DNS/parking signals, not business closures."""
from collections import Counter
from federal_signals import HERE, ROOT, read, write
old={r['domain']:r for r in read(ROOT/'tasks/liveness-sweep-2026-11-01/signals.csv')}
new={r['domain']:r for r in read(HERE/'sweep/signals.csv')}
assert len(old)==len(read(ROOT/'tasks/liveness-sweep-2026-11-01/signals.csv'))
assert len(new)==len(read(HERE/'sweep/signals.csv'))
common=old.keys() & new.keys()
rows=[dict(domain=d,previous=old.get(d,{}).get('signal_class','NOT_IN_FRAME'),current=new.get(d,{}).get('signal_class','NOT_IN_FRAME')) for d in sorted(old.keys()|new.keys())]
write(HERE/'comparison.csv',rows,['domain','previous','current'])
print('Unit: unique normalized eligible domains (not business closures).')
for label, domains in [('previous_full',old),('current_full',new),('common_previous',{d:old[d] for d in common}),('common_current',{d:new[d] for d in common})]:
    c=Counter(r['signal_class'] for r in domains.values())
    print(label,len(domains),'NXDOMAIN',c['NXDOMAIN'],'PARKED_SUSPECT',c['PARKED_SUSPECT'],'combined',c['NXDOMAIN']+c['PARKED_SUSPECT'])
print('new frame',len(new.keys()-old.keys()),'left frame',len(old.keys()-new.keys()))
