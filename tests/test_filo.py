"""Tests for filo module."""

import filo
from pathlib import Path
from filo import Series

module_path = Path(filo.__file__).parent / '..'
data_path = module_path / 'data'

def test_series():
    """Verify numbering of files is ok in multiple folders for series."""
    folders = data_path / 'img1', data_path / 'img2'
    s = Series(folders, extension='.png')
    assert s.files[-1].num == 19
