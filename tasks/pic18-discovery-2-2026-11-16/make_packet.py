#!/usr/bin/env python3
"""One-off packet generator: adjudications of the 72 held PIC-18 leads -> verdicts.csv + witnesses.csv.
Quotes are validated against stored raw pages (words in order); build.py/check.py re-validate."""
import csv, hashlib, json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
S = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist')
PRIOR, MINE = S / 'pic18-discovery-leads', S / 'pic18-discovery-2' / 'raw'
PRIOR_PR = HERE / 'prior_pr356_verdicts.csv'  # copy of PR #356 verdicts (generic holds)

def words(t): return re.findall(r'[a-z0-9]+', t.lower())
def locate(src):
    if src[0] == 'prior':
        r = json.load(open(PRIOR / src[1] / 'receipt.json'))
        return PRIOR / src[1] / f'{src[2]}.html', PRIOR / src[1] / f'{src[2]}.txt', r['pages'][src[2]]['url']
    meta = (MINE / f'{src[1]}.meta').read_text().split()
    return MINE / f'{src[1]}.html', MINE / f'{src[1]}.txt', meta[1]

WIT = []
def W(rank, src, quote):
    html, txt, url = locate(src)
    tw, qw = words(txt.read_text()), words(quote)
    assert any(tw[i:i + len(qw)] == qw for i in range(len(tw))), ('quote not on page', rank, quote)
    wid = f'W{len(WIT) + 1:03d}'
    WIT.append(dict(witness_id=wid, rank=rank, url=url, raw_file=str(html.relative_to(S)),
                    sha256=hashlib.sha256(html.read_bytes()).hexdigest(), quote=quote))
    return wid

V = {}  # rank -> (verdict, target, own_name, fact, work, [witness ids])
def D(rank, verdict, target, own, fact, work, wits=()): V[str(rank)] = (verdict, target, own, fact, work, ';'.join(wits))

# ---- held already (the first lane's guessed-domain dedupe missed these) ----
D(1, 'DUPLICATE_OF', 'ORG-000416;SITE-000445', 'GL International / GLI Pool Products',
  'Street 215 Sinter Court, Youngstown is the held street of SITE-000445 (ORG-000416, domain exact glipoolproducts.com); alias follow-up only.', 'dedupe')
D(28, 'DUPLICATE_OF', 'ORG-000117;SITE-000116', 'North American Plastics & Chemicals',
  "Own contact page prints 1400 E. 222nd. St., Euclid, OH 44117, identical to held SITE-000116 (ORG-000117, domain noramcobag.com).", 'own-site',
  [W(28, ('mine', 'noramco_contact'), 'Corporate Office Address: 1400 E. 222nd. St. Euclid, OH 44117')])
D(39, 'DUPLICATE_OF', 'ORG-000336;SITE-000357', 'Extrudex',
  "Own contact page prints 310 Figgie Road, Painesville, OH 44077, the held street of SITE-000357 (ORG-000336, domain extrudex.net); the first lane's guessed extrudex.com was the wrong domain.", 'own-site',
  [W(39, ('mine', 'extrudex_contact'), '310 Figgie Road, Painesville, OH 44077')])
D(41, 'DUPLICATE_OF', 'ORG-000215;SITE-000228', 'Advanced Polymer Coatings',
  "Street 951 Jaycox Rd., Avon is held in SITE-000228 (ORG-000215). The guessed domain advpolymer/apcoat is a different company (own page prints Carlstadt, NJ).", 'own-site',
  [W(41, ('mine', 'apc_home'), '400 Paterson Plank Rd. Carlstadt, NJ 07072')])
D(43, 'DUPLICATE_OF', 'ORG-001597;SITE-001669', 'International Technical Polymer Systems',
  "Own site (itps-inc.com) is the held domain of ORG-001597, Niles, Trumbull County; the site text says Rubber Processing, Injection Molding, and Extrusion Technology.", 'own-site',
  [W(43, ('mine', 'itps_home'), 'Specialists in Rubber Processing, Injection Molding, and Extrusion Technology Find us in Niles, Ohio')])
