"""Reviewed verdicts for the 40 framed sites (rows 41-80), the immutable evidence-ID slots, and correction-method findings."""
import sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from prep import read,write
V='VERIFIED_ALL_SEVEN_AT_B'
HOLD={
'SITE-011166':'Own pages never say paint is made at 4808 Farragut Road; the about page says Mercury operates two distribution facilities. A page tying paint manufacture to the filed Brooklyn street is required.',
'SITE-011168':'Own Locations page labels 310 Erie Street Headquarters and 204 Cemetery Road Manufacturing, while the held site is typed a manufacturing plant at 310 Erie. A page tying production to 310 Erie Street, or a dated address correction, is required.',
'SITE-011170':'Own contact page labels 316 Colonial Drive Corporate Headquarters and Warehouse; about and home name only a manufacturing facility in the Finger Lakes Region. A page naming Horseheads as the forming site is required.',
'SITE-011173':'Newer ITA 1284638 files primary code 333248 at 1 Bank St against the held 326199 (OSHA row files 326199). A dated site-specific source settling the primary code is required.',
'SITE-011301':'Both ITA 992721 and the OSHA row file 326299 for Ames Rubber at 19 Ames Blvd against the held primary 326291. A dated site-specific source settling the primary code is required.',
'SITE-011303':'The filed ITA 388683 registrant is Monmouth Rubber Corp. against the held legal name Monmouth Rubber & Plastics Corporation. Explicit linkage between the filed registrant and the held operator is required.',
'SITE-011304':'ITA 1062096 files 326112 at 50 Lafayette Place against the held primary 326199. A dated site-specific source settling the primary code is required.',
'SITE-011305':'Only a 2019 OSHA row exists (OSHAE-0c110feeed), spelled 1969 Rugers University Blvd and coded 325991 against the held 325510. A current filing or page settling operator street and code is required.',
'SITE-011307':'Newer OSHA OSHAE-e0b44e421e (2026-04-28) files 326111 for All American Poly at 40 Turner Place against the held 326113. A dated source settling the primary code is required.',
'SITE-011308':'Own page passed the raw plant witness, but the site county cell is blank and the Census geocoder returned no match for 50 Flexcraft Drive 07753. A physical-address county determination must be applied first.',
'SITE-011309':'ITA 870462 files 326112 and the older OSHA row files 325211, against the held 326111. A dated site-specific source settling the primary code is required.',
'SITE-011310':'ITA 838354 files 326113 at 103 West Park Drive against the held 326199. A dated site-specific source settling the primary code is required.',
'SITE-011311':'Own page passed the raw plant witness and Census matched 360 W Oakland Ave (Bergen County), but the site county cell is blank, so the address must-have cannot be raised to B. Apply the Census county through the correction method first.',
'SITE-011312':'Own pages are ROBOTS_BLOCKED (availability, not absence) and the record carries a scope flag for pigment dispersions. A readable own page and the owner scope ruling are required.',
'SITE-011314':'The filed ITA 1230281 row at 1301 Park Ave S carries a blank company name. A filing or page naming Rotuba Extruders as the operator at this street is required.',
'SITE-011315':'The creating lane flagged scope: vinyl pool liners and safety covers made from purchased film and fabric, with no stated process. An owner scope ruling or a page stating a polymer process at Hamilton is required.',
'SITE-011316':'The about page names the South Plainfield manufacturing facility but no polymer material; the polypropylene filament page says the filament is custom manufactured but labels the address only Global Headquarters. One page tying poly filament or strip-broom production to South Plainfield, or an owner scope ruling for NAICS 339994 brooms, is required.',
'SITE-011318':'The filed ITA 183832 and OSHA registrant at 60 Green Pond Road is Endot Industries, not Infra Pipes. Explicit linkage between Endot Industries and the held operator is required.',
'SITE-011319':'ITA 1430390 files 326113 at 879 Main Street against the held 326199, and the OSHA row carries ZIP 08872 against 08861. A dated source settling code and ZIP is required.',
'SITE-011320':'The filed ITA 1477397 registrant is BWAY Dayton against the held Mauser Packaging Solutions, and the OSHA row files 326121. Explicit dated linkage of the BWAY registrant to the held operator and code is required.',
'SITE-011321':'The Pennsauken locations page prints the operator, street and about 200 associates but no manufacturing statement, and the ISO certificate PDF fetch failed (availability). A readable Pennsauken page stating manufacture is required.',
'SITE-011322':'The filed ITA 1428084 registrant is Amcor Rigid Packaging against the held Amcor Flexibles North America. Explicit linkage of the rigid-packaging registrant to the held operator at 625 Sharp Street is required.',
'SITE-011323':'The filed ITA 969350 registrant is Saint-Gobain, not the held Saint-Gobain Performance Plastics. Explicit linkage of the filed registrant to the held operator at 150 Dey Road is required.',
'SITE-011451':'Home page names the plant and its manufacturing but not Browns Summit; the news post that names Browns Summit is a dated announcement, not a present-tense plant witness. One page tying Browns Summit to current heat-shrink film production is required.',
'SITE-011452':'Newer ITA 1530623 (2026-03-02) files 326112 at 1809 Airport Rd against the held 326140. A dated source settling the primary code is required.',
'SITE-011453':'Both modernpolymers.com routes are ROBOTS_BLOCKED or failed (availability, not absence). A readable own page naming the Cherryville plant activity is required.',
'SITE-011454':'The filed OSHA registrant is R-D PLASTICS OF HICKORY, LTD., which does not match the held name R&D Plastics of Hickory, Ltd. under the literal alias rule. Recorded alias linkage is required.',
'SITE-011455':'The creating lane flagged scope: synthetic filament yarn under NAICS 325220, a supporting-signal code. An owner scope ruling is required before the scope claim can stand at B.',
'SITE-011457':'ITA 1378177 files 333248 (machinery) at 4833 W Gate City Blvd against the held 326199, and the OSHA registrant is Thunderbird Molding. A dated source settling code and registrant is required.',
'SITE-011458':'The page names Polyart America, Inc. at 10901 Westlake Drive and says Polyart is made by Arjobex, with no statement that Charlotte produces. Linkage of Arjobex America to Polyart America and a Charlotte production statement are required.',
'SITE-011459':'The creating lane flagged scope: a tire retread shop that is Ring 1 only if it cures or bonds tread on site, which the page does not say. An owner ring ruling or a page stating on-site curing is required.',
}
FINDINGS=[
('SITE-011168','Own exact-street function differs from manufacturing_plant','Apple Rubber Locations page: Headquarters 310 Erie Street; Manufacturing 204 Cemetery Road, Lancaster NY.','https://www.applerubber.com/about/locations-and-directions/','Correction-method lead; no site, status, type or street change in this PR.'),
('SITE-011170','Own exact-street function differs from manufacturing_plant','Rimco contact page: LOCATION Corporate Headquarters and Warehouse Rimco Plastics Corporation 316 Colonial Drive Horseheads, New York 14845.','https://rimcoplastics.com/contact/','Correction-method lead only. HQ and warehouse wording alone does not prove absence of manufacturing.'),
('SITE-011166','Plant function not stated at the filed street','Mercury Paint about page: Mercury operates two distribution facilities; no page sentence places paint manufacture at 4808 Farragut Road.','https://www.mercurypaint.com/about','Correction-method lead only; manufacture is stated for the company, not for the street.'),
('SITE-011318','Conflicting source identity at same street','Filed ITA 183832 and OSHA registrant Endot Industries at 60 Green Pond Road, Rockaway; held operator is Infra Pipes.','https://www.infrapipes.com/locations','Reconcile source-fusion identity before any promotion or correction; no operator reassignment.'),
('SITE-011173','Primary-code conflict at same street','ITA 1284638 (2026-02-03) files 333248 for PM Plastics at 1 Bank St; OSHA row files 326199; held primary is 326199.','https://pmplastics.net/our-company/','No code or ring self-ruling; correct the primary code only after a dated site-specific source settles it.'),
('SITE-011457','Primary-code conflict at same street','ITA 1378177 files 333248 for Thunderbird, LLC at 4833 W Gate City Blvd; held primary is 326199; OSHA registrant is Thunderbird Molding - Greensboro.','https://thunderbird-molding.com/greensboro-north-carolina/','No code or ring self-ruling; correct the primary code only after a dated site-specific source settles it.'),
('SITE-011452','Newer competing filed code at same street','ITA 1530623 (2026-03-02) files 326112 for Darnel Inc at 1809 Airport Rd; held primary is 326140.','https://darnelgroup.com/en-us/about-us','No code or ring self-ruling; settle the primary code with a dated site-specific source.'),
]
def main():
 inputs=read(H/'input.csv');sel={r['site_id'] for r in read(H/'selected.csv')};rows=[]
 assert set(HOLD)|sel=={r['site_id'] for r in inputs} and not (set(HOLD)&sel) and len(sel)==9,(len(HOLD),len(sel))
 for i in inputs:
  s=i['site_id'];rows.append(dict(site_id=s,cluster_id=i['cluster_id'],verdict='VERIFIED' if s in sel else 'STILL_UNCERTAIN',reason='All seven must-have claims at B; raw own-site city/activity plus held operator/address/code corroboration.' if s in sel else HOLD[s]))
 write(H/'verdicts.csv',rows,['site_id','cluster_id','verdict','reason'])
 write(H/'id_slots.csv',[dict(site_id=s,slot=n,first_evidence_id=f'EVD-{330000+n*7:06d}') for n,s in enumerate(sorted(sel))],['site_id','slot','first_evidence_id'])
 write(H/'retired_ids.csv',[],['site_id','evidence_id','reason'])
 write(H/'findings.csv',[dict(site_id=s,scope='worked40 (rows 41-80)',finding=f,own_page=o,url=u,disposition=d) for s,f,o,u,d in FINDINGS],['site_id','scope','finding','own_page','url','disposition'])
 print(len(rows),'verdicts',len(sel),'verified')
if __name__=='__main__':main()
