# PIC-18 street fills from held establishment filings

Built by: Codex (OpenAI)

Claimed by atlas-p1-street-gaps on 2026-11-24. First user is City of Akron economic development staff. Check for use by 2026-12-20. The approved set combines two original candidates and 17 same-street operator holds. Wrap Tite is in both groups, so the set covers 18 distinct sites. The base has 155 blank streets among 879 active Ohio PIC-18 sites at tier A, B or C.

## Result

Two physical address fills passed the full screen and the binding gate. SITE-000650 (tier C) comes from an OSHA inspection and SITE-000678 (tier A) from the ITA establishment record for Wrap Tite Site 3. Both sources state the existing ZIP. The packet adds two address observations and changes two `street_address` cells. The active tier A–C PIC-18 frame goes from 155 to 153 blank streets. No inclusion-log calls or record creates.

The 17 original refusals comprise 11 private-address screen hits and six normalization misses. The privacy screen tests the raw and normalized filing name. A hit can arise from a short name with the corporate form removed. Alternate parent-only quotes fail the held-name rule as well. BASIS.csv gives the founding filing label, original name refusal, prior notes class and remaining filing-level screen results. The site screen also evaluates physical role, locality and ZIP, filing date, same-locality siblings and occupied streets, and applicable registry links and source strength. Required screen conditions apply even if the binding gate passes the proposed quote.

| Site | Original name refusal | Disposition after the full screen |
|---|---|---|
| SITE-000004 | Private-address test | Held. The other filing labels also include different names and localities. |
| SITE-000061 | Normalization miss | Held. The parenthetical qualifier changes the filing name, the clean inspections are from 1984, and the prior notes hold two streets. |
| SITE-000212 | Private-address test | Held. Other structured quotes do not name a held operator. |
| SITE-000214 | Private-address test | Held. The held ZIP also conflicts with the filings. |
| SITE-000220 | Private-address test | Held. The alternative inspection is outside the filing window and registry strength is below the site tier. |
| SITE-000252 | Normalization miss | Held. The full establishment name passes the gate with ZIP 44146, and the local screen still finds Bedford versus Bedford Heights. Other quotes include a parent-only name. |
| SITE-000255 | Private-address test | Held. The inspections are from 1993. |
| SITE-000589 | Normalization miss | Held. The expanded name passes the gate, and the prior physical ZIP conflict remains. |
| SITE-000605 | Normalization miss | Held. Same-locality sibling and no gate-passing filing at the site street. Some filing names are parent-only. |
| SITE-000678 | Private-address test | The BDG form stays held. The separately approved ITA quote names Wrap Tite Site 3 at 6250 Camp Industrial Road and distinguishes it from the other plant on Cochran Road. |
| SITE-001480 | Private-address test | Held. Some filings also differ in locality or ZIP. |
| SITE-001524 | Private-address test | Held. The prior office-versus-plant and ZIP conflicts remain. |
| SITE-001676 | Private-address test | Held. The prior dated-filing conflict remains. |
| SITE-001720 | Normalization miss | Held. Same-locality sibling and prior two-street hold. The gate rejects held-name and parent-only quotes. |
| SITE-001855 | Normalization miss | Held. Prior two-street hold and `name_not_held` at the target street. |
| SITE-001923 | Private-address test | Held. Several alternative quotes also fail locality or registry strength. |
| SITE-002050 | Private-address test | Held. The previous notes flag historical or superseded information. |

FILLS.csv identifies each selected raw locator, exact filing name field and evidence ID. CLAIMS_CHECKED.csv accounts for the two changed cells and the 153 remaining blank-street sites. INPUTS.sha256 identifies the two shared-store inputs used for the applied evidence. No web sources were fetched or used.
