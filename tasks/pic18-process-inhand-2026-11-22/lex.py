import re
# process lexicon -> SCHEMA 3.1 term (candidate only; adjudicated by reading)
LEX=[("injection_molding",r"injection[- ]mold(?:ing|ed|er|s)?|injection[- ]moulding"),
("blow_molding",r"blow[- ]mold(?:ing|ed)"),("extrusion_unspecified",r"\bextrud\w*|\bextrusion\b"),
("thermoforming_unspecified",r"thermoform\w*"),("rotational_molding",r"rotational(?:ly)?[- ]mold\w*|rotomold\w*"),
("compression_molding",r"compression[- ]mold\w*"),("transfer_molding",r"transfer[- ]mold\w*"),("calendering",r"calender\w*"),
("rubber_mixing_compounding",r"rubber (?:mixing|compound\w*)|mix(?:es|ing)? rubber"),("compounding_unspecified",r"\bcompound(?:s|ing|er|ers|ed)\b"),
("composites_pultrusion",r"pultru\w*"),("composites_filament_winding",r"filament[- ]wind\w*"),("composites_hand_layup",r"hand[- ]lay[- ]?up|lay-up"),
("laminating",r"laminat\w*"),("coating_applying",r"coating (?:of|line|operation)|powder[- ]coat\w*|\bapplies? coating"),("coating_formulation",r"(?:paint|coating)s? (?:blend|manufactur|formulat)\w*|formulat\w* (?:paint|coating)\w*"),
("printing_decorating_plastics",r"\bprint(?:s|ing)\b"),("plastics_machining_cnc",r"\bcnc\b|machin(?:es|ing)"),("plastics_fabrication_welding",r"fabricat\w*|plastic weld\w*"),
("recycling_mechanical",r"recycl\w*|reclaim\w*|regrind\w*|pelletiz\w*"),("mold_tool_making",r"mold (?:making|manufactur\w*|building)|tool(?:ing)? (?:and|&) (?:die|mold)|mold maker|moldmak\w*"),
("foam_production_unspecified",r"\bfoam\w*"),("tire_manufacturing",r"tire manufactur\w*"),("tire_retreading",r"retread\w*"),
("additive_manufacturing_polymer",r"3d[- ]print\w*|additive manufactur\w*"),("assembly_secondary_ops",r"\bassembl(?:y|es|ing)\b"),("die_cutting_converting",r"die[- ]cut\w*|converting"),
("polymerization",r"polymeri[sz]\w*"),("vulcanization_curing_services",r"vulcani[sz]\w*"),("latex_dipping_foaming",r"latex dip\w*|dipp?ed"),("hose_belting_manufacturing",r"\bhose\b|belting"),
("pigment_colorant_dispersion",r"dispers\w*"),("color_masterbatch",r"masterbatch"),("potting_encapsulation_casting",r"potting|encapsulat\w*"),("molding_unspecified",r"\bmold(?:s|ing|ed|er)\b|\bmould\w*")]
LEXRE=[(t,re.compile(p,re.I)) for t,p in LEX]
def sents(text):
    return [s.strip() for s in re.split(r"(?<=[.;!?])\s+|\s\|\s|\n",text) if s.strip()]
def hits(sent):
    return sorted({t for t,r in LEXRE if r.search(sent)})
