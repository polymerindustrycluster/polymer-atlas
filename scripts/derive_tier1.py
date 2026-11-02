#!/usr/bin/env python3
"""Refresh the derived ``tier1_qualifier`` / ``tier1_qualifier_basis`` columns
(SCHEMA §4.4 "Tier-1 qualifier derivation", AGENTS.md §1 "Derived fields are
hands-off").

The derivation rules are the binding ones in SCHEMA §4.4 and mirror
``derive_tier1_set`` in ``scripts/validate.py`` (V-29); the test suite checks
parity by running this script on a temp copy and asserting the validator then
reports zero V-29 drift.

  public_parent       stock_ticker non-empty, or a SEC_CIK / SEC_CIK_PARENT_FILER registry link
  tri_reporter        a TRI_TRIFID registry link
  employees_250plus   employee_band_ohio in {250-499, 500-999, 1000-4999, 5000+}
  national_footprint  held sites with operating_status != closed span >= 3 states

Modes
  (default)           check: report drift; exit 1 if any qualifier drift, else 0
  --packet DIR        also write DIR/changes.csv (one row per changed org: the
                      pass-journal list of changed rows SCHEMA §4.4 asks for)
  --write             apply in place. INTEGRATOR work (AGENTS.md §2 rule 7):
                      refuses the repository's real data/ unless
                      --i-am-the-integrator is passed. Rehearse on a copy:

    cp -r data /tmp/atlas_t1 && python3 scripts/derive_tier1.py --data-dir /tmp/atlas_t1 --write
    ATLAS_DATA_DIR=/tmp/atlas_t1 python3 scripts/validate.py

Basis clauses. A row is rewritten only when its qualifier set drifts (or, with
--refresh-basis, when a canonical basis clause is stale). In a rewritten row:
  * public_parent keeps its existing clause verbatim when the value persists
    (held clauses carry exchange/parent annotations the derivation cannot
    rebuild); a new public_parent clause is built canonically:
    ``stock_ticker=X + sec_cik=N + sec_cik_parent_filer=N (Filer Name)``;
  * the other three legs always get their canonical clause:
    ``tri_reporter: registry_links TRI_TRIFID``,
    ``employees_250plus: employee_band_ohio=<band>``,
    ``national_footprint: states=A,B,C (n)``.

Files round-trip byte-for-byte through the csv module (verified before any
write); only shard files with changed rows are rewritten; only the two derived
columns change. Stdlib only.
"""
import argparse
import csv
import io
import sys
from pathlib import Path

csv.field_size_limit(10 ** 9)

ROOT = Path(__file__).resolve().parent.parent
REAL_DATA = (ROOT / "data").resolve()
QUAL_ORDER = ["public_parent", "tri_reporter", "employees_250plus", "national_footprint"]
BIG_BANDS = {"250-499", "500-999", "1000-4999", "5000+"}
FILER_PREFIX = "edgar_ex21_subsidiary_of_filer:"
CHANGE_COLS = ["file", "org_id", "change_class", "old_tier1_qualifier", "new_tier1_qualifier",
               "old_tier1_qualifier_basis", "new_tier1_qualifier_basis", "inputs"]


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


class Shard:
    """One CSV file held in memory with exact round-trip."""

    def __init__(self, path):
        self.path = path
        raw = path.read_bytes()
        txt = raw.decode("utf-8")
        self.nl = "\r\n" if "\r\n" in txt else "\n"
        self.rows = list(csv.reader(io.StringIO(txt, newline="")))
        if self.serialize() != raw:
            die(f"{path.name}: does not round-trip byte-for-byte through csv; refusing to touch it")
        self.header = self.rows[0]
        self.col = {c: i for i, c in enumerate(self.header)}

    def serialize(self):
        out = io.StringIO(newline="")
        csv.writer(out, lineterminator=self.nl).writerows(self.rows)
        return out.getvalue().encode("utf-8")

    def dicts(self):
        for idx, row in enumerate(self.rows[1:], 1):
            yield idx, dict(zip(self.header, row))


