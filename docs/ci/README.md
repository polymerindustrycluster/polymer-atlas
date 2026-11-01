# Turning on CI (owner action, ~2 minutes)

The repo has no automated validation on pull requests. AGENTS.md §2 rule 2 says
the reason is that the GitHub App the agent harnesses use cannot write to
`.github/workflows/`. **A human with admin rights can.** Once the workflow is on
the remote, every PR from every harness gets `validate.py`, the vocabulary check,
the tests and the SQLite build run automatically. AGENTS.md says campaign mode
gets revisited "if Workflows permission is ever granted and the workflow lands on
the remote".

Steps:

1. On github.com open the repo → **Add file → Create new file**.
2. Name it `.github/workflows/validate.yml` and paste in the contents of
   [`docs/ci/validate.yml`](validate.yml).
3. Commit straight to `main`. This is your own push, not an agent's.
4. Optional: Settings → Branches → add a protection rule for `main` that
   requires the `validate` check. Agents' PRs then cannot merge red.

Then run a dated AGENTS.md revision for §2 rule 2 (campaign mode). That revision
is an owner ruling, so no agent self-rules it.

Runtime: about 30 s on GitHub's free runners. Everything is stdlib Python, with
nothing to install.
