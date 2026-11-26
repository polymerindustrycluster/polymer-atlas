# SITE-000056 street from the operator's own contact page (owner ruling 2026-11-26 14:51, "Look up named source")

Built by: Claude Code (Anthropic)

Claimed by atlas-p2-note-street-lookup on 2026-11-26. First user is City of Akron economic development staff (the user of the PIC-18 street fills in `tasks/pic18-map-streets-2026-11-24/`). Check for use by 2026-12-20. Base `f921eba8`.

## Result

**One street cell filled: SITE-000056 (CF Extrusion Technologies, Cuyahoga Falls, tier A) takes `2748 2nd Street Suite C`.** Unit and filter: active Ohio PIC-18 tier A-C sites with a blank street; the base holds 152, this head 151. The evidence row `EVD-483296` is an own-site `address` row, role physical, `supports_A`: the operator's own contact page prints `Shipping/Receiving 2748 2nd Street Suite C Cuyahoga Falls, OH 44221`, and its P.O. Box line (a postal address, not used) is separate. Wayback `id_` capture 2026-08-11 (the live page's bytes change on every fetch, the capture's do not); the live page printed the same block on 2026-11-26. The quote is at character offset 596 of the capture's main text. No other cell changes, and no note is edited.

This uses the ordinary own-site street route, not the map-listing route the ruling named: that route reads its second source only from rows already on the base tree, so a same-PR own-site row cannot serve it (measured; see the thread packet `note-street-lookup-2026-11-26/README.md`). The other five sites of the lookup are not in this PR: SITE-001793 and SITE-001798 print the street only in the page footer, which the gate's main-text extraction excludes; SITE-000212, SITE-000362 and SITE-001473 are STILL_UNCERTAIN, each with the named fact in `verdicts.csv` of that packet.

## Caveats a reader should weigh

The page labels the street "Shipping/Receiving", not plant or headquarters, and does not say the firm moved. The note's "moved to" wording is what led the 2026-11-17 lane to hold it SUPERSEDED_OR_HISTORICAL; the live page shows the street current on 2026-11-26, and Overture and Google list the business open at 2748 2nd St. The row's `zip` cell is blank and stays blank (the page prints 44221); this route fills the street and nothing else.

## Reading by another family

Codex (OpenAI, GPT-6.2 Astra, `council-ask codex --effort deep`, 2026-11-26) read the page's whole 1,208-character main text with the quote and offset, told to try to refute: quote exact at offset 596 (67 characters); the page is the operator's own and names CF Extrusion Technologies beside the address; "Shipping/Receiving" is the physical premises, with the P.O. Box listed separately for office mail; no individual's email, direct line, mobile or home address attached to the quote; no conflicting street, move or closure notice on either copy. VERDICT: VERIFIED. The reading is `READING_CODEX.md`; `BINDING_PROOF.csv` holds the line (claim hash unchanged from the evidence row).

## Checks

`python3 tasks/note-street-lookup-2026-11-26/check.py` is the named check. It asserts one changed cell equal to `CLAIMS_CHECKED.csv`, base blank and head the pinned street, the blank-street count down by exactly one, the evidence row pinned and exactly one row added with none changed or lost, the gate's own mechanical verdict for the row (`READ_REQUIRED mechanics_clear`), the proof line (claim hash, VERIFIED, non-Anthropic reader), the archive link, the capture digest, the quote at its offset in the capture's main text, no unreviewed email address in the capture, and no file outside the allowed set. 14 planted defects are rejected, each for its own rule; one of them is judged by the gate itself (a record street that the quote does not print: `FAIL street_absent_from_quote`). The capture is read from the shared store (`provenance/note-street-lookup-2026-11-26/`); this check fetches nothing.

`tasks/ppp-size-bands-rerun-2026-11-26/AUDIT.md` is added verbatim from `reviews/573/AUDIT.md` (sha256 `2c199acaf2d0e12a0a46de60ad70d111e28ad51ad320813c54c3518d45ca1ec5`) because #573's label is audited there and AGENTS section 2a rule 5 needs it on `main` before a `data/` PR passes `pr-rules`.

## Not checked

CI's live replay of the Wayback capture (`--verify-proofs` fetches with another user agent; not run locally). `check_pr_rules.py` (needs GitHub facts). Whether Overture and Google both list the plant as open was read from the 2026-11-24 street-gaps packet, not re-fetched.
