"""Raw-check band-B VERIFIED rows: re-fetch each gate URL (NAS Firecrawl full page, then Jina Reader), match the quote as
a contiguous word sequence, and for Gate A also require the person's surname within 40 words of the quote (a bare
"Professor" matches any roster page). Resumable: rows already in the output are skipped.
    python -I rawcheck_people.py <merged.csv> <out.csv>"""
import csv, re, sys, unicodedata, urllib.request
sys.path.insert(0, r"C:\Users\JohnSwanson\Documents\pic-github\polymer-faculty-census")
from tools.layer_b_fetch import call, env  # noqa: E402

W = lambda s: re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower())
SUFFIX = {"jr", "sr", "ii", "iii", "iv", "phd", "md", "pe", "dr", "prof"}
surname = lambda n: next((t for t in reversed(W(n)) if t not in SUFFIX and len(t) > 1), "")
dom = lambda u: ".".join(re.sub(r"^https?://", "", u or "").split("/")[0].split(":")[0].lower().split(".")[-2:])
fc, key = env("FIRECRAWL_BASE_URL").rstrip("/"), env("FIRECRAWL_NAS_API_KEY")
cache = {}


def plain(u):
    """The lanes' own route (fetch.py): a plain GET, visible text."""
    import html
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (compatible; polymer-atlas-people-check/1.0)"})
        with urllib.request.urlopen(req, timeout=30) as r:
            if dom(r.geturl()) != dom(u):  # a redirect off the requested domain is not that page
                return None
            raw = r.read(4_000_000).decode("utf-8", "replace")
        raw = re.sub(r"(?is)<(script|style|noscript|svg|template)[^>]*>.*?</\1>", " ", raw)
        return W(html.unescape(re.sub(r"<[^>]+>", " ", raw)))
    except Exception:
        return None


def pages(u):
    """Every independent re-fetch route that returned text: Firecrawl, Jina, plain GET."""
    first = page(u)
    if (u, "plain") not in cache:
        cache[(u, "plain")] = plain(u)
    return [w for w in (first, cache[(u, "plain")]) if w]


def page(u):
    if u in cache:
        return cache[u]
    words = None
    try:
        d = call(f"{fc}/v2/scrape", {"url": u, "formats": ["markdown"], "onlyMainContent": False},
                 {"Authorization": f"Bearer {key}"}, timeout=120).get("data") or {}
        m = d.get("metadata") or {}
        if m.get("statusCode") == 200 and dom(m.get("url") or u) == dom(u):
            words = W(d.get("markdown"))
    except Exception:
        pass
    if not words or len(words) < 40:
        try:
            req = urllib.request.Request("https://r.jina.ai/" + u, headers={"Authorization": f"Bearer {env('JINA_API_KEY')}", "User-Agent": "polymer-atlas/1.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                words = W(r.read().decode("utf-8", "replace"))
        except Exception:
            pass
    cache[u] = words
    return words


def at(words, q):
    q = W(q)
    return next((i for i in range(len(words) - len(q) + 1) if words[i:i + len(q)] == q), None) if q and words else None


def main():
    src, outp = sys.argv[1], sys.argv[2]
    try:
        done = {r["lead_id"] for r in csv.DictReader(open(outp, encoding="utf-8"))}
    except FileNotFoundError:
        done = set()
    rows = [r for r in csv.DictReader(open(src, encoding="utf-8")) if r["lead_id"] not in done]
    new = not done
    with open(outp, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["lead_id", "gate_a", "gate_a_surname", "gate_b"], lineterminator="\n")
        if new:
            w.writeheader()
        for r in rows:
            sur = surname(r["full_name"])
            qa = len(W(r["gate_a_quote"]))
            A = pages(r["gate_a_url"]); hits = [(w, at(w, r["gate_a_quote"])) for w in A]
            ga = "unfetchable" if not A else ("yes" if any(i is not None for _, i in hits) else "no")
            near = "yes" if any(i is not None and sur in w[max(0, i - 40):i + qa + 40] for w, i in hits) else "no"
            B = pages(r["gate_b_url"])
            gb = "unfetchable" if not B else ("yes" if any(at(w, r["gate_b_quote"]) is not None for w in B) else "no")
            res = {"lead_id": r["lead_id"], "gate_a": ga, "gate_a_surname": near, "gate_b": gb}
            w.writerow(res); fh.flush()
            print(r["lead_id"], res["gate_a"], res["gate_a_surname"], res["gate_b"], flush=True)


if __name__ == "__main__":
    main()
