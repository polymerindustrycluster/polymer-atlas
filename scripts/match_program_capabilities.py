#!/usr/bin/env python3
"""Read-only exact-token topical fits. Never creates relationship or data rows."""
import argparse
import ast
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRAINING = {'degree', 'certificate', 'apprenticeship', 'training', 'course'}
RESEARCH = {'center', 'lab_facility'}
TIERS = {'A', 'B', 'C'}


def tokens(value):
    return {v.strip() for v in (value or '').split(';') if v.strip()}


def vocabulary(validator):
    """Read literal vocabulary declarations; do not import/run the validator."""
    names = {'PROCESSES', 'MATERIALS', 'CAP_PROCESS', 'CAP_MATERIAL'}
    values = {}
    for node in ast.parse(validator.read_text()).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in names:
                    values[target.id] = ast.literal_eval(node.value)
    if set(values) != names:
        raise ValueError('Expected literal vocabulary declarations missing; review schema drift')
    return {'process': values['PROCESSES'] & values['CAP_PROCESS'],
            'material': values['MATERIALS'] & values['CAP_MATERIAL']}


def read_rows(path):
    with path.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def index_unique(rows, key):
    result = {}
    for row in rows:
        ident = row.get(key, '')
        if not ident or ident in result:
            raise ValueError(f'Missing or duplicate {key}: {ident!r}; run validator first')
        result[ident] = row
    return result


def geography(site, program):
    # Names are compared as recorded; no geocoding, county inference or distances.
    a, b = site.get('state', ''), program.get('state', '')
    if not a or not b:
        return 'unknown'
    if a != b:
        return 'different_state'
    x, y = site.get('county', ''), program.get('county', '')
    return 'same_county' if x and y and x == y else 'same_state'


