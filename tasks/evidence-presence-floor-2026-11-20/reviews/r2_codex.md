council-ask: codex effort=deep -> model=gpt-6-astra reasoning=max
VERDICT: UNSOUND

FINDING — **Blocking:** `scripts/validate.py`, V-65 baseline lookup and its ID-reuse comment; corresponding SCHEMA §4.13 and task README claims.

Replace a baselined, row-less organization with a different organization’s fields while retaining its `org_id` in the same PR. The key exists before and after, so a keyed row-loss check sees no removal and requires no `REMOVALS.csv` entry. V-65 inherits the baseline exemption and only warns.

Thus reuse does **not** require a declared removal, contrary to the stated mitigation. AGENTS.md prohibits it, but that remains a procedural constraint. The original enforcement gap remains; the described CI safeguard does not close it.
