# Record-health leads from the 2026-11-20 evidence lanes

**What this is:** 182 leads on 178 Atlas records (`leads.csv`). Each one is a place where a government filing or
registry record sits at the record's place under **another company's name**, or carries a closure signal.
- It is a triage packet: nothing under `data/` changes.
- A lead is a reason to re-verify the operator, name or status, never a change by itself. Under AGENTS.md §3, a status
  change needs dated evidence, and a false merge destroys data.

**First user:** the owner (triage), then whichever lane runs the next record-health pass.
**Non-use finding:** 2026-12-18 (PORTFOLIO §8).

| Lane | Lead class | Leads | What it means |
|-|-|-|-|
| OSHA | `files_under_other_name` | 123 | A 2025 OSHA Form 300A filing at the site's exact street names another company. This may be a successor, affiliate or tenant, or a multi-tenant building. |
| OSHA | `filer_differs_from_operator` | 9 | Name matched, but review rejected the filer as a different company or street. |
| FRS | `registry_names_other_company` | 22 | EPA's FRS record linked to the site names another company. 9 come from the matcher and 13 were rejected by review. |
| TRI | `tri_names_other_facility` | 27 | The organization's TRI link names another facility or parent. |
| TRI | `closure_signal` | 1 | The TRI facility carries the closed flag (THIEM, ORG-000286). |

**Examples worth a first look:**
- **SITE-002734 and SITE-002745:** LORD Corporation files at Parker-Hannifin's sites. For SITE-002734 both OSHA and
  FRS say so; for SITE-002745, FRS does.
- **SITE-000867:** Drew Foam files at Alleguard's Lancaster site.
- **SITE-000827:** Crane Performance Siding files at Royal Building Products' Columbus site.
- **SITE-003466:** Lear Corp files at IAC Wauseon.
- **OSHA address-only successors:** Lehigh Gasket → Staver Hydraulics, J-B Weld → EG4 Electronics, Resinall → Ergon.

**Two more, from the TRI lane README:**
- Euramax International (ORG-002443) now files TRI as OmniMax International.
- Panolam's (ORG-000038) TRIFID points to the Auburn, Maine Pionite plant.

## Columns

| Column | Meaning |
|-|-|
| `lead_id` | Identifier, `RH-0001` onward. |
| `lane`, `lead_class` | Where the lead came from and what kind it is. |
| `record_table`, `record_id`, `tier` | The Atlas record. |
| `atlas_name`, `atlas_place` | The record's name and place as the Atlas holds them. |
| `witness`, `witness_name`, `witness_place` | The filing or registry record and what it says. |
| `reviewer_note` | The review family's reason, where a reviewer rejected the match. |
| `suggested_check` | What to re-verify. |

**Privacy:** business names and addresses only. No personal data was read.

## Reproduce

`python3 tasks/record-health-leads-2026-11-20/build.py` (from the repo root).
- The script asserts each count against the lane's own ledger and review files before writing (AGENTS.md §2 rule 10c),
  and asserts that no lead repeats.
- **Not yet included:** the Form 5500 lane's leads (3 names spread over several EINs; 40 names filing in the HQ state
  but not the HQ city). They'll be added when that lane merges.
