from enum import Enum

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"
    
def block_to_block_type(block: str) -> BlockType:
    heading_level = 0
    for char in block:
        if char == "#":
            heading_level += 1
        else:
            break

    if 1 <= heading_level <= 6:
        if len(block) > heading_level and block[heading_level] == " ":
            return BlockType.HEADING

    if block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE

    lines = block.split("\n")

    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    ordered = True
    for i, line in enumerate(lines, start=1):
        if not line.startswith(f"{i}. "):
            ordered = False
            break

    if ordered:
        return BlockType.ORDERED_LIST

    # Paragraph
    return BlockType.PARAGRAPH