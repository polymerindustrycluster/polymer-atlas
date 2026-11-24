"""Split a public `notes` value into pieces and decide where each piece lives (DESIGN.md §4).

A note is cut into pieces (whitespace-only boundaries, so no character is lost). Each piece is
  KEEP     stays on the row verbatim (clean, reader-facing),
  MOVE     goes verbatim to the history file,
  RESTATE  goes verbatim to the history file AND a plain sentence is logged beside it and placed on the row,
  READER   matches no template but carries pipeline words: a person has to decide (the script never guesses).
Lossless by construction: original pieces == KEEP + MOVE + RESTATE originals (check.py proves it per row).
"""
import re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import atlas  # noqa: E402  (street_key, NOTES_STREET_RE: the readers this design must not break)

# ---------------------------------------------------------------- pipeline word list (derived from the 200-note read)
# Each entry: (label, regex). A hit on a row's kept text is a defect. Source acronyms (TRI, ITA, OSHA, ECHO, FRS, EDGAR),
# record ids (ORG-/SITE-) and tier letters are NOT pipeline words here: that is an owner ruling (DESIGN.md §9).
_W = [
    ("agent", r"\b(?:Grok|spaghetti|Muse|Codex|Gemini|Antigravity|subagent|harness)\b|\bClaude\b"),
    ("role", r"\b(?:integrators?|coordinator|orchestrator)\b"),
    ("pass", r"\b(?:integration pass|[Pp][Aa][Ss][Ss][- ]\d+)\b"),
    ("wave", r"\b(?:verification|enrichment|requeue|skimpy-state|STRONG|national|candidate-queue)[ -]wave\b|\bwave[- ]?\d+\b|\bnational-spine pilot\b|\bwave packet\b"),
    ("burndown", r"\bburn-?down\b"),
    ("packet", r"\b(?:packets?|verdicts?|lane [A-Z]?\d+|lane's|lane evidence|journal)\b|\bEvidence basis \(lane\)"),
    ("id", r"\b(?:W\d{1,2}-(?:[A-Z]{2}-)?\d{3,4}|L\d-\d+|PKT-\d+|P\d{3}-P\d{3}|LF-[A-Z]{2}-\d+|QMS-[A-Z]{2}-\d+|P2-[A-Z]{2}-\d+|H-\d+\.\d+|K-\d+(?:\.\d+)?|V-\d{2}|R\d+[a-z]?|[A-Z]\d{2}-\d{2}(?:-S\d)?)\b|\bNEW(?:SITE)?:\S+|\bPR #\d+"),
    ("path", r"\b(?:staging|working/|tasks/|raw/)\S*|\b\w+\.(?:csv|md|json)\b"),
    ("field", r"\b[a-z]+(?:_[a-z0-9]+)+\b|\b\w+=\S+"),
    ("doc", r"§|\bAGENTS\b|\bSCHEMA\b|\bs4\.\d|\bs3 step\b|\bAGENTS s"),
    ("trace", r"\bsites? schema\b|\bmatcher\b|\bprep (?:org|assignment|allocation)\b|\bSpot-check\b|\bsection \d\b|\bASSIGNMENT CHANGE\b|\bR-\d+\b|\bdesign row\b|\bhence tier\b|\bpacket identifiers\b|\bstatus change\b|\b(?:the )?(?:fetch|search)[- ]cap\b|\bwithin cap\b|\bat light standard\b|\b(?:dedupe|de-dupe|tombstone[ds]?|re-?pointed|folded into|FLAG for|flag for integrator|near-name magnet|prep assignment|adjacency|site design|org design|freeze (?:tier|dedupe)|requeue|RETRY RECOVERED)\b|\bPrep assignment\b|\bAdjacency\b"),
    ("tierfx", r"\btier (?:restated|set|U ->)|\bTier [ABCU] at birth|\bweakest must-have|\bat birth\b|[A-Z] -> [A-Z]\b|\bmotion [A-Z]\d+"),
    ("jargon", r"\bTier [ABCU]\b|\bVERIFIED\b|\blegs?\b|\b[Ss]ettling fact\b|\brow \d+\b|\bin this pass\b|\bStep-\d|\bquote span\b|\bTRIFID\b|\bcoded from\b|\bnot designed\b|\bupgrade path\b|\bdesigned\b|\b(?:un)?held\b|\bgrain\b|\bASSERT\b|ASSERT-AT-APPLICATION|DO-NOT-MERGE|\bRETIRED\b|\bADDRESS NOTE\b|\bwave\b|\bpass\b|\bstep \d|\bregistry ID\b.{0,5}phantom|\bmagnet\b|\bfreeze\b|\bpilot\b|\bRing \d\b|\bring \d\b|\btier [abcu] proposed\b|\bproposed\b|\bcarry \d{6}\b|\bspans?\b|\bPhase [A-Z0-9]\b|\bscope[- ]only\b|\bquote-only\b|\bI did not\b|\bsingle-source\b|\bfederal[- ]frame\b|\b\d{6}\)? as secondary\b|\brides as\b|\bupgrade path\b|\bsite-under\b|\bwitness\b|\badjudicat\w+|\bcall matches\b"),
    ("marker", r"\b(?:BAND|CERT)-SITE?\b|\bBAND-SOURCE\b|\bCAPABILITY-QUEUE\b"),
]
WORDS = [(n, re.compile(rx, re.I if n == "jargon" else 0)) for n, rx in _W]


