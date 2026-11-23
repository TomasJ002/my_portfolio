import unittest

from page_generator import extract_title


class TestExtractTitle(unittest.TestCase):
    def test_extracts_h1(self):
        self.assertEqual(extract_title("# Hello"), "Hello")

    def test_trims_whitespace_and_preserves_unicode(self):
        self.assertEqual(extract_title("#  \tŽilina  🌲 \t\r\n"), "Žilina  🌲")

    def test_finds_first_h1_after_other_lines(self):
        markdown = "## Subtitle\nA paragraph\n# First\n# Second"
        self.assertEqual(extract_title(markdown), "First")

    def test_rejects_documents_without_a_title(self):
        for markdown in ("", "Plain text", "## Subtitle", "#No space", "#", "#  ", "Text # inline"):
            with self.subTest(markdown=markdown):
                with self.assertRaisesRegex(ValueError, "H1"):
                    extract_title(markdown)
