# American Bath Group Salem address evidence repair

The #486 audit split on EVD-483012 because the quoted operator was American Standard Inc. The Atlas records American Standard as a licensed brand and American Bath Group as the plant operator. Under SCHEMA §4.13 the packet appends a physical address observation from American Bath Group's OSHA ITA Form 300A filing, preserving the earlier evidence and the current site street. Acceptance requires one new evidence row at the next tree-wide ID, full replay against the input hash and cited row, exact held legal-name binding, street equality with SITE-001455, and both binding-gate modes, validation and the row-loss guard passing.

**Lead for the owner’s operator-status queue.** OSHA opened an inspection on 2026-10-20 naming American Standard Inc. at the same street. The repair relies on the 2025 ITA filing by American Bath Group, filed on 2026-02-27. The 2025 observation date follows the existing packet’s filing-year-end convention. Current operator re-verification belongs to the owner’s operator-status queue.

Run `python3 tasks/pic18-street-fill-repair-2026-11-23/check.py` with the Atlas shared store mounted. It checks the input digest and raw row, proves the new evidence is the sole data delta, and injects the licensed-brand operator to verify rejection.