def hits(text):
    return [(n, m.group(0)) for n, rx in WORDS for m in rx.finditer(text)]


# ---------------------------------------------------------------- segmenter
ABBR = {"wm", "rte", "rt", "inc", "co", "corp", "ltd", "llc", "lp", "st", "ave", "dr", "rd", "blvd", "mt", "ft", "no", "vs", "approx", "jr", "sr",
        "ste", "pkwy", "hwy", "mfg", "fed", "e.g", "i.e", "u.s", "div", "est", "fig", "ind", "bros", "assoc", "intl", "natl", "mgmt"}
_BOUND = re.compile(r"(?<=[.;?!])(\s+)(?=(?:\|\s+)?[A-Z0-9$~\[(\"'\u2018\u201c])")
_HEADS = re.compile(
    r"(?<!INTEGRATION)(\s+)(?=(?:county (?:UNVERIFIED|RESOLVED)|Verified \d{4}-\d\d-\d\d|Wave-\d+ verification|Association corroboration|BAND-SOURCE:|CERT-SITE \(|CAPABILITY-QUEUE:|"
    r"INTEGRATION PASS|PASS \d+|Pass \d+[ (§]|\[Pass|\[Dedupe|NAICS corrected|Street[^:]{0,40}:\s*\d|Created \d{4}-\d\d-\d\d|Relationship \(|Basis: ))")
_PREFIX = re.compile(  # a pipeline header glued by a colon to a reader fact: the header is its own piece, the fact is classified alone
    r"^((?:Created|Tier [ABCU]|Basis|Lane evidence|Evidence basis \(lane\)|Source checked|Verified|Wave-\d+ verification|Association corroboration|"
    r"Pass \d+|PASS \d+|INTEGRATION PASS|Integration \d{4}-\d\d-\d\d|Verification wave \d)[^:()]{0,170}(?:\([^()]*\)[^:()]{0,60})?:\s+)(?=\S)")


def _is_abbrev(before):
    tok = re.findall(r"[A-Za-z.]+$", before.rstrip(". "))
    w = (tok[0] if tok else "").rstrip(".").lower()
    return before.rstrip().endswith(".") and (w in ABBR or bool(re.fullmatch(r"[a-z]|(?:[a-z]\.)+[a-z]?", w)))


