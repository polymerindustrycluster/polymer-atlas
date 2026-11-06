"""Render only the campaign QUEUE section from the frozen public audit packet."""
import json
from pathlib import Path

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[1]
MARKER = '## Integrity + re-verification campaign ('


def load(name):
    return json.loads((TASK / name).read_text())


def validate_claims(claims):
    expected = {}
    for state in ['merged', 'open']:
        for pr in load(state + '-prs.json'):
            assert pr['number'] not in expected, 'PR occurs in both snapshots'
            expected[pr['number']] = (state, pr['headRefName'], pr.get('mergedAt', '2026-11-06')[:10])
    assert len(claims) == len(expected), 'missing or duplicated claim'
    assert len({p['number'] for p in claims}) == len(claims), 'duplicated claim'
    for pr in claims:
        assert (pr['state'], pr['branch'], pr['date']) == expected[pr['number']], 'claim disagrees with GitHub snapshot'
    assert 'PR #68' in next(p['title'] for p in claims if p['number'] == 129)


def render(prefix, claims, continuations, c):
    validate_claims(claims)
    branches = {p['branch'] for p in claims}
    assert not branches & {p['branch'] for p in continuations}, 'opened continuation still marked claimed'
    lines = [MARKER + '2026-11-06, controller: claude-code thread thr_9i2c6byhcz)',
             'Status snapshot and provenance: `tasks/campaign-hygiene-2026-11-06/README.md`. `done` means the bounded PR merged; it does not close its remaining research holds. Open PRs remain unchecked. Original ID reservations are retained below; gaps remain permanent. The registry restore merged; registry and derived-field writes still require their own authorization.', '']
    for state, heading in [('merged', 'Merged passes'), ('open', 'PRs awaiting merge')]:
        lines += ['### ' + heading, '']
        for p in sorted(claims, key=lambda p: p['number']):
            if p['state'] != state:
                continue
            token = f"done {p['date']} (#{p['number']})" if state == 'merged' else f"in-pr:codex 2026-11-06 #{p['number']}"
            ids = ' Original reserved IDs: ' + p['ids'] + '.' if p.get('ids') else ''
            lines.append(f"- [{'x' if state == 'merged' else ' '}] `{token}` **{p['title'].strip()}** Branch `{p['branch']}`.{ids}")
        lines.append('')
    lines += ['### Claimed continuations without a PR at the snapshot', '']
    for p in continuations:
        lines.append(f"- [ ] `claimed:codex 2026-11-06` **{p['description']}** Branch `{p['branch']}`.")
    lines += ['', '### Open follow-ups (public counts only)', '',
      '- [ ] `open` **Tombstone-site operator holds:** 4 held site rows in the corrected PR #201 packet (14 candidate site rows: 10 VERIFIED, 4 STILL_UNCERTAIN). Resolve exact legal-operator/alias and probable-duplicate questions from primary evidence; the other 2 tombstone bindings are sourced valid keeps, not holds.',
      '- [ ] `open` **Tier-1 owner/scope decisions:** final PR #205 remainder is 155 unhealthy organization rows with 197 overlapping gap memberships. Disjoint organization classes: 50 owner-only, 11 scope-only, 1 mixed owner+human; 93 human-only are separate below. Owner rulings remain required; no target/scenario is adopted here.',
      '- [ ] `open` **Tier-1 human outreach:** 93 human-only organization rows with 130 overlapping gaps (73 capability, 37 tier, 20 website). Counts only; no private organization list or outreach is published or sent.',
      f"- [ ] `open` **Archive top-up:** {c['archive_union']:,} distinct supported evidence rows still lack an admitted archive witness in the two disjoint archive packets (3,227 PIC-18 + 2,975 OH/PA continuation). The 34 admitted links in merged PR #137 are excluded. Verify readable captures and exact raw quotes; discovered URLs alone are not links.",
      f"- [ ] `open` **Residual-HQ holds:** {c['residual_hq_holds']} held organization rows across 249 unique candidates in PRs #189/#195/#199 (92/88/41 holds; 28 HQ_FOUND). Two L3 ownership exclusions remain held. Obtain explicit exact-entity HQ evidence; do not infer HQ from plant, correspondence or parent addresses. These are pending-packet outcomes, not additional main edits.",
      f"- [ ] `open` **Ohio streets remaining:** {c['active_oh_blank_streets']:,} of {c['active_oh_sites']:,} active Ohio site rows have blank street_address at the pinned main baseline; pending fills are excluded. Resolve own-operator physical-address conflicts. The final 88 rows of the original 448-row A/B frame are already claimed in PR #211, not unassigned.", '']
    return prefix + '\n'.join(lines)


def main():
    queue = ROOT / 'tasks/QUEUE.md'
    prefix = queue.read_text().split(MARKER, 1)[0]
    queue.write_text(render(prefix, load('claims.json'), load('continuations.json'), load('counts.json')))
    print('Rendered campaign section; earlier QUEUE sections preserved.')


if __name__ == '__main__':
    main()
