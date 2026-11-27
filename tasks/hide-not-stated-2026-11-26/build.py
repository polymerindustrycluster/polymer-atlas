"""Build VALUE_VERDICTS.csv, VALUE_PAGES.csv and HOLDS.csv in this folder from the controller's 2026-11-26 adjudication (second-family/ADJUDICATION-hide.csv).
Usage: python3 -I tasks/hide-not-stated-2026-11-26/build.py PERSIST_DIR
PERSIST_DIR holds requote-all-2026-11-24/ (values.csv, value-pages-builder/) and the page store.
Scope: the NOT_STATED lines of the keys the adjudication says `withhold`, copied from the pack's values.csv in the pack's own format (an NOT_STATED line carries
no quote or offset, SCHEMA §4.24). Every `hold` line goes to HOLDS.csv with the adjudication's reason; nothing else is built here."""
import csv, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import value_basis as vb  # noqa: E402

csv.field_size_limit(10**9)
key = lambda r: (r["record_table"], r["record_id"], r["field"], r["value"])
HOLD_COLS = ["record_table", "record_id", "owner", "field", "value", "source", "reader_class", "second_family_class", "reason"]


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def adjudication():
    """-> (withhold lines, hold lines) of second-family/ADJUDICATION-hide.csv; one line per key, action withhold or hold."""
    adj = read(HERE / "second-family/ADJUDICATION-hide.csv")
    assert len({key(r) for r in adj}) == len(adj), "the adjudication has a duplicate key"
    assert {r["action"] for r in adj} == {"withhold", "hold"}, "action must be withhold or hold"
    return [r for r in adj if r["action"] == "withhold"], [r for r in adj if r["action"] == "hold"]


def verdict_lines(pack, withhold):
    """The pack's own NOT_STATED line for each withhold key, unchanged."""
    by_key = {key(r): r for r in read(pack / "values.csv")}
    out = []
    for a in withhold:
        r = by_key[key(a)]
        assert r["class"] == "NOT_STATED" and a["source"] == "values" and a["reader_class"] == "NOT_STATED", f"{key(a)}: not a pack NOT_STATED line"
        out.append(r)
    return out


def main():
    pages = Path(sys.argv[1])
    withhold, holds = adjudication()
    lines = verdict_lines(pages / "requote-all-2026-11-24", withhold)
    write(HERE / "VALUE_VERDICTS.csv", vb.VERDICT_COLS, lines)
    subprocess.run([sys.executable, "-I", str(pages / "requote-all-2026-11-24/value-pages-builder/build_value_pages.py"), str(pages),
                    str(HERE / "VALUE_VERDICTS.csv"), str(HERE / "VALUE_PAGES.csv")], check=True)
    write(HERE / "HOLDS.csv", HOLD_COLS, holds)
    print(f"{len(lines)} NOT_STATED lines (withhold), {len(holds)} holds")


if __name__ == "__main__":
    main()
