#!/usr/bin/env python3
"""Build public change Markdown and Atom from full main history; stdlib only.

    python3 scripts/build_changelog.py                 # local origin/main
    python3 scripts/build_changelog.py --ref main       # full local main checkout

Only build/changelog/ is written. Fetch full history before running in a shallow clone.
"""
import argparse
import csv
import io
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
REPO_URL = "https://github.com/polymerindustrycluster/polymer-atlas"
ATOM = "http://www.w3.org/2005/Atom"
KEYS = {
    "organizations": "org_id", "sites": "site_id", "ecosystem": "org_id", "evidence": "evidence_id",
    "registry_links": "org_id", "members": "member_row_id", "people": "person_id",
    "programs": "program_id", "events": "event_id", "event_participation": "participation_id",
    "relationships": "relationship_id", "site_capabilities": "capability_id",
    "equipment": "equipment_id", "people_engagement": "engagement_id",
    "people_identifiers": "person_id", "archive_links": "evidence_id",
    "ref_codes": "ref_code_id", "ref_code_map": "map_id", "code_assignments": "assignment_id",
}
# Same link grain as the row-loss guard; archive_links is one row per evidence_id (§4.22).
COMPOSITE = {
    "registry_links": ("org_id", "registry", "registry_id", "site_id"),
    "people_identifiers": ("person_id", "identifier_type", "identifier_id"),
}
STATUSES = {
    "active", "active_idled_partial", "idled", "closed", "acquired", "merged",
    "relocated_in_scope", "relocated_out_of_scope", "pre_revenue", "unknown",
    "superseded",
}
EVIDENCE_TABLES = {"organizations", "sites", "ecosystem", "programs", "people"}
ID = re.compile(r"[A-Z][A-Z0-9_]*-\d{6}")
ET.register_namespace("", ATOM)


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True).stdout


def table_of(path):
    stem = Path(path).stem
    if stem == "inclusion_log" or stem.endswith("_all"):
        return None
    table = "evidence" if stem.startswith("evidence_") else re.sub(r"_(?:[A-Z]{2}|INTL)$", "", stem)
    if table not in KEYS:
        raise ValueError(f"unsupported data CSV: {path}")
    return table


def read_rows(path, text):
    """Keep only keyed public metadata; never carry notes/names/claims into the feed."""
    table = table_of(path)
    if table is None:
        return []
    reader = csv.DictReader(io.StringIO(text), strict=True)
    if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
        raise ValueError(f"missing or repeated CSV header: {path}")
    required = {KEYS[table]} | set(COMPOSITE.get(table, ()))
    if table == "registry_links":
        required.discard("site_id")  # The optional site key was added after this table was introduced.
    if table == "evidence":
        required.add("record_table")
    if not required.issubset(reader.fieldnames):
        raise ValueError(f"missing key columns: {path}")
    out = []
    for row in reader:
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"malformed CSV row: {path}")
        ident = row[KEYS[table]]
        if not ID.fullmatch(ident):
            raise ValueError(f"invalid immutable ID: {path}")
        key = tuple(row.get(col, "") for col in COMPOSITE[table]) if table in COMPOSITE else (ident,)
        if table == "evidence" and row.get("record_table") not in EVIDENCE_TABLES:
            raise ValueError(f"unsupported evidence target table: {path}")
        projection = {
            "table": table, "id": ident,
            "status": row.get("operating_status", "") if table == "sites" else row.get("status", ""),
            "tier": row.get("verification_tier", ""),
            "evidence_table": row.get("record_table", "") if table == "evidence" else "",
        }
        out.append(((table, key), projection))
    return out


def snapshot(files):
    rows = {}
    for path in sorted(files):
        for key, row in files[path]:
            if key in rows and rows[key] != row:
                raise ValueError("conflicting duplicate keyed row in historical snapshot")
            rows[key] = row
    return rows


def keyed_diff(before, after, seen):
    created, restored, removed, status, tier = [], [], [], [], []
    evidence = Counter()
    added, deleted = after.keys() - before.keys(), before.keys() - after.keys()
    pairs = [(key, key) for key in before.keys() & after.keys()]
    # Historical ORG-ID collisions exist: match a cross-table transfer only if unique on BOTH sides.
    old_orgs, new_orgs = defaultdict(list), defaultdict(list)
    for rows, target in [(before, old_orgs), (after, new_orgs)]:
        for key, row in rows.items():
            if row["table"] in {"organizations", "ecosystem"}:
                target[row["id"]].append(key)
    for ident in old_orgs.keys() & new_orgs.keys():
        old, new = old_orgs[ident], new_orgs[ident]
        if len(old) == len(new) == 1 and old[0] != new[0]:
            added.discard(new[0]); deleted.discard(old[0])
            pairs.append((old[0], new[0]))
    for key in sorted(added):
        row = after[key]
        if key in seen:
            restored.append(row)
        elif row["table"] == "evidence":
            evidence[row["evidence_table"]] += 1
        else:
            created.append(row)
    for key in sorted(deleted):
        removed.append(before[key])
    for old_key, new_key in sorted(pairs):
        old, new = before[old_key], after[new_key]
        if old["status"] != new["status"]:
            status.append((new, old["status"], new["status"]))
        if old["tier"] != new["tier"]:
            tier.append((new, old["tier"], new["tier"]))
    return {"created": created, "restored": restored, "removed": removed,
            "status": status, "tier": tier, "evidence": evidence}


