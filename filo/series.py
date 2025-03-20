"""Manage FileSeries of experimental data in potentially several folders."""

import os
import datetime
from pathlib import Path
from collections import OrderedDict

import pandas as pd

from .general import make_iterable, list_files


# ================================= Classes ==================================

class File:
    """Individual file among the series of files. Used by FileSeries"""

    def __init__(self, path, num=None, unix_time=None):
        """Init File object

        Parameters
        ----------

        path : str or pathlib.Path
            file path

        num : int [optional]
            number identifier of the file across all folders

        unix_time : float [optional]
            if None, will be caculated automatically from file modification time
         """
        self.path = Path(path)
        self.num = num

        if unix_time is None:
            self.unix_time = self.get_unix_time()
        else:
            self.unix_time = unix_time

    def __repr__(self):
        return f"filo.File #{self.num} [{self.name} in folder '{self.folder}']"

    def __eq__(self, other):
        condition1 = self.path == other.path
        condition2 = self.num == other.num
        return condition1 & condition2

    def __hash__(self):
        return hash(self.path)

    def get_unix_time(self):
        """Automatically get unix time from file creation/modification time"""
        return self.path.stat().st_mtime

    @property
    def datetime(self):
        """Returns datetime.datetime object from unix_time"""
        if self.unix_time is not None:
            return datetime.datetime.fromtimestamp(self.unix_time)

    @datetime.setter
    def datetime(self, value):
        raise AttributeError(
            'File.datetime not settable ; use File.unix_time instead'
        )

    @property
    def folder(self):
        return self.path.parent

    @property
    def name(self):
        return self.path.name


class FileSeries:
    """Class to manage series of files in one or several folders."""

    def __init__(self, files, refpath='.'):
        """Init file series object.

        Parameters
        ----------
        files : iterable of filo.File objects

        refpath : {str, pathlib.Path}, optional
            reference path from which folders are expressed from in the
            info attribute and when saving to CSV.
        """
        self._files = files
        self.folders = self._list_folders()
        self.refpath = Path(refpath)

    def __repr__(self):
        relative_folders = [
            os.path.relpath(folder, self.refpath) for folder in self.folders
        ]
        return (
            f"{self.__class__} in {self.refpath} / {relative_folders}, "
            f"{len(self._files)} files]"
        )

    def __getitem__(self, key):
        """To make file series indexable and sliceable."""
        return self._files[key]

    # --------------------------- Misc. init tools ---------------------------

    def _list_folders(self):
        """Detect the various folders the files are in from self._files"""
        folders = []
        for file in self._files:
            if file.folder not in folders:
                folders.append(file.folder)
        return folders

    @staticmethod
    def _detect_files(folders, extension):
        """Create list of filo.File objects by automatic detection in folders.

        Used by Files.auto()

        Parameters
        ----------
        folders : iterable of pathlib.Path
        extension : str

        Returns
        -------
        list
            list of filo.File objects.
        """
        files = []
        num = -1
        for folder in folders:
            for filepath in list_files(folder, extension):
                num += 1
                files.append(File(path=filepath, num=num))
        return files

    # ============= Class methods to generate FileSeries objects =============

    @classmethod
    def auto(cls, folders='.', extension='', refpath='.'):
        """Create file series by automatic detection of files in paths or folders

        Parameters
        ----------
        folders : str, pathlib.Path ot iterable of those
            can be a string, path object, or a list of str/paths if data
            is stored in multiple folders.

        extension : str
            extension of files to be considered (e.g. '.txt')

        refpath : {str, pathlib.Path}, optional
            reference path from which folders are expressed from in the
            info attribute and when saving to CSV.

        Returns
        -------
        filo.FileSeries
        """
        if type(folders) is str:
            folders = folders,
        else:
            folders = make_iterable(folders)
        files = cls._detect_files(folders=folders, extension=extension)
        return cls(files=files, refpath=refpath)

    @classmethod
    def from_csv(cls, filepath, sep='\t', refpath='.'):
        """Create file series using information stored in csv file

        The columns need to contian at least 'num', 'folder', 'filename' and
        'time (unix)'.

        Parameters
        ----------
        filepath : {str, pathlib.Path}
            file in which info on the file series is stored

        sep : str
            separator used in the CSV file

        refpath : {str, pathlib.Path}, optional
            reference path from which folders are expressed from in the
            CSV file.

        Returns
        -------
        filo.FileSeries
        """
        files = []
        data = pd.read_csv(filepath, sep=sep).set_index('num')
        for num in data.index:
            filename = data.at[num, 'filename']
            foldername = data.at[num, 'folder']
            unix_time = data.at[num, 'time (unix)']
            filepath = Path(refpath) / foldername / filename
            files.append(File(path=filepath, num=num, unix_time=unix_time))
        return cls(files=files, refpath=refpath)

    # =========================== Public methods =============================

    @property
    def info(self):
        """Dataframe with all file info.

        Returns
        ------
        pandas dataframe with 'num' as index and 'time (unix)', folder, filename
        as columns.
        """
        data = {
            'num': [file.num for file in self._files],
            'folder': [os.path.relpath(f.folder, self.refpath) for f in self._files],
            'filename': [file.name for file in self._files],
            'time (unix)': [file.unix_time for file in self._files],
        }
        return pd.DataFrame(data).set_index('num')

    def to_csv(self, filepath, sep='\t'):
        """Save info DataFrame (see self.info property) into csv file."""
        self.info.to_csv(filepath, sep=sep)

    def update_times(self, filepath, sep='\t'):
        """Update file times using info contained in csv file.

        Only nums present in the csv data will be updated
        """
        time_data = pd.read_csv(filepath, sep=sep).set_index('num')
        for num in time_data.index:
            self._files[num].unix_time = time_data.at[num, 'time (unix)']

    @property
    def duration(self):
        """Timedelta between timing info of first and last file.

        Output
        ------
        datetime.Timedelta object.
        """
        t = self.info['time (unix)']
        dt_s = t.iloc[-1] - t.iloc[0]
        return datetime.timedelta(seconds=float(dt_s))



