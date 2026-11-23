#!/usr/bin/env python3
"""Named check for the notes-history canary (run from anywhere: python3 tasks/notes-history-2026-11-22/check.py).

 1. LOSSLESS   canary: concatenating the history pieces by seq (person-held pieces from the row) reproduces the original note byte for byte,
               and the multiset of segments (history) equals the multiset of segments of the original (order-insensitive); every kept/restated piece is on the row.
 2. RESIDUE    no pipeline word remains on a canary row. The word list here is INDEPENDENT of notes_split.WORDS (so the classifier cannot grade itself),
               plus shape tests (ALL-CAPS tokens, underscores, id shapes). Two planted misses must be caught.
 3. DEPENDENCY corpus-wide, original vs after-row, with each reader's own regex: street keys, FRS ids, FEI ids, tombstone, WARN, parcel marker,
               Settling fact rule, other-org name mentions. Each class must inspect > 0 positives or the check fails. Two bounds are run:
               'script-only' (every unresolved READER piece stays on the row) and 'worst case' (every unresolved READER piece moves, code-pinned ones excepted).
 4. TREE       data/ is unchanged against origin/main (this lane touches nothing under data/).
"""
import csv, json, re, subprocess, sys, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from load import load                       # noqa: E402
from corpus import run                      # noqa: E402
import notes_split as NS                    # noqa: E402
import atlas                                # noqa: E402
FAIL = []
def fail(msg): FAIL.append(msg); print("FAIL", msg)
def ok(msg): print("ok  ", msg)

# ---------------------------------------------------------------- 2. independent residue detector
PINNED = ["Settling fact:", "parcel candidate queue", "tombstoned as duplicate of SITE-", "WARN"]   # code reads these on the row (DESIGN §3); owner may reword
ALLOWED_CAPS = {"ISO", "IATF", "OSHA", "FRS", "ITA", "ECHO", "TRI", "EPA", "FDA", "ITAR", "NAICS", "SIC", "SDS", "PPP", "EIN", "CIK", "FEI", "HQ", "USA", "PVC", "PET", "HDPE", "LDPE",
                "ABS", "TPO", "PE", "PP", "EPS", "FRP", "ASME", "RTP", "SEC", "LLC", "INC", "US", "OH", "PA", "IN", "NC", "TX", "CA", "NY", "NJ", "GA", "MI", "IL", "WI", "AL", "SC", "VA", "MD",
                "AZ", "CT", "RI", "NH", "KS", "IA", "CO", "NV", "MA", "AR", "MS", "MN", "MO", "KY", "TN", "LA", "ME", "OR", "WA", "FL", "EPAP", "ULTEPAP", "FGIA", "AAMA", "DEQ", "DEP", "NPDES",
                "MS", "PTI", "STCC", "EDGAR", "TIER", "RY", "PY", "CY", "NAICS", "BBB", "GBP", "DNR", "ESD", "LEI", "GLEIF", "RV", "II", "III", "IV", "LP", "LLP", "INOAC", "EPC", "AHF", "BWAY",
                "RIM", "RTM", "CAGE", "PPG", "DME", "NSF", "SPI", "UL", "VRC", "JM", "ITW", "IMM", "MCA", "MCPP", "DOE", "NREL", "SBIR", "STTR", "ECO"}
RES = [("agent", r"(?i)\b(?:grok|spaghetti|muse|codex|gemini|antigravity|claude|subagent|harness)\b"), ("role", r"(?i)\b(?:integrators?|coordinators?|orchestrators?)\b"),
       ("pass", r"(?i)\bpass(?:es)?[- ]?\d+|\bintegration pass\b"), ("wave", r"(?i)\bwaves?\b"), ("verdict", r"(?i)\bverdicts?\b"), ("packet", r"(?i)\bpackets?\b"),
       ("lane", r"(?i)\blanes?\b"), ("burndown", r"(?i)\bburn-?down\b"), ("staging", r"(?i)\bstaging\b|working/|tasks/|raw/"), ("file", r"\b\w+\.(?:csv|md|json)\b"),
       ("section", r"§|\bAGENTS\b|\bSCHEMA\b"), ("tier", r"\bTier [ABCU]\b|\btier [abcu]\b"), ("ring", r"(?i)\bring \d\b"), ("marker", r"BAND-SOURCE|CERT-SITE|CAPABILITY-QUEUE"),
       ("id-shape", r"\bW\d{1,2}-|\bNEW(?:SITE)?:|\bPKT-|\bLF-[A-Z]{2}|\bQMS-|\bP2-[A-Z]{2}|\bL\d-\d|\bR-\d+\b"), ("underscore", r"\b[A-Za-z]+_[A-Za-z0-9_]+\b"),
       ("dedupe", r"(?i)\bdedupe\b|\btombstone[ds]?\b"), ("grain", r"(?i)\bgrain\b|\bdesigned\b|\bunheld\b")]
