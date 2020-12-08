General information
===================

**filo** is a Python 3 module for file management. It provides the various functions and a `Series` class to manage series of files (e.g. series of images or series of spectra), that use a custom `File` class. See summary of functions and classes below, and associated docstrings for details.

Install
-------

### Method 1

In a terminal:
```bash
pip install git+https://cameleon.univ-lyon1.fr/ovincent/filo
```

### Method 2

- Clone the project or download directly the files into a folder.
- In a terminal, `cd` into the project or folder, where the __setup.py__ is, then
```bash
pip install .
```
(use the `-e` option to install in editable mode).


Contents
========

Functions
---------

```python
list_files(path='.', extension='')  # all files in a folder, sorted by name
list_all(path='.')  # all contents of a folder, sorted by name
move_files(src='.', dst='.', extension='')  # move only files with some suffix
move_all(src='.', dst='.')  # move everything
batch_file_rename(name, newname, path='.')  # rename recursively files named name into newname
data_to_line(data, sep='\t')  # transform iterable data into a line with \n at the end and separated with separator sep.
line_to_data(line, sep='\t', dtype=float) # "Inverse of data_to_line(). Returns data as a tuple of type dtype.
```
`extension` is optional, to consider only files with a certain extension, e.g. `'.txt'`. If left blank, all files considered (excluding directories).


`Series` class
--------------

Class to manage series of files of the same type (e.g. image series or spectra series from time-lapse experiments), possibly spread out across multiple folders. The main purpose of the class is to be subclassed in other modules specialized for analysis of specific experiment types.

### Methods
- `save_info()`: save info of files into csv file,
- `load_info()`: load info of files from csv file (overwrites `self.files`),
- `load_time()`: keep current file info but only update time from info in csv file.

### Attributes and properties

#### Regular attributes
- `folders`: list of folders (`pathlib.Path` objects) across which the file series is spread,
- `files`: list of files (`filo.File` objects, see below); `self.files[num]` is the file of identifier `num`,
- `savepath`: directory in which data extracted/analyzed from files is saved, if applicable,
- `extension`: extension of the files (str).

#### Read-only properties
(derived from regular attributes and methods)
- `info`: pandas DataFrame containing info (number, folder, file, time) time of files; re-calculated every time `self.info` is called and thus reflects changes in `self.files`.


### `File` class

Class describing a single file within a file series and used by the `Series` class.

#### Regular attributes
- `file`: Pathlib object of the file,
- `num`: identifier of file within (int). In the series context, `num` starts at 0 in the first folder,
- `time`: stores unix time (float, in seconds) when `Series.set_times()` is called.

#### Read-only properties
(derived from regular attributes)
- `folder` Pathlib object of the parent directory containing the file,
- `name`: filename (str).


### Examples

```python
from filo import Series
series = Series(paths=['img1', 'img2'], savepath='analysis')
series.info         # see all file info in form of a pandas DataFrame
series.save_info()  # save info into 'File_Info.txt' (filename can be specified)
series.files[10].time  # unix time of file creation
series.load_info('Other_File_Info.txt')  # update file data from other file
series.load_time('Time_File_Info.txt')  # keep file data but update time
```



Miscellaneous
=============

Dependencies
------------
- pandas (for saving series data in `Series` class)

Author
------
Olivier Vincent
(olivier.vincent@univ-lyon1.fr)