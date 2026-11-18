#!/usr/bin/env python3
"""National capability batch b01: replay lane_decisions.csv into site processes/materials, site_capabilities and
site evidence rows. Rules follow the PIC-18 corpus lanes (tasks/pic18-capabilities-corpus-2b-2026-11-16):
  - every term's quote (<= 25 words) and its locality witness are re-checked against the stored raw page and its
    SHA-256 (the corpus sits outside the repository, at CORPUS);
  - narrative sentence = supports_A; menu item = supports_C; on a tier A/B site a menu term becomes a capability row
    only, with no section-3 tag (owner ruling 2026-11-14);
  - fill-blank-only: the frame admits only sites whose processes AND materials are blank on the pinned base;
  - integrator overrides (HOLD_SITES, DROP_TERMS) record judgement calls taken after reading the lanes' own flags.
Idempotent: IDs are recomputed from decision order and must equal any row already present.

    python3 tasks/capability-national-b01-2026-11-18/build.py [--apply]
"""
import csv, hashlib, html, io, json, re, subprocess, sys
from pathlib import Path

T = Path(__file__).resolve().parent
ROOT = T.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from shard_io import append_sorted  # noqa: E402

CORPUS = Path(r"C:\Users\JohnSwanson\Documents\pic-github\_atlas-corpus\capnat-b01")
BASE = (T / "base.txt").read_text().strip()
WHO, DATE, CAP0, EVD0 = "claude-code capability-national-b01", "2026-11-18", 1600, 397000  # above main + open PRs
MENU_CAP_ONLY = "capability row only; tag held (owner ruling 2026-11-14)"
HOLD_SITES = {
    "SITE-010055": "home page says '5 Locations'; plant not allocated (multi-location)",
    "SITE-002383": "stored address 531 Tel Power Rd differs from the record's 521 (house-number mismatch)",
    "SITE-002660": "the live 'Our Story' page (not in the stored corpus) states three production facilities (codex, refute 1)",
}
DROP_TERMS = {
    ("SITE-008334", "mold_tool_making"): "a press release credits this part's tooling to an outside firm",
    ("SITE-010025", "mold_tool_making"): "'in-house tooling' for fast delivery does not state mold making",
    ("SITE-002517", "polyethylene_pe"): "a product name (HMPE rope), not a material the plant states it processes",
    ("SITE-002294", "polyethylene_pe"): "'polyethylene plugs' is product copy, not a processing statement",
    ("SITE-002467", "assembly_secondary_ops"): "'other secondary operations' is too vague for the term",
    ("SITE-011908", "polyurethane_pu"): "'Moisture Cure Urethanes' is a product name (grok, refute 2)",
    ("SITE-002555", "mold_tool_making"): "a capabilities-page list item, not a narrative sentence (codex, refute 1)",
    ("SITE-002555", "assembly_secondary_ops"): "a generic definition with no company actor (codex, refute 1)",
    # codex full-set review 3: only rows it judged SOUND are kept
    ("SITE-002477", "silicones"): "a second address (seminar entrance, 1725 Willow Lane) is unresolved (codex, review 3)",
    ("SITE-002477", "polyurethane_pu"): "a second address (seminar entrance, 1725 Willow Lane) is unresolved (codex, review 3)",
    ("SITE-002321", "pvc"): "'vinyl' does not name PVC, and 'use' is not a processing verb (codex, review 3)",
    ("SITE-011908", "coating_formulation"): "furnishing 'own formulated products' does not say Indmar formulates (codex, review 3)",
    ("SITE-011908", "coatings"): "basis mislabelled as a list item; re-adjudicate as narrative (codex, review 3)",
    ("SITE-002586", "elastomers_rubber"): "'core competence' carries no processing verb (codex, review 3)",
    ("SITE-008229", "fabrication_unspecified"): "a generic line-bending definition, not the company's own list (codex, review 3)",
    ("SITE-008255", "plastics_machining_cnc"): "the full sentence is an 'operations like' example list (codex, review 3)",
    ("SITE-008334", "thermoforming_vacuum"): "'leader in ... solutions' is positioning, not a process claim (codex, review 3)",
    # grok full-set review 4: only rows BOTH families judged SOUND are kept
    ("SITE-002285", "polyethylene_pe"): "a film product list with no processing verb (grok, review 4)",
    ("SITE-002586", "insert_overmolding"): "'can also provide overmolding' is offer wording; 'insert' is absent (grok, review 4)",
    ("SITE-008229", "plastics_machining_cnc"): "the quote never says plastics (grok, review 4)",
    ("SITE-008334", "plastics_machining_cnc"): "the quote never says CNC or plastics (grok, review 4)",
    ("SITE-002586", "injection_molding_lsr_silicone"): "pages name Stockwell, the record Src: alias not on a stored page (grok, review 4)",
    ("SITE-002586", "rubber_molding_compression"): "pages name Stockwell, the record Src: alias not on a stored page (grok, review 4)",
    ("SITE-002586", "die_cutting_converting"): "pages name Stockwell, the record Src: alias not on a stored page (grok, review 4)",
    ("SITE-002586", "silicones"): "pages name Stockwell, the record Src: alias not on a stored page (grok, review 4)",
    ("SITE-008255", "molding_unspecified"): "witness is a city-level 'headquarters' line; street and single site unconfirmed (grok, review 4)",
    ("SITE-008255", "mold_tool_making"): "witness is a city-level 'headquarters' line; street and single site unconfirmed (grok, review 4)",
    ("SITE-008255", "polyurethane_pu"): "witness is a city-level 'headquarters' line; street and single site unconfirmed (grok, review 4)",
    ("SITE-002294", "assembly_secondary_ops"): "'department can save you time' names no operation performed (grok, review 4)",
}


