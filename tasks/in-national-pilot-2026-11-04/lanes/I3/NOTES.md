# Lane I3 notes (2026-11-04)

Counts (17 clusters): VERIFIED_NEW_ORG 6 (all tier C), VERIFIED_NEW_SITE 6 (all tier C), STILL_UNCERTAIN 4, REJECT 1, DUPLICATE_OF 0.
No tier B: no new site had a single own-site page naming both plant and in-scope activity, and new orgs are C by rule.

Method: `atlas.py dedupe-check` (all four steps) per cluster, `show` on held orgs, then company-site fetches (WebFetch/WebSearch).
Fetch budget was tight; several sites returned 404, expired certificates or bot walls. Those are availability signals only.

Integrator re-check list
- Quotes marked "relayed by fetch tool" (Priority Plastics, MonoSol x2, Triangle, DeKalb, Futurex, Polywood, Pregis) came through a summarizing fetch model, not raw HTML. Verify the wording against the live page before use.
- Tenneco quote is from a PDF (pdftotext), line-wrapped in a two-column layout; the span is continuous in reading order.

Traps found
- trianglerubber.com is Triangle Rubber Co. of Bohemia NY. The Goshen company is trianglerubberco.com.
- LF-IN-00512 fusion_refs ORG-001404 (Deflecto) looks spurious; no Deflecto link to Priority Plastics found.
- Held org ORG-004456 (MonoSol) records HQ Lebanon; MonoSol's current locations page gives HQ 1500 Louis Sullivan Dr, Portage. Correction candidate.
- Tenneco: only held Tenneco org is ORG-001582 (HQ recorded Van Wert OH); integrator chooses the parent for Angola.
- Polywood: 1000 Polywood Way vs held SITE-005893 at 1001 West Brooklyn Street; confirm distinct building.
- Futurex: federal 169 E Smith St is an ITA "Finance Office"; own site prints 70 N Main St and 80 E Smith St. Two Futurex rows (00371, 00603) share one new org.
- Pregis Plymouth: own site evidences paper only; polymer scope rests on 2014 press release and federal NAICS.

Closures: none found for any cluster. Premier Magnesia is a scope reject, so the Form 5500 closure gate does not apply.
Not done: no Form 5500 lookups were needed; GTA, Keter, APR and Orion were left uncertain rather than guessed.
