from pathlib import Path
from shutil import copy2, rmtree


def copy_directory(source: Path, destination: Path) -> None:
    """Replace the destination with a recursive copy of the source directory."""
    if not source.is_dir():
        raise NotADirectoryError(source)

    source_path = source.resolve()
    destination_path = destination.resolve()
    if (
        source_path.is_relative_to(destination_path)
        or destination_path.is_relative_to(source_path)
    ):
        raise ValueError("Source and destination directories must be separate")

    if destination.exists() or destination.is_symlink():
        rmtree(destination)

    _copy_contents(source, destination)


def _copy_contents(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True)
    for entry in source.iterdir():
        target = destination / entry.name
        if not entry.is_symlink() and entry.is_dir():
            _copy_contents(entry, target)
        else:
            print(f"Copying {entry} -> {target}")
            copy2(entry, target, follow_symlinks=False)
