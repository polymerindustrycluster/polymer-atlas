# ACMA composites directory — CORROBORATION_ONLY

Observed2026-11-06. Headless HTML at [Member Directory](https://acmanet.org/membership/why-membership-matters/membership-directory/) returns the Vue shell. Its shipped site JS calls the public same-origin [directory JSON](https://acmanet.org/wp-json/mg/v1/content/directory?type=&state=), which returned HTTP200 without login/key. No authenticated endpoint or account was used. The public list has **252 unique directory record IDs**, **121 Manufacturer listings**; the exact sampling slice is **98 Manufacturer listings with a US state/DC and opt=false**, sorted by recordId. Listing/company-location grain, not distinct legal parents or establishments. No claim every composite is polymer-matrix; category is a lead.

Terms check: [Terms and Conditions](https://acmanet.org/tcs/) is primarily the site's posting policy. Raw-checked excerpt:
> Postings may not violate or infringe copyright, trademark, trade secret, privacy, personal publicity or proprietary rights.

It does not establish a public roster redistribution grant. [Privacy policy](https://acmanet.org/privacy-policy/) addresses member information. Publication rights stay held; public accessibility is not rights clearance. Do not mint public member_of edges from this scout. API opt=true listings were excluded from sampling; no profile/contact field is exported. The public detail endpoint exposes individual email/contact information and was therefore not harvested. Source count metadata and a minimal20-row factual lead sample only, not a full roster.

Sample: uniform draw without replacement, seed20261106, from the98 sorted listing IDs. **16 DUPLICATE_OF held organization IDs, 4 STILL_UNCERTAIN, 0 VERIFIED new**. Verified-new organization-lead yield **0/20 = 0%, Wilson95%CI 0–16.11%**; descriptive interval at directory-listing grain, not a parent-level census estimate. Existing Atlas coverage dominates this sample. One own-site homepage request attempted per listed URL; a missing website is explicitly uninspectable. Homepage keyword snippets are discovery signals, not adjudicated scope evidence. Four uncertainties: American Woodmark, Gordon Development, RL Industries (multiple held identity candidates), Modern Welding. Modern Welding's steel/fiberglass comparison does not establish polymer manufacturing; no scope REJECT/self-ruling.

All-shard dedupe uses scripts/atlas.py: domain, normalized legal/trade name, then aliases/notes. Street is unavailable in this list API, so no street/site absence claim is made. `duplicate_of` is the singleton domain/name hit; `atlas_ids` additionally preserves looser candidates and must not be read as multiple merged identities. No closure REJECTs. Source categories never carry a polymer scope claim.

`scout.py` KAT distinguishes US/non-US/opted-out Manufacturer records before sampling; root oracle checks the20 unique IDs/names, verdict counts and held duplicate endpoints. The source's121 Manufacturer category is not a polymer-scope count;98 is a polymer-discovery slice only.

| Hold | Settling fact | Recommendation |
|---|---|---|
| Directory publication | Explicit reuse right/authorization for public membership snapshots | CORROBORATION_ONLY, no edges |
| Four identity/scope uncertainties | Primary polymer-process evidence and legal identity/US business address | No create or merge from category or substring alone |
