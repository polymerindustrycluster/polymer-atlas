# Correction PR 4 · ATLAS-8 and ATLAS-9 follow-up reads

Built by: Codex GPT-6.2 Sol (atlas-p1-integrator-1), 2026-11-23.

| Scope | Verified | Corrected | Withdrawn | Held |
|---|---:|---:|---:|---:|
| ATLAS-8 distinct packet claims | 63 | 2 | 1 | 20 |
| ATLAS-9 distinct sampled evidence claims | 134 | 1 | 1 | 55 |
| Other checked canonical cells | 0 | 3 | 1 | 0 |
| Claim ledger and original holds | 197 | 6 | 3 | 75 |

The 86 ATLAS-8 claims include the 37 people keys settled by Gemini
(34 verified, one corrected, two held). The ATLAS-9 total comprises 191
distinct sampled evidence IDs across rest-of-Ohio, the PIC-18 screen-5
sample and rest-of-country. The 23 cross-reads amend those decisions
without increasing the population. The three additional rubber-transfer
checks and the Exel canonical street withdrawal account for the last
four claims. The 206 checked claims have one row each in
`CLAIMS_CHECKED.csv`. The queue also has one Exel replacement lead,
bringing its total to 76 entries.

## What publishes

Seven canonical cells change. S4 Medical restores its street to the
contact address confirmed at the held city and ZIP. Exel's known-wrong
Erlanger street is withdrawn. The current contact page supplies a
replacement, but the existing public memento lacks it. The program
research specialty withdrawn by the reader is blanked.

The faculty correction uses the exact professional name on the cited
faculty capture. `FACULTY_WITNESS.csv` locates the verbatim name by
capture checksum, character offset and length for independent replay.
The corrected name is carried in the canonical `full_name` field.
Prior evidence stays append-only.

SCHEMA v1.16's `rubber_molding_transfer` replaces `transfer_molding`
in the held RPM, Woodlawn and Ohio Elastomers cells. All three current
bodies carry the existing cited wording. Woodlawn's service phrase
replays in the HTML outside the gate's main-text region, and the main
text names transfer molding within its custom rubber services.
There are no new citations for these vocabulary corrections.

Two new own-site address observations and their public archive links
carry exact-byte proofs with Sonnet's independent read. The S4 witness
supports tier A. The Jackson Kayak re-cite supports tier C and matches
the existing site address. Jackson calls the address its head office.
Its plant function has separate evidence.

## Holds and owner settlement

- Kent ORG-000503 / PROG-000014 remains held. The gate suppresses the
  page body under a header-class wrapper. The controller is carrying
  the gate question to the owner.
- Lincoln EVD-420042 remains queued for a gate-readable SEC EDGAR
  re-cite. The controller directed settlement of the original
  non-tying citation and its cell in G8.
- Custom Rubber EVD-014675 is held for the exact existing service
  witness. The service route did not replay the rubber-transfer quote.
  The controller directed it to G8 if in PIC-18.
- Exel's source artifact is the live contact-us page. Re-admission
  requires a readable public archive with the current street.
- The audit 12 draw remains held under the owner's “Settle PIC-18
  first” ruling. G8 settlement follows this PR.

## Check

```sh
lockf -k /tmp/polymer-atlas-heavy.lock python3 -I tasks/p1-correction4-2026-11-23/check.py --at HEAD
```

The replay reads the sealed packet excerpts, applies all dispositions,
replays six capture checksums and compares every data file touched
against the approved correction. It verifies each claim and queue
entry and both archive proofs. The published evidence is append-only.
The check does not reread or adjudicate the remaining held sources.
