# Lane L5 notes (2026-11-03) - columbia, nyu, yale

Counts (examined / VERIFIED / REJECT / STILL_UNCERTAIN):
- nyu: 20 / 8 / 3 / 9. Pages: engineering.nyu.edu CBE people directory (Gate A stylings) + 19 individual faculty profiles; wp.nyu.edu/kirshenbaumlab. as.nyu.edu returned HTTP 405 (3 URLs) and nyuscholars.nyu.edu HTTP 503, so Weck and Kirshenbaum are STILL_UNCERTAIN.
- yale: 10 / 3 / 4 / 3. Pages: engineering.yale.edu individual profiles (names from the CEE research-areas page); chem.yale.edu Zhong profile. The Yale faculty directory is script-rendered and returned no names, so the roster was not enumerated and Yale chemistry/MEMS/physics were only sampled via search.
- columbia: 9 / 1 / 0 / 8. Every columbia.edu host returned HTTP 403 except obermeyer.cheme.columbia.edu (cheme., chem., engineering., me., magazine., gang.cheme., mrsec., plasticnetwork.climate., www.columbia.edu/cu/kumargroup). The 8 STILL_UNCERTAIN names come from web search result lists only, not fetched pages; no quotes recorded for them.

Other points:
- Yale is NOT in data/organizations_CT.csv, ecosystem.csv, or any data file by name (grep for "yale" hits only unrelated Royale rows), contrary to the lane assignment. Integrator needs to check/create the Yale institution record.
- already_in_atlas: no name from this lane matches data/people.csv.
- institutions.csv: polymer_unit left blank for all three. NYU's CBE page says "Korley leads the Center for Plastics Innovation" (appears to be her prior-institution center; not confirmed as an NYU unit), so I did not record it. Columbia legal name is as given in the lane assignment, not read from a fetched page.
- Gate quotes come from WebFetch's extraction of each page (a model summary, not raw HTML). Spot-check before integration; the Modestino Gate B quote is a paraphrased listing.
- Weak-but-stated Gate B VERIFIEDs worth an integrator glance: Levicky, Modestino, Taylor, Pine (NYU); Kyriakides (Yale). Montclare's Gate B quote is from a news item hosted on her profile.
- Zhong (Yale) rank differs between Yale pages; recorded associate_professor.
- Not re-tried after HTTP 403/405/503 per proxy guidance; these are availability signals, not evidence.
