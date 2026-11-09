"""Adjudication of the 34 medium clusters of tasks/site-name-dedupe-2026-11-06/leads.csv (strength == medium).

This file is the packet: every verdict and its deciding fact. build.py renders it to CSV; check.py verifies it against
data/. Grammar (AGENTS §2 rule 8): DUPLICATE_OF / DISTINCT / STILL_UNCERTAIN.

Pair  = (cluster, level, a, b, verdict, survivor, state, basis, fact, sources, operator_org)
  level   org | site
  verdict DUPLICATE_OF (survivor is a or b; the other folds into it) | DISTINCT | STILL_UNCERTAIN (survivor empty)
  state   recorded = the tree already carries the fold (status merged/acquired + successor, or a tombstone note)
          to_apply = the integrator PR has to apply it      n/a = DISTINCT / STILL_UNCERTAIN
  basis   how check.py re-derives a to_apply site fold from data/: shared_frs_id | same_street | street_variant |
          same_city_streetless (one row has no street; needs a cited FRS/WEB witness) ; org folds: same_website |
          division_of_survivor_site (site pair in the same cluster at one street)
  survivor rule (checked): the record holding more registry_links + relationships, then more evidence rows, survives
          (ties keep the stated survivor); so a fold orphans the least history. A site survivor under a non-operator org
          is repointed (`operator_org` names the operator; blank = operator unsettled, needs a hold_operator action)
Action = (cluster, action, record, target, state, fact, sources)
  repoint_site  site belongs to the operator `target`, not to its current parent (AGENTS §3: operator, never brand owner)
  hold_operator operator not settled; `fact` names the settling fact
Sources: TREE:<id> (a field or note of that data/ row), FRS:<registry id> (EPA ECHO exporter row, frs_excerpt.csv),
WEB:<id> (a page cached under persist/, evidence.csv).
"""

# (id, cached file, url, quote) -- quotes are re-checked raw against the cached page by check.py
EVIDENCE = [
    ("W01", "goodyear-divest.txt", "https://news.goodyear.com/2025-11-03-Goodyear-Completes-Divestiture-of-Chemical-Business",
     "completed the previously announced divestiture of the majority of its Goodyear Chemical business to an affiliate of Gemspring Capital Management, LLC, effective Oct. 31, 2025"),
    ("W02", "gemspring-pr.txt", "https://www.gemspring.com/gemspring-capital-completes-acquisition-of-the-goodyear-tire-rubber-companys-polymer-chemicals-business",
     "The acquisition includes two manufacturing plants in Houston and Beaumont, Texas, as well as a research and development facility in Akron, Ohio. Goodyear will retain its chemical facilities in Niagara Falls, New York, and Bayport, Texas"),
    ("W03", "ludlow-about.txt", "https://www.ludlowcomp.com/about-ludlow-composites",
     "The company rebranded the two operating divisions, the foam and matting divisions to Crown Matting Technologies and Crown Foam Technologies, and began operating the Ludlow name as the parent company."),
    ("W04", "ludlow-about.txt", "https://www.ludlowcomp.com/about-ludlow-composites",
     "Present day Ludlow Composites Corp. is still located at 2100 Commerce Drive."),
    ("W05", "ccg-home.txt", "https://www.creativecompositesgroup.com/",
     "Companies Composite Advantage Creative Pultrusions Enduro Composites E.T. Techtonics Kenway Composites Trident Industries United Fiberglass"),
    ("W06", "ultrapoly-about.txt", "https://ultrapoly.com/about",
     "oversees operations of all 5 of Ultra-Poly's production facilities"),
    ("W07", "ultrapoly-about.txt", "https://ultrapoly.com/about",
     "Ultra-Poly Corporation Headquarters 102 Demi Rd. P.O. Box 330 Portland, PA 18351"),
    ("W08", "farathane-home.txt", "https://www.usfarathane.com/",
     "© 2023 by US Farathane Corporation"),
    ("W09", "farathane-locations.txt", "https://www.usfarathane.com/locations",
     "4872 S Lapeer Rd, Lake Orion, MI 48359"),
    ("W10", "tyrfil-home.txt", "https://carlisletyrfil.com/",
     "140 Sheldon Rd, Berea, OH 44017"),
    ("W11", "tyrfil-home.txt", "https://carlisletyrfil.com/",
     "Copyright 2026 Carlisle TyrFil"),
    ("W12", "dpc-home.txt", "https://www.dpcpipe.com/",
     "Diamond Plastics Corporation 1212 Johnstown Road Grand Island, NE 68803"),
]

# EPA ECHO exporter rows (cache/bulk/frs.sqlite, fetched 2026-11-06) cited below
FRS_IDS = """110071410584 110012554770 110070566727 110004698300 110000825723 110025332959 110000356347 110070025854
110002095768 110001059121 110009815539 110000386029 110000386494 110000386920 110049721627 110000462231 110061782566
110000389491 110000385244 110009662855 110071154405 110070684578 110070207889 110044232238 110023859083 110000383219
110004735109 110000823431 110000388937 110000387554 110000391371 110070273580 110057329485 110001219556 110031820126
110015537007 110043412278 110017617373 110067597960 110001516501 110031298423 110000841331 110004617781 110018011088""".split()

PAIRS = []   # filled by P()
ACTIONS = []


def P(cluster, level, a, b, verdict, survivor, state, basis, fact, sources, operator_org=""):
    PAIRS.append(dict(cluster=cluster, level=level, record_a=a, record_b=b, verdict=verdict, survivor=survivor,
                      state=state, basis=basis, fact=fact, sources=sources, operator_org=operator_org))


def A(cluster, action, record, target, state, fact, sources):
    ACTIONS.append(dict(cluster=cluster, action=action, record=record, target=target, state=state, fact=fact,
                        sources=sources))


# cluster-level headline fact + sources (the verdict itself is derived from the org-level pairs by check.py)
CLUSTER = {}


def C(cluster, fact, sources):
    CLUSTER[cluster] = dict(fact=fact, sources=sources)


# ---------------------------------------------------------------- 0009 Barentz
C("SND-0009", "ORG-001846 'Barentz' (website maroongroupllc.com) is already status=merged into ORG-000242 'Barentz North America' (2026-10-29); the cluster's one site SITE-000258 (1390 Jaycox Rd, Avon) already sits under the survivor. EPA lists BARENTZ AVON and MAROON INCORPORATED at that address: one establishment, one operator.",
  "TREE:ORG-001846;TREE:ORG-000242;FRS:110071410584;FRS:110012554770")
P("SND-0009", "org", "ORG-001846", "ORG-000242", "DUPLICATE_OF", "ORG-000242", "recorded", "",
  "status=merged, successor_org_id=ORG-000242; same HQ city (Avon OH). No unmerged duplicate remains.", "TREE:ORG-001846;TREE:ORG-000242")

