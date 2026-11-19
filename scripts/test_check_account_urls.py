"""check_account_urls: each barred form is caught in every common representation; placeholders, fisid, fragments,
sibling hosts and prose pass. Synthetic accounts only. UC-host fixtures are split ("…/p/" "smithjq") so that no
line of this file holds the form and the pre-push disclosure scan stays quiet."""
import unittest
from urllib.parse import quote

from check_account_urls import findings, read

UC = "https://researchdirectory.uc.edu/p/"


class TestFindings(unittest.TestCase):
    def test_barred_forms_caught(self):
        for line in (
            "https://www.example.org/profile?u=jq12",
            "x,https://www.example.org/dir/people.php?id=3&unid=ab9,y",
            "www.math.example.org/~jq9/cv.pdf",
            UC + "smithjq",
            "HTTPS://ResearchDirectory.UC.edu./p/" "smithjq",
            "u='" + UC + "smithjq'",
            "[profile](https://www.example.org/~jq9/)",
            "see `https://www.example.org/x?u=jq12`.",
            # Codex r1: percent-encoding, a port, escapes, scheme-relative, unquoted assignment, HTML entity
            "https://www.example.org/?%75nid=jq9",
            "https://www.example.org/?u=%6Aq9",
            "https://www.example.org/%7Ejq9",
            "https://researchdirectory.uc.edu:443/p/" "smithjq",
            (UC + "smithjq").replace("/", "\\/"),
            "https://www.example.org/\\u007ejq9",
            "//researchdirectory.uc.edu/p/" "smithjq",
            "url=" + UC + "smithjq",
            "https://www.example.org/x?a=1&amp;unid=jq9",
            # Gemini r1: JSON \n before a URL, Markdown bold, braces, a percent-encoded value or path segment
            '{"note": "see\\n' + UC + 'smithjq"}',
            "**" + UC + "smithjq**",
            "{" + UC + "smithjq}",
            UC + "%73mithjq",
            "https://researchdirectory.uc.edu/%70/" "smithjq",
            # Codex r2: an encoded key, an entity for "=", path punctuation, a JS hex escape, a URL-encoded redirect target
            "https://www.example.org/?u%6eid=jq9",
            "https://www.example.org/?u&equals;jq9",
            "https://www.example.org/people;jsessionid=1?unid=jq9",
            "https://www.example.org/entry(1)?unid=jq9",
            "https://www.example.org/last,first?unid=jq9",
            "https://www.example.org/\\x7ejq9",
            "https://www.example.org/login?next=" + quote(UC + "smithjq", safe=""),
            # Codex r3: a bracketed query filter, an apostrophe in the path, a bare IPv4 host; Gemini r3: JSON \n
            'ORG-1,"https://www.example.org/list?filter[kind]=staff&unid=jq9",2026-11-19',
            "https://www.example.org/o'brien/profile?u=jq9",
            "192.0.2.7/profile?u=jq9",
            '{"note": "see\\nresearchdirectory.uc.edu/p/' 'smithjq"}',
        ):
            self.assertEqual(findings(line), [1], line)

    def test_allowed_forms_pass(self):
        for line in (
            "https://www.example.org/profile?u=<id>",
            "https://www.example.org/~<acct>/cv.pdf",
            "researchdirectory.uc.edu/p/<shortname> **[v1.15]**",
            "https://experts.example.org/en/persons/x/fisid_123456",
            "https://www.sibling.uc.edu/p/smithjq",
            "https://researchdirectory.uc.edu/x/p/smithjq",
            "https://www.example.org/researchdirectory.uc.edu/p/" "smithjq",
            "https://www.example.org/page#?u=jq9",
            "a `?unid=<id>` query, and `**[v1.15]**` prose; ~99 candidates; menu=1",
            "(see https://www.example.org/page), ~99 items; u=1",
            # Codex r4: a Markdown link whose text is its own URL, and a text-selection fragment
            "[https://researchdirectory.uc.edu](https://researchdirectory.uc.edu)",
            "[https://www.example.org/page](https://www.example.org/page#:~:text=Polymer%20lab)",
        ):
            self.assertEqual(findings(line), [], line)

    def test_reads_utf16_by_bom(self):  # Codex r2: a UTF-16 export was decoded as UTF-8 and passed
        for enc in ("utf-16", "utf-8-sig", "utf-32"):
            self.assertEqual(findings(read("url\nhttps://www.example.org/?u=jq9\n".encode(enc))), [2], enc)

    def test_reads_utf16_without_bom(self):  # Codex r3: Python's utf-16-le and Node's utf16le write no BOM
        for enc in ("utf-16-le", "utf-16-be"):
            self.assertEqual(findings(read("url\nhttps://www.example.org/?u=jq9\n".encode(enc))), [2], enc)
            notes = "url,notes\nhttps://www.example.org/?u=jq9," + "\u65e5\u672c\u8a9e\u306e\u30e1\u30e2" * 16 + "\n"
            self.assertEqual(findings(read(notes.encode(enc))), [2], enc + " with CJK notes (Codex r4)")

    def test_html_base_href(self):  # Codex r3: a root-relative link under <base href> on the UC directory
        page = '<base href="https://researchdirectory.uc.edu/">\n<a href="/p/' 'smithjq">profile</a>\n<a href="/about">x</a>'
        self.assertEqual(findings(page), [2])

    def test_reports_line_numbers(self):
        self.assertEqual(findings("ok\nhttps://www.example.org/~jq9\nok\n?u=x https://a.example.org/?u=jq1"), [2, 4])


if __name__ == "__main__":
    unittest.main()
