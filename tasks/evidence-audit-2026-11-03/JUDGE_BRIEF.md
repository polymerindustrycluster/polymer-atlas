# Judge brief: does the cited page support the evidence row? (Atlas evidence audit, 2026-11-03)

Each input row is one evidence row from the Polymer Atlas. It names:
- a record (`record_name`, `record_table`);
- a claim (`claim_type`, `claim_detail`);
- the cited page, already fetched raw today and saved at `page_file` as markdown, truncated at 40k characters.

**Judge only from that saved file. Do not fetch anything, search the web, or use outside knowledge.** You are
measuring whether the cited page, as it stands today, supports the row.

## Claim types (what each must show)
- `existence`: the page is the entity's own page, and it names the entity: its legal or trading name, or a clear
  successor name.
- `scope`: the page states the in-scope polymer activity the detail claims, such as molding, compounding, resin
  production, rubber products, composites, coatings, polymer research or a polymer program. Generic "manufacturing"
  is not enough.
- `activity`: the page states the specific primary activity the detail claims.
- `address`: the page shows the address or city the detail claims for this entity or site.
- `parent`: the page states the ownership or operator link the detail claims.
- `liveness`: the page shows the entity operating, with current content and no closure notice.
- `code`: the page states the code or classification the detail claims.

## Verdict (exactly one)
- `SUPPORTED`: the page states the claim for this entity. Quote the deciding words.
- `PARTIAL`: the page supports part of the detail but not all of it. For example, it shows polymer scope but not the
  named process or material, or the right company but a different city. Say which part fails.
- `NOT_SUPPORTED`: the page is about this entity, but it does not state the claim.
- `WRONG_PAGE`: the page is not about this entity. Examples: a different company, a parked domain, a
  domain-for-sale page, or a generic portal with no mention of the entity.
- `CANNOT_JUDGE`: the text is a cookie wall, a login page, an empty JavaScript shell, or too little text to decide.

## Output
Write the CSV named in your task with these columns: evidence_id, verdict, quote, reason.
- `quote`: at most 25 words, copied **verbatim** as one continuous span of the page file. Leave it blank for
  WRONG_PAGE and CANNOT_JUDGE. The controller checks every quote word for word against the file.
- `reason`: at most 25 words.
- Write one row per input row, in input order. Be strict: when the page leaves it unclear, the verdict is PARTIAL or
  NOT_SUPPORTED, not SUPPORTED.
