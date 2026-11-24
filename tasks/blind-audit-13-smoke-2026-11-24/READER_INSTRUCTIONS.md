# Reader instructions: audit 13 smoke

You read one Atlas record and judge each published value against the sources in this message. Do not browse, search, run commands or read files. Everything you may use is below the record: SOURCES (`S1`, `S2`, …: pages fetched once by script, redacted excerpts), REPLAY RECEIPTS (`R1`, …: filing checks already run by script) and the CHECKLIST. A failed or missing source is a fact about the route, never about the record.

Reply with one JSON object and nothing else.

```json
{"findings": [{"target": "<checklist key>", "verdict": "VERIFIED|CONTRADICTED|UNCONFIRMED|REQUEST",
               "source_id": "S1", "source_value": "<what the source states for this field>", "quote": "<verbatim words from that source>",
               "settling_fact": "<the one fact that would settle it>", "request_url": "<one public URL>",
               "core_effect": "name|status|street|county|polymer_relevance|null", "note": ""}],
 "notes": [{"kind": "ring_difference|legal_form_name|drift|omission|other", "text": ""}]}
```

Give exactly one finding per checklist key, in order. A blank value is not a claim and has no key.

## Verdicts

- **VERIFIED**: a source supports the value at the record's grain (organization or site). Cite `source_id`; a quote is optional, but one you give must be verbatim.
- **CONTRADICTED**: a source states a value incompatible with the claim about this entity at this grain, or shows the row is a different entity or a duplicate of a held record. Give `source_id`, `source_value` and a **verbatim `quote` from that source**. The script replays the quote word for word against the stored page: a quote that is not on the page makes your finding unconfirmed, so never paraphrase. A source about another grain does not contradict: a company-level page cannot contradict a site value, and a site page cannot contradict a company value. A parent's headquarters street does not contradict a plant's street; a page saying an address belongs only to headquarters would. A failed fetch, a silent page, an unreachable source or an empty excerpt is never a contradiction.
- **UNCONFIRMED**: you could not settle the claim and no source contradicts it. Name the fact that would settle it in `settling_fact`. A value that the sources simply do not mention is unconfirmed, not contradicted.
- **REQUEST**: one more public page would settle it; give its URL. You get at most one round and six pages per record including those already shown; after that, give final findings. A request the cache cannot serve leaves the value unconfirmed.

## Core fields (these decide the audit)

Core fields are name (`legal_name`, `site_name`), operating status (`status`, `operating_status`), street (`street_address`), county (`county`, `hq_county`) and **polymer relevance**, which is its own checklist key.

**Polymer relevance** is judged at the record's grain, in or out of scope under the Atlas rings and exclusions, from the entity's own site or filing. It is contradicted only when a source shows the record is out of scope at that grain. Apply the inclusion test of every ring. A record is out of scope when it passes no ring's test, and also when its activity is expressly excluded even with polymer contact (a tire installer that does no curing, retail only, a different entity). One ring's exclusion is never the overall test: polymer used only as a purchased part fails the molding-and-processing ring but is tested against the downstream-user ring, and a general economic-development or workforce organization for a geography in scope is tested against the ecosystem ring. A different ring number is not an error: note it as `ring_difference`.

**Names.** A held name that differs from the source's name only by a legal-form word (Inc, LLC, Corp, Co, Company, The) or by punctuation names the same entity. It is not contradicted: give VERIFIED, put the source's wording in `source_value` and add a `legal_form_name` note. A division, predecessor, parent or different entity name is contradicted.

**Child rows** (`c1`, `c2`, …) are judged with the record. A contradicted child value gates the record only if it shows one of the record's core fields wrong: set `core_effect` to that field (a link that belongs to another operator shows the name wrong). Otherwise leave it null; it is reported as a descriptive error.

## Everything else is descriptive

Process, material and market tokens (judge each token; a token the sources do not support is UNCONFIRMED), employee bands, NAICS and its source type, ownership, dates and links are reported but do not gate. Contradict them only with a replayed quote.

- **Filing receipts.** A receipt is a replayed public fact. `CONTRADICTS` means the same establishment's filing, inside the age cutoff, states a different band: cite `R#` and quote its text. `UNRESOLVED` or `LEAD_ONLY` means unsettled: UNCONFIRMED with the receipt's missing fact. Never treat a Form 5500 participant count as an employee count.
- **A value shown as `[withheld for blindness]`** has no readable literal. Check the underlying claim from the evidence, or leave it UNCONFIRMED. It earns no credit as shown.
- **A value true at the record's date and changed later** by a dated source is VERIFIED with a `drift` note.
- A cell the sources plainly fill that the record leaves empty is an `omission` note, never an error.

Keep contact data (individual emails, direct phone numbers, home addresses) out of every field you write.
