"""Adapt Audit 11's blind row, pinned record lookup and leak scan to Audit 12's draw."""
import argparse
import csv
from collections import Counter, defaultdict
import io
import json
from pathlib import Path
import random
import re
import sys
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / name) for name in (
    "blind-audit-12-protocol-2026-11-23", "blind-audit-11-2026-11-17")]
import draw
import sample as a11

FIELDS = ("blind_id", "stratum", "table", "record_id", "record_label", "columns_under_audit",
          "values_json", "context_json", "cited_sources", "evidence_json")
CHILDREN = {
    "registry_links": ("org_id", "site_id"),
    "site_capabilities": ("org_id", "site_id"),
    "equipment": ("host_org_id", "site_id", "program_id"),
    "people_identifiers": ("person_id",),
    "people_engagement": ("person_id",),
    "code_assignments": ("org_id",),
    "members": ("org_id",),
}
LINKS = {
    **dict.fromkeys(("org_id", "parent_org_id", "institution_org_id", "parent_institution_org_id",
                    "program_org_id", "successor_org_id", "organizer_org_id", "host_org_id"), "organizations"),
    "site_id": "sites", "program_id": "programs", "event_id": "events", "person_id": "people",
}
LABEL = dict(organizations="legal_name", ecosystem="legal_name", sites="site_name",
             people="full_name", programs="program_name", events="name", event_participation="edition_name")
EXTRA_LEAK = re.compile(r'\b(?:gate[_ -]?verdict|reader[_ -]?family|reviewer[_ -]?(?:family|label)|'
                        r'tier[_ -]?history|last_verified|claim_detail|source_class|'
                        r'READ_REQUIRED|UNINSPECTABLE|web_proof_replayed)\b', re.I)
CONTACT = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|"
                     r"\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b")


def csv_rows(text):
    return list(csv.DictReader(io.StringIO(text, newline="")))


def record_key(row):
    return row["table"], row["record_id"]


def unique(rows, key):
    result = {}
    for row in rows:
        name = key(row)
        if name in result:
            raise ValueError("duplicate record key")
        result[name] = row
    return result


def read_draw(folder):
    receipt = json.loads((folder / "draw_receipt.json").read_text())
    tables = []
    for name in ("frame.csv", "sample.csv", "plants.csv"):
        body = (folder / name).read_bytes()
        if draw.sha(body) != receipt["files"][name]:
            raise ValueError(f"{name} differs from draw receipt")
        tables.append(csv_rows(body.decode("utf-8")))
    frame, sample, plants = tables
    frame = unique(frame, record_key)
    sampled = unique(sample, record_key)
    planted = unique(plants, record_key)
    if sampled.keys() & planted.keys():
        raise ValueError("plant overlaps the sample")
    counts = Counter(r["stratum"] for r in frame.values())
    if counts != receipt["reconciliation"]["frame_by_stratum"]:
        raise ValueError("frame counts do not reconcile with receipt")
    for row in sample:
        original = frame.get(record_key(row))
        if original is None or row["stratum"] != original["stratum"]:
            raise ValueError("sample disagrees with frame")
    for s in draw.STRATA:
        n = counts[s]
        n1, n2 = (receipt["plan"][s][k] for k in ("n1", "n2"))
        census = n <= n2
        group = sorted((r for r in sample if r["stratum"] == s), key=lambda r: int(r["rank"]))
        expected = [(i, "1" if census or i <= n1 else "2") for i in range(1, min(n, n2) + 1)]
        if ([(int(r["rank"]), r["stage"]) for r in group] != expected
                or any(int(r["stratum_N"]) != n or r["census"] != str(census).lower() for r in group)):
            raise ValueError(f"{s}: sample size or stage differs from the draw plan")
    if Counter(r["stratum"] for r in plants) != dict.fromkeys(draw.STRATA, draw.PLANT_PER_STRATUM):
        raise ValueError("plant counts differ from the draw plan")
    for row in sample + plants:
        if row["table"] not in draw.STRATUM_TABLES[row["stratum"]]:
            raise ValueError("ineligible table for stratum")
    return receipt, frame, sample, plants


def records_for_stage(sample, extend):
    for row in sample:
        if (not extend and row["stage"] == "1") or (row["stage"] == "2" and row["stratum"] in extend):
            yield row


