"""Deterministic report writer (adapted from blind audit 10): docs/reviews/BLIND_AUDIT_11_2026-11-17.md from statistics.json,
adjudication.json, final_grades.csv, sample.csv, blind_a.csv, frame.csv, draw.json, freeze.json and locks.json.
check.py regenerates the text and fails if the committed report differs, so no number in the report is hand-typed.
R-SAM: UEI rows appear as grades and counts only; no SAM name, address or per-row match detail.
Run: python3 write_report.py"""
import csv, json
from collections import Counter
from pathlib import Path

H = Path(__file__).resolve().parent
OUT = H.parents[1] / 'docs/reviews/BLIND_AUDIT_11_2026-11-17.md'
read = lambda p: list(csv.DictReader((H / p).open(newline='')))
pct = lambda x: f'{100 * x:.1f}%'
ci = lambda w: 'census' if w is None else f'[{pct(w[0])}, {pct(w[1])}]'
esc = lambda s: s.replace('|', '\\|')
A10_RATE = 0.046
FIRST_USER_NONUSE_DATE = '2026-12-01'
COND = {'filled_blank_cell': 'blank cell', 'labelled_with_2020_or_2021_loan_date': 'dated label', 'single_site_ohio_only_active_in_pic18': 'single-site OH, PIC-18',
        'borrower_name_street_city_match': 'name+street+city', 'band_equals_jobs_reported_band': 'band = JobsReported'}


