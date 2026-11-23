import unittest

from inline.node_split import split_nodes_delimiter, split_nodes_image, split_nodes_link
from textnode import TextNode, TextType


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_splits_each_supported_inline_delimiter(self):
        cases = (
            ("**", TextType.BOLD),
            ("_", TextType.ITALIC),
            ("`", TextType.CODE),
        )
        for delimiter, text_type in cases:
            with self.subTest(delimiter=delimiter):
                self.assertEqual(
                    split_nodes_delimiter(
                        [TextNode(f"Before {delimiter}Žilina{delimiter} after\n", TextType.TEXT)],
                        delimiter,
                        text_type,
                    ),
                    [
                        TextNode("Before ", TextType.TEXT),
                        TextNode("Žilina", text_type),
                        TextNode(" after\n", TextType.TEXT),
                    ],
                )

    def test_splits_multiple_spans_at_start_and_end(self):
        nodes = [TextNode("**first** between **last**", TextType.TEXT)]

        self.assertEqual(
            split_nodes_delimiter(nodes, "**", TextType.BOLD),
            [
                TextNode("first", TextType.BOLD),
                TextNode(" between ", TextType.TEXT),
                TextNode("last", TextType.BOLD),
            ],
        )

    def test_adjacent_spans_do_not_create_empty_text_nodes(self):
        nodes = [TextNode("**first****second**", TextType.TEXT)]

        self.assertEqual(
            split_nodes_delimiter(nodes, "**", TextType.BOLD),
            [TextNode("first", TextType.BOLD), TextNode("second", TextType.BOLD)],
        )

    def test_empty_span_is_skipped_without_changing_surrounding_text(self):
        nodes = [TextNode("before****after", TextType.TEXT)]

        self.assertEqual(
            split_nodes_delimiter(nodes, "**", TextType.BOLD),
            [TextNode("before", TextType.TEXT), TextNode("after", TextType.TEXT)],
        )

    def test_empty_inputs_produce_no_nodes(self):
        for nodes in ([], [TextNode("", TextType.TEXT)], [TextNode("****", TextType.TEXT)]):
            with self.subTest(nodes=nodes):
                self.assertEqual(split_nodes_delimiter(nodes, "**", TextType.BOLD), [])

    def test_preserves_text_without_the_exact_delimiter(self):
        nodes = [TextNode("Keep *asterisks* and _underscores_.", TextType.TEXT)]

        self.assertEqual(split_nodes_delimiter(nodes, "**", TextType.BOLD), nodes)

    def test_preserves_formatted_nodes_and_order_across_inputs(self):
        link = TextNode("**unmatched", TextType.LINK, "/about")
        code = TextNode("**literal**", TextType.CODE)
        nodes = [
            TextNode("**first**", TextType.TEXT),
            link,
            TextNode("**second**", TextType.TEXT),
            code,
        ]

        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)

        self.assertEqual(
            result,
            [TextNode("first", TextType.BOLD), link, TextNode("second", TextType.BOLD), code],
        )
        self.assertIs(result[1], link)
        self.assertIs(result[3], code)

    def test_rejects_unmatched_delimiters(self):
        for text in ("**", "**open", "close**", "**matched** then **open"):
            with self.subTest(text=text):
                with self.assertRaisesRegex(ValueError, "unmatched delimiter"):
                    split_nodes_delimiter([TextNode(text, TextType.TEXT)], "**", TextType.BOLD)

    def test_delimiters_cannot_pair_across_nodes(self):
        nodes = [TextNode("**start", TextType.TEXT), TextNode("end**", TextType.TEXT)]

        with self.assertRaisesRegex(ValueError, "unmatched delimiter"):
            split_nodes_delimiter(nodes, "**", TextType.BOLD)

    def test_rejects_empty_delimiter_for_text(self):
        with self.assertRaises(ValueError):
            split_nodes_delimiter([TextNode("text", TextType.TEXT)], "", TextType.BOLD)


