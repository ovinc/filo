"""Tests for filo module."""

import filo
from pathlib import Path
from filo import FileSeries
import pandas as pd
import numpy as np

MODULE_PATH = Path(filo.__file__).parent / '..'
DATA_PATH = MODULE_PATH / 'data'
ISOTH_PATH = DATA_PATH / 'isotherm'
FILE_INFO = DATA_PATH / 'External_File_Info.txt'
TIME_INFO = DATA_PATH / 'External_Time_Info.txt'

FOLDERS = DATA_PATH / 'img1', DATA_PATH / 'img2'
FILES = FileSeries.auto(folders=FOLDERS, refpath=DATA_PATH,  extension='.png')

pressure_file = ISOTH_PATH / 'ValvePID_Pressure_resampled.tsv'
analysis_file = ISOTH_PATH / 'Spectro_WLI.tsv'
PRESSURE_DATA = pd.read_csv(pressure_file, sep='\t').set_index('time (unix)')
ANALYSIS_DATA = pd.read_csv(analysis_file, sep='\t').set_index('time (unix)')


# ------------------------------- File series --------------------------------


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


# -------------------------------- Resampling --------------------------------


def test_centered_bins():
    bins = filo.create_bins_centered_on(ANALYSIS_DATA.index)
    assert len(bins) == 11
    assert int(bins[3][0]) == 1659008150


def test_resample():
    """Resampling with auto max_interval"""
    df = filo.resample_dataframe(
        dataframe=PRESSURE_DATA.drop('dt (s)', axis=1),
        new_index=ANALYSIS_DATA.index,
        agg=['mean', 'std']
    )
    assert round(df['p (Pa)']['mean'].iloc[-3]) == 2183


def test_resample_short_time():
    """Resampling with max_interval that is short and creates NaN"""
    df = filo.resample_dataframe(
        dataframe=PRESSURE_DATA.drop('dt (s)', axis=1),
        new_index=ANALYSIS_DATA.index,
        max_interval=15,
        agg=['mean', 'std']
    )
    assert np.isnan(df['p (Pa)']['mean'].iloc[-1])
