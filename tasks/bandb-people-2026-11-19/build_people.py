#!/usr/bin/env python3
"""Band-B census leads -> people records (packet integration; run from the Atlas worktree root).

A lane VERIFIED row is admitted only when ALL hold:
  - raw check (rawcheck.csv): Gate A and Gate B quotes found word for word on a fresh re-fetch, and the person's
    surname within 40 words of the Gate A quote;
  - both gate URLs are on the institution's own registered domain (V-22: people existence/scope are own_site);
  - role is a SCHEMA 4.9 controlled value; no '@' in any URL and no personal-account identifier URL (V-62);
  - the name is not already held in people.csv (any institution: a same-name hold is a possible mover, held);
  - not held by the two-family review (review_holds.csv: person rows either family did not judge SOUND).
Each admitted person gets existence, scope and parent evidence rows (own_site, supports_A) and tier A.
    python3 <this file> <corpus dir> [--apply]
"""
import csv, io, re, sys, unicodedata
from pathlib import Path
from urllib.parse import urlparse

C = Path(sys.argv[1]); ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))
from people_url import has_account_identifier  # noqa: E402  (the same parser validate.py V-62 uses)
DATE, BY = "2026-11-19", "claude-code bandb-people-2026-11-19"
PID0, EVD0 = 2403, 399100  # above main and every open PR on 2026-11-19
ROLES = {"professor", "associate_professor", "assistant_professor", "research_professor", "center_director_professor",
         "senior_lecturer"}


def read(p):
    raw = p.read_bytes(); eol = "\r\n" if b"\r\n" in raw[:4096] else "\n"
    r = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
    return r.fieldnames, list(r), eol


def write(p, head, rows, eol):
    buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=head, lineterminator=eol); w.writeheader(); w.writerows(rows)
    p.write_bytes(buf.getvalue().encode("utf-8"))


def toks(n):
    s = "".join(c for c in unicodedata.normalize("NFKD", (n or "").lower()) if not unicodedata.combining(c))
    return [t for t in re.split(r"[^a-z]+", s) if len(t) > 1 and t not in ("jr", "sr", "ii", "iii", "phd", "dr", "prof")]


key = lambda n: (toks(n)[0], toks(n)[-1]) if len(toks(n)) >= 2 else None
dom = lambda u: ".".join(urlparse(u if "//" in u else "https://" + u).netloc.lower().split(":")[0].split(".")[-2:])


