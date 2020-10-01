## General information

**filo** is a Python 3 module for file management. It provides the following functions:

```python
list_files(path='.', extension='')  # all files in a folder, sorted by name
list_all(path='.')  # all contents of a folder, sorted by name
move_files(src='.', dst='.', extension='')  # move only files with some suffix
move_all(src='.', dst='.')  # move everything
data_to_line(data, sep='\t')  # transform iterable data into a line with \n at the end and separated with separator sep.
line_to_data(line, sep='\t', dtype=float) # "Inverse of data_to_line(). Returns data as a tuple of type dtype.
```
`extension` is optional, to consider only files with a certain extension, e.g. `'.txt'`. If left blank, all files considered (excluding directories).

## Install

#### Method 1

In a terminal:
```bash
pip install git+https://cameleon.univ-lyon1.fr/ovincent/files-ov
```

#### Method 2

- Clone the project or download directly the files into a folder.
- In a terminal, `cd` into the project or folder, where the __setup.py__ is, then
```bash
pip install .
```