# ---------------------------------------------------------------- 0010 Berry Global
C("SND-0010", "ORG-002149 'Berry Global - Streetsboro, OH' is status=merged (2026-10-30) and has 0 sites; its notes record consolidation into ORG-002544 with successor_org_id deliberately left empty. All 18 sites in the cluster sit under ORG-002544 (a plant named after its own org is normal). Streetsboro plant SITE-002106 (1275 Ethan Ave): EPA lists BERRY GLOBAL DBA CARDINAL PACKAGING, INC. and CARDINAL PACKAGING INC there, so one establishment.",
  "TREE:ORG-002149;TREE:ORG-002544;FRS:110070566727;FRS:110004698300")
P("SND-0010", "org", "ORG-002149", "ORG-002544", "DUPLICATE_OF", "ORG-002544", "recorded", "",
  "status=merged 2026-10-30; notes: 'duplicate record consolidated into ORG-002544 ... successor_org_id left empty so no generated edge arises'.", "TREE:ORG-002149")

# ---------------------------------------------------------------- 0014 Carlisle Polyurethane Systems
C("SND-0014", "Whether ORG-000262 'Carlisle Polyurethane Systems' (Berea OH; its site prints 140 Sheldon Rd and is (c) Carlisle TyrFil) is a legal entity separate from ORG-002251 Carlisle Construction Materials LLC (Carlisle PA), or a business-unit name under it, is not settled: STILL_UNCERTAIN, no merge. The tree and the EPA registrants support a unit name (ACCELLA POLYURETHANE SYSTEMS, CARLISLE POLYURETHANE SYSTEMS, MARCHEM CORPORATION at four of the plants) but name no filing entity. The TyrFil duplicate ORG-001766 is already merged into ORG-000262. Four plants named 'Carlisle Polyurethane Systems -' sit under ORG-002251; their operator is held on the same fact.",
  "TREE:ORG-000262;TREE:ORG-002251;TREE:ORG-001766;FRS:110000825723;FRS:110025332959;FRS:110000356347;FRS:110070025854;FRS:110018011088;WEB:W10;WEB:W11")
P("SND-0014", "org", "ORG-001766", "ORG-000262", "DUPLICATE_OF", "ORG-000262", "recorded", "",
  "status=merged 2026-10-29 (dedupe pair P2-04; shared site address 140 Sheldon Rd, Berea).", "TREE:ORG-001766")
P("SND-0014", "org", "ORG-000262", "ORG-002251", "STILL_UNCERTAIN", "", "n/a", "",
  "Different names and HQs (Berea OH vs Carlisle PA), but 'Carlisle Polyurethane Systems' is also ORG-000262's whole legal_name and trade name, i.e. a brand/unit name; ORG-000262's own site is (c) Carlisle TyrFil and names no filing entity. Unlike Euclid or Tremco CPG, nothing here shows a distinct legal entity. Settling fact: the legal entity named on the EPA/TRI filings for the Berea plant (SOS record) and whether it is distinct from Carlisle Construction Materials LLC; if CPS is a unit of the LLC, ORG-000262 is a division record (the Ludlow/Crown Foam precedent) and the four plants stay with ORG-002251.",
  "TREE:ORG-000262;TREE:ORG-002251;FRS:110000825723;WEB:W10;WEB:W11")
for s, why in [("SITE-003087", "Rancho Cucamonga CA: EPA registrant ACCELLA POLYURETHANE SYSTEMS LLC (110025332959)"),
               ("SITE-003088", "Cartersville GA: EPA registrant ACCELLA POLYURETHANE SYSTEMS (110000356347)"),
               ("SITE-003091", "Maryland Heights MO: EPA registrant MARCHEM CORPORATION (110018011088)"),
               ("SITE-003095", "Chattanooga TN: EPA registrant CARLISLE POLYURETHANE SYSTEMS (FORMERLY ACELLA POLYURETHANE SYSTEMS) (110070025854), the same text as ORG-000262's legal_name; it is held rather than repointed (unlike Euclid/Tremco) because that text is a unit name, not a shown legal entity (see the org pair)")]:
    A("SND-0014", "hold_operator", s, "ORG-000262|ORG-002251", "hold",
      "Operator unsettled (currently ORG-002251). " + why + ". Settling fact: the legal entity that files the EPA/TRI report for this plant and whether it is ORG-000262's entity or a Carlisle Construction Materials LLC division. The earlier packet already flagged this grain inconsistency (SITE-000279 notes).",
      "TREE:" + s)

# ---------------------------------------------------------------- 0015 Carpenter Co.
C("SND-0015", "ORG-002484 'Carpenter Co. Incorporated' (Lititz PA) is status=merged (2026-10-30) into ORG-002348 'Carpenter Co.' (Richmond VA); the 9 sites in the cluster all sit under the survivor at 9 different addresses (no site duplicate). EPA lists CARPENTER CO INCORPORATED at the Lititz site (400 Arrowhead Dr).",
  "TREE:ORG-002484;TREE:ORG-002348;FRS:110002095768")
P("SND-0015", "org", "ORG-002484", "ORG-002348", "DUPLICATE_OF", "ORG-002348", "recorded", "",
  "status=merged, successor_org_id=ORG-002348; the Lititz plant SITE-002471 is held once under the survivor.", "TREE:ORG-002484;TREE:ORG-002348")

# ---------------------------------------------------------------- 0016 Charter Plastics
C("SND-0016", "ORG-002674 Charter Plastics is status=acquired (2021-12-31) with successor ORG-003282 WL Plastics recorded; the plant SITE-002665 (221 S Perry St, Titusville) is held once, under the successor. EPA lists both CHARTER PLASTICS and WL PLASTICS MFG at that address: one establishment whose operator changed. A predecessor and its acquirer are different legal entities, so there is nothing to merge.",
  "TREE:ORG-002674;TREE:ORG-003282;FRS:110001059121;FRS:110009815539")
P("SND-0016", "org", "ORG-002674", "ORG-003282", "DISTINCT", "", "n/a", "",
  "Acquired-entity tombstone with successor_org_id recorded (acquisition 2021-12-31); different legal entities.", "TREE:ORG-002674;TREE:ORG-003282")

# ---------------------------------------------------------------- 0020 Creative Composites Group
C("SND-0020", "Creative Composites Group's own site lists Composite Advantage as one of the group's seven 'Companies' (with Creative Pultrusions, Enduro Composites, E.T. Techtonics, Kenway Composites, Trident Industries, United Fiberglass): group vs member company, DISTINCT. ORG-001790 carries the group name as a trade name, which is what clustered it. Open: SITE-000831 'Creative Composites Group - Dayton' (hq_only, no street, under the group) is the Dayton operation that ORG-001790's notes call Composite Advantage's.",
  "TREE:ORG-000768;TREE:ORG-001790;TREE:SITE-000831;WEB:W05")
P("SND-0020", "org", "ORG-000768", "ORG-001790", "DISTINCT", "", "n/a", "",
  "Group site presents Composite Advantage as a member company next to six others; ORG-000768's own note says the group site 'lists its divisions with phones, incl. Composite Advantage' (Dayton).", "TREE:ORG-000768;WEB:W05")