def main():
    ver = list(csv.DictReader(open(C / "verified.csv", encoding="utf-8")))
    rc = {r["lead_id"]: r for r in csv.DictReader(open(C / "rawcheck.csv", encoding="utf-8"))}
    rh = {r["lead_id"]: r["reason"] for r in csv.DictReader(open(C / "review_holds.csv", encoding="utf-8"))} \
        if (C / "review_holds.csv").exists() else {}
    ph, people, pe = read(ROOT / "data/people.csv")
    eh, ev, ee = read(ROOT / "data/evidence_people.csv")
    import glob
    insts = {r["org_id"]: r for r in csv.DictReader(open(ROOT / "data/ecosystem.csv", encoding="utf-8"))}
    insts.update({r["org_id"]: r for f in glob.glob(str(ROOT / "data/organizations_*.csv")) if not f.endswith("_all.csv")
                  for r in csv.DictReader(open(f, encoding="utf-8"))})
    # An institution's own domains: its website's, plus any registered domain already used by >= 2 of its held people's
    # profile URLs (a website cell can be blank; universities run more than one domain, e.g. washington.edu and uw.edu).
    import collections
    by_inst = collections.defaultdict(collections.Counter)
    for p in people:
        if p["public_profile_url"]:
            by_inst[p["institution_org_id"]][dom(p["public_profile_url"])] += 1
    def own_domains(oid):
        d = {dom(insts.get(oid, {}).get("website", ""))} - {""}
        return d | {x for x, n in by_inst[oid].items() if n >= 2}
    held = {}
    for p in people:
        if key(p["full_name"]): held.setdefault(key(p["full_name"]), p["person_id"])
    pids = {p["person_id"] for p in people}; eids = {e["evidence_id"] for e in ev}
    admit, outcome, seen = [], [], set()
    for r in ver:
        lid, k = r["lead_id"], key(r["full_name"])
        x = rc.get(lid, {})
        idoms = own_domains(r["institution_org_id"])
        why = None
        if lid in rh: why = "review hold: " + rh[lid]
        elif x.get("gate_a") != "yes" or x.get("gate_b") != "yes": why = f"raw check gate_a={x.get('gate_a')} gate_b={x.get('gate_b')}"
        elif x.get("gate_a_surname") != "yes": why = "raw check: surname not within 40 words of the Gate A quote"
        elif r["role"] not in ROLES: why = f"role {r['role']!r} not a SCHEMA 4.9 value"
        elif "@" in r["public_profile_url"] + r["gate_a_url"] + r["gate_b_url"]: why = "a URL contains '@'"
        elif has_account_identifier(";".join((r["public_profile_url"], r["gate_a_url"], r["gate_b_url"]))):
            why = "a URL carries a personal-account identifier (?u=, ?unid=, /~; V-62 owner rulings 2026-11-18)"
        elif not idoms or dom(r["gate_a_url"]) not in idoms or dom(r["gate_b_url"]) not in idoms:
            why = f"gate URL off the institution's own domains ({', '.join(sorted(idoms)) or 'none on record'})"
        elif not k: why = "name not parseable"
        elif k in held: why = f"same name already held as {held[k]} (possible mover or duplicate)"
        elif k in seen: why = "duplicate within this batch"
        outcome.append({"lead_id": lid, "full_name": r["full_name"], "outcome": "admitted" if why is None else "held", "reason": why or ""})
        if why is None:
            seen.add(k); admit.append(r)
    new_p, new_e = [], []
    for i, r in enumerate(admit):
        pid = f"PERSON-{PID0 + i:06d}"; assert pid not in pids
        src = [r["public_profile_url"]] + [u for u in (r["gate_a_url"], r["gate_b_url"]) if u != r["public_profile_url"]]
        row = {c: "" for c in ph}
        row.update(person_id=pid, full_name=r["full_name"], institution_org_id=r["institution_org_id"], role=r["role"],
                   role_as_published=r["role_as_published"], public_profile_url=r["public_profile_url"],
                   sources=";".join(dict.fromkeys(src)), verification_tier="A", last_verified=DATE)
        new_p.append(row)
        for j, (claim, url, detail, quote) in enumerate((
                ("existence", r["gate_a_url"], f"name {r['full_name']}; role {r['role']}; title {r['role_as_published']}", r["gate_a_quote"]),
                ("scope", r["gate_b_url"], "Current own-institution polymer research", r["gate_b_quote"]),
                ("parent", r["gate_a_url"], f"institution_org_id {r['institution_org_id']}; public_profile_url {r['public_profile_url']}", r["gate_a_quote"]))):
            eid = f"EVD-{EVD0 + 3 * i + j:06d}"; assert eid not in eids
            new_e.append(dict(evidence_id=eid, record_table="people", record_id=pid, claim_type=claim, claim_detail=detail,
                              source_class="own_site", source_ref=url, observed_date=DATE, tier_effect="supports_A",
                              created_by=BY, notes="Raw words in order: " + " ".join(quote.split())))
    out = ROOT / "tasks/bandb-people-2026-11-19"; out.mkdir(parents=True, exist_ok=True)
    with open(out / "outcomes.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["lead_id", "full_name", "outcome", "reason"], lineterminator="\n"); w.writeheader(); w.writerows(outcome)
    print(f"verified {len(ver)}; admitted {len(admit)}; held {len(ver) - len(admit)}")
    print(collections.Counter(o["reason"].split(":")[0].split(" (")[0] for o in outcome if o["outcome"] == "held"))
    if "--apply" in sys.argv and new_p:
        write(ROOT / "data/people.csv", ph, people + new_p, pe)
        write(ROOT / "data/evidence_people.csv", eh, ev + new_e, ee)
        print("written")


if __name__ == "__main__":
    main()