CAPS = re.compile(r"\b(?!(?:SITE|ORG)-\d{6}\b)[A-Z]{4,}(?:-[A-Z]+)*\b")
def residue(text):
    t = text
    for ph in PINNED: t = t.replace(ph, " ")
    hits = [(n, m.group(0)) for n, rx in RES for m in re.finditer(rx, t)]
    hits += [("ALL-CAPS", m.group(0)) for m in CAPS.finditer(t) if m.group(0).split("-")[0] not in ALLOWED_CAPS and m.group(0) not in ALLOWED_CAPS]
    return hits

def group_after(parts, mode):
    out = []
    for p in parts:
        d = p["disp"]
        if d == "READER": d = "KEEP" if mode == "script-only" or p["kind"].startswith("code-pinned") else "MOVE"
        if d in ("KEEP", "PERSON"): out.append(NS.tidy(p["text"]))
        elif d == "RESTATE": out.append(p["restated"])
    return " ".join(out)

def main():
    orgs, sites = run()
    by = {r["_id"]: r for r in orgs + sites}
    # ---------------------------------------------------------------- 1. LOSSLESS (canary)
    cv = list(csv.DictReader(open(HERE / "canary.csv", encoding="utf-8")))
    hist = collections.defaultdict(list)
    for h in csv.DictReader(open(HERE / "canary_history.csv", encoding="utf-8")): hist[h["record_id"]].append(h)
    assert len(cv) == 25, len(cv)
    for c in cv:
        rid = c["record_id"]; orig = by[rid]["notes"]; hs = sorted(hist[rid], key=lambda h: int(h["seq"]))
        assert [int(h["seq"]) for h in hs] == list(range(len(hs))), rid
        recon = "".join(h["text"] if h["on_row"] != "person-held" else "<<from row>>" for h in hs)
        if "<<from row>>" in recon: fail(f"{rid} has a person-held piece in the canary (must be excluded)")
        if recon != orig: fail(f"{rid} history does not reproduce the original note")
        if sorted(NS.pieces(orig)) != sorted(h["text"] for h in hs): fail(f"{rid} segment multiset differs")
        for h in hs:
            if h["on_row"] == "kept" and NS.tidy(h["text"]) not in c["after"]: fail(f"{rid} kept piece {h['seq']} missing from the row")
            if h["on_row"] == "restated" and h["restated_as"] not in c["after"]: fail(f"{rid} restated piece {h['seq']} missing from the row")
            if h["on_row"] == "moved" and h["restated_as"]: fail(f"{rid} moved piece {h['seq']} has a restatement")
    ok(f"lossless: {len(cv)} canary notes reproduced exactly from history pieces ({sum(len(v) for v in hist.values())} pieces)")
    # ---------------------------------------------------------------- 2. RESIDUE
    bad = [(c["record_id"], residue(c["after"])) for c in cv if residue(c["after"])]
    for rid, h in bad: fail(f"{rid} residue on row: {h[:4]}")
    if not bad: ok("residue: no pipeline word remains on any of the 25 canary rows (pinned code-read phrases excepted)")
    # planted misses go through the real row-building path (split_note -> after_note), not onto the word list
    plant1 = by["SITE-004152"]["_parts"] + [{"seq": 99, "text": "Reviewed in integration pass 9 by Grok.", "disp": "KEEP", "kind": "forged", "restated": None}]
    plant2 = by["SITE-004152"]["_parts"] + [{"seq": 99, "text": "Held under FOOBAR_BAZ review.", "disp": "KEEP", "kind": "forged", "restated": None}]
    for name, pl in (("planted agent/pass sentence", plant1), ("planted underscore/ALL-CAPS token only the independent list knows", plant2)):
        if residue(NS.after_note(pl, {1: "KEEP", 99: "KEEP"})): ok(f"planted miss caught: {name}")
        else: fail(f"planted miss NOT caught: {name}")
    # ---------------------------------------------------------------- 3. DEPENDENCIES (corpus-wide)
    street_phr = [re.compile(r"Street(?:\s+correct(?:ion|ed)[^:]{0,20})?(?:\s*\((?:per|from)[^)]*\))?:\s*(\d[^;|\n]{2,80})", re.I), re.compile(r"Address[^:]{0,60}match\):\s*(\d[^;|\n]{2,80})", re.I)]  # copy of build_osha_ita._STREET_PATS
    def skeys(t):
        k = {atlas.notes_candidate_key(m[0]) for m in atlas.NOTES_STREET_RE.finditer(t)}
        for rx in street_phr:
            for m in rx.finditer(t): k.add(atlas.street_key(re.split(r"\s\(|\.\s*$", m.group(1))[0]))
        return {x for x in k if x}
    FRS, FEI = re.compile(r"\b1\d{11}\b"), re.compile(r"\bFEI\W{0,3}(\d{6,10})\b")
    TOMB, WARNRX = re.compile(r"tombstoned as duplicate of (SITE-\d{6})", re.I), re.compile(r"\bWARN\b")
    names = {}
    for o in orgs:
        for f in ("legal_name",):
            n = atlas.squash(o[f])
            if len(n) >= 8: names.setdefault(n, o["org_id"])
    def mentions(text, self_id):
        toks = atlas.squash(text).split(); found = set()
        for i in range(len(toks)):
            for L in range(1, 7):
                n = " ".join(toks[i:i + L])
                if n in names and names[n] != self_id: found.add(names[n])
        return found
    res = {m: collections.Counter() for m in ("script-only", "worst-case")}
    for r in orgs + sites:
        orig, parts = r["notes"], r["_parts"]
        col = atlas.street_key(r.get("street_address", ""))
        row_keys_orig = skeys(orig) - {col}
        ids_o = set(FRS.findall(orig)); fei_o = set(FEI.findall(orig)); tomb_o = bool(TOMB.search(orig)) and r["_table"] == "sites"
        warn_o = bool(WARNRX.search(orig)) and r["_table"] == "sites"; men_o = mentions(orig, r["_id"]) if r["_table"] == "organizations" else set()
        n_reader = sum(p["disp"] == "READER" for p in parts)
        for mode in res:
            a = group_after(parts, mode); c = res[mode]
            c["rows"] += 1
            if row_keys_orig:
                c["street+"] += 1
                if not row_keys_orig <= skeys(a): c["street lost"] += 1
            if ids_o:
                c["frs+"] += 1
                if not ids_o <= set(FRS.findall(a)): c["frs lost from row"] += 1
            if fei_o:
                c["fei+"] += 1
                if not fei_o <= set(FEI.findall(a)): c["fei lost from row"] += 1
            if tomb_o:
                c["tomb+"] += 1
                if not TOMB.search(a): c["tomb lost"] += 1
            if warn_o:
                c["warn+"] += 1
                if not WARNRX.search(a): c["warn lost"] += 1
            if r["_table"] == "sites" and "parcel candidate queue" in orig and r["state"] == "OH" and not r["county"].strip():
                c["parcel+"] += 1
                if "parcel candidate queue" not in a: c["parcel lost (V: Ohio blank county)"] += 1
            if r["_table"] == "organizations" and "Settling fact:" in orig and r.get("status") == "active" and r.get("liveness_signal") == "closure_signature" and r.get("monitor_watch") == "true":
                c["settling+"] += 1
                if "Settling fact:" not in a: c["settling lost (V-24)"] += 1
            if men_o:
                c["name-mention+"] += 1
                if not men_o <= mentions(a, r["_id"]): c["name-mention lost from row"] += 1
            if mode == "script-only": c["reader pieces"] += n_reader
    for mode, c in res.items():
        print(f"  [{mode}] ", {k: v for k, v in sorted(c.items())})
    for cls in ("street+", "frs+", "fei+", "tomb+", "warn+", "name-mention+"):
        if res["worst-case"][cls] == 0: fail(f"dependency class {cls} inspected zero positives (vacuous)")
    for mode in res:   # pinned classes: code reads the phrase on the row, so no mode may lose it
        for k in ("tomb lost", "warn lost", "parcel lost (V: Ohio blank county)", "settling lost (V-24)"):
            if res[mode][k]: fail(f"[{mode}] pinned marker lost: {k} = {res[mode][k]}")
    for cls in ("parcel+", "settling+"):
        if res["worst-case"][cls] == 0: print(f"  note: {cls} has zero live positives on this tree (validator rule is vacuous today: DESIGN §3); canary still carries the literal marker rows")
    ok("dependencies measured corpus-wide (see DESIGN §3 for what the lost counts mean)")
    json.dump({m: dict(c) for m, c in res.items()}, open(HERE / "dependency_counts.json", "w"), indent=1, sort_keys=True)
    # ---------------------------------------------------------------- 4. TREE
    d = subprocess.run(["git", "diff", "--stat", "origin/main", "--", "data"], cwd=HERE, capture_output=True, text=True).stdout.strip()
    ok("data/ unchanged vs origin/main") if not d else fail("data/ differs from origin/main:\n" + d)
    print("\nRESULT:", "FAIL (%d)" % len(FAIL) if FAIL else "PASS")
    return 1 if FAIL else 0

if __name__ == "__main__":
    sys.exit(main())