A("SND-0020", "hold_operator", "SITE-000831", "ORG-000768|ORG-001790", "hold",
  "Operator is probably ORG-001790 (Composite Advantage), currently ORG-000768 (the group). Settling fact: the Dayton street address and the Ohio SOS entity record showing whether Composite Advantage is a separate legal entity from the group.",
  "TREE:ORG-001790;TREE:SITE-000831;WEB:W05")

# ---------------------------------------------------------------- 0021 Day-Glo
C("SND-0021", "ORG-000005 Day-Glo Color Corp is a recorded subsidiary of RPM (parent_org_id ORG-000006): DISTINCT orgs. The two RPM-owned rows named 'Day-Glo Color Corp' are the same establishments as the operator's own rows (the richer row survives, repointed to the operator): SITE-002964 = SITE-000005 (4515 St Clair Ave, Cleveland; both rows cite EPA FRS 110000386494) and SITE-002968 = SITE-002082 (1570 (E.) Highland Rd, Twinsburg; EPA registrant DAY-GLO COLOR CORP).",
  "TREE:ORG-000005;TREE:SITE-002964;TREE:SITE-000005;TREE:SITE-002968;TREE:SITE-002082;FRS:110000386494;FRS:110000386029")
P("SND-0021", "org", "ORG-000005", "ORG-000006", "DISTINCT", "", "n/a", "",
  "parent_org_id ORG-000006 already recorded on ORG-000005; RPM's own note: classify subsidiaries individually.", "TREE:ORG-000005;TREE:ORG-000006")
P("SND-0021", "site", "SITE-000005", "SITE-002964", "DUPLICATE_OF", "SITE-002964", "to_apply", "shared_frs_id",
  "Same address (4515 St Clair Ave, Cleveland) and the same EPA FRS id 110000386494 in both rows' own sources. SITE-002964 holds more history (6 evidence rows vs 1), so it survives and is repointed to the operator ORG-000005; carry SITE-000005's hq_and_plant type and Form 5500 liveness note into it.",
  "TREE:SITE-002964;TREE:SITE-000005;FRS:110000386494", "ORG-000005")
P("SND-0021", "site", "SITE-002082", "SITE-002968", "DUPLICATE_OF", "SITE-002968", "to_apply", "same_street",
  "Same address, 1570 (E.) Highland Rd, Twinsburg OH 44087; EPA registrant DAY-GLO COLOR CORP; SITE-002082's notes carry the street (street column empty). SITE-002968 holds 6 evidence rows and a registry link (SITE-002082 none), so it survives, repointed to ORG-000005; carry SITE-002082's tier-A own-domain ISO-certificate basis into its notes.",
  "TREE:SITE-002968;TREE:SITE-002082;FRS:110000386029", "ORG-000005")
A("SND-0021", "repoint_site", "SITE-002964", "ORG-000005", "to_apply",
  "Survivor of the St Clair Ave fold; EPA registrant DAY-GLO COLOR CORP (operator), RPM is the brand owner.", "TREE:SITE-002964;FRS:110000386494")
A("SND-0021", "repoint_site", "SITE-002968", "ORG-000005", "to_apply",
  "Survivor of the Highland Rd fold; EPA registrant DAY-GLO COLOR CORP (operator).", "TREE:SITE-002968;FRS:110000386029")

# ---------------------------------------------------------------- 0022 Diamond Plastics
C("SND-0022", "ORG-004865 and ORG-005115 are both 'Diamond Plastics Corporation', both HQ Grand Island NE, same website dpcpipe.com, created the same day by two different waves (NE skimpy-state, IN national-spine pilot). The company's own site names one corporation at 1212 Johnstown Road, Grand Island. ORG-005115 holds only the Muncie plant; fold it into ORG-004865 (which holds the HQ site) and repoint SITE-006423.",
  "TREE:ORG-004865;TREE:ORG-005115;FRS:110001516501;FRS:110031298423;WEB:W12")
P("SND-0022", "org", "ORG-005115", "ORG-004865", "DUPLICATE_OF", "ORG-004865", "to_apply", "same_website",
  "Identical legal_name, hq_city/hq_state and website host (dpcpipe.com); one corporation with plants in Grand Island, Lubbock and Muncie; survivor holds the HQ site SITE-006047.",
  "TREE:ORG-004865;TREE:ORG-005115;WEB:W12")
A("SND-0022", "repoint_site", "SITE-006423", "ORG-004865", "to_apply",
  "Muncie plant belongs to the surviving org once ORG-005115 folds; EPA/OSHA registrant is Diamond Plastics Corporation.", "TREE:SITE-006423;TREE:ORG-005115")

# ---------------------------------------------------------------- 0028 Esstech
C("SND-0028", "ORG-002323 'Esstech - Division Of Esschem Co.' is status=merged (2026-11-04) into ORG-002324 Esstech, Inc. Residual: SITE-002301 ('...Division Of Esschem') and SITE-002302 ('Esstech, Inc.') are both under ORG-002324 at 48 Powhatten / Powhattan Ave, Essington PA 19029 (a one-vowel typo); EPA lists ESSTECH ESSINGTON FAC at 48 POWHATTAN AVE. One establishment held twice.",
  "TREE:ORG-002323;TREE:ORG-002324;TREE:SITE-002301;TREE:SITE-002302;FRS:110000841331")
P("SND-0028", "org", "ORG-002323", "ORG-002324", "DUPLICATE_OF", "ORG-002324", "recorded", "",
  "status=merged, successor_org_id=ORG-002324 (2026-11-04).", "TREE:ORG-002323")
P("SND-0028", "site", "SITE-002301", "SITE-002302", "DUPLICATE_OF", "SITE-002302", "to_apply", "street_variant",
  "48 Powhatten Ave. vs 48 Powhattan Ave., same city/ZIP, same org; the EPA row spells it Powhattan, so SITE-002302 (tier A) survives and SITE-002301 folds, carrying its OSHA ITA and monomers-page sources. EPA also lists 'ESSTECH SITE B' at 48 W POWHATTAN AVE: not examined here.",
  "TREE:SITE-002301;TREE:SITE-002302;FRS:110000841331", "ORG-002324")

# ---------------------------------------------------------------- 0029 Euclid Chemical
C("SND-0029", "The Euclid Chemical Company (ORG-001807) and RPM International (ORG-000006) are different legal entities (RPM is the ultimate parent): DISTINCT. SITE-000168 'Euclid Chemical - Cleveland' (19218 Redwood Rd, hq_and_plant) sits under RPM, but the EPA registrant at that address is EUCLID CHEMICAL CO and ORG-001807 holds no site: the operator is ORG-001807.",
  "TREE:ORG-001807;TREE:ORG-000006;TREE:SITE-000168;FRS:110000386920")
