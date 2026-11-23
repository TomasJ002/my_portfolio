import unittest

from block.markdown_converter import markdown_to_blocks


class TestMarkdownToBlocks(unittest.TestCase):
    def test_splits_document_into_ordered_blocks(self):
        markdown = "# Heading\n\nA **bold** paragraph.\n\n- First\n- Second"

        self.assertEqual(
            markdown_to_blocks(markdown),
            ["# Heading", "A **bold** paragraph.", "- First\n- Second"],
        )

    def test_trims_whitespace_at_each_block_boundary(self):
        markdown = " \t First block \t\n\n \t Second block \t "

        self.assertEqual(markdown_to_blocks(markdown), ["First block", "Second block"])

    def test_preserves_single_newlines_and_internal_whitespace(self):
        markdown = "first  line\n  indented\tline\nlast line"

        self.assertEqual(markdown_to_blocks(markdown), [markdown])

    def test_ignores_leading_trailing_and_repeated_blank_lines(self):
        markdown = "\n\nFirst\n\n\n\nSecond\n\n\nThird\n\n"

        self.assertEqual(markdown_to_blocks(markdown), ["First", "Second", "Third"])

    def test_ignores_whitespace_only_blocks(self):
        markdown = "First\n\n \t \n\nSecond"

        self.assertEqual(markdown_to_blocks(markdown), ["First", "Second"])

    def test_empty_and_whitespace_only_documents(self):
        for markdown in ("", " \t ", "\n", "\n\n\n\n", " \t\n\n \n"):
            with self.subTest(markdown=markdown):
                self.assertEqual(markdown_to_blocks(markdown), [])

    def test_preserves_duplicate_blocks_and_unicode(self):
        markdown = "Žilina 🏔️\n\nKošice\n\nŽilina 🏔️"

        self.assertEqual(markdown_to_blocks(markdown), ["Žilina 🏔️", "Košice", "Žilina 🏔️"])