def _sentence_cuts(text):
    cuts = set()
    for rx in (_BOUND, _HEADS):
        for m in rx.finditer(text):
            before = text[:m.start(1)]
            i = before.rfind("(")
            if i >= 0 and before.rfind(")") < i and len(before) - i < 80:  # inside a short parenthesis: not a boundary
                continue
            if rx is _BOUND and _is_abbrev(before):
                continue
            cuts.add(m.end(1))  # cut AFTER the whitespace so it stays on the previous piece
    return sorted(cuts)


def _split_at(text, cuts):
    out, last = [], 0
    for c in cuts:
        out.append(text[last:c]); last = c
    out.append(text[last:])
    return out


def pieces(note):
    """-> list of piece texts; ''.join(pieces) == note exactly (every separator stays on a piece)."""
    work, res = [note], []
    while work:
        t = work.pop(0)
        parts = _split_at(t, _sentence_cuts(t))
        if len(parts) > 1:
            work = parts + work; continue
        m = _PREFIX.match(t)
        if m and t[m.end():].strip():
            work = [t[:m.end()], t[m.end():]] + work
            # the header itself must not be re-cut: emit it directly
            res.append(work.pop(0)); continue
        res.append(t)
    assert "".join(res) == note
    return [p for p in res if p != ""]


# ---------------------------------------------------------------- classification
_MOVE_LEADS = re.compile(
    r"^(?:Created \d{4}-\d\d-\d\d|Created in PKT|Source: Grok|Grok (?:parent_org_id|org_id|polymer_relevance)|HQ city/county from representative|"
    r"INTEGRATION PASS|PASS \d+|Pass \d+[ (§]|\[Pass \d+|\[Dedupe|Packet (?:entity_type|ownership_type)|NAICS corrected|Wave-\d+ verification|"
    r"Association corroboration|Verified \d{4}-\d\d-\d\d|Atlas Tier U burn-down|Field edits:|Converted from|Prep assignment|"
    r"Adjacency (?:lead|signal)|Packet adjacency|TRI parent strings?|Coordinator|Freeze dedupe|Exact-string check|No dedupe hit|"
    r"Dedupe: name|Basis:|Lane evidence:|Created in the|Tier C at birth|Federal source:|L\d STRONG|LF-[A-Z]{2}-\d+;|"
    r"Packet entity|Basis for tier|Tier (?:set|restated)|CORROBORATED|"
    r"Parent primary aligns|CY20\d\d ITA establishment_ID|\(pass-\d+|NAICS adjudication|Prep allocation|HQ shown as the packet|TRI PARENT NOTE|R-\d+:|"
    r"\(held record|NAICS \d+ ->|Note: this record carries no NAICS|Verification wave \d|Adjacency|Folded same-establishment|Integration \d{4}|"
    r"Ring \d and Tier [ABCU] per|ITA:\d|Filed ITA company_name|Held parent resolved|Held parent/registrant|manufacturing_plant \||[a-z_]+ \|\s*$|"
    r"Federal-only provisional C, operating evidence is CY|Prep |New org designed|Placed under|Net-new (?:org|site)|"
    r"Tier [ABCU]\b|Federal[- ]only|Federal sources?|Fed\s*$|Provisional federal|Held parent|Dedupe: |Move is not|Active status retained|Row never deleted|"
    r"No parent change|Staged |Evidence class|Membership corroborates|Disposition|Base values kept|New org|Under ORG|"
    r"Site-level tier|Shared domain|True unheld|Website not in pilot|Operator re-derived|County blank in federal|FRS county|FRS \d|"
    r"County not settled|Startup ringed|Settling fact for|ITA:|Net-new|"
    r"Ring \d (?:operating|plant)|Ring \d\.$|Tier set|FDA FEI \d+ \u2014 the registration was)", re.I)
