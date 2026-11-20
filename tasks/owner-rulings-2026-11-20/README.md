# Owner ruling, 2026-11-20 (bare group names in the show harvest)

The repo owner ruled one item in session on 2026-11-19/20, as multiple choice, choosing the recommended option. The
ruling text is separate from how it is applied.

## The seam

Since #404, the show-harvest passes hold a bare group name whose Atlas record is the group's US entity: rule (i). For
example, a list printing "Arkema" does not mint a row for Arkema Inc. The holds are keyed on the name key, which drops
legal suffixes, so a hold bound every listed form of the name at its event, in every role and year. A bare "BASF" on a
speaker list therefore also blocked "BASF Corporation" on the same event's registration list (#414 held it).

PCI Magazine's dated 2026 sponsor list prints a bare "Evonik" at the Coatings Trends & Technologies Summit
(EVT-000077). Two merged rows there already credit "Evonik Corporation": a #411 speaker row and a #414 attendee row.
Under the event-wide rule, banking that list would have required retracting both.

## Ruled

**A rule (i) hold binds the bare form only.** A listing that names the US entity itself pins it, even where a bare form
appears elsewhere at the event. Examples: "Evonik Corporation", "BASF Corporation", "Covestro LLC". The two
Evonik Corporation rows stay.

Not chosen:
- keep event-wide holds, and retract the two rows;
- let only a bare form on the same kind of list (same role) trigger the hold.

## How it is applied (method, not ruling)

- **"Names the US entity itself"** is read strictly. The listed name must equal the held organization's Atlas legal
  name, ignoring case and punctuation, and must include a legal-form word ("Inc", "Corporation", "LLC" and so on). An
  abbreviated suffix ("Corp." for "Corporation") or a geographic marker ("Hempel USA") under a hold stays held.
  - So "BASF Corporation" pins BASF Corporation.
  - "BASF SE" or "BASF" would not.
  - "Orion Engineered Carbons" at Great Lakes 2025 does not either: the Atlas legal name has no suffix, so the
    listing is the group's bare name.
- **Rule (ii) holds** (a generic name with nothing to pick the organization) are unchanged and still bind every form.
- **Applied in `tasks/show-harvest-muse-leads-2026-11-20/`:**
  - to that pass's lists;
  - to #414's list: the three names #414 held on the Coatings Trends 2026 registration list, "BASF Corporation",
    "Covestro LLC" and "Omya, Inc.". Each now mints an attendee row carrying the ruling's note.
- **No other merged list has such a listing.** The controller scanned every banked harvest list for listings caught
  by a rule (i) hold of #404, #411 or #414. It found five that print the organization's full name:
  - the three above;
  - "Orion Engineered Carbons" (no suffix; still held);
  - "Evonik Corporation" at SAMPE 2027, which already has a row.
- **SCHEMA:** no change. The holds are a harvest method recorded in the task READMEs, not a SCHEMA rule.