P("SND-0029", "org", "ORG-000006", "ORG-001807", "DISTINCT", "", "n/a", "",
  "Parent vs subsidiary; ORG-000006 notes: 'Classify subsidiaries individually'. Different legal names and HQs (Medina vs Cleveland).", "TREE:ORG-000006;TREE:ORG-001807")
A("SND-0029", "repoint_site", "SITE-000168", "ORG-001807", "to_apply",
  "EPA registrant at 19218 Redwood Rd, Cleveland is EUCLID CHEMICAL CO (operator), not RPM (brand owner).", "TREE:SITE-000168;FRS:110000386920")

# ---------------------------------------------------------------- 0030 Valtris / Ferro Polymer Additives
C("SND-0030", "ORG-000338 (Valtris Specialty Chemicals, trade name 'Ferro CORP Polymer Additives Div', HQ Cleveland) is status=merged (2026-10-29) into ORG-000135 Valtris Specialty Chemicals (Independence OH); the cluster's site SITE-000359 'Ferro CORP Polymer Additives Div - Cleveland' already sits under the survivor.",
  "TREE:ORG-000338;TREE:ORG-000135;TREE:SITE-000359")
P("SND-0030", "org", "ORG-000338", "ORG-000135", "DUPLICATE_OF", "ORG-000135", "recorded", "",
  "status=merged, successor_org_id=ORG-000135; identical legal_name 'Valtris Specialty Chemicals' and website valtris.com.", "TREE:ORG-000338;TREE:ORG-000135")

# ---------------------------------------------------------------- 0037 Goodyear Chemical
C("SND-0037", "Goodyear Tire & Rubber (ORG-000003) and Goodyear Chemical (ORG-003746) are different entities since Goodyear sold the Houston and Beaumont polymer-chemical plants and the Akron R&D facility to a Gemspring affiliate effective 2025-10-31 (Goodyear kept Niagara Falls NY and Bayport TX): DISTINCT. Houston and Beaumont are each held twice: the street-bearing rows SITE-002868 / SITE-002870 under Goodyear Tire (they survive, repointed to Goodyear Chemical) and the sale-release rows SITE-004181 / SITE-004182 under Goodyear Chemical (they fold). Niagara Falls (SITE-002867) correctly stays with Goodyear Tire.",
  "TREE:ORG-000003;TREE:ORG-003746;TREE:SITE-002868;TREE:SITE-002870;TREE:SITE-004181;TREE:SITE-004182;TREE:SITE-002867;WEB:W01;WEB:W02;FRS:110049721627;FRS:110000462231;FRS:110061782566;FRS:110000389491")
P("SND-0037", "org", "ORG-000003", "ORG-003746", "DISTINCT", "", "n/a", "",
  "Divestiture closed effective 2025-10-31: a Gemspring affiliate owns Goodyear Chemical; Goodyear Tire is the former parent (ORG-003746 ultimate_parent_name = Gemspring Capital Management).", "TREE:ORG-003746;WEB:W01;WEB:W02")
P("SND-0037", "site", "SITE-004181", "SITE-002868", "DUPLICATE_OF", "SITE-002868", "to_apply", "same_city_streetless",
  "The sale covered exactly two manufacturing plants, one in Houston and one in Beaumont, so Goodyear's one Houston chemical plant (EPA: HOUSTON CHEMICAL PLANT, 2000 Goodyear Dr) is the sale-release row's plant. SITE-002868 holds 9 evidence rows and a registry link (the sale-release row none), so it survives and is repointed to ORG-003746; its notes already record the 2025-10-31 operator change.",
  "TREE:SITE-002868;TREE:SITE-004181;WEB:W02;FRS:110049721627;FRS:110000462231", "ORG-003746")
P("SND-0037", "site", "SITE-004182", "SITE-002870", "DUPLICATE_OF", "SITE-002870", "to_apply", "same_city_streetless",
  "Same reasoning for Beaumont (one plant named in the sale; SITE-002870 is 11241 Interstate Hwy 10, holds 8 evidence rows vs 0, and its own notes say it was sold to a Gemspring affiliate effective 2025-10-31). It survives, repointed to ORG-003746.",
  "TREE:SITE-002870;TREE:SITE-004182;WEB:W02", "ORG-003746")
P("SND-0037", "site", "SITE-002867", "SITE-004181", "DISTINCT", "", "n/a", "",
  "Niagara Falls NY is not in the sale ('Goodyear will retain its chemical facilities in Niagara Falls ... and Bayport'); EPA registrant there is GOODYEAR TIRE & RUBBER CO. Not a duplicate of any ORG-003746 row.",
  "TREE:SITE-002867;WEB:W02;FRS:110061782566")

A("SND-0037", "repoint_site", "SITE-002868", "ORG-003746", "to_apply",
  "Survivor of the Houston fold; the plant belongs to Goodyear Chemical (Gemspring affiliate) since 2025-10-31.", "TREE:SITE-002868;WEB:W01;WEB:W02")
A("SND-0037", "repoint_site", "SITE-002870", "ORG-003746", "to_apply",
  "Survivor of the Beaumont fold; same sale.", "TREE:SITE-002870;WEB:W02")

# ---------------------------------------------------------------- 0038 Harrison Paint
C("SND-0038", "ORG-001837 'Harrison Paint Corp.' is status=merged (2026-10-29) into ORG-001678 'Harrison Paint Company' (same Canton OH HQ); the cluster's site SITE-001754 already sits under the survivor.",
  "TREE:ORG-001837;TREE:ORG-001678")
P("SND-0038", "org", "ORG-001837", "ORG-001678", "DUPLICATE_OF", "ORG-001678", "recorded", "",
  "status=merged, successor_org_id=ORG-001678.", "TREE:ORG-001837")

# ---------------------------------------------------------------- 0039 HEXPOL
C("SND-0039", "ORG-002044 'HEXPOL Compounding LLC (HEXPOL Akron / HEXPOL Silicone Compounding)' is status=merged (2026-10-29) into ORG-000103 HEXPOL Compounding; the cluster's site SITE-002038 (named with the long form) already sits under the survivor.",
  "TREE:ORG-002044;TREE:ORG-000103")
P("SND-0039", "org", "ORG-002044", "ORG-000103", "DUPLICATE_OF", "ORG-000103", "recorded", "",
  "status=merged, successor_org_id=ORG-000103.", "TREE:ORG-002044")

# ---------------------------------------------------------------- 0040 House of Plastics
C("SND-0040", "ORG-000109 House of Plastics is status=acquired with successor ORG-000108 HP Manufacturing and its notes say 'RETIRED ... duplicate record - House of Plastics is a division of HP Manufacturing'; SITE-000108 was repointed to the survivor.",
  "TREE:ORG-000109;TREE:ORG-000108;TREE:SITE-000108")
P("SND-0040", "org", "ORG-000109", "ORG-000108", "DUPLICATE_OF", "ORG-000108", "recorded", "",
  "successor_org_id=ORG-000108; notes record the division-of-operator dedupe verdict (pass 6).", "TREE:ORG-000109")

