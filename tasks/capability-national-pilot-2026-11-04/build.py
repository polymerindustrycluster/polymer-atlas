#!/usr/bin/env python3
"""Capability national pilot (2026-11-04): processes/materials terms stated on 100 organizations' own sites.
Reused from tasks/capability-pass-2026-11-04/build_fixes.py (itself from tasks/record-fixes-2026-11-03/). Changes: the
EVD floor sits above the open PRs #122/#123, and a term counts only when its quote is on the record's own website
domain (a sister or parent domain is held).

    python3 tasks/capability-national-pilot-2026-11-04/build.py --data-dir data [--apply --i-am-the-integrator]
        -> evidence_append.csv, edits.csv (apply edits with scripts/apply_p1_crm_scrub.py --packet-dir), holds.csv

Admits a lane row only when the integrator's raw re-fetch found its quote verbatim (rawcheck.csv). An address row
must also name the record's own HQ city or one of its held site cities (a quote for a different HQ is a finding,
held, not evidence for the record's address). Processes/materials must be SCHEMA §3.1/§3.2 terms (docs/schema/
vocab.json); each admitted term also gets a scope evidence row carrying its quote. Tier: when existence, address and
scope all carry support, the tier is the weakest supported strength among the must-have claims present (code
included if it has rows); it is only ever raised here. Duplicate verdicts are recorded, never merged.
EVD ids start above EVD-128000: open PRs #122 and #123 use up to EVD-126447 at build time.
"""
import argparse, csv, glob, hashlib, json, re, sys, unicodedata
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "census-gap-people-2026-11-03"))
from build_integration import append_rows, read  # noqa: E402

TODAY, BY, EVD_FLOOR = "2026-11-04", "claude-code capability-national-pilot-2026-11-04", 128000  # above open PRs #122/#123
# Cross-family refute (grok, deep, 60-term random sample, 2026-11-05): the quote mentions the process or material
# without saying the company does it. Held.
COUNCIL_HELD = {
    ("ORG-003903", "extrusion_unspecified"): "council: the company uses extrusions as inputs; it does not extrude",
    ("ORG-003630", "rotational_molding"): "council: the floats use a rotomolded shell; the quote does not say the company molds it",
    ("ORG-003495", "extrusion_unspecified"): "council: the material is being developed for others to extrude",
    ("ORG-001885", "thermoforming_unspecified"): "council: the quote compares the product against thermoformed blisters",
    ("ORG-000774", "extrusion_sheet"): "council: the quote is a fragment that does not say the company extrudes sheet",
    ("ORG-003688", "nylon_pa"): "council: the quote states a nylon property, not that the company makes nylon parts",
    ("ORG-002453", "rubber_molding_unspecified"): "council: 'custom rubber molded parts' may be a sourced product line",
    ("ORG-004283", "rubber_calendering"): "council: 'four rolls for milling' describes milling, not calendering",
}
CEIL = {"own_site": "supports_A", "government_filing": "supports_A", "press": "supports_B"}
RANK = {"supports_C": 1, "supports_B": 2, "supports_A": 3}
TIER = {3: "A", 2: "B", 1: "C"}
MUST = ("existence", "address", "scope")
W = lambda s: re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower())


def dom(u):  # registrable host, good enough for .com/.net/.org and similar
    h = re.sub(r"^(https?://)?", "", (u or "").strip().lower()).split("/")[0]
    return ".".join(h.split(".")[-2:])


