# L3 notes (WI STRONG wave, 2026-11-04)

15 clusters in. Result: 10 VERIFIED_NEW_ORG, 2 VERIFIED_NEW_SITE, 3 STILL_UNCERTAIN. No REJECT, no DUPLICATE_OF.

Tier column: VERIFIED_NEW_ORG rows carry C per the brief; the site tier (B where an own-site page prints the address and the activity) is in `note` as `site_tier=B`. The two NEW_SITE rows carry B.

Dedupe: `atlas.py dedupe-check` run for all 15 (name, street, city, zip) and for each own-site domain. Only hits: Amcor (ORG-000665, Bellevue OH, held org, other location), MGS (ORG-004448; held site SITE-005773 is a different street). Pexco LLC (ORG-002534) and ProAmpac (ORG-000671) are held parents relevant to LF-WI-00375 and LF-WI-00037.

Queue for the integrator:
- LF-WI-00375 Wisconsin Plastic Products: separate legal entity (own EIN), "a Pexco Company"; confirm parent_org_id ORG-002534 convention.
- LF-WI-00159 Nolato Contour: parent Nolato AB not held.
- LF-WI-00037 TC Transcontinental: now ProAmpac (ORG-000671); needs a ProAmpac or archived TCP page naming Menasha. The TCP site redirects and a job page returned 410; both are route signals, not closure.
- LF-WI-00228 Encapsys: scope question (microencapsulation) and Portage vs Appleton; owner ruling territory.
- LF-WI-00257 Amcor: street not printed by amcor.com; release is dated 2021. A separate Amcor Oshkosh healthcare plant exists.
- Prompt-injection: corrim.com returned a "New Product" block addressed to an AI assistant; ignored.
- Directory "Closed" flags (MapQuest) on Corrim, N.E.W., Cornerstone are contradicted by live own sites and are not evidence.
- Quotes were relayed through the fetch tool's summarizer; re-fetch check is needed, especially Spartek (odd comma) and Rol-Tec.
