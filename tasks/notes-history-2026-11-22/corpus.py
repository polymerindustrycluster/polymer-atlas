"""Run the splitter over every organization and site row in memory (no writes). Shared by taxonomy, check and estimate."""
import re, collections
from load import load
import notes_split  # noqa: F401  (puts scripts/ on sys.path)
import atlas
from notes_split import split_note, after_note, hits

def contexts():
    orgs, sites = load("organizations"), load("sites")
    by_org = collections.defaultdict(set)
    for s in sites:
        k = atlas.street_key(s["street_address"])
        if k: by_org[s["org_id"]].add(k)
    for r in orgs:
        r["_ctx"] = {"street_keys": by_org.get(r["org_id"], set()), "table": "organizations"}
        r["_id"] = r["org_id"]; r["_table"] = "organizations"
    for r in sites:
        k = atlas.street_key(r["street_address"])
        r["_ctx"] = {"street_keys": {k} if k else set(), "table": "sites", "street_blank": not k}
        r["_id"] = r["site_id"]; r["_table"] = "sites"
    return orgs, sites

def run():
    orgs, sites = contexts()
    for r in orgs + sites:
        r["_parts"] = split_note(r["notes"], r["_ctx"])
    return orgs, sites
