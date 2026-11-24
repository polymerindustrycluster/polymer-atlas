#!/usr/bin/env python3
"""Verify every shard and account for every pre-pass capability value."""
import argparse
import csv
import io
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = "d69c4099dd08ecf7a14f762e3328718438bb0fe9"
FIELDS = ("processes", "materials")
NOTES = {f + "_other_note" for f in FIELDS}

sys.path.insert(0, str(ROOT / "scripts"))
from export_vocab import literal_constants


def git(*args):
    return subprocess.check_output(
        ["env", "-u", "GH_TOKEN", "-u", "GITHUB_TOKEN", "git", "-C", str(ROOT), *args],
        text=True,
    )


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def read(text):
    reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
    rows = list(reader)
    require(all(None not in r and None not in r.values() for r in rows), "Malformed CSV")
    return reader.fieldnames, rows


def replay_cell(before, after, field, allowed, counts, label):
    note = field + "_other_note"
    old = [v for v in before[field].split(";") if v.strip()]
    kept = [v for v in old if v.strip() in allowed]
    carried = {v.strip() for v in kept}
    notes = before.get(note, "")
    moves = []
    debt = 0
    for value in old:
        if value.strip() in allowed:
            counts["kept"] += 1
            continue
        debt += 1
        parts = re.split(r",|\band\b", value, flags=re.IGNORECASE)
        encoded = [
            re.sub(r"[ /-]", "_", re.sub(r" \(secondary\)$", "", p.lower().strip()))
            for p in parts
        ]
        if set(encoded) <= allowed:
            counts["exact re-encoded"] += 1
            for token in encoded:
                if token not in carried:
                    kept.append(token)
                    carried.add(token)
        else:
            counts["moved verbatim"] += 1
            moves.append(value)
    expected_tokens = ";".join(kept) if debt else before[field]
    expected_note = notes
    if debt:
        expected_note = ";".join(dict.fromkeys((notes.split(";") if notes else []) + moves))
    require(after[field] == expected_tokens, f"{label}: {field} lost or added a token")
    require(after[note] == expected_note, f"{label}: {note} lost or added verbatim wording")


