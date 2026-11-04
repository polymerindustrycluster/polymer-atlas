# Lane brief: scope evidence repair, round 2 (2026-11-04)

Each input row is a Polymer Atlas evidence row of claim type `scope`. Its cited page, re-read on 2026-11-03, did
**not** fully state the claim. `verdict` and `reason` say what was missing, and `claim_detail` is the claim. Usually
the cited page is a corporate or group page that does not name the specific site.

Your job is to find **one public page that states the claimed polymer activity for this site or organization**:
1. Best: the company's own page for **this plant or location**, stating what is made or done there.
2. Next: a government filing that names the facility and its activity, such as an EPA permit or a state air permit
   (`government_filing`).
3. Otherwise: dated trade press naming the plant and its activity (`press`).

Directories and aggregators do not count, and neither does the page already cited.

About 4 fetches per row. A failed fetch is never evidence. If the evidence shows the activity is **different**, the
plant closed, or it moved, use `CONTRADICTED` and quote it.

## Output CSV
`evidence_id, outcome, source_class, source_url, quote, note`
- `outcome`: `FOUND`, `NONE_FOUND` (name what you searched) or `CONTRADICTED`.
- `quote`: at most 25 words, copied **exactly**. The integrator re-fetches every URL raw and keeps a row only when the
  words appear in order. **Never edit any repo file and never run git.** No emails, phones or personal data.
