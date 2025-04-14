"""Resample data stored in pandas dataframes

Originally I was using pd.cut but it does not allow to have disjoint and/or
centered bins.
"""


def create_bins_centered_on(values, max_interval=None):
    """Given a list of values (e.g. times), create centered bins around them.

    The values can be non evenly spaced, in which case the minimum interval
    that can yield a centered bin around the values without overlapping
    with the other bins will be chosen.

    For example:
    values                 .     .     .     .                .     .     .
    bins (default)      |     |     |     |     |          |     |     |     |

    Parameters
    ----------
    values : iterable
        typically of floats, but can probably work with datetimes

    max_interval : float
        if supplied, the bins cannot be more than max_interval wide
        if None, use the maximum bin size that prevents overlapping
        between bins.

    Returns
    -------
    list
        list of (v_min, v_max) tuples
    """
    bins = []
    ntot = len(values)
    for i, t in enumerate(values):
        possible_dts = [max_interval] if max_interval is not None else []
        if i > 0:
            possible_dts.append(t - values[i - 1])
        if i < ntot - 1:
            possible_dts.append(values[i + 1] - t)
        dt = min(possible_dts)
        bins.append((t - dt / 2, t + dt / 2))
    return bins


def resample_dataframe(
    dataframe,
    new_index,
    agg='mean',
    max_interval=None,
):
    """Resample dataframe according to new index

    For example, if one has recorded images with a sampling rate different
    than a temperature signal, one can make them match based on their
    'time (unix)' index. The new index must have higher sampling
    rate than the index of the input dataframe.

    The function creates centered bins (t - dt/2, t + dt/2) around each of the
    values (t) of the column in the reference_dataframe, and applies the agg
    method(s) to all points located in that column range in the input dataframe
    to create new values associated with t.

    The function also replaces the index of the dataframe

    For example:
    dataframe         ........................................................
    new_index             .     .     .     .                .     .     .
    bins (default)     |     |     |     |     |          |     |     |     |

    Parameters
    ----------
    dataframe : pandas.DataFrame
        data to reduce

    new_index : pandas.DataFrame.index
        new index with lower sampling rate than dataframe index

    agg : {str, iterable[str]}
        aggregation method(s) ; by default 'mean' to average all points
        in the input dataframe, but can be e.g. 'std', or several functions
        e.g. ['mean', 'std].

    max_interval : float
        (or type of the specified column)
          - if not supplied (None, default), the centered bins have the
            maximum extent that does not overlap with other bins
          - if supplied, the bins cannot be more than max_interval wide.

    Returns
    -------
    pandas.DataFrame
        resampled data

    Notes
    -----
        If dataframe has a column named '_num', it will be removed by
        the present function.
    """
    dataframe['_num'] = -1  # all rows affected -1 will be ignored

    bins = create_bins_centered_on(values=new_index, max_interval=max_interval)

    for i, (vmin, vmax) in enumerate(bins):
        condition = (dataframe.index >= vmin) & (dataframe.index < vmax)
        dataframe.loc[condition, '_num'] = i

    dataframe_gpby = dataframe.groupby('_num', observed=False)
    dataframe_final = dataframe_gpby.agg(agg).drop(-1)

    dataframe_final.index = new_index
    # This is to return the initial dataframe to its initial state
    dataframe.drop('_num', axis=1, inplace=True)

    return dataframe_final
