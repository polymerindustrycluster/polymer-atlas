#!/usr/bin/env python3
"""Field-fill profile of the canonical CSVs. Stdlib only.

Reads data/*.csv directly (union of per-state shards for organizations and
sites) and writes a Markdown report: per-table row counts and per-column fill
rates, key-field fill by state, evidence coverage, enum distributions and a
vocabulary / must-have sanity check. Every figure names its unit and filter
(AGENTS.md section 7).

Read-only with respect to data/. Usage:
    python3 scripts/profile_fields.py --out docs/reviews/FIELD_FILL_PROFILE_2026-11-01.md
"""
import argparse
import csv
import datetime
import glob
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

SHARDED = {"organizations": "org_id", "sites": "site_id", "evidence": "evidence_id"}
SINGLE = [
    "ecosystem", "programs", "people", "members", "events",
    "event_participation", "relationships", "site_capabilities",
    "registry_links", "inclusion_log", "code_assignments", "ref_codes",
    "ref_code_map",
]
# unit label used for row counts / fill rates ("<unit>, <filter>")
UNIT = {
    "organizations": "organization rows (parent orgs)",
    "sites": "site rows (establishments)",
    "ecosystem": "ecosystem rows (Ring 5 entities)",
    "programs": "program rows",
    "people": "people rows (professors / federal-lab research staff)",
    "members": "PIC member-list rows",
    "events": "event-series rows",
    "event_participation": "event-participation rows",
    "evidence": "evidence rows",
    "relationships": "relationship edge rows",
    "site_capabilities": "site-capability rows",
    "registry_links": "registry-link rows",
    "inclusion_log": "inclusion-log rows",
    "code_assignments": "code-assignment rows",
    "ref_codes": "reference-code rows",
    "ref_code_map": "code-concordance rows",
}

SITE_KEY = [
    ("street_address", None), ("latitude", None), ("naics_primary", None),
    ("naics_primary_source_type", None), ("processes", None),
    ("materials", None), ("markets_served", None),
    ("employee_band_site", "unknown"), ("ring_primary", None),
    ("county", None),
]
ORG_KEY = [
    ("website", None), ("naics_primary", None), ("processes", None),
    ("materials", None), ("markets_served", None),
    ("employee_band_ohio", "unknown"), ("entity_type", "unknown"),
    ("ownership_type", "unknown"), ("year_founded", None),
]

PIC12 = {"ashtabula", "cuyahoga", "geauga", "lake", "lorain", "mahoning",
         "medina", "portage", "stark", "summit", "trumbull", "wayne"}

# Enum-like columns to tabulate (only those with <= ENUM_MAX distinct values
# are printed in full).
ENUM_MAX = 40
ENUM_COLS = {
    "sites": ["site_type", "operating_status", "verification_tier",
              "ring_primary", "naics_primary_source_type", "naics_confidence",
              "county_source", "geocode_precision", "employee_band_site",
              "country"],
    "organizations": ["entity_type", "ownership_type", "status",
                      "verification_tier", "ring_primary", "ring_secondary",
                      "naics_primary_source_type", "naics_confidence",
                      "employee_band_ohio", "hq_country",
                      "diversified_conglomerate", "hq_in_scope", "pic_member",
                      "monitor_watch", "liveness_signal"],
    "ecosystem": ["ecosystem_subtype", "status", "verification_tier",
                  "record_grain", "polymer_program", "pic_member"],
    "programs": ["program_type", "level", "status", "verification_tier",
                 "cip_source_type"],
    "people": ["verification_tier", "role"],
    "events": ["event_format", "cadence", "status", "verification_tier"],
    "event_participation": ["role", "verification_tier"],
    "evidence": ["record_table", "claim_type", "source_class", "tier_effect"],
    "relationships": ["relationship_type", "basis"],
    "site_capabilities": ["capability_type", "provenance"],
    "registry_links": ["registry", "match_basis"],
    "members": ["member_tier", "record_class"],
}

