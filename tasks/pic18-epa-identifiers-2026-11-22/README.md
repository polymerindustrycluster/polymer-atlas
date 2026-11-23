# PIC-18 EPA facility identifiers

Packet against Atlas base `393c3895` and the November 22, 2026 Parquet lake. The frame contains **813 active Ohio sites in PIC-18 with a civic street**. The pinned lake projection reconciles to the Ohio site shard. These sites account for **346 of the 549 quarantined Ohio registry links**. The rest-of-Ohio frame contains **153 active sites with a civic street**.

| Registry | Proposed links | Verbatim returns | New links | Quarantined links refused | Direct facility proof | FRS crosswalk proof |
|---|---:|---:|---:|---:|---:|---:|
| FRS | 65 | 32 | 33 | 44 | 65 | 0 |
| RCRA EPA ID | 121 | 114 | 7 | 121 | 52 | 69 |
| NPDES permit ID | 20 | 18 | 2 | 17 | 10 | 10 |
| **Total** | **206** | **164** | **42** | **182** | **127** | **79** |

The 206 links cover 153 sites in the frame. Of the 141 program IDs, 62 rest on their own program facility row and 79 use the EPA FRS program crosswalk to an exact FRS facility. The crosswalk and program file agree on the ID, and the program row also passes the physical address check with a compatible operator. All six columns of a returning registry row are preserved, including its original match basis and date.

Of the 182 refused quarantine links, 107 had an unheld operator name, 30 failed street equality, 23 passed on a different basis than the quarantined row stated, 17 matched only a recorded parent, 15 had a program operator that conflicted with the FRS operator, four failed unit or building agreement, and two used a former legal name recorded in Atlas notes. A row can have several reasons across witnesses, so the reason counts overlap. Every refused quarantine link appears by site and registry ID in `leads.csv`.

## Match and open questions

The November 22 strict-floor ruling supersedes the original brief's tolerance of one-sided suites. Street equality uses Atlas's `same_street` guard. Site and source must also agree on unit, building, floor and department designators, when present, and state must be present and equal. City can match either recorded locality in parentheses or outside them, and equal ZIP5 also satisfies locality. The facility name must be held by the site or its operator, with at most the allowed corporate-form addition. Generic site-name parts, recorded parents and recorded former operators are excluded. Historical-name screening uses explicitly marked names in Atlas site and organization notes, including the old name in a documented legal rename. An anchored program may omit corporate-form words when its operator still agrees with the exact FRS witness.

Nine lead keys match multiple site records, and three have IDs held elsewhere. The strict ruling holds both candidate sites for a shared facility. R10 permits several different IDs at one site and permits a documented co-location with a note. A co-location exception requires the owner to identify the distinct operator sites and specify the note. Two questions remain for the owner. Can a former legal name support a link when the record documents the same operator under a legal rename? Can a different verified match basis authorize a replacement for 23 quarantined rows whose original basis could not be reproduced?

The seeded 25-site canary retained all six proposals under the strict floor. Three RCRA links return verbatim, three quarantined links fail the operator-name test, and three links are new. Its ten distinct raw CSV witnesses were read against the facility and Atlas record.

## Reproduce and verify

From the pinned repository root, set `EPA_LAKE` to the absolute path of the `lake/2026-11-22` snapshot. The checksum manifest uses repository paths for repository inputs, `provenance/lake/2026-11-22/` for the shared snapshot identified by `EPA_LAKE`, and `raw/` for files under the shared store’s raw root.

```sh
PACKET=tasks/pic18-epa-identifiers-2026-11-22
uv run --with duckdb==2.0.1 python "$PACKET/check.py" --lake "$EPA_LAKE" --hash-inputs
uv run --with duckdb==2.0.1 python "$PACKET/build.py" --lake "$EPA_LAKE" --out /path/to/local/rebuild
```

The checker rebuilds the selection, checks every packet row by its recorded Parquet source and raw CSV row number, and runs planted failures for a different street, a parent-only operator, and an ID held by another site. The builder also compares the projected witness fields against their original CSV rows in the ZIPs. Raw row numbers are 1-based data records with the header excluded. The first six columns of `packet.csv` follow `data/registry_links.csv` exactly. The remaining columns identify the raw witnesses. Program crosswalk rows carry separate locators for their program facility, crosswalk and FRS facility. The packet leaves registry and evidence integration to the controller. The builder and checker support `--region rest-oh` for the later pass.

Verification on November 22 replayed all 206 links from 356 Parquet witness rows and rejected all three planted failures. All 19 input digests matched. `python3 scripts/validate.py` passed on the canonical tree.
