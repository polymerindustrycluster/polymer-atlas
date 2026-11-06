Try to REFUTE completion of L14 equipment wave2. Read SPEC.md, README.md, inputs.csv (all canonical output fields + raw per-row quotes), verdicts.csv, holds.csv, source-fetches.csv, build.py, check.py and logs. SHA256 manifest review-packet.json covers the packet; inspect complete artifact before verdict. Use the branch/PR ref if the worktree has moved. Independently fetch own pages, inspect grain, class, access, optional CAMP FK and exact held host identity; challenge all 54 rows and all source/host holds, particularly NASA material instruments, multifunction lines, Ohio published spellings, Penn State DSC/FSC, CSU SLA and rheometer class. Equipment §4.19 is the contract; §4.13 excludes equipment from EVD record_table. No organization/site, registry or operating-availability change is authorized.

Scope: only data/equipment.csv gains 54 rows EQP-000100..000153 (5 Ohio institutions/41 rows; 3 Pennsylvania/13). Existing 34 equipment rows must be byte/value preserved. No tier column exists. Seven UC fee_for_service,47 not_stated; only 6 Ohio University CAMP program FKs, no sites. 10 STILL_UNCERTAIN holds, six source/host cases and four list-grain/class cases. Own pages only, no aggregator/CRM/licensed/contact content.

Re-run:
python3 tasks/equipment-wave-2-2026-11-06/build.py --raw-check
python3 tasks/equipment-wave-2-2026-11-06/check.py
python3 scripts/validate.py
python3 scripts/build_pages.py
python3 tasks/equipment-wave-2-2026-11-06/check.py --pages

Checks already report raw54/54 over8/8 sources; hand-known3/3 and fabricated-name rejection; projection/preservation/census, byte-idempotent main-based apply, existing-ID/duplicate-name/unheld-host mutations reject before write; validate0; exact Pages builds5474HTML with54/54 canonical names/classes/access/sourceURLs on8host pages. No scripts/ changes; no pytest repeated. Please inspect/assert all claimed checks; injecting bad evidence should fail, not silently skip. No hosted deployment or physical booking tests were performed. Two independent families must approve; any refuting finding must name the settling source/rule and concrete repro. Return APPROVE or REFUTE with severity and uninspected scope. Do not amend files.

Corrected packet supersedes f66d0d3: Codex4two accepted findings, UC7fee_for_service with external-rates witness, PennState separateDSC144/FSC153 =>54rows41OH13PA,old34unchanged,7fee47notstated,dsc6. Production guards+old-defect mutations fail beforewrite. Freshall8raw54/54,known3,Pages54rows. Grok5original53approvalhistorical. Deepfocusedrereview accessreferent/grain and preservation, complete source/code available. No further scope expansion.
