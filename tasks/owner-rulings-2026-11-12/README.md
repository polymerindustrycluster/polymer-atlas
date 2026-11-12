# Owner rulings — 2026-11-12

Packet for held hygiene items and leftover skimpy-state scope/naming questions.
Research date: 2026-11-12. Public professional facts only. No contact data, no paid calls, no licensed-directory republication.

Each item that still needs a ruling has a recommended choice marked **(a)**. Items that are already settled on `main` are recorded as stale queue entries — no apply is proposed.

This file does not edit Ohio data files.

---

## H-CHROMAFLO: Chromaflo Technologies → Vibrantz tombstone

**QUEUE line (still open):** "Add tombstone parent record: Chromaflo Technologies → successor Vibrantz (ORG-000007)"

**Deciding facts already on main:**
- `ORG-000007` Vibrantz Technologies Inc. is the live successor (trade name Chromaflo Technologies; website vibrantz.com).
- `ORG-013200` Chromaflo Technologies Corporation already exists in `data/organizations_OH.csv`, `status=acquired`, `status_date=2022-04-21`, `successor_org_id=ORG-000007`. Notes cite SCHEMA §5.2 and GLEIF (current legal name Vibrantz Color Solutions Inc.; prior legal name Chromaflo Technologies Corporation).

**Recommendation: (a)** Treat the QUEUE item as already done. Do not mint a second tombstone. Do not edit the Ohio shard.

- (b) Still add a new tombstone (would duplicate `ORG-013200`).

---

## H-HANKOOK: ORG-000167 vs ORG-000204

**QUEUE line (still open):** "Hankook duplicate merge (ORG-000167 vs ORG-000204) — prepared fix, awaiting owner pick"

**Deciding facts already on main:**
- `ORG-000167` Hankook Tire America is already `status=merged`, `status_date=2026-10-29`, `successor_org_id=ORG-000204`. Notes say it is the same America Technical Center at 3535 Forest Lake Dr, Green, created twice.
- `ORG-000204` Hankook Tire America Corp. (HQ Nashville, TN) remains active, with active site `SITE-000215` at 3535 Forest Lake Dr, Green, OH (tier B).
- Leftover: `SITE-000174` "Hankook Tire America Technical Center — Green" is still attached to tombstoned `ORG-000167` and is `operating_status=closed`, with no street on the row. This looks like the unrepointed first site, not a second facility.

**Recommendation: (a)** Confirm the 2026-10-29 org tombstone stands. Authorize a later non-Ohio-or-integrator pass to fold or repoint `SITE-000174` to `ORG-000204` / `SITE-000215` if the owner agrees they are the same Green technical center (address-first: `SITE-000174` currently has a blank street, so this is not a same-street merge on the face of the row). This pass does not edit Ohio site files.

- (b) Unwind the org merge and keep both organizations.
- (c) Leave `SITE-000174` as a closed historical row under the tombstoned org indefinitely.

---

## H-ROECHLING: SITE-000589 division assignment

**QUEUE line (still open):** "SITE-000589 (Röchling Industrial Cleveland) was promoted under ORG-000550 Röchling Automotive USA LLP … distinct Röchling divisions; confirm or unwind"

**Deciding facts already on main:**
- `SITE-000589` "Roechling Industrial Cleveland, L.P." is already under `ORG-000551` (Roechling Industrial Cleveland, LP, HQ South Euclid), not under Automotive `ORG-000550`.
- `ORG-000551` notes record a 2026-10-29 ruling (A2 unwind).

**Recommendation: (a)** Treat the QUEUE item as already unwound. No further apply.

- (b) Move the site back under Automotive `ORG-000550`.

---

## H-PA-STREET: PA same-street / Conica Lane pair

**Held pair:** `SITE-002364` ↔ `SITE-002304` at 109 Conica Lane, Evans City, PA, carried as STILL_UNCERTAIN in the 2026-11-06 tombstone-site-operator packet and in `tasks/dedupe-leads-2026-11-06` (D10).

**Settling fact still named there:** a dated legal record resolving Harmony/Evans City continuity versus relocation or separate premises. The 2026 Florida annual report cited in that packet was treated as a legal principal address only, not plant operation.

**Recommendation: (a)** Keep the hold. Do not merge on address alone (flag: this would be an address-first merge). A later pass should fetch a current Pennsylvania or operator own-page witness before any fold.

- (b) Fold the two site rows now on the shared street.

---

## H-TARKETT: Tarkett USA Inc. vs Tarkett North America (SITE-003477, SITE-003478)

**Settling fact from the PR #201 holds:** a dated primary legal-name bridge equating filed operator Tarkett USA Inc. with held successor `ORG-000131` Tarkett North America, or identification of the actual held legal operator. A successor pointer alone does not settle the naming gap.

**Recommendation: (a)** Keep the hold until that legal-name bridge is in hand. Do not repoint on the group name alone.

- (b) Repoint both sites to `ORG-000131` now.

---

## H-DANIMER: post-sale operator at 605 Rolling Hills Lane (SITE-003134)

**Settling fact from the PR #201 hold:** identify the post-sale legal entity operating 605 Rolling Hills Lane and bridge it to a held Atlas operator. The Teknor 2025 release saying Danimer continues separately does not establish that the old public Danimer Scientific Inc. is the continuing operator.

**Recommendation: (a)** Keep the hold.