def match(sites, programs, owners, capabilities, vocab, site_state='OH', program_state='OH'):
    site_index = index_unique(sites, 'site_id')
    program_index = index_unique(programs, 'program_id')
    owner_index = index_unique(owners, 'org_id')
    index_unique(capabilities, 'capability_id')
    eligible_sites = {}
    excluded_sites = {}
    for sid, site in site_index.items():
        if site_state and site.get('state') != site_state:
            continue
        owner = owner_index.get(site.get('org_id'))
        reason = None
        if site.get('operating_status') != 'active': reason = 'site_not_active'
        elif site.get('verification_tier') not in TIERS: reason = 'site_unverified'
        elif not owner: reason = 'missing_operator'
        elif owner.get('status') != 'active': reason = 'operator_not_active'
        elif owner.get('verification_tier') not in TIERS: reason = 'operator_unverified'
        if reason: excluded_sites[sid] = reason
        else: eligible_sites[sid] = site
    eligible_programs, excluded_programs = {}, {}
    for pid, program in program_index.items():
        if program_state and program.get('state') != program_state:
            continue
        institution = owner_index.get(program.get('institution_org_id'))
        reason = None
        if program.get('status') != 'active': reason = 'program_not_active'
        elif program.get('verification_tier') not in TIERS: reason = 'program_unverified'
        elif not institution: reason = 'missing_institution'
        elif institution.get('status') != 'active': reason = 'institution_not_active'
        elif institution.get('verification_tier') not in TIERS: reason = 'institution_unverified'
        elif program.get('program_type') not in TRAINING | RESEARCH: reason = 'unsupported_program_type'
        elif program.get('program_type') in TRAINING and program.get('admissions_status') == 'not_admitting': reason = 'not_admitting'
        elif not program.get('url') or not program.get('sources'): reason = 'missing_program_source'
        if reason: excluded_programs[pid] = reason
        else: eligible_programs[pid] = program
    caps = {}
    ignored = {}
    for cap in capabilities:
        sid, axis, term = cap.get('site_id'), cap.get('capability_type'), cap.get('term')
        if sid not in eligible_sites: continue
        reason = None
        if cap.get('withdrawn_date'): reason = 'withdrawn'
        elif cap.get('org_id') != eligible_sites[sid].get('org_id'): reason = 'operator_mismatch'
        elif cap.get('provenance') not in {'company_disclosed', 'government_filing'}: reason = 'unsupported_provenance'
        elif not cap.get('source_ref') or not cap.get('observed_date'): reason = 'missing_capability_source_or_date'
        elif axis not in vocab or term not in vocab[axis]: reason = 'no_exact_shared_vocabulary'
        if reason: ignored[cap['capability_id']] = reason
        else: caps.setdefault(sid, {}).setdefault((axis, term), []).append(cap)
    matches = []
    for sid, site in sorted(eligible_sites.items()):
        for pid, program in sorted(eligible_programs.items()):
            keys = {('process', t) for t in tokens(program.get('specialty_processes'))}
            keys |= {('material', t) for t in tokens(program.get('specialty_materials'))}
            overlap = keys & caps.get(sid, {}).keys()
            if not overlap: continue
            if site.get('org_id') == program.get('institution_org_id'): continue
            training = program.get('program_type') in TRAINING
            admissions = program.get('admissions_status') or 'unknown'
            route = 'education_training' if training else 'research_or_facility'
            matched_caps = [c for key in sorted(overlap) for c in caps[sid][key]]
            matches.append({
                'site_id': sid, 'site_name': site.get('site_name'), 'site_type': site.get('site_type', ''), 'operator_id': site['org_id'],
                'operator_name': owner_index[site['org_id']].get('legal_name'),
                'program_id': pid, 'program_name': program.get('program_name'),
                'institution_id': program['institution_org_id'],
                'institution_name': owner_index[program['institution_org_id']].get('legal_name'),
                'program_type': program.get('program_type'), 'candidate_route': route,
                'readiness': 'admissions_unverified' if training and admissions != 'admitting' else 'contact_and_scope_check_required',
                'admissions_status': admissions if training else 'not_applicable_to_this_research_route',
                'geography': geography(site, program),
                'site_locality': {k: site.get(k, '') for k in ('city', 'state', 'county')},
                'program_locality': {k: program.get(k, '') for k in ('city', 'state', 'county')},
                'exact_terms': [{'axis': a, 'term': t} for a, t in sorted(overlap)],
                'capability_evidence': [{k: c.get(k, '') for k in ('capability_id', 'capability_type', 'term', 'provenance', 'source_ref', 'observed_date')} for c in sorted(matched_caps, key=lambda c: c['capability_id'])],
                'program_url': program['url'], 'public_door_url': program.get('public_door_url', ''),
                'program_sources': program['sources'], 'program_last_verified': program.get('last_verified', ''),
                'program_engagement_modes': sorted(tokens(program.get('engagement_modes'))),
                'tiers': {'site': site['verification_tier'], 'operator': owner_index[site['org_id']]['verification_tier'], 'program': program['verification_tier'], 'institution': owner_index[program['institution_org_id']]['verification_tier']},
                'meaning': 'Potential topical fit only; no verified need, service availability, partnership, customer or supplier relationship.'})
    matched_sites = {m['site_id'] for m in matches}
    matched_programs = {m['program_id'] for m in matches}
    return {'filters': {'site_state': site_state or 'all', 'program_state': program_state or 'all', 'status': 'active_only', 'record_tiers': sorted(TIERS)},
            'summary': {'eligible_site_rows': len(eligible_sites), 'eligible_program_rows': len(eligible_programs), 'site_program_candidate_pairs': len(matches), 'distinct_matched_site_rows': len(matched_sites), 'distinct_matched_program_rows': len(matched_programs)},
            'matches': matches, 'excluded_sites': excluded_sites, 'excluded_programs': excluded_programs,
            'eligible_sites_without_exact_match': sorted(set(eligible_sites) - matched_sites),
            'eligible_programs_without_exact_match': sorted(set(eligible_programs) - matched_programs),
            'ignored_capability_rows': ignored,
            'interpretation': 'Absence of a match means absent compatible structured data, not absent expertise or a negative finding. No hierarchy, fuzzy matching, family expansion, product-form mapping, inferred partnership or distance scoring.'}


def report(root, site_state='OH', program_state='OH'):
    paths = sorted((root / 'data').glob('organizations_*.csv')) + sorted((root / 'data').glob('sites_*.csv'))
    paths += [root / 'data' / f for f in ('ecosystem.csv', 'programs.csv', 'site_capabilities.csv')]
    if not list((root / 'data').glob('organizations_*.csv')) or not list((root / 'data').glob('sites_*.csv')):
        raise ValueError('Missing canonical shards')
    loaded = {str(p.relative_to(root)): read_rows(p) for p in paths}
    orgs = [r for p, rows in loaded.items() if p.startswith('data/organizations_') for r in rows]
    sites = [r for p, rows in loaded.items() if p.startswith('data/sites_') for r in rows]
    result = match(sites, loaded['data/programs.csv'], orgs + loaded['data/ecosystem.csv'], loaded['data/site_capabilities.csv'], vocabulary(root / 'scripts/validate.py'), site_state, program_state)
    # Includes definitions that determine behavior; independent of branch/commit metadata.
    inputs = paths + [root / 'scripts/validate.py', root / 'docs/SCHEMA.md']
    result['input_sha256'] = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(inputs)}
    result['input_manifest_sha256'] = hashlib.sha256(json.dumps(result['input_sha256'], sort_keys=True).encode()).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--site-state', default='OH', help='Exact recorded state; ALL for all states')
    parser.add_argument('--program-state', default='OH', help='Exact recorded state; ALL for all states')
    args = parser.parse_args()
    result = report(args.root, '' if args.site_state == 'ALL' else args.site_state, '' if args.program_state == 'ALL' else args.program_state)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
