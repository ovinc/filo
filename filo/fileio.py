"""File Management."""

import json

# ================== Functions for json saving and reading ===================


def load_json(filepath):
    """"Load json file as a dict.

    Parameters
    ----------
    filepath : pathlib object
        file to load the data from

    Returns
    -------
    dict
    """
    with open(filepath, 'r', encoding='utf8') as f:
        data = json.load(f)
    return data

def to_json(data, filepath):
    """"Save data (dict) to json file.

    Parameters
    ----------
    data : dict
        dictionary of data

    filepath : pathlib object
        file to write the data into

    Returns
    -------
    None
        (writes data to file)
    """
    with open(filepath, 'w', encoding='utf8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# =================== Functions for csv saving and reading ===================


def data_to_line(data, sep='\t'):
    """Transform iterable into line to write in a file, with a separarator."""
    data_str_list = [str(x) for x in data]
    data_str_all = sep.join(data_str_list)
    return data_str_all + '\n'


def line_to_data(line, sep='\t', dtype=float):
    """Inverse of data_to_line(). Returns data as a tuple of type dtype."""
    line_list = line.split(sep)
    data_list = [dtype(x) for x in line_list]
    return tuple(data_list)


def load_csv(filepath, sep=',', skiprows=0):
    """Load csv file into a list of lists, similar to numpy.genfromtxt()

    Parameters
    ----------
    filepath : str or pathlib.Path
    sep : str
    skiprows : int
    """
    data = []
    with open(filepath, 'r') as f:
        for i, line in enumerate(f.readlines()):
            if i < skiprows:
                continue
            data_raw = line.split(sep)
            data.append([x.strip() for x in data_raw])
    return data