_BAND = re.compile(r"^BAND-SOURCE:\s*employee_band_(site|ohio)=(\S+) from (.+?) \((?:government_filing|company_disclosed|directory_assigned|researcher_inferred); ([^)]*)\)\.?\s*$")
_CERT = re.compile(r"^CERT-SITE \(([^,)]+), observed (\d{4}-\d\d-\d\d)\):\s*(.+?)\.?\s*$")
_CAPQ = re.compile(r"^CAPABILITY-QUEUE:\s*(.+?)(?:\s*\(|;|\.\s*$|\s*$)")
_STREET = re.compile(r"^(Street(?: correct(?:ion|ed)[^:(]{0,20})?)(?:\s*\((?:per|from)\s+([^)]*)\))?:\s*(\d.+?)\s*$", re.S)
_CERTNAME = {"iso_9001": "ISO 9001", "iso_14001": "ISO 14001", "iatf_16949": "IATF 16949", "as9100": "AS9100", "iso_13485": "ISO 13485",
             "iso_45001": "ISO 45001", "nadcap": "NADCAP", "itar": "ITAR registration", "iso_13485": "ISO 13485", "ul_listed": "UL listed", "fda_registered": "FDA registered"}
_RING = re.compile(r"^Ring (\d) subtype: (\w+)(?: \(from Grok org_type '[^']*'\))?\.?\s*$")
_PLAIN_OK = re.compile(  # reader-fact templates the script may keep without a reader (each was read in the 200-note sample)
    r"^(?:County [A-Z][\w .'-]+ (?:from|per) (?:the )?physical address|Operator: .+|HQ not established; federal establishment address is not asserted as HQ|"
    r"Founded \d{4}|ZIP not (?:captured|established)|Form 5500 sponsor is [^.]+\(PY\d{4}\)|"
    r"Street: \d.+|County [A-Z][\w .'-]+ from the physical address|HQ site only|Employee figure [\w-]+ per [\w ]+)\.?\s*$")
# markers that code reads on the ROW: validate.py:497 (parcel candidate queue), :1390 (Settling fact:), build_osha_ita.py:657 (tombstone), :668 (WARN)
_PIN = {"organizations": re.compile(r"Settling fact:"),
        "sites": re.compile(r"parcel candidate queue|tombstoned as duplicate of SITE-\d{6}|\bWARN\b")}
_PERSON = re.compile(r"\b(?:CEO|CFO|COO|CTO|President|Owner|Founder|Founder/CEO|Co-?founder|Vice President|VP|Mr\.|Mrs\.|Ms\.)\s+[A-Z][a-z]+(?:\s[A-Z]\.?)?\s[A-Z][a-z']+|\b[A-Z] [A-Z][a-z]+ [A-Z][a-z]+ (?:Jr|Sr|II|III)\.? (?:Trust|Estate)\b")


def _plain(s):
    return re.sub(r"_", " ", s)


