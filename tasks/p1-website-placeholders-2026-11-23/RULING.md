# Controller ruling on blank_if_ruled.csv (P1 controller, 2026-11-23)
This applies an existing schema rule; it does not change the schema. SCHEMA line 980 says website is "MUST if exists; explicit `none_found` otherwise".
- The five cells that already say none was found ("none found" x3: ORG-001706, ORG-001710, ORG-001712; "https://none found/" x2: ORG-001689, ORG-001692) become the schema marker `none_found`. They keep their meaning in the marker's spelling.
- The four cells that do not say a search found nothing become blank, meaning not yet known: "none fetched" ORG-002036, "A2LA scope document" ORG-001961, "own-site warranty page" ORG-001990 (this one implies an own site exists, so `none_found` would be false), "manufacturer listings (ARCAT)" ORG-002016.
- My earlier instruction to blank every placeholder was wrong for the first five. The lane caught it against SCHEMA.