# Gates added after the codex refute of the first draft (9 WRONG / 7 DOUBT in 40). Each is mechanical and recorded:
MULTI = re.compile(r"\b(\d+|two|three|four|five|six|several|multiple)\s+(large\s+)?(manufacturing\s+|production\s+)?"
                   r"(locations|facilities|plants|sites)\b|\bour (other )?(locations|facilities|plants)\b|\ball locations\b", re.I)
SUBJECT = re.compile(r"\b(we|our|us|ours)\b", re.I)   # a narrative sentence names its actor; otherwise it is a list item
EXAMPLES = re.compile(r"\bsuch as\b|\blike\b", re.I)  # an example list is not a capability statement


# Second-round gates (grok refute 2: 9 WRONG / 11 DOUBT in a fresh 40).
OPEN_LIST = re.compile(r"\binclud(e|es|ing)\b|\band more\b|\boptions\b|\be\.g\.", re.I)
NOT_MAKER = re.compile(r"\bsuppl(y|ies|ier)\b|\bdistribut|\bexperts? in\b|\byour (parts?|product|project)|\bwhether\b", re.I)
PROCESS_VERB = re.compile(r"mold|extru|process|fabricat|machin|form|cast|compound|manufactur|produc|run|make|made|"
                          r"convert|laminat|coat|print|weld|blend|formulat|cur(e|ing)|mix", re.I)
CAP_PAGE = re.compile(r"capabilit|service|process|material|equipment|what-we-do|manufactur|facilit", re.I)
ALIAS = {"polyurethane": "urethan", "polyethylene": "polyethylene|hdpe|ldpe|lldpe|\\bpe\\b", "pvc": "pvc|vinyl"}


def term_named(term, quote):
    """Every head of the term's name appears in the quote ('hose_belting' needs hose AND belt) - materials and
    compound process codes only; a generic process word like 'molding' is matched by PROCESS_VERB instead."""
    heads = [h for h in term.split("_") if len(h) >= 3 and h not in ("unspecified", "manufacturing", "services", "other")]
    q = quote.lower()
    return all(re.search(ALIAS.get(h, re.escape(h[:5])), q) for h in heads)


