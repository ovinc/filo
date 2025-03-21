"""File Management."""

from .general import list_files, list_all, move_files, move_all
from .general import batch_file_rename
from .general import load_csv, data_to_line, line_to_data
from .general import make_iterable

from .series import File, FileSeries, DataSeries

from .results import ResultsBase

from .viewers import KeyPressSlider, DataViewerBase, AnalysisViewerBase

from .readers import DataSeriesReaderBase

from .parameters import ParameterBase, TransformParameterBase, CorrectionParameterBase

from .analysis import AnalysisBase

# from importlib.metadata import version  # only for python 3.8+
from importlib_metadata import version

__version__ = version('filo')
