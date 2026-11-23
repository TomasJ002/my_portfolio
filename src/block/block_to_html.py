from htmlnode import ParentNode
from textnode import TextNode, TextType, text_node_to_html_node
from inline.text_converter import text_to_textnodes
from .blocktype import BlockType, block_to_block_type
from .markdown_converter import markdown_to_blocks

def text_to_children(text: str) -> list:
    text_nodes = text_to_textnodes(text)
    children = []

    for node in text_nodes:
        children.append(text_node_to_html_node(node))

    return children

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        block_type = block_to_block_type(block)
        
        if block_type == BlockType.PARAGRAPH:
            text = block.replace("\n", " ")
            node = ParentNode("p", text_to_children(text))

        elif block_type == BlockType.HEADING:
            level = len(block) - len(block.lstrip("#"))
            text = block[level + 1:]
            node = ParentNode(f"h{level}", text_to_children(text))

        elif block_type == BlockType.CODE:
            text = block[4:-3]
            text_node = TextNode(text, TextType.TEXT)
            code_node = text_node_to_html_node(text_node)
            node = ParentNode("pre", [
                ParentNode("code", [code_node])
            ])

        elif block_type == BlockType.QUOTE:
            lines = block.split("\n")
            text_lines = []

            for line in lines:
                text_lines.append(line[1:].lstrip())

            text = " ".join(text_lines)
            node = ParentNode("blockquote", text_to_children(text))

        elif block_type == BlockType.UNORDERED_LIST:
            lines = block.split("\n")
            items = []

            for line in lines:
                text = line[2:]
                items.append(ParentNode("li", text_to_children(text)))

            node = ParentNode("ul", items)

        elif block_type == BlockType.ORDERED_LIST:
            lines = block.split("\n")
            items = []

            for line in lines:
                text = line.split(". ", 1)[1]
                items.append(ParentNode("li", text_to_children(text)))

            node = ParentNode("ol", items)

        else:
            raise ValueError("Unknown block type")

        children.append(node)

    return ParentNode("div", children)