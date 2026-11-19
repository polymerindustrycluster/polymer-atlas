"""check_account_urls: each barred form is caught (also inside quotes and Markdown links); placeholders, fisid and
prose pass. Synthetic accounts only."""
import unittest

from check_account_urls import findings


class TestFindings(unittest.TestCase):
    def test_barred_forms_caught(self):
        for line in (
            "https://www.example.org/profile?u=jq12",
            "x,https://www.example.org/dir/people.php?id=3&unid=ab9,y",
            "www.math.example.org/~jq9/cv.pdf",
            "https://researchdirectory.uc.edu/p/" "smithjq",  # split so no file line holds the form
            "HTTPS://ResearchDirectory.UC.edu./p/" "smithjq",
            "u='https://researchdirectory.uc.edu/p/" "smithjq'",
            "[profile](https://www.example.org/~jq9/)",
            "see `https://www.example.org/x?u=jq12`.",
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
            "a `?unid=<id>` query, and `**[v1.15]**` prose",
        ):
            self.assertEqual(findings(line), [], line)

    def test_reports_line_numbers(self):
        self.assertEqual(findings("ok\nhttps://www.example.org/~jq9\nok\n?u=x https://a.example.org/?u=jq1"), [2, 4])


if __name__ == "__main__":
    unittest.main()
