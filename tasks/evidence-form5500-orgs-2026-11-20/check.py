#!/usr/bin/env python3
"""Task check for the Form 5500 lane, 2026-11-22 cut (exit 1 on any failure). From the repo root:

    python3 tasks/evidence-form5500-orgs-2026-11-20/check.py            # packet checks (+ applied checks once applied)
    python3 tasks/evidence-form5500-orgs-2026-11-20/check.py selftest   # plants five defects; each must be caught

- ledger and bundle carry only whitelisted business fields (no signer, phone or care-of data);
- the cut balances: kept + dropped + held = the 780 rows of packet_rows_2026-11-20.csv, each exactly once;
- every kept non-liveness row is on an organization with no evidence row of any other lane (data/evidence_organizations_*.csv,
  read now, excluding this lane's own rows); every dropped row is on an organization that has one (or is no longer active)
  and carries the reason; no liveness row was dropped;
- every kept row cites the ledger's ACK_ID; liveness rows carry the plan-year end as observed_date, an end on or after
  2024-11-20, active participants > 0 and no final filing; at most one row per (organization, claim);
- no ACK_ID is cited for two kept organizations; no street text, reason or detail carries a care-of/attention/e-mail marker;
- every kept address row's filing street equals, under atlas.street_key, the street of an Atlas HQ site (bundle);
- once applied: applied + withheld = kept; every applied row is SOUND in every family that reviewed (Codex always,
  Antigravity when present) and carries the waiver note iff Codex reviewed alone; rows are government_filing at supports_A
  (supports_U on tier U); IDs run contiguously from EVD-480100 inside EVD-480100..480999, once tree-wide, in the org's home
  shard, equal to applied.csv; no evidenced org is still listed in V-65 or V-68.
"""
import csv, glob, importlib.util, json, re, sys
from collections import Counter
from pathlib import Path

T = Path(__file__).resolve().parent
ROOT = T.parents[1]
START, END, LIVE_FROM, LANE = 480100, 480999, "2024-11-20", "claude-code-evd-form5500-lane"
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8", newline="")))
_s = importlib.util.spec_from_file_location("atlas_cli", ROOT / "scripts" / "atlas.py")
atlas = importlib.util.module_from_spec(_s); _s.loader.exec_module(atlas)
PERSONAL = re.compile(r"@|c/o|\battn\b|\bcare of\b|^\s*%", re.I)
LEDGER_COLS = ["org_id", "tier", "verdict", "legal_name", "hq_city", "hq_state", "atlas_eins", "filing_eins", "sponsor", "dba",
               "form", "plan_year_end", "active", "final", "loc_city", "loc_state", "mail_city", "mail_state", "ack_id"]


def evidenced_orgs():
    """Records with an evidence row of any other lane, read now from every data/evidence_*.csv (any record_table)."""
    return {r["record_id"].strip() for f in glob.glob(str(ROOT / "data" / "evidence_*.csv")) for r in rd(f) if r["created_by"] != LANE}