def history(repo, ref):
    if git(repo, "rev-parse", "--is-shallow-repository").strip() == "true":
        raise ValueError("full main history required; fetch --unshallow before generating")
    ref = git(repo, "rev-parse", "--verify", "--end-of-options", ref + "^{commit}").strip()
    commits = git(repo, "log", "--first-parent", "--reverse",
                  "--format=%H%x00%P%x00%cI%x00%s", ref).splitlines()
    if not commits:
        raise ValueError("main history is empty")
    files, before, seen, entries = {}, {}, set(), []
    for line in commits:
        sha, parents, date, subject = line.split("\0", 3)
        if parents:
            changes = git(repo, "diff-tree", "-r", "--no-commit-id", "--no-renames",
                          "--name-status", parents.split()[0], sha, "--", "data/").splitlines()
        else:
            changes = ["A\t" + p for p in git(repo, "ls-tree", "-r", "--name-only", sha, "data/").splitlines()]
        touched = False
        for change in changes:
            action, path = change.split("\t", 1)
            if not re.fullmatch(r"data/[^/]+\.csv", path) or table_of(path) is None:
                continue
            touched = True
            if action == "D":
                files.pop(path, None)
            else:
                files[path] = read_rows(path, git(repo, "show", f"{sha}:{path}"))
        if not touched:
            continue
        after = snapshot(files)
        diff = keyed_diff(before, after, seen)
        pr = re.match(r"Merge pull request #(\d+)\b", subject) or re.search(r"\(#(\d+)\)$", subject)
        entries.append({"sha": sha, "date": date, "pr": pr[1] if pr else None, **diff})
        seen.update(after)
        before = after
    return entries, commits[-1].split("\0", 1)[0], commits[-1].split("\0")[2]


def controlled(value, tier=False):
    if not value:
        return "(blank)"
    return value if value in ({"A", "B", "C", "U"} if tier else STATUSES) else "(unrecognized)"


def record_lines(label, rows):
    grouped = defaultdict(Counter)
    for row in rows:
        grouped[row["table"]][row["id"]] += 1
    lines = []
    for table, ids in sorted(grouped.items()):
        labels = [ident + (f" ({n} rows)" if n > 1 else "") for ident, n in sorted(ids.items())]
        lines.append(f"- {label} — {table}: {sum(ids.values())} keyed rows; " + ", ".join(labels))
    return lines


def entry_text(entry):
    lines = record_lines("Created", entry["created"])
    lines += record_lines("Restored, previously seen", entry["restored"])
    lines += record_lines("Removed from snapshot", entry["removed"])
    for field, label in [("status", "Status"), ("tier", "Verification tier")]:
        for row, old, new in entry[field]:
            lines.append(f"- {label} — {row['table']} {row['id']}: "
                         f"{controlled(old, field == 'tier')} → {controlled(new, field == 'tier')} "
                         "(1 existing keyed row change)")
    for table, count in sorted(entry["evidence"].items()):
        lines.append(f"- New evidence — {table}: {count} evidence rows (first-seen EVD IDs)")
    return "\n".join(lines) or "No keyed creations, restorations, removals, status/tier changes or new evidence rows."


def title(entry):
    return "PR #" + entry["pr"] if entry["pr"] else "Commit " + entry["sha"][:12] + " (no PR recorded)"


def build(repo, ref):
    repo = Path(repo).resolve()
    out = repo / "build/changelog"
    if not out.resolve().is_relative_to(repo / "build"):
        raise ValueError("output must stay under repository build/")
    entries, head, updated = history(repo, ref)
    intro = ("# Polymer Atlas change feed\n\n"
             f"Main snapshot: [{head[:12]}]({REPO_URL}/commit/{head}).\n\n"
             "Changes are recorded when a pull request reaches main; older direct updates are labelled by commit. "
             "Counts are distinct keyed rows or existing-row field changes, not companies or current operations. "
             "Shards and unique organization/ecosystem transfers preserve keys; historical cross-table ID collisions stay distinct. Restorations are not first-time creations. "
             "Evidence counts are grouped by target record table. Composite-link rows share their owner ID label. "
             "Other field edits, inclusion_log and generated *_all exports are outside this feed. "
             "Only IDs and controlled values are published; unknown legacy values are redacted.\n\n")
    sections = []
    feed = ET.Element(f"{{{ATOM}}}feed")
    def child(parent, tag, text=None, **attrs):
        el = ET.SubElement(parent, f"{{{ATOM}}}{tag}", attrs)
        el.text = text
        return el
    child(feed, "id", REPO_URL + "#data-change-feed")
    child(feed, "title", "Polymer Atlas changes")
    child(feed, "updated", updated)
    child(child(feed, "author"), "name", "Polymer Industry Cluster")
    child(feed, "link", href=REPO_URL + "/tree/main/data", rel="alternate")
    for entry in reversed(entries):
        link = REPO_URL + ("/pull/" + entry["pr"] if entry["pr"] else "/commit/" + entry["sha"])
        body = entry_text(entry)
        sections.append(f"## {entry['date'][:10]} — [{title(entry)}]({link})\n\n{body}\n")
        atom = child(feed, "entry")
        child(atom, "id", REPO_URL + "/commit/" + entry["sha"])
        child(atom, "title", "Atlas changes — " + title(entry))
        child(atom, "updated", entry["date"])
        child(atom, "link", href=link, rel="alternate")
        child(atom, "content", body, type="text")
    out.mkdir(parents=True, exist_ok=True)
    (out / "CHANGELOG.md").write_text(intro + "\n".join(sections), encoding="utf-8")
    ET.indent(feed)
    ET.ElementTree(feed).write(out / "feed.xml", encoding="utf-8", xml_declaration=True)
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default="origin/main", help="local full main ref (default: origin/main)")
    args = parser.parse_args()
    entries = build(ROOT, args.ref)
    print(f"change feed: {len(entries)} data-history entries -> build/changelog/CHANGELOG.md and feed.xml")


if __name__ == "__main__":
    main()
