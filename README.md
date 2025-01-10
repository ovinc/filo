About
=====

**filo** is a Python 3 module for file management. Its main purpose is to provide a `Series` class to manage series of files (e.g. series of images or series of spectra), that use a custom `File` class. In particular, file creation time is detected automatically and can be accessed as a *pandas* dataframe.

Some other useful functions for file management are also provided. See summary of functions and classes below, and associated docstrings for details.

Install
=======

```bash
pip install filo
```

Contents
========


`Series` class
--------------

Class to manage series of files of the same type (e.g. image series or spectra series from time-lapse experiments), possibly spread out across multiple folders. The main purpose of the class is to be subclassed in other modules specialized for analysis of specific experiment types, but it can be used as is, i.e. to extract timing info of series of files.

The main idea is that files are attributed a unique identifier (`num`) that starts at 0 in the first folder. Each file is described by an object of the `File` class that stores file path, identifier, and a time attribute.

**Note**: the time attribute is automatically extracted as the creation time of the file (*st_mtime*), but can be overwritten with external information, or can be defined differently by subclassing the `_measure_times()` method.

The list of file objects is accessed through the list `Series.files` containing all `filo.File` objects (`Series.files[i]` is the file object with identifier `num=i`). The correspondence between identifier, actual files, and file times is summarized in the `Series.info` attribute, which is a pandas DataFrame tied to `Series.files`, and which can be saved into a csv file. Loading options also exist to update file data using data stored in external files.


### `Series` Methods
- `save_info()`: save info of files into csv file,
- `load_info()`: load info of files from csv file (overwrites `self.files`),
- `load_time()`: keep current file info but only update time from info in csv file.

### `Series` Attributes and properties

#### Regular attributes
- `folders`: list of folders (`pathlib.Path` objects) across which the file series is spread,
- `files`: list of files (`filo.File` objects, see below); `self.files[num]` is the file of identifier `num`,
- `savepath`: directory in which data extracted/analyzed from files is saved, if applicable,
- `extension`: extension of the files (str).

#### Read-only properties
(derived from regular attributes and methods)
- `info`: pandas DataFrame containing info (number, folder, file, time) time of files; re-calculated every time `self.info` is called and thus reflects changes in `self.files`.
- `duration`: datetime.Timedelta object, time difference between last file and first file in the series


### `File` objects

File objects listed in `Series.files` have the following attributes:
- `file`: Pathlib object of the file,
- `num`: identifier of file within (int). In the series context, `num` starts at 0 in the first folder,
- `time`: stores unix time (float, in seconds) when `Series.set_times()` is called,

with the following additional read-only properties derived from the ones above for convenience
- `folder` Pathlib object of the parent directory containing the file,
- `name`: filename (str).


### Examples

(See **ExampleSeries.ipynb** for examples with actual data).

```python
from filo import Series

# create series object of .png files located in 2 folders img1 and img2 ------
series = Series(paths=['img1', 'img2'], savepath='analysis', extension='.png')

# Access individual files in the file series ---------------------------------
series.files[0]        # first file in the first folder
series.files[55].num   # should always be equal to 55
series.files[10].time  # unix time of file creation

# Manage the infos DataFrame -------------------------------------------------
series.info         # see all file info in form of a pandas DataFrame
series.save_info()  # save info into 'FileSeries_Info.txt' (filename can be specified)

# Update Series.files objects and Series.info --------------------------------
series.load_info('Other_File_Info.txt')  # update all file data using data from external file
series.load_time('Other_File_Info.txt')   # update time information but keep other info
series.save_info('FileSeries_Info_New.txt')  # save updated info into new txt file
```

Misc. Functions
===============

```python
# List files and folders -----------------------------------------------------
list_files(path='.', extension='')  # all files in a folder, sorted by name
list_all(path='.')  # all contents of a folder, sorted by name

# Move files and folders -----------------------------------------------------
move_files(src='.', dst='.', extension='')  # move only files with some suffix
move_all(src='.', dst='.')  # move everything

# Line formatting for csv ----------------------------------------------------
load_csv(file, sep='\t', skiprows=2)  # load csv into list of lists
data_to_line(data, sep='\t')  # iterable data to a line with \n, separated with separator sep.
line_to_data(line, sep='\t', dtype=float) # "Inverse of data_to_line(). Returns data as a tuple of type dtype.

# Misc -----------------------------------------------------------------------
batch_file_rename(name, newname, path='.')  # rename recursively files named name into newname
make_iterable(x):  # Transform non-iterables into a tuple, but keeps iterables unchanged
```
**Note**: `extension` is optional, to consider only files with a certain extension, e.g. `'.txt'`. If left blank, all files considered (excluding directories).


Requirements
============
(installed automatically by pip if necessary)
- python >= 3.6
- pandas (for managing data in `Series` class)
- importlib-metadata

Author
======
Olivier Vincent
(ovinc.py@gmail.com)

License
=======

3-clause BSD (see *LICENSE* file)

