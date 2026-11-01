# How the owner cuts a release

A release is a dated snapshot of the Atlas: the SQLite database, the merged
CSV exports, every single-file table, and a Frictionless `datapackage.json`,
zipped with a checksum manifest. Everything is generated from the canonical
CSVs in `data/`; nothing under `build/` is ever committed (`build/` is
gitignored, and AGENTS.md section 1 bars committing generated exports).

Cutting a release is an **owner action**. Agents prepare the bundle; they do
not tag, publish or upload.

## 1. Cut a GitHub Release

Start from a clean checkout of the commit you want to publish (normally
`main`), so the bundle's version suffix is a real commit and not `-dirty`.

```bash
git checkout main && git pull
python3 scripts/validate.py                 # must pass; do not release on a failing tree
python3 scripts/build_sqlite.py             # rebuilds build/polymer-atlas.db + merged *_all.csv
python3 scripts/export_release.py           # builds build/release/ and the zip
```

`export_release.py` prints the zip path, its sha256, the resource count and
the row count per table. It re-runs `build_sqlite.py` itself when the build
outputs are missing or older than `data/`, and refuses to continue if the
merged exports or the database disagree with the CSVs
(`--rebuild` forces a rebuild, `--no-build` requires current outputs).

Check before uploading:

- The zip name is `polymer-atlas-release-<date>-<sha>.zip`. If it ends in
  `-dirty`, `data/` had uncommitted changes; rebuild from a clean tree.
- `build/release/COUNTS.md` row counts look right. Every count there names its
  unit (parent organizations vs. site rows vs. evidence rows, and so on);
  keep that unit when you quote a number in the release notes
  (AGENTS.md section 7).
- Integrity: inside the unzipped folder, `sha256sum -c MANIFEST.sha256`
  reports every file OK.

Then publish:

```bash
TAG=v$(date +%Y.%m.%d)                      # vYYYY.MM.DD
git tag -a "$TAG" -m "Polymer Atlas $TAG"
git push origin "$TAG"
gh release create "$TAG" build/polymer-atlas-release-*-*.zip \
    --title "Polymer Atlas $TAG" --notes-file <your notes>
```

If two releases land on one day, add a suffix (`v2026.11.01.1`) rather than
moving a tag. Release notes should state the git commit, the date, the counts
(with units, copied from `COUNTS.md`) and the license (below).

### Licensing in the bundle

`datapackage.json` declares the **data** as CC BY 4.0 (README, Licensing
section) and notes that the **scripts** are MIT. The repository has no
`LICENSE` file at the time of writing; adding one is an owner decision and
would go in by pull request. The licensed-source rule (AGENTS.md section 5)
applies to releases as much as to the repo: nothing from Plastics News, D&B
and similar sources may ride in a public bundle, and neither may any
information that exists only in the PIC CRM (AGENTS.md sections 5.1 and 6).

## 2. Optional mirrors (owner decisions)

Neither mirror is required, and each is a public, hard-to-retract publication
that the repo owner has to choose. Nothing here is automated.

### Zenodo (citable DOI)

1. Sign in to zenodo.org with the GitHub account that administers the repo,
   open the GitHub integration page, and switch the repository on.
2. Each subsequent GitHub Release is then archived automatically and gets a
   version DOI plus a concept DOI that always points at the latest version.
   Zenodo archives the repository snapshot at the tag; attach the bundle zip
   to the Zenodo record by hand if the DOI should cover the database file
   too.
3. Metadata (title, authors, license, description) comes from a
   `.zenodo.json` or `CITATION.cff` in the repo if present; adding either is
   a repo change and goes through the normal branch and pull request
   process. The author list and affiliation are the owner's call.
4. A Zenodo record cannot be fully deleted once published. Decide on the
   author list, license and description first.

### Hugging Face Datasets

1. Create a dataset repository under the owner's or organization's account.
2. Upload the contents of `build/release/` (the `data/` folder,
   `datapackage.json`, `COUNTS.md`, `MANIFEST.sha256`, and optionally
   `polymer-atlas.db`) with `huggingface-cli upload` or the web UI, and set
   the dataset card license to `cc-by-4.0`.
3. Treat the mirror as a copy: the GitHub repository stays canonical, and
   corrections are made in `data/` and re-released, never edited on the
   mirror.

Both mirrors make the data discoverable beyond the PIC audience. Confirm
that is intended, and that the privacy rules (AGENTS.md section 6: no
personal contact data, people records limited to public professional facts)
hold for everything in the bundle, before enabling either.