# ---------------------------------------------------------------- 0043 IER Fujikura
C("SND-0043", "ORG-000173 'IER Fujikura Inc.' is status=merged (2026-10-29) into ORG-000373 'IER Fujikura' (same Macedonia OH HQ and website); its site SITE-000180 is already tombstoned as a duplicate of SITE-000398 under the survivor.",
  "TREE:ORG-000173;TREE:ORG-000373;TREE:SITE-000180;TREE:SITE-000398")
P("SND-0043", "org", "ORG-000173", "ORG-000373", "DUPLICATE_OF", "ORG-000373", "recorded", "",
  "status=merged, successor_org_id=ORG-000373.", "TREE:ORG-000173")
P("SND-0043", "site", "SITE-000180", "SITE-000398", "DUPLICATE_OF", "SITE-000398", "recorded", "",
  "SITE-000180 notes: 'tombstoned as duplicate of SITE-000398 (dedupe pair P1-60)'.", "TREE:SITE-000180")

# ---------------------------------------------------------------- 0048 Johnsonite
C("SND-0048", "ORG-001836 Johnsonite Inc. is status=acquired (2005-12-08) with successor ORG-000131 Tarkett North America recorded: predecessor vs acquirer, DISTINCT. Residuals: SITE-000427 and SITE-003478 are the same Chagrin Falls plant (16910 Munn Rd; EPA registrant JOHNSONITE; SITE-003478 survives), and the active rows SITE-003477 / SITE-003478 sit under the acquired org although their notes name the operator 'Tarkett USA Inc. dba Johnsonite'.",
  "TREE:ORG-001836;TREE:ORG-000131;TREE:SITE-000427;TREE:SITE-003478;TREE:SITE-003477;FRS:110000385244;FRS:110009662855")
P("SND-0048", "org", "ORG-001836", "ORG-000131", "DISTINCT", "", "n/a", "",
  "Acquired-entity tombstone with successor recorded (2005-12-08).", "TREE:ORG-001836;TREE:ORG-000131")
P("SND-0048", "site", "SITE-000427", "SITE-003478", "DUPLICATE_OF", "SITE-003478", "to_apply", "same_street",
  "Both rows are 16910 Munn Rd, Chagrin Falls (SITE-000427's notes: 'Street (per Grok): 16910 Munn Rd'; pass-4 note 'Johnsonite/Tarkett 16910 Munn Rd ... verified active'); EPA registrant JOHNSONITE. SITE-003478 holds more evidence (2 rows vs 1) and survives, repointed from the acquired ORG-001836 to ORG-000131.",
  "TREE:SITE-003478;TREE:SITE-000427;FRS:110000385244", "ORG-000131")
A("SND-0048", "repoint_site", "SITE-003478", "ORG-000131", "to_apply",
  "Survivor of the Munn Rd fold; its notes name the operator Tarkett USA Inc. dba Johnsonite and its current parent ORG-001836 is the acquired (2005) entity.", "TREE:SITE-003478;TREE:ORG-001836;FRS:110000385244")
A("SND-0048", "repoint_site", "SITE-003477", "ORG-000131", "to_apply",
  "Middlefield plant: notes name the operator Tarkett USA Inc. dba Johnsonite and EPA registrant is TARKETT USA INC.; the current parent ORG-001836 is the acquired (2005) entity whose successor is ORG-000131.", "TREE:SITE-003477;TREE:ORG-001836;FRS:110009662855")

# ---------------------------------------------------------------- 0049 Jushi USA
C("SND-0049", "ORG-003321 'Jushi USA' and ORG-003755 'Jushi USA Fiberglass Co., Ltd.' were created in the same pass by two lanes, same Columbia SC HQ. The EPA registrant at the plant (2971 Shop Rd, two FRS ids) is a third name, CHINA JUSHI USA CORPORATION, so which legal entity operates the plant is not settled: STILL_UNCERTAIN for the orgs. The two plant rows are the same establishment (one Jushi plant at Pineview Industrial Park; EPA has a single address): fold SITE-004191 into SITE-003765; the operator question rides on the survivor.",
  "TREE:ORG-003321;TREE:ORG-003755;TREE:SITE-003765;TREE:SITE-004191;FRS:110071154405;FRS:110070684578")
P("SND-0049", "org", "ORG-003755", "ORG-003321", "STILL_UNCERTAIN", "", "n/a", "",
  "Three names for one plant (Jushi USA / Jushi USA Fiberglass Co., Ltd. / China Jushi USA Corporation). Settling fact: the SC Secretary of State (or SCDES permit) record naming the entity that owns and operates the Columbia plant.",
  "TREE:ORG-003321;TREE:ORG-003755;FRS:110071154405;FRS:110070684578")
P("SND-0049", "site", "SITE-004191", "SITE-003765", "DUPLICATE_OF", "SITE-003765", "to_apply", "same_city_streetless",
  "Both rows are the Columbia SC plant ('Columbia plant' vs 'Columbia Plant & HQ'); EPA lists the plant only at 2971 Shop Rd (SITE-003765's street) under CHINA JUSHI USA CORPORATION; SITE-004191 has no street and its notes say the street was 'not reliably established'.",
  "TREE:SITE-004191;TREE:SITE-003765;FRS:110071154405")

A("SND-0049", "hold_operator", "SITE-003765", "ORG-003321|ORG-003755", "hold",
  "The surviving plant row sits under ORG-003321 only because the folded row's org (ORG-003755) is unsettled, not because ORG-003321 is shown to be the operator. Settling fact: the SC Secretary of State or SCDES record naming the entity that owns and operates the Columbia plant (EPA registrant: CHINA JUSHI USA CORPORATION).",
  "TREE:SITE-003765;TREE:SITE-004191;FRS:110071154405")

# ---------------------------------------------------------------- 0050 Key Resin
C("SND-0050", "Key Resin Company (ORG-000919) and RPM (ORG-000006) are different legal entities: DISTINCT. The Batavia OH plant is held twice: SITE-000989 (under Key Resin, street only in notes) and SITE-002962 (under RPM, 4050 Clough Woods Dr). EPA registrant at that address is KEY RESIN COMPANY, so Key Resin is the operator; SITE-002962 holds the history and survives, repointed to Key Resin, and SITE-000989 folds.",
  "TREE:ORG-000919;TREE:ORG-000006;TREE:SITE-000989;TREE:SITE-002962;FRS:110070207889")
P("SND-0050", "org", "ORG-000006", "ORG-000919", "DISTINCT", "", "n/a", "",
  "Different legal names and HQs (Medina vs Batavia); no parent link recorded on ORG-000919 (a link_parent is an owner matter, not done here).", "TREE:ORG-000006;TREE:ORG-000919")
