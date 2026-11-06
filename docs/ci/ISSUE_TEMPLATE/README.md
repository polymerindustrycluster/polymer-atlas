# Proposed Atlas issue forms (IDEAS E-07)

These files are **PROPOSED and inactive**. The owner may copy `company-record.yml`,
`remove-person.yml` and `config.yml` into `.github/ISSUE_TEMPLATE/` on the default branch.
Leave this README here. No root file is changed by this proposal. Both forms assign
`LynyrdGrynyrd` (the owner); confirm the assignee still has repository access when activating.
No new labels or workflow automation are required. The chooser hides blank issues from
read/triage users; maintainers can still open them. GitHub issues and answers are public.

Company corrections collect exactly four required fields: record ID, field, proposed
value and public source URL. A claim is a review request, not authenticated ownership,
record-editing access or an automatically accepted fact. The owner triages it under the
project's existing commitment rules. The designated integrator checks the held record,
source identity and exact claim, re-fetches the source, and appends the matching §4.13
evidence observation before applying an accepted correction through a validated PR.
Sources must support the field and permitted tier; existing evidence is never rewritten.
Status changes still require dated primary/near-primary evidence and the closure gates.
Scope, ring, vocabulary and grain questions remain owner rulings. Rejected or unresolved
corrections retain their deciding or missing fact; no automatic CSV, tier or status edits.

Person removal is a separate privacy request, assigned directly to the owner. It asks
only for the PERSON ID and a relationship category; **no evidence or explanation is
required**, and the company-correction evidence gate does not apply to submitting it.
Do not request identity documents or sensitive details in public comments. Assignment
routes the request, not a promise of a private channel or automatic removal. The owner
handles any approved removal and required policy/history treatment; this proposal does
not authorize an agent to delete data or expose personal information. A record-ID-only
request can still reveal interest in that public record: this is a public intake, not a
confidential reporting service. Do not submit sensitive material through it.

Before activation, preview both forms in GitHub without submitting a real privacy
request, check required fields and owner assignment, and confirm the public warning is
visible. This PR checks YAML and field/routing constraints; the live chooser is untested.
First intended user: an Atlas company representative or person requesting removal;
review whether either form has been used by 2026-12-06 after activation (non-use is a finding).

References: [GitHub issue-form syntax](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms),
[chooser configuration](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository),
[Atlas evidence contract](../../SCHEMA.md)
and [contributor rules](../../../AGENTS.md).

Review receipt (2026-11-06): Codex/OpenAI APPROVE, zero blocking findings, original
proposal head `db3007e` (clerk 5). Independently checked all four files, official GitHub
syntax, owner assignability, YAML/negative controls, validator and change boundaries.
Live chooser/submission remains untested. Grok review is pending; this is not a completion
or activation approval. This receipt changes no YAML or proposed intake behavior.
