"""check_account_urls: each barred form is caught in every common representation; placeholders, fisid, fragments,
sibling hosts and prose pass. Synthetic accounts only. UC-host fixtures are split ("…/p/" "smithjq") so that no
line of this file holds the form and the pre-push disclosure scan stays quiet."""
import unittest

from check_account_urls import findings

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
        ):
            self.assertEqual(findings(line), [], line)

    def test_reports_line_numbers(self):
        self.assertEqual(findings("ok\nhttps://www.example.org/~jq9\nok\n?u=x https://a.example.org/?u=jq1"), [2, 4])


if __name__ == "__main__":
    unittest.main()
