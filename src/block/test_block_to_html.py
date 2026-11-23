import unittest

from block.block_to_html import markdown_to_html_node, text_to_children
from htmlnode import LeafNode, ParentNode


class TestTextToChildren(unittest.TestCase):
    def test_converts_inline_markup_in_order(self):
        children = text_to_children("  Žilina **bold** _italic_ `code` [map](/map)\n")

        self.assertTrue(all(isinstance(child, LeafNode) for child in children))
        self.assertEqual(
            "".join(child.to_html() for child in children),
            '  Žilina <b>bold</b> <i>italic</i> <code>code</code> <a href="/map">map</a>\n',
        )

    def test_converts_image_with_empty_alt_text(self):
        child, = text_to_children("![](/image.png)")

        self.assertIsInstance(child, LeafNode)
        self.assertEqual(child.tag, "img")
        self.assertEqual(child.value, "")
        self.assertEqual(child.props, {"src": "/image.png", "alt": ""})
        self.assertEqual(child.to_html(), '<img src="/image.png" alt="">')

    def test_empty_text_has_no_children(self):
        self.assertEqual(text_to_children(""), [])

    def test_unmatched_inline_delimiter_raises_value_error(self):
        with self.assertRaisesRegex(ValueError, "unmatched delimiter"):
            text_to_children("**open")


class TestMarkdownToHTMLNode(unittest.TestCase):
    def test_renders_mixed_blocks_in_document_order(self):
        markdown = (
            "# Heading\n\n"
            "Visit [Žilina](/city).\n\n"
            "> A **quote**\n\n"
            "- First\n- _Second_\n\n"
            "1. One\n2. Two"
        )
        node = markdown_to_html_node(markdown)

        self.assertIsInstance(node, ParentNode)
        self.assertEqual(
            node.to_html(),
            '<div><h1>Heading</h1><p>Visit <a href="/city">Žilina</a>.</p>'
            '<blockquote>A <b>quote</b></blockquote>'
            '<ul><li>First</li><li><i>Second</i></li></ul>'
            '<ol><li>One</li><li>Two</li></ol></div>',
        )

    def test_renders_heading_levels_one_through_six(self):
        for level in range(1, 7):
            with self.subTest(level=level):
                node = markdown_to_html_node("#" * level + " Title")
                self.assertIsInstance(node, ParentNode)
                self.assertEqual(node.to_html(), f"<div><h{level}>Title</h{level}></div>")

    def test_renders_fenced_code_without_inline_conversion(self):
        node = markdown_to_html_node("```\n**literal**\n  indented\n```")

        self.assertIsInstance(node, ParentNode)
        self.assertEqual(node.to_html(), "<div><pre><code>**literal**\n  indented\n</code></pre></div>")

    def test_skips_surrounding_and_repeated_blank_lines(self):
        node = markdown_to_html_node("\n\nFirst\n\n\n\nSecond\n\n")

        self.assertIsInstance(node, ParentNode)
        self.assertEqual(node.to_html(), "<div><p>First</p><p>Second</p></div>")

    def test_invalid_block_markers_render_as_paragraphs(self):
        node = markdown_to_html_node("####### Heading\n\n2. Item")

        self.assertIsInstance(node, ParentNode)
        self.assertEqual(node.to_html(), "<div><p>####### Heading</p><p>2. Item</p></div>")
