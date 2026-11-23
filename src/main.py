from argparse import ArgumentParser
from pathlib import Path

from copy_static import copy_directory
from page_generator import generate_pages_recursive


def main():
    parser = ArgumentParser()
    parser.add_argument("base_path", nargs="?", default="/")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    copy_directory(root / "static", root / "public")
    generate_pages_recursive(
        root / "content", root / "template.html", root / "public", args.base_path
    )


if __name__ == "__main__":
    main()
