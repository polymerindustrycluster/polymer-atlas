#!/usr/bin/env python3
"""Websites for organizations that had none (2026-11-04, owner-approved Serper + Jina run).

    python3 tasks/websites-2026-11-04/build.py --data-dir data [--apply --i-am-the-integrator]
        -> edits.csv (apply with scripts/apply_p1_crm_scrub.py --packet-dir), evidence_append.csv, holds.csv,
           no_own_domain.csv

Input: `search_results.csv`, written by `search.py` (the v3 rule: a Serper result whose domain carries a distinctive
name token, and a homepage, read through Jina Reader, that carries every such token).
Each accepted website is written only when all three of these hold:
1. The record still has no website.
2. No other held organization already uses the same domain. A shared domain may mean the record is a duplicate, so it
   is held for a dedupe decision (AGENTS.md §3 step 1).
3. A homepage re-fetch now yields a verbatim span of 25 words or fewer that contains the name tokens. The span is the
   evidence quote.
Evidence: one `existence` row per website, `own_site` at `supports_A` (the class ceiling, SCHEMA §4.13). The company's
own domain naming the entity is the primary identity witness, and V-25 requires A-strength existence evidence on
tier-A records. The row supports existence only, not the address. Tiers are not changed here.
`no_own_domain.csv` lists organizations for which no own-domain result came back, with the top search hosts. Many are
small firms with no site; others look acquired (their search results point at a buyer). It is a findings list for a
status and ownership pass, and nothing in it is applied.
"""
import argparse, csv, hashlib, json, os, re, sys, urllib.request
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(HERE.parent / "census-gap-people-2026-11-03"))
import atlas  # noqa: E402
from build_integration import append_rows, read  # noqa: E402

TODAY, BY = "2026-11-04", "claude-code websites-2026-11-04"
GENERIC = {"plastics", "plastic", "products", "industries", "company", "corporation", "manufacturing", "group", "international",
           "usa", "america", "american", "north", "technologies", "technology", "systems", "solutions", "enterprises", "and", "the"}
CACHE = HERE / "jina_cache"
PLACE = {"alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware", "florida", "georgia",
         "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine", "maryland", "massachusetts",
         "michigan", "minnesota", "mississippi", "missouri", "montana", "nebraska", "nevada", "hampshire", "jersey", "mexico",
         "york", "carolina", "dakota", "ohio", "oklahoma", "oregon", "pennsylvania", "rhode", "island", "tennessee", "texas",
         "utah", "vermont", "virginia", "washington", "wisconsin", "wyoming", "akron", "cleveland", "midwest", "southern",
         "northern", "eastern", "western", "pacific", "atlantic", "central", "great", "lakes", "valley", "river", "national"}
# A Jina fetch of a protected site can return the challenge page itself, whose URL carries the domain. In the pilot
# this let lancer-systems.com and schrader-pacific.com "match" on the URL alone.
BOTWALL = re.compile(r"sgcaptcha|captcha|just a moment|attention required|verify you are human|access denied|cf-chl", re.I)
# Sanity check against a same-name or same-acronym company: the pilot accepted epcusa.com, a computer refurbisher.
POLY = re.compile(r"plastic|polymer|rubber|resin|coating|paint|adhesive|sealant|foam|composite|mold|extru|film|packag|vinyl|"
                  r"urethane|silicone|fiberglass|elastomer|\bink|laminat|pvc|nylon|polyeth|polyprop|thermo|tire|latex|"
                  r"gasket|hose|pipe|container|bottle|caulk|epoxy|acrylic|fiber|fibre|tape|label|membrane|compound", re.I)
# Cross-family refute (grok + codex, 60-row sample, 2026-11-04), each verdict checked against the cached homepage.
COUNCIL_HOLD = {
    "ORG-002556": "council: ametek.com is the former owner's corporate site; the record says Niche Polymer bought this plant in 2020",
    "ORG-004194": "council: stockmeier.com is the group site and the quote is a Tampa trade-show listing, not the Clarksburg entity",
}


def dom(u):
    return re.sub(r"^(https?://)?(www\.)?", "", (u or "").strip().lower()).split("/")[0]


