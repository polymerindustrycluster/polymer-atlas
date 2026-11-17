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

PROV = {
 '1': 'held-record ORG-000416 website glipoolproducts.com (not fetched)', '6': 'held-record ORG-000290 website cosmocorp.com', '17': 'held-record ORG-000825 website engineeredprofiles.com',
 '19': 'held-record ORG-000636 website wraptite.com', '28': 'held-record ORG-000117 website noramcobag.com (paths /contact-us/ and /company/about-us/ from site links/redirect)',
 '39': 'held-record ORG-000336 website extrudex.net (paths /contact-us/ and /about-us/facilities/)', '43': 'held-record ORG-001597 website itps-inc.com',
 '32': 'held-record ORG-000600 website technoform.com', '52': 'held-record ORG-000600 website technoform.com', '80': 'held-record ORG-000140 website clevelandsp.com (not fetched)',
 '7': "web search 'Horizons Incorporated 18351 S Miles Rd Cleveland Ohio' -> https://horizonsisg.com/about",
 '36': "web search 'American Quality Stripping Inc Sandusky Ohio weatherstripping 1750 5th St' -> https://www.americanqualitystripping.com/degreasing-dirt-removal",
 '37': "web search 'Ques Industries Brook Park Ohio 5420 140th St' -> https://www.quesinc.com",
 '58': "web search 'Helical Line Products Company Avon Lake Ohio 659 Miller Rd' -> http://helical-line.com",
 '12': "web search 'Pioneer National Latex Ashland Ohio latex products official website' -> https://www.pioneerballoon.com",
 '47': "web search 'R.C.A. Rubber Company Flexi-Flor sheet rubber flooring Akron Ohio contact' -> directory pages listing www.rcarubber.com",
 '69': "web search 'Genesis Plastic Technologies Solon Ohio 27200 Tinkers Ct' -> result text names genesisplastic.com (does not resolve)",
 '74': "web search 'Chagrin Valley Soap & Salve Solon Ohio' -> https://chagrinvalleysoapandsalve.com/pages/about"}
NONE = 'none: no held-record or search-returned URL; first-lane guessed domain discarded'

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
  "Street 951 Jaycox Rd., Avon is held in SITE-000228 (ORG-000215, Advanced Polymer Coatings). No own page read.", 'dedupe')
D(43, 'DUPLICATE_OF', 'ORG-001597;SITE-001669', 'International Technical Polymer Systems',
  "Own site (itps-inc.com) is the held domain of ORG-001597, Niles, Trumbull County; the site text says Rubber Processing, Injection Molding, and Extrusion Technology.", 'own-site',
  [W(43, ('mine', 'itps_home'), 'Specialists in Rubber Processing, Injection Molding, and Extrusion Technology Find us in Niles, Ohio')])
D(80, 'DUPLICATE_OF', 'ORG-000140;SITE-000140', 'Cleveland Specialty Products, Inc.',
  "Held ORG-000140 has the same name (the lead spells it SPECIALY) in Cleveland; match is name plus city only. No own page read. Alias follow-up only.", 'dedupe')

# ---- shared street or group with a held record: hold with that fact ----
D(59, 'STILL_UNCERTAIN', 'SITE-001777', '', "Street 2926 Chester Avenue, Cleveland is the held street of SITE-001777 (Cru Performance Coatings, ORG-001701). Needs the company's own page naming its operator and establishment, as with the MVP refutation.", 'dedupe')
D(18, 'STILL_UNCERTAIN', 'SITE-000928', '',
  "Street 509 Water Street, Bolivar sits in the notes of held SITE-000928 (GMR Material Technology, ORG-000354). No own page tied to the lead (a directory listing names a Bolivar plastics molder; its own site was not found by search). Settling fact: an own page or federal filing tying a Bolivar establishment to this name or to GMR.", 'search')
D(65, 'STILL_UNCERTAIN', 'ORG-000354', '', "GMR Kent shares the GMR group with held ORG-000354 (SITE-000378 Ashtabula, SITE-000928 Bolivar). Needs own page for the Kent establishment and its operator.", 'dedupe')
D(32, 'STILL_UNCERTAIN', 'ORG-000600;SITE-000639', 'Technoform North America, Inc.',
  "Own page prints 1755 Enterprise Parkway, Suite 300, Twinsburg; held ORG-000600 Technoform has SITE-000639 in Twinsburg without a street. Subsidiary-versus-parent and exact site grain not settled; no edit.", 'own-site',
  [W(32, ('prior', '32', 2), 'Technoform North America, Inc. 1755 Enterprise Parkway, Suite 300 OH 44087 Twinsburg USA')])
D(52, 'STILL_UNCERTAIN', 'ORG-000600;SITE-000639', 'Technoform North America, Inc.',
  "Same street and group as rank 32 and held ORG-000600; the Glass Insulation name is a second borrower name at one address. Same settling fact as rank 32.", 'own-site', [V['32'][5].split(';')[0]])
