#!/usr/bin/env python3
"""Mint the ruled registry links (owner battery 2026-11-01 R10/R11) from the federal-data packets.

    python3 tasks/registry-links-2026-11-02/build_links.py --data-dir <dir>                 # write new_links.csv + holds.csv
    python3 tasks/registry-links-2026-11-02/build_links.py --data-dir data --apply --i-am-the-integrator

Rules (every ID is read from the source system's own extract or record, so none is
a phantom, AGENTS.md section 4):
  FRS      echo-frs-spine site_matches.csv, verdict MATCH_SITE with match_strength
           strong or strong_id_corroborated_name_differs; org-keyed with site_id (R10).
           moderate (name + zip, street unknown) matches are held.
  EIN      form5500-spine matches.csv, MATCH_ORG with match_step 2+3 (name + street on
           one of the org's sites), the R11 mint rule; organizations table only.
  UEI      federal-leads matches.csv, source USASPENDING_UEI, link_candidate Y.
  FDA_FEI  federal-leads matches.csv, source OPENFDA_FEI, link_candidate Y.
A candidate whose org or site is no longer held, or whose (org, registry, id) is
already linked, goes to holds.csv. --apply adds the optional site_id column (R10)
to registry_links.csv when missing and appends the new rows; existing rows keep
their bytes apart from the added trailing empty field.
"""
import argparse, csv, io, sys
from pathlib import Path

csv.field_size_limit(10 ** 9)
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
T = ROOT / "tasks"
COLS = ["org_id", "registry", "registry_id", "match_basis", "as_of", "site_id"]


def read(p):
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def build(data):
    orgs = {r["org_id"]: r for p in data.glob("organizations_*.csv") for r in read(p)}
    eco = {r["org_id"] for r in read(data / "ecosystem.csv")}
    sites = {r["site_id"]: r for p in data.glob("sites_*.csv") for r in read(p)}
    held = {(r["org_id"], r["registry"], r["registry_id"]) for r in read(data / "registry_links.csv")}
    new, holds, seen = [], [], set()

    def add(src, row, why_hold=None):
        key = (row["org_id"], row["registry"], row["registry_id"], row.get("site_id", ""))
        if why_hold:
            holds.append({**row, "source": src, "reason": why_hold}); return
        if row["org_id"] not in orgs and row["org_id"] not in eco:
            holds.append({**row, "source": src, "reason": "org not held"}); return
        if row.get("site_id"):
            s = sites.get(row["site_id"])
            if not s:
                holds.append({**row, "source": src, "reason": "site not held"}); return
            if s["org_id"] != row["org_id"]:
                holds.append({**row, "source": src, "reason": f"site now belongs to {s['org_id']}"}); return
        if key[:3] in held:
            holds.append({**row, "source": src, "reason": "already linked"}); return
        if key in seen:
            return
        seen.add(key); new.append({**row, "source": src})

    for m in read(T / "echo-frs-spine-2026-11-01" / "site_matches.csv"):
        if m["verdict"] != "MATCH_SITE":
            continue
        row = {"org_id": m["proposed_registry_links_row_org_id"], "registry": "FRS", "registry_id": m["proposed_registry_id"],
               "match_basis": m["proposed_match_basis"], "as_of": m["proposed_as_of"], "site_id": m["site_id"]}
        ok = m["match_strength"] in ("strong", "strong_id_corroborated_name_differs")
        add("echo-frs-spine", row, None if ok else f"match_strength {m['match_strength']} (held for review)")
    for m in read(T / "form5500-spine-2026-11-01" / "matches.csv"):
        if m["match_class"] != "MATCH_ORG":
            continue
        row = {"org_id": m["org_id"], "registry": "EIN", "registry_id": m["ein"],
               "match_basis": f"form5500_sponsor_name+site_street_py{m['plan_year']}", "as_of": "2026-11-01", "site_id": ""}
        if m["match_step"] != "2+3":
            continue  # name/state only: not mint-ready under R11 (not a hold, a non-candidate)
        add("form5500-spine", row, None if m["matched_table"] == "organizations" else "R11 mints on organizations only")
    for m in read(T / "federal-leads-2026-11-01" / "matches.csv"):
        if m["link_candidate"] != "Y":
            continue
        reg = {"USASPENDING_UEI": "UEI", "OPENFDA_FEI": "FDA_FEI"}[m["source"]]
        basis = "usaspending_exact_uei" if reg == "UEI" else "openfda_establishment_exact_fei"
        add("federal-leads", {"org_id": m["atlas_ids"].strip(), "registry": reg, "registry_id": m["source_id"],
                              "match_basis": basis, "as_of": "2026-11-01", "site_id": ""})
    return new, holds


def apply(data, new):
    path = data / "registry_links.csv"
    raw = path.read_bytes(); txt = raw.decode("utf-8")
    nl = "\r\n" if "\r\n" in txt else "\n"
    rows = list(csv.reader(io.StringIO(txt, newline="")))
    buf = io.StringIO(newline=""); csv.writer(buf, lineterminator=nl).writerows(rows)
    if buf.getvalue() != txt:
        sys.exit("registry_links.csv does not round-trip through csv; refusing to rewrite it")
    if "site_id" not in rows[0]:
        rows = [rows[0] + ["site_id"]] + [r + [""] for r in rows[1:]]
    hdr = rows[0]
    rows += [[n.get(c, "") for c in hdr] for n in new]
    buf = io.StringIO(newline=""); csv.writer(buf, lineterminator=nl).writerows(rows)
    path.write_text(buf.getvalue(), encoding="utf-8", newline="")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    a = ap.parse_args()
    data = Path(a.data_dir).resolve()
    if a.apply and data == (ROOT / "data").resolve() and not a.i_am_the_integrator:
        sys.exit("applying to the real data/ is integrator work (AGENTS.md section 2 rule 7)")
    new, holds = build(data)
    if a.apply:
        apply(data, new)
        print(f"appended {len(new)} links to {data / 'registry_links.csv'}")
        return
    with open(OUT / "new_links.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS + ["source"], lineterminator="\n"); w.writeheader(); w.writerows(new)
    with open(OUT / "holds.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS + ["source", "reason"], lineterminator="\n"); w.writeheader(); w.writerows(holds)
    from collections import Counter
    print("new:", dict(Counter(n["registry"] for n in new)), "| holds:", dict(Counter(h["reason"].split(" (")[0] for h in holds)))


if __name__ == "__main__":
    main()
