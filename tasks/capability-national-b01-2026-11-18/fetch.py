#!/usr/bin/env python3
"""Fetch the stored-page corpus for slice.csv: each org's homepage plus up to 5 same-host pages whose path names
capabilities, services, processes, products, materials, about, facilities or contact (link ranking after b01's
capfetch.py). Raw HTML and visible text are stored outside the repository with their SHA-256 in manifest.csv.
Resumable: a page already in the manifest is not fetched again. A failed fetch is availability, never absence.

    python3 tasks/capability-national-b01-2026-11-18/fetch.py <corpus dir>
"""
import csv, hashlib, html, re, sys, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

T = Path(__file__).resolve().parent
UA = "Mozilla/5.0 (compatible; polymer-atlas-capability-check/1.0; +https://github.com/polymerindustrycluster/polymer-atlas)"
KEY = re.compile(r"capabilit|service|process|material|manufactur|about|what-we-do|facilit|plant|location|contact|product|industr", re.I)
SKIP = re.compile(r"\.(pdf|jpe?g|png|gif|svg|zip|docx?|xlsx?)$|career|job|news|blog|event|privacy|cookie|login|cart", re.I)


def get(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=25) as r:
            return r.geturl(), r.read(4_000_000)
    except Exception:
        return url, b""


def visible(raw):
    t = raw.decode("utf-8", "replace")
    t = re.sub(r"(?is)<(script|style|noscript|svg|template)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"(?i)<(br|/p|/div|/li|/h\d|/tr)[^>]*>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip())


def links(base, raw):
    out, b = [], urllib.parse.urlparse(base)
    for href in re.findall(r'href=["\']([^"\'#]+)', raw.decode("utf-8", "ignore")):
        u = urllib.parse.urljoin(base, html.unescape(href)).split("?")[0]
        p = urllib.parse.urlparse(u)
        if (p.scheme.startswith("http") and p.netloc.replace("www.", "") == b.netloc.replace("www.", "")
                and KEY.search(p.path) and not SKIP.search(p.path) and p.path.count("/") <= 3 and u not in out):
            out.append(u)
    rank = lambda u: (0 if re.search("capabilit", u, re.I) else 1 if re.search("service|process|manufactur|facilit|plant", u, re.I)
                      else 2 if re.search("product|material", u, re.I) else 3 if re.search("about|location|contact", u, re.I) else 4, len(u))
    return sorted(out, key=rank)


def work(row, corpus, done):
    site = row["website"]
    host = re.sub(r"^https?://", "", site).split("/")[0].replace("www.", "")
    rows, base, home = [], None, b""
    for v in dict.fromkeys([site if site.startswith("http") else "https://" + site, "https://" + host, "https://www." + host]):
        eff, body = get(v)
        if len(body) > 500:
            base, home = eff, body; break
    if not base:
        return [dict(site_id=row["site_id"], org_id=row["org_id"], url=site, status="unreachable", raw_file="", text_file="", sha256="")]
    for u, body in [(base, home)] + [(u, None) for u in links(base, home)[:5]]:
        if (row["site_id"], u) in done:
            continue
        if body is None:
            u, body = get(u)
        if len(body) < 500:
            rows.append(dict(site_id=row["site_id"], org_id=row["org_id"], url=u, status="empty", raw_file="", text_file="", sha256="")); continue
        sha = hashlib.sha256(body).hexdigest()
        d = corpus / row["org_id"]; d.mkdir(parents=True, exist_ok=True)
        (d / f"{sha}.html").write_bytes(body); (d / f"{sha}.txt").write_text(visible(body), encoding="utf-8")
        rows.append(dict(site_id=row["site_id"], org_id=row["org_id"], url=u, status="ok",
                         raw_file=f"{row['org_id']}/{sha}.html", text_file=f"{row['org_id']}/{sha}.txt", sha256=sha))
    return rows


def main():
    corpus = Path(sys.argv[1]); corpus.mkdir(parents=True, exist_ok=True)
    man = corpus / "manifest.csv"
    have = list(csv.DictReader(open(man, encoding="utf-8"))) if man.exists() else []
    done = {(r["site_id"], r["url"]) for r in have if r["status"] == "ok"}
    todo = [r for r in csv.DictReader(open(T / "slice.csv", encoding="utf-8")) if r["site_id"] not in {h["site_id"] for h in have}]
    with ThreadPoolExecutor(10) as ex:
        for res in ex.map(lambda r: work(r, corpus, done), todo):
            have += res
            with open(man, "w", newline="", encoding="utf-8") as fh:  # rewrite after each org, so a killed run resumes
                w = csv.DictWriter(fh, fieldnames=list(res[0]), lineterminator="\n"); w.writeheader(); w.writerows(have)
    ok = {r["site_id"] for r in have if r["status"] == "ok"}
    print(f"sites {len({r['site_id'] for r in have})}; with >=1 stored page {len(ok)}; stored pages {sum(r['status'] == 'ok' for r in have)}")


if __name__ == "__main__":
    main()
