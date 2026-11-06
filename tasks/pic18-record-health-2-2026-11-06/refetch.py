#!/usr/bin/env python3
"""Re-fetch packet sources raw; no summarizer. Failed fetches fail closed."""
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'pic18-record-health-2026-11-06'))
from health import read

class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.skip = 0; self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in {'script','style'}: self.skip += 1
    def handle_endtag(self, tag):
        if tag in {'script','style'}: self.skip -= 1
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)

if __name__ == '__main__':
    packet=read(Path(__file__).with_name('evidence_packet.csv'))
    seen=set()
    with tempfile.TemporaryDirectory() as d:
        for row in packet:
            url=row['source_ref']
            if url in seen: continue
            raw=Path(d)/'raw'
            subprocess.run(['curl','--fail','-L','-sS','--max-time','45','-A','Mozilla/5.0',url,'-o',str(raw)],check=True)
            out=Path(row['raw_path'])
            if raw.read_bytes().startswith(b'%PDF'):
                subprocess.run(['pdftotext','-layout',str(raw),str(out)],check=True)
            else:
                p=Text();p.feed(raw.read_text());out.write_text(' '.join(p.parts))
            assert out.stat().st_size, url
            seen.add(url)
    print(f'Re-fetched {len(seen)} primary source URLs; run build.py --raw-check next')
