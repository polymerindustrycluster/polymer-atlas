# Final residual HQ4 — packet B

Researcher residual-hq4-b; observed 2026-11-06. Frozen input: **24 organization IDs**, positions226–249, SHA-256 `1715fc1c9a2afbc0787e63c778f3cee50b52eb7039c2689209e33c24a7ac1c37`. Parent frame base: `8a5821b37e308a31b22ed57015edb54636641f1c`.

`verdicts.csv` accounts for all24 IDs: **6 HQ_FOUND proposals,16 research holds,2 ownership holds**. ORG-009017 and ORG-009026 are explicitly L3-owned exclusions: zero fetches, blank HQ/evidence fields, no research or canonical edits. Every hold has an explicit `settling_fact`.

Proposals: Wikoff Color Corporation, Fort Mill SC; Sun Drilling Products Corp, Belle Chasse LA; ASH Industries, Lafayette LA; Watkins Wellness, Vista CA; Cal Spas, Pomona CA; Scientific Specialties Inc, Lodi CA. All witnesses own_site, all counties blank without evidence. Unknown operating status stays unknown; an HQ fact is not status reverification. No confidence autofill, contact/plant/mailing inference, parent HQ transfer, or LEI-only promotion.

`receipts.csv` contains **58 actual browser-UA curl attempts across22 eligible organizations**, including repeated routes and failures. Maximum4 used, below cap5 and reserving integrator verification. Every attempt has URL, HTTP result, raw SHA-256 and temporary path. All raw HTML/PDF, extracted PDF text and research code remain only in `/tmp/residual-hq4-b/`; no full pages, personal contacts or emails in the packet outputs.

Sun identity is explicit, not inferred from domain: own COASTAL SPOT SDS, effective2023-03-31, Section1 manufacturer, states **SUN DRILLING PRODUCTS CORP. d/b/a SUN SPECIALTY PRODUCTS**. Already captured at attempt4: https://sunspecialtyproducts.com/wp-content/uploads/2024/09/2023-SDS-COASTAL-SPOT.pdf . Raw SHA-256 `29390133a14f0f71b89ad7a2307eecc956589df58c50660338d356087a6a5e35`; raw PDF and pdftotext-layout output are in the temporary cache. The current own about page separately explicitly identifies Belle Chasse headquarters. This identity bridge was sent to L5b without another fetch.

Cal Spas uses its current company narrative. Watkins uses its company-specific careers about page hosted by Masco, not Masco global HQ. Wikoff uses its dated2026-09-01 release naming Fort Mill HQ. ASH explicitly labels its own corporate office. Scientific Specialties privacy policy updated2026-06-23 explicitly names the legal entity and headquarters; ` || ` separates two same-page excerpts. Each positive page contributes at most25 quoted words.

Holds include DELFINGEN-TX rather than French group head office; CMP Coatings US sales office/factory rather than headquarters; NDS redirects to ADS brand content rather than exact legal HQ; MSRS/VM International lacks exact Buy Low Wholesale identity/HQ evidence; Norton has an indexed Hayward HQ lead but both raw routes returned403. Failure is an availability observation, never evidence of absence. No indexed quote alone was promoted.

Coordination agreements with sole integrator L5b `thr_ii6ybubss4`: this is the final batch, no continuation; helper owns only this lane folder; two L3 exclusions untouched; max5 helper routes plus integrator reserve; exact-entity primary HQ standard; registry-address evidence capsC and cannot lower held A/B; county unsupported stays blank; status/tier/qualifier/site changes barred. L5b independently raw-passed Cal Spas calibration, captured it once in HQ4 `rawcheck.json`, and will reuse it. Sun bridge is already captured within cap. No data, Git, branch, settings, queue, tracker or task-status writes by this lane; no independent Done approval claimed.

Runnable check from repository root:

`python3 tasks/residual-hq-4-2026-11-06/lanes/b/check_packet.py`

**PASS:**24/24 unique frozen IDs/names, exact headers,6 positive quotes raw-matched as contiguous normalized words,58 raw hashes, eligible fetch counts reconciled to unique receipt attempts, both exclusions at0 fetches with blank evidence, specific hold facts, no county fill. Three positive known answers: Cal Spas company narrative, ASH corporate-office block, Scientific Specialties legal/privacy HQ statement. Additional checks: Sun legal/DBA PDF identity and DELFINGEN parent-HQ hold. Six deliberate faults fail: missing ID, duplicate ID, invented quote, missing header, empty settling fact, research count on excluded ID.

Rerunning requires the temporary raw cache and pdftotext; missing raw files fail closed. Parent integration, repository validator/replay, and independent Codex/Grok review remain parent responsibilities. Packet research stops after delivery.
