# Lane L5 notes (MI STRONG wave, 2026-11-04)

Result: 21 clusters. VERIFIED_NEW_SITE 2 (tier B), VERIFIED_NEW_ORG 16 (tier C), STILL_UNCERTAIN 3, REJECT 0, DUPLICATE_OF 0.
CSV parse check: 21 rows, 22 columns each, cluster IDs match input.csv exactly, no quote over 25 words.

## Integrator must re-check
- Quotes came through WebFetch, which summarizes with a small model. I used only spans it returned in quotation marks, but none was independently re-read. Re-fetch each `own_url` and compare words before applying. Weakest: Preferred Plastics (4-word menu link text), Renosol and Diversitak (company-level text, plant named elsewhere on the page).
- Tier C for every new org follows the brief ("a new organization is C") even where an own-site witness exists. Rows with a plant-naming own page: Plascon, Royal (B), Harbor Foam (B), Mayfair, Renosol, Vantage, Preferred, Premier, DT, RheTech, Diversitak, Wright (address only).
- Rows where the own site does NOT name the plant (federal-only for the site): 21st Century Plastics, AirBoss Flexible Products, Western Diversified (address in contact block only), United Paint (address only, activity not tied).

## Dedupe results
- `atlas.py dedupe-check` (name + street + city) returned 0 hits at steps 2-4 for the ten clusters I ran it on (Western, Mayfair, Diversitak, Plascon, 21st Century, DT, Harbor Foam, Dipsol, AirBoss, United Paint); the other clusters were checked by grepping the organization shards for the name, which found nothing except the cases below.
- LF-MI-00612 Royal Technologies: ORG-004107 held; no Hudsonville site exists in sites_MI.csv, so VERIFIED_NEW_SITE (Corporate Grove, 2905 Corporate Grove). Royal Center (3765 Quincy) and Quincy I/II (3712 Quincy) are further candidate sites not in this packet.
- LF-MI-00416 RheTech: step-4 hit ORG-001078 is Rhetech Colors (Sandusky OH). RheTech's own page calls RheTech Colors its "sister company", so I treated Whitmore Lake as a different entity (new org). Both are HEXPOL-branded; HEXPOL Compounding ORG-000103 / ORG-002044 are held. Parent links are the integrator's call. If the owner wants one RheTech org, this flips to VERIFIED_NEW_SITE under ORG-001078.
- LF-MI-00534 Harbor Foam: Alleguard (ORG-000802, Lancaster OH) announced the acquisition, effective 2024-08-06. Filed as a new site under ORG-000802; alternative is a separate org with parent link. Integrator choice.
- LF-MI-00892 AirBoss Flexible Products: same parent (AirBoss of America Corp.) as held ORG-003437 AirBoss Rubber Solutions, but different division and LLC; filed as new org.
- LF-MI-00253 Mayfair: Husco acquired Mayfair in 2026 (Husco page). Husco is not held.

## STILL_UNCERTAIN
- LF-MI-00463 Dipsol of America: own site not reachable (dipsolofamerica.com does not resolve). Third-party descriptions say plating chemistry (zinc-nickel, electroless nickel, conversion coatings, sealers/topcoats). Settling fact: own product list showing polymer-based topcoats/sealers, or none.
- LF-MI-00985 Lawrence Plastics: lawrenceplastics.com fails TLS (cert for *.cloudaccess.net). Availability only. Third-party says injection molder, Clarkston, 117,000 sq ft.
- LF-MI-00302 United Resin: owner's page (Chase Corporation, info.chasecorp.com/united_resin) says "Manufacturing Operations are Relocating": products transferred from Royal Oak to Pittsburgh. No date for the transfer, no word "closure". This is not a dated closure, so not REJECT. Federal activity is old (2020-10-21). Watch item.

## Other observations
- 21st Century Plastics: directories say 300 Wright Parkway; federal says Wright Industrial Pkwy. One directory shows a Grand Ledge location. Neither verified.
- Premier Protective Packaging converts PE foam/bubble/SBPP (die-cut, laminate, bag/pouch). Ring is borderline (Ring 1 converting vs Ring 3 contract services); an owner ruling on scope/ring is not made here.
- United Paint: coatings formulator for plastic substrates; binder/resin never stated, so scope rests on the Ring 2 coatings precedent.
- US Farathane: Dec 2023 Plastics News story on a Michigan plant closure has a Shelby Township URL; nothing found tying it to Lake Orion. A search summary also tied LymTal International to 4150 S Lapeer Rd (a different address), not this site.
- No Form 5500 check was needed: no REJECT for closure or no-establishment.
- Counties blank in the federal row (Auburn Hills, Clarkston, Standish, Clinton Twp, Plainwell, Grand Rapids, Bay City, Royal Oak) were filled from geography, not from a document; verify against the Atlas county rules.
- Fetch effort: roughly 4-8 calls per cluster including searches; several own sites returned DNS or TLS errors, which I treated as availability only.
