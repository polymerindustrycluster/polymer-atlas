# Lane L3 notes, CA STRONG wave (2026-11-04)

Input: 19 clusters (the file has 19 data rows). Output: `verdicts.csv`.

## Counts (unit: input clusters)
- VERIFIED_NEW_SITE, tier B: 2 (LF-CA-00740 Pregis Visalia under ORG-002935; LF-CA-01214 JM Eagle Stockton under ORG-002261)
- VERIFIED_NEW_ORG, tier C: 13
- STILL_UNCERTAIN: 3 (LF-CA-01107 TNT, LF-CA-00678 Spatz, LF-CA-00071 W.R. Meadows Pomona)
- REJECT: 1 (LF-CA-00995 M Chemical, scope)
- DUPLICATE_OF: 0

## Method and limits
- Dedupe: `atlas.py dedupe-check` (name, street, city, state) run for 10 candidates plus parent-name probes; results matched `current_atlas_hits` in the input. Only Pregis (ORG-002935) and JM Eagle (ORG-002261) have organization hits.
- Fetch route: WebFetch returns model-summarized text. Quotes in `own_quote` were copied from that summarizer's quoted output, not from raw HTML, so the integrator's re-fetch check may find small whitespace or punctuation differences. Highest-risk quotes: LF-CA-01408 (VIP), LF-CA-00978 (Magic), LF-CA-01228 (Orion, mid-sentence cut), LF-CA-01215 (Fabexco, mid-sentence cut), LF-CA-01067 (Serpac). The JM Eagle quote was read from the PDF with pdftotext.
- No emails or phones recorded. No data/ edits, no git.
- Where the own page prints the address but the activity sits in a different sentence, `own_quote_kind` is `activity_only` and the address is noted in `note`.
- `naics_primary` left blank except JM Eagle (326122, the single code in the set); other sets carry several codes with no clear primary.
- No dated closures found. Directory "Closed" flag on Newby Rubber (MapQuest) was not treated as evidence. Form 5500 check was not needed (no closure REJECT).

## Flags for the integrator
- LF-CA-01214: ORG-002261 shows HQ Cochranton PA, while jmeagle.com gives HQ as 5200 West Century Boulevard, Los Angeles. Org record may need review (not a lane decision).
- LF-CA-00071: Atlas holds ORG-002722 W R Meadows Of Pennsylvania (verified from the same contact page). Entity structure for Pomona is an owner ruling; held as STILL_UNCERTAIN until a source says what Pomona makes.
- LF-CA-02845 Llamas Plastics: acquired by Lee Aerospace in 2024 (press release); a for-sale listing exists for the building. Neither is a dated closure. Record as active with ownership note.
- LF-CA-01408 VIP: street corrected from "Rd." to "St." per own site. A possibly related Redwood Plastics and Rubber (ORG-003616, Langley BC) exists in Atlas; no evidence tying it to VIP found, so no merge.
- LF-CA-01228 Orion: use orionplastics.net, not orionplastics.com (that is the Alberta company).
- LF-CA-01413 Omega: parent Sigma Plastics Group has no Atlas record; Omega's own page is a Sigma location page.
- LF-CA-01067 Serco Mold: link to Serpac rests on federal DBA name and identical address; the Serpac site never says "Serco Mold".
- Scope: LF-CA-02845 (formed acrylic aerospace transparencies) is judged Ring 1 shaped polymer article but is the one scope call a reviewer may want to confirm.
- Not checked: Form 5500 address matches, SOS legal-name suffixes (Emerald, Magic, VIP, Newby), org HQ for WARCO, Fabexco, Omega, Poly Processing.
