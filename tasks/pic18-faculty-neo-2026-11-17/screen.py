import json,re,view,csv,sys
P=view.P
man={r['url']:r['sha256'] for r in csv.DictReader(open(P+'manifest.csv'))}
KW=re.compile(r'polymer|macromolec|elastomer|hydrogel|rubber|plastic|resin|composite|copolymer|polyester|polyurethane|silicone|nanofib|electrospin|membrane|PEG|polyethylene|gel\b|latex',re.I)
def screen(url,maxl=6):
    h=man.get(url)
    if not h: return None
    L=view.text(view.raw(h))
    hits=[l for l in L if KW.search(l) and len(l)<600 and 'Student' not in l[:10]]
    return h,L,hits[:maxl]
if __name__=="__main__":
    sel=json.load(open(sys.argv[1]))
    for nm,u,pid,title in sel:
        r=screen("https://case.edu"+u)
        if not r: print("NOFETCH",nm); continue
        h,L,hits=r
        print("==",nm,h[:8],'|',title.split(' | ',1)[1][:110] if ' | ' in title else title[:100])
        for x in hits: print("    ",x[:260])
