import re
from html import escape
from pathlib import Path

from block.block_to_html import markdown_to_html_node


def extract_title(markdown: str) -> str:
    for line in markdown.splitlines():
        if re.match(r"^#[ \t]+\S", line):
            return line[1:].strip()
    raise ValueError("Markdown must contain an H1 heading")


def generate_page(
    from_path: str | Path, template_path: str | Path, dest_path: str | Path
) -> None:
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    markdown = Path(from_path).read_text(encoding="utf-8")
    template = Path(template_path).read_text(encoding="utf-8")
    replacements = {
        "{{ Title }}": escape(extract_title(markdown), quote=False),
        "{{ Content }}": markdown_to_html_node(markdown).to_html(),
    }
    page = re.sub(r"\{\{ (?:Title|Content) \}\}", lambda match: replacements[match[0]], template)
    destination = Path(dest_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(page, encoding="utf-8")


def generate_pages_recursive(
    dir_path_content: str | Path,
    template_path: str | Path,
    dest_dir_path: str | Path,
) -> None:
    destination = Path(dest_dir_path)
    for entry in sorted(Path(dir_path_content).iterdir()):
        if entry.is_symlink():
            continue
        if entry.is_dir():
            generate_pages_recursive(entry, template_path, destination / entry.name)
        elif entry.is_file() and entry.suffix == ".md":
            generate_page(entry, template_path, destination / entry.with_suffix(".html").name)
