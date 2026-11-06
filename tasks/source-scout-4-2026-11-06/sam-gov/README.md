# SAM.gov public entity extracts — CORROBORATION_ONLY, credential/route hold

Scope: terms and route assessment only, per controller06:30 continuation. No entity extraction or record verification claimed.

[Official SAM terms](https://sam.gov/about/terms-of-use), Full Legal Language:
> Automated data gathering, web scraping tools are prohibited

This is read with the same terms' Data Access/API provisions: software may connect with permission and public sharing must use public APIs. It is not interpreted as banning the explicitly documented extract API. Browser scraping/Login.gov automation is CLOSED; authorized PUBLIC extracts remain the viable path. Terms page raw-fetched HTTP200 and the quote checked.

[Official GSA extract API documentation](https://open.gsa.gov/api/sam-entity-extracts-api/) documents `GET https://api.sam.gov/data-services/v1/extracts?fileType=ENTITY&sensitivity=PUBLIC&api_key=<key>`; Public access requires an individual account/key or a system account with Read Public. No SAM-named key/token is present in this process environment. The anonymous endpoint request returned HTTP404 with an empty body, not a dataset; this does not establish authentication failure as the root cause and is not evidence no extract/entities exist. Authenticated retrieval NOT TESTED. No account creation, key request, login automation or paid service used.

Monthly PUBLIC ASCII `SAM_PUBLIC_MONTHLY_V2_YYYYMMDD.ZIP` or UTF-8 equivalent: first Sunday after7am Eastern; includes active registrations and entities expired in the last6months. Never describe that frame as all active firms. Production public Entity/Exclusions Extracts API is distinct from procurement opportunities API and exclusions-only extracts. Explicitly request PUBLIC; do not obtain FOUO/CUI/Sensitive/opted-out information for publication. Even public extracts require projection that excludes individual contacts and potential home-address records before Atlas use.

Polymer slice, dedupe, sample, yield and CI: NOT MEASURED; header-only sample.csv. A future scout would select explicit schema core NAICS, verify IDs in the extract, run domain/name/street/alias dedupe, and verify operations separately. Registration/eligibility is not operating activity. No NAICS fact, UEI/CAGE link or entity row applied.

| Hold | Settling fact | Recommendation |
|---|---|---|
| Authorized route | Working Read Public credential and successful PUBLIC extract retrieval | CORROBORATION_ONLY pending route test; no inference from anonymous404 |
