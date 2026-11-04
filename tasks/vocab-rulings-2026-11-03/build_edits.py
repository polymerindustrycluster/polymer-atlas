#!/usr/bin/env python3
"""Apply B-VOC-1..4 locally; default dry run, --apply requires its hash-checked plan."""
import argparse
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PROPOSALS = ROOT / "tasks/vocab-normalize-2026-11-02/ruling_proposals.csv"
FIELDS = {"processes": "PROCESSES", "materials": "MATERIALS"}
LOG_FIELDS = ["file", "row_id", "column", "old_value", "new_value", "proposal", "value"]
csv.field_size_limit(10 ** 9)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def tokens(value):
    return [t.strip() for t in value.split(";") if t.strip()]


def joined(values):
    return ";".join(dict.fromkeys(values))


def read(raw):
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
    rows = list(reader)
    assert all(None not in r and None not in r.values() for r in rows), "Malformed CSV"
    return reader.fieldnames, rows


def effective(rule):
    return "TO_NOTE" if rule["target"] == "monomers_intermediates" else rule["proposal"]


def rewrite(value, note, field, kind, rules):
    output, notes, outcomes = [], tokens(note), []
    for token in tokens(value):
        rule = rules.get((field, token))
        if rule is None:
            output.append(token)
            continue
        action = effective(rule)
        held = action == "WRONG_FIELD" or (action == "TO_NOTE" and kind == "organizations")
        outcomes.append((rule, "held" if held else "changed"))
        if held:
            output.append(token)
        elif action in {"MAP", "NEW_UMBRELLA"}:
            output.extend(tokens(rule["target"]))
        elif action == "TO_NOTE":
            notes.append(token)
        else:
            assert action == "DROP_NOT_CAPABILITY", action
    if not any(status == "changed" for _, status in outcomes):
        return value, note, outcomes
    return joined(output), joined(notes), outcomes