def jina(url, key):
    CACHE.mkdir(exist_ok=True)
    p = CACHE / (hashlib.sha1(url.encode()).hexdigest() + ".md")
    if p.exists():
        return p.read_text(encoding="utf-8")
    req = urllib.request.Request("https://r.jina.ai/" + url, headers={"Authorization": f"Bearer {key}", "User-Agent": "polymer-atlas/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        t = r.read().decode("utf-8", "replace")
    p.write_text(t, encoding="utf-8")
    return t


def span(text, toks):
    """A verbatim phrase from one line of the page: it starts at the first name token and runs to the end of the line
    or 25 words, whichever comes first. It must contain every token, and at least 4 words when the line has them. A
    bare one-word name ("Rhodes") is too thin to stand as evidence that the domain is this company's."""
    best = None
    for line in text.splitlines():
        if line.startswith(("URL Source:", "Markdown Content:", "Published Time:", "Title:")) or "](" in line[:3]:
            continue
        words = [w for w in re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", line).split() if w.strip("#*|-")]
        sq = [set(atlas.squash(w).split()) for w in words]
        starts = [i for i, s in enumerate(sq) if s & set(toks)]
        for i in starts:
            win = words[i:i + 25]
            if all(any(t in s for s in sq[i:i + len(win)]) for t in toks) and (len(win) >= 4 or len(words) < 4):
                cand = " ".join(win).strip(" #*|[]()")
                if best is None or abs(len(cand.split()) - 12) < abs(len(best.split()) - 12):
                    best = cand  # prefer a sentence-sized phrase (~12 words) over a fragment or a 25-word run
                break
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    a = ap.parse_args()
    data = Path(a.data_dir).resolve()
    key = dict(re.findall(r"^([A-Z0-9_]+)=(.*)$", Path(os.path.expanduser("~/.env")).read_text(encoding="utf-8"), re.M))["JINA_API_KEY"].strip()
    orgs, shard = {}, {}
    for f in sorted(data.glob("organizations_*.csv")):
        for r in read(f):
            orgs[r["org_id"]], shard[r["org_id"]] = r, f.stem.split("_", 1)[1]
    held_dom = defaultdict(set)
    for oid, r in orgs.items():
        if dom(r["website"]):
            held_dom[dom(r["website"])].add(oid)
    ev = [e for f in sorted(data.glob("evidence*.csv")) for e in read(f)]
    evd = max(int(e["evidence_id"][4:]) for e in ev if e["evidence_id"][4:].isdigit()) + 1  # AGENTS §3: above the max
    res = read(HERE / "search_results.csv")
    edits, new_ev, holds, nod = [], [], [], []
    seen_dom = defaultdict(list)
    for r in res:
        if r["result"] == "accept":
            seen_dom[dom(r["website"])].append(r["org_id"])
    for r in res:
        oid = r["org_id"]
        if r["result"] == "no_candidate":
            nod.append({"org_id": oid, "legal_name": r["legal_name"], "hq_city": r["hq_city"], "hq_state": r["hq_state"], "top_hosts": r["top_hosts"]})
            continue
        if r["result"] != "accept":
            continue
        o, d = orgs.get(oid), dom(r["website"])
        why = []
        if not o: why.append("record not found")
        elif o["website"].strip(): why.append(f"record already has website {o['website']}")
        if held_dom.get(d): why.append(f"domain already held by {sorted(held_dom[d])} (possible duplicate)")
        if len(seen_dom[d]) > 1: why.append(f"same domain accepted for {seen_dom[d]} (possible duplicate)")
        if oid in COUNCIL_HOLD: why.append(COUNCIL_HOLD[oid])
        quote = None
        if not why:
            full = [t for t in atlas.name_key(o["legal_name"]).split() if t not in ("and", "the")]
            toks = [t for t in full if t not in GENERIC and len(t) > 2] or full
            # The domain must carry a distinctive word that is not a place name. madeinalabama.com "matched" an
            # Alabama company on the state name alone.
            dtoks = [t for t in toks if t not in PLACE]
            initials = "".join(t[0] for t in full)
            dlabel = d.split(".")[0].replace("-", "")
            if not (any(t in dlabel for t in dtoks) or (len(initials) >= 3 and dlabel.startswith(initials))):
                why.append(f"domain {d} carries no distinctive non-place name token")
            try:
                page = jina(r["website"], key)
                # Full normalized name only. A distinctive-word-only match let allegheny.com ("Allegheny Card
                # Solutions") through for a different Allegheny company, so those are held for review instead.
                quote = span(page, full)
                if not quote and span(page, toks):
                    why.append("homepage carries only the distinctive name word, not the full name: review")
            except Exception as e:
                why.append(f"re-fetch failed ({type(e).__name__})"); page = ""
            if not why:
                if BOTWALL.search(page[:3000]):
                    why.append("fetched page is a bot wall or challenge page, not the site")
                elif not POLY.search(page):
                    why.append("page states no polymer-related term (wrong company with the same name or acronym?)")
                elif not quote or "http" in quote or "](" in quote or len(quote.split()) < 3:
                    why.append("no clean verbatim phrase (3 to 25 words, no link text) carries the name")
        if why:
            holds.append({"org_id": oid, "website": r["website"], "reason": "; ".join(why)}); continue
        edits.append({"file": f"organizations_{shard[oid]}.csv", "row_id": oid, "column": "website",
                      "old_sha256": hashlib.sha256(o["website"].encode()).hexdigest(), "new_value": r["website"],
                      "edit_class": "WEBSITE_FILL", "rationale": "own domain found by name search; homepage carries the name (evidence row)"})
        new_ev.append({"evidence_id": f"EVD-{evd:06d}", "record_table": "organizations", "record_id": oid, "claim_type": "existence",
                       "claim_detail": f"website {r['website']}: \"{quote}\"", "source_class": "own_site", "source_ref": r["website"],
                       "observed_date": TODAY, "tier_effect": "supports_A", "created_by": BY,
                       "notes": "website fill 2026-11-04: homepage re-fetched (Jina Reader) and the quote found verbatim"})
        evd += 1
    for name, rows, fields in (("edits.csv", edits, ["file", "row_id", "column", "old_sha256", "new_value", "edit_class", "rationale"]),
                               ("evidence_append.csv", new_ev, list(ev[0].keys())),
                               ("holds.csv", holds, ["org_id", "website", "reason"]),
                               ("no_own_domain.csv", nod, ["org_id", "legal_name", "hq_city", "hq_state", "top_hosts"])):
        with open(HERE / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n", extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    assert len({e["row_id"] for e in edits}) == len(edits), "two edits for one org"
    print(f"websites {len(edits)}; evidence {len(new_ev)}; holds {len(holds)} {Counter(h['reason'].split(' (')[0][:40] for h in holds).most_common(4)}; no own domain {len(nod)}")
    if a.apply:
        if data == (ROOT / "data").resolve() and not a.i_am_the_integrator:
            sys.exit("appending to the real data/ is integrator work; pass --i-am-the-integrator")
        by = defaultdict(list)
        for e in new_ev:
            by[f"evidence_organizations_{shard[e['record_id']]}.csv"].append(e)
        for name, rows in by.items():
            append_rows(data / name, rows)
        print("evidence appended; now apply edits.csv with scripts/apply_p1_crm_scrub.py")


if __name__ == "__main__":
    main()