P("SND-0050", "site", "SITE-000989", "SITE-002962", "DUPLICATE_OF", "SITE-002962", "to_apply", "same_street",
  "SITE-000989 notes: 'Street (per Grok): 4050 Clough Woods Drive'; SITE-002962 street 4050 Clough Woods Dr, Batavia; EPA FRS 110070207889 KEY RESIN COMPANY at that address. SITE-002962 holds 7 evidence rows (SITE-000989 none), so it survives and is repointed from RPM to ORG-000919.",
  "TREE:SITE-002962;TREE:SITE-000989;FRS:110070207889", "ORG-000919")
A("SND-0050", "repoint_site", "SITE-002962", "ORG-000919", "to_apply",
  "Survivor of the Batavia fold; EPA registrant KEY RESIN COMPANY (operator), RPM is the brand owner.", "TREE:SITE-002962;FRS:110070207889")

# ---------------------------------------------------------------- 0051 LANXESS
C("SND-0051", "ORG-000547 'LANXESS Rhein Chemie' already has parent_org_id ORG-003919 'LANXESS Corporation': DISTINCT (subsidiary of a recorded parent). The Pittsburgh office is held twice: SITE-002777 (111 Park West Dr., under Rhein Chemie) and SITE-004377 (111 RIDC Park West Drive, under LANXESS Corporation); RIDC is the park's name, and EPA lists LANXESS CORPORATION at 111 PARK WEST DRIVE, so the operator is ORG-003919.",
  "TREE:ORG-000547;TREE:ORG-003919;TREE:SITE-002777;TREE:SITE-004377;FRS:110044232238;FRS:110023859083")
P("SND-0051", "org", "ORG-000547", "ORG-003919", "DISTINCT", "", "n/a", "",
  "parent_org_id ORG-003919 already recorded on ORG-000547.", "TREE:ORG-000547")
P("SND-0051", "site", "SITE-002777", "SITE-004377", "DUPLICATE_OF", "SITE-004377", "to_apply", "street_variant",
  "111 Park West Dr. vs 111 RIDC Park West Drive, Pittsburgh PA; EPA registrant LANXESS CORPORATION at 111 PARK WEST DRIVE (two FRS ids). Survivor under the registrant org.",
  "TREE:SITE-002777;TREE:SITE-004377;FRS:110044232238;FRS:110023859083", "ORG-003919")

# ---------------------------------------------------------------- 0055 Ludlow / Crown Foam
C("SND-0055", "Crown Foam Technologies is a brand division of Ludlow Composites, not a separate company: Ludlow's own history page says the foam and matting divisions were rebranded Crown Foam / Crown Matting 'and began operating the Ludlow name as the parent company', still at 2100 Commerce Drive, Fremont. ORG-001792 (trade name 'Ludlow Composites Corp') folds into ORG-000937, and its site SITE-001866 (2100 Commerce Dr) into SITE-001008 (2100 Commerce Drive; EPA LUDLOW COMPOSITES CORP).",
  "TREE:ORG-000937;TREE:ORG-001792;TREE:SITE-001008;TREE:SITE-001866;FRS:110000383219;WEB:W03;WEB:W04")
P("SND-0055", "org", "ORG-001792", "ORG-000937", "DUPLICATE_OF", "ORG-000937", "to_apply", "division_of_survivor_site",
  "ORG-001792's own notes: 'Foam division of Ludlow Composites Corp'; same Fremont OH HQ; the division's one site is at the parent's address (see site pair). Same precedent as House of Plastics -> HP Manufacturing (ORG-000109 -> ORG-000108). Carry the division name 'Crown Foam Technologies' to ORG-000937 trade_names.",
  "TREE:ORG-001792;TREE:ORG-000937;WEB:W03;WEB:W04")
P("SND-0055", "site", "SITE-001866", "SITE-001008", "DUPLICATE_OF", "SITE-001008", "to_apply", "same_street",
  "2100 Commerce Dr(ive), Fremont OH 43420 in both rows' notes; Ludlow's page states the single facility is at 2100 Commerce Drive. EPA also lists LUDLOW COMPOSITES CORPORATION at 2260 Cedar St, Fremont: a separate address, not examined.",
  "TREE:SITE-001866;TREE:SITE-001008;FRS:110000383219;WEB:W04", "ORG-000937")

# ---------------------------------------------------------------- 0061 Murdock Industrial
C("SND-0061", "ORG-000168 Murdock Industrial Inc. (status=acquired, successor ORG-000028 'The M. F. Murdock Co' / Murdock Industrial Inc.) was merged in pass 4 as the same single Akron operation (one footer address on murdockindustrial.com); its site SITE-000175 is tombstoned as the same establishment as SITE-000027.",
  "TREE:ORG-000168;TREE:ORG-000028;TREE:SITE-000175;TREE:SITE-000027")
P("SND-0061", "org", "ORG-000168", "ORG-000028", "DUPLICATE_OF", "ORG-000028", "recorded", "",
  "successor_org_id=ORG-000028; notes: 'same single Akron establishment/operation'.", "TREE:ORG-000168")
P("SND-0061", "site", "SITE-000175", "SITE-000027", "DUPLICATE_OF", "SITE-000027", "recorded", "",
  "SITE-000175 notes: 'RETIRED ... same single Akron establishment as SITE-000027'.", "TREE:SITE-000175")

# ---------------------------------------------------------------- 0064 Newko
C("SND-0064", "ORG-000141 Newko Polymers is status=merged (2026-10-29) into ORG-000460 Newko Polymers (same Strongsville OH HQ and website); its site SITE-000141 is tombstoned as a duplicate of SITE-000492.",
  "TREE:ORG-000141;TREE:ORG-000460;TREE:SITE-000141;TREE:SITE-000492")
P("SND-0064", "org", "ORG-000141", "ORG-000460", "DUPLICATE_OF", "ORG-000460", "recorded", "",
  "status=merged, successor_org_id=ORG-000460; identical legal_name.", "TREE:ORG-000141")
P("SND-0064", "site", "SITE-000141", "SITE-000492", "DUPLICATE_OF", "SITE-000492", "recorded", "",
  "SITE-000141 notes: 'tombstoned as duplicate of SITE-000492 (dedupe pair P1-53)'.", "TREE:SITE-000141")

# ---------------------------------------------------------------- 0065 NFM
C("SND-0065", "ORG-000463 'NFM Welding Engineers, Inc.' is status=merged (2026-10-29) into ORG-000456 'NFM / Welding Engineers, Inc.' (Massillon OH); its site SITE-000495 is tombstoned as a duplicate of SITE-000488.",
  "TREE:ORG-000463;TREE:ORG-000456;TREE:SITE-000495;TREE:SITE-000488")
P("SND-0065", "org", "ORG-000463", "ORG-000456", "DUPLICATE_OF", "ORG-000456", "recorded", "",
  "status=merged, successor_org_id=ORG-000456.", "TREE:ORG-000463")
