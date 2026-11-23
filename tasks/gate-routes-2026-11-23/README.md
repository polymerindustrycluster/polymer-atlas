# ATLAS-38 G8 evidence binding gate

Built by: Codex GPT-6.2 Sol

The gate check admits new citations only after the following witnesses
bind. Current Atlas rows keep their original citations.

| Case | Gate replay or outstanding fact |
| --- | --- |
| EVD-421581 | Rubber World dated dateline and named launch bind ACE Innovations existence. |
| EVD-421582 | The dateline cannot establish ACE Innovations HQ. An explicit HQ source is needed. |
| EVD-405007 | Houlihan Capital explicitly names Stretchtape's Cleveland HQ. The capture binds the held existence claim. |
| EVD-421737, EVD-425054 | KASE and Innoplast are organization records with no comparable held street or ZIP. KASE's FRS source exercises the allowed postal pair against a test site. |
| EVD-421870 | Raw CY2021 ITA establishes the 43-character width, with the full name in CY2017 for the same establishment. The held Bellevue site supplies the street, ZIP and place match. |
| EVD-422240, EVD-422241 | The Giesecke registry name lacks the held word “America”. The site also has no held ZIP. Seek an exact operator witness before re-citing. |
| EVD-422344 | CY2017 OSHA ITA and FRS match at the same ShurTech physical address. FRS supplies Lorain County. The held Avon record supports a place-only claim. |
| EVD-425347 | Bridgestone record lacks a held ZIP. The ECHO operator label also differs from the held tire-production site name. |
| EVD-422451, EVD-422452 | “GMR Materials Technology” in the registry differs from the held “GMR Material Technology”. |
| EVD-424304 | HEXPOL's operator matches. The site lacks a held ZIP. |
| EVD-420042 | SEC submissions business address binds the held Lincoln Electric HQ site, using the Cleveland/Euclid postal pair and base CIK. |
| ORG-000503 / PROG-000014 | Kent's captured page body survives extraction. Nested page chrome remains excluded. |

## Checks

Run the raw and capture replay with isolated Python. The captures are
the reader packets' existing files and remain outside the repository.

```sh
python3 -I tasks/gate-routes-2026-11-23/check.py "$S" "$C/persist" /tmp/a8w/cache/ddebf0603c422722.raw
lockf -k /tmp/polymer-atlas-heavy.lock env PYTHONPATH=scripts python3 -m unittest test_check_evidence_binding
lockf -k /tmp/polymer-atlas-heavy.lock python3 scripts/validate.py
lockf -k /tmp/polymer-atlas-heavy.lock python3 scripts/run_tests.py
```

The census reads every canonical evidence row on the main base. Run
the following separately from that base's worktree and this branch's
worktree, supplying distinct output paths.

```sh
lockf -k /tmp/polymer-atlas-heavy.lock python3 -I scripts/check_evidence_binding.py \
  --all --head cd994c68042b6c1c1c65cc5af88ec416dd4ba7dd --out "$OUT"
cmp "$BEFORE" "$AFTER"
```

The complete verdict CSVs are byte-identical at both bases. There
are zero changes to list in [CENSUS_DIFF.csv](CENSUS_DIFF.csv).

| Main base | Evidence rows | PASS | FAIL | HELD | READ_REQUIRED | UNINSPECTABLE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1600f540 (initial) | 47,688 | 50 | 227 | 0 | 2,826 | 44,585 |
| cd994c68 (after G8a) | 47,696 | 56 | 227 | 0 | 2,828 | 44,585 |

The census uses `--all` (pre-proof mechanics). Positive
web admissions are exercised separately from stored captures. The SEC
full-filing text path has a synthetic replay test. It accepts the
standard full-submission filer header and a sole business address.

The PR check runs trusted code from main. A data PR can cite these
routes after the gate PR merges.
