#!/usr/bin/env python3
"""ORCID completion pass 2 (2026-11-11): retry the 649 people records the first fill (tasks/people-orcid-2026-11-09,
PR #259) left unlinked, under the SAME linking rule (SCHEMA §4.21: a name resemblance finds a candidate; only the
iD itself links one). Nothing in the linking rule is loosened. What changes is only the finders and the target set:
  - Targets: people with no row in data/people_identifiers.csv (649 at main a3b395f5). Already-linked people are
    never re-judged; an iD already recorded for one person that passes for another is a dedupe alarm (§4.21),
    journaled and listed in alarm_pairs.csv, never minted as a second row.
  - Page finder: raw fetch first (as pass 1); when the raw read is empty or near-empty (blocked / JS shell,
    187 pages were unreadable in pass 1), fall back to the Jina Reader rendering of the same URL.
  - Search finder: pass 1's affiliation query, plus a name-only query (family + given, rows=50). The wider net
    only finds candidates; the name + current-employment rule still decides every link.
  - The census finder is not used: no census.sqlite exists in this environment (pass 1 ran on the owner's
    desktop). Documented here so the omission is a fact, not an oversight.

Repairs found by QA on the first completed pass-2 run (2026-11-11, same day; finders/institution keys only,
the linking rule still unchanged):
  - Page finder also harvests an iD printed as bare text in a labelled ORCID field (an "orcid" mention in
    the 160 characters before the iD): Penn State's MatSE directory (and similar Drupal directories) prints
    the iD as plain text, never as an orcid.org link, so the URL-only harvest missed it entirely (Seong H.
    Kim's record was never even fetched). The iD is still only a candidate; the same rule judges it.
  - Institution name keys also include the legal/trade name with parenthetical qualifiers stripped
    ("Pennsylvania State University (University Park)" -> "pennsylvania state university"), but only when
    that stripped key is produced by exactly one institution in the dataset (collision-guarded), so two
    campuses that share a stripped name gain nothing. The parenthetical is this dataset's own annotation;
    ORCID records carry the plain name, so the name leg could never match.
  - Deliberately NOT repaired (an owner rule question, left for a future pass): a record that puts the full
    name in given-names with family-name empty (Brittany A. Rodriguez, ORNL; her exact name appears in the
    record's other-names) fails the name check although her iD is on her institution page and her current
    ORNL employment matches. Loosening name_matches for that shape is a rule change, not a finder repair.

    python3 tasks/people-orcid-2-2026-11-11/build.py --cache <dir> [--fetch] [--apply]
Without --fetch only cached responses are read. --apply appends to data/people_identifiers.csv.
"""
import argparse, csv, glob, json, re, sqlite3, sys, time, unicodedata
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from hashlib import sha1
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import atlas  # noqa: E402

API = "https://pub.orcid.org/v3.0/"
UA = "polymer-atlas-orcid-check/1.0 (+https://github.com/polymerindustrycluster/polymer-atlas)"
ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
SUFFIX = {"jr", "sr", "ii", "iii", "iv", "phd", "pe"}
UNITID_ALIAS = {"495767": "214777"}  # Penn State: IPEDS 2020+ consolidated id -> the id the census uses