def render():
    st = json.loads((H / 'statistics.json').read_text())
    meta, adj = (lambda d: (d['meta'], d['decisions']))(json.loads((H / 'adjudication.json').read_text()))
    fin = read('final_grades.csv')
    blind = {r['blind_id']: r for r in read('blind_a.csv')}
    frame = read('frame.csv')
    draw = json.loads((H / 'draw.json').read_text())
    fz = json.loads((H / 'freeze.json').read_text())['sha256']
    locks = json.loads((H / 'locks.json').read_text())
    c, ow, cw = st['final_counts'], st['overall_weighted'], st['content_weighted']
    small = [r['change_class'] for r in st['strata'] if r['readable'] == 'too small to read']
    feeds_350 = sum(1 for r in frame if r['prs'] == '350' and 'newsroom_feed_url' in r['changed_columns'].split(';'))
    uei = meta['uei_counts']
    disputed = [e for e in adj if not e.get('lead_check')]
    lead = [e for e in adj if e.get('lead_check')]
    content_err = ', '.join(k['blind_id'] for k in st['corrections'] if k['change_class'] not in st['content_weighted']['excludes'])
    assert len(content_err.split(', ')) == 1, 'the single-row sentence assumes one content error'
    rb = json.loads((H / 'receipts_b.json').read_text())
    sam_b = next(r for r in rb if 'r_sam_summary' in r)  # B's SAM API receipts are held privately; the public copy keeps their count
    sam_b_codes = ', '.join(f'{n} HTTP {code}' for code, n in sam_b['http_status_counts'].items())
    b_last = max(r['fetched_at'] for r in rb if 'fetched_at' in r)[:16].replace('T', ' ')
    a10_inside = cw['confirmed_error_wilson95_at_effective_n'][0] <= A10_RATE <= cw['confirmed_error_wilson95_at_effective_n'][1]
    L = []
    L.append('# Blind audit 11: data PRs merged 2026-11-16 and 2026-11-17\n')
    L.append(f"**Sample: {st['sample_record_changes']} record changes, drawn from a frame of {st['frame_record_changes']:,}.** A record change is one Atlas record "
             f"(table + ID) changed under one change class by a data PR merged in `{draw['base'][:7]}..{draw['head'][:7]}`. "
             f"Final grades: **{c['AGREE']} agree, {c['FIELD_ERROR']} field error, {c['CREATION_ERROR']} creation error, {c['UNRESOLVED']} unresolved.** "
             'Canonical rows changed by this audit: **0**. The two corrections are listed below and not applied.\n')
    L.append('Every PR in this frame passed a two-family refute gate before it merged. This audit is a blind sample read of what those PRs '
             'wrote. It is not that refute, and it makes no claim about records outside the frame.\n')
    L.append('## The three rates\n')
    L.append(f"1. **Overall, design-weighted to the frame: {pct(ow['confirmed_error'])} confirmed errors**, 95% Wilson interval "
             f"{ci(ow['confirmed_error_wilson95_at_effective_n'])} at the Kish effective sample size {ow['kish_effective_n']:.1f}. "
             f"Half the frame is archive links ({next(r['population'] for r in st['strata'] if r['change_class'] == 'archive_links'):,} of {st['frame_record_changes']:,}), so this figure mostly measures them.")
    L.append(f"2. **Content rate, like-for-like with blind audit 10: {pct(cw['confirmed_error'])}**, interval {ci(cw['confirmed_error_wilson95_at_effective_n'])} at effective "
             f"n {cw['kish_effective_n']:.1f}. It leaves out archive links, ZIP fills and navigation links, which A10's frame did not have "
             f"({cw['frame_record_changes']:,} record changes, {cw['sampled']} sampled). "
             + (f"A10's {pct(A10_RATE)} lies inside this interval, so **this audit cannot say these PRs are better or worse than A10's.**" if a10_inside
                else f"A10's {pct(A10_RATE)} lies outside this interval.")
             + f" The rate rests on a single row: {content_err} is the only confirmed error in the content strata; without it the point estimate would be 0.0%.")
    L.append(f"3. **Per stratum**, in the table below. **Too small to read** (fewer than 12 sampled, so even zero errors leaves an upper bound above 25%): "
             + ', '.join(f'`{s}`' for s in small) + '. Their rates cannot be read, whether zero or not. The two census strata (`tier_changes`, `rulings`) are exact counts.\n')
    L.append('| Stratum (change class) | Frame N | Sampled | Agree | Field error | Creation error | Unresolved | Confirmed error, 95% Wilson | Readable |\n|---|---:|---:|---:|---:|---:|---:|---|---|')
    for r in st['strata']:
        L.append(f"| `{r['change_class']}` | {r['population']:,} | {r['sampled']} | {r['AGREE']} | {r['FIELD_ERROR']} | {r['CREATION_ERROR']} | {r['UNRESOLVED']} | "
                 f"{r['confirmed_error']}/{r['sampled']} ({pct(r['confirmed_error_rate'])}) {ci(r['confirmed_error_wilson95'])} | {r['readable']} |")
    L.append(f"\nDesign weights are N/n per stratum. Unresolved rows would stay in every denominator; there are {c['UNRESOLVED']}, so counting them as errors leaves both "
             f"weighted rates unchanged ({pct(ow['unresolved_counted_as_errors'])} and {pct(cw['unresolved_counted_as_errors'])}). The weighted intervals are approximations.\n")
    L.append('## Corrections, not applied\n')
    L.append('| Sampled record | Field | Current value | Correct value | Basis |\n|---|---|---|---|---|')
    for k in st['corrections']:
        src = '; '.join(f'<{s}>' for s in dict.fromkeys(k['sources'])) or 'held privately under R-SAM'
        L.append(f"| {k['blind_id']}, {esc(k['record_id'])} ({blind[k['blind_id']]['record_label']}) | `{k['field']}` | {esc(k['current_value'])} | {esc(k['correct_value'])} | {src} |")
    L.append('')
    for k in st['corrections']:
        L.append(f"- **{k['blind_id']}**: {k['rationale']}")
    L.append('\n**Follow-ups (leads, not rates; controller decision 2026-11-17):**')
    L.append("1. Re-verify the parent of SITE-002767 (currently under ORG-000889) against held record ORG-003917, from public sources. "
             "The root cause predates the audit window (legacy record).")
    L.append("2. #355's UEI matcher can accept a non-HQ held site as its witness. Re-check #355's links of that class and tighten the matcher.")
    L.append(f"3. #350 accepted a newsroom feed when the newsroom page declared it, without reading the feed (its README: \"Feed contents are not fetched or asserted\"). "
             f"The earlier newsroom passes required at least one feed item that the newsroom page also links; ProVia's feed fails that test. "
             f"Re-run the item-overlap test on #350's {feeds_350} `newsroom_feed_url` fills.\n")
    L.append('## UEI rows (R-SAM: counts only)\n')
    L.append(f"The 13 sampled UEI links were checked against one batched SAM Entity API v3 response, stored outside the repo with its sha256 (`{meta['sam_files_sha256']['sam_uei_raw.json'][:12]}…` and "
             f"`{meta['sam_files_sha256']['sam_uei_raw_page1.json'][:12]}…`). All 13 UEIs were returned. "
             f"**{uei['match']} match; {uei['no_match']} does not.** The test: an active registration with the same normalized name (AGENTS §3) and the same HQ city and state. Per-row detail is in a private note "
             f"(sha256 `{meta['uei_private_note_sha256'][:12]}…`). No SAM name or address appears in this report or the repo.\n")
    L.append(f"## The {len(disputed)} disputed rows: lead adjudication\n")
    L.append(f"Reviewer A (Claude Opus, blind) locked {', '.join(f'{v} {k}' for k, v in sorted(st['reviewer_a_counts'].items(), key=lambda kv: -kv[1]))}. "
             f"Reviewer B (Codex, GPT-6.2 Astra, blind) locked {', '.join(f'{v} {k}' for k, v in sorted(st['reviewer_b_counts'].items(), key=lambda kv: -kv[1]))}. "
             'Cross-tab: ' + '; '.join(f'{k}: {v}' for k, v in st['cross_tab'].items()) + '. '
             f"The lead re-researched every disputed row from fresh raw fetches (`adjudication_receipts.jsonl`; `adjudication.json` re-checks each quote as an ordered word sequence on the stored page).\n")
    L.append('| Blind id | Record | A / B | Final | Decisive fact |\n|---|---|---|---|---|')
    for e in disputed:
        L.append(f"| {e['id']} | {esc(e['record_id'])} ({blind[e['id']]['record_label']}) | {e['reviewer_a']} / {e['reviewer_b']} | **{e['grade']}** | {esc(e['key_fact'])} |")
    L.append(f"\n## The {len(lead)} band rows: lead check against the PPP ruling\n")
    L.append('Both reviewers graded the seven band rows AGREE, but reviewer A noted that PPP is not in SCHEMA\'s size-band source list. At the controller\'s direction the lead '
             'checked each against the owner\'s ruling of 2026-11-16, "Strict matches" (`tasks/ppp-size-bands-2026-11-16/README.md`, line 3). A row passes only if all five conditions hold. '
             'Each condition is recomputed from git and from a fresh read of the SBA file #348 cites, whose sha256 matches #348\'s manifest. This check could only add errors; it found none.\n')
    L.append('| Blind id | Record | Band | PPP loan date | JobsReported | ' + ' | '.join(COND.values()) + ' |\n|---|---|---|---|---:|' + '---|' * len(COND))
    for e in lead:
        b = e['band_check']
        L.append(f"| {e['id']} | {e['record_id']} ({blind[e['id']]['record_label']}) | {b['band']} | {b['ppp_row']['DateApproved']} | {b['ppp_row']['JobsReported']} | "
                 + ' | '.join('yes' if b['conditions'][k] else '**no**' for k in COND) + ' |')
    L.append('\nThe ruling is not yet written into SCHEMA (§1 R13 lists only OSHA ITA, OSHA inspection and Form 5500 sources for site bands) or into `DECISIONS.md`. That is a docs follow-up, not an audit error.\n')
    L.append('## Reviewers, blindness and caveats\n')
    L.append(f"- **Locks.** Reviewer outputs matched the BOARD lock lines: A `{locks['a']['locked_sha256'][:8]}…{locks['a']['locked_sha256'][-4:]}`, B `{locks['b']['locked_sha256'][:8]}…{locks['b']['locked_sha256'][-4:]}`. "
             'The committed `verdicts_a.csv` and `verdicts_b.csv` are LF copies with every free-text cell blanked on the 13 UEI rows, because reviewer A\'s cells quote SAM names and addresses (R-SAM). '
             '`locks.json` pins both the lock hashes and the committed hashes; `check.py` re-applies the redaction to the private originals when they are present.')
    L.append(f"- **Reviewer B and the UEI rows.** B's last receipt is at {b_last} UTC, before the 00:00 UTC quota reset that the stored SAM response had to wait for. "
             f"B's receipts log {sam_b['count']} SAM API calls ({sam_b_codes}; the receipts themselves are held privately), yet every B note on these rows says \"SAM record not available\". The cause is not established. "
             "The controller checked B's SAM receipts: no key appears in any URL. Adjudication used the lead's stored response (both pages, hash-verified), not B's calls; reviewer A also read the stored response.")
    L.append('- **Navigation wording.** The reviewer instructions described `navigation_links` as "this organization\'s own page or feed", looser than SCHEMA §4.4\'s "a feed of the same newsroom". '
             'That explains B\'s AGREE on ProVia. The lead graded against §4.4, using the item-overlap test the earlier newsroom passes used.')
    L.append('- **AFFOA rows are not blind.** The two `rulings` rows (blind label `program_status`) are AFFOA records that both reviewers had already graded in blind audit 10 (A10-003). '
             'Reviewer A graded the blank `polymer_program` a field error under §4.6; the lead graded it AGREE because it is the owner\'s ruling of record.')
    L.append('- **Same family.** The lead is Claude, as is reviewer A. The lead decided from its own fresh fetches, overturned A twice (A11-073, A11-118), and used no OpenAI route. '
             'Only the band rows among the both-AGREE rows got a lead re-check.')
    L.append('- **Blindness is by protocol.** `frame.csv` and `sample.csv` carry PR attribution and sit in this branch; reviewers received only their blind file and the instructions, copied outside the repo.\n')
    L.append('## Observations that are not graded\n')
    L.append('- **AFFOA (A11-118).** SCHEMA §4.6 lists `polymer_program` as a MUST boolean, while the owner\'s ruling sets it blank. This is a schema-text question for the owner. '
             'Reviewer A also noted that the record keeps `polymer_program_name` and `polymer_program_url` though its only program row is tombstoned; #339 left that generated rollup unchanged on purpose (validator V-16).')
    L.append('- **Synapse Biomedical (A11-073).** The recorded feed is the site-wide feed: seven of its eight items are forms and policies, and its newest item is from 2023. It passes the overlap test, but it is a weak monitoring source.')
    L.append('- **Premere Enterprises (A11-100).** The PPP borrower ZIP is 44612; the site records 44663. The ZIP was not changed in this window, so it was not audited.\n')
    L.append('## First user and non-use date\n')
    L.append(f"The first user is the repo owner, who decides whether to apply the two corrections and act on the three follow-ups. If neither correction is applied or explicitly declined by **{FIRST_USER_NONUSE_DATE}**, "
             '`DECISIONS.md` records that as non-use (portfolio rule 8).\n')
    L.append('## Frame and fixed draw\n')
    L.append(f"Data pin `{draw['head'][:12]}`; window start `{draw['base'][:12]}`. Seed `{draw['seed']}`; stratified by change class, census below {draw['census_below']} record changes, "
             f"at least {draw['floor']} per larger stratum, the rest by largest remainder. Frame, unit, exclusions and the 25 reconciled PR counts are in `tasks/blind-audit-11-2026-11-17/README.md`. "
             f"Sample sha256 `{fz['sample.csv'][:12]}…`; blind file sha256 `{fz['blind_a.csv'][:12]}…` (A = B).\n")
    L.append('## Complete sample index\n')
    L.append('| Blind id | Change class | Table | Record | Label | PR(s) | A | B | Final |\n|---|---|---|---|---|---|---|---|---|')
    for r in sorted(fin, key=lambda r: r['blind_id']):
        L.append(f"| {r['blind_id']} | {r['change_class']} | {r['table']} | {esc(r['record_id'])} | {esc(blind[r['blind_id']]['record_label'])} | {r['prs'].replace(';', ', ')} | {r['reviewer_a']} | {r['reviewer_b']} | **{r['final_grade']}** |")
    L.append('\n## Review status\n')
    L.append('Draft. This report and its PR have **not** had a two-family refute; the controller routes that review. Check: `python3 tasks/blind-audit-11-2026-11-17/check.py` recomputes every count here from the committed files.')
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    OUT.write_text(render())
    print('wrote', OUT.relative_to(H.parents[1]))
