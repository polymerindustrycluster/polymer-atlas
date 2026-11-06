"""Raw HTML fetch via curl; token matcher reused from the house evidence-repair prep."""
import importlib.util
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('repair_prep', ROOT / 'tasks/evidence-repair-2-2026-11-04/prep.py')
prep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prep)
W = prep.W

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.links = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.skip += 1
        if tag == 'a': self.links.extend(v for k, v in attrs if k == 'href')
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip = max(0, self.skip - 1)
    def handle_data(self, text):
        if not self.skip: self.parts.append(text)

def fetch(url):
    for route in (url, 'https://r.jina.ai/' + url):
        r = subprocess.run(['curl', '--compressed', '-fLsS', '--max-time', '35', '-A', 'Mozilla/5.0', route], capture_output=True)
        if r.returncode: continue
        if r.stdout.startswith(b'%PDF'):
            with tempfile.TemporaryDirectory() as d:
                path = Path(d) / 'certificate.pdf'; path.write_bytes(r.stdout)
                pdf = subprocess.run(['pdftotext', '-layout', str(path), '-'], capture_output=True, check=True)
                return pdf.stdout.decode('utf-8'), [], route
        raw = r.stdout.decode('utf-8', 'replace')
        p = Page(); p.feed(raw)
        text = ' '.join(' '.join(p.parts).split()) if route == url else raw
        if len(text) > 100 and not any(marker in text[:500].lower() for marker in ('just a moment...', 'you are being redirected', 'access denied', "doesn't work properly without javascript", 'request rejected network security system')):
            return text, p.links, route
    raise RuntimeError('unfetchable: ' + url)

def found(text, quote):
    p, q = W(text), W(quote)
    return bool(q) and any(p[i:i+len(q)] == q for i in range(len(p)-len(q)+1))

if __name__ == '__main__':
    import sys
    text, links, route = fetch(sys.argv[1]); print(route); print(text); print('\nLINKS', '\n'.join(links))