class TestSplitNodesImageAndLink(unittest.TestCase):
    splitters = (
        (split_nodes_image, "!", TextType.IMAGE),
        (split_nodes_link, "", TextType.LINK),
    )

    def test_splits_text_around_matches_in_order(self):
        for split, prefix, kind in self.splitters:
            with self.subTest(kind=kind):
                text = f"  {prefix}[Žilina](/city?q=1#map) and {prefix}[Two](/two)\n"
                self.assertEqual(
                    split([TextNode(text, TextType.TEXT)]),
                    [
                        TextNode("  ", TextType.TEXT),
                        TextNode("Žilina", kind, "/city?q=1#map"),
                        TextNode(" and ", TextType.TEXT),
                        TextNode("Two", kind, "/two"),
                        TextNode("\n", TextType.TEXT),
                    ],
                )

    def test_adjacent_repeated_matches_skip_empty_text_fragments(self):
        for split, prefix, kind in self.splitters:
            with self.subTest(kind=kind):
                text = f"{prefix}[Same](/same)" * 2
                expected = [TextNode("Same", kind, "/same")] * 2
                self.assertEqual(split([TextNode(text, TextType.TEXT)]), expected)

    def test_empty_label_and_destination(self):
        for split, prefix, kind in self.splitters:
            with self.subTest(kind=kind):
                text = f"{prefix}[](/url){prefix}[Label](){prefix}[]()"
                expected = [
                    TextNode("", kind, "/url"),
                    TextNode("Label", kind, ""),
                    TextNode("", kind, ""),
                ]
                self.assertEqual(split([TextNode(text, TextType.TEXT)]), expected)

    def test_empty_inputs(self):
        for split, _, kind in self.splitters:
            with self.subTest(kind=kind):
                self.assertEqual(split([]), [])
                self.assertEqual(split([TextNode("", TextType.TEXT)]), [])

    def test_preserves_plain_and_malformed_text(self):
        for split, prefix, kind in self.splitters:
            for text in ("Plain text", " \n ", f"{prefix}[Unclosed](/url", f"{prefix}[Label] (/url)"):
                with self.subTest(kind=kind, text=text):
                    nodes = [TextNode(text, TextType.TEXT)]
                    self.assertEqual(split(nodes), nodes)

    def test_preserves_existing_nodes_between_text_inputs(self):
        for split, prefix, kind in self.splitters:
            with self.subTest(kind=kind):
                code = TextNode(f"{prefix}[Literal](/code)", TextType.CODE)
                link = TextNode("Existing", TextType.LINK, "/existing")
                nodes = [
                    TextNode(f"{prefix}[First](/first)", TextType.TEXT),
                    code,
                    link,
                    TextNode(f"{prefix}[Last](/last)", TextType.TEXT),
                ]
                result = split(nodes)
                self.assertEqual(
                    result,
                    [TextNode("First", kind, "/first"), code, link, TextNode("Last", kind, "/last")],
                )
                self.assertIs(result[1], code)
                self.assertIs(result[2], link)

    def test_markup_cannot_span_nodes(self):
        for split, prefix, kind in self.splitters:
            with self.subTest(kind=kind):
                nodes = [
                    TextNode(f"{prefix}[Label]", TextType.TEXT),
                    TextNode("(/url)", TextType.TEXT),
                ]
                self.assertEqual(split(nodes), nodes)

    def test_distinguishes_images_and_links_with_identical_markup(self):
        nodes = [TextNode("![Same](/same)[Same](/same)", TextType.TEXT)]

        self.assertEqual(
            split_nodes_image(nodes),
            [TextNode("Same", TextType.IMAGE, "/same"), TextNode("[Same](/same)", TextType.TEXT)],
        )
        self.assertEqual(
            split_nodes_link(nodes),
            [TextNode("![Same](/same)", TextType.TEXT), TextNode("Same", TextType.LINK, "/same")],
        )
