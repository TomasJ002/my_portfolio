import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        node = HTMLNode(
            "a",
            "Click me",
            None,
            {
                "href": "https://www.google.com",
                "target": "_blank",
            },
        )
        self.assertEqual(
            node.props_to_html(),
            ' href="https://www.google.com" target="_blank"',
        )

    def test_props_none(self):
        node = HTMLNode("p", "Hello world")
        self.assertEqual(node.props_to_html(), "")

    def test_props_empty(self):
        node = HTMLNode("p", "Hello world", None, {})
        self.assertEqual(node.props_to_html(), "")

    def test_single_prop(self):
        node = HTMLNode(
            "img",
            None,
            None,
            {"src": "image.png"},
        )
        self.assertEqual(
            node.props_to_html(),
            ' src="image.png"',
        )

    def test_to_html_not_implemented(self):
        node = HTMLNode("p", "Hello world")
        with self.assertRaises(NotImplementedError):
            node.to_html()


class TestLeafNode(unittest.TestCase):
    def test_constructor_passes_props_without_children(self):
        props = {"class": "intro"}
        node = LeafNode("p", "Hello", props)

        self.assertIsInstance(node, HTMLNode)
        self.assertEqual(node.tag, "p")
        self.assertEqual(node.value, "Hello")
        self.assertIsNone(node.children)
        self.assertEqual(node.props, props)

    def test_renders_tag_with_props(self):
        node = LeafNode(
            "a",
            "Read more",
            props={"href": "/about", "target": "_blank"},
        )

        self.assertEqual(
            node.to_html(),
            '<a href="/about" target="_blank">Read more</a>',
        )

    def test_renders_empty_attribute_value(self):
        node = LeafNode("span", "Text", props={"data-label": ""})

        self.assertEqual(node.to_html(), '<span data-label="">Text</span>')

    def test_renders_without_attributes(self):
        cases = (
            LeafNode("p", "Hello"),
            LeafNode("p", "Hello", props=None),
            LeafNode("p", "Hello", props={}),
        )
        for node in cases:
            with self.subTest(props=node.props):
                self.assertEqual(node.to_html(), "<p>Hello</p>")

    def test_untagged_value_is_returned_verbatim(self):
        for value in ("plain text", "", "  \n", "Žilina & <em>text</em>"):
            with self.subTest(value=value):
                self.assertEqual(LeafNode(None, value).to_html(), value)

    def test_untagged_node_does_not_render_props(self):
        node = LeafNode(None, "Text", props={"class": "intro"})

        self.assertEqual(node.to_html(), "Text")

    def test_tagged_value_is_preserved_verbatim(self):
        value = "  Žilina & <em>text</em>\n"

        self.assertEqual(LeafNode("p", value).to_html(), f"<p>{value}</p>")

    def test_empty_tagged_value_still_renders_tags(self):
        self.assertEqual(LeafNode("p", "").to_html(), "<p></p>")
        self.assertEqual(
            LeafNode("div", "", props={"id": "empty"}).to_html(),
            '<div id="empty"></div>',
        )

    def test_none_value_raises_value_error(self):
        for tag in (None, "p"):
            for props in (None, {"id": "missing"}):
                with self.subTest(tag=tag, props=props):
                    with self.assertRaises(ValueError):
                        LeafNode(tag, None, props=props).to_html()

    def test_repr_includes_tag_value_and_props(self):
        self.assertEqual(repr(LeafNode(None, "Text")), "LeafNode(None, Text, None)")
        self.assertEqual(
            repr(LeafNode("p", "Text", props={"id": "intro"})),
            "LeafNode(p, Text, {'id': 'intro'})",
        )


class TestParentNode(unittest.TestCase):
    def test_constructor_passes_children_and_props_to_htmlnode(self):
        children = [LeafNode("p", "Hello")]
        props = {"id": "main"}
        node = ParentNode("section", children, props)

        self.assertIsInstance(node, HTMLNode)
        self.assertEqual(node.tag, "section")
        self.assertIsNone(node.value)
        self.assertEqual(node.children, children)
        self.assertEqual(node.props, props)

    def test_renders_single_child_without_props(self):
        children = [LeafNode("p", "Hello")]
        nodes = (
            ParentNode("div", children),
            ParentNode("div", children, props=None),
            ParentNode("div", children, props={}),
        )
        for node in nodes:
            with self.subTest(props=node.props):
                self.assertEqual(node.to_html(), "<div><p>Hello</p></div>")

    def test_renders_props_on_parent_and_child(self):
        node = ParentNode(
            "div",
            [LeafNode("a", "Read more", props={"href": "/about"})],
            props={"id": "main", "data-label": ""},
        )

        self.assertEqual(
            node.to_html(),
            '<div id="main" data-label=""><a href="/about">Read more</a></div>',
        )

    def test_preserves_child_order_and_text_spacing(self):
        children = [
            LeafNode(None, "Žilina "),
            LeafNode("strong", "&"),
            LeafNode(None, " Košice\n"),
            LeafNode("span", ""),
        ]

        self.assertEqual(
            ParentNode("div", children).to_html(),
            "<div>Žilina <strong>&</strong> Košice\n<span></span></div>",
        )

    def test_renders_nested_parents_with_siblings(self):
        item = ParentNode("li", [LeafNode(None, "One")])
        items = ParentNode("ul", [item, LeafNode("li", "Two")])
        node = ParentNode("section", [LeafNode("h2", "List"), items])

        self.assertEqual(
            node.to_html(),
            "<section><h2>List</h2><ul><li>One</li><li>Two</li></ul></section>",
        )

    def test_repeated_child_renders_at_each_position(self):
        child = LeafNode("li", "Same")
        node = ParentNode("ul", [child, child])

        self.assertEqual(node.to_html(), "<ul><li>Same</li><li>Same</li></ul>")

    def test_accepts_child_that_renders_empty_text(self):
        node = ParentNode("div", [LeafNode(None, "")])

        self.assertEqual(node.to_html(), "<div></div>")

    def test_rejects_missing_or_empty_tag(self):
        for tag in (None, ""):
            with self.subTest(tag=tag):
                node = ParentNode(tag, [LeafNode(None, "Text")])
                with self.assertRaisesRegex(ValueError, "tag"):
                    node.to_html()

    def test_rejects_missing_or_empty_children(self):
        for children in (None, []):
            with self.subTest(children=children):
                node = ParentNode("div", children)
                with self.assertRaisesRegex(ValueError, "children"):
                    node.to_html()

    def test_propagates_child_rendering_errors(self):
        cases = (
            (LeafNode("span", None), "value"),
            (ParentNode(None, [LeafNode(None, "Text")]), "tag"),
            (ParentNode("section", []), "children"),
        )
        for child, message in cases:
            with self.subTest(child=child):
                node = ParentNode("div", [LeafNode(None, "Before"), child])
                with self.assertRaisesRegex(ValueError, message):
                    node.to_html()


if __name__ == "__main__":
    unittest.main()