def check(inject_drop):
    constants = literal_constants()
    paths = set(git("ls-tree", "--name-only", BASE, "data/").splitlines())
    require(paths == {str(p.relative_to(ROOT)) for p in (ROOT / "data").iterdir()},
            "Data file set differs from the pre-pass tree")
    targets = sorted(p for p in paths if Path(p).name.startswith(("organizations_", "sites_")))
    require(set(git("diff", "--name-only", BASE, "--", "data/").splitlines()) <= set(targets),
            "Out-of-scope data file changed")
    seen_ids = set()
    pre_debt, post_debt = set(), set()
    repaired = set()
    totals = Counter()
    changes = Counter()
    actions = Counter()
    for path in targets:
        table = Path(path).name.split("_")[0]
        id_col = "org_id" if table == "organizations" else "site_id"
        header, old = read(git("show", f"{BASE}:{path}"))
        next_header, new = read((ROOT / path).read_bytes().decode())
        expected_header = []
        for col in header:
            expected_header.append(col)
            if table == "organizations" and col in FIELDS:
                expected_header.append(col + "_other_note")
        require(next_header == expected_header, f"{path}: unexpected columns or column order")
        totals[table, "shards"] += 1
        totals[table, "rows"] += len(old)
        require([r[id_col] for r in old] == [r[id_col] for r in new],
                f"{path}: row count, IDs or order changed")
        for before, after in zip(old, new, strict=True):
            rid = before[id_col]
            label = f"{path} {rid}"
            require(rid not in seen_ids, f"Duplicate record ID {rid}")
            seen_ids.add(rid)
            require(all(before[f] == after[f] for f in set(header) - NOTES - set(FIELDS)),
                    f"{label}: unrelated cell changed")
            ring3 = before["ring_primary"].strip() == "3"
            row_changed = False
            for field in FIELDS:
                note = field + "_other_note"
                ordinary = constants[field.upper()]
                scoped = constants["RING3_PROCESSES"] if field == "processes" else set()
                allowed = ordinary | scoped if ring3 else ordinary
                old_values = {v.strip() for v in before[field].split(";") if v.strip()}
                new_values = {v.strip() for v in after[field].split(";") if v.strip()}
                if old_values - ordinary:
                    pre_debt.add(rid)
                if new_values - allowed:
                    post_debt.add(rid)
                actions[table, field, "Ring 3 admitted"] += len(old_values & new_values & scoped) if ring3 else 0

                changed = (before[field] != after[field] or before.get(note, "") != after[note])
                if changed:
                    row_changed = True
                    per_cell = Counter()
                    if inject_drop and after[note] and after[note] != before.get(note, ""):
                        after[note] = after[note].rpartition(";")[0]
                        print(f"Injected loss in {label} {note}", flush=True)
                        inject_drop = False
                    replay_cell(before, after, field, allowed, per_cell, label)
                    for action, n in per_cell.items():
                        actions[table, field, action] += n
                else:
                    require(old_values <= allowed, f"{label}: off-vocabulary {field} remained")
            if row_changed:
                repaired.add(rid)
                changes[table] += 1
    require(not inject_drop, "Could not inject a dropped value")
    require(not post_debt, f"V-55 residual: {sorted(post_debt)}")
    require(repaired <= pre_debt, f"Vocabulary edits on unrelated rows: {sorted(repaired - pre_debt)}")
    baseline_path = "scripts/validate_debt_baseline.json"
    baseline = json.loads(git("show", f"{BASE}:{baseline_path}"))["rules"]["V-55"]
    require(len(pre_debt) == 2884 and pre_debt == set(baseline),
            f"Pre-pass V-55 census ({len(pre_debt)} records) does not match the debt baseline")
    require(not json.loads((ROOT / baseline_path).read_text())["rules"]["V-55"],
            "V-55 baseline still contains IDs")
    for table in sorted(changes):
        print(f"{table}: {totals[table, 'rows']} rows in {totals[table, 'shards']} shards; "
              f"{changes[table]} rows with capability or other-note value changes")
        for field in FIELDS:
            print(f"  {field}: " + ", ".join(
                f"{actions[table, field, action]} {action}"
                for action in ("kept", "exact re-encoded", "moved verbatim", "Ring 3 admitted")
            ))
    print(f"V-55 records: {len(pre_debt)} before, {len(post_debt)} after; "
          f"{len(repaired)} repaired, {len(pre_debt - repaired)} cleared by Ring 3 admission alone")
    print("PASS: all changed rows accounted for, shard IDs/counts stable, unrelated cells unchanged")


def check_normalization():
    from build import repair

    standard = {"injection_molding", "blow_molding", "mold_tool_making", "tooling_repair_maintenance"}
    raw = "Injection molding, BLOW-MOLDING and mold/tool making (secondary);tooling_mold_die (secondary);Product wording and blow molding"
    row = {"processes": raw, "processes_other_note": "Existing note"}
    repair(row, "processes", standard)
    require(row == {
        "processes": "injection_molding;blow_molding;mold_tool_making",
        "processes_other_note": "Existing note;tooling_mold_die (secondary);Product wording and blow molding",
    }, "Exact-normalization or verbatim-preservation fixture failed")
    repair(row, "processes", standard)
    require(row["processes_other_note"].count("Product wording") == 1, "Repeated note after replay")
    row = {"processes": "tooling_mold_die (secondary)"}
    repair(row, "processes", standard | {"tooling_mold_die"})
    require(row == {"processes": "tooling_mold_die", "processes_other_note": ""},
            "Ring 3 suffix-normalization fixture failed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inject-drop", action="store_true", help="delete one migrated value in memory")
    check_normalization()
    check(parser.parse_args().inject_drop)