def read_dicts(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def split_vals(s):
    return [x.strip() for x in (s or "").split(";") if x.strip()]


def basis_clauses(s):
    """'a: x; b: y' -> {'a': 'a: x', 'b': 'b: y'} (clauses start with their qualifier value)."""
    out = {}
    for cl in split_vals(s):
        key = cl.split(":", 1)[0].strip()
        out.setdefault(key, cl)
    return out


def load_context(data_dir):
    links, states = {}, {}
    for l in read_dicts(data_dir / "registry_links.csv"):
        links.setdefault(l["org_id"], []).append(l)
    for p in sorted(data_dir.glob("sites_*.csv")):
        for s in read_dicts(p):
            if s.get("operating_status") != "closed" and s.get("state"):
                states.setdefault(s["org_id"], set()).add(s["state"])
    return links, states


def derive(r, links, states):
    """Return (ordered qualifier values, {value: canonical clause}, inputs summary)."""
    vals, clauses = set(), {}
    oid = r["org_id"]
    olinks = links.get(oid, [])
    ticker = (r.get("stock_ticker") or "").strip()
    cik = sorted(l["registry_id"] for l in olinks if l["registry"] == "SEC_CIK")
    pf = sorted((l["registry_id"], l.get("match_basis") or "") for l in olinks if l["registry"] == "SEC_CIK_PARENT_FILER")
    if ticker or cik or pf:
        vals.add("public_parent")
        parts = ([f"stock_ticker={ticker}"] if ticker else []) + [f"sec_cik={c}" for c in cik]
        for c, mb in pf:
            name = mb[len(FILER_PREFIX):].strip() if mb.startswith(FILER_PREFIX) else ""
            parts.append(f"sec_cik_parent_filer={c}" + (f" ({name})" if name else ""))
        clauses["public_parent"] = "public_parent: " + " + ".join(parts)
    if any(l["registry"] == "TRI_TRIFID" for l in olinks):
        vals.add("tri_reporter")
        clauses["tri_reporter"] = "tri_reporter: registry_links TRI_TRIFID"
    band = (r.get("employee_band_ohio") or "").strip()
    if band in BIG_BANDS:
        vals.add("employees_250plus")
        clauses["employees_250plus"] = f"employees_250plus: employee_band_ohio={band}"
    st = sorted(states.get(oid, set()))
    if len(st) >= 3:
        vals.add("national_footprint")
        clauses["national_footprint"] = f"national_footprint: states={','.join(st)} ({len(st)})"
    inputs = f"employee_band_ohio={band or '(blank)'}; stock_ticker={ticker or '(blank)'}; " \
             f"sec_links={len(cik) + len(pf)}; tri_links={sum(1 for l in olinks if l['registry'] == 'TRI_TRIFID')}; " \
             f"active_states={len(st)}"
    return [v for v in QUAL_ORDER if v in vals], clauses, inputs


def plan(data_dir, refresh_basis=False):
    links, states = load_context(data_dir)
    shards = {p.name: Shard(p) for p in sorted(data_dir.glob("organizations_*.csv"))}
    changes, stale_basis = [], 0
    for fname, sh in shards.items():
        for c in ("org_id", "tier1_qualifier", "tier1_qualifier_basis"):
            if c not in sh.col:
                die(f"{fname}: missing column {c}")
        for idx, r in sh.dicts():
            old_q, old_b = r["tier1_qualifier"], r["tier1_qualifier_basis"]
            new_vals, canon, inputs = derive(r, links, states)
            held = basis_clauses(old_b)
            kept = {v: held[v] for v in ("public_parent",) if v in held and v in new_vals}
            new_b = "; ".join(kept.get(v, canon[v]) for v in new_vals)
            new_q = ";".join(new_vals)
            drift = set(split_vals(old_q)) != set(new_vals)
            if not drift and new_q == old_q and new_b != old_b:
                stale_basis += 1
                if not refresh_basis:
                    continue
                cls = "basis_refresh"
            elif drift:
                gained = set(new_vals) - set(split_vals(old_q))
                lost = set(split_vals(old_q)) - set(new_vals)
                cls = ";".join([f"gain:{v}" for v in QUAL_ORDER if v in gained] +
                               [f"lose:{v}" for v in QUAL_ORDER if v in lost])
            elif new_q != old_q:
                cls = "reorder"
            else:
                continue
            changes.append({"file": fname, "org_id": r["org_id"], "change_class": cls,
                            "old_tier1_qualifier": old_q, "new_tier1_qualifier": new_q,
                            "old_tier1_qualifier_basis": old_b, "new_tier1_qualifier_basis": new_b,
                            "inputs": inputs, "_idx": idx})
    return shards, changes, stale_basis


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--data-dir", default=str(REAL_DATA))
    ap.add_argument("--packet", metavar="DIR", help="write DIR/changes.csv")
    ap.add_argument("--write", action="store_true", help="apply the refresh in place (integrator only)")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    ap.add_argument("--refresh-basis", action="store_true",
                    help="also rewrite stale canonical basis clauses on rows whose qualifier set is unchanged")
    a = ap.parse_args(argv)
    data_dir = Path(a.data_dir).resolve()
    if not data_dir.is_dir():
        die(f"data dir not found: {data_dir}")
    if a.write and data_dir == REAL_DATA and not a.i_am_the_integrator:
        die("--write against the repository's data/ is integrator work (AGENTS.md §2 rule 7); "
            "pass --i-am-the-integrator, or point --data-dir at a copy to rehearse")

    shards, changes, stale_basis = plan(data_dir, a.refresh_basis)
    drift = [c for c in changes if c["change_class"] not in ("basis_refresh", "reorder")]
    by_class = {}
    for c in drift:
        for k in c["change_class"].split(";"):
            by_class[k] = by_class.get(k, 0) + 1
    total = sum(len(s.rows) - 1 for s in shards.values())
    print(f"tier1_qualifier derivation over {total} organization rows in {len(shards)} shards ({data_dir})")
    print(f"  organizations with qualifier drift: {len(drift)}")
    for k in sorted(by_class):
        print(f"    {k}: {by_class[k]}")
    print(f"  organizations with a stale canonical basis clause only: {stale_basis}"
          + ("" if a.refresh_basis else " (not rewritten; pass --refresh-basis)"))
    for c in changes:
        print(f"  {c['org_id']}  {c['file']}  {c['change_class']}  [{c['old_tier1_qualifier']}] -> [{c['new_tier1_qualifier']}]")

    if a.packet:
        out = Path(a.packet)
        out.mkdir(parents=True, exist_ok=True)
        with open(out / "changes.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=CHANGE_COLS, extrasaction="ignore", lineterminator="\n")
            w.writeheader()
            w.writerows(sorted(changes, key=lambda c: c["org_id"]))
        print(f"wrote {out / 'changes.csv'} ({len(changes)} rows)")

    if a.write:
        touched = set()
        for c in changes:
            sh = shards[c["file"]]
            row = sh.rows[c["_idx"]]
            row[sh.col["tier1_qualifier"]] = c["new_tier1_qualifier"]
            row[sh.col["tier1_qualifier_basis"]] = c["new_tier1_qualifier_basis"]
            touched.add(c["file"])
        for fname in sorted(touched):
            shards[fname].path.write_bytes(shards[fname].serialize())
        print(f"applied {len(changes)} row changes across {len(touched)} file(s): {', '.join(sorted(touched)) or '-'}")
        print("next: run scripts/validate.py (V-29 should report no drift); list the changed rows in the pass journal")
        return 0
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
