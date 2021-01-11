"""Manage Series of experimental data in potentially several folders."""

import os
from pathlib import Path
import datetime

import pandas as pd

from .general import make_iterable, list_files


# ================================= Classes ==================================

class File:
    """Individual file among the series of files. Used by Series"""

    def __init__(self, file, num):
        """Parameters:

         - file: pathlib object linking to the file
         - num: number identifier of the file across all folders
         """
        self.file = file            # Pathlib object
        self.num = num              # identifier (int)
        self.time = None  # stores time when Series._measure_times() is called

    def __repr__(self):
        return f"filo.File #{self.num} [{self.name} in folder '{self.folder}']"

    @property
    def folder(self):
        return self.file.parent

    @property
    def name(self):
        return self.file.name


class Series:
    """Class to manage series of experimental data in one or several folders."""

    name = 'File series'
    info_filename = 'FileSeries_Info.txt'

    def __init__(self, paths='.', extension='', savepath='.'):
        """Init series of spectra object.

        Parameters
        ----------
        - paths can be a string, path object, or a list of str/paths if data
          is stored in multiple folders.
        - extension: extension of files to be considered (e.g. '.txt')
        - savepath: folder in which to save analysis data if applicable.
        """
        self.savepath = Path(savepath)
        self.savepath.mkdir(exist_ok=True)  # create savepath if does not exist.

        if type(paths) is str:
            self.folders = paths,
        else:
            self.folders = make_iterable(paths)
        self.folders = [Path(folder) for folder in self.folders]
        self.extension = extension

        self.times_set = False  # True when file times are set (e.g. by measure_time())

        self.files = self._list_files()  # empty list if no files in folder.
        self._measure_times()             # add creation time info

    def __repr__(self):
        return f"{self.__class__.name} [extension '{self.extension}', "\
               f'folders {[str(folder) for folder in self.folders]}, '\
               f"savepath '{self.savepath}', {len(self.files)} files]"

    # =================== Private methods to get files info ==================

    def _list_files(self):
        """Create list of filo.File objects from files in self.folders.

        Return a list of filo.File objects.
        """
        files = []
        n = 0  # shift in measurement number if multiple folders
        for i_folder, folder in enumerate(self.folders):
            for i_local, file in enumerate(list_files(folder, self.extension)):
                num = i_local + n
                files.append(File(file, num))
            else:
                try:
                    n += i_local + 1
                except UnboundLocalError:  # no data in folder
                    pass
        return files

    def _measure_times(self):
        """Define time (unix) associated with each file (subclass if necessary)."""
        for file in self.files:
            file.time = file.file.stat().st_mtime
        self.times_set = True

    # =========================== Public methods =============================

    @property
    def info(self):
        """Get time of files from creation date (st_mtime).

        Output
        ------
        pandas dataframe with 'num' as index and 'time (unix)', folder, filename
        as columns.
        """
        nums = [file.num for file in self.files]
        filenames = [file.name for file in self.files]
        dirs = [os.path.relpath(f.folder, self.savepath) for f in self.files]

        columns = ['num', 'folder', 'filename']
        info = zip(nums, dirs, filenames)
        data = pd.DataFrame(info, columns=columns)
        data.set_index('num', inplace=True)

        if self.times_set:
            times = [file.time for file in self.files]
            data['time (unix)'] = times

        return data

    def save_info(self, filename=None, sep='\t'):
        """Save info DataFrame (see self.info property) into csv file.

        Use default filename if filename is None, else specified name.
        The file is created in self.savepath (default current directory).
        """
        filename = self.info_filename if filename is None else filename
        data = self.info  # pandas dataframe (see self.times below)
        time_file = Path(self.savepath) / filename
        data.to_csv(time_file, sep=sep)

    def load_info(self, filename=None, sep='\t'):
        """Update files list and infos DataFrame using csv-saved data.

        Data must be saved in a csv file in self.savepath, with csv separator
        `sep`, and with columns (at least) 'num', 'folder', 'filename'.
        If timing info is available (column 'time (unix)'), file.time is set
        as well.

        No output (self.files and self.info are updated).
        """
        filename = self.info_filename if filename is None else filename
        data_file = Path(self.savepath) / filename
        data = pd.read_csv(data_file, sep=sep)
        data.set_index('num', inplace=True)

        # Check if there is time info ----------------------------------------
        try:
            data['time (unix)']
        except KeyError:
            self.times_set = False
        else:
            self.times_set = True

        # Update file information in the list of filo.File objects -----------
        self.files = []
        for num in data.index:
            filename = data.at[num, 'filename']
            foldername = data.at[num, 'folder']
            filepath = self.savepath / foldername / filename
            file = File(filepath, num)
            if self.times_set:
                file.time = data.at[file.num, 'time (unix)']
            self.files.append(file)

    def load_time(self, filename=None, sep='\t'):
        """Same as load_files but updates only times, not file info.

        The data in filename must be csv with as least columns 'num' and
        'time (unix)'. All nums in self.files must be present in the data.
        """
        filename = self.info_filename if filename is None else filename
        data_file = Path(self.savepath) / filename
        data = pd.read_csv(data_file, sep=sep)
        data.set_index('num', inplace=True)

        # Update file information in the list of filo.File objects -----------
        for file in self.files:
            file.time = data.at[file.num, 'time (unix)']

    @property
    def duration(self):
        """Timedelta between timing info of first and last file.

        Output
        ------
        datetime.Timedelta object.
        """
        if self.times_set:
            t = 'time (unix)'
            dt_s = self.info[t].iloc[-1] - self.info[t].iloc[0]
            return datetime.timedelta(seconds=float(dt_s))
        else:
            raise AttributeError('File timing info missing.')
