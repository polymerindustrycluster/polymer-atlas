#!/usr/bin/env python3
"""Scan every user-facing text surface for process and build wording (ATLAS-40, the lexicon pass).

    python3 tasks/site-lexicon-2026-11-23/scan.py PAGES_DIR RELEASE_DIR OUT_DIR

The wide watch list (PROCESS_WATCH_RE) is applied to description text only (the lede paragraph of a page, JSON fields d, desc and
description_1line, release description_1line); on other text only the strict lists apply (build prose, the blind-audit scan, CRM,
temporary ids), because the site's own labels use words such as "tier" and "verified" on purpose.

Surfaces: record-specific text of every built HTML page (text that sits on 25 or more pages is the shared template and is skipped),
every string value of every built JSON file, every cell of the built CSV downloads, and the description_1line and notes columns of
the release CSVs and the bundled SQLite copy. A hit is a match of the build-prose list, the wider watch list, the blind-audit scan or a
temporary id (all from scripts/build_site.py). Status SHOWN = the text is published; ALLOWED:<reason> = an ordinary use named in
PROSE_ALLOW. Notes cells are counted in HITS_notes.csv, one row per cell, because the release carries notes as the repository CSV does.
Writes HITS.csv, HITS_notes.csv and COUNTS.md to OUT_DIR.
"""
import collections
import csv
import html
import json
import re
import sqlite3
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import build_site as b  # noqa: E402

csv.field_size_limit(10**9)
TEMPLATE_MIN_FILES = 25
STRICT = [b.BUILD_PROSE_RE, b.INTERNAL_RE, b.CRM_RE, b.TEMP_ANY_RE]
DESC_FIELDS = {"d", "desc", "description_1line", "lede"}


# Words that the strict lists hit in fields that are not descriptions: the site's own labels, and names, addresses and URLs.
# Each is recorded as ALLOWED with its reason. Descriptions are never matched against this list.
LABEL_ALLOW = [
    (re.compile(r"\b(?:verification )?tiers? [A-CU](?:-C)?\b|\bLast verified\b|\bverification tiers?\b|\bverified\b", re.I), "the site's own verification-tier and last-verified labels"),
    (re.compile(r"[A-Za-z][^\s]*\b(?:council|gemini|claude|wave|battery|held|lane|pass|staging|pr|owner)\b[^\s]*|\b(?:council|gemini|claude|wave|battery|held|lane|pass|staging|owner)\b", re.I),
     "a company, person, place, street or URL name, or the market name energy (renewables & battery); the blind-audit scan is word-based"),
    (re.compile(r"#\d+"), "a suite, unit or street number in an address"),
    (re.compile(r"https?://\S+|\b[\w.-]+\.(?:com|org|net|edu|gov)\S*|\b\w*_\w*\b|[\w.-]*/[\w./%-]+\.(?:pdf|html?)\b|[\w-]+-[\w-]+\.(?:pdf|html?)\b"), "a URL or a vocabulary token (energy_renewables_battery): a name, not prose"),
    (re.compile(r",? PR \d{5}|\bPR\d?\b|MONTEREY PASS[- ]?|Monterey Pass[- ]?", re.I), "a Puerto Rico address or street name"),
    (re.compile(r"\bnotes\b|\bother[ _]specified[ _]in[ _]notes\b", re.I), "the vocabulary label 'other (specified in the record's notes, which are not published)'"),
]


def hits(text, wide=False):
    """(phrase, status) for every net match in text; ALLOWED when the match lies inside a PROSE_ALLOW span."""
    text = str(text or "")
    spans = [(m.start(), m.end(), why) for rx, why in b.PROSE_ALLOW for m in rx.finditer(text)]
    out, seen = [], set()
    for rx in STRICT + ([b.PROCESS_WATCH_RE] if wide else []):
        for m in rx.finditer(text):
            key = (m.start(), m.group(0).lower())
            if key in seen:
                continue
            seen.add(key)
            why = next((w for a, z, w in spans if a <= m.start() and m.end() <= z), None)
            if not why and not wide:
                why = next((w for rx2, w in LABEL_ALLOW if rx2.search(text[max(0, m.start() - 40):m.end() + 40]) and any(
                    a2.start() <= m.start() - max(0, m.start() - 40) and m.end() - max(0, m.start() - 40) <= a2.end()
                    for a2 in rx2.finditer(text[max(0, m.start() - 40):m.end() + 40]))), None)
            out.append((m.group(0), f"ALLOWED:{why}" if why else "SHOWN"))
    return out


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.nodes, self.skip, self.stack = [], 0, []

    def handle_starttag(self, tag, attrs):
        self.skip += tag in ("script", "style")
        if tag != "br":
            self.stack.append(tag == "p" and "lede" in (dict(attrs).get("class") or "").split())

    def handle_endtag(self, tag):
        self.skip -= tag in ("script", "style")
        if self.stack and tag != "br":
            self.stack.pop()

    def handle_data(self, data):
        t = " ".join(data.split())
        if t and not self.skip:
            self.nodes.append((t, any(self.stack)))


