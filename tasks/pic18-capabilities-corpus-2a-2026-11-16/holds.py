"""Hold reasons per slice site (site number -> (reason class, settling fact)). Sites with applied terms are not listed unless a term is held."""
DIST = ('distributor_or_dealer', 'A page stating that this establishment itself processes or manufactures a governed material or process (stored pages describe resale or distribution)')
EQUIP = ('equipment_or_supply_firm', 'A page stating that this establishment runs a governed polymer process or material in its own plant (stored pages describe machinery, components or supplies)')
TEST = ('testing_or_lab', 'A page stating that this establishment processes a governed polymer material (stored pages describe testing services)')
NOTFOUND = ('nothing_found', 'An own-page narrative sentence or capability list naming a governed process or material for this establishment; none is on the stored pages')
HOLDS = {}
for n in (27, 48, 52, 145, 176, 192, 223, 292, 304, 371, 500, 514, 555, 577, 626): HOLDS[n] = DIST
for n in (56, 58, 142, 267, 268, 351, 360, 401, 406, 435, 441, 488, 544, 679, 685, 1025): HOLDS[n] = EQUIP
for n in (47, 150, 567): HOLDS[n] = TEST
for n in (363, 43, 75, 152, 153, 154, 156, 157, 286, 308, 312, 331, 338, 387, 450, 455, 465, 523, 534, 539, 936, 1078, 1436, 1440, 1449, 1468, 445, 403, 898):
    HOLDS[n] = NOTFOUND
HOLDS.update({
    14: ('off_vocabulary', 'Owner vocabulary ruling on whether extrusion-die and custom-tooling manufacture ("forming dies, sheet dies, film dies and other custom tooling") maps to mold_tool_making; no governed term fits the page words today'),
    59: ('multi_location_unbound', 'A page tying the fabrication list (thermoforming, plastic welding, CNC machining) to the Stow site rather than the national company (a Texas address is on the same pages)'),
    148: ('locality_not_witnessed', 'A page naming the location of the "ISO 9001:2015 certified compounding facility"; stored pages show no Strongsville address and say stock is held in four states'),
    229: ('plant_elsewhere', 'Page labels the Mantua address 4466 Orchard St as "Fabrication & Production" and the Cleveland address as sales and distribution; fabrication cannot be bound to the Cleveland site'),
    262: ('multi_location_unbound', 'About page says BioThane has "two locations in Northeast Ohio"; a page binding fabrication/extrusion or the TPU/PVC/TPE product lines to North Ridgeville'),
    266: ('plant_allocation', 'Allocate the disclosed capability to the Youngstown plant among Boardman Molded locations (already held in PR #351)'),
    343: ('menu_only_no_capability_term', 'Tier A site: "CNC Machining" is a customization-menu item (supports_C), and plastics_machining_cnc has no section 3.6 term; a narrative sentence that the Avon plant machines parts would settle it'),
    423: ('plant_allocation', 'Locations page says "plants in Ohio and Georgia" and calls Wadsworth the corporate office (Minerva, Ohio is named for logistics); a page placing compounding, toll pulverizing or regrind at Wadsworth'),
    453: ('plant_allocation', 'About page lists a New Jersey manufacturing and distribution center and Hartville; a page stating which plant runs the 33 injection molding machines'),
    462: ('multi_location_unbound', 'Home page describes "one of North America\'s largest custom profile and tubing extrusion operations" for the company; no Middlefield address or plant statement is stored'),
    479: ('nothing_found', 'A narrative sentence stating which polymer process the mold texturing serves; stored pages list tool-finishing steps only'),
    485: ('off_vocabulary', 'Page says the company "builds tooling made with composite materials and 3D printing technology"; tooling made from composites has no governed term, and the site already carries tooling_mold_die'),
    487: ('site_type_hq_only', 'Page says Integra Enclosures "offers" CNC machining and drilling on polycarbonate enclosures and gives 8989 Tyler Blvd only as the company address; Atlas site_type is hq_only. A page stating machining is performed at that address, or a site_type correction'),
    535: ('menu_only_no_capability_term', 'Tier B site: the page names fiberglass doors as a product; composites_frp has no section 3.6 term, and a narrative sentence on how the Ashtabula plant makes them would settle it'),
    537: ('partner_processing', 'Page says "Our manufacturing partners are strategically located"; a page stating that Poly Source processes scrap at the Brunswick address'),
    563: ('plant_allocation', 'History page says "two locations" (Beach City 111,000 sq ft and Gnadenhutten 220,000 sq ft); a page stating which plant makes foam insulation (Gnadenhutten has no Atlas site: lead)'),
    576: ('not_in_house', 'Product page says the holster is "Injection molded from a proprietary polymer blend" but not that Raven molds it in-house; a page naming in-house molding at North Ridgeville'),
    591: ('term_hold', 'Applied: injection_molding. Held: the menu terms Decorating, Tool Making, CNC Machining (supports_C on a tier B site, and no section 3.6 term); the about page lists RPI-China toolmaking and molding, so tool counts are not bound to Mentor'),
    646: ('multi_location_unbound', 'Capabilities page lists vacuum forming and injection molding as display add-ons; locations page shows plants in several states (WI, AR addresses on stored pages)'),
    666: ('multi_location_unbound', 'Home page titles the company "Custom Injection Molding in Ohio & Texas"; a page binding molding to the Newton Falls plant rather than the Texas plant'),
    670: ('locality_not_witnessed', 'Pages say only "Located in Northeast Ohio"; the Atlas site is a warehouse_distribution site at 20493 Hannan Pkwy, Walton Hills; a page giving that address and stating production there'),
    764: ('locality_not_witnessed', 'About page calls the company "one of the industry\'s largest Truck Tire retreaders" but no stored page names Dover or 204 Deeds Dr; a page binding retreading to that plant'),
    863: ('not_processor', 'Capabilities page lists "Materials We Support" (PE, PP, PVC, PET) for an additives producer; that names the polymers its products serve, not materials it processes'),
    879: ('nothing_found', 'Injection molding is already tagged; no material term is named (pages say "industrial polymer storage products")'),
    519: ('locality_not_witnessed', 'Stored pages carry a 321 area code and no Elyria address; a page binding FRP duct fabrication to the Elyria site'),
    983: ('multi_location_unbound', 'JP Industrial describes North American locations including North Carolina and gives no Lisbon address on stored pages; a page binding PVC reprocessing and grinding to the Lisbon plant'),
    997: ('nothing_found', 'All six stored pages carry the same 4,693-character text (a script-rendered shell); a fetch that renders the site content would settle it'),
    1029: ('locality_not_witnessed', 'Home page describes rubber profile manufacturing for the Meteor group; no Dover address is stored; a page binding it to the Dover plant'),
    1422: ('off_vocabulary', 'Page lists "Mold Building & Manufacturing" and "Mold Repair" but also sanitary valves and EDM; no page says the molds serve plastics or rubber'),
})
HOLD_TERMS = {  # term-level holds on sites that also have applied terms
}
