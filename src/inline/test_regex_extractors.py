import unittest

from inline.regex_extractors import extract_markdown_images, extract_markdown_links


class TestRegexExtractors(unittest.TestCase):
    def test_extracts_image_alt_text_and_url(self):
        text = "Before ![Žilina skyline](/city.png?size=2#view) after"

        self.assertEqual(
            extract_markdown_images(text),
            [("Žilina skyline", "/city.png?size=2#view")],
        )

    def test_extracts_link_label_and_url(self):
        text = "See [Žilina guide](https://example.com/guide?q=city#map)."

        self.assertEqual(
            extract_markdown_links(text),
            [("Žilina guide", "https://example.com/guide?q=city#map")],
        )

    def test_extractors_distinguish_adjacent_images_and_links(self):
        text = "![One](/one.png)[First](/first)\n[Second](/second)![Two](/two.png)"

        self.assertEqual(
            extract_markdown_images(text), [("One", "/one.png"), ("Two", "/two.png")]
        )
        self.assertEqual(
            extract_markdown_links(text), [("First", "/first"), ("Second", "/second")]
        )

    def test_repeated_matches_are_preserved(self):
        text = "![Alt](img.png) ![Alt](img.png) [Link](/page) [Link](/page)"

        self.assertEqual(extract_markdown_images(text), [("Alt", "img.png")] * 2)
        self.assertEqual(extract_markdown_links(text), [("Link", "/page")] * 2)

    def test_empty_labels_and_destinations(self):
        for prefix, extract in (("!", extract_markdown_images), ("", extract_markdown_links)):
            with self.subTest(extractor=extract.__name__):
                text = f"{prefix}[](/url) {prefix}[Label]() {prefix}[]()"
                self.assertEqual(extract(text), [("", "/url"), ("Label", ""), ("", "")])

    def test_no_matches_for_empty_plain_or_malformed_input(self):
        samples = (
            "",
            "Plain text",
            "[label] ![alt]",
            "[label](url ![alt](url",
            "[label] (url) ![alt] (url)",
            "[a [nested] label](url) ![a [nested] label](url)",
            "[label](url(with-parentheses)) ![alt](url(with-parentheses))",
        )
        for text in samples:
            with self.subTest(text=text):
                self.assertEqual(extract_markdown_images(text), [])
                self.assertEqual(extract_markdown_links(text), [])

    def test_finds_valid_matches_after_malformed_markup(self):
        text = "![broken](missing [good](/page) ![good](/image.png)"

        self.assertEqual(extract_markdown_links(text), [("good", "/page")])
        self.assertEqual(extract_markdown_images(text), [("good", "/image.png")])
