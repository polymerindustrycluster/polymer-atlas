"""Audit applied cells against backups; reconcile and repair note-log attribution."""
import csv
import json
from collections import Counter
from pathlib import Path

import build_edits as edits

ROOT, OUT = edits.ROOT, edits.OUT


def main():
    receipt = json.loads((OUT / "reconciliation.json").read_text(encoding="utf-8"))
    _, proposals = edits.read(edits.PROPOSALS.read_bytes())
    rules = {(r["field"], r["value"]): r for r in proposals}
    expected_logs, changed_cells, changed_rows = [], set(), set()
    for rel, original_hash in receipt["input_sha256"].items():
        current = ROOT / rel
        if rel not in receipt["output_sha256"]:
            assert edits.sha(current.read_bytes()) == original_hash, (rel, "unplanned edit")
            continue
        backup = OUT / "backups" / current.name
        raw = backup.read_bytes()
        assert edits.sha(raw) == original_hash
        assert edits.sha(current.read_bytes()) == receipt["output_sha256"][rel]
        header, original_rows = edits.read(raw)
        columns, rows = edits.read(current.read_bytes())
        kind = "sites" if current.name.startswith("sites_") else "organizations"
        key = "site_id" if kind == "sites" else "org_id"
        assert len(rows) == len(original_rows)
        expected_columns = list(header)
        if kind == "sites":
            for f in edits.FIELDS:
                expected_columns.insert(expected_columns.index(f) + 1, f + "_other_note")
        assert columns == expected_columns
        for old, new in zip(original_rows, rows):
            assert old[key] == new[key]
            for col in header:
                if col not in edits.FIELDS:
                    assert old[col] == new[col], (rel, old[key], col)
            for field in edits.FIELDS:
                note_col = field + "_other_note"
                expected, note, outcomes = edits.rewrite(old[field], "", field, kind, rules)
                assert new[field] == expected
                if kind == "sites":
                    assert new[note_col] == note
                for col in (field, note_col) if kind == "sites" else (field,):
                    if old.get(col, "") != new[col]:
                        changed_cells.add((rel, old[key], col))
                        changed_rows.add((rel, old[key]))
                for rule, status in outcomes:
                    if status != "changed":
                        continue
                    for col in (field, note_col) if kind == "sites" else (field,):
                        if col == note_col and edits.effective(rule) != "TO_NOTE":
                            continue
                        if old.get(col, "") != new[col]:
                            expected_logs.append(dict(zip(edits.LOG_FIELDS, [current.name, old[key], col,
                                old.get(col, ""), new[col], rule["proposal"], rule["value"]])))
    assert len(changed_cells) == receipt["changed_cells"]
    assert len(changed_rows) == receipt["changed_records"]
    _, existing = edits.read((OUT / "edits_log.csv").read_bytes())
    encode = lambda r: tuple(r[f] for f in edits.LOG_FIELDS)
    extra = Counter(map(encode, existing)) - Counter(map(encode, expected_logs))
    assert not (Counter(map(encode, expected_logs)) - Counter(map(encode, existing))), "missing log entry"
    assert all(row[2].endswith("_other_note") and
               edits.effective(rules[row[2].removesuffix("_other_note"), row[6]]) != "TO_NOTE"
               for row in extra), "unexpected log difference"
    if extra:
        with (OUT / "edits_log.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=edits.LOG_FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(expected_logs)
    print(f"NOTE_LOG_ATTRIBUTIONS_REMOVED={sum(extra.values())}")
    print(f"APPLICATION_AUDIT=PASS: {len(changed_rows)} edited records; {len(changed_cells)} changed cells; every input hash, output hash, header and untouched field checked")


if __name__ == "__main__":
    main()