# Vocabularies as written in docs/SCHEMA.md (sections 2.1, 4.1, 4.2, 4.4, 4.5)
# at the time this script was written; a mismatch here may mean the schema was
# revised after this script, not necessarily bad data.
VOCAB = {
    "sites": {
        "site_type": {"manufacturing_plant", "hq_only", "hq_and_plant",
                      "rd_center", "lab_testing", "warehouse_distribution",
                      "sales_office", "tool_shop", "recycling_facility",
                      "training_center", "campus", "virtual_incubator"},
        "operating_status": {"active", "active_idled_partial", "idled",
                             "closed", "acquired", "merged",
                             "relocated_in_scope", "relocated_out_of_scope",
                             "pre_revenue", "unknown"},
        "verification_tier": {"A", "B", "C", "U"},
        "ring_primary": {"1", "2", "3", "4", "5"},
        "naics_primary_source_type": {"directory_assigned",
                                      "company_disclosed",
                                      "government_filing",
                                      "researcher_inferred"},
        "county_source": {"parcel", "physical_address", "geocoder_centroid",
                          "directory"},
        "geocode_precision": {"rooftop", "parcel", "address_interpolated",
                              "zip_centroid", "city_centroid"},
        "employee_band_site": {"1-9", "10-49", "50-99", "100-249", "250-499",
                               "500-999", "1000-4999", "5000+", "unknown"},
    },
    "organizations": {
        "entity_type": {"corporation_public", "corporation_private", "llc",
                        "partnership", "sole_proprietor", "nonprofit",
                        "government", "academic", "cooperative", "unknown"},
        "ownership_type": {"public_company", "private_company",
                           "private_equity_portfolio", "family_owned",
                           "employee_owned", "nonprofit", "government",
                           "academic", "cooperative", "unknown"},
        "status": {"active", "active_idled_partial", "idled", "closed",
                   "acquired", "merged", "relocated_in_scope",
                   "relocated_out_of_scope", "pre_revenue", "unknown"},
        "verification_tier": {"A", "B", "C", "U"},
        "ring_primary": {"1", "2", "3", "4", "5"},
        "naics_primary_source_type": {"directory_assigned",
                                      "company_disclosed",
                                      "government_filing",
                                      "researcher_inferred"},
        "employee_band_ohio": {"1-9", "10-49", "50-99", "100-249", "250-499",
                               "500-999", "1000-4999", "5000+", "unknown"},
    },
}
# fields that are blank-tolerant in the vocabulary check
VOCAB_BLANK_OK = {
    ("sites", "county_source"), ("sites", "geocode_precision"),
    ("sites", "naics_primary_source_type"), ("sites", "employee_band_site"),
    ("organizations", "ownership_type"), ("organizations", "employee_band_ohio"),
    ("organizations", "naics_primary_source_type"),
}

# MUST fields (SCHEMA 4.4 / 4.5) checked for blanks.
MUST = {
    "sites": ["site_id", "org_id", "site_name", "site_type", "city", "state",
              "ring_primary", "operating_status", "sources",
              "verification_tier", "last_verified"],
    "organizations": ["org_id", "legal_name", "entity_type", "ring_primary",
                      "hq_city", "hq_state", "hq_country", "status",
                      "sources", "verification_tier", "last_verified"],
}


def git(*args):
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return ""


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        cols = rdr.fieldnames or []
        return cols, list(rdr)


def load_all():
    tables, shard_info = {}, {}
    for t in SHARDED:
        cols, rows, per = None, [], {}
        header_variants = set()
        for fp in sorted(glob.glob(str(DATA / f"{t}_*.csv"))):
            c, r = read_csv(fp)
            header_variants.add(tuple(c))
            cols = cols or c
            per[Path(fp).stem[len(t) + 1:]] = len(r)
            rows.extend(r)
        tables[t] = (cols, rows)
        shard_info[t] = (per, len(header_variants))
    for t in SINGLE:
        tables[t] = read_csv(DATA / f"{t}.csv")
    return tables, shard_info


def filled(v, excl=None):
    v = (v or "").strip()
    return bool(v) and (excl is None or v.lower() != excl)


def pct(n, d):
    return f"{100.0 * n / d:.1f}%" if d else "n/a"


