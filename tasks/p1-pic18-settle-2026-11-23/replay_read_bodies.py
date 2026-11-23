"""Replay the two sealed reader quote normalizations from landed bodies."""
import gzip
import html
from html.parser import HTMLParser
import re
import subprocess
import unicodedata

class VisibleText(HTMLParser):
    skip_tags = {"script", "style", "noscript", "template"}
    blocks = {"br", "p", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "td"}

    def __init__(self, lane):
        super().__init__()
        self.parts = []
        self.skip = 0
        self.boundaries = self.blocks | ({"tr", "th", "span", "a"} if lane == "read-b" else set())

    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags:
            self.skip += 1
        if tag in self.boundaries:
            self.parts.append(" ")
        if tag == "img":
            self.parts.extend(" "+value+" " for key, value in attrs if key == "alt" and value)

    def handle_endtag(self, tag):
        if tag in self.skip_tags and self.skip:
            self.skip -= 1

    def handle_data(self, contents):
        if not self.skip:
            self.parts.append(contents)


def text(data, lane):
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    if data[:4] == b"%PDF":
        return subprocess.check_output(["pdftotext", "-layout", "-", "-"], input=data, timeout=60).decode("utf-8", "replace")
    decoded = data.decode("utf-8", "replace")
    if lane == "read-b" and decoded.lstrip()[:1] in "{[":
        return decoded
    parser = VisibleText(lane)
    parser.feed(decoded)
    return html.unescape(" ".join(parser.parts))


def fold(value, lane):
    value = unicodedata.normalize("NFKD", value)
    value = value.translate(str.maketrans("’‘“”–—", "''\"\"--"))
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = " ".join(re.sub(r"[|/•·]", " ", value).split()).casefold()
    return re.sub(r"\s+([,.;:)])", r"\1", value) if lane == "read-a" else value


def quote_matches(quote, normalized_body, lane):
    if lane == "read-a":
        parts = [q for q in re.split(r"\s*(?:\.\.\.|…)\s*", quote) if q.strip()]
        return bool(parts) and all(fold(q, lane) in normalized_body for q in parts)
    quote = re.sub(r"\s*\[[^\]]*cut\]|\s*\([^)]*(cut|page footer|footer text|contact page|list entry)[^)]*\)|\.\.\.|…", "", quote)
    exact = fold(quote, lane)
    return bool(exact) and exact in normalized_body