class DataSeries:
    """Class to manage series of experimental data but not necessarily
    connected to actual files.

    It offers the possibility to define transforms and corrections,
    and to use caching when loading the data.
    It also offers the opportunity to define viewers and data readers.
    """

    def __init__(
        self,
        savepath='.',
        corrections=(),
        transforms=(),
        reader=None,
        viewer=None,
    ):
        """Init data series object.

        Parameters
        ----------
        savepath : {str, pathlib.Path}, optional

        corrections : iterable
            Iterable of correction objects
            (their order indicates the order in which they are applied),

        transforms : iterable
            Iterable of transform objects
            (their order indicates the order in which they are applied)

        reader : subclass of ReaderBase
            object that defines how to read images

        viewer : subclass of ViewerBase
            which viewer to use for show(), inspect() etc.
        """
        self.savepath = Path(savepath)

        self.corrections = OrderedDict()
        self.transforms = OrderedDict()

        for correction in corrections:
            self.corrections[correction.name] = correction
            setattr(self, correction.name, correction)

        for transform in transforms:
            self.transforms[transform.name] = transform
            setattr(self, transform.name, transform)

        self.reader = reader
        self.viewer = viewer

    # ===================== Corrections and  Transforms ======================

    @property
    def active_corrections(self):
        active_corrs = []
        for correction_name, correction in self.corrections.items():
            if not correction.is_empty:
                active_corrs.append(correction_name)
        return active_corrs

    def reset_corrections(self):
        """Reset all active corrections."""
        for correction in self.corrections:
            correction.reset()

    @property
    def active_transforms(self):
        active_corrs = []
        for transform_name, transform in self.transforms.items():
            if not transform.is_empty:
                active_corrs.append(transform_name)
        return active_corrs

    def reset_transforms(self):
        """Reset all active transforms."""
        for transform in self.transforms:
            transform.reset()

    # =========================== Cache management ===========================

    def cache_info(self):
        """cache info of the various caches in place.

        Returns
        -------
        dict
            with the cache info corresponding to 'files' and 'transforms'
        """
        if not self.reader.cache:
            return None
        return {
            name: method.cache_info()
            for name, method in self.reader.cached_methods.items()
        }

    def clear_cache(self, which=None):
        """Clear specified cache.

        Parameters
        ----------
        which : str or None
            can be 'files' or 'transforms'
            (default: None, i.e. clear both)

        Returns
        -------
        None
        """
        if not self.reader.cache:
            return

        if which in ('files', 'transforms'):
            self.reader.cached_methods[which].cache_clear()
        elif which is None:
            for method in self.reader.cached_methods.values():
                method.cache_clear()
        else:
            raise ValueError(f'{which} not a valid cache name.')

    # ============================= Main methods =============================

    def read(self, num=0, correction=True, transform=True, **kwargs):
        """Read and return data of identifier num

        Parameters
        ----------
        num : int
            data identifier

        correction : bool
            By default, if corrections are defined on the image
            (flicker, shaking etc.), then they are applied here.
            Put correction=False to only load the raw image in the stack.

        transform : bool
            By default, if transforms are defined on the image
            (rotation, crop etc.), then they are applied here.
            Put transform=False to only load the raw image in the stack.

        **kwargs
            by default if transform=True, all active transforms are applied.
            Set any transform name to False to not apply this transform.
            e.g. images.read(subtraction=False).

        Returns
        -------
        array_like
            Image data as an array
        """
        return self.reader.read(
            num=num,
            correction=correction,
            transform=transform,
            **kwargs,
        )

    # ==================== Interactive inspection methods ====================

    def show(self, num=0, **kwargs):
        """Show image in a matplotlib window.

        Parameters
        ----------
        num : int
            image identifier in the file series

        **kwargs
            any keyword-argument to pass to the viewer
        """
        return self.viewer.show(num=num, **kwargs)

    def inspect(self, start=0, end=None, skip=1, **kwargs):
        """Interactively inspect image series.

        Parameters
        ----------
        start : int
        end : int
        skip : int
            images to consider. These numbers refer to 'num' identifier which
            starts at 0 in the first folder and can thus be different from the
            actual number in the image filename

        **kwargs
            any keyword-argument to pass to the viewer
        """
        return self.viewer.inspect(nums=self.nums[start:end:skip], **kwargs)

    def animate(self, start=0, end=None, skip=1, blit=False, **kwargs):
        """Interactively inspect image stack.

        Parameters
        ----------
        start : int
        end : int
        skip : int
            images to consider. These numbers refer to 'num' identifier which
            starts at 0 in the first folder and can thus be different from the
            actual number in the image filename

        blit : bool
            use blitting for faster rendering (default False)

        **kwargs
            any keyword-argument to pass to the viewer
        """
        return self.viewer.animate(nums=self.nums[start:end:skip], blit=blit, **kwargs)
