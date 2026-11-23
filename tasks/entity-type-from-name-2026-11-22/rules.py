"""entity_type from the legal name's final suffix. One rule, used by build.py and check.py.

Fills ONLY an unambiguous legal-form suffix at the very end of legal_name:
  LLC form   -> llc          (LLC, L.L.C., Limited Liability Company)
  LP form    -> partnership  (LP, L.P., LLP, L.L.P., LLLP, Limited [Liability] Partnership)
  corporation form -> corporation   (Inc, Inc., Incorporated, Corp, Corp., Corporation)  [owner ruling 2026-11-22, "Add 'corporation'"]
`corporation` is the plain value added to the SCHEMA §4.4 enum at v1.19.4: a suffix does not say public or private, so public
or private is never guessed. Co, Company, Ltd and Limited stay unknown (they do not identify a corporation: an Ohio LLC may use
Ltd). Co/Company inside the name ("Smith & Co., Inc.") is a name word, not a second form.
Everything else is held."""
import re

US = {"US", "USA", "UNITED STATES", "UNITED STATES OF AMERICA"}
LLC_END = re.compile(r"^(?P<stem>.+?)[\s,]+(?P<suf>l\.?\s?l\.?\s?c\.?|limited\s+liability\s+company)\s*$", re.I)
LP_END = re.compile(r"^(?P<stem>.+?)[\s,]+(?P<suf>l\.?\s?l\.?\s?l\.?\s?p\.?|l\.?\s?l\.?\s?p\.?|l\.?\s?p\.?|limited\s+partnership|"
                    r"limited\s+liability\s+partnership)\s*$", re.I)
CORP_FILL = re.compile(r"^(?P<stem>.+?)[\s,]+(?P<suf>inc\.?|incorporated|corp\.?|corporation)\s*$", re.I)
CORP_END = re.compile(r"[\s,]+(inc|inc\.|incorporated|corp|corp\.|corporation|co|co\.|company|ltd|ltd\.|limited|plc|"
                      r"gmbh|ag|s\.?a\.?|b\.?v\.?|n\.?v\.?|s\.?r\.?l\.?|s\.?p\.?a\.?|k\.?k\.?|pty|sas|a/s|oy|ab)\s*$", re.I)
# other legal-form words anywhere in the name = conflicting forms; markers of a second name = dba forms
FORM_WORDS = {"inc", "incorporated", "corp", "corporation", "co", "company", "ltd", "limited", "llc", "lp", "llp", "lllp",
              "plc", "gmbh", "ag", "sa", "bv", "nv", "srl", "spa", "kk", "pty", "sas", "partnership", "partners"}
DBA = re.compile(r"\b(d/?b/?a|doing\s+business\s+as|a/?k/?a|f/?k/?a|formerly|c/o|t/a|trading\s+as)\b|[()/]", re.I)


def words(s):
    return re.findall(r"[a-z0-9]+", s.lower())


NAME_WORDS = {"co", "company"}


def classify(r):
    """(value or '', category, suffix as printed) for one organizations row. value is set only for category 'fill'."""
    name = " ".join((r["legal_name"] or "").split())
    country = (r["hq_country"] or "").strip().upper()
    corp = CORP_END.search(name)
    m = LLC_END.match(name) or LP_END.match(name)
    if DBA.search(name):
        return "", "held_dba_form", ""
    if not m:
        c = CORP_FILL.match(name)
        if c:
            stem, suf = c.group("stem"), c.group("suf")
            if (set(words(stem)) & FORM_WORDS) - NAME_WORDS:
                return "", "held_conflicting_forms", suf
            if (country and country not in US) or (not country and not r["hq_state"].strip()):
                return "", "held_foreign_or_unplaced", suf
            if r["stock_ticker"].strip():
                return "", "held_ticker_conflict", suf
            if r["entity_type"] not in ("", "unknown"):
                return "", ("already_this" if r["entity_type"] == "corporation" else "existing_corporation_value"), suf
            return "corporation", "fill", suf
        if corp and {"llc", "lp", "llp", "lllp"} & set(words(name)):
            return "", "held_conflicting_forms", corp.group(1)
        return "", ("held_corporate_suffix" if corp else "held_no_suffix"), (corp.group(1) if corp else "")
    stem, suf = m.group("stem"), m.group("suf")
    value = "llc" if LLC_END.match(name) else "partnership"
    if set(words(stem)) & FORM_WORDS:
        return "", "held_conflicting_forms", suf
    if (country and country not in US) or (not country and not r["hq_state"].strip()):
        return "", "held_foreign_or_unplaced", suf
    if r["stock_ticker"].strip():
        return "", "held_ticker_conflict", suf
    if r["entity_type"] not in ("", "unknown"):
        return "", ("already_this" if r["entity_type"] == value else "conflict_existing_value"), suf
    return value, "fill", suf
