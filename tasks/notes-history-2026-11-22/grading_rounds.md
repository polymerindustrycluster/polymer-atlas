# Hand grading of the splitter (read by the lane, as the company's owner would; unit = piece of a note)

Question per piece: does what the script decided leave the owner a clean, true row, and lose no fact the owner needs (a fact with no column of its own)?
Samples are seeded, drawn with `grade_sample.py` (and the MOVE draw inline, seed 20261126). Pieces are sentence-sized segments from `notes_split.pieces`.

| round | pool | seed | n | drawn after | wrong | rate | what was wrong |
|---|---|---|---|---|---|---|---|
| 1 | plain-unlisted (no word-list hit, not a known template): would be KEPT by default | 20261122 | 70 | first word list | 25 | 36% | pipeline talk without a listed word: "legs", "upgrade path", "settling fact", "quote span", "NAICS ... coded from capability text", "(R-05)", fragments from abbreviation splits |
| 2 | same | 20261124 | 70 | + jargon class (case-sensitive) | 17 | 24% | "Tier A" tails, "Ring 3", "carry 326199 as secondary", first-person lines ("I did not treat..."), packet ids, case-sensitive misses |
| 3 | same | 20261125 | 50 | + case-insensitive jargon, Ring N, witness, adjudicate | 7 | 14% | federal packet id strings, "Integrator may prefer U", "Green presence to resolve at verification", one source fragment |
| M | MOVE (not an obvious header) | 20261126 | 70 | final | 3 (4%) | 4% | a fact swallowed by a pipeline lead-in: an own-brochure address confirmation behind "Coordinator ... lead confirmed"; own-site facility address behind "Atlas Tier U burn-down"; a TRI-parent caution |

Conclusion used in DESIGN §6: the script moves pipeline text with ~4% loss of reader facts (audited, and nothing is lost from the repo because history keeps it),
but defaulting unlisted plain text to KEEP leaves ~14% pipeline talk on rows after three rounds of word-list repair. A reader or a second model pass has to
decide the unlisted pieces. Round 3's 14% is on n=50 (95% interval roughly 6% to 27%).
