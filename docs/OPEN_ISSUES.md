# Open issues — read before trusting SCHEMA.md rulings blindly

Schema v1.0 (docs/SCHEMA.md) was drafted by a research agent on 2026-10-28
and is strong overall, but the following items are flagged by the
coordinator for human ruling. Do not treat them as settled.

1. **GEON ruling is disputed (likely wrong).** SCHEMA §5.2 rules GEON a
   division of Avient with no separate org_id. Counter-evidence: GEON
   Performance Solutions was spun out of PolyOne in 2019 to SK Capital
   and operates as a standalone company HQ'd in Westlake, OH (PIC cluster
   intel watchlist, 2026-10-23, lists it as its own anchor; it also
   acquired Foster Corp. as a standalone acquirer). Coordinator's working
   position: GEON gets its OWN parent record with
   `ultimate_parent_name = SK Capital`. Needs John's ruling, then SCHEMA
   §5.2 must be corrected — the worked example matters because other
   agents will copy it.
2. **Geography definition conflict.** SCHEMA §4.4 uses a 19-county
   "PIC/GAC working definition" for NE Ohio; PIC's Evidence Room and
   cluster intel use **PIC-12** (Ashtabula, Cuyahoga, Geauga, Lake,
   Lorain, Mahoning, Medina, Portage, Stark, Summit, Trumbull, Wayne).
   AGENTS.md §8 freezes the workaround: store county, apply either
   definition at report time. John to rule on which is canonical for
   headline counts.
3. **Resin production cross-ring filter.** SCHEMA §1 codes standalone
   resin plants Ring 1 with a Ring 2 filter view. Workable, but any
   reporting code must implement the filter or Ring 2 counts will
   silently exclude resin producers.
4. **Source-count reconciliation and Summit County pilot** (in
   ~/workspace/polymer-database-scoping/ until reviewed) should be folded
   into docs/ once the coordinator's synthesis is accepted: headline
   findings — Summit pilot found ~99 candidates from 4 source types;
   coverage and overlap stats to be summarized here after review.
