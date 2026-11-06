"""Small byte-preservation checks for the one-time data step."""
import unittest

from add_crosswalk import append_crosswalk


class CrosswalkTests(unittest.TestCase):
    def test_preserves_quoting_multiline_unicode_line_endings_and_no_final_newline(self):
        before = 'event_id,name,notes\r\nA,"Café, Inc.","line 1\nline 2"\r\nB,"B",""'.encode()
        expected = ('event_id,name,notes,pic_events_slug\r\n'
                    'A,"Café, Inc.","line 1\nline 2",a-winter;a-spring\r\nB,"B","",').encode()
        self.assertEqual(append_crosswalk(before, {"A": "a-winter;a-spring", "B": ""}), expected)

    def test_mismatched_or_duplicate_ids_fail(self):
        for raw, mapping in ((b"event_id\nA\n", {"B": "b"}),
                             (b"event_id\nA\n", {"A": "a", "B": "b"}),
                             (b"event_id\nA\nA\n", {"A": "a"})):
            with self.subTest(raw=raw, mapping=mapping):
                with self.assertRaises((AssertionError, KeyError)):
                    append_crosswalk(raw, mapping)

    def test_malformed_slug_fails_before_serialization(self):
        for value in ('bad,"slug', "pic_events_slug"):
            with self.subTest(value=value), self.assertRaises(AssertionError):
                append_crosswalk(b"event_id\nA\n", {"A": value})


if __name__ == "__main__":
    unittest.main()
