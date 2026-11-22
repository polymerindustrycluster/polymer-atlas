# Evidence binding: web-row admission by per-row proof (follow-up to PR #467)

Built by: Claude Code, Anthropic

**Status:** work in progress. This is a branch, not a PR yet.

On 2026-11-22 the owner split PR #467 (multiple choice). PR #467 keeps the gate for structured rows only. In that PR a web (free-text) row is FAIL or READ_REQUIRED, and READ_REQUIRED fails the PR because it has no admission path. This branch carries the admission path that was removed from #467, as it stood at c6b6f83b:

- `tasks/<folder>/BINDING_PROOF.csv` proof lines, each with a cross-family reading;
- `--verify-proofs`, which fetches archived captures;
- `capture_text()`;
- execution of a folder's `check.py`.

None of it is ready to merge. The list below is what must be true before it opens as a PR.

## To do

From the Codex round-2 review of #467 (`S/reviews/467-r2-review-codex.md`) and the streets lane:

1. **Bind the reading to the row (Codex finding 1).** A reading currently survives a row being re-pointed to another record. It must be keyed to `evidence_id`, `record_id` and a hash of the quote (and the claim), so that re-pointing or editing the row voids it.
2. **Confine the batch script (Codex finding 5).**
   - A script a batch supplies must not run in the trusted job at all unless it is confined: no filesystem beyond a copy, no network and no credentials.
   - Today the child keeps the runner user's filesystem access, and `GIT_DIR` points at real checkout metadata.
   - Otherwise, the gate checks presence only, and the lane and the reviewing family run the replay.
3. **Enforce verified bytes on the trusted path (Codex finding 6).**
   - The trusted (`pull_request_target`) workflow must run the archive verification and fail closed.
   - It must never publish a neutral skip, for example when the isolation probe cannot run.
   - In `--new-since` mode, an indexed archive proof is not admitted on its form alone.
4. **Decode gzip.** Wayback `id_` responses arrive gzip-encoded; the streets lane measured 5 of 6 archived pages affected. Decode by Content-Encoding (and by magic bytes) before hashing and text extraction, and define which bytes the digest covers.
5. **Use main text only.** Text extraction must exclude navigation, headers and footers, or proof offsets index boilerplate.
6. **Small fixes from the same review:**
   - duplicate `archive_links.csv` IDs must not collapse into one dictionary entry;
   - invalid UTF-8 in a proof file must be reported, not decoded with replacement.
