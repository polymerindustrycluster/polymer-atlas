# Researcher titles in held institutional quotations

At base 65d0f53b, the original detector flags 293 of 1,614 people across the Atlas. Of these, 254 have wording absent from a held excerpt and 39 have a rank discrepancy. The detector folds case and punctuation to find candidates. Admission compares the chosen phrase case-sensitively against the institutional quotation.

The decisions file records one reading per flagged person and points to the deciding evidence row. The column pair in CLAIMS_CHECKED.csv distinguishes checked cells from corrections. For a hold the evidence ID identifies the triggering quotation, even where it cannot settle the rank. Quotes came from existing own-site evidence only. Institution and program records corroborate the domain separately from the person’s profile. The exact spelling of a named professorship, its capitalization and its title qualifiers are retained when identified as part of the title.

Run `python3 tasks/people-title-verbatim-2026-11-24/build.py` from the pre-repair tree to apply the packet. Run its sibling `check.py` to compare the entire people table to the base. The packet covers two fields per person. All verification dates come from the base.
