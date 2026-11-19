# Owner rulings, 2026-11-18 (third set: show harvest)

The repo owner ruled three questions in session on 2026-11-18, as multiple choice, each as recommended. They arose
from the show harvest (`tasks/show-harvest-w23-2026-11-18/README.md`). Items 1 and 2 are applied by SCHEMA v1.16.1
and `tasks/show-harvest-rulings-2026-11-19/`; item 3 is recorded in `DECISIONS.md`.

## 1. An attendee list printed in the organizer's own brochure

SAMPE's sponsorship brochure for its 2027 show carries a full company list headed "SAMPE 2026 | April 27-30, 2026.
INDUSTRY LEADERS WERE HERE. Attendees represented the organizations advancing aerospace, defense, space, energy,
transportation, research, and advanced manufacturing worldwide", followed by 800 organization names and no people.
The 2026-11-09 ruling bars brochure or marketing lines and delegate lists that name people.

- **Question:** does a complete company list for a named edition count when the organizer prints it in its brochure?
- **Ruled: count it.** The organizer's complete company list for a named edition is an attendee list wherever the
  organizer prints it. A line naming only some companies ("attendees include companies like ...") stays a marketing
  line. Each row notes that the list is in the brochure.
- Not affected: SPE International Polyolefins 2026 publishes a delegate workbook with first name, last name, title
  and organization. That is a delegate list naming people, which never mints (2026-11-09).

## 2. A name in a logo's alt or title text

Some organizers type each company's name into a logo's alt text instead of the visible page (India Rubber Expo,
CareerTech VISION). Others give only a logo whose link or file name suggests the company (Eastern Coatings Show).

- **Question:** does a name the organizer wrote as alt text count as on the list?
- **Ruled: yes.** A name the organizer wrote as a logo's alt or title text is on the list. A name rebuilt from a
  link URL or an image file name is not.

## 3. Person names in an old commit on main

PR #252 (show harvest wave 1) landed as a merge commit, so its first commit (3b30b2f), which stored about ten
speakers' names in a drop list before a later commit replaced them with hashes, is in main's history. The names were
on public speaker pages, and no current file holds them.

- **Ruled: leave it.** Main's history is not rewritten. Recorded in `DECISIONS.md` (2026-11-19).
