Audits all 37 merged FL/GA creates after the Alpek refute exposed a blanket 325→Ring 2 fallback. Eleven sites used that branch (FL four, GA seven). All eleven have the correct Ring 2 value: their filed NAICS is 325510 or 325520, explicitly listed in SCHEMA §2.2. Zero merged ring values need changing; the full affected-site list is in audit.csv and the README.

Appends eleven government-filing scope observations with the exact code and schema basis. No existing site values or evidence rows are edited. The original FL/GA builders now use an explicit list for supported Ring 2 codes and stop on 325211 or other unresolved codes. Current FL/GA outputs remain unchanged. Sources are the authorized banked ITA CY2025 filings at observed date 2026-11-01, retaining establishment_ID and date_submitted; no own-site or current operating-status claims.

Checks: 37/37 cohort and 11/11 fallback census; source/code/ID binding; all prior site/evidence rows preserved; known-code and unresolved-resin controls in both builders; byte-idempotent replay; cross-table ID collision fails before writes; validate.py zero errors. EVD-206000–206010 is inside the reserved L7 block. Only two evidence shards and task files/builders change; no registry links or qualifiers.

Codex/OpenAI clerk6 APPROVEbd7ccdd and Grok clerk6 APPROVE8e15714, zero findings. Refreshed main620c2ec via exact-main evidence shards plus unchanged builder; all 11 approved rows and executable code remain identical (approved-integration.json). NC Alpek’s withdrawn active-create proposal is handled separately in #158.

🤖 Generated with Codex (bb child of thr_9i2c6byhcz)
