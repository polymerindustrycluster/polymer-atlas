# Lane L2 notes (CA STRONG wave, 2026-11-04)

20 input clusters, 20 verdict rows. Counts: VERIFIED_NEW_SITE 1 (tier B), VERIFIED_NEW_ORG 10 (tier C),
REJECT 2, STILL_UNCERTAIN 7, DUPLICATE_OF 0.

Dedupe: `atlas.py dedupe-check` run for all 20 (name + street + city). No street hit anywhere. Name hits only for
Pactiv (ORG-002537, PA), Sealed Air (ORG-000566, NC) and Plastipak (ORG-001033, OH), all parents in other states.
The step-4 hits for Global Plastics (Unistar Plastics LA; Global Plastics Equipment & Services OH) are unrelated companies.

Review first:
- LF-CA-02234 Santa Fe Rubber: site has an expired TLS certificate; quote taken from page title/description via
  search. Re-fetch with cert checking off before applying.
- LF-CA-00940 Plastipak Modesto: own page only lists "Modesto, CA" as a plant. Held back under B14; one fact from
  promotion to B.
- LF-CA-00775 Crossfield: own page names the Rancho Dominguez plant and company-wide coating production in separate
  sentences, so the site-level activity is inherited.
- LF-CA-02553 Al's Plastics: recycler/converter and trader; ring call (1/3 recycling vs 3 distribution) is the integrator's.
- LF-CA-00175 Pactiv Bakersfield: REJECT on dated trade-press closure (Packaging Dive, 2025-08-20, WARN-based, plant
  closing Oct 14, 2025). No F5500 source in the cluster, so the 5500 gate does not block.
- LF-CA-00722 MP Associates: REJECT as explosives maker, but the evidence is third-party directories; own site unreachable.

Fetch problems (availability only, never used as evidence): milgard.com 403, hunterirrigation.com 403,
plasticsnews.com 403, garratt.com parked (the real site is garrattcallahan.com), mpassociates.com connection refused,
qycell.com redirects to a for-sale page, plastipak GRI PDF 404.

Method note: WebFetch returns model-summarised text capped at about 125 characters per quote, so quotes are short
fragments. The integrator's exact-match re-fetch is the real check; several quotes carry a dropped trailing comma
(still a substring of the page).

Fields left blank on purpose: org_hq_* where the page does not label an HQ; naics_primary where the federal NAICS set
is mixed; processes/materials where the page does not name them. Counties for Laguna Hills, Irvine, Ontario and
Pomona were filled from the city because the federal row was blank.
