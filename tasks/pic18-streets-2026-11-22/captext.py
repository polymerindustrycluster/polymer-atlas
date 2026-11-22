"""capture_text: the text a binding-gate proof line indexes. MIRRORS scripts/check_evidence_binding.py capture_text/_Text/norm_space as of PR #467
head c5d886be (visible text of the HTML by stdlib html.parser, script/style/noscript/template skipped, entities decoded, whitespace collapsed to one
space; offsets index this string). When #467 merges, import from it instead; check.py asserts parity with it if present."""
import re
from html.parser import HTMLParser


class _Text(HTMLParser):
    SKIP = {"script", "style", "noscript", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        self.skip += tag in self.SKIP

    def handle_endtag(self, tag):
        self.skip -= tag in self.SKIP and self.skip > 0

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def norm_space(s):
    return re.sub(r"\s+", " ", s or "").strip()


def capture_text(data):
    s = data.decode("utf-8", errors="replace")
    if re.search(r"<(?:html|body|head|p|div|span|table|br)\b", s[:4096], re.I):
        t = _Text()
        t.feed(s)
        t.close()
        s = " ".join(t.parts)
    return norm_space(s)
