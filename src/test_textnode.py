import unittest
from typing import cast

from htmlnode import LeafNode
from textnode import TextNode, TextType, text_node_to_html_node


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        node3 = TextNode("This is a text node", TextType.ITALIC)
        node4 = TextNode("This is another text node", TextType.BOLD)
        node5 = TextNode("This is another text node", TextType.ITALIC)
        node6 = TextNode("This is a text node", TextType.BOLD, url=None)
        node7 = TextNode("This is a text node", TextType.BOLD, "aaaauto.sk")
        self.assertEqual(node, node2)
        self.assertNotEqual(node, node3)
        self.assertNotEqual(node, node4)
        self.assertNotEqual(node, node5)
        self.assertEqual(node, node6)
        self.assertNotEqual(node, node7)
        self.assertNotEqual(node6, node7)


class TestTextNodeToHTMLNode(unittest.TestCase):
    def test_non_url_types_preserve_text_and_render_expected_tags(self):
        cases = (
            (TextType.TEXT, None),
            (TextType.BOLD, "b"),
            (TextType.ITALIC, "i"),
            (TextType.CODE, "code"),
        )
        for text_type, tag in cases:
            for text in ("", "  Žilina & <span>text</span>\n"):
                with self.subTest(text_type=text_type, text=text):
                    leaf = text_node_to_html_node(TextNode(text, text_type))
                    self.assertIsInstance(leaf, LeafNode)
                    self.assertEqual(leaf.tag, tag)
                    self.assertEqual(leaf.value, text)
                    self.assertIsNone(leaf.children)
                    self.assertIsNone(leaf.props)
                    expected_html = text if tag is None else f"<{tag}>{text}</{tag}>"
                    self.assertEqual(leaf.to_html(), expected_html)

    def test_non_url_types_ignore_supplied_url(self):
        for text_type in (TextType.TEXT, TextType.BOLD, TextType.ITALIC, TextType.CODE):
            with self.subTest(text_type=text_type):
                leaf = text_node_to_html_node(TextNode("Text", text_type, "/unused"))
                self.assertIsNone(leaf.props)

    def test_link_uses_text_as_content_and_url_as_href(self):
        for text, url in (("Visit Žilina", "/visit"), ("", "/visit"), ("Text", "")):
            with self.subTest(text=text, url=url):
                leaf = text_node_to_html_node(TextNode(text, TextType.LINK, url))
                self.assertIsInstance(leaf, LeafNode)
                self.assertEqual(leaf.tag, "a")
                self.assertEqual(leaf.value, text)
                self.assertIsNone(leaf.children)
                self.assertEqual(leaf.props, {"href": url})
                self.assertEqual(leaf.to_html(), f'<a href="{url}">{text}</a>')

    def test_image_uses_text_as_alt_and_has_empty_content(self):
        for text, url in (("Žilina skyline", "/city.png"), ("", "/city.png"), ("City", "")):
            with self.subTest(text=text, url=url):
                leaf = text_node_to_html_node(TextNode(text, TextType.IMAGE, url))
                self.assertIsInstance(leaf, LeafNode)
                self.assertEqual(leaf.tag, "img")
                self.assertEqual(leaf.value, "")
                self.assertIsNone(leaf.children)
                self.assertEqual(leaf.props, {"src": url, "alt": text})
                self.assertEqual(leaf.props_to_html(), f' src="{url}" alt="{text}"')

    def test_link_and_image_reject_missing_urls(self):
        for text_type in (TextType.LINK, TextType.IMAGE):
            nodes = (TextNode("Text", text_type), TextNode("Text", text_type, url=None))
            for node in nodes:
                with self.subTest(text_type=text_type):
                    with self.assertRaisesRegex(ValueError, "require a URL"):
                        text_node_to_html_node(node)

    def test_rejects_unsupported_text_types(self):
        for invalid_type in ("unsupported", "text", None):
            with self.subTest(text_type=invalid_type):
                node = TextNode("Text", cast(TextType, invalid_type))
                with self.assertRaisesRegex(ValueError, "Invalid text type"):
                    text_node_to_html_node(node)


if __name__ == "__main__":
    unittest.main()
