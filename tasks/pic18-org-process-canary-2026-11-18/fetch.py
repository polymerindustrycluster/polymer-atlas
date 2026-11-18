"""Live fetches for the canary (contract rule 14). Every URL is either the website on the org record or a link on a stored page.
Cache: S/persist/pic18-org-process-canary-2026-11-18/cache (outside the repo). Robots-gated via scripts/site_corpus.py."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from site_corpus import Corpus, DEFAULT_CACHE
CACHE = DEFAULT_CACHE.parents[1] / "persist/pic18-org-process-canary-2026-11-18/cache"
# (org, url, why it is allowed)
URLS = [
 ("ORG-000107", "http://www.tmplasticsusa.com/", "website on the org record"),
 ("ORG-000192", "http://trianglechem.com/", "website on the org record"),
 ("ORG-001497", "https://budzar.com/", "website on the org record"),
 ("ORG-000488", "https://pharmacylite.com/biodegradable", "href on stored home page (biodegradable)"),
 ("ORG-001513", "https://www.coltene.com/company/about/", "link on stored company page"),
 ("ORG-001513", "https://www.coltene.com/science/", "link on stored company page"),
 ("ORG-001986", "https://optimaxplastic.com/index.php/rotomolding/", "website on the org record"),
 ("ORG-000488", "https://pharmacylite.com/products/simple-safe-vial-system", "href on stored home page"),
 ("ORG-000488", "https://pharmacylite.com/products/convenient-vial-sets", "href on stored home page"),
 ("ORG-000488", "https://pharmacylite.com/products/compounding-solutions", "href on stored home page"),
 ("ORG-000488", "https://pharmacylite.com/pdf/bio-sheet-2021.pdf", "href on stored home page"),
 ("ORG-002047", "https://www.wayne-dalton.com/garage-doors/by-material/vinyl", "link on stored home page"),
]
if __name__ == "__main__":
    c = Corpus(CACHE); out = []
    for org, u, why in URLS:
        r = c.fetch(u); out.append(dict(org=org, url=u, why=why, status=r["status"], http=r["http_status"], sha256=r["sha256"], fetched_at=r["fetched_at"], text_file=r["text_file"], final_url=r["final_url"]))
        print(org, u, r["status"], r["http_status"])
    Path(CACHE).parent.joinpath("live-fetches.json").write_text(json.dumps(out, indent=1))