D(80, 'DUPLICATE_OF', 'ORG-000140;SITE-000140', 'Cleveland Specialty Products, Inc.',
  "Held ORG-000140 has the same name (the lead spells it SPECIALY) in Cleveland; the guessed domain clevelandspecialty.com is Cleveland Specialty Inspection Services of Mentor, a different company. Alias follow-up only.", 'own-site',
  [W(80, ('prior', '80', 0), 'CLEVELAND SPECIALTY INSPECTION SERVICES, INC. 8562 East Avenue Mentor, Ohio 44060')])

# ---- shared street or group with a held record: hold with that fact ----
D(59, 'STILL_UNCERTAIN', 'SITE-001777', '', "Street 2926 Chester Avenue, Cleveland is the held street of SITE-001777 (Cru Performance Coatings, ORG-001701). Needs the company's own page naming its operator and establishment, as with the MVP refutation.", 'dedupe')
D(18, 'STILL_UNCERTAIN', 'SITE-000928', 'Suburban Plastics Company',
  "Street 509 Water Street, Bolivar sits in the notes of held SITE-000928 (GMR Material Technology, ORG-000354). The only own page found (suburbanplastics.com) names Elgin IL and Grenada MS and no Ohio site. Settling fact: an own page or federal filing tying a Bolivar establishment to this name or to GMR.", 'own-site',
  [W(18, ('mine', 'suburban_home'), 'Currently, Suburban Plastics operates in two locations, Elgin, Illinois and Grenada, Mississippi.')])
D(65, 'STILL_UNCERTAIN', 'ORG-000354', '', "GMR Kent shares the GMR group with held ORG-000354 (SITE-000378 Ashtabula, SITE-000928 Bolivar). Needs own page for the Kent establishment and its operator.", 'dedupe')
D(32, 'STILL_UNCERTAIN', 'ORG-000600;SITE-000639', 'Technoform North America, Inc.',
  "Own page prints 1755 Enterprise Parkway, Suite 300, Twinsburg; held ORG-000600 Technoform has SITE-000639 in Twinsburg without a street. Subsidiary-versus-parent and exact site grain not settled; no edit.", 'own-site',
  [W(32, ('prior', '32', 2), 'Technoform North America, Inc. 1755 Enterprise Parkway, Suite 300 OH 44087 Twinsburg USA')])
D(52, 'STILL_UNCERTAIN', 'ORG-000600;SITE-000639', 'Technoform North America, Inc.',
  "Same street and group as rank 32 and held ORG-000600; the Glass Insulation name is a second borrower name at one address. Same settling fact as rank 32.", 'own-site', [V['32'][5].split(';')[0]])
D(64, 'STILL_UNCERTAIN', '', 'Eveready Products',
  "Own page says it is now part of Zenex (group); polymer scope not shown. Same group fact as rank 34.", 'own-site',
  [W(64, ('prior', '64', 0), 'Eveready Is Now Part of Zenex')])
D(34, 'STILL_UNCERTAIN', '', 'Zenex International',
  "Own page lists Adhesives & Sealants and Coolants & Coatings as product categories at One Zenex Circle (Bedford) and aerosol manufacturing at 1101 Belt Line Avenue, Cleveland. A menu item is supports_C only, so polymer scope is an owner scope ruling.", 'own-site',
  [W(34, ('prior', '34', 0), 'Corporate Headquarters One Zenex Circle Cleveland, OH 44146')])

# ---- own page or search read, no create possible ----
D(47, 'STILL_UNCERTAIN', '', 'R.C.A. Rubber Company (per search)',
  "Best prospect left: search results describe R.C.A. Rubber, Akron, as a sheet-rubber-flooring maker (not held; dedupe zero hits at all 5 steps). Its domain rcarubber.com answered with a 114-byte redirect page (raw/rca_home.html, an availability observation, not a quote) and srpindustries.com with a 403 bot challenge. Settling fact: a current own page or federal filing for its Akron establishment.", 'search')
D(75, 'STILL_UNCERTAIN', '', 'Command Plastic Corporation (per search)',
  "Not held (dedupe zero hits, 5 steps). Directories describe a vinyl-packaging maker in Tallmadge, but its own site failed (TLS handshake alert on both hosts, HTTP 409 on plain http). Availability, not absence. Settling fact: its own page read through another route.", 'search')
D(69, 'STILL_UNCERTAIN', '', 'Genesis Plastic Technologies LLC (per search)',
  "Not held (dedupe zero hits). Directories describe an injection molder in Solon; the website in directories (genesisplastic.com) does not resolve. Settling fact: its own page.", 'search')
