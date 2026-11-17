#!/usr/bin/env python3
"""Build frame.csv from the stored listing pages (sha-named in persist). Emails/phones are dropped at parse time."""
import csv, html, re, sys, urllib.parse
from pathlib import Path
P = Path("/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-faculty-akron-2026-11-17")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
# (unit, page url, sha) -- every url is in manifest.csv with its provenance
PAGES = [
 ("SPSPE", "https://www.uakron.edu/polymer/about-us/our-people/faculty", "3c8e297b24b2ec382dbc3953f75216d50e61d5a5e987237c63c1fc09712af1e6"),
 ("SPSPE-adjunct", "https://www.uakron.edu/polymer/about-us/our-people/adjunct", "9b3ae6c72e7f679e18077ff4a31b427d05c41cf74371f2ca3e8bf50de9b08a26"),
 ("SPSPE-emeritus", "https://www.uakron.edu/polymer/about-us/our-people/emeritus", "076dfa1f5af87d20e5fe146b68a976354452954112917a999c1eedcb94fd525a"),
 ("Chemistry", "https://www.uakron.edu/chemistry/faculty-staff/index.dot", "61a0593364883d1d5f67aaf25a22cb75802c006596bba1ca80f0b0e8725fe7c4"),
 ("CBCE", "https://www.uakron.edu/engineering/cbe/our-people/", "1c30700f1d6438b9a677de784ebf13e7c53b3b911ae2938dd98e968ad4527134"),
 ("BME", "https://www.uakron.edu/engineering/bme/our-people/", "eadc2e0780336b99d1123e4e0dd1bf7af8772de9c5e6b7f0d6ffd8089550dd49"),
 ("BME", "https://www.uakron.edu/engineering/bme/our-people/?currentPage=2", "a478b704c03efd186b8d0b9835fd432aabf3a185c13de7702ec10179f541958a"),
 ("ME", "https://www.uakron.edu/engineering/me/our-people/", "84fc3a3c2b1b9096f44582011291a77001fa5737b392b86570aca756eaa2dc29"),
 ("ME", "https://www.uakron.edu/engineering/me/our-people/?currentPage=2", "bfbe66a8a0b1c182d6e97962a2156218f902f25d5d8d6c96081e82d14ec505fb"),
 ("ME", "https://www.uakron.edu/engineering/me/our-people/?currentPage=3", "883658fb8fd2cc0abdd1e25a1c657860117b7e2cd19e3f61bc0b3018de50500f"),
 ("ME", "https://www.uakron.edu/engineering/me/our-people/?currentPage=4", "cb434651a545b66685d7bf043f4788179ecd8dec87922f68ca0d3fcd33f451fd"),
]
GATE_A_OUT = re.compile(r"emerit|adjunct|instruction|practice|lecturer|visiting|dean emer|technician|manager|secretary|coordinator|specialist|engineer\b|scientist", re.I)
GATE_A_IN = re.compile(r"\bprofessor\b", re.I)

PRIV = re.compile(r"@|\d{3}[-.)]\s*\d{3}[-.]\d{4}")
def scrub(x):
    return "" if PRIV.search(x) else x

def norm(n):
    n = re.sub(r"\(.*?\)|,?\s*Ph\.?D\.?|^(Dr|Mr|Ms|Mrs)\.?\s+|[^A-Za-z\s-]", " ", n)
    w = n.lower().replace("-", " ").split()
    w = [x for x in w if len(x) > 1]
    return (w[0], w[-1]) if w else ("", "")

def held_matches(people, name):
    f, l = norm(name)
    return [(p["person_id"], p["full_name"], p["institution_org_id"]) for p in people
            if norm(p["full_name"])[1] == l and (norm(p["full_name"])[0].startswith(f) or f.startswith(norm(p["full_name"])[0]))]

def parse(unit, url, sha):
    h = (P / sha).read_bytes().decode("utf-8", "replace")
    out = []
    for m in re.finditer(r'<div class="bio-item"[^>]*>(.*?)</div>', h, re.S):
        b = m.group(1)
        a = re.search(r'<p>\s*<a href="([^"]+)">([^<]+)</a>', b)
        if not a: continue
        t = re.search(r"<b>Title:\s*</b>(.*?)<br", b, re.S); d = re.search(r"<b>Dept/Program:\s*</b>(.*?)<br", b, re.S)
        name = html.unescape(a.group(2)).strip()
        href = urllib.parse.urljoin(url.split("?")[0], html.unescape(a.group(1)))
        out.append({"unit": unit, "name": name, "title": html.unescape(t.group(1)).strip() if t else "",
                    "dept": html.unescape(d.group(1)).strip() if d else "", "profile_url": href, "listing_url": url, "listing_sha": sha})
    return out

def parse_pb(unit, url, sha):
    """adjunct / emeritus pages: <p><b>name</b><br />title<br />affiliation</p>"""
    h = re.sub(r"<!--.*?-->", "", (P / sha).read_bytes().decode("utf-8", "replace"), flags=re.S)  # commented-out entries are not published
    out = []
    for m in re.finditer(r"<p><(?:b|strong)>([^<]+)</(?:b|strong)><br />(.*?)</p>", h, re.S):
        parts = [html.unescape(x).strip() for x in re.split(r"<br\s*/?>", m.group(2))]
        out.append({"unit": unit, "name": html.unescape(m.group(1)).strip(), "title": parts[0], "dept": scrub(parts[1]) if len(parts) > 1 else "",
                    "profile_url": "", "listing_url": url, "listing_sha": sha})
    return out

def build():
    # rows this lane wrote (PERSON-002300..002399) are excluded so that verdicts do not change after build.py has run
    people = [p for p in csv.DictReader(open(ROOT / "data/people.csv", newline="", encoding="utf-8")) if not 2300 <= int(p["person_id"][7:]) <= 2399]
    rows = []
    for unit, url, sha in PAGES:
        for r in (parse_pb if unit in ("SPSPE-adjunct", "SPSPE-emeritus") else parse)(unit, url, sha):
            r["gate_a_listing"] = "pass" if unit not in ("SPSPE-adjunct", "SPSPE-emeritus") and GATE_A_IN.search(r["title"]) and not GATE_A_OUT.search(r["title"]) else "fail"
            hm = held_matches(people, r["name"])
            r["held_ids"] = ";".join(f"{i}@{o}" for i, _, o in hm)
            r["held_at_akron"] = "yes" if any(o == "ORG-000501" for _, _, o in hm) else ""
            rows.append(r)
    seen, uniq = set(), []
    for r in rows:  # same person may appear on two dept pages; keep the first listing
        k = (r["unit"], r["name"]) if r["unit"].startswith("SPSPE-") else ("", r["profile_url"], r["name"])
        if k in seen: continue
        seen.add(k); uniq.append(r)
    return uniq

if __name__ == "__main__":
    rows = build()
    cols = ["unit", "name", "title", "dept", "profile_url", "listing_url", "listing_sha", "gate_a_listing", "held_ids", "held_at_akron"]
    with open(HERE / "frame.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    from collections import Counter
    print(Counter(r["unit"] for r in rows)); print(Counter((r["unit"], r["gate_a_listing"]) for r in rows))
