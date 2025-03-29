"""Tests for filo module."""

import filo
from pathlib import Path
from filo import FileSeries

MODULE_PATH = Path(filo.__file__).parent / '..'
DATA_PATH = MODULE_PATH / 'data'
FILE_INFO = DATA_PATH / 'External_File_Info.txt'
TIME_INFO = DATA_PATH / 'External_Time_Info.txt'

FOLDERS = DATA_PATH / 'img1', DATA_PATH / 'img2'
FILES = FileSeries.auto(folders=FOLDERS, refpath=DATA_PATH,  extension='.png')


def test_series_numbering():
    """Verify numbering of files is ok in multiple folders for files."""
    assert FILES[-1].num == 19


def test_series_info():
    """test generation of infos DataFrame."""
    files = FileSeries.from_csv(FILE_INFO, sep='\t', refpath=DATA_PATH)
    assert round(files.info.at[4, 'time (unix)']) == 1599832405


def test_series_info_update_time():
    """Test loading file data from external file."""
    FILES.update_times(TIME_INFO)
    info = FILES.info
    assert info.at[2, 'time (unix)'] == 1607500504


def test_series_duration():
    """Test calculation of time duration of files."""
    FILES.update_times(TIME_INFO)
    assert round(FILES.duration.total_seconds()) == 38
