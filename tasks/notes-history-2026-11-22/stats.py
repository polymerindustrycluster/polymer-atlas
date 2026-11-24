import collections, re
from corpus import run
from notes_split import hits
orgs, sites = run()
for name, rows in (("organizations",orgs),("sites",sites)):
    c=collections.Counter(); rowc=collections.Counter(); pw=0
    for r in rows:
        ds={p["disp"] for p in r["_parts"]}
        for p in r["_parts"]: c[p["disp"]]+=1
        rowc["has_READER" if "READER" in ds else "auto-only"]+=1
        if hits(r["notes"]): pw+=1
    ctl=sum(1 for r in rows if re.search(r"Grok|spaghetti|PASS \d|verdicts\.csv|staging|working/|burn-down|integrator assert",r["notes"]))
    print(name,len(rows),"pieces",dict(c),"rows",dict(rowc),"rows with word-list hit",pw,"controller-style regex rows",ctl)
