# IAF CertSearch — CLOSED (public extraction route), 2026-11-06

Terms checked before any certificate query. No certificate records fetched. Polymer-slice count, dedupe, 20-row sample and yield are **not measured**, not zero. `sample.csv` is header-only because the terms gate stops the scout.

[Live terms](https://www.iafcertsearch.org/policies/terms), YOUR DATABASE ACCOUNT:
> You may not copy, modify, distribute, sell, or lease any part of our Database

The same terms' INTELLECTUAL PROPERTY RIGHTS section also reserves reproduction/derivative works for commercial **or non-commercial** purposes without written permission. This is a copying/publication restriction, not a claimed verbatim ban on every form of automation. The public route is unsuitable for an Atlas extraction absent authorization; stopped before sampling. [Official API guide](https://support.iafcertsearch.org/verifiers/api-verification/api-verification) requires an Enterprise subscription. No paid service was used.

Route: headless GET returns the React shell (HTTP 200). Terms text was read raw from its public JS asset, `https://f0.iafcertsearch.org/assets/service-main-p-751893871/PoliciesTerms.e319bd7f.js`; the terms-page main asset points to that exact chunk. The prerender route returned an error; Jina required authentication. Neither error says anything about certified entities.

| Hold | Settling fact | Recommendation |
|---|---|---|
| IAF public redistribution | Written authorization permitting the intended Atlas use | Keep public extraction CLOSED; certificate holder's own current certificate remains a separate primary route under SCHEMA §3.4 |

No ISO, IATF or AS9100 coverage claim was tested. No certification fact enters data/.