def has(text, phrase):
    t, p = W(text), W(phrase)
    return bool(p) and any(t[i:i + len(p)] == p for i in range(len(t) - len(p) + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    a = ap.parse_args()
    data = Path(a.data_dir).resolve()
    vocab = json.load(open(HERE.parents[1] / "docs/schema/vocab.json", encoding="utf-8"))["vocabularies"]
    VOC = {"processes": set(vocab["PROCESSES"]["values"]), "materials": set(vocab["MATERIALS"]["values"])}
    raw = {(r["lane"], r["kind"], int(r["idx"])): r["raw"] for r in read(HERE / "rawcheck.csv")}
    orgs, shard = {}, {}
    for f in sorted(data.glob("organizations_*.csv")):
        for r in read(f):
            orgs[r["org_id"]], shard[r["org_id"]] = r, f.stem.split("_", 1)[1]
    cities = defaultdict(set)
    for f in data.glob("sites_*.csv"):
        for s in read(f):
            cities[s["org_id"]].add(s["city"])
    ev = [r for f in sorted(data.glob("evidence*.csv")) for r in read(f)]
    evd = max([EVD_FLOOR] + [int(e["evidence_id"][4:]) for e in ev if re.fullmatch(r"EVD-\d+", e["evidence_id"])]) + 1
    new_ev, holds, terms = [], [], defaultdict(lambda: defaultdict(list))

    def mint(oid, claim, sc, url, quote, detail, why):
        nonlocal evd
        new_ev.append({"evidence_id": f"EVD-{evd:06d}", "record_table": "organizations", "record_id": oid, "claim_type": claim,
                       "claim_detail": f"{detail.strip()} \"{quote.strip()}\"", "source_class": sc, "source_ref": url.strip(),
                       "observed_date": TODAY, "tier_effect": CEIL[sc], "created_by": BY, "notes": why})
        evd += 1

    seen = set()
    for lane in sorted(HERE.glob("lanes/F*")):
        for i, r in enumerate(read(lane / "evidence.csv") if (lane / "evidence.csv").exists() else []):
            oid, claim, sc = r["org_id"], r["claim_type"].strip(), r["source_class"].strip()
            why = []
            if raw.get((lane.name, "evidence", i)) != "yes": why.append(f"raw check {raw.get((lane.name, 'evidence', i))}")
            if claim not in MUST: why.append(f"claim {claim} not minted here (no NAICS found; SIC is not a NAICS claim)")
            if sc not in CEIL: why.append(f"source_class {sc}")
            o = orgs.get(oid)
            if o and claim == "address" and not any(has(r["quote"], c) for c in {o["hq_city"]} | cities[oid] if c):
                why.append(f"address quote does not name the record's city ({o['hq_city']}): finding, not evidence")
            if (oid, claim, r["source_url"]) in seen: why.append("duplicate row")
            if why:
                holds.append({"org_id": oid, "kind": f"evidence:{claim}", "detail": r["quote"][:120], "reason": "; ".join(why)}); continue
            seen.add((oid, claim, r["source_url"]))
            mint(oid, claim, sc, r["source_url"], r["quote"], r.get("claim_detail") or claim,
                 "record-health fix 2026-11-04 (lane quote re-fetched raw and found verbatim)")
        for i, r in enumerate(read(lane / "fields.csv") if (lane / "fields.csv").exists() else []):
            fld, val = r["field"].strip(), r["value"].strip()
            why = []
            if raw.get((lane.name, "fields", i)) != "yes": why.append(f"raw check {raw.get((lane.name, 'fields', i))}")
            if fld not in VOC: why.append(f"field {fld} not applied here")
            elif val not in VOC[fld]: why.append(f"'{val}' not a SCHEMA term")
            o = orgs.get(r["org_id"])
            if not o: why.append("org not found")
            elif dom(r["source_url"]) != dom(o["website"]): why.append(f"page {dom(r['source_url'])} is not the record's own domain {dom(o['website'])}")
            if len(W(r["quote"])) <= 3:
                why.append("quote of three words or fewer is too thin to evidence a term")  # e.g. a bare menu item "Foam"
            if (r["org_id"], val) in COUNCIL_HELD:
                why.append(COUNCIL_HELD[(r["org_id"], val)])
            if val == "pvc" and not re.search(r"\bpvc\b|polyvinyl chloride", r["quote"], re.I):
                why.append("pvc inferred from 'vinyl'; the quote does not name PVC")  # a lane mapped vinyl windows to pvc
            if why:
                holds.append({"org_id": r["org_id"], "kind": f"field:{fld}", "detail": val, "reason": "; ".join(why)}); continue
            terms[r["org_id"]][fld].append((val, r))
    edits = []

    def edit(oid, col, new, cls, why):
        old = orgs[oid][col]
        if old != new:
            edits.append({"file": f"organizations_{shard[oid]}.csv", "row_id": oid, "column": col,
                          "old_sha256": hashlib.sha256(old.encode()).hexdigest(), "new_value": new, "edit_class": cls, "rationale": why})

    for oid, f in terms.items():
        for fld, items in f.items():
            cur = [t.strip() for t in orgs[oid][fld].split(";") if t.strip()]
            add = [v for v, _ in items if v not in cur]
            if add:
                edit(oid, fld, ";".join(dict.fromkeys(cur + add)), "CAPABILITY_FILL", "terms stated on the company's own page (scope evidence rows carry the quotes)")
            for v, r in items:
                mint(oid, "scope", "own_site", r["source_url"], r["quote"], f"{fld} term {v}:", "capability term, national pilot 2026-11-04 (lane quote re-fetched raw and found verbatim)")
    # tier restatement over old + new rows (only raised)
    best = defaultdict(dict)
    for e in ev + new_ev:
        if e["record_table"] == "organizations" and e["tier_effect"] in RANK and e["claim_type"] in MUST + ("code",):
            best[e["record_id"]][e["claim_type"]] = max(best[e["record_id"]].get(e["claim_type"], 0), RANK[e["tier_effect"]])
    touched = {e["record_id"] for e in new_ev}
    tiers = Counter()
    for oid in touched:
        b = best[oid]
        if all(c in b for c in MUST):
            t = TIER[min(b.values())]
            cur = orgs[oid]["verification_tier"]
            if "ABCU".index(t) < "ABCU".index(cur):
                edit(oid, "verification_tier", t, "TIER_RESTATE", f"SCHEMA 4.1/4.13: weakest evidenced must-have claim is {t}")
                tiers[f"{cur}->{t}"] += 1
        edit(oid, "last_verified", TODAY, "REVERIFIED", "capability national pilot 2026-11-04")
    with open(HERE / "evidence_append.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ev[0].keys()), extrasaction="ignore", lineterminator="\n"); w.writeheader(); w.writerows(new_ev)
    with open(HERE / "edits.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["file", "row_id", "column", "old_sha256", "new_value", "edit_class", "rationale"], lineterminator="\n")
        w.writeheader(); w.writerows(edits)
    with open(HERE / "holds.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["org_id", "kind", "detail", "reason"], lineterminator="\n"); w.writeheader(); w.writerows(holds)
    print(f"evidence {len(new_ev)} ({Counter(e['claim_type'] for e in new_ev)}); edits {len(edits)} ({Counter(e['edit_class'] for e in edits)}); "
          f"tier moves {dict(tiers)}; holds {len(holds)}; orgs touched {len(touched)}")
    if a.apply:
        if data == (HERE.parents[1] / "data").resolve() and not a.i_am_the_integrator:
            sys.exit("appending to the real data/ is integrator work; pass --i-am-the-integrator")
        by = defaultdict(list)
        for e in new_ev:
            by[f"evidence_organizations_{shard[e['record_id']]}.csv"].append(e)
        for name, rows in by.items():
            append_rows(data / name, rows)
        print("evidence appended; now apply edits.csv with scripts/apply_p1_crm_scrub.py")


if __name__ == "__main__":
    main()
