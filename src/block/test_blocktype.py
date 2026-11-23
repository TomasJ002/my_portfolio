import unittest

from block.blocktype import BlockType, block_to_block_type


class TestBlockToBlockType(unittest.TestCase):
    def test_heading_levels_one_through_six(self):
        for level in range(1, 7):
            with self.subTest(level=level):
                block = "#" * level + " Žilina"
                self.assertIs(block_to_block_type(block), BlockType.HEADING)

    def test_invalid_heading_markers_are_paragraphs(self):
        for block in ("#", "######", "####### Title", "#Title", "#\tTitle", " # Title"):
            with self.subTest(block=block):
                self.assertIs(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_fenced_code_can_be_empty_or_contain_other_block_markers(self):
        for block in ("```\n```", "```\n# Heading\n> Quote\n- Item\n```"):
            with self.subTest(block=block):
                self.assertIs(block_to_block_type(block), BlockType.CODE)

    def test_incomplete_or_unsupported_code_fences_are_paragraphs(self):
        for block in ("```", "```\ncode", "code\n```", "```python\npass\n```"):
            with self.subTest(block=block):
                self.assertIs(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_every_quote_line_must_start_with_a_quote_marker(self):
        for block in (">", ">Quote", "> First\n>> Nested\n>"):
            with self.subTest(block=block):
                self.assertIs(block_to_block_type(block), BlockType.QUOTE)
        for block in (" > Indented", "> First\nplain", "> First\n\n> Last"):
            with self.subTest(block=block):
                self.assertIs(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_every_unordered_list_line_must_start_with_dash_and_space(self):
        for block in ("- One", "- One\n- Two"):
            with self.subTest(block=block):
                self.assertIs(block_to_block_type(block), BlockType.UNORDERED_LIST)
        for block in ("-One", "-\tOne", "* One", "- One\nplain", "- One\n1. Two"):
            with self.subTest(block=block):
                self.assertIs(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_supports_single_items_and_multi_digit_numbers(self):
        for block in ("1. One", "\n".join(f"{i}. Item" for i in range(1, 12))):
            with self.subTest(block=block):
                self.assertIs(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_requires_consecutive_numbers_starting_at_one(self):
        for block in ("0. Zero", "2. Two", "01. One", "1.One", "1.\tOne",
                      "1. One\n3. Three", "1. One\n1. Again", "1. One\nplain"):
            with self.subTest(block=block):
                self.assertIs(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_empty_plain_and_inline_markdown_blocks_are_paragraphs(self):
        for block in ("", " \t\n", "First line\nSecond line", "**Bold** and [link](/page)"):
            with self.subTest(block=block):
                self.assertIs(block_to_block_type(block), BlockType.PARAGRAPH)
