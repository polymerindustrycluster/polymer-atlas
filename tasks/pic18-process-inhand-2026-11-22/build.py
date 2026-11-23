"""Canary packet builder (Part A, process in hand). Read-only on data/. Writes packet.csv, leads.csv, holds.csv, summary.json.
Adjudications are hand-made (DECISIONS below) from the material that material.py prints; this script resolves each FILL quote against
the stored 2026-11-16 corpus, and refuses to write a FILL it cannot find verbatim."""
import csv, hashlib, json, sys
import common as c

H = 'https://'
# FILL: (site_id, term, basis, page url, quote, locality quote, locality url)
FILLS = [
 ('SITE-001930', 'tooling_repair_maintenance', 'narrative', H + 'rotocastmold.com/',
  'The pros in these departments also provide expert mold rebuilding and repair.',
  'Rotocast Technologies, Inc. 1900 Englewood Ave Akron, OH 44312', H + 'rotocastmold.com/'),
 ('SITE-001930', 'mold_tool_making', 'narrative_testimonial', H + 'rotocastmold.com/',
  'The high quality cast aluminum molds they manufacture have consistently helped us achieve our production goals.',
  'Rotocast Technologies, Inc. 1900 Englewood Ave Akron, OH 44312', H + 'rotocastmold.com/'),
]
# LEAD / HOLD: site_id -> (verdict, reason, candidate term(s), route, evidence-or-source named, settling fact)
# routes: A = a URL on the record names the statement, no capture in hand: one permitted fetch settles it
#         B = the note names a source with no URL on the record (document id, directory, staging verdict): new research
#         C = a live process capability row exists; the permit sentence is not in hand (SCHEMA 3.6.2 question)
D = {
 'SITE-002032': ('HOLD', 'wrong_company_page', '', '', 'the record website pinnaclerecyclingllc.com serves Rumpke Waste & Recycling pages in the stored corpus', 'a page that names Pinnacle Recycling and a process at 2330 Romig Rd'),
 'SITE-001939': ('LEAD', 'note_names_source_without_url', 'extrusion_profile', 'B', 'site.notes: "PVC profile extrusion at the exact North Jackson address is settled by two primary-class sources: (1) the FGIA/AAMA Fenestration Exterior Profile Certification Program directory (1 Jan 2025, fetched) lists Vinyl Profiles, Inc."; own site vinylprofilesinc.com recorded as unreachable (availability only)', 'a retained capture of the certification directory listing, or an own-site page, stating the plant extrudes profile; a directory is a lead class, so tier ceiling applies'),
 'SITE-001559': ('HOLD', 'distributor_no_polymer_process', '', '', 'warehouse_distribution site; org description "Composites tooling and materials distributor"', 'a statement that the site itself shapes or formulates polymer'),
 'SITE-002113': ('LEAD', 'url_on_record_not_in_corpus', 'mold_tool_making', 'A', 'site.notes: "Own site creativemoldandmachine.com places Creative Mold & Machine at 10385 Kinsman Rd, Newbury, performing mold manufacturing and machining"; EVD-421881 cites http://www.creativemoldandmachine.com/profile.html (own_site)', 'fetch the on-record profile page and quote the mold-making sentence'),
 'SITE-001779': ('HOLD', 'no_31_term_fits', '', '', 'notes state paint filling and packaging (aerosol); EVD-425207 quote concerns touch-up paint supply', 'an owner ruling on whether aerosol filling has a 3.1 term; formulation is not stated'),
 'SITE-002102': ('LEAD', 'note_names_source_without_url', 'coating_formulation', 'B', 'site.notes: "Ohio EPA Director\'s Final Findings and Orders (2019, primary government document): All Coatings Corp. ... operating the Meridian Facility ... as a paint blending and manufacturing facility"; no website or URL on the record', 'the Findings and Orders document retained, with the sentence quoted'),
 'SITE-000076': ('LEAD', 'url_on_record_not_in_corpus', 'mold_tool_making', 'A', 'site.notes: own site "describes current design/manufacture of precision pultrusion dies (CNC/EDM/grinding)"; sources list https://crownmold.net/', 'fetch the on-record site and quote the die-making sentence'),
 'SITE-000147': ('HOLD', 'distributor_no_polymer_process', '', '', 'warehouse_distribution site; "Distributor of additives, resins and pigments"', 'a statement that the site itself formulates or processes polymer'),
 'SITE-002114': ('LEAD', 'url_on_record_not_in_corpus', 'composites_pultrusion', 'A', 'site.notes: Ohio EPA Title V permit P0139216 "including pultrusion operations, fabrication machines and resin batch mixers" (permit id, no URL); own site http://custompultrusions.com is on the record', 'fetch the on-record site for a pultrusion sentence, or retain the permit document'),
 'SITE-001784': ('HOLD', 'stored_page_is_an_error', '', '', 'stored home page is a Cloudflare error 1014 page; notes cite a Stow Planning Commission application with no process word', 'a readable own-site page; availability is not evidence of absence'),
 'SITE-000035': ('HOLD', 'no_statement_in_hand', '', '', 'multi-plant organization (12 active sites); notes carry no process sentence; sources list an Ohio EPA PDF (ES2014SaintGobain.pdf)', 'read the on-record Ohio EPA PDF for a process sentence about the Akron plant'),
 'SITE-000601': ('LEAD', 'capability_row_question', 'compounding_unspecified', 'C', 'CAP row term compounding, government_filing, Ohio EPA permit document (edocpub.epa.ohio.gov); stored own-site pages describe laminates and thermoplastic sheets, not compounding', 'owner question 1 below, or retain the permit and quote it'),
 'SITE-001854': ('HOLD', 'no_31_term_fits', '', '', 'own pages: 5-axis CNC mill to produce industrial knives; earlier canary 2026-11-18 held the org as owner_vocab_ruling', 'owner ruling on tooling_repair_maintenance for metal industrial knives (recommendation in tasks/pic18-org-process-canary-2026-11-18/holds.csv: no)'),
 'SITE-001933': ('HOLD', 'material_developer_not_plant_process', '', '', 'EVD-016277 quote states ECO-FLEX RTPV compounds are marketed; notes say processing guidance for injection molding, extrusion, blow molding is for customers', 'a sentence that the Creston plant compounds or processes'),
 'SITE-001505': ('HOLD', 'distributor_no_polymer_process', '', '', 'hq_only site; stored page is a one-line title; "specialty chemicals distributor"', 'a statement that the site itself processes polymer'),
 'SITE-002116': ('LEAD', 'note_names_source_without_url', 'injection_molding;thermoforming_unspecified', 'B', 'site.notes: "Encore Industries\' Encore Plastics division injection-molds and thermoforms pails, paint trays, and containers at 319 Howard Dr, Sandusky; manufacturer and GS1 records show current production into 2026"; no website or URL on the record', 'a retained own-site or manufacturer page; the division wording also needs a site-grain check'),
 'SITE-001731': ('HOLD', 'grain_question', '', '', 'own pages say "We deliver tailored recycling programs" at company level and name a headquarters at another street; the Atlas site is the warehouse at 16855 Park Circle Dr (EVD-422683)', 'a sentence placing a recycling operation at the warehouse street'),
 'SITE-001622': ('HOLD', 'no_process_named', '', '', 'note says the splints are made with injection-molded plastics: a product part, not a statement that the plant molds; stored pages name no process', 'an own-page sentence that FareTec itself molds'),
 'SITE-001795': ('HOLD', 'no_statement_in_hand', '', '', 'tier C; no corpus page; notes carry no process sentence', 'any own-site or filing sentence naming a process'),
 'SITE-001964': ('LEAD', 'url_on_record_not_in_corpus', 'recycling_unspecified', 'A', 'site.notes: Cuyahoga County Solid Waste District page "states collected materials are recycled by Northcoast Recycling Specialists in Wickliffe and the plastic is marketed to compounders who pelletize it"; URL on record https://cuyahogarecycles.org/recyclables/campaign_signs/', 'fetch the on-record county page; its class (agency page, not the company) bounds the tier, and "recycled by" does not say which plant step'),
 'SITE-001577': ('HOLD', 'no_process_named', '', '', 'stored pages name materials and polymerisation lamps as products; held in the 2026-11-18 canary as no_process_named', 'an own-page sentence that the plant mixes, molds or formulates'),
 'SITE-001951': ('HOLD', 'no_31_term_fits', '', '', 'equipment maker (blast cleaning equipment); no 3.1 process', 'none: outside the process vocabulary'),
 'SITE-001909': ('HOLD', 'no_statement_in_hand', '', '', 'hq_only; no corpus page; "printing" hits were a street-address line, not a process', 'any sentence naming a plant process'),
 'SITE-001605': ('LEAD', 'url_on_record_not_in_corpus', 'rotational_molding', 'A', 'site.notes: "Manufactures Bak-Pak spine boards, vacuum splints and immobilization/extrication devices by rotational molding"; org website https://epandr.com/ is on the record', 'fetch the on-record site and quote the rotational-molding sentence'),
}