def toks(s):
    s = unicodedata.normalize("NFKD", re.sub(r"\([^)]*\)", " ", s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return [t for t in re.split(r"[^a-z]+", s) if t]


def name_words(full):
    """Name words without initials and suffixes: 'Mark D. Foster Jr.' -> ['mark', 'foster']."""
    return [t for t in toks(full) if len(t) > 1 and t not in SUFFIX]


def name_matches(full, rec, family_only=False):
    """True when the ORCID record's given + family name is the people record's name (see module doc). An iD on the
    person's own page is itself the match (§4.21), so there only the family name is checked ('R. Joseph Kline')."""
    words = name_words(full)
    nm = ((rec.get("person") or {}).get("name")) or {}
    given = toks(((nm.get("given-names") or {}).get("value")))
    family = [t for t in toks(((nm.get("family-name") or {}).get("value"))) if t not in SUFFIX]
    if len(words) < 2 or not given or not family:
        return False
    if family_only:  # ... and one of the record's given names is among the ORCID given or other names (grok, #259)
        other = [t for o in ((rec.get("person") or {}).get("other-names") or {}).get("other-name") or []
                 for t in toks(o.get("content"))]
        return words[-len(family):] == family and bool(set(words[:-len(family)]) & set(given + other))
    if not (given[0] == words[0] and words[-len(family):] == family and len(family) < len(words)):
        return False
    # 'Wei A. Gao' is not 'Wei B. Gao': when both sides carry a middle name or initial, its first letter must agree
    allw = [t for t in toks(full) if t not in SUFFIX]
    mid, omid = allw[1:len(allw) - len(family)], given[1:]
    return not (mid and omid and mid[0][0] != omid[0][0])


def _selftest():
    r = lambda g, f: {"person": {"name": {"given-names": {"value": g}, "family-name": {"value": f}}}}
    assert name_matches("Chung-Fu Cheng", r("Chung-Fu", "Cheng"))
    assert name_matches("Roberto C. Andresen Eguiluz", r("Roberto", "Andresen Eguiluz"))
    assert name_matches("José Pérez Jr.", r("Jose", "Perez"))
    assert not name_matches("Wei A. Gao", r("Wei B.", "Gao"))
    assert not name_matches("Wei Gao", r("Wen", "Gao"))
    assert not name_matches("R. Joseph Kline", r("R. Joseph", "Kline"))
    assert name_matches("R. Joseph Kline", r("R. Joseph", "Kline"), family_only=True)
    assert not name_matches("Ann Smith", r("Ann", "Smithson"), family_only=True)
    assert not name_matches("Xi Chen", r("Chelsea", "Chen"), family_only=True)
    xi = r("Chelsea", "Chen"); xi["person"]["other-names"] = {"other-name": [{"content": "Xi Chelsea Chen"}]}
    assert name_matches("Xi Chen", xi, family_only=True)
    job = lambda **k: {"activities-summary": {"employments": {"affiliation-group": [{"summaries": [
        {"employment-summary": {"organization": {"name": "University of Akron"}, **k}}]}]}}}
    assert not current_jobs(job()) and current_jobs(job(**{"role-title": "Professor"}))


def current_jobs(rec):
    """Open employments (no end date) that say what the job is: a line with no role and no department cannot tell a
    professor from a same-name student at a big school (grok, #259), so it never links."""
    groups = (((rec.get("activities-summary") or {}).get("employments") or {}).get("affiliation-group")) or []
    jobs = [s["employment-summary"] for g in groups for s in g.get("summaries") or []]
    return [j.get("organization") or {} for j in jobs
            if not j.get("end-date") and ((j.get("role-title") or "").strip() or (j.get("department-name") or "").strip())]


def employment_basis(rec, inst):
    """'ror' / 'name' when a current employment is the institution, else ''."""
    found = ""
    for org in current_jobs(rec):
        d = org.get("disambiguated-organization") or {}
        if inst["ror"] and d.get("disambiguation-source") == "ROR" and \
                d.get("disambiguated-organization-identifier", "").rstrip("/").lower() == inst["ror"]:
            return "ror"
        if atlas.name_key(org.get("name") or "") in inst["keys"]:
            found = "name"
    return found


def get(cache, url, fetch):
    path = cache / (sha1(url.encode()).hexdigest() + ".json")
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    if not fetch:
        return None
    for attempt in range(4):
        try:
            with urlopen(Request(url, headers={"User-Agent": UA, "Accept": "application/json"}), timeout=45) as r:
                data = json.loads(r.read().decode("utf-8"))
            path.write_text(json.dumps(data), encoding="utf-8")  # cache per call, so a killed run resumes
            return data
        except Exception as e:  # 404 = deactivated/unknown iD: cache an empty record
            if getattr(e, "code", None) == 404:
                path.write_text("{}", encoding="utf-8")
                return {}
            time.sleep(2 * (attempt + 1))
    return None


PAGE_ID = re.compile(r"orcid\.org/(\d{4}-\d{4}-\d{4}-\\d{3}[\\dX])", re.I)
BARE_ID = re.compile(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]")


PAGE_FALLBACKS = []


def page_orcids(cache, url, fetch):
    """The distinct ORCID iDs linked on the person's own profile page (the record's public_profile_url).
    Raw read first; an empty or near-empty raw read (blocked / JS shell) falls back to the Jina Reader
    rendering of the same URL. A page that cannot be read yields no iD, never a negative fact."""
    path = cache / ("page-" + sha1(url.encode()).hexdigest() + ".txt")
    if not path.exists():
        if not fetch:
            return None
        text = ""
        try:
            with urlopen(Request(url, headers={"User-Agent": UA}), timeout=30) as r:
                text = r.read(3_000_000).decode("utf-8", "replace")
        except Exception:
            text = ""
        if len(text.strip()) < 400:
            try:
                with urlopen(Request("https://r.jina.ai/" + url, headers={"User-Agent": UA}), timeout=45) as r:
                    alt = r.read(3_000_000).decode("utf-8", "replace")
                if len(alt.strip()) > len(text.strip()):
                    text = alt
                    PAGE_FALLBACKS.append(url)
            except Exception:
                pass
        path.write_text(text, encoding="utf-8")
    text = path.read_text(encoding="utf-8")
    found = {m.upper() for m in PAGE_ID.findall(text)}
    for m in BARE_ID.finditer(text):  # an iD printed as bare text counts only in a labelled ORCID field
        if "orcid" in text[max(0, m.start() - 160):m.start()].lower():
            found.add(m.group(0).upper())
    return found


def institutions():
    eco = {r["org_id"]: r for r in csv.DictReader(open(ROOT / "data/ecosystem.csv", encoding="utf-8"))}
    orgs = {r["org_id"]: r for f in glob.glob(str(ROOT / "data/organizations_*.csv"))
            for r in csv.DictReader(open(f, encoding="utf-8"))}
    unitid = {r["org_id"]: r["registry_id"] for r in csv.DictReader(open(ROOT / "data/registry_links.csv",
              encoding="utf-8")) if r["registry"] == "IPEDS_UNITID"}
    out = {}
    for oid, r in {**orgs, **eco}.items():
        names = [r["legal_name"]] + [n for n in (r.get("trade_names") or "").split(";") if n.strip()]
        u = r.get("ipeds_unitid") or unitid.get(oid, "")
        out[oid] = {"name": r["legal_name"], "ror": (r.get("ror_id") or "").rstrip("/").lower(),
                    "keys": {atlas.name_key(n) for n in names}, "unitid": UNITID_ALIAS.get(u, u),
                    "_names": names}
    # Parenthetical qualifiers in this dataset's own names ("Pennsylvania State University (University
    # Park)") defeat the name leg: ORCID records carry the plain name. Add the stripped key only when a
    # single institution in the dataset produces it, so campuses sharing a stripped name gain nothing.
    stripped = {}
    for oid, inst in out.items():
        for n in inst["_names"]:
            bare = re.sub(r"\s*\([^)]*\)", "", n).strip()
            if bare and bare != n:
                k = atlas.name_key(bare)
                stripped[k] = oid if k not in stripped else None
    for k, oid in stripped.items():
        if oid is not None:
            out[oid]["keys"].add(k)
    for inst in out.values():
        del inst["_names"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True, type=Path)
    ap.add_argument("--census", type=Path)
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    _selftest()
    a.cache.mkdir(parents=True, exist_ok=True)
    id_owner = {r["identifier_id"]: r["person_id"] for r in
                csv.DictReader(open(ROOT / "data/people_identifiers.csv", encoding="utf-8"))}
    held_ids = set(id_owner)
    people = [p for p in csv.DictReader(open(ROOT / "data/people.csv", encoding="utf-8"))
              if p["person_id"] not in set(id_owner.values())]
    insts = institutions()

    census = {}
    if a.census:
        db = sqlite3.connect(a.census)
        for name, unitid, orcid in db.execute("select name, unitid, orcid from candidate where orcid != ''"):
            w = name_words(name)
            if len(w) >= 2 and unitid:
                census.setdefault((w[0], w[-1], str(unitid)), set()).add(orcid.strip().upper())

    def candidates(p):
        inst = insts.get(p["institution_org_id"])
        w = name_words(p["full_name"])
        page = page_orcids(a.cache, p["public_profile_url"], a.fetch) if p["public_profile_url"] else set()
        found = {o: "page" for o in page or ()}  # a roster page with several iDs is only a finder
        if not inst or len(w) < 2:
            return p, inst, found
        found.update({o: "census" for o in census.get((w[0], w[-1], inst["unitid"]), ()) if o not in found})
        aff = f'affiliation-org-name:"{inst["name"]}"'
        if inst["ror"]:
            aff = f'(ror-org-id:"https://ror.org/{inst["ror"].rsplit("/", 1)[-1]}" OR {aff})'
        q = f'family-name:"{w[-1]}" AND given-names:"{w[0]}" AND {aff}'
        res = get(a.cache, API + "search/?rows=20&q=" + quote(q), a.fetch)
        for hit in (res or {}).get("result") or []:
            found.setdefault(hit["orcid-identifier"]["path"], "search")
        q2 = f'family-name:"{w[-1]}" AND given-names:"{w[0]}"'
        res2 = get(a.cache, API + "search/?rows=50&q=" + quote(q2), a.fetch)
        for hit in (res2 or {}).get("result") or []:
            found.setdefault(hit["orcid-identifier"]["path"], "search_name")
        return p, inst, found

    with ThreadPoolExecutor(6) as ex:
        cands = list(ex.map(candidates, people))
    ids = sorted({o for _, _, f in cands for o in f if ORCID_RE.match(o)})
    with ThreadPoolExecutor(6) as ex:
        records = dict(zip(ids, ex.map(lambda o: get(a.cache, API + o + "/record", a.fetch), ids)))

    passing, journal, missing = {}, [], 0
    for p, inst, found in cands:
        ok, on_page = [], [o for o, s in found.items() if s == "page"]
        for o, src in found.items():
            rec = records.get(o)
            if rec is None:
                missing += 1
                continue
            if not rec:
                continue
            if len(on_page) == 1 and o == on_page[0]:
                if name_matches(p["full_name"], rec, family_only=True):
                    ok.append((o, src, "page"))
            elif name_matches(p["full_name"], rec) and inst and employment_basis(rec, inst):
                ok.append((o, src, employment_basis(rec, inst)))
        page_ok = [x for x in ok if x[2] == "page"]
        if page_ok and len(ok) > 1:  # the page's iD and a record match disagree: the precision check
            journal.append((p["person_id"], "", "held: page iD differs from record match"))
        elif page_ok or len(ok) == 1:
            passing.setdefault(ok[0][0], []).append((p["person_id"], ok[0][1], ok[0][2]))
        elif ok:
            journal.append((p["person_id"], "", "held: two or more iDs pass"))
        elif not inst:
            journal.append((p["person_id"], "", "no institution record"))
        else:
            journal.append((p["person_id"], "", "no candidate passed" if found else "no candidate found"))

    today = date.today().isoformat()
    rows, alarms = [], []
    for o, claims in sorted(passing.items()):
        if len(claims) > 1:  # one iD, two people records: presumptively the same person (§4.21)
            journal += [(pid, "", "held: dedupe alarm, iD shared with " + ",".join(c[0] for c in claims if c[0] != pid))
                        for pid, _, _ in claims]
            alarms += [(claims[i][0], claims[j][0], o, "one iD passes for two unlinked records")
                       for i in range(len(claims)) for j in range(i + 1, len(claims))]
        elif o in held_ids:
            journal.append((claims[0][0], "", "held: dedupe alarm, iD recorded for " + id_owner[o]))
            alarms.append((id_owner[o], claims[0][0], o, "iD recorded for one record passes for another"))
        else:
            pid, src, basis = claims[0]
            rows.append({"person_id": pid, "identifier_type": "ORCID", "identifier_id": o,
                         "match_basis": {"page": "orcid_on_institution_page", "ror": "orcid_record_employment_match_ror",
                                         "name": "orcid_record_employment_match_name"}[basis],
                         "as_of": today})
            journal.append((pid, src, "linked (" + basis + ")"))
    rows.sort(key=lambda r: r["person_id"])
    with open(HERE / "identifiers_append.csv", "w", newline="", encoding="utf-8") as fh:  # the packet, dry run or not
        w = csv.DictWriter(fh, fieldnames=["person_id", "identifier_type", "identifier_id", "match_basis", "as_of"],
                           lineterminator="\n")
        w.writeheader(); w.writerows(rows)

    with open(HERE / "journal.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["person_id", "candidate_source", "outcome"])
        w.writerows(sorted(journal))
    with open(HERE / "alarm_pairs.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["person_id_a", "person_id_b", "identifier_id", "alarm"])
        w.writerows(sorted(alarms))
    tally = {}
    for _, _, out in journal:
        k = out.split(",")[0] if out.startswith("held: dedupe") else out
        tally[k] = tally.get(k, 0) + 1
    print(f"{len(people)} people; {len(ids)} candidate iDs; {missing} candidate records not fetched; mint {len(rows)}")
    print(f"page fallback (Jina) used for {len(PAGE_FALLBACKS)} pages; dedupe alarms {len(alarms)}")
    for k, v in sorted(tally.items(), key=lambda kv: -kv[1]):
        print(f"  {v:5d}  {k}")
    if a.apply:
        assert missing == 0, "fetch every candidate record before applying"
        path = ROOT / "data/people_identifiers.csv"
        raw = path.read_bytes()
        eol = "\r\n" if b"\r\n" in raw else "\n"
        with open(path, "a", newline="", encoding="utf-8") as fh:
            if raw and not raw.endswith(eol.encode()):
                fh.write(eol)
            csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else [], lineterminator=eol).writerows(rows)
        print("appended", len(rows))


if __name__ == "__main__":
    main()