def cell(n, d):
    return f"{n:,}/{d:,} ({pct(n, d)})"


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join("---" for _ in header) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def key_label(col, excl):
    return col if excl is None else f"{col} (non-empty and != {excl})"


def breakdown(rows, state_field, keys, top_n=15):
    """Key-field fill by state: top_n states by rows + all other + total."""
    by_state = defaultdict(list)
    for r in rows:
        by_state[(r.get(state_field) or "").strip() or "(blank)"].append(r)
    ranked = sorted(by_state, key=lambda s: (-len(by_state[s]), s))
    top = ranked[:top_n]
    other = [r for s in ranked[top_n:] for r in by_state[s]]
    groups = [(s, by_state[s]) for s in top]
    if other:
        groups.append((f"all other ({len(ranked) - top_n} states/values)", other))
    groups.append(("ALL", rows))
    header = [state_field, "rows"] + [key_label(c, e) for c, e in keys]
    table = []
    for name, rs in groups:
        n = len(rs)
        table.append([name, f"{n:,}"] +
                     [pct(sum(1 for r in rs if filled(r.get(c), e)), n)
                      for c, e in keys])
    return md_table(header, table)


def fill_counts(rows, col, excl=None):
    return sum(1 for r in rows if filled(r.get(col), excl))


def evidence_index(ev_rows):
    idx = defaultdict(set)  # record_table -> set(record_id)
    for r in ev_rows:
        idx[r["record_table"]].add(r["record_id"])
    return idx


def evidence_coverage(rows, idcol, table, idx):
    ids = idx.get(table, set())
    by_tier = defaultdict(lambda: [0, 0])
    for r in rows:
        t = (r.get("verification_tier") or "").strip() or "(blank)"
        by_tier[t][0] += 1
        if r[idcol] not in ids:
            by_tier[t][1] += 1
    return by_tier


def counter_table(counter, total, label):
    rows = [[f"`{k}`" if k != "" else "*(blank)*", f"{v:,}", pct(v, total)]
            for k, v in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))]
    return md_table([label, "rows", "% of rows"], rows)