def gate(d, site_name, org_pages):
    """(decision, None) with basis possibly downgraded, or (None, reason) when the term is dropped."""
    if EXAMPLES.search(d["quote"]) or OPEN_LIST.search(d["quote"]):
        return None, "quote is an example or open-ended list ('such as', 'like', 'include', 'and more', 'options')"
    if NOT_MAKER.search(d["quote"]):
        return None, "supply, expertise or customer wording, not a statement that the company does this itself"
    if d["term"].endswith("_formulation") and "formulat" not in d["quote"].lower():
        return None, "a formulation term needs the page to say it formulates"
    if d["field"] == "materials" and not PROCESS_VERB.search(d["quote"]):
        return None, "a material named without a processing verb (product heading or name)"
    if (d["field"] == "materials" or "_" in d["term"].replace("_unspecified", "")) and d["field"] == "materials" and not term_named(d["term"], d["quote"]):
        return None, "the quote does not name every part of the material term"
    if d["term"] in ("hose_belting_manufacturing", "melamine_urea_formaldehyde") and not term_named(d["term"], d["quote"]):
        return None, "a compound term needs every part named"
    if d["basis"] == "narrative" and not SUBJECT.search(d["quote"]):
        name = [w for w in re.findall(r"[A-Za-z]{4,}", site_name)][:1]
        if not (name and name[0].lower() in d["quote"].lower()):
            d = dict(d, basis="menu")  # no actor in the sentence: list-item strength (supports_C)
    if d["basis"] == "menu" and not CAP_PAGE.search(d["url"]):
        return None, "list-strength wording on a page that is not a capabilities, services or materials page"
    return d, None


def identity_or_city_gap(site, man):
    """A witness must name the record's city, and the company's pages must carry the record's name (grok refute 2:
    Ferguson vs St. Louis; Stockwell vs Src)."""
    pages = [(CORPUS / m["text_file"]).read_text(encoding="utf-8").lower() for m in man
             if m["site_id"] == site["site_id"] and m["status"] == "ok"]
    city = re.sub(r"[^a-z]", "", site["city"].lower())
    if not any(city in re.sub(r"[^a-z]", "", p) for p in pages):
        return f"no stored page names the record's city ({site['city']})"
    first = next((w for w in re.findall(r"[A-Za-z]{3,}", site["site_name"])), "")
    if first and not any(first.lower() in p for p in pages):
        return f"no stored page names the record's company ({site['site_name']})"
    return None


def multi_location(site_id, man):
    for m in man:
        if m["site_id"] == site_id and m["status"] == "ok":
            hit = MULTI.search((CORPUS / m["text_file"]).read_text(encoding="utf-8"))
            if hit:
                return f"multi-location signal on {m['url']}: '{hit.group(0)}'"
    return None


def read(p):
    return list(csv.DictReader(open(p, newline="", encoding="utf-8")))


def base(p):
    return list(csv.DictReader(io.StringIO(subprocess.check_output(["git", "show", f"{BASE}:{p}"], cwd=ROOT,
                                                                    text=True, encoding="utf-8"))))


norm = lambda t: " ".join(t.split())
VOCAB = json.loads((ROOT / "docs/schema/vocab.json").read_text(encoding="utf-8"))["vocabularies"]
ROLLUP = ("thermoforming_", "rubber_molding_", "extrusion_", "blow_molding_")


def validate_decision(d):
    """AssertionError unless quote, term and locality witness all hold against the stored pages."""
    for raw, sha in ((d["raw_file"], d["sha256"]), (d["grain_raw_file"], d["grain_sha256"])):
        assert hashlib.sha256((CORPUS / raw).read_bytes()).hexdigest() == sha, f"raw hash mismatch {raw}"
    plain = html.unescape(re.sub("<[^>]+>", " ", (CORPUS / d["raw_file"]).read_text(encoding="utf-8", errors="replace")))
    words = iter(re.findall(r"\w+", plain.lower()))
    assert all(any(w == q for w in words) for q in re.findall(r"\w+", d["quote"].lower())), "quote words absent or out of order in raw page"
    assert norm(d["quote"]) in norm((CORPUS / d["text_file"]).read_text(encoding="utf-8")), "quote not in stored text"
    gtext = norm((CORPUS / d["grain_raw_file"].replace(".html", ".txt")).read_text(encoding="utf-8"))
    assert norm(d["grain_quote"]) in gtext, "locality witness not in stored text"
    assert len(d["quote"].split()) <= 25, "quote over 25 words"
    assert d["term"] in VOCAB[d["field"].upper()]["values"], "term not in vocabulary"
    assert d["basis"] in ("narrative", "menu")


