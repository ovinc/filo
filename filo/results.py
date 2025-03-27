"""Base class to manage analysis results and save/load data/metadata."""


from pathlib import Path
from abc import ABC


class ResultsBase(ABC):
    """Base class for classes that stores results and metadata to files.

    Can be used as is (without subclassing) but won't be able to
    interact with files.
    In order to interact (save/load) with files, define the following methods:
    - _load_data()
    - _save_data()
    - _load_metadata()
    - _save_metadata()
    (see below)
    """
    # define in subclass (e.g. 'Img_GreyLevel')
    # Note that the program will add extensions depending on context
    # (data or metadata).
    default_filename = 'Results'
    data_extension = '.tsv'
    metadata_extension = '.json'

    def __init__(self, savepath='.'):
        """Init Results object

        Parameters
        ----------
        savepath : str or pathlib.Path object
            folder in which results are saved
        """
        self.reset()  # creates self.data and self.metadata
        self.savepath = Path(savepath)

    def _set_filename(self, filename):
        """Return default filename if filename is None, or filename input

        Parameters
        ----------
        filename : str
            File name without extension

        Returns
        -------
        str
            file name
        """
        return self.default_filename if filename is None else filename

    def _set_filepath(self, filename, kind):
        """Return file depending on input filename and kind (data or metadata)

        Parameters
        ----------
        filename : str
            File name without extension

        Returns
        -------
        pathlib.Path
            file path
        """
        if kind == 'data':
            extension = self.data_extension
        elif kind == 'metadata':
            extension = self.metadata_extension
        else:
            raise ValueError(
                f'{kind} not a valid kind (should be data or metadata)'
            )
        return self.savepath / (self._set_filename(filename) + extension)

    def reset(self):
        """Erase data and metadata from the results."""
        self.data = None
        self.metadata = {}

    # ============= Global methods that load/save data/metadata ==============

    def save(self, filename=None):
        """Save analysis data and metadata into .tsv / .json files.

        Parameters
        ----------
        filename : str

            If filename is not specified, use default filenames.

            If filename is specified, it must be an str without the extension
            e.g. filename='Test' will create Test.tsv and Test.json files,
            containing tab-separated data file and metadata file, respectively.

        Returns
        -------
        None
        """
        self.save_data(data=self.data, filename=filename)
        self.save_metadata(metadata=self.metadata, filename=filename)

    def load(self, filename=None):
        """Load analysis data and metadata and stores it in self.data/metadata.

        Parameters
        ----------
        filename : str

            If filename is not specified, use default filenames.

            If filename is specified, it must be an str without the extension
            e.g. in the case of using json and csv/tsv,
            filename='Test' will create Test.tsv and Test.json files,
            containing tab-separated data file and metadata file, respectively.

        Returns
        -------
        None
            But stores data and metadata in self.data and self.metadata
        """
        self.data = self.load_data(filename=filename)
        self.metadata = self.load_metadata(filename=filename)

    # ==== More specific methods that load/save metadata and return them =====

    def load_data(self, filename=None):
        """Load analysis data from file and return it as pandas DataFrame.

        Parameters
        ----------
        filename : str

            If filename is not specified, use default filenames.

            If filename is specified, it must be an str without the extension,
            e.g. in the case of using json and csv/tsv,
            filename='Test' will load from Test.tsv.

        Returns
        -------
        Any
            Data in the form specified by user in _load_data()
            Typically a pandas dataframe.
        """
        filepath = self._set_filepath(filename, kind='data')
        return self._load_data(filepath=filepath)

    def save_data(self, data, filename=None):
        """Save analysis data to file.

        Parameters
        ----------
        data : Any
            Data in the form specified by user in _load_data()
            Typically a pandas dataframe.

        filename : str

            If filename is not specified, use default filenames.

            If filename is specified, it must be an str without the extension,
            e.g. in the case of using json and csv/tsv,
            filename='Test' will save to Test.tsv.

        Returns
        -------
        None
        """
        filepath = self._set_filepath(filename, kind='data')
        self._save_data(data=data, filepath=filepath)

    def load_metadata(self, filename=None):
        """Return analysis metadata from file as a dictionary.

        Parameters
        ----------
        filename : str

            If filename is not specified, use default filenames.

            If filename is specified, it must be an str without the extension, e.g.
            filename='Test' will load from Test.json.

        Returns
        -------
        dict
            Metadata in the form of a dictionary
        """
        filepath = self._set_filepath(filename, kind='metadata')
        return self._load_metadata(filepath=filepath)

    def save_metadata(self, metadata, filename=None):
        """Save analysis metadata (dict) to file.

        Parameters
        ----------
        metadata : dict
            Metadata as a dictionary

        filename : str

            If filename is not specified, use default filenames.

            If filename is specified, it must be an str without the extension, e.g.
            filename='Test' will load from Test.json.

        Returns
        -------
        None
        """
        filepath = self._set_filepath(filename, kind='metadata')
        self._save_metadata(metadata=metadata, filepath=filepath)

    # ------------------------------------------------------------------------
    # ===================== To be defined in subclasses ======================
    # ------------------------------------------------------------------------

    def _load_data(self, filepath):
        """Return analysis data from file

        [Optional]

        Parameters
        ----------
        filepath : pathlib.Path object
            file to load the data from

        Returns
        -------
        Any
            Data in the form specified by user in _load_data()
            Typically a pandas dataframe.
        """
        pass

    def _save_data(self, data, filepath):
        """Write data to file

        [Optional]

        Parameters
        ----------
        data : Any
            Data in the form specified by user in _load_data()
            Typically a pandas dataframe.

        filepath : pathlib.Path object
            file to load the metadata from

        Returns
        -------
        None
        """
        pass

    def _load_metadata(self, filepath):
        """Return analysis metadata from file as a dictionary.

        [Optional]

        Parameters
        ----------
        filepath : pathlib.Path object
            file to load the metadata from

        Returns
        -------
        dict
            metadata
        """
        pass

    def _save_metadata(self, metadata, filepath):
        """Write metadata to file

        [Optional]

        Parameters
        ----------
        metadata : dict
            Metadata as a dictionary

        filepath : pathlib.Path object
            file to load the metadata from

        Returns
        -------
        None
        """
        pass
