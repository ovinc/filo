"""Base class to manage analysis results and save/load data/metadata."""


from pathlib import Path


class ResultsBase:
    """Base class for classes that stores results and metadata to files.

    Can be used as is (without subclassing) but won't be able to
    interact with files.
    In order to interact (save/load) with files, define the following methods:
    - _load_data()
    - _save_data()
    - _load_metadata()
    - _save_metadata()
    OR if not using the default load and save methods defined below,
    use the custom names instead
    (see below)
    """
    # define in subclass (e.g. 'Img_GreyLevel')
    # Note that the program will add extensions depending on context
    # (data or metadata).
    default_filename = 'Results'

    # Define type of data (e.g. data / metadata and corresponding extensions)
    # Possible to change in subclasses.
    # Possible to put
    extensions = {
        'data': ('.tsv',),
        'metadata': ('.json',),
    }

    # What to add to the default filename or specified filename
    # needs to be same length as extensions above.
    # useful if two extensions are the same, to distinguish filenames
    filename_adds = {
        'data': ('',),
        'metadata': ('',),
    }

    # Corresponding loading and saving methods, possibility to put several
    # in order to save data to various files or different formats.
    # Must be same length as extensions above.
    load_methods = {
        'data': ('_load_data',),
        'metadata': ('_load_metadata',),
    }

    # idem for save methods
    save_methods = {
        'data': ('_save_data',),
        'metadata': ('_save_metadata',),
    }

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

    def _set_filepaths(self, filename, kind):
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
        extensions = self.extensions[kind]
        filename_adds = self.filename_adds[kind]
        filenames = [
            self._set_filename(filename) + filename_add
            for filename_add in filename_adds
        ]
        return [
            self.savepath / (filename + extension)
            for filename, extension in zip(filenames, extensions)
        ]

    # How to initialize data and metadata attributes -------------------------

    def default_data(self):
        """Can be subclassed"""
        return None

    def default_metadata(self):
        """Can be subclassed"""
        return {}

    def reset(self):
        """Erase data and metadata from the results."""
        self.data = self.default_data()
        self.metadata = self.default_metadata()

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

    # ----------------- Common methods used by other methods -----------------

    def _load(self, kind, filename=None):
        """Method used for both load_data and load_metadata, see below)

        kind is 'data' or 'metadata'
        """
        loadmethods = self.load_methods[kind]
        filepaths = self._set_filepaths(filename, kind=kind)
        return [
            getattr(self, loadmethod)(filepath)
            for loadmethod, filepath in zip(loadmethods, filepaths)
        ]

    def _save(self, kind, data, filename=None):
        """Method used for both save_data and save_metadata, see below)

        kind is 'data' or 'metadata'
        """
        savemethods = self.save_methods[kind]
        filepaths = self._set_filepaths(filename, kind=kind)
        for savemethod, filepath in zip(savemethods, filepaths):
            getattr(self, savemethod)(data, filepath)

    # ------------------------------- Loading --------------------------------

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
        loaded_data = self._load('data', filename=filename)
        return self.loaded_data_to_data(loaded_data)

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
        loaded_metadata = self._load('metadata', filename=filename)
        return self.loaded_metadata_to_metadata(loaded_metadata)

    # -------------------------------- Saving --------------------------------

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
        return self._save('data', data=data, filename=filename)

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
        return self._save('metadata', data=metadata, filename=filename)

    # ======== Default loading/saving behavior that can be subclassed ========

    def loaded_data_to_data(self, loaded_data):
        """How to go from the results of load_data into self.data

        Possibility to subclass, by default assumes just one
        data returned that goes directly into self.data
        """
        data, = loaded_data
        return data

    def loaded_metadata_to_metadata(self, loaded_metadata):
        """How to go from the results of load_metadata into self.metadata

        Possibility to subclass, by default assumes just one
        metadata returned that goes directly into self.metadata
        """
        metadata, = loaded_metadata
        return metadata

    # ------------------------------------------------------------------------
    # ===================== To be defined in subclasses ======================
    # ------------------------------------------------------------------------
    # NOTE: the names of the methods below must correspond to the ones
    # defined in the class attributes loadmethods / savedmethods.
    # If changed, this must be changed below as well

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
