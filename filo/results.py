"""Base class to manage analysis results and save/load data/metadata."""


from pathlib import Path
from abc import ABC, abstractmethod


class ResultsBase(ABC):
    """Base class for classes that stores results and metadata to files."""

    # define in subclasses (e.g. 'glevel' or 'ctrack' etc.)
    measurement_type = None

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
        """
        return self.default_filename if filename is None else filename

    def _set_file(self, filename, kind):
        """Return file depending on input filename and kind (data or metadata)

        Parameters
        ----------
        filename : str
            File name without extension
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
        file = self._set_file(filename, kind='data')
        return self._load_data(file=file)

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
        file = self._set_file(filename, kind='data')
        self._save_data(data=data, file=file)

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
        file = self._set_file(filename, kind='metadata')
        return self._load_metadata(file=file)

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
        file = self._set_file(filename, kind='metadata')
        self._save_metadata(metadata=metadata, file=file)

    # ------------------------------------------------------------------------
    # ===================== To be defined in subclasses ======================
    # ------------------------------------------------------------------------

    @abstractmethod
    def _load_data(self, file):
        """Return analysis data from file.

        Parameters
        ----------
        file : pathlib.Path object
            file to load the data from

        Returns
        -------
        Any
            Data in the form specified by user in _load_data()
            Typically a pandas dataframe.
        """
        pass

    @abstractmethod
    def _save_data(self, data, file):
        """Write data to file

        Parameters
        ----------
        data : Any
            Data in the form specified by user in _load_data()
            Typically a pandas dataframe.

        file : pathlib.Path object
            file to load the metadata from

        Returns
        -------
        None
        """
        pass

    @abstractmethod
    def _load_metadata(self, file):
        """Return analysis metadata from file as a dictionary.

        Parameters
        ----------
        file : pathlib.Path object
            file to load the metadata from

        Returns
        -------
        dict
            metadata
        """
        pass

    @abstractmethod
    def _save_metadata(self, metadata, file):
        """Write metadata to file

        Parameters
        ----------
        metadata : dict
            Metadata as a dictionary

        file : pathlib.Path object
            file to load the metadata from

        Returns
        -------
        None
        """
        pass
