"""Tests for filo module."""

import filo
from pathlib import Path
from filo import Series

module_path = Path(filo.__file__).parent / '..'
data_path = module_path / 'data'

folders = data_path / 'img1', data_path / 'img2'
series = Series(folders, savepath=data_path, extension='.png')


def test_series_numbering():
    """Verify numbering of files is ok in multiple folders for series."""
    assert series.files[-1].num == 19


def test_series_info():
    """test generation of infos DataFrame."""
    series.load_info('External_File_Info.txt')
    info = series.info
    assert round(info.at[4, 'time (unix)']) == 1599832405


def test_series_info_overwrite():
    """Test loading file data from external file."""
    series.load_info('External_File_Info.txt')
    info = series.info
    assert info.at[2, 'time (unix)'] == 1599832401


def test_series_info_update_time():
    """Test loading file data from external file."""
    series.load_time('External_Time_Info.txt')
    info = series.info
    assert info.at[2, 'time (unix)'] == 1607500504


def test_series_duration():
    """Test calculation of time duration of series."""
    series.load_time('External_Time_Info.txt')
    assert round(series.duration.total_seconds()) == 38