def build_report(args):
    tables, shard_info = load_all()
    orgs_cols, orgs = tables["organizations"]
    sites_cols, sites = tables["sites"]
    ev_cols, ev = tables["evidence"]
    ev_idx = evidence_index(ev)

    head = git("rev-parse", "HEAD") or "(unavailable)"
    dirty = git("status", "--porcelain", "--", "data")
    date = args.date

    # ---- numbers used by the gaps section
    ns, no = len(sites), len(orgs)
    f_sites = lambda c, e=None: fill_counts(sites, c, e)
    f_orgs = lambda c, e=None: fill_counts(orgs, c, e)
    oh_sites = [r for r in sites if r["state"] == "OH"]
    non_oh_sites = [r for r in sites if r["state"] != "OH"]
    oh_orgs = [r for r in orgs if r["hq_state"] == "OH"]
    pic12_sites = [r for r in oh_sites
                   if r["county"].replace(" County", "").strip().lower() in PIC12]
    ev_sites = evidence_coverage(sites, "site_id", "sites", ev_idx)
    ev_orgs = evidence_coverage(orgs, "org_id", "organizations", ev_idx)
    zero_s = sum(v[1] for v in ev_sites.values())
    zero_o = sum(v[1] for v in ev_orgs.values())
    zero_s_ab = sum(ev_sites[t][1] for t in ("A", "B"))
    zero_o_ab = sum(ev_orgs[t][1] for t in ("A", "B"))
    n_s_ab = sum(ev_sites[t][0] for t in ("A", "B"))
    n_o_ab = sum(ev_orgs[t][0] for t in ("A", "B"))
    naics_no_src = sum(1 for r in sites if filled(r["naics_primary"])
                       and not filled(r["naics_primary_source_type"]))
    naics_filled = f_sites("naics_primary")
    inferred = sum(1 for r in sites
                   if r["naics_primary_source_type"] == "researcher_inferred")
    org_naics_filled = f_orgs("naics_primary")
    org_naics_no_src = sum(1 for r in orgs if filled(r["naics_primary"])
                           and not filled(r["naics_primary_source_type"]))

    def sub(rows, c, e=None):
        return fill_counts(rows, c, e), len(rows)

    # states with lowest coordinate fill among states with >= 50 site rows
    coord_by_state = defaultdict(lambda: [0, 0])
    for r in sites:
        s = r["state"] or "(blank)"
        coord_by_state[s][1] += 1
        coord_by_state[s][0] += filled(r["latitude"])
    weakest = sorted((s for s, v in coord_by_state.items() if v[1] >= 50),
                     key=lambda s: coord_by_state[s][0] / coord_by_state[s][1])[:3]
    weakest_txt = ", ".join(
        f"{s} {pct(*coord_by_state[s])} of {coord_by_state[s][1]:,}"
        for s in weakest)
    prec = Counter(r["geocode_precision"] for r in sites if filled(r["latitude"]))

    gaps = []
    gaps.append(
        f"**Markets served is nearly empty.** `markets_served` is filled on "
        f"{cell(*sub(sites, 'markets_served'))} site rows (all tiers, all "
        f"statuses) and {cell(*sub(oh_sites, 'markets_served'))} Ohio site rows "
        f"({cell(*sub(pic12_sites, 'markets_served'))} PIC-12-county site rows); "
        f"on organization rows it is {cell(*sub(orgs, 'markets_served'))}. A "
        f"cluster user cannot yet filter the base by end market.")
    gaps.append(
        f"**Employee size is largely missing.** `employee_band_site` is "
        f"informative (non-empty, not `unknown`) on "
        f"{cell(*sub(sites, 'employee_band_site', 'unknown'))} site rows, "
        f"{cell(*sub(oh_sites, 'employee_band_site', 'unknown'))} Ohio site rows; "
        f"`employee_band_ohio` on "
        f"{cell(*sub(orgs, 'employee_band_ohio', 'unknown'))} organization rows "
        f"(all tiers, all statuses). Size-based targeting (e.g. 50+ employee "
        f"plants) is not possible for most of the base.")
    gaps.append(
        f"**Capabilities (processes / materials) are thin outside the "
        f"headline fields.** `processes` is filled on "
        f"{cell(*sub(sites, 'processes'))} site rows and `materials` on "
        f"{cell(*sub(sites, 'materials'))} (all tiers, all statuses); "
        f"for Ohio site rows `processes` is "
        f"{cell(*sub(oh_sites, 'processes'))} and `materials` "
        f"{cell(*sub(oh_sites, 'materials'))}, versus "
        f"{cell(*sub(non_oh_sites, 'processes'))} and "
        f"{cell(*sub(non_oh_sites, 'materials'))} on non-Ohio site rows. "
        f"`site_capabilities.csv` holds "
        f"{len(tables['site_capabilities'][1]):,} capability rows (unit: "
        f"capability rows) against {ns:,} site rows.")
    gaps.append(
        f"**Coordinates and street addresses are partial.** `latitude` is "
        f"filled on {cell(*sub(sites, 'latitude'))} site rows (precision of the "
        f"geocoded rows: "
        + ", ".join(f"`{k or '(blank)'}`={v:,}" for k, v in prec.most_common())
        + f"; rooftop/parcel-grade rows: "
        f"{prec.get('rooftop', 0) + prec.get('parcel', 0):,}); `street_address` on "
        f"{cell(*sub(sites, 'street_address'))}. Lowest-coverage states "
        f"(>=50 site rows): {weakest_txt}. Ohio: latitude "
        f"{cell(*sub(oh_sites, 'latitude'))}, street_address "
        f"{cell(*sub(oh_sites, 'street_address'))} (Ohio site rows).")
    gaps.append(
        f"**Evidence backfill is large.** {cell(zero_s, ns)} site rows and "
        f"{cell(zero_o, no)} organization rows (all tiers, all statuses) have "
        f"zero rows in `evidence.csv`; among Tier A/B records the gap is "
        f"{cell(zero_s_ab, n_s_ab)} site rows and {cell(zero_o_ab, n_o_ab)} "
        f"organization rows, i.e. high-tier claims whose evidence rows have "
        f"not been written. (Match is on `record_table` + `record_id`.)")
    gaps.append(
        f"**NAICS provenance is incomplete and often inferred.** "
        f"{naics_no_src:,} of {naics_filled:,} site rows with a `naics_primary` "
        f"({pct(naics_no_src, naics_filled)}) have no "
        f"`naics_primary_source_type` (AGENTS.md section 4 requires one); "
        f"{inferred:,} site rows ({pct(inferred, ns)} of all site rows) are "
        f"`researcher_inferred`. On organization rows {org_naics_no_src:,} of "
        f"{org_naics_filled:,} with a `naics_primary` lack a source type.")
    ring_blank = ns - f_sites("ring_primary")
    gaps.append(
        f"**Site ring and county gaps.** `ring_primary` is blank on "
        f"{ring_blank:,} site rows ({pct(ring_blank, ns)}; MUST field per "
        f"SCHEMA 4.5). Ohio site rows missing `county`: "
        f"{len(oh_sites) - fill_counts(oh_sites, 'county'):,} of "
        f"{len(oh_sites):,}; Ohio site rows with `county_source` blank: "
        f"{len(oh_sites) - fill_counts(oh_sites, 'county_source'):,} (blank is "
        f"an honest unknown, but limits county-level audit).")
    gaps.append(
        f"**Organization legal form and ownership are mostly unclassified.** "
        f"`entity_type` is informative (!= `unknown`) on "
        f"{cell(*sub(orgs, 'entity_type', 'unknown'))} organization rows; "
        f"`ownership_type` on {cell(*sub(orgs, 'ownership_type', 'unknown'))}; "
        f"`year_founded` on {cell(*sub(orgs, 'year_founded'))} (all tiers, all "
        f"statuses); for Ohio-HQ organization rows (hq_state = OH) "
        f"`entity_type` is {cell(*sub(oh_orgs, 'entity_type', 'unknown'))} and "
        f"`ownership_type` {cell(*sub(oh_orgs, 'ownership_type', 'unknown'))}. "
        f"Website is "
        f"{cell(*sub(orgs, 'website'))}.")
    u_s = sum(1 for r in sites if r["verification_tier"] == "U")
    c_s = sum(1 for r in sites if r["verification_tier"] == "C")
    gaps.append(
        f"**Verification depth.** {u_s:,} site rows are Tier U and {c_s:,} "
        f"Tier C ({pct(u_s + c_s, ns)} of all site rows combined); only "
        f"{sum(1 for r in sites if r['verification_tier'] == 'A'):,} are Tier A.")

    # ---- assemble
    L = []
    A = L.append
    A(f"# Field-fill profile of the canonical CSVs — {date}")
    A("")
    A(f"- **Git HEAD:** `{head}`")
    A(f"- **Working-tree state of `data/` at generation:** "
      + ("clean (matches HEAD)" if not dirty else
         f"{len(dirty.splitlines())} uncommitted path(s) under data/ — the "
         f"figures describe the working tree, not HEAD alone"))
    A(f"- **Generated by:** `python3 scripts/profile_fields.py` (stdlib only, "
      f"read-only on `data/`)")
    A(f"- **Source:** `data/*.csv` read directly; organizations and sites are "
      f"the union of per-state shards "
      f"({len(shard_info['organizations'][0])} organization shards, "
      f"{len(shard_info['sites'][0])} site shards).")
    A("- **Fill rule:** a cell is *filled* when non-empty after whitespace "
      "strip. In key-field breakdowns, columns whose vocabulary contains "
      "`unknown` (`employee_band_*`, `entity_type`, `ownership_type`) count "
      "`unknown` as *not* filled; the column label says so.")
    A("- **Unit discipline:** every count below names its unit and filter. "
      "\"All tiers, all statuses\" means no filtering by verification tier or "
      "operating/organization status (closed, acquired and merged rows are "
      "included).")
    A("")
    A("## Biggest gaps")
    A("")
    A("Derived mechanically from the numbers in this report, oriented to "
      "cluster / economic-development use.")
    A("")
    for g in gaps:
        A(f"- {g}")
    A("")

    # 1. tables
    A("## 1. Row counts and per-column fill, by table")
    A("")
    A(md_table(["table", "unit", "rows", "columns"],
               [[f"`{t}`", UNIT[t], f"{len(tables[t][1]):,}",
                 len(tables[t][0])] for t in list(SHARDED) + SINGLE]))
    A("")
    for t in SHARDED:
        per, nhdr = shard_info[t]
        A(f"`{t}` shard row counts ({UNIT[t]}, all tiers, all statuses; "
          f"{nhdr} distinct header layout{'s' if nhdr != 1 else ''} across "
          f"shards): "
          + ", ".join(f"{k} {v:,}" for k, v in sorted(per.items())))
        A("")
    for t in list(SHARDED) + SINGLE:
        cols, rows = tables[t]
        n = len(rows)
        A(f"### 1.{list(SHARDED).index(t) + 1 if t in SHARDED else len(SHARDED) + SINGLE.index(t) + 1} `{t}` — fill by column ({UNIT[t]}, all tiers, all statuses; n = {n:,})")
        A("")
        data = []
        for c in cols:
            k = sum(1 for r in rows if filled(r.get(c)))
            data.append([f"`{c}`", f"{k:,}", f"{n - k:,}", pct(k, n)])
        A(md_table(["column", "non-empty", "empty", "fill rate"], data))
        A("")

    # 2. sites by state
    A("## 2. Sites — key-field fill by state")
    A("")
    A(f"Unit: site rows, all tiers, all statuses (n = {ns:,}). Top 15 states by "
      f"site-row count, remainder pooled. Cells are fill rates "
      f"(non-empty / site rows in that state). State = the site row's own "
      f"`state` field.")
    A("")
    A(breakdown(sites, "state", SITE_KEY))
    A("")
    A("### 2.1 Ohio and PIC-12 slice")
    A("")
    slice_rows = []
    for name, rs in (("Ohio site rows (state = OH)", oh_sites),
                     ("PIC-12-county site rows (Ohio, county in PIC-12)",
                      pic12_sites),
                     ("Ohio site rows outside PIC-12 (incl. blank county)",
                      [r for r in oh_sites if r not in pic12_sites])):
        n = len(rs)
        slice_rows.append([name, f"{n:,}"] +
                          [pct(fill_counts(rs, c, e), n) for c, e in SITE_KEY])
    A(md_table(["slice (site rows, all tiers, all statuses)", "rows"] +
               [key_label(c, e) for c, e in SITE_KEY], slice_rows))
    A("")

    # 3. orgs by hq_state
    A("## 3. Organizations — key-field fill by HQ state")
    A("")
    A(f"Unit: organization rows, all tiers, all statuses (n = {no:,}). Top 15 "
      f"`hq_state` values by row count, remainder pooled; blank `hq_state` is "
      f"shown as `(blank)`. `employee_band_ohio` is an Ohio-footprint band, so "
      f"low fill outside Ohio is expected.")
    A("")
    A(breakdown(orgs, "hq_state", ORG_KEY))
    A("")

    # 4. evidence
    A("## 4. Evidence coverage")
    A("")
    A(f"Unit: records with zero rows in `data/evidence.csv` "
      f"({len(ev):,} evidence rows total). Match key: `record_table` + "
      f"`record_id`, so an id appearing under a different `record_table` does "
      f"not count. All statuses.")
    A("")

    def ev_block(title, by_tier, rows_n):
        data = []
        for t in sorted(by_tier, key=lambda x: ("ABCU(".find(x[0]), x)):
            n, z = by_tier[t]
            data.append([t, f"{n:,}", f"{n - z:,}", f"{z:,}", pct(z, n)])
        tn = sum(v[0] for v in by_tier.values())
        tz = sum(v[1] for v in by_tier.values())
        data.append(["**all tiers**", f"{tn:,}", f"{tn - tz:,}", f"{tz:,}",
                     pct(tz, tn)])
        return (f"**{title}**\n\n" +
                md_table(["verification_tier", "records", "with >=1 evidence row",
                          "zero evidence rows", "% zero"], data))

    A(ev_block("Organization rows (record_table = organizations)", ev_orgs, no))
    A("")
    A(ev_block("Site rows (record_table = sites)", ev_sites, ns))
    A("")
    eco_cols, eco = tables["ecosystem"]
    prog_cols, prog = tables["programs"]
    A(ev_block("Ecosystem rows (record_table = ecosystem)",
               evidence_coverage(eco, "org_id", "ecosystem", ev_idx), len(eco)))
    A("")
    A(ev_block("Program rows (record_table = programs)",
               evidence_coverage(prog, "program_id", "programs", ev_idx),
               len(prog)))
    A("")
    # ev rows per record + orphans
    per_site = Counter(r["record_id"] for r in ev if r["record_table"] == "sites")
    per_org = Counter(r["record_id"] for r in ev
                      if r["record_table"] == "organizations")
    A("**Evidence-row depth** (evidence rows per record, among records with "
      ">=1): sites median/max = "
      f"{_med(per_site)}/{max(per_site.values()) if per_site else 0}; "
      f"organizations median/max = "
      f"{_med(per_org)}/{max(per_org.values()) if per_org else 0}.")
    A("")
    held = {"organizations": {r["org_id"] for r in orgs},
            "sites": {r["site_id"] for r in sites},
            "ecosystem": {r["org_id"] for r in eco},
            "programs": {r["program_id"] for r in prog}}
    orphan = Counter(r["record_table"] for r in ev
                     if r["record_id"] not in held.get(r["record_table"], set()))
    A("**Orphan check** (evidence rows whose `record_id` is not in the "
      f"named table; unit: evidence rows): "
      + (", ".join(f"{k}: {v:,}" for k, v in orphan.items()) if orphan
         else "none"))
    A("")
    tier_eff = Counter(r["tier_effect"] for r in ev)
    A("Evidence rows by `tier_effect` (unit: evidence rows): "
      + ", ".join(f"`{k or '(blank)'}`={v:,}" for k, v in tier_eff.most_common()))
    A("")

    # 5. enums
    A("## 5. Value distributions (enum-like columns, <= 40 distinct values)")
    A("")
    A("Each table gives the unit and filter in its heading; percentages are of "
      "all rows in the table (blank included). Columns with more than 40 "
      "distinct values are listed as omitted.")
    A("")
    for t, cols_wanted in ENUM_COLS.items():
        cols, rows = tables[t]
        n = len(rows)
        for c in cols_wanted:
            if c not in cols:
                continue
            cnt = Counter((r.get(c) or "").strip() for r in rows)
            if len(cnt) > ENUM_MAX:
                A(f"### `{t}.{c}` — {len(cnt)} distinct values (> {ENUM_MAX}); "
                  f"omitted")
                A("")
                continue
            A(f"### `{t}.{c}` — {UNIT[t]}, all tiers, all statuses "
              f"(n = {n:,}; {len(cnt)} distinct incl. blank)")
            A("")
            A(counter_table(cnt, n, c))
            A("")

    # 6. vocab + must
    A("## 6. Vocabulary and must-have sanity check")
    A("")
    A("Out-of-vocabulary values compared with the controlled vocabularies in "
      "`docs/SCHEMA.md` §2.1, §4.1, §4.2, §4.4, §4.5 as read when this script "
      "was written. Blank values are flagged only for MUST fields; a "
      "vocabulary mismatch can also mean a schema revision this script does "
      "not know about. These are observations, not edits; resolving them is an "
      "owner / integrator matter (AGENTS.md section 2 rule 9).")
    A("")
    for t in ("sites", "organizations"):
        cols, rows = tables[t]
        n = len(rows)
        A(f"### 6.{1 if t == 'sites' else 3} Out-of-vocabulary values — `{t}` ({UNIT[t]}, all tiers, all statuses; n = {n:,})")
        A("")
        data = []
        for c, vocab in VOCAB[t].items():
            cnt = Counter((r.get(c) or "").strip() for r in rows)
            for v, k in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0])):
                if v == "" and (t, c) in VOCAB_BLANK_OK:
                    continue
                if v not in vocab and v != "":
                    data.append([f"`{c}`", f"`{v}`", f"{k:,}"])
        A(md_table(["column", "out-of-vocabulary value", "rows"], data)
          if data else "None found.")
        A("")
        A(f"### 6.{2 if t == 'sites' else 4} Blank MUST fields — `{t}` ({UNIT[t]}, all tiers, all statuses; n = {n:,})")
        A("")
        data = [[f"`{c}`", f"{sum(1 for r in rows if not filled(r.get(c))):,}"]
                for c in MUST[t]]
        data = [d for d in data if d[1] != "0"]
        A(md_table(["MUST column", "blank rows"], data) if data
          else "No blanks in the checked MUST columns.")
        A("")
    # Ohio county, hq_country variants, dates
    A("### 6.5 Other checks")
    A("")
    oh_nocounty = sum(1 for r in oh_sites if not filled(r["county"]))
    A(f"- Ohio site rows (state = OH) with blank `county` (AGENTS.md section 4 "
      f"requires county for every Ohio site): {oh_nocounty:,} of "
      f"{len(oh_sites):,}.")
    hc = Counter((r["hq_country"] or "").strip() for r in orgs)
    A("- `organizations.hq_country` spellings (organization rows): "
      + ", ".join(f"`{k or '(blank)'}`={v:,}" for k, v in hc.most_common())
      + ".")
    iso = lambda v: len(v) == 10 and v[4] == "-" and v[7] == "-" and \
        v.replace("-", "").isdigit()
    for t, c in (("sites", "last_verified"), ("organizations", "last_verified"),
                 ("evidence", "observed_date")):
        rows = tables[t][1]
        bad = sum(1 for r in rows if filled(r.get(c)) and not iso(r[c].strip()))
        A(f"- `{t}.{c}` non-empty but not a full ISO date ({UNIT[t]}): "
          f"{bad:,} of {fill_counts(rows, c):,} non-empty.")
    lat_bad = 0
    for r in sites:
        try:
            if filled(r["latitude"]):
                lat = float(r["latitude"])
                lon = float(r["longitude"])
                if not (15 <= lat <= 72 and -180 <= lon <= -60) and \
                        r["country"] in ("US", ""):
                    lat_bad += 1
        except ValueError:
            lat_bad += 1
    A(f"- US-country site rows whose coordinates are non-numeric or outside a "
      f"loose US bounding box (site rows): {lat_bad:,}.")
    lat_nolon = sum(1 for r in sites if filled(r["latitude"]) !=
                    filled(r["longitude"]))
    gp_mismatch = sum(1 for r in sites if filled(r["latitude"]) !=
                      filled(r["geocode_precision"]))
    A(f"- Site rows where latitude and longitude fill disagree: {lat_nolon:,}; "
      f"where latitude and `geocode_precision` fill disagree: {gp_mismatch:,}.")
    dup_o = [k for k, v in Counter(r["org_id"] for r in orgs).items() if v > 1]
    dup_s = [k for k, v in Counter(r["site_id"] for r in sites).items() if v > 1]
    A(f"- Duplicate primary keys across shards: organizations {len(dup_o):,}, "
      f"sites {len(dup_s):,}.")
    org_ids = {r["org_id"] for r in orgs} | {r["org_id"] for r in eco}
    orphan_sites = sum(1 for r in sites if r["org_id"] not in org_ids)
    A(f"- Site rows whose `org_id` is not in organizations or ecosystem: "
      f"{orphan_sites:,}.")
    A("")
    return "\n".join(L) + "\n"


def _med(counter):
    vals = sorted(counter.values())
    if not vals:
        return 0
    m = len(vals) // 2
    return vals[m] if len(vals) % 2 else (vals[m - 1] + vals[m]) / 2


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", help="output Markdown path (default: stdout)")
    ap.add_argument("--date", default=datetime.date.today().isoformat(),
                    help="report date (default: today)")
    args = ap.parse_args()
    text = build_report(args)
    if args.out:
        out = Path(args.out)
        if not out.is_absolute():
            out = Path.cwd() / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out} ({len(text.splitlines())} lines)")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