P("SND-0065", "site", "SITE-000495", "SITE-000488", "DUPLICATE_OF", "SITE-000488", "recorded", "",
  "SITE-000495 notes: 'tombstoned as duplicate of SITE-000488 (dedupe pair P2-19)'.", "TREE:SITE-000495")

# ---------------------------------------------------------------- 0069 Performance Elastomers
C("SND-0069", "ORG-000484 Performance Elastomers is status=acquired (2021-12-01) with successor ORG-002534 Pexco LLC recorded; SITE-000518 (Ravenna) was already repointed to the successor on 2026-11-06 ('OPERATOR REVIEW'). Predecessor vs acquirer: DISTINCT, nothing to merge.",
  "TREE:ORG-000484;TREE:ORG-002534;TREE:SITE-000518")
P("SND-0069", "org", "ORG-000484", "ORG-002534", "DISTINCT", "", "n/a", "",
  "Acquired-entity tombstone with successor_org_id recorded; different HQs (Ravenna OH vs Alpharetta GA).", "TREE:ORG-000484;TREE:ORG-002534")

# ---------------------------------------------------------------- 0072 Pilot Plastics
C("SND-0072", "ORG-000492 Pilot Plastics, Inc. is status=acquired (2023-02-02) with successor ORG-004564 Preformed Line Products Company recorded; SITE-000527 (Peninsula) was already repointed to the successor on 2026-11-06. Predecessor vs acquirer: DISTINCT.",
  "TREE:ORG-000492;TREE:ORG-004564;TREE:SITE-000527")
P("SND-0072", "org", "ORG-000492", "ORG-004564", "DISTINCT", "", "n/a", "",
  "Acquired-entity tombstone with successor_org_id recorded; different legal entities and HQs (Peninsula vs Mayfield Village OH).", "TREE:ORG-000492;TREE:ORG-004564")

# ---------------------------------------------------------------- 0074 Polymer & Steel Technologies
C("SND-0074", "ORG-001762 'Polymer & Steel Technologies, Inc.' is status=merged (2026-10-29) into ORG-001806 ENPRESS LLC (trade name 'Polymer & Steel Technologies, Inc.'): the Form 5500 filer at 34899 Curtis Blvd, Eastlake. Its site SITE-001845 is retired as the duplicate of SITE-001873 (same address).",
  "TREE:ORG-001762;TREE:ORG-001806;TREE:SITE-001845;TREE:SITE-001873")
P("SND-0074", "org", "ORG-001762", "ORG-001806", "DUPLICATE_OF", "ORG-001806", "recorded", "",
  "status=merged, successor_org_id=ORG-001806; same Eastlake OH situs.", "TREE:ORG-001762")
P("SND-0074", "site", "SITE-001845", "SITE-001873", "DUPLICATE_OF", "SITE-001873", "recorded", "",
  "SITE-001845 notes: 'Retired in integration pass 9 as the duplicate of SITE-001873 (same establishment, 34899 Curtis Blvd, Eastlake)'.", "TREE:SITE-001845")

# ---------------------------------------------------------------- 0077 Premere
C("SND-0077", "ORG-001871 'Premere Enterprises Inc.' is status=merged (2026-10-29) into ORG-000902 'Premere Enterprises, Inc.' (Bolivar OH); the cluster's site SITE-000971 (10882 Fort Laurens Rd NW; EPA PREMERE ENTERPRISES INC) already sits under the survivor.",
  "TREE:ORG-001871;TREE:ORG-000902;FRS:110004617781")
P("SND-0077", "org", "ORG-001871", "ORG-000902", "DUPLICATE_OF", "ORG-000902", "recorded", "",
  "status=merged, successor_org_id=ORG-000902.", "TREE:ORG-001871")

# ---------------------------------------------------------------- 0082 Quikey
C("SND-0082", "ORG-002058 Quikey Manufacturing Co, Inc. is status=merged (2026-10-29) into ORG-001997 (same legal name, Akron OH); its site SITE-002057 (status closed) was folded into SITE-001991 in pass 10.",
  "TREE:ORG-002058;TREE:ORG-001997;TREE:SITE-002057;TREE:SITE-001991")
P("SND-0082", "org", "ORG-002058", "ORG-001997", "DUPLICATE_OF", "ORG-001997", "recorded", "",
  "status=merged, successor_org_id=ORG-001997.", "TREE:ORG-002058")
P("SND-0082", "site", "SITE-002057", "SITE-001991", "DUPLICATE_OF", "SITE-001991", "recorded", "",
  "SITE-001991 notes: 'pass-10 duplicate SITE-002057 ... folded into this site'.", "TREE:SITE-001991")

# ---------------------------------------------------------------- 0083 Republic Powdered Metals
C("SND-0083", "Republic Powdered Metals Inc (ORG-001724, ultimate_parent_name RPM International) and RPM (ORG-000006) are different legal entities: DISTINCT. The Medina plant is held twice: SITE-001800 (under Republic) and SITE-002965 (under RPM, 2628 Pearl Rd); EPA registrant is REPUBLIC POWDERED METALS INC, so Republic is the operator (SITE-002965 holds the history and survives, repointed to Republic). 2628 Pearl Rd is also RPM's headquarters street, so the fold rests on the registrant name and SITE-001800's own TRI-based note, not on the street alone.",
  "TREE:ORG-001724;TREE:ORG-000006;TREE:SITE-001800;TREE:SITE-002965;FRS:110000388937")
P("SND-0083", "org", "ORG-000006", "ORG-001724", "DISTINCT", "", "n/a", "",
  "Parent vs subsidiary (ORG-001724 ultimate_parent_name = RPM International Inc); different legal names.", "TREE:ORG-000006;TREE:ORG-001724")
P("SND-0083", "site", "SITE-001800", "SITE-002965", "DUPLICATE_OF", "SITE-002965", "to_apply", "same_street",
  "Both rows are 2628 Pearl Rd, Medina OH 44256 (SITE-001800 notes: 'Street: 2628 Pearl Rd.'). SITE-001800's notes cite EPA TRI records for REPUBLIC POWDERED METALS INC at that address; SITE-002965 cites FRS 110000388937 (same registrant name). SITE-002965 holds 7 evidence rows (SITE-001800 none), so it survives and is repointed from RPM to ORG-001724.",
  "TREE:SITE-002965;TREE:SITE-001800;FRS:110000388937", "ORG-001724")
A("SND-0083", "repoint_site", "SITE-002965", "ORG-001724", "to_apply",
  "Survivor of the Pearl Rd fold; EPA registrant REPUBLIC POWDERED METALS INC (operator), RPM is the brand owner.", "TREE:SITE-002965;FRS:110000388937")

