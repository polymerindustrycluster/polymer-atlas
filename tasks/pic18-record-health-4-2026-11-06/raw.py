#!/usr/bin/env python3
"""Re-fetch packet sources raw; no summarizer. Failed fetches fail closed."""
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path
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

