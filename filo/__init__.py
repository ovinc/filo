"""File Management."""

from pathlib import Path


__version__ = 0.1


def list_files(path='.', extension=''):
    """Return list of files with specific extension in path.

    - by default, return all files with any extension.
    - directories are excluded
    - results are sorted by name
    """
    folder = Path(path)
    pattern = '*' + extension
    paths = folder.glob(pattern)
    files = [p for p in paths if p.is_file()]
    return sorted(files)


def list_all(path='.'):
    """List all contents of a folder, sorted by name."""
    folder = Path(path)
    contents = folder.glob('*')
    return sorted(contents)


def move_files(src='.', dst='.', extension=''):
    """Move all files with a certain extension from folder 1 to folder 2.

    - directories are excluded
    - directory dst is created if not already existing
    """
    p1, p2 = Path(src), Path(dst)
    files = list_files(p1, extension)
    p2.mkdir(exist_ok=True)
    for file in files:
        newfile = p2 / file.name
        file.rename(newfile)


def move_all(src='.', dst='.'):
    """Move all contents of folder 1 into folder 2.

    directory dst is created if not already existing
    """
    p1, p2 = Path(src), Path(dst)
    p2.mkdir(exist_ok=True)
    contents = p1.glob('*')  # I do not use list_all to keep a generator
    for content in contents:
        new_content = p2 / content.name
        content.rename(new_content)