def page_nodes(pages):
    per_file = {}
    count = collections.Counter()
    for f in sorted(pages.rglob("*.html")):
        p = Text()
        p.feed(f.read_text(encoding="utf-8", errors="replace"))
        per_file[f] = p.nodes
        count.update({n for n, _ in p.nodes})
    for f, nodes in per_file.items():
        rec = f.stem if f.parent.name == "orgs" else str(f.relative_to(pages))
        for n, lede in nodes:
            if count[n] < TEMPLATE_MIN_FILES:
                yield "page", rec, "lede" if lede and f.parent.name == "orgs" else "text", n   # a record page's lede is the record's description; a site page's lede is site copy


def walk(obj, path, rec):
    if isinstance(obj, dict):
        rec = obj.get("id") or obj.get("org_id") or rec
        for k, v in obj.items():
            yield from walk(v, f"{path}.{k}", rec)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{path}[{i}]", rec)
    elif isinstance(obj, str):
        yield path, rec, obj


def json_strings(pages):
    for f in sorted(pages.rglob("*.json")):
        name = str(f.relative_to(pages))
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        for path, rec, v in walk(data, "", None):
            yield f"json:{name}", rec or path.split(".")[1] if "." in path else name, path.rsplit(".", 1)[-1], v


def csv_cells(pages):
    for f in sorted(pages.glob("*.csv")):
        with f.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        for r in rows[1:]:
            for h, v in zip(rows[0], r):
                yield f"csv:{f.name}", r[0], h, v


def release_cells(release):
    for f in sorted((release / "data").glob("*.csv")):
        with f.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        for i, h in enumerate(rows[0]):
            if h in ("description_1line", "notes"):
                for r in rows[1:]:
                    yield f"release-csv:{f.name}", r[0], h, r[i] if i < len(r) else ""
    con = sqlite3.connect(release / "polymer-atlas.db")
    for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall():
        cols = [r[1] for r in con.execute(f'PRAGMA table_info("{t}")')]
        for c in ("description_1line", "notes"):
            if c in cols:
                for k, v in con.execute(f'SELECT "{cols[0]}", "{c}" FROM "{t}" WHERE "{c}" IS NOT NULL'):
                    yield f"release-sqlite:{t}", k, c, v


def main(pages, release, out):
    pages, release, out = Path(pages), Path(release), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rows, notes = [], []
    for stream in (page_nodes(pages), json_strings(pages), csv_cells(pages), release_cells(release)):
        for surface, rec, field, text in stream:
            if not isinstance(text, str) or not text:
                continue
            found = hits(text, wide=field in DESC_FIELDS or (field == 'description_1line'))
            if not found:
                continue
            if field == "notes":
                notes.append((surface, rec, "; ".join(sorted({p.lower() for p, _ in found}))))
                continue
            for phrase, status in found:
                i = text.lower().find(phrase.lower())
                rows.append((surface, rec, field, phrase.lower(), status, text[max(0, i - 40):i + len(phrase) + 40].replace("\n", " ")))
    with (out / "HITS.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["surface", "record", "field", "phrase", "status", "snippet"])
        w.writerows(sorted(set(rows)))
    with (out / "HITS_notes.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["surface", "record", "phrases"])
        w.writerows(sorted(set(notes)))
    per = collections.defaultdict(collections.Counter)
    for surface, rec, field, phrase, status, _ in set(rows):
        per[surface.split(":")[0] + (":" + surface.split(":")[1] if surface.startswith(("json", "csv")) else "")][status.split(":")[0]] += 1
    lines = ["# Lexicon scan counts", "", "Hits are (surface, record, field, phrase) rows; SHOWN = published, ALLOWED = an ordinary use named in PROSE_ALLOW.", "",
             "| Surface | SHOWN | ALLOWED |", "|---|---|---|"]
    for s in sorted(per):
        lines.append(f"| {s} | {per[s]['SHOWN']} | {per[s]['ALLOWED']} |")
    nc = collections.Counter(s.split(":")[0] + ":" + s.split(":")[1].split("_")[0] if ":" in s else s for s, _, _ in set(notes))
    lines += ["", "Notes cells with at least one hit (not withheld by design; see README):", ""] + [f"- {k}: {v}" for k, v in sorted(nc.items())]
    (out / "COUNTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main(*sys.argv[1:4])