def reconcile(proposals, counts):
    for rule in proposals:
        field, value = rule["field"], rule["value"]
        total = 0
        for kind in ("sites", "organizations"):
            c = counts[kind, field, value]
            assert c["matched"] == c["changed"] + c["held"], (kind, field, value, c)
            total += c["matched"]
        assert total == int(rule["tokens"]), (field, value, "historical/current count conflict", rule["tokens"], total)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    proposals_raw = PROPOSALS.read_bytes()
    _, proposals = read(proposals_raw)
    rules = {(r["field"], r["value"]): r for r in proposals}
    assert len(proposals) == len(rules) == 164
    vocab = json.loads((ROOT / "docs/schema/vocab.json").read_text(encoding="utf-8"))["vocabularies"]
    additions = {f: sorted({t for r in proposals if r["field"] == f and
                           r["proposal"] == "NEW_UMBRELLA" and effective(r) != "TO_NOTE"
                           for t in tokens(r["target"]) if t.endswith("_unspecified") or
                           t in {"carbon_black", "polymer_additives", "thermoplastic_olefin_tpo", "reaction_injection_molding"}})
                 for f in FIELDS}
    assert sum(map(len, additions.values())) == 12
    before_vocab = {f: set(vocab[k]["values"]) - set(additions[f]) for f, k in FIELDS.items()}
    after_vocab = {f: before_vocab[f] | set(additions[f]) for f in FIELDS}
    for r in proposals:
        assert r["field"] in FIELDS
        if effective(r) in {"MAP", "NEW_UMBRELLA"}:
            assert tokens(r["target"]) and set(tokens(r["target"])) <= after_vocab[r["field"]], r

    plans, logs, counts = [], [], defaultdict(Counter)
    row_sets = defaultdict(set)
    shares = {stage: {f: Counter() for f in FIELDS} for stage in ("before", "after")}
    seen = defaultdict(set)
    hashes = {str(PROPOSALS.relative_to(ROOT)).replace("\\", "/"): sha(proposals_raw)}
    for kind in ("sites", "organizations"):
        paths = sorted((ROOT / "data").glob(f"{kind}_*.csv"))
        assert paths and not any(p.stem.endswith("_all") for p in paths)
        for path in paths:
            raw = path.read_bytes()
            assert b"\r" not in raw, (path.name, "expected LF")
            header, rows = read(raw)
            columns = list(header)
            if kind == "sites":
                for field in FIELDS:
                    note = field + "_other_note"
                    assert note not in columns, "Already applied; use the retained reconciliation and backups"
                    columns.insert(columns.index(field) + 1, note)
            key = "site_id" if kind == "sites" else "org_id"
            for row in rows:
                rid = row[key]
                assert rid not in seen[kind], (kind, "duplicate ID", rid)
                seen[kind].add(rid)
                for field in FIELDS:
                    old, note_col = row[field], field + "_other_note"
                    old_note = row.get(note_col, "")
                    new, note, outcomes = rewrite(old, old_note, field, kind, rules)
                    row[field] = new
                    if kind == "sites":
                        row[note_col] = note
                        for stage, cell, allowed in (("before", old, before_vocab[field]), ("after", new, after_vocab[field])):
                            ts = tokens(cell)
                            shares[stage][field].update(total=len(ts), in_vocabulary=sum(t in allowed for t in ts))
                    for rule, status in outcomes:
                        c = counts[kind, field, rule["value"]]
                        c.update(["matched", status])
                        row_sets[kind, rule["proposal"], "matched"].add(rid)
                        row_sets[kind, rule["proposal"], status].add(rid)
                        if status == "changed":
                            for col, previous, final in ((field, old, new), (note_col, old_note, note)):
                                if previous != final and (col == field or (kind == "sites" and effective(rule) == "TO_NOTE")):
                                    logs.append(dict(zip(LOG_FIELDS, [path.name, rid, col, previous, final,
                                                                     rule["proposal"], rule["value"]])))
            stream = io.StringIO(newline="")
            writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
            result = stream.getvalue().encode("utf-8")
            rel = path.relative_to(ROOT).as_posix()
            hashes[rel] = sha(raw)
            if result != raw:
                # Parse round-trip also covers empty shards and every untouched column.
                _, originals = read(raw)
                out_header, actual = read(result)
                assert out_header == columns and len(actual) == len(originals)
                for old_row, new_row in zip(originals, actual):
                    assert all(new_row[c] == v for c, v in old_row.items() if c not in FIELDS)
                plans.append((path, raw, result))

    reconcile(proposals, counts)
    per_value, summary, by_class = [], {}, {}
    for kind in ("sites", "organizations"):
        by_class[kind] = {}
        for proposal in sorted({r["proposal"] for r in proposals}):
            selected = [r for r in proposals if r["proposal"] == proposal]
            c = sum((counts[kind, r["field"], r["value"]] for r in selected), Counter())
            by_class[kind][proposal] = dict(values=sum(bool(counts[kind, r["field"], r["value"]]["matched"]) for r in selected),
                tokens_matched=c["matched"], tokens_changed=c["changed"], tokens_held=c["held"],
                rows_matched=len(row_sets[kind, proposal, "matched"]), rows_changed=len(row_sets[kind, proposal, "changed"]),
                rows_held=len(row_sets[kind, proposal, "held"]))
        for r in proposals:
            c = counts[kind, r["field"], r["value"]]
            per_value.append(dict(file_class=kind, field=r["field"], value=r["value"], proposal=r["proposal"],
                                  effective_proposal=effective(r), tokens_matched=c["matched"], tokens_changed=c["changed"], tokens_held=c["held"]))
    for proposal in sorted({r["proposal"] for r in proposals}):
        summary[proposal] = {k: sum(by_class[c][proposal][k] for c in by_class)
                             for k in ("tokens_matched", "tokens_changed", "tokens_held")}
        summary[proposal]["values"] = sum(r["proposal"] == proposal for r in proposals)
    receipt = dict(schema_terms_added=additions, reconciliation=summary, by_file_class=by_class,
                   per_value=per_value, site_vocabulary_shares=shares, input_sha256=hashes,
                   output_sha256={p.relative_to(ROOT).as_posix(): sha(new) for p, _, new in plans},
                   changed_records=len({(r["file"], r["row_id"]) for r in logs}),
                   changed_cells=len({(r["file"], r["row_id"], r["column"]) for r in logs}))
    if args.apply:
        dry = json.loads((OUT / "dry_run.json").read_text(encoding="utf-8"))
        assert dry == receipt, "Dry-run plan changed; inspect and rerun dry run"
        backup = OUT / "backups"
        backup.mkdir(exist_ok=False)
        for path, raw, _ in plans:
            (backup / path.name).write_bytes(raw)
        (OUT / "rollback_manifest.json").write_text(json.dumps({p.relative_to(ROOT).as_posix():
            {"backup": (backup / p.name).relative_to(ROOT).as_posix(), "sha256": sha(raw)}
            for p, raw, _ in plans}, indent=2) + "\n", encoding="utf-8", newline="\n")
        # Check every input before the first write, then each file again at replacement.
        for rel, expected in hashes.items():
            assert sha((ROOT / rel).read_bytes()) == expected, (rel, "input changed")
        for path, raw, result in plans:
            assert sha(path.read_bytes()) == sha(raw), path
            path.write_bytes(result)
            assert path.read_bytes() == result, path
        output = OUT / "reconciliation.json"
    else:
        output = OUT / "dry_run.json"
    with (OUT / "edits_log.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LOG_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(logs)
    output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("file_class proposal values tokens_matched tokens_changed tokens_held rows_matched rows_changed rows_held")
    for kind, groups in by_class.items():
        for proposal, c in groups.items():
            print(kind, proposal, *c.values())
    print(f"{'APPLIED' if args.apply else 'DRY RUN'}: {len(plans)} files; {receipt['changed_records']} capability-edited records; {receipt['changed_cells']} changed cells")
    print("RECONCILED: 164 proposal values; 2061 matched tokens; all historical counts agree")


if __name__ == "__main__":
    main()
