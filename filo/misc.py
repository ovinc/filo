"""File Management."""


from pathlib import Path


# ========================== Basic File Management ===========================


def list_files(path='.', extension=''):
    """Return list of files with specific extension in path.

    - by default, return all files with any extension.
    - directories are excluded
    - results are sorted by name
    """
    folder = Path(path)
    pattern = '*' + extension
    paths = folder.glob(pattern)
    filepaths = [p for p in paths if p.is_file()]
    return sorted(filepaths)


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
    filepaths = list_files(p1, extension)
    p2.mkdir(exist_ok=True)
    for filepath in filepaths:
        newfilepath = p2 / filepath.name
        filepath.rename(newfilepath)


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


def batch_file_rename(name, newname, path='.'):
    """Change name to newname for all files in path and subdirectories.

    Parameters
    ----------
    name, newname: str
    path: str or path object

    Example
    -------
    batch_file_rename('Test.txt', 'test.txt')
    will rename all files named 'Test.txt' into 'test.txt' in current directory
    and subdirectories.

    Notes
    -----
    - IMPORTANT: before running this function, check all files that will be
    impacted by running list(Path(path).glob(f'**/{name}')).
    - modification, creation dates etc. not changed in the process.
    """
    folder = Path(path)
    filepaths = folder.glob(f'**/{name}')

    for filepath in filepaths:
        newfilepath = filepath.with_name(newname)
        filepath.rename(newfilepath)


# ================================== MISC. ===================================


def make_iterable(x):
    """Transform non-iterables into a tuple, but keeps iterables unchanged."""
    try:
        iter(x)
    except TypeError:
        return x,
    else:
        return x
