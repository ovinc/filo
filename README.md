## General information

**filo** is a Python 3 module for file management. It provides the following functions:

```python
list_files(path='.', extension='')  # all files in a folder, sorted by name
list_all(path='.')  # all contents of a folder, sorted by name
move_files(src='.', dst='.', extension='')  # move only files with some suffix
move_all(src='.', dst='.')  # move everything
```
`extension` is optional, to consider only files with a certain extension, e.g. `'.txt'`. If left blank, all files considered (excluding directories).