def cut_problems(ledger, original, kept, dropped, held, bundle, evidenced, bundle_text):
    fail = []
    if list(ledger[0]) != LEDGER_COLS:
        fail.append(f"ledger columns are not the whitelist: {list(ledger[0])}")
    if re.search(r"SIGNED|PHONE|CARE_OF|signer|phone", bundle_text):
        fail.append("review bundle carries a signer/phone/care-of field")
    led = {l["org_id"]: l for l in ledger}
    key = lambda r: (r["record_id"], r["claim_type"])
    n = len(kept) + len(dropped) + len(held)
    if n != len(original) or Counter(map(key, kept + dropped + held)) != Counter(map(key, original)):
        fail.append(f"kept {len(kept)} + dropped {len(dropped)} + held {len(held)} = {n}, not the {len(original)} original rows exactly once")
    if any(v > 1 for v in Counter(map(key, kept)).values()):
        fail.append("a kept (organization, claim) appears twice")
    for p in kept:
        if p["claim_type"] != "liveness" and p["record_id"] in evidenced:
            fail.append(f"{p['record_id']} {p['claim_type']} is kept on an organization that has other evidence")
    for p in dropped:
        ok = p["reason"] == "organization evidenced since 2026-11-20" and p["record_id"] in evidenced or p["reason"] == "organization no longer active"
        if p["claim_type"] == "liveness" or not ok:
            fail.append(f"{p['record_id']} {p['claim_type']} is dropped without cause or reason")
    if sum(1 for r in original if r["claim_type"] == "liveness") != sum(1 for r in kept + held if r["claim_type"] == "liveness"):
        fail.append("a liveness row was dropped")
    if any(not h["reason"] for h in held):
        fail.append("a held row carries no settling fact")
    b = {x["record_id"]: x for x in bundle}
    acks = {}
    for p in kept:
        ack = led[p["record_id"]]["ack_id"]
        if acks.setdefault(ack, p["record_id"]) != p["record_id"]:
            fail.append(f"ACK_ID {ack} is cited for both {acks[ack]} and {p['record_id']}: one filing cannot witness two organizations")
    # no person in a published street line (AGENTS §6): the bundle's street fields, every held/dropped reason, every kept text
    texts = [h["reason"] for h in held + dropped] + [p["claim_detail"] + " " + p["notes"] for p in kept]
    for x in bundle:
        texts += [x["filing"].get("location_street", ""), x["filing"].get("mailing_street", ""), x.get("street_check", {}).get("fact", "")]
        for s in (x["filing"].get("location_street", ""), x["filing"].get("mailing_street", "")):
            if s and not re.search(r"\d", s):
                fail.append(f"{x['record_id']} bundle street line has no digit: not a street")
    for tx in texts:
        if PERSONAL.search(tx):
            fail.append(f"a published text carries a care-of/attention/e-mail marker: {tx[:60]!r}")
    for p in kept:
        l = led[p["record_id"]]
        if f"ACK_ID {l['ack_id']} " not in p["source_ref"] or re.match(r"https?://", p["source_ref"]) or "@" in p["claim_detail"] + p["notes"]:
            fail.append(f"{p['record_id']} {p['claim_type']} does not cite the ledger ACK_ID by name, or carries a URL or '@'")
        if p["claim_type"] == "liveness" and not (p["observed_date"] == l["plan_year_end"] >= LIVE_FROM and int(l["active"] or 0) > 0 and l["final"] != "1"):
            fail.append(f"{p['record_id']} liveness row breaks ruling 8 (end {l['plan_year_end']}, active {l['active']}, final {l['final']})")
        if p["claim_type"] == "address":
            x = b.get(p["record_id"], {})
            f, sites = x.get("filing", {}), x.get("atlas_hq_site_streets", {})
            street = f.get("location_street") if l["loc_city"] else f.get("mailing_street")
            if not street or not any(atlas.street_key(s) == atlas.street_key(street) for s in sites.values()):
                fail.append(f"{p['record_id']} address row: the filing street '{street}' does not equal an Atlas HQ site street {sites}")
    return fail


def selftest():
    """Plant each defect on a copy of the real cut; every one must be caught, the unplanted cut must pass."""
    ledger, orig, kept, dropped, held = (rd(T / n) for n in ("ledger.csv", "packet_rows_2026-11-20.csv", "packet_rows.csv", "dropped_rows.csv", "held_rows.csv"))
    bundle = json.loads((T / "review_bundle.json").read_text(encoding="utf-8"))
    ev = evidenced_orgs()
    run = lambda **k: cut_problems(ledger, orig, **{**dict(kept=kept, dropped=dropped, held=held, bundle=bundle, evidenced=ev, bundle_text=""), **k})
    assert not run(), run()
    dropped_row = next(r for r in dropped if r["claim_type"] == "existence")
    planted = dict(dropped_row)  # an already-evidenced organization's existence row, put back among the kept rows
    assert any("has other evidence" in f for f in run(kept=kept + [planted], dropped=[r for r in dropped if r is not dropped_row])), "planted evidenced-org row not caught"
    assert any("not the" in f for f in run(kept=kept[1:])), "a lost row is not caught"
    addr = next(i for i, r in enumerate(kept) if r["claim_type"] == "address")
    bad = json.loads(json.dumps(bundle))
    next(x for x in bad if x["record_id"] == kept[addr]["record_id"])["atlas_hq_site_streets"] = {"SITE-X": "1 Other Road"}
    assert any("does not equal an Atlas HQ site street" in f for f in run(bundle=bad)), "a different-street address row is not caught"
    leak = json.loads(json.dumps(bundle)); leak[0]["filing"]["mailing_street"] = "C/O JANE DOE 1 MAIN ST"
    assert any("care-of" in f for f in run(bundle=leak)), "a person in a street line is not caught"
    o1, o2 = sorted({p["record_id"] for p in kept})[:2]
    ledger2 = [dict(l, ack_id=next(x for x in ledger if x["org_id"] == o1)["ack_id"]) if l["org_id"] == o2 else l for l in ledger]
    assert any("cannot witness two" in f for f in cut_problems(ledger2, orig, kept, dropped, held, bundle, ev, "")), "a shared ACK_ID is not caught"
    print("check selftest ok: planted evidenced-org row, lost row, different-street address row, person in a street line and shared ACK_ID are each caught")