def cap_term(term, typ):
    values = VOCAB["CAP_" + typ.upper()]["values"]
    if term in values:
        return term
    return next((p[:-1] for p in ROLLUP if term.startswith(p) and p[:-1] in values), None)


def outputs():
    sl = {r["site_id"]: r for r in read(T / "slice.csv")}
    man = read(CORPUS / "manifest.csv")
    multi = {s: why for s in sl if (why := multi_location(s, man) or identity_or_city_gap(sl[s], man))}
    gated_out, decisions = [], []
    for d in read(T / "lane_decisions.csv"):
        if d["site_id"] in HOLD_SITES or d["site_id"] in multi or (d["site_id"], d["term"]) in DROP_TERMS:
            continue
        d2, why = gate(d, sl[d["site_id"]]["site_name"], man)
        if why:
            gated_out.append((d["site_id"], d["term"], why))
        else:
            decisions.append(d2)
    states = sorted({r["state"] for r in sl.values()})
    sites = {r["site_id"]: dict(r) for st in states for r in base(f"data/sites_{st}.csv") if r["site_id"] in sl}
    assert set(sites) == set(sl)
    live = {(c["site_id"], c["capability_type"], c["term"]) for c in base("data/site_capabilities.csv") if not c["withdrawn_date"]}
    caps, ev, verdicts = [], {}, []
    evid, capid = iter(range(EVD0, EVD0 + 1000)), iter(range(CAP0, CAP0 + 1000))
    for d in decisions:
        validate_decision(d)
        s = sites[d["site_id"]]
        typ = "process" if d["field"] == "processes" else "material"
        tag = not (d["basis"] == "menu" and s["verification_tier"] in ("A", "B"))
        if tag:
            s[d["field"]] = ";".join(sorted(set(filter(None, s[d["field"]].split(";"))) | {d["term"]}))
            ev.setdefault(s["state"], []).append(dict(
                evidence_id=f"EVD-{next(evid):06d}", record_table="sites", record_id=s["site_id"], claim_type="scope",
                claim_detail=f"{d['field']}={d['term']}; quote: {d['quote']}", source_class="own_site",
                source_ref=d["url"], observed_date=DATE,
                tier_effect="supports_A" if d["basis"] == "narrative" else "supports_C", created_by=WHO,
                notes=f"{d['basis']}; raw SHA256 {d['sha256']}; locality witness: {d['grain_quote']} ({d['grain_url']}); "
                      f"single active Atlas site."))
        ct = cap_term(d["term"], typ)
        if ct and (s["site_id"], typ, ct) not in live:
            live.add((s["site_id"], typ, ct))
            caps.append(dict(capability_id=f"CAP-{next(capid):06d}", site_id=s["site_id"], org_id=s["org_id"],
                             capability_type=typ, term=ct, provenance="company_disclosed", source_ref=d["url"],
                             observed_date=DATE, withdrawn_date="", created_by=WHO,
                             notes=f"Quote: {d['quote']} Basis: {d['basis']}. Raw SHA256 {d['sha256']}."
                                   + ("" if tag else " Section-3 tag held per owner ruling 2026-11-14; needs narrative plant evidence.")))
        verdicts.append(dict(site_id=d["site_id"], term=d["term"], verdict="VERIFIED",
                             disposition="applied" if tag else MENU_CAP_ONLY, reason=f"{d['basis']} quote on own page",
                             settling_fact="" if tag else "Plant narrative sentence stating this term"))
    decided = {d["site_id"] for d in decisions}
    for h in read(T / "lane_holds.csv"):
        verdicts.append(dict(site_id=h["site_id"], term=h["terms"], verdict="STILL_UNCERTAIN", disposition="held",
                             reason=h["reason"], settling_fact=h["settling_fact"]))
    for sid, why in {**HOLD_SITES, **multi}.items():
        verdicts.append(dict(site_id=sid, term="", verdict="STILL_UNCERTAIN", disposition="held (integrator)",
                             reason=why, settling_fact="An own page tying the terms to this establishment's address"))
    for sid, term, why in gated_out:
        verdicts.append(dict(site_id=sid, term=term, verdict="STILL_UNCERTAIN", disposition="held (gate)",
                             reason=why, settling_fact="An own-page sentence stating the company does this itself"))
    for (sid, term), why in DROP_TERMS.items():
        verdicts.append(dict(site_id=sid, term=term, verdict="STILL_UNCERTAIN", disposition="held (integrator)",
                             reason=why, settling_fact="An own-page sentence stating the company does this itself"))
    man = read(CORPUS / "manifest.csv")
    for sid in sl:
        if not any(m["site_id"] == sid and m["status"] == "ok" for m in man):
            verdicts.append(dict(site_id=sid, term="", verdict="STILL_UNCERTAIN", disposition="no stored page",
                                 reason="the company website did not return a readable page (availability, not absence)",
                                 settling_fact="A readable own-site page"))
    covered = {v["site_id"] for v in verdicts}
    assert covered == set(sl), f"sites without a verdict: {sorted(set(sl) - covered)}"
    return sl, sites, caps, ev, sorted(verdicts, key=lambda v: (v["site_id"], v["term"])), decided


