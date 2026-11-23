import collections, re, sys
from corpus import run
orgs, sites = run()
def norm(t):
    t=re.sub(r"\d+","#",t.strip()); return re.sub(r"\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b","N",t)[:80]
disp=sys.argv[1]; a,b=int(sys.argv[2]),int(sys.argv[3])
c=collections.Counter(); ex={}
for r in orgs+sites:
    for p in r["_parts"]:
        if p["disp"]==disp:
            k=norm(p["text"]); c[k]+=1; ex.setdefault(k,p["text"].strip()[:170])
print(disp,len(c),"templates",sum(c.values()),"pieces")
for k,n in c.most_common(b)[a:]: print(n,"|",ex[k])
