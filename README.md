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

- `set_times()`: goes through all `self.files` and set their `time` attribute by extracting the creation time of the file (unix time),
- `save_times()`: save all file times and other file info into .txt file,
- `load_times()`: return a pandas DataFrame containing info saved in .txt file by `save_times()` (currently, does not impact `self.times` and individual `File.time` of files).

### Attributes and properties

- `folders`: list of folders (`pathlib.Path` objects) across which the file series is spread,
- `files`: list of files (`filo.File` objects, see below),
- `savepath`: directory in which data extracted/analyzed from files is saved, if applicable,
- `extension`: extension of the files (str),
- `times`: pandas DataFrame containing info on time of files, accessible only after `set_times()` has run (note: currently not impacted by a call to `load_times()`).


`File` class
------------

Class describing a single file within a file series. It is used by the `Series` class.

### Attributes

- `file`: Pathlib object of the file,
- `folder` Pathlib object of the parent directory containing the file,
- `name`: filename (str),
- `num`: identifier of file within (int). In the series context, `num` starts at 0 in the first folder,
- `time`: stores unix time (float, in seconds) when `Series.set_times()` is called.


Miscellaneous
=============

Dependencies
------------
- pandas (for saving series data in `Series` class)

Author
------
Olivier Vincent
(olivier.vincent@univ-lyon1.fr)