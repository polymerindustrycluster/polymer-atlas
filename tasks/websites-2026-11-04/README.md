# Websites for organizations that had none (2026-11-04)

The repo owner approved this pass in session on 2026-11-04, after a 100-organization pilot. The pool is 897 active
organizations with no `website` and a USPS HQ state.

## Method
- **Search (`search.py`):** one Serper (Google) query per organization, `"<legal name>" <city> <state>`. The candidate is
  the first result outside directories and social sites whose domain carries a distinctive name word or the name's
  initials. Its homepage is read through Jina Reader. The raw results are in `search_results.csv`.
- **Build (`build.py`):** a website is written only when all of the following hold.
  1. The record still has no website.
  2. No other held organization uses the same domain. A shared domain may mean a duplicate record, so those are held.
  3. The domain carries a distinctive name word that is not a place name.
  4. The re-fetched homepage is the site itself, not a bot wall or challenge page.
  5. The homepage states a polymer-related term. This guards against a same-name or same-acronym company.
  6. The homepage carries the organization's full normalized name (AGENTS.md §3) in a clean phrase of 3 to 25 words.
     That phrase is the evidence quote.
- **Why each rule exists:** every one comes from a false positive found by sampling the output. These were a
  computer refurbisher sharing an acronym, a state economic-development site matched on "Alabama", a card-printing firm
  sharing "Allegheny", and challenge pages that matched on the URL alone.

## Applied

| Change | Rows |
|-|-:|
| `website` filled (`edits.csv`, applied with `scripts/apply_p1_crm_scrub.py`) | 171 |
| `existence` evidence rows (`own_site`, `supports_A`), one per website, carrying the homepage quote | 171 |

No tier moves. The evidence ids sit above the tree-wide maximum.

## Not applied
- **`holds.csv`, 146 rows, each with its reason:**
  - only the distinctive word was on the page, not the full name: 38 (review candidates);
  - no clean phrase: 57;
  - bot wall: 20;
  - no polymer term: 20;
  - shared domain, a possible duplicate record: 8 (among them Pexco ORG-002534 / ORG-000484, Vaupell ORG-004948 /
    ORG-007004, and PLP ORG-004564 / ORG-000492). These are dedupe findings for a separate pass.
- **`no_own_domain.csv`, 501 organizations:** no own-domain result came back. Many are small firms with no site. Others
  look acquired, because their results point at a buyer: dlhBOWLES at ABC Technologies, Revlis at Akrochem, Firestone
  Polymers at Bridgestone, Cooper Tire at Goodyear. It is a findings list for a status and ownership pass.

Checks: rehearsed on a temp copy. `python scripts/validate.py` exits 0 on the committed tree.