def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()

def manifest():
    return [r for r in csv.DictReader(open(c.CORPUS / 'manifest.csv', newline='')) if r['text_file']]

def resolve(org_id, url, quote):
    for r in manifest():
        if r['org_id'] == org_id and r['url'] == url:
            if c.norm(quote) in c.norm((c.CORPUS / r['text_file']).read_text(errors='replace')):
                return r
    raise SystemExit(f'quote not found verbatim in stored page: {org_id} {url} {quote[:60]}')

def build():
    d = c.load(); smp = c.sample(d['frame']); by = {s['site_id']: s for s in smp}
    assert len(smp) == 25 and set(D) | {f[0] for f in FILLS} == set(by), 'every canary site needs exactly one adjudication'
    packet, leads, holds = [], [], []
    for sid, term, basis, url, q, gq, gurl in FILLS:
        s = by[sid]; r = resolve(s['org_id'], url, q); g = resolve(s['org_id'], gurl, gq)
        tier = s['verification_tier']
        packet.append(dict(site_id=sid, org_id=s['org_id'], site_name=s['site_name'], tier=tier, term=term, basis=basis, quote=q, source_url=url,
                           raw_file=r['raw_file'], text_file=r['text_file'], raw_sha256=r['sha256'], text_sha256=sha(c.CORPUS / r['text_file']),
                           grain_quote=gq, grain_url=gurl, grain_text_file=g['text_file'], site_street=s['street_address'],
                           proposed_tier_effect='supports_A' if basis.startswith('narrative') else 'supports_C',
                           review_flag='testimonial voice on the company\'s own page; if rejected, only a menu line (supports_C) remains and V-25 bars supports_C on a tier A site' if basis == 'narrative_testimonial' else ''))
    for sid, (v, reason, term, route, named, settle) in D.items():
        s = by[sid]
        row = dict(site_id=sid, org_id=s['org_id'], site_name=s['site_name'], tier=s['verification_tier'], site_type=s['site_type'], reason=reason)
        if v == 'LEAD': leads.append({**row, 'candidate_term': term, 'route': route, 'statement_and_source_named': named, 'settling_step': settle})
        else: holds.append({**row, 'what_was_found': named, 'settling_fact': settle})
    return d, smp, packet, leads, holds

def write(name, rows):
    with open(c.T / name, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

if __name__ == '__main__':
    d, smp, packet, leads, holds = build()
    write('packet.csv', packet); write('leads.csv', leads); write('holds.csv', holds)
    lr = {r: sum(1 for l in leads if l['route'] == r) for r in 'ABC'}
    hr = {}
    for h in holds: hr[h['reason']] = hr.get(h['reason'], 0) + 1
    sm = dict(frame_sites=len(d['frame']), frame_orgs=len(d['unk']), canary_sites=25, seed=c.SEED, fill_sites=len({p['site_id'] for p in packet}),
              fill_terms=len(packet), leads=len(leads), leads_by_route=lr, holds=len(holds), holds_by_reason=dict(sorted(hr.items())))
    (c.T / 'summary.json').write_text(json.dumps(sm, indent=1)); print(json.dumps(sm, indent=1))