def classify(text, ctx):
    """-> (disposition, kind, restated_text_or_None). ctx: dict(street_keys=set, exempt=bool)."""
    t = text.strip().lstrip("| ")
    if _PERSON.search(t):
        return "PERSON", "person-name", None  # stays on the row exactly as today; its text is NOT copied to the history file (§8)
    if _PIN[ctx.get("table", "sites")].search(t):
        return ("READER" if hits(t) else "KEEP"), "code-pinned", None
    m = _BAND.match(t)
    if m:
        parts = [p.strip() for p in m.group(4).split(";") if not re.fullmatch(r"R\d+\w*|single-establishment org", p.strip())]
        scope = "for this site" if m.group(1) == "site" else "for Ohio operations"
        parts = [re.sub(r"\bCY(\d{4})\b", r"calendar year \1", re.sub(r"\bPY(\d{4})\b", r"plan year \1", x)) for x in parts]
        src = re.sub(r"\bCY(\d{4})\b", r"calendar year \1", re.sub(r"\bPY(\d{4})\b", r"plan year \1", m.group(3)))
        return "RESTATE", "marker-band", f"Employee size band {m.group(2)} {scope}, from {src}: {', '.join(parts)}."
    m = _CERT.match(t)
    if m:
        names = ", ".join(_CERTNAME.get(c.strip(), _plain(c.strip()).upper() if c.strip().startswith(("iso", "iatf")) else _plain(c.strip()))
                          for c in m.group(3).split(";"))
        src = "the company's own site" if m.group(1) == "own site" else m.group(1)
        return "RESTATE", "marker-cert", f"Certifications listed by {src} (observed {m.group(2)}): {names}."
    if _CAPQ.match(t):
        what = _plain(_CAPQ.match(t).group(1)).strip()
        return "RESTATE", "marker-capability", f"Capability not covered by the standard process list: {what}."
    m = _STREET.match(t)
    if m:
        addr = m.group(3)
        key = atlas.street_key(re.split(r"\s\(|\.\s*$|;", addr)[0].rstrip(". "))
        if key and key in ctx.get("street_keys", ()):
            return "MOVE", "street-redundant", None  # the street_address column carries it; readers prefer the column
        if hits(addr):
            return "READER", "street-mixed", None
        return ("KEEP", "street-fact", None) if not hits(t) else ("READER", "street-mixed", None)
    m = re.match(r"^City[- ](?:level|grain)(?: only)?\.?\s*$", t)
    if m:
        return "RESTATE", "city-grain", "Address known to city level only."
    m = re.match(r"^CIK (\d+)\.?\s*$", t)
    if m:
        return "RESTATE", "cik", f"SEC registrant number (CIK) {m.group(1)}."
    m = _RING.match(t)
    if m:
        return "RESTATE", "ring-subtype", f"Business subtype: {_plain(m.group(2))}."
    m = re.match(r"^Direct parent \(unheld, name only\):\s*(.+?)\.*\s*$", t)
    if m:
        return "RESTATE", "parent-fact", f"Parent company (not itself in the Atlas): {m.group(1)}."
    m = re.match(r"^ECHO/FRS (1\d{11})\.?\s*$", t)
    if m:
        return "RESTATE", "frs-id", f"EPA facility registry ID {m.group(1)}."
    if re.search(r"\|[^|]*\|", t):
        return "MOVE", "table-dump", None
    if _MOVE_LEADS.match(t):
        return "MOVE", "pipeline-lead", None
    h = hits(t)
    if not h:
        return ("KEEP", "plain-listed", None) if _PLAIN_OK.match(t) else ("READER", "plain-unlisted", None)
    return "READER", "mixed-pipeline-words", None


# ---------------------------------------------------------------- taxonomy (what a piece IS), independent of disposition
_KINDS = [
    ("T1 creation line", r"^Created \d{4}|^Created in"),
    ("T2 harvest/staging wrapper", r"^Source: Grok|^Grok |^HQ city/county from representative|^Federal source|^L\d STRONG|^LF-[A-Z]{2}|Staged "),
    ("T3 verification/tier/NAICS history", r"^(?:Verified \d|Wave-\d|PASS \d|Pass \d|INTEGRATION PASS|\[Pass|NAICS corrected|Atlas Tier U|Tier (?:set|restated)|Field edits|Basis for tier|Association corroboration)"),
    ("T4 schema/vocabulary mapping", r"^Packet (?:entity|ownership)|per SCHEMA|s4\.4 enum"),
    ("T5 dedupe/merge/retire/fold", r"^\[Dedupe|RETIRED|folded into|duplicate (?:site )?(?:row )?of|merged into|re-?pointed|Freeze dedupe|No dedupe hit|hygiene sweep"),
    ("T6 structured marker (BAND/CERT/CAPABILITY)", r"^(?:BAND-SOURCE|CERT-SITE|CAPABILITY-QUEUE)"),
    ("T7 street recorded in notes", r"^Street"),
    ("T8 flag/caution to integrator or owner", r"(?:FLAG|flag for|Integrator note|flagged|BORDERLINE|do not conflate|do not promote|never silently|not merged)"),
    ("T9 correction/withdrawn claim", r"(?:corrected|superseded|wrong|NOT created|not created|was not used|NOT used|discarded|DISCARDED|contradicted)"),
    ("T10 source description/quote", r"['‘\"].{4,}['’\"]|^(?:Own site|Basis:|Company'?s own|Operator'?s own)"),
]
_KINDS = [(n, re.compile(rx)) for n, rx in _KINDS]