def cited(value):
    value = a11.READ_DATE.sub(" ", value).replace("( )", "").replace("()", "").strip()
    return " ".join(a11.urls(value)) if a11.LEAK.search(value) or a11.PASS_DATE.search(value) else value


class Head(a11.Head):
    """Use the draw reader for Audit 12 tables and Audit 11's indexed blind-row contract."""

    def __init__(self, reader):
        self.t = {t: {key: [row] for key, row in unique(reader.rows(t), lambda r: r[c]).items()}
                  for t, c in draw.ID_COL.items()}
        self.orgs = {key: row[0] for t in ("organizations", "ecosystem") for key, row in self.t[t].items()}
        self.evidence, self.children = defaultdict(list), defaultdict(list)
        self.ev_by_id = unique(reader.rows("evidence"), lambda r: r["evidence_id"])
        for row in self.ev_by_id.values():
            self.evidence[row["record_table"], row["record_id"]].append(row)
        for table, parents in CHILDREN.items():
            for row in reader.rows(table):
                keys = {(LINKS[f], row[f]) for f in parents if row[f]}
                for t, key in sorted(keys):
                    if t == "organizations" and key in self.t["ecosystem"]:
                        t = "ecosystem"
                    self.children[t, key].append(self.child(table, row))
        archives = unique(reader.rows("archive_links"), lambda r: (r["evidence_id"], r["archive_ref"]))
        for (eid, _), row in archives.items():
            ev = self.ev_by_id[eid]
            child = self.child("archive_links", row)
            child["context"]["cited_page_urls"] = a11.urls(ev["source_ref"])
            self.children[ev["record_table"], ev["record_id"]].append(child)

    def label(self, table, row):
        return row[LABEL[table]]

    def context(self, table, row, audit):
        context = {}
        for field, kind in draw.FIELD_CLASS[table].items():
            if kind == "K" and field not in ("sources", draw.ID_COL.get(table)) and row[field]:
                context[field] = cited(row[field]) if field.endswith(("_ref", "_source")) else row[field]
            target = LINKS.get(field)
            if not target or kind not in ("J", "K") or field == draw.ID_COL.get(table) or not row[field]:
                continue
            related = (self.orgs.get(row[field]) if target == "organizations"
                       else self.t[target].get(row[field], [None])[0])
            if related:
                context[field + "_resolved"] = related[LABEL[target]]
        return context

    def child(self, table, row):
        values = {f: row[f] for f, k in draw.FIELD_CLASS[table].items() if k == "J"}
        return dict(table=table, values=values, context=self.context(table, row, values))


def leak_scan(rows):
    for row in rows:
        if row.keys() != set(FIELDS):
            raise ValueError("blind header contains unexpected fields")
        # Audit 11 scans the same payload. Scan child claims as values so published claim dates stay eligible.
        context = json.loads(row["context_json"])
        children = context.pop("children", [])
        if any(child.keys() != {"table", "values", "context"}
               or child["table"] not in {*CHILDREN, "archive_links"} for child in children):
            raise ValueError("blind child contains unexpected fields")
        evidence = json.loads(row["evidence_json"])
        if any(ev.keys() != {"claim_type", "url"} for ev in evidence):
            raise ValueError("blind evidence contains unexpected fields")
        for child in [{"table": row["table"], "values": json.loads(row["values_json"]),
                       "context": context}, *children]:
            classes = draw.FIELD_CLASS[child["table"]]
            if child["values"].keys() != {f for f, k in classes.items() if k == "J"}:
                raise ValueError("blind values differ from the judged field list")
            allowed = {f for f, k in classes.items() if k == "K"}
            allowed |= {f + "_resolved" for f in LINKS.keys() & classes.keys() if classes[f] in ("J", "K")}
            if child["table"] == "archive_links":
                allowed.add("cited_page_urls")
            if child["context"].keys() - allowed:
                raise ValueError("blind context contains unexpected fields")
            scope = dict(row, change_class=row["stratum"], change_kind="",
                         values_json=json.dumps(child["values"], ensure_ascii=False),
                         context_json=json.dumps(child["context"], ensure_ascii=False))
            if child.get("table") == "archive_links":
                # This is the public archive link key (the same exception as Audit 11).
                scope["context_json"] = json.dumps({k: v for k, v in child["context"].items() if k != "evidence_id"})
                if not a11.ARCHIVE_KEY.fullmatch(child["context"]["evidence_id"] + "|" + child["values"]["archive_ref"]):
                    raise ValueError(f"{row['blind_id']}: malformed archive link key")
            hits = a11.leak_scan([scope])
            if hits:
                raise ValueError(f"{row['blind_id']}: blind scan flagged {hits[0][1]}")
            for field in FIELDS:
                if EXTRA_LEAK.search(unquote(scope[field])) or CONTACT.search(unquote(scope[field])):
                    raise ValueError(f"{row['blind_id']}: blind scan flagged {field}")