D(76, 'STILL_UNCERTAIN', '', '', "No company at this name and address found by search; guessed domain does not resolve. Settling fact: an own page or filing.", 'search')
D(12, 'STILL_UNCERTAIN', '', 'Pioneer National Latex', "Own group page (pioneerballoon.com) fetched, no Ashland establishment on it. A search summary of a 2023 local news item says Ashland production ended; unfetched, so no status change is asserted. Settling fact: dated outcome record plus the Form 5500 check (AGENTS 8).", 'search')
D(37, 'STILL_UNCERTAIN', '', 'Ques Industries, Inc.',
  "Own page: private-label blending of water-treatment and cleaning products; chemical blender, no polymer work shown. Owner scope ruling (recommendation: out of scope).", 'own-site',
  [W(37, ('mine', 'ques_home'), 'Ques Industries, Inc. offers quick turnaround for custom formulations')])
D(7, 'STILL_UNCERTAIN', '', 'Horizons Imaging Systems Group',
  "Own page: manufacturer of printable aluminum for labels and nameplates; material is metal. Owner scope ruling (recommendation: out of scope).", 'own-site',
  [W(7, ('mine', 'horizons_about'), 'manufacturer of printable aluminum used to produce labels, nameplates, equipment panels and more')])
D(36, 'STILL_UNCERTAIN', '', 'American Quality Stripping, Inc.',
  "Own page: coating removal and surface preparation services; not polymer production. Owner scope ruling (recommendation: out of scope).", 'own-site',
  [W(36, ('mine', 'aqs_home'), 'Providing coating removal and surface preparation services to the painting industry since 1987')])
D(58, 'STILL_UNCERTAIN', '', 'Helical Line Products Company',
  "Own page: helically shaped products for the electrical utility market (spiral formed wire); no polymer scope shown.", 'own-site',
  [W(58, ('mine', 'helical_home'), 'Helical Line Products Company is a North American manufacture of helically shaped products used primarily by the electrical utility market')])

# ---- REJECT: own page states a business with no polymer, chemical or material link ----
for rank, name, src, q in [
    (11, 'Hilltop Energy', ('prior', '11', 0), 'Hilltop Energy – Drill and Blast Services, Mixing Plant'),
    (62, 'Olmsted Transportation Co., Inc.', ('prior', '62', 0), 'Car Hauling Services for WA, OR, BC'),
    (68, 'Deters Law, LLC', ('prior', '68', 0), 'Estate Planning Asset Protection Planning Special Needs Planning Probate'),
    (77, 'Harbor Industrial Services, Inc.', ('prior', '77', 0), 'Port Services and Solutions - Harbor Industrial Services, Inc.'),
    (79, 'Auto Dealer Designs', ('prior', '79', 0), 'Dealership Supplies - Find Them at Auto Dealer Designs'),
    (74, 'Chagrin Valley Soap & Salve', ('prior', '74', 0), 'Natural & Organic Skin Care')]:
    D(rank, 'REJECT', '', name, f"Own page shows a business outside polymer scope: \"{q}\".", 'own-site', [W(rank, src, q)])

# ---- everything else: generic hold carried from PR #356 with the work done recorded ----
prior = {r['rank']: r for r in csv.DictReader(open(PRIOR_PR))}
frame = {r['rank']: r for r in csv.DictReader(open(PRIOR / 'frame.csv'))}
held = [k for k in sorted(frame, key=int) if prior[k]['verdict'] != 'DUPLICATE_OF']
assert len(held) == 72
for k in held:
    if k not in V:
        V[k] = ('STILL_UNCERTAIN', '', '', 'Not re-researched to a verdict in this lane; first-lane settling fact stands: ' + prior[k]['settling_fact'], 'dedupe', '')
assert set(V) == set(held), (set(V) ^ set(held))

with open(HERE / 'verdicts.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['rank', 'verdict', 'disposition', 'target_record', 'own_site_name', 'settling_fact', 'work_done', 'witness_ids'])
    for k in held:
        v = V[k]; w.writerow([k, v[0], 'held', v[1], v[2], v[3], v[4], v[5]])
with open(HERE / 'witnesses.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['witness_id', 'rank', 'url', 'raw_file', 'sha256', 'quote']); w.writeheader(); w.writerows(WIT)
print(len(held), 'verdicts', len(WIT), 'witnesses')
