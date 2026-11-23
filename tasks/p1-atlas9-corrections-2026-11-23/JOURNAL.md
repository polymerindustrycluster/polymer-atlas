# ATLAS-9 integration journal

The base is `24f71798`, with data and B6 task files byte-identical to the
reviewed B6 head. The two source packet manifests passed 20 of 20 checks.
The first source replay verified 193 quotes. The cross-family source replay
verified its 37 assigned excerpts, comprising 33 VERIFIED and four
STILL_UNCERTAIN decisions.

The pre-pass backup preserves all six canonical files edited here.
`scripts/atlas.py next-id EVD` returned EVD-483046. The pass appends
EVD-483046 in North Carolina and EVD-483047 in Michigan, along with their
archive links. It moves the two existing organization rows to their
destination shards.

The controller's 12:49 ET ruling and the follow-up after B6 approved the
headquarters changes, the separate evidence-ID and canonical-cell counts,
and leaving the replacement counties unknown. The King memento is reused
from the old archive index, with its true February 7 date and `unknown`
for the original creator of the new link. The old archive row is preserved.
The Total Plastics contact page was captured through authenticated Save Page
Now under owner round 21. `ARCHIVES.csv` holds the receipt.

Claude Sonnet 5.5 independently verified both byte hashes, quote offsets,
organization bindings and city/state claims on 2026-11-23. King’s source
places the headquarters move in a company history entry. [Task source replay](check.py)
Sonnet's detailed report is `reviews/atlas9-pr3-hq-read-sonnet.md` in the
controller's review directory. The two exact HTML bodies are in private
provenance under the paths in `INPUTS.sha256`.

The audit 12 frame replay moved the two organization records out of PIC-18
(1,931 to 1,929 records) and into the rest-of-country stratum (8,406 to 8,408
records). The frame still has zero unassignable records and one named
exclusion. The canonical site files are byte-identical to the base.

The named batch check passed for 234 packet rows, 201 claims, eight HQ
cells, two proofs and 41 queued evidence IDs. The validator and row-loss
guard passed under the heavy lock. A repeat local replay with main's binding
gate fetched both public mementos and passed both proofs.