if len(sys.argv) > 1 and sys.argv[1] == "selftest":
    selftest(); sys.exit(0)
ledger, original, packet = rd(T / "ledger.csv"), rd(T / "packet_rows_2026-11-20.csv"), rd(T / "packet_rows.csv")
dropped, held = rd(T / "dropped_rows.csv"), rd(T / "held_rows.csv")
bundle_text = (T / "review_bundle.json").read_text(encoding="utf-8")
led = {l["org_id"]: l for l in ledger}
wit = {p["record_id"] for p in packet}
fail = cut_problems(ledger, original, packet, dropped, held, json.loads(bundle_text), evidenced_orgs(), bundle_text)

if (T / "applied.csv").exists():
    applied, withheld = rd(T / "applied.csv"), rd(T / "withheld.csv")
    fams = {}
    for name in ("codex", "agy"):
        for p in sorted(T.glob(f"review_{name}_*.json")):
            t = p.read_text(encoding="utf-8")
            fams.setdefault(name, {}).update({(v["record_id"], v["claim_type"]): v["verdict"] for v in json.loads(t[t.index("{"):t.rindex("}") + 1])["verdicts"]})
    if "codex" not in fams:
        fail.append("applied without Codex verdicts")
    if len(applied) + len(withheld) != len(packet):
        fail.append(f"applied {len(applied)} + withheld {len(withheld)} != packet {len(packet)}")
    sound = lambda k: all(v.get(k) == "SOUND" for v in fams.values())
    bad = {p["record_id"] for p in packet if p["claim_type"] == "existence" and not sound((p["record_id"], "existence"))}
    for x in applied:
        if not sound((x["record_id"], x["claim_type"])) or x["record_id"] in bad:
            fail.append(f"{x['evidence_id']} applied without SOUND from every reviewing family on an accepted org")
        if ("owner's waiver of 2026-11-20" in x["notes"]) == ("agy" in fams):
            fail.append(f"{x['evidence_id']} waiver note does not match the families that reviewed")
        eff = "supports_U" if led[x["record_id"]]["tier"] == "U" else "supports_A"
        if x["source_class"] != "government_filing" or x["tier_effect"] != eff:
            fail.append(f"{x['evidence_id']} is {x['source_class']}/{x['tier_effect']}, expected government_filing/{eff}")
    ids = [x["evidence_id"] for x in applied]
    if ids != [f"EVD-{n:06d}" for n in range(START, START + len(ids))] or START + len(ids) - 1 > END:
        fail.append(f"applied IDs are not EVD-{START:06d}.. contiguous inside the lane's EVD-{START:06d}..{END:06d}")
    tree, rows = Counter(), {}
    for f in glob.glob(str(ROOT / "data" / "evidence_*.csv")):
        for r in rd(f):
            tree[r["evidence_id"]] += 1
            rows[r["evidence_id"]] = (Path(f).name, r)
    for x in applied:
        if tree[x["evidence_id"]] != 1:
            fail.append(f"{x['evidence_id']} appears {tree[x['evidence_id']]} times tree-wide"); continue
        fname, r = rows[x["evidence_id"]]
        if fname != f"evidence_organizations_{x['_shard']}.csv" or any(r[k] != x[k] for k in r):
            fail.append(f"{x['evidence_id']} is not in its home shard or differs from applied.csv")
    base = json.loads((ROOT / "scripts" / "validate_debt_baseline.json").read_text(encoding="utf-8"))["rules"]
    done = {x["record_id"] for x in applied}
    left = sorted(done & set(base["V-65"])) + sorted(k for k in base["V-68"] if k.startswith("organizations:") and k.split(":")[1] in done)
    if left:
        fail.append(f"evidenced orgs still baselined: {', '.join(left[:10])}")
    summary = f"OK: {len(applied)} applied rows on {len(done)} orgs ({'+'.join(sorted(fams))}), {len(withheld)} withheld; "
else:
    summary = "OK (not yet reviewed or applied): "
print("\n".join(fail) or summary + f"kept {len(packet)} rows on {len(wit)} orgs ({dict(Counter(p['claim_type'] for p in packet))}), "
      f"dropped {len(dropped)}, held {len(held)}, original {len(original)}")
sys.exit(1 if fail else 0)
