import urllib.request,urllib.parse,http.cookiejar,re,html
from html.parser import HTMLParser
BASE="https://edocpub.epa.ohio.gov/publicportal/"
UA="Mozilla/5.0 (compatible; AtlasSiteCorpus/1.0)"
class F(HTMLParser):
    def __init__(s): super().__init__(); s.f={}; s.sel=None; s.opts={}; s.cur=None; s.txt=None
    def handle_starttag(s,t,a):
        a=dict(a)
        if t=="input" and a.get("name") and a.get("type","text") not in("submit","image","button","checkbox","radio"): s.f[a["name"]]=a.get("value") or ""
        if t=="select": s.sel=a.get("name"); s.opts[s.sel]=[]; s.f.setdefault(s.sel,"")
        if t=="option" and s.sel:
            s.cur=a.get("value",""); s.opts[s.sel].append([s.cur,""])
            if "selected" in a: s.f[s.sel]=s.cur
    def handle_data(s,d):
        if s.sel and s.opts.get(s.sel) and s.cur is not None: s.opts[s.sel][-1][1]+=d.strip()
    def handle_endtag(s,t):
        if t=="select": s.sel=None; s.cur=None
def parse(h): p=F(); p.feed(h); return p
class Sess:
    def __init__(s):
        s.o=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())); s.o.addheaders=[("User-Agent",UA)]
        s.h=s.o.open(BASE,timeout=60).read().decode('utf8','replace')
    def post(s,upd,target=""):
        p=parse(s.h); d=dict(p.f); d.update(upd); d["__EVENTTARGET"]=target; d["__EVENTARGUMENT"]=""
        s.h=s.o.open(urllib.request.Request(BASE,urllib.parse.urlencode(d).encode()),timeout=90).read().decode('utf8','replace'); return s.h
if __name__=="__main__":
    s=Sess(); p=parse(s.h); print(p.opts["ctl00$search$ddlDocType"][:30])
