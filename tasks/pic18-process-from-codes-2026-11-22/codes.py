"""The code-to-process table (Part B). T1 = the NAICS title itself names the activity, so the process term is the title restated.
Titles are from data/ref_codes.csv (SCHEMA 2.2); 333511 from SCHEMA 2.2 line 539. Nothing here widens a code: a code outside T1/T2
is REJECT (too broad, product not process, or mixed processes)."""
T1 = {  # code: (process term, why it is one-to-one)
 '326211': ('tire_manufacturing', 'title is the process: tire manufacturing, retreading excluded'),
 '326212': ('tire_retreading', 'title is the process: tire retreading'),
 '326220': ('hose_belting_manufacturing', 'title names hoses and belting, which is the term'),
 '325991': ('custom_compounding', 'title is the process: custom compounding of purchased resins'),
 '325510': ('coating_formulation', 'title is making paint and coatings; 3.1 coating_formulation is "makes it" (contrast coating_applying)'),
 '325520': ('adhesive_sealant_formulation', 'title is making adhesives'),
 '325910': ('ink_formulation', 'title is making printing ink'),
 '333511': ('mold_tool_making', 'title is making industrial molds (SCHEMA 2.2 line 539)'),
 '326140': ('foam_production_unspecified', 'title names a foam product; the process type is not stated, which is what the unspecified term is for'),
 '326150': ('foam_production_unspecified', 'same as 326140 for urethane and other foam'),
}
T2 = {  # owner pick: the title names a product or material; the process is the usual route, not the definition
 '325211': ('polymerization', 'resin manufacture is polymerization by the usual route, but the title names a material and the plant may only blend'),
 '325212': ('polymerization', 'same as 325211 for synthetic rubber'),
 '326121': ('extrusion_profile', 'profile shapes are usually extruded; pultruded and machined shapes exist'),
 '326160': ('blow_molding', 'bottles are usually blow molded (legacy umbrella term); injection-molded jars exist'),
 '326130': ('laminating', 'laminated plate and shape; the title names a product and thermoset laminate presses are not in 3.1 laminating'),
}
REJECT_WHY = {
 '326111': 'bags and pouches: extrusion plus converting, no single process',
 '326112': 'packaging film and sheet incl. laminated: blown, cast and laminated all fit',
 '326113': 'film and sheet: extruded, cast or calendered',
 '326122': 'pipe and pipe fittings: fittings are molded, pipe is extruded',
 '326191': 'plumbing fixtures: molded, thermoformed or fabricated',
 '326192': 'resilient floor covering: calendered, coated or pressed',
 '326199': 'all other plastics products: no process',
 '326291': 'rubber products for mechanical use: molded, extruded or cut',
 '326299': 'all other rubber products: no process',
 '325199': 'all other basic organic chemicals: no process in 3.1',
 '325998': 'all other miscellaneous chemical products: no process',
}