def selftest():
    """Each injected defect must be refused by validate_decision (a check that cannot fail is not a check)."""
    good = read(T / "lane_decisions.csv")[0]
    validate_decision(good)
    defects = {"false quote": dict(good, quote="we extrude titanium spaceship hulls daily"),
               "wrong hash": dict(good, sha256="0" * 64),
               "term not in vocabulary": dict(good, term="unobtainium_molding"),
               "false locality witness": dict(good, grain_quote="located in Atlantis"),
               "quote over 25 words": dict(good, quote=(good["quote"] + " ") * 6),
               "bad basis": dict(good, basis="hearsay")}
    for name, d in defects.items():
        try:
            validate_decision(d)
        except AssertionError:
            continue
        raise SystemExit(f"selftest: '{name}' was NOT refused")
    print(f"selftest: {len(defects)} injected defects refused")


def write_shard(path, updates):
    raw = path.read_bytes(); eol = "\r\n" if b"\r\n" in raw[:4096] else "\n"
    rdr = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline="")); rows = list(rdr)
    for r in rows:
        if r["site_id"] in updates:
            for col in ("processes", "materials"):
                if updates[r["site_id"]][col] and not r[col].strip():
                    r[col] = updates[r["site_id"]][col]
                else:
                    assert r[col] == updates[r["site_id"]][col] or not updates[r["site_id"]][col], f"{r['site_id']} {col} not blank on main"
    buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=rdr.fieldnames, lineterminator=eol); w.writeheader(); w.writerows(rows)
    path.write_bytes(buf.getvalue().encode("utf-8"))


def main():
    selftest()
    sl, sites, caps, ev, verdicts, decided = outputs()
    tagged = {e["record_id"] for rows in ev.values() for e in rows}
    summary = dict(slice_sites=len(sl), decided_sites=len(decided), tagged_sites=len(tagged),
                   tag_terms=sum(len(v) for v in ev.values()), capability_rows=len(caps),
                   held_or_nothing_sites=len(set(sl) - decided), verdict_rows=len(verdicts))
    print(summary)
    if "--apply" not in sys.argv:
        return
    for st in sorted({sites[s]["state"] for s in tagged}):
        write_shard(ROOT / f"data/sites_{st}.csv", {s: sites[s] for s in tagged if sites[s]["state"] == st})
    for st, rows in ev.items():
        p = ROOT / f"data/evidence_sites_{st}.csv"; have = {r["evidence_id"]: r for r in read(p)}
        for r in rows:
            if r["evidence_id"] in have: assert r == have[r["evidence_id"]], f"{r['evidence_id']} differs"
        append_sorted(p, [r for r in rows if r["evidence_id"] not in have], "evidence_id")
    p = ROOT / "data/site_capabilities.csv"; have = {r["capability_id"]: r for r in read(p)}
    for r in caps:
        if r["capability_id"] in have: assert r == have[r["capability_id"]], f"{r['capability_id']} differs"
    append_sorted(p, [r for r in caps if r["capability_id"] not in have], "capability_id")
    with open(T / "verdicts.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(verdicts[0]), lineterminator="\n"); w.writeheader(); w.writerows(verdicts)
    (T / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print("written")


if __name__ == "__main__":
    main()
