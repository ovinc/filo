"""File Management."""

from .misc import list_files, list_all, move_files, move_all
from .misc import batch_file_rename, make_iterable

from .fileio import load_json, to_json
from .fileio import load_csv, data_to_line, line_to_data

from .file_series import File, FileSeries
from .data_series import DataSeries

from .results import ResultsBase

from .viewers import KeyPressSlider, DataViewerBase, AnalysisViewerBase

from .readers import DataSeriesReaderBase

from .parameters import ParameterBase, TransformParameterBase, CorrectionParameterBase

from .analysis import AnalysisBase

# from importlib.metadata import version  # only for python 3.8+
from importlib_metadata import version

__version__ = version('filo')