def build(folder, out, reader=None, extend=()):
    receipt, frame, sample, plants = read_draw(folder)
    if reader is None:
        if receipt["plan"] != draw.sealed_plan():
            raise ValueError("receipt plan differs from sealed sizes")
        reader = draw.GitReader(draw.require_ancestor(receipt["at"]))
    if hasattr(reader, "placements"):
        placements = reader.placements()
        assigned = {rid: r["stratum"] for (t, rid), r in frame.items() if t in ("organizations", "ecosystem")}
        for rid, (stratum, _) in placements.items():
            if (rid in assigned if stratum == "EXCLUDED" else assigned.get(rid) != stratum):
                raise ValueError("pinned B6 placements disagree with the draw frame")
    rows = list(records_for_stage(sample, extend))
    if extend and set(extend) != {r["stratum"] for r in rows}:
        raise ValueError("each requested extension must have stage-2 rows")
    if not extend:
        rows += plants
    stage = 2 if extend else 1
    # The public SHA and release list seed only the presentation order.
    random.Random(draw.sha(f"{receipt['at']}|{stage}|{','.join(sorted(extend))}".encode())).shuffle(rows)
    h = Head(reader)
    blind, private = [], []
    suffix = "-".join(sorted(extend))
    prefix = f"A12-S{stage}" + (f"-{suffix}" if suffix else "")
    for i, entry in enumerate(rows, 1):
        table, rid = record_key(entry)
        original = h.t[table][rid][0]
        record = original
        judge = [f for f, k in draw.FIELD_CLASS[table].items() if k == "J"]
        if "field" in entry:
            field, donor = entry["field"], entry["donor_record_id"]
            replacement = h.t[table][donor][0].get(field)
            if field not in judge or not replacement or not original[field] or replacement == original[field]:
                raise ValueError("invalid plant substitution")
            record = dict(original, **{field: replacement})
        # Audit 11 uses its changed-column path here, supplied with the entire explicit J whitelist.
        h.t[table][rid][0] = record
        row = a11.blind_row(h, dict(entry, change_kind="audit", change_class=entry["stratum"],
                                   changed_columns=";".join(judge)))
        h.t[table][rid][0] = original
        context = json.loads(row["context_json"])
        context["children"] = h.children[table, rid]
        row.update(blind_id=f"{prefix}-{i:04}", stratum=entry["stratum"],
                   context_json=json.dumps(context, ensure_ascii=False, sort_keys=True))
        row["cited_sources"] = cited(row["cited_sources"])
        # Audit 11's generic withheld list also includes a few columns that are J for specific Audit 12 tables.
        row.update(columns_under_audit=";".join(judge),
                   values_json=json.dumps({f: record[f] for f in judge}, ensure_ascii=False, sort_keys=True))
        blind.append({f: row[f] for f in FIELDS})
        private.append(dict(blind_id=row["blind_id"], stratum=entry["stratum"], table=table, record_id=rid,
                            plant_field=entry.get("field", "")))
    leak_scan(blind)
    out.mkdir(mode=0o700)
    packet = draw.csv_text(blind, FIELDS)
    for name in ("blind_a.csv", "blind_b.csv"):
        draw.write_private(out / name, packet)
    draw.write_private(out / "private_map.csv", draw.csv_text(private, list(private[0])))
    print(f"{len(blind)} reader rows, SHA-256 {draw.sha(packet.encode())}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draw", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--extend", nargs="+", choices=draw.STRATA, default=[])
    args = parser.parse_args()
    try:
        build(args.draw, args.out, extend=args.extend)
    except ValueError as exc:
        parser.exit(1, f"packet build refused: {exc}\n")
    except (KeyError, OSError) as exc:
        parser.exit(1, f"packet build refused ({type(exc).__name__})\n")


if __name__ == "__main__":
    main()