- (b) Repoint now to a held Danimer or Teknor organization without a new site-level operator witness.

---

## S-CRM-AZ: naming for CRM of America LLC (Mesa) — QMS-AZ-23

Witnessed by ITA 224680 + OSHA 348264797 (rubber products, NAICS 326299) at 11400 E Pecos Rd, Mesa, but not created because the legal name "CRM of America" trips validate.py V-50 (PIC CRM string).

**Recommendation: (a)** Accept a recorded legal name that does not contain the bare token `CRM` as a standalone acronym, for example `C.R.M. of America LLC` or `CRM of America, LLC` if the validator can be given an allow-list for this EIN/legal name, and then create the org/site from the federal witnesses. Do not self-rule the string.

- (b) Leave the row uncreated until V-50 is revised.
- (c) Create under a trade name only, omitting the legal name (not recommended; the federal filings use the legal name).

---

## S-SCOPE: borderline polymer-scope leftover rows

These leftover STILL_UNCERTAIN rows are product-class questions, not operator-identity questions. They are held for the owner (AGENTS.md §2 rule 9). A short recommendation is given; none is applied in the 2026-11-12 data PRs.

| ID | Candidate | Question | Recommended lean |
|---|---|---|---|
| QMS-AL-09 | Lenzing Fibers, Axis, AL | Is lyocell cellulosic fiber (NAICS 325220) in atlas polymer scope? | **(a)** Hold out of Rings 1–2 unless the owner extends scope to regenerated cellulosic fiber. Cellulose is not a synthetic polymer. |
| QMS-AZ-01 / LF-RI-00043 | Fujifilm Electronic Materials (Mesa, AZ and North Kingstown, RI) | Are photoresists/polyimides made at these sites, and are they in scope? | **(a)** Hold. Needs a site-level own-page or federal product witness tying polymer binders to the named site. Business-line brochures are not site witnesses. |
| QMS-AZ-11 | Shin-Etsu MicroSi, Phoenix | Photoresists/encapsulants made on site vs distribution? | **(a)** Hold for an own-site manufacturing witness. |
| QMS-CO-04 / QMS-CO-11 | Boulder Scientific Mead and Longmont | Polyolefin catalysts vs polymers (NAICS 325199/325412). | **(a)** Treat catalysts as out of Ring 1–2 (precursor/auxiliary, consistent with precursor-only doctrine) unless the owner brings catalyst plants into scope. Do not create until that ruling. |
| QMS-WV-09 | ICL-IP Gallipolis Ferry | Are products polymer flame-retardant additives? | **(a)** Hold for an own-page product identity. Flame-retardant additives can be in Ring 2 if the product is a polymer additive; the NAICS alone does not say. |

Other chemical-plant leftovers (Ricca reagents, ERA standards, Molecular Products CO2 absorbents, Azure water treatment, Brand Nu, MacDermid plating chemicals, Pemco porcelain enamel, etc.) can be settled as factual REJECTs once an own-page or dated product witness is attached in a later pass; they are not being self-ruled as scope expansions in this packet.

---

## S-PPC-PAYSON: which org operates the Payson, UT plant

**Original settling fact:** integrator dedupe ruling on `ORG-001029` vs `ORG-004209`.

**Facts now on main (the question was not settled; a third org was added):**
- `ORG-001029` PPC Flex (Alliance, OH; website ppcflex.com; tier U; trade name Plastic Packaging Technologies, LLC).
- `ORG-004209` PPC Flexible Packaging, LLC (North Salt Lake, UT; SITE-005303 at 95 South Riverbend Way; ultimate parent Fisher Container Holdings LLC).
- `ORG-006226` "Ppc Flexible Packaging - Payson Printing Plant" (Payson, UT; SITE-008292 at 213 South Temkin Way), created 2026-11-04 from Grok P2 packet PR #87.

Lead-fusion cluster LF-UT-00047 already flagged Payson as `HELD_ORG_OTHER_LOCATION` of `ORG-004209`.

**Recommendation: (a)** Do not merge on the name alone. Ask the integrator which legal entity operates 213 South Temkin Way. Likely fold `ORG-006226` into `ORG-004209` if a domain or own-page witness ties Payson to PPC Flexible Packaging, LLC / Fisher Container, and treat `ORG-001029` (ppcflex.com, Ohio) as a separate company unless a dated legal identity bridge exists. Flag: any fold of 006226 into 004209 is not address-first (the sites are in different cities); a fold into 001029 would need more than the shared "PPC" letters.

- (b) Merge all three now.
- (c) Keep all three indefinitely.

---

## Already settled on main (no ruling needed)

- **QMS-AR-24** Building Materials Manufacturing LLC, Arkadelphia: already `SITE-005437` GAF - Arkadelphia (PMMA) at 151 McClellan/MCCELLAN Blvd under `ORG-004251`. Operator is GAF; product is PMMA.
- **3form Ecoresin plant, 955 S 3800 W:** already `SITE-008189` under `ORG-004817`, with both EPA FRS 110070516125 and the Utah DAQ FCE memo — the named second-source settling fact is satisfied.
- **QMS-CT-30, QMS-OR-08, QMS-KS-40:** the pending parent PRs (#69 LATICRETE, #64 Carestream, #57 NOV Inc.) have merged. Sites are applied in the 2026-11-12 state-group data PRs under those existing orgs.