# ---------------------------------------------------------------- 0084 Royal Building Products
C("SND-0084", "Two Columbus OH establishments on Universal Rd, not one: ORG-000764's EPA registrant is CRANE PERFORMANCE SIDING L L C NORTH at 1550 Universal Rd; ORG-001091's is ROYAL BUILDING PRODUCTS INC at 1441 Universal Rd (SITE-001182). Different street, different registrant legal entity; both orgs' notes carry a 2026-10-28 dedupe-audit verdict 'sibling link ... do not merge'. DISTINCT.",
  "TREE:ORG-000764;TREE:ORG-001091;TREE:SITE-001182;TREE:SITE-000827;FRS:110004735109;FRS:110000823431")
P("SND-0084", "org", "ORG-000764", "ORG-001091", "DISTINCT", "", "n/a", "",
  "Not the Diamond/Farathane pattern: those org rows share one operator name, HQ address and site. Here the two rows share only the brand name 'Royal Building Products' and the Westlake Royal website; their establishments are at different addresses (1550 vs 1441 Universal Rd) under different EPA registrant legal entities (CRANE PERFORMANCE SIDING L L C NORTH, FRS 110004735109; ROYAL BUILDING PRODUCTS INC, FRS 110000823431), and the 2026-10-28 dedupe audit ruled 'sibling link ... do not merge'. ORG-000764's legal_name is a brand name, not its operator's (the registrant is Crane Performance Siding LLC North): surfaced, not changed.",
  "TREE:ORG-000764;TREE:ORG-001091;FRS:110004735109;FRS:110000823431")

# ---------------------------------------------------------------- 0099 Tremco CPG
C("SND-0099", "Tremco CPG Inc. (ORG-001908, Beachwood OH) and RPM (ORG-000006) are different legal entities: DISTINCT. Four plants named 'Tremco CPG -' sit under RPM and ORG-001908 holds none. Only SITE-001530 (4475 E 175th St) has a registrant that names the operator (TREMCO CPG INC); the others are held for the operator's legal entity ('TREMCO INC' at Ashland predates the CPG name).",
  "TREE:ORG-001908;TREE:ORG-000006;TREE:SITE-000167;TREE:SITE-001514;TREE:SITE-001529;TREE:SITE-001530;FRS:110000387554;FRS:110000391371")
P("SND-0099", "org", "ORG-000006", "ORG-001908", "DISTINCT", "", "n/a", "",
  "Parent vs subsidiary-brand with its own legal name and Beachwood HQ; RPM's note: classify subsidiaries individually.", "TREE:ORG-000006;TREE:ORG-001908")
A("SND-0099", "repoint_site", "SITE-001530", "ORG-001908", "to_apply",
  "EPA registrant at 4475 E 175th St, Cleveland is TREMCO CPG INC (operator).", "TREE:SITE-001530;FRS:110000387554")
for s, why in [("SITE-000167", "Beachwood hq_only row, no street; ORG-001908 is Beachwood-headquartered but no registrant witness"),
               ("SITE-001514", "Ashland OH: EPA registrant is TREMCO INC ASHLAND OH (110000391371), a different name from Tremco CPG Inc."),
               ("SITE-001529", "Cleveland (Miles Ave): no registrant seen")]:
    A("SND-0099", "hold_operator", s, "ORG-000006|ORG-001908", "hold",
      "Operator unsettled (currently ORG-000006). " + why + ". Settling fact: the legal entity that files the EPA/TRI report for this address.",
      "TREE:" + s + (";FRS:110000391371" if s == "SITE-001514" else ""))

# ---------------------------------------------------------------- 0100 Ultra Poly
C("SND-0100", "ORG-002218 'Ultra-Poly Corporation' (Berwick PA) is status=merged (2026-10-30) into ORG-002619 (Ultra-Poly Corporation, Portland PA); the Berwick plant SITE-002182 sits under the survivor, which fits the company's own page (HQ at 102 Demi Rd, Portland; a Berwick compounding plant; 5 production facilities). ORG-004942 'Ultra Poly Inc.' (Tacoma WA) is DISTINCT: every EPA registrant for the PA/NJ Ultra-Poly plants is 'ULTRA POLY CORP/CORPORATION', Tacoma's is 'ULTRA POLY INC' 2,400 miles away, and the company's own page names no Washington plant.",
  "TREE:ORG-002218;TREE:ORG-002619;TREE:ORG-004942;FRS:110070273580;FRS:110057329485;FRS:110001219556;FRS:110031820126;FRS:110015537007;WEB:W06;WEB:W07")
P("SND-0100", "org", "ORG-002218", "ORG-002619", "DUPLICATE_OF", "ORG-002619", "recorded", "",
  "status=merged, successor_org_id=ORG-002619.", "TREE:ORG-002218")
P("SND-0100", "org", "ORG-004942", "ORG-002619", "DISTINCT", "", "n/a", "",
  "Different legal-form suffix (Inc. vs Corporation), different state, EPA registrant ULTRA POLY INC at 2926 S Steele St Tacoma vs ULTRA POLY CORP/ULTRA-POLY CORPORATION at Portland, Bloomsburg and Hackettstown; the Corporation's page lists Portland HQ, Berwick and three embedded tolling plants at customers, none in Washington. Not proof of absence of a link: if a link is later found, treat it as a new lead.",
  "TREE:ORG-004942;FRS:110015537007;FRS:110070273580;FRS:110001219556;FRS:110031820126;WEB:W06;WEB:W07")

# ---------------------------------------------------------------- 0101 US Farathane
C("SND-0101", "ORG-007002 'US Farathane Corporation' and ORG-007061 'US Farathane LLC' are one company: same HQ (2700 High Meadow Cir, Auburn Hills), same website usfarathane.com whose footer reads 'US Farathane Corporation', and the EPA registrant at ORG-007061's own Lake Orion plant (4872 S Lapeer Rd) is U S FARATHANE CORPORATION; the LLC form comes only from OSHA inspection names, which also appear on ORG-007002's own sources. Fold ORG-007061 into ORG-007002 (holds the HQ site) and add 'US Farathane LLC' as a federal-registrant trade name (B-ALIAS). Residual: the Michigan LARA record would show whether the LLC is a conversion (then the survivor's legal_name becomes the LLC: survivor ID is not survivor name) or a separate entity (then reverse the fold).",
  "TREE:ORG-007002;TREE:ORG-007061;TREE:SITE-010064;FRS:110043412278;FRS:110017617373;FRS:110067597960;WEB:W08;WEB:W09")
P("SND-0101", "org", "ORG-007061", "ORG-007002", "DUPLICATE_OF", "ORG-007002", "to_apply", "same_website",
  "Same website host, same HQ address; EPA names Corporation at both HQ (110043412278) and Lake Orion (110017617373); OSHA inspection names say 'US FARATHANE, LLC' for both orgs' establishments (ORG-007002's own sources cite 349016683).",
  "TREE:ORG-007002;TREE:ORG-007061;FRS:110043412278;FRS:110017617373;WEB:W08;WEB:W09")
A("SND-0101", "repoint_site", "SITE-010064", "ORG-007002", "to_apply",
  "Lake Orion plant moves with the fold (ORG-007061 -> ORG-007002).", "TREE:SITE-010064;WEB:W09")
