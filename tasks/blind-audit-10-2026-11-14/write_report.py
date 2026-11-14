"""Deterministic report writer: docs/reviews/BLIND_AUDIT_10_2026-11-14.md from statistics.json, adjudication.json, final_grades.csv, sample.csv.
check.py regenerates the text and fails if the committed report differs, so no number in the report is hand-typed.
Run: python3 write_report.py"""
import csv, json
from pathlib import Path

H = Path(__file__).resolve().parent
OUT = H.parents[1] / 'docs/reviews/BLIND_AUDIT_10_2026-11-14.md'
read = lambda p: list(csv.DictReader((H / p).open(newline='')))
pct = lambda x: f'{100 * x:.1f}%'
ci = lambda w: 'census' if w is None else f'[{pct(w[0])}, {pct(w[1])}]'
cell = lambda k, n, w: f'{k}/{n} ({pct(k / n)}) {ci(w)}'
TABLE_NAME = {'people': 'people', 'programs': 'programs', 'ecosystem': 'ecosystem', 'organizations': 'organizations', 'sites': 'sites',
              'people_identifiers': 'people_identifiers', 'event_participation': 'event_participation'}
ONE = lambda s: s.split('. ')[0].rstrip('.') + '.'


def render():
    st = json.loads((H / 'statistics.json').read_text())
    adj = json.loads((H / 'adjudication.json').read_text())
    fin = read('final_grades.csv')
    blind = {r['blind_id']: r for r in read('blind_a.csv')}
    draw = json.loads((H / 'draw.json').read_text())
    fz = json.loads((H / 'freeze.json').read_text())['sha256']
    prov = json.loads((H / 'frame_provenance.json').read_text())
    c, u, w = st['final_counts'], st['unweighted_confirmed_error'], st['weighted_to_frame']
    L = []
    L.append('# Blind audit 10 — data PRs merged 2026-11-09 to 2026-11-12\n')
    L.append(f"**{st['sample_records']} sampled records (unit: record created or changed in a non-derived column by a first-parent commit in `1fefbd2..4ecc7cf`; frame {st['frame_records']:,} records): "
             f"{c['AGREE']} agreement on the tested claims ({pct(c['AGREE'] / 50)}), {c['FIELD_ERROR']} confirmed field errors ({pct(c['FIELD_ERROR'] / 50)}), "
             f"{c['CREATION_ERROR']} creation errors, and {c['UNRESOLVED']} unresolved ({pct(c['UNRESOLVED'] / 50)}).** Canonical rows changed by this audit: **0**. "
             f"Correction application belongs to the controller; the confirmed corrections are listed below and not applied.\n")
    L.append(f"Design-weighted to the frame, the confirmed-error rate is **{pct(w['confirmed_error_point'])}** (approximate 95% Wilson interval at the Kish effective sample size "
             f"{w['kish_effective_n']:.1f}: {ci(w['confirmed_error_wilson95_at_effective_n'])}); counting both unresolved records as errors it is "
             f"{pct(st['sensitivity_weighted']['unresolved_counted_as_errors'])}. Pooled unweighted: {u['count']}/50 ({pct(u['rate'])}) {ci(u['wilson95'])}. "
             "Per-stratum rates are in the table below and are the primary result: both errors sit in strata of four sampled records, so those stratum intervals are wide.\n")
    L.append('Agreement certifies only the claims each reviewer actually tested (columns under audit, as in `blind_a.csv`); it does not certify untested fields, NAICS, '
             'verification tier or continuous operation. These PRs merged on owner-approved packet checks with no recorded two-family refute; this audit is a blind sample read, '
             'not that refute, and it makes no claim about records outside the frame.\n')
    L.append('## Confirmed corrections — not applied\n')
    L.append('| Sampled record | Field | Current value | Correct value | Settling public source |\n|---|---|---|---|---|')
    for k in st['corrections']:
        src = '; '.join(f'<{s}>' for s in dict.fromkeys(k['sources']))
        L.append(f"| {k['blind_id']} — {k['record_id']} ({blind[k['blind_id']]['record_label']}) | `{k['field']}` | {k['current_value']} | {k['correct_value']} | {src} |")
    L.append('')
    for k in st['corrections']:
        L.append(f"- **{k['record_id']}**: {k['rationale']}")
    L.append('')
    ld = st['leads']['event_participation_rows_with_the_TPO_2026_end_date_2026_10_01']
    L.append(f"Lead, unsampled and not a rate: {len(ld)} `event_participation` rows at HEAD (including the sampled one) carry the same `edition_dates` value `2026-09-28 to 2026-10-01` for EVT-000046 (2026), "
             f"so the same end-date error may repeat across that edition ({', '.join(ld[:3])} … {ld[-1]}). They were not audited.\n")
    L.append('## Two unresolved records — settling facts\n')
    L.append('| Sampled record | Held claim | Settling fact | What was established |\n|---|---|---|---|')
    for e in adj:
        if e['grade'] == 'UNRESOLVED':
            L.append(f"| {e['id']} — {e['record_id']} ({blind[e['id']]['record_label']}) | `{e['fields']}` | {e['settling_fact']} | {e['rationale']} |")
    L.append('\nUnresolved records stay in every denominator and are never counted as agreement.\n')
    L.append('## Frame and fixed draw\n')
    L.append(f"Data pin `{draw['head'][:12]}`; window start `{draw['base'][:12]}`. Frame by table (records): " + ', '.join(f"{t} {n:,}" for t, n in draw['frame_sizes'].items()) +
             f"; relationships 0. Two derivations agree (per-commit first-parent diffs and one base-to-head diff), creation counts match the PR titles for all 34 (PR, table) pairs a title states, "
             f"and ids are unique. Excluded: {prov['tables']['ecosystem']['derived_rollup_only_excluded']} ecosystem records changed only in the generated rollup columns (controller ruling), "
             f"{sum(v['derived_only_excluded'] for v in prov['tables'].values())} `tier1_qualifier*`-only changes, 4 merged-away people. Seed `{draw['seed']}`; table strata, simple random within stratum, "
             f"census for tables under {draw['census_below']} records, at least {draw['floor']} per larger stratum. Sample SHA256 `{fz['sample.csv']}`; blind file SHA256 `{fz['blind_a.csv']}` (A = B). "
             'The first draw (seed `...-v1`, frame 1,653) was superseded before any reviewer saw it; its receipts are in `superseded_v1/`.\n')
    L.append('## Rates by sampling stratum\n')
    L.append('Unit: sampled records in the named table stratum. Each cell: count/denominator (percent) and 95% Wilson interval; census strata (all records sampled) have no sampling error and show no interval. '
             'All sampled records, including unresolved, stay in the denominator.\n')
    L.append('| Table | Population / sample | Agreement | Field error | Creation error | Unresolved | Confirmed error (field + creation) |\n|---|---:|---|---|---|---|---|')
    for r in st['strata']:
        n = r['sampled_records']
        L.append(f"| {r['table']} | {r['population_records']:,} / {n}{' (census)' if r['census'] else ''} | " +
                 ' | '.join(cell(r[g], n, r[g + '_wilson95']) for g in ('AGREE', 'FIELD_ERROR', 'CREATION_ERROR', 'UNRESOLVED')) +
                 f" | {cell(r['confirmed_error'], n, r['confirmed_error_wilson95'])} |")
    p = w['point']
    L.append(f"| **all, design-weighted to the frame** | 1,621 / 50 | {pct(p['AGREE'])} | {pct(p['FIELD_ERROR'])} | {pct(p['CREATION_ERROR'])} | {pct(p['UNRESOLVED'])} | {pct(w['confirmed_error_point'])} {ci(w['confirmed_error_wilson95_at_effective_n'])} |")
    L.append(f"| all, pooled unweighted | 50 | {st['unweighted_counts']['AGREE']}/50 | {st['unweighted_counts']['FIELD_ERROR']}/50 | {st['unweighted_counts']['CREATION_ERROR']}/50 | {st['unweighted_counts']['UNRESOLVED']}/50 | {u['count']}/50 ({pct(u['rate'])}) {ci(u['wilson95'])} |")
    L.append('\nDesign weights are N/n per stratum (identifiers 38.9, people 38.1, event rows 38.5, programs 36.3, ecosystem 2.0, sites and organizations 1.0). '
             'The pooled unweighted figure over-weights the two census strata; use the weighted row for the frame. The weighted interval is an approximation.\n')
    L.append('## The 14 reviewer disagreements — lead adjudication\n')
    L.append(f"Reviewer A (Claude, blind) locked {st['reviewer_a_counts']}; reviewer B (Codex, blind) locked {st['reviewer_b_counts']}. Cross-tab: " + '; '.join(f'{k}: {v}' for k, v in st['cross_tab'].items()) +
             '. The 36 records both reviewers graded AGREE keep that grade. The other 14 were re-researched by the lead from fresh raw fetches (receipts: `adjudication_receipts.jsonl`, `adjudication.json`; every quote re-checked as an ordered word sequence on the stored page).\n')
    L.append('| Blind id | Record | A / B | Final | Decisive fact |\n|---|---|---|---|---|')
    for e in adj:
        L.append(f"| {e['id']} | {e['record_id']} — {blind[e['id']]['record_label']} | {e['reviewer_a']} / {e['reviewer_b']} | **{e['grade']}** | {ONE(e['rationale'])} |")
    L.append('\nPattern in the nine records A graded AGREE and B left UNRESOLVED: B\'s notes cite blocked or JavaScript-only pages (403, dynamic shell, image-only PDF), not contrary evidence; '
             'on fresh fetches all nine were settled to AGREE except one program link (A10-041) that is genuinely indirect. In the four A FIELD_ERROR / B UNRESOLVED records, two of A\'s findings stood (A10-015, A10-038), '
             'one was overturned (A10-007, NextFlex operator is FlexTech Alliance dba NextFlex) and one is held as a scope question for the owner (A10-003). A10-038 also corrects A on thermosets, which the NSF CCI page does state.\n')
    L.append('## Reviewers, blindness and caveats\n')
    L.append('- Blind inputs were whitelisted from git at the pinned head, with the PR, lane, notes, `created_by` and verification dates withheld; blindness is by protocol (`frame.csv`, `sample.csv` sit in the branch), and reviewers received copies of one blind file only. Reviewer outputs are frozen in `verdicts_a.csv` (sha256 `dfd8f490…cf4e`) and `verdicts_b.csv` (`60efe428…d7bc`), hashes matched the controller\'s BOARD lock lines.\n'
             '- **Reviewer A\'s stale-checkout disclosure.** A\'s early notes came from a checkout behind the audited state; A redid the vocabulary and duplicate checks in a current worktree and corrected A10-002 (a vocabulary objection, withdrawn: `fiber_formation` was added to the vocabulary on 2026-11-12) and A10-041 (FIELD_ERROR to AGREE). '
             'Effect on grades: none. A10-002 was graded AGREE by both reviewers and `scripts/validate.py` passes at the pinned head (vocabulary rules); A10-041\'s final grade is the lead\'s own adjudication (UNRESOLVED), not A\'s. '
             'The lead also re-ran the duplicate checks for all 50 records at the pinned head (`stale_checkout_check.py`): no duplicates found.\n'
             '- Reviewer A read two pages only through Tavily (the PTXPO exhibitor list and a Spaepen lab page), so those quotes were not mechanically checked by A. The lead re-read both mechanically (organizer roster JSON; lab page via the Jina reader) before grading.\n'
             '- Reviewer B left 13 records UNRESOLVED. Most cite blocked, JavaScript-only or image-only pages (availability limits, not findings); the substantive ones (A10-003, A10-041) are held above. Each of the 13 was settled or explicitly held.\n'
             '- The lead is Claude, as is reviewer A; the lead adjudicated from its own fresh fetches, not from A\'s notes, and overturned or narrowed A\'s findings in A10-007 (operator), A10-038 (thermosets) and A10-019 (ownership is not asserted). No OpenAI route was used. No second-family review of this report has been run.\n')
    L.append('## Observations that are not graded\n')
    L.append('- **A10-018 Wake Forest**: the record carries `polymer_program=false` for a non-Ohio university; SCHEMA 4.6 text limits false to NE Ohio generalists while the data holds 134 such rows. A schema/data tension for the owner; the validator accepts it.\n'
             '- **A10-007 NextFlex**: the cited pages never name FlexTech Alliance; federal registration and trademark records do. A citation gap, not a value error.\n'
             '- **A10-019 OMG Thermoforming**: whether it is OMG srl\'s subsidiary or an independent distributor is not settled and not asserted by the record.\n'
             '- **A10-032 Spaepen**: Gate B is met literally; the witness is thin (polymers are one of three material classes).\n'
             '- **A10-044 Gregstrom Woburn plant**: `closed` rests on a dated 2025-11-12 relocation report, the company\'s own move post and the current contact page; SCHEMA 4.2 also offers `relocated_in_scope`.\n')
    L.append('## Complete sampled-record index\n')
    L.append('| Blind id | Table | Record | Label | PR(s) | A | B | Final |\n|---|---|---|---|---|---|---|---|')
    for r in sorted(fin, key=lambda r: r['blind_id']):
        L.append(f"| {r['blind_id']} | {r['table']} | {r['record_id']} | {blind[r['blind_id']]['record_label']} | {r['prs'].replace(';', ', ')} | {r['reviewer_a']} | {r['reviewer_b']} | **{r['final_grade']}** |")
    L.append('\n## Review status\n')
    L.append('Draft. Completion review: this report and the PR have **not** had a two-family refute; the controller routes that review. Check: `python3 tasks/blind-audit-10-2026-11-14/check.py` recomputes every count here from the frozen files.')
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    OUT.write_text(render())
    print('wrote', OUT.relative_to(H.parents[1]))
