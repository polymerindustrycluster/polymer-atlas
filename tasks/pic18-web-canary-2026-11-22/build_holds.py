#!/usr/bin/env python3
"""holds.csv: every (organization, field) with no VERIFIED fill, with the reason and the fact that would settle it. check.py asserts the cover is exact."""
import csv
D = 'tasks/pic18-web-canary-2026-11-22/'
rd = lambda f: list(csv.DictReader(open(D + f, newline='', encoding='utf-8')))
frame, cands, fet = rd('frame.csv'), rd('candidates.csv'), rd('fetches.csv')
readable = {}
for r in fet:
    if r['kind'] != 'robots' and r['status'] == 'ok': readable[r['org_id']] = readable.get(r['org_id'], 0) + 1
filled = {(r['org_id'], r['field']) for r in cands if r['verdict'] == 'VERIFIED'}
NP = 'An own-page narrative sentence stating that the company itself performs a named section 3.1 process'
NM = 'An own-page narrative sentence naming a section 3.3 industry as a customer of this company'
H = {  # org: (process reason, process settling fact or None for default, market reason, market settling fact or None)
 'ORG-000025': ('distributor_service_menu', None, 'no_market_claim', 'A sentence naming a customer industry (the pages list products and brands only)'),
 'ORG-000256': ('no_readable_page', 'A readable copy of the home page (robots.txt request reset by the server, curl exit 92, after the one retry; an availability fact)', 'no_readable_page', 'Same'),
 'ORG-000483': ('no_polymer_process_named', None, None, None),
 'ORG-002068': ('not_a_processor', 'Chemstress is an engineering and construction firm; no §3.1 process applies unless an owner ruling says otherwise', None, None),
 'ORG-001391': ('no_process_named', 'A sentence naming molding (or another §3.1 process) for the rubber toys; the page says products are made at the Colorado headquarters', 'no_vocab_market', 'A §3.3 term for pet products, or an owner ruling adding one'),
 'ORG-000098': ('parent_group_page', 'A page of Spazzolplastica North America LLC itself (the record website is the Italian parent site)', 'parent_group_page', 'Same: a North America entity page; candidate agriculture quote held'),
 'ORG-001183': ('parent_group_page', 'A Ventra page, or an owner ruling that the Flex-N-Gate group site speaks for the record; the home page names no process (only "plastics, metals, lighting and mechanical assemblies experience")', 'parent_group_page', 'Same; candidate automotive_unspecified quote held'),
 'ORG-001808': ('no_readable_page', 'A readable copy of the home page (HTTP 403 to this client; an availability fact)', 'no_readable_page', 'Same'),
 'ORG-001541': ('no_process_named', 'A sentence stating that AlphaMicron itself makes or coats liquid-crystal films or cells with a §3.1 process (none of the six pages read names one)', None, None),
 'ORG-001963': (None, None, 'no_market_claim', 'A sentence naming an industry the molds go to (the page says "clients and customers from many different sectors")'),
 'ORG-001742': ('waste_management_not_process', None, 'no_vocab_market', 'A §3.3 term for waste-management customers, or a sentence naming an industry served'),
 'ORG-000135': ('no_vocab_process', 'A sentence naming a §3.1 process; the page says it operates "in the production of specialty chemical additives and precursors", which no §3.1 term names', None, None),
 'ORG-000186': ('no_readable_page', 'A readable copy of the home page (a script-rendered page returned HTTP 200 with no main text; an availability fact)', 'no_readable_page', 'Same'),
 'ORG-000048': ('distributor_supplier_not_process', 'A sentence that Akrochem itself compounds or blends (the pages describe supplying "compounding materials")', None, None),
 'ORG-002157': ('no_readable_page', 'A readable copy of the home page (robots.txt request timed out after the one retry, curl exit 28; an availability fact)', 'no_readable_page', 'Same'),
 'ORG-002049': ('robots_blocked', 'A page the site permits crawlers to read, or a permission from the site', 'robots_blocked', 'Same'),
 'ORG-000555': ('parent_group_page', 'A Rubbermaid page (the record website is the Newell Brands parent site)', 'parent_group_page', 'Same; candidate consumer_goods_housewares quote held'),
 'ORG-000416': ('no_process_named', 'A sentence naming how the vinyl liners and covers are made (the pages say "lean manufacturing processes")', 'no_vocab_market', 'An owner ruling on whether swimming-pool products map to lawn_garden_recreation'),
 'ORG-001648': ('product_spec_not_company_process', 'A sentence that the company itself extrudes or fabricates (the one hit is an HDPE product feature)', 'ambiguous_vocabulary', 'An owner ruling: dam and hydropower customers as infrastructure_civil or energy_renewables_battery'),
 'ORG-000635': ('no_process_named', 'A sentence naming a §3.1 process for brushes and roller covers', 'no_vocab_market', 'A §3.3 term for painting tools (professional painters), or an owner ruling adding one'),
 'ORG-001730': ('no_process_named', 'A sentence naming how the dental resin and cutting products are made', None, None),
 'ORG-000207': ('no_readable_page', 'A readable copy of the home page (HTTP 202 with no body; an availability fact)', 'no_readable_page', 'Same'),
 'ORG-002011': ('no_readable_page', 'A readable copy of the home page (TLS certificate failure, curl exit 60, no insecure retry; an availability fact)', 'no_readable_page', 'Same'),
}
H['ORG-000025'] = (H['ORG-000025'][0], 'A sentence that Musson itself fabricates or assembles, naming the process (candidate fabrication_unspecified held)',) + H['ORG-000025'][2:]
H['ORG-001742'] = (H['ORG-001742'][0], 'A sentence that the company itself sorts, bales, grinds or reprocesses material (candidate recycling_unspecified held)',) + H['ORG-001742'][2:]
H['ORG-000483'] = (H['ORG-000483'][0], 'A sentence naming a polymer process; the pages say pump parts are machined and cartridges made with recycled materials', None, None)
out = []
for f in frame:
    o = f['org_id']
    if (o, 'processes') in filled and (o, 'markets_served') in filled: continue
    pr, ps, mr, ms = H[o]
    for field, reason, fact in (('processes', pr, ps), ('markets_served', mr, ms)):
        if (o, field) in filled: continue
        assert reason, (o, field)
        out.append(dict(org_id=o, field=field, reason=reason, pages_read=readable.get(o, 0), settling_fact=fact or (NP if field == 'processes' else NM)))
with open(D + 'holds.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, ['org_id', 'field', 'reason', 'pages_read', 'settling_fact']); w.writeheader(); w.writerows(out)
print(len(out), 'holds;', sum(r['field'] == 'processes' for r in out), 'process,', sum(r['field'] == 'markets_served' for r in out), 'market')
