#!/usr/bin/env python3
"""Pilot record (34 sites read by hand: the seeded draw of 25 from class A, plus the 9 class-B sites outside the draw).

Writes PILOT.csv. Every quote is replayed word for word against the retained page text before it is written; a quote that is not
on the page stops the run (AGENTS.md section 2 rule 8: quotes are replayed by script). Verdicts per AGENTS.md section 2 rule 8.
Usage: pilot.py [--candidates DIR]   (DIR holds candidates_raw.csv from candidates.py)
"""
import argparse, csv, glob, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import candidates as c  # noqa: E402

V, R, U = 'VERIFIED', 'REJECT', 'STILL_UNCERTAIN'
# site_id: (verdict, quote: a verbatim run beside the street, deciding fact or settling fact)
PILOT = {
 'SITE-001568': (V, 'NextStep Arthropedix, 1800 Triplett Boulevard, Akron, OH, 44306, USA', 'Own site prints NextStep Arthropedix at the street, and states "NextStep Arthropedix is a division of the Akron-based company, Theken"; held name is the parent. Rename to NextStep Arthropedix.'),
 'SITE-001776': (V, 'HAR Adhesive Technologies 60 South Park Street, Bedford, OH 44146', 'Own site (held website) prints HAR Adhesive Technologies at the street and never names Certon; the organization row already records HAR as the operating company and Certon as its brand. Rename to HAR Adhesive Technologies.'),
 'SITE-002008': (V, 'Stroup Belting 2184 State Route 43 Mogadore, Oh 44260', 'Own site (held website) prints Stroup Belting at the street; the held name Stroup & Son Ltd is on no retained page of the site. Trade name, not a legal-form word. Rename to Stroup Belting.'),
 'SITE-001801': (U, 'SealMaster Headquarters 2520 South Campbell Street Sandusky, OH 44870', 'Brand SealMaster beside the street on a multi-location page; Thorworks is on no retained page. Settling fact: a page naming Thorworks Industries as operator of the Sandusky SealMaster location.'),
 'SITE-000273': (U, 'Manufacturing Site 786 Hardy Road Painesville, OH 44077', 'Page names Styropek USA, Inc. (Houston headquarters) and gives the plant street under a label with no name; BVPV Styrenics is on no page. Settling fact: a page or filing naming the operator of the Painesville plant.'),
 'SITE-000522': (R, 'Midwest Office and Mfg. 201 Vista Ave SE Massillon, OH 44646', 'A location label, no name, beside the street.'),
 'SITE-000813': (R, 'Contact Details 5539 Gundy Drive', 'A heading, no name, beside the street.'),
 'SITE-000612': (R, 'CONTACT US ADDRESS: 338 Remington Rd. Cuyahoga Falls, OH 44224', 'An address label, no name.'),
 'SITE-001657': (R, '12621 Chardon Windsor Road Chardon, Ohio 44024', 'Footer copyright says Hi-Tech Extrusions: a spelling variant of High Tech Extrusions on the held domain, not a division, parent or other entity (borderline: reader may disagree).'),
 'SITE-001834': (R, 'Niles Facility 1600 Hunter Street', 'A location label; the page names Niles Building Products.'),
 'SITE-001943': (R, 'Address: 3291 Manchester Road Akron, Ohio USA 44319', 'The block label is ASF, the held name abbreviated, on the parent Poling Group contact page.'),
 'SITE-001823': (R, '671 MCCAULEY RD. | STOW, OH 44224', 'Heading "Reach Out", no name.'),
 'SITE-001862': (R, 'B.F. Plastics, Inc. 1377 Manchester Ave. S.W. North Lawrence, OH 44666', 'B.F. Plastics, Inc. is the held name BF Plastics Inc (punctuation and legal form).'),
 'SITE-000647': (R, 'Timco Rubber 125 Blaze Industrial Parkway', 'Short form of held Timco Rubber Products, Inc.'),
 'SITE-000496': (R, 'Cleveland, OH NPAA Office 11110 Berea Road', 'NPAA is the held name abbreviated.'),
 'SITE-000592': (R, '33490 Pin Oak Parkway , Avon Lake , Ohio 44012', 'Text before the street is a registry code, no name.'),
 'SITE-001851': (R, 'ACTION SUPERABRASIVE INC. 945 Greenbriar Parkway. Kent, OH 44240', 'Held Action Super Abrasive Products, Inc. written as one word without Products: same entity on the held domain (borderline: reader may disagree).'),
 'SITE-000464': (R, '5600 Mayfair Road , North Canton, Ohio 44720', 'Label only, no name.'),
 'SITE-000563': (R, 'Progressive Foam Headquarters 6753 Chestnut Ridge Rd. Beach City, OH 44608', 'Short form of held Progressive Foam Technologies.'),
 'SITE-001578': (R, 'Julius Zorn, Inc. • 3690 Zorn Drive • Cuyahoga Falls, OH 44223', 'Printed name is part of the held name.'),
 'SITE-001861': (R, '1610 Coutant Avenue Lakewood, Ohio 44107', 'A PO box line, no name.'),
 'SITE-001755': (R, '154 East Aurora Road , #123 Northfield, Ohio 44067', 'Heading only, no name.'),
 'SITE-000667': (R, 'Vinylume Windows Location 3745 Hendricks Rd Youngstown,OH 44515', 'Body text calls the company Vinylume Products; Vinylume Windows is a section label.'),
 'SITE-000640': (R, 'Headquarters 10036 Aurora-Hudson Road Streetsboro, OH 44241', 'A label; the held name and trade name stand.'),
 'SITE-000109': (R, 'Contact Information Address 3901 W 150th St , Cleveland, OH 44111', 'Labels only, no name.'),
 'SITE-000039': (R, 'World Headquarters 1331 Kelly Ave. Akron, Ohio 44306', 'A label, no name.'),
 'SITE-000263': (R, 'Blade-Tech Holsters 10125 Wellman Road Streetsboro, OH 44241', 'Held brand Blade-Tech plus a product word; the page names Blade-Tech Industries elsewhere.'),
 'SITE-000071': (R, 'Contact Us Miles Rubber 9020 Dutton Drive, Twinsburg, Ohio 44087', 'Short form of held Miles Rubber & Packing.'),
 'SITE-000436': (R, 'Get in Touch 2700 Atlantic Blvd., NE Canton, Ohio 44705', 'No name beside the street.'),
 'SITE-000569': (R, 'Cleveland Laird Cleveland 4707 Detroit Ave, Cleveland, OH 44102', 'Location list on the parent site; the listing is the held Cleveland Laird.'),
 'SITE-001487': (R, '33490 Pin Oak Parkway , Avon Lake Ohio , 44012', 'Footer address, no name.'),
 'SITE-001613': (R, 'Address: 7740 Metric Drive, Mentor, Ohio 44060', 'Held name carries Frantz Medical Group, which the page uses.'),
 'SITE-001833': (R, 'North East Office 9470 Pinecone Dr. Mentor, OH 44060', 'A label, no name.'),
 'SITE-001924': (R, 'Contact Us 7675 Jenther Dr Mentor, Ohio 44060', 'No name beside the street.'),
 # class C: the page prints the legal or a trade name beside the street, never the site_name's own part (10 of 26 read, chosen by snippet triage)
 'SITE-000672': (V, 'Wooster Elastomers 1205 E Bowman Street Wooster, OH 44691', 'Own site footer prints the legal name Wooster Elastomers at the street; the held site_name Wayne County Rubber is a held trade name.'),
 'SITE-000889': (V, 'SIMONA Boltaron Inc. 1 General Street Newcomerstown, OH 43832 USA', 'Own site prints the legal name SIMONA Boltaron Inc. at the street; the held site_name Empire Plastics is a held trade name, on no retained page.'),
 'SITE-001846': (V, 'Dalin Mold & Machine Contact Us Get in Touch 2915 Industrial Pk Dr Austinburg, OH 44010', 'Own site prints the held trade name Dalin Mold & Machine at the street; the held site_name is the legal name Rubber Mold Design LLC, on no retained page.'),
 'SITE-000279': (V, 'Contact Carlisle TyrFil 140 Sheldon Rd, Berea, OH 44017', 'Own site prints the held trade name Carlisle TyrFil at the street; the held site_name is the legal name, on no retained page.'),
 'SITE-001843': (V, 'Contact Pioneer Athletics 4529 Industrial Parkway Cleveland, OH 44135', 'Own site (held website) prints Pioneer Athletics at the street; The Pioneer Manufacturing Company is on no retained page. Not found by the finder (one-word held name).'),
 'SITE-000401': (V, 'Address IMS Company 10373 Stafford Road Chagrin Falls, Ohio 44023-5296 USA', 'Own site prints the legal name IMS Company at the street; the held site_name IMS Industrial Molding Supplies is a held trade name, on no retained page.'),
 'SITE-000466': (U, 'Medco Coated Products - Adhesive Coating Liners, Films, Foams & Fabrics 5156 Richmond Road, Bedford Heights, Ohio', 'Page header and street line run together; held MEDCO LABS is also on the site. Settling fact: the address block alone naming the operator.'),
 'SITE-000310': (U, 'Creative Packaging Concepts 214 Brace Avenue, Elyria, OH 44035', 'Footer prints the legal name, and the held site_name CPC Bags is a brand the site also uses. Owner call on which name the site carries.'),
 'SITE-000327': (U, 'OEM and Custom Manufacturing by Dott Products in Avon, OH 1273 Lear Industrial Pkwy. Avon, OH 44011', 'Sentence names Dott Products (legal name); held Dott Foam Products differs by one word. Reader call, not a division or parent.'),
 'SITE-000574': (R, 'ADDRESS: HQ/Engineering/R&D 9107 PLEASANTWOOD AVE NW NORTH CANTON, OH 44720', 'Page says Rapid Molding, held Rapid Molds: a variant of one word on the held domain, label before the street.'),
}
# the page evidence is clean either way; whether a brand, trade name or legal-name difference is a rename is an owner question
STATES_DIVISION = {'SITE-001568'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidates', type=Path, default=Path(__file__).parent)
    a = ap.parse_args()
    sites = {r['site_id']: r for p in glob.glob(str(c.ROOT / 'data/sites_*.csv')) for r in c.read(p)}
    pages = c.load_pages(c.CORPORA)
    klass = {r['site_id']: r['cls'] for r in c.read(a.candidates / 'CANDIDATES.csv')}
    out = []
    for sid, (verdict, quote, fact) in PILOT.items():
        s = sites[sid]; rx = c.street_regex(s['street_address'])
        found = None
        for p in pages[s['org_id']]:
            text = Path(p['text_file']).read_text(encoding='utf-8', errors='replace')
            if rx and rx.search(text) and c.on_page(quote, text):
                found = p; break
        assert found, f'{sid}: quote not on any retained page: {quote!r}'
        out.append(dict(site_id=sid, org_id=s['org_id'], held_site_name=s['site_name'], verdict=verdict, quote=quote, page_url=found['url'],
                        capture_sha256=found['sha256'], corpus=found['corpus'], finder_class=klass.get(sid, '-'),
                        names_division_link='yes' if sid in STATES_DIVISION else '', deciding_or_settling_fact=fact))
    with open(Path(__file__).parent / 'PILOT.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, list(out[0])); w.writeheader(); w.writerows(out)
    tally = {v: sum(r['verdict'] == v for r in out) for v in (V, R, U)}
    print(len(out), tally)


if __name__ == '__main__':
    main()
