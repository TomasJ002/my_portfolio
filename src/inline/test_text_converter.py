import unittest

from inline.text_converter import text_to_textnodes
from textnode import TextNode, TextType


class TestTextToTextNodes(unittest.TestCase):
    def test_converts_all_inline_types_in_order(self):
        text = "**Bold** _italic_ `code` ![Photo](/photo.png) [Guide](/guide)\n"

        self.assertEqual(
            text_to_textnodes(text),
            [
                TextNode("Bold", TextType.BOLD),
                TextNode(" ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" ", TextType.TEXT),
                TextNode("Photo", TextType.IMAGE, "/photo.png"),
                TextNode(" ", TextType.TEXT),
                TextNode("Guide", TextType.LINK, "/guide"),
                TextNode("\n", TextType.TEXT),
            ],
        )

    def test_preserves_plain_text_unicode_and_whitespace(self):
        for text in ("  Žilina & Košice\n", " \t\n", "A *single* asterisk"):
            with self.subTest(text=text):
                self.assertEqual(text_to_textnodes(text), [TextNode(text, TextType.TEXT)])

    def test_empty_input_and_empty_delimited_spans(self):
        for text in ("", "****", "__", "``"):
            with self.subTest(text=text):
                self.assertEqual(text_to_textnodes(text), [])

    def test_adjacent_and_repeated_markup_creates_no_empty_text_nodes(self):
        text = "**one****two**_three_`four`[Same](/same)[Same](/same)"

        self.assertEqual(
            text_to_textnodes(text),
            [
                TextNode("one", TextType.BOLD),
                TextNode("two", TextType.BOLD),
                TextNode("three", TextType.ITALIC),
                TextNode("four", TextType.CODE),
                TextNode("Same", TextType.LINK, "/same"),
                TextNode("Same", TextType.LINK, "/same"),
            ],
        )

    def test_distinguishes_images_and_links_with_identical_labels_and_urls(self):
        self.assertEqual(
            text_to_textnodes("![Same](/same)[Same](/same)"),
            [
                TextNode("Same", TextType.IMAGE, "/same"),
                TextNode("Same", TextType.LINK, "/same"),
            ],
        )

    def test_keeps_image_and_link_markup_inside_code_literal(self):
        text = "Use `![Photo](/photo.png) [Guide](/guide)`."

        self.assertEqual(
            text_to_textnodes(text),
            [
                TextNode("Use ", TextType.TEXT),
                TextNode("![Photo](/photo.png) [Guide](/guide)", TextType.CODE),
                TextNode(".", TextType.TEXT),
            ],
        )

    def test_preserves_malformed_image_and_link_markup(self):
        text = "![Photo] (photo.png) [Broken](/missing"

        self.assertEqual(text_to_textnodes(text), [TextNode(text, TextType.TEXT)])

    def test_allows_empty_image_alt_text_link_label_and_destinations(self):
        self.assertEqual(
            text_to_textnodes("![](/icon.png)[](/home)![alt]()[label]()"),
            [
                TextNode("", TextType.IMAGE, "/icon.png"),
                TextNode("", TextType.LINK, "/home"),
                TextNode("alt", TextType.IMAGE, ""),
                TextNode("label", TextType.LINK, ""),
            ],
        )

    def test_rejects_unmatched_delimiters(self):
        for text in ("**open", "close_", "text `open", "**valid** then **open"):
            with self.subTest(text=text):
                with self.assertRaisesRegex(ValueError, "unmatched delimiter"):
                    text_to_textnodes(text)