def kind_of(text):
    t = text.strip()
    for n, rx in _KINDS:
        if rx.search(t):
            return n
    return "T11 other plain fact"


_STREET_PHR = [re.compile(r"Street(?:\s+correct(?:ion|ed)[^:]{0,20})?(?:\s*\((?:per|from)[^)]*\))?:\s*(\d[^;|\n]{2,80})", re.I),
               re.compile(r"Address[^:]{0,60}match\):\s*(\d[^;|\n]{2,80})", re.I)]  # copy of build_osha_ita._STREET_PATS (the readers' own patterns)


def street_sentences(t):
    """Streets a site-notes reader could find in piece text: 'Street: X.' for what a `Street...:` phrase yields, else 'Address mentioned in the source: X.'"""
    out, seen = [], set()
    for rx in _STREET_PHR:
        for m in rx.finditer(t):
            raw = re.split(r"\s\(|\.\s*$", m.group(1))[0].strip().rstrip(".").strip()
            k = atlas.street_key(raw)
            if k and k not in seen: seen.add(k); out.append((m.start(), f"Street: {raw}."))
    for m in atlas.NOTES_STREET_RE.finditer(t):
        k = atlas.notes_candidate_key(m[0])
        if k and k not in seen: seen.add(k); out.append((m.start(), f"Address mentioned in the source: {m[0].strip()}."))
    return [x[1] for x in sorted(out)]


def split_note(note, ctx):
    """-> list of dicts(seq, text, disp, kind, restated)."""
    out = []
    for i, p in enumerate(pieces(note)):
        d, k, r = classify(p, ctx)
        if d == "RESTATE" and r and hits(r):
            d, k, r = "READER", k + "+restated-unclean", None
        if ctx.get("street_blank") and d in ("MOVE", "READER") and k != "code-pinned":
            ss = street_sentences(p)   # the row has no street column, so notes are the only street: it must stay readable by atlas.py / street_from_notes
            if ss and d == "MOVE": d, k, r = "RESTATE", "street-extracted", " ".join(ss)
            elif ss: k = "code-pinned-street"
        out.append({"seq": i, "text": p, "disp": d, "kind": k, "restated": r})
    return out


def tidy(text):
    """Row-side form of a kept piece: no leading '| ', no trailing ';', ends with a full stop. The verbatim piece lives in the history file."""
    t = text.strip().lstrip("| ").rstrip(";").rstrip()
    return t if t.endswith((".", "!", "?", ")", '"', "'")) else t + "."


def after_note(parts, decisions=None):
    """Row text after the split. decisions: {seq: ('KEEP'|'MOVE'|('RESTATE', text))} resolves READER pieces (a reader's call)."""
    decisions = decisions or {}
    row = []
    for p in parts:
        d, r = p["disp"], p["restated"]
        if d == "READER":
            dec = decisions.get(p["seq"])
            if dec is None:
                raise ValueError(f"unresolved READER piece {p['seq']}: {p['text'][:60]!r}")
            d, r = (dec, None) if isinstance(dec, str) else dec
        if d == "PERSON":
            row.append(p["text"].strip())      # verbatim: the history file holds nothing for this piece
        elif d == "KEEP":
            row.append(tidy(p["text"]))
        elif d == "RESTATE":
            row.append(r)
    return " ".join(row)