D(64, 'STILL_UNCERTAIN', '', 'Eveready Products',
  "Own page says it is now part of Zenex (group); polymer scope not shown. Same group fact as rank 34.", 'own-site',
  [W(64, ('prior', '64', 0), 'Eveready Is Now Part of Zenex')])
D(34, 'STILL_UNCERTAIN', '', '', "No URL tied to the lead: search returned only directory and aggregator pages placing One Zenex Circle in Cleveland and describing private-label aerosol and liquid products. Polymer scope is an owner scope question (recommendation: out of scope unless an own page shows polymer products).", 'search')
D(64, 'STILL_UNCERTAIN', '', '', "No URL tied to the lead; the first lane's guessed domain is discarded. A search for the Zenex group (rank 34) shows no own page for Eveready. Settling fact: an own page naming Eveready Products and its establishment.", 'search')

# ---- own page or search read, no create possible ----
D(47, 'STILL_UNCERTAIN', '', 'R.C.A. Rubber Company (per search)',
  "Best prospect left: search results describe R.C.A. Rubber, Akron, as a sheet-rubber-flooring maker (not held; dedupe zero hits at all 5 steps). Directory pages returned by search list www.rcarubber.com, which answers with a 114-byte redirect page (raw/rca_home.html, an availability observation, not a quote). Settling fact: a current own page or federal filing for its Akron establishment.", 'search')
D(75, 'STILL_UNCERTAIN', '', 'Command Plastic Corporation (per search)',
  "Not held (dedupe zero hits, 5 steps). Directories describe a vinyl-packaging maker in Tallmadge but name no own-site URL I can tie to it (the first lane's guessed domain is discarded; my own fetches of that guess failed). Settling fact: an own-site URL returned by search or linked from a fetched page, then its page.", 'search')
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
D(74, 'REJECT', '', 'Chagrin Valley Soap & Salve', "Own page (domain returned by search 'Chagrin Valley Soap & Salve Solon Ohio'), same name as the lead, shows a business outside polymer scope: \"Natural & Organic Skin Care\".", 'own-site',
  [W(74, ('prior', '74', 0), 'Natural & Organic Skin Care')])
for rank, name, why in [
    (11, 'Hilltop Energy', 'search found no own URL for the lead; directory pages describe a Lisbon, Ohio explosives and blasting firm, so scope looks out of polymer'),
    (79, 'Auto Dealer Designs', 'search found no own URL for the lead (a likely product site, licenseframes.com, is not confirmed as the same company); directory pages describe dealer license-plate frames'),
    (62, '', 'the first lane\'s guessed domain is a different company and is discarded; no own URL for the lead'),
    (68, '', 'the first lane\'s guessed domain is a different company and is discarded; no own URL for the lead'),
    (77, '', 'the first lane\'s guessed domain is discarded; no own URL tied to the lead')]:
    D(rank, 'STILL_UNCERTAIN', '', name, f"No own page tied to the lead by name and location: {why}.", 'search')

# ---- held-record facts for shared-name or shared-group holds ----
D(6, 'STILL_UNCERTAIN', 'ORG-000290', 'Cosmo Corporation', "Domain cosmocorp.com is the held domain of ORG-000290 Cosmo Corporation (Solon); the own pages read do not print the name Cosmo Plastics Company. Alias unconfirmed; no edit.", 'dedupe')
D(17, 'STILL_UNCERTAIN', 'ORG-000825', 'Engineered Profiles', "Domain engineeredprofiles.com is the held domain of ORG-000825 (sites: Columbus, Ironton). The own page read names no Mansfield establishment, so EP Holdings of Mansfield is an unconfirmed alias or a new site of the held parent.", 'dedupe')
D(19, 'STILL_UNCERTAIN', 'ORG-000636', 'Wrap Tite', "Held ORG-000636 Wrap Tite (Solon, wraptite.com, two sites without streets); wraptite.com answered 403, so the BDG Wrap-Tite alias and establishment are unconfirmed.", 'dedupe')
D(23, 'STILL_UNCERTAIN', 'SITE-000237', 'MVP Plastics', "Street shared with held SITE-000237 (All Foam Products, ORG-000223); the first lane's refutation stands. Settling fact: primary operator and distinct-establishment evidence.", 'dedupe')
D(48, 'STILL_UNCERTAIN', 'ORG-001931;SITE-001925', '', "Held ORG-001931 is Cooper Standard Industrial and Specialty Group (Lauren Manufacturing), New Philadelphia; whether Lauren International at the Tech Park Drive address is that establishment or a separate company is unsettled.", 'dedupe')

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
    w = csv.writer(f); w.writerow(['rank', 'verdict', 'disposition', 'target_record', 'own_site_name', 'settling_fact', 'work_done', 'url_provenance', 'witness_ids'])
    for k in held:
        v = V[k]; w.writerow([k, v[0], 'held', v[1], v[2], v[3], v[4], PROV.get(k, NONE), v[5]])
with open(HERE / 'witnesses.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['witness_id', 'rank', 'url', 'raw_file', 'sha256', 'quote']); w.writeheader(); w.writerows(WIT)
print(len(held), 'verdicts', len(WIT), 'witnesses')
