"""Reading data from series of files with transforms and corrections"""

# Standard library
from abc import ABC, abstractmethod
from functools import lru_cache


class DataSeriesReaderBase(ABC):
    """Base class for reading data from series of files and applying modifications

    Modifications can include :
    - transforms : that are the same for every file in the series
    - corrections : that can vary file to file
    """

    def __init__(
        self,
        data_series,
        cache=False,
        read_cache_size=128,
        transform_cache_size=128,
    ):
        """Init DataSeriesReader object

        Parameters
        ----------
        data_series : filo.DataSeries (or subclass)
            series from which to read the data

        cache : bool, optional
            if True, use caching for speed improvement
            (both for loading files and transforms)
            this is useful when calling read() multiple times on the same
            image (e.g. when inspecting series/stacks)

        read_cache_size : int, optional
            How many data readings can be loaded in the cache
            (if cache=True, files/data are read only once and stored in memory
            unless they exceed this limit).
            Prefer using power of 2 for cache efficiency.

        transform_cache_size : int, optional
            The calculation from loaded data into transformed data can also be
            cached : see file_cache_size
        """
        self.data_series = data_series
        self.cache = cache

        if self.cache:
            self._read = lru_cache(maxsize=read_cache_size)(self._read)
            self.read = lru_cache(maxsize=transform_cache_size)(self.read)
            self.cached_methods = {
                'files': self._read,
                'transforms': self.read,
            }
        else:
            self.cached_methods = {}

    def apply_correction(self, data, num, correction_name):
        """Apply specific correction (str) to data and return new data array"""
        correction = getattr(self.data_series, correction_name)
        if correction.is_empty:
            return data
        return correction.apply(data=data, num=num)

    def apply_corrections(self, data, num, **kwargs):
        """Apply stored corrections on the data"""
        for correction_name in self.data_series.corrections:
            # Do not consider any correction specifically marked as False
            if kwargs.get(correction_name, True):
                data = self.apply_correction(
                    data=data,
                    num=num,
                    correction_name=correction_name,
                )
        return data

    def apply_transform(self, data, transform_name):
        """Apply specific transform (str) to data and return new data"""
        transform = getattr(self.data_series, transform_name)
        if transform.is_empty:
            return data
        return transform.apply(data)

    def apply_transforms(self, data, **kwargs):
        """Apply stored transforms on the data"""
        for transform_name in self.data_series.transforms:
            # Do not consider any transform specifically marked as False
            if kwargs.get(transform_name, True):
                data = self.apply_transform(
                    data=data,
                    transform_name=transform_name,
                )
        return data

    def read(self, num, correction=True, transform=True, **kwargs):
        """Read file #num in file series and apply transforms if requested.

        Kwargs can be e.g. rotation=True or threshold=False to switch on/off
        transforms during the processing of the file
        """
        data = self._read(num=num)
        data = self.apply_corrections(data, num, **kwargs) if correction else data
        data = self.apply_transforms(data, **kwargs) if transform else data
        return data

    # ============================= To subclass ==============================

    @abstractmethod
    def _read(self, num):
        """How to read file from series/stack. To be defined in subclasses.

        Parameters
        ----------
        num : int
            file identifier

        Returns
        -------
        array-like
            file as an array (typically np.array)

        Notes
        -----
            Here it takes num and not file, because in certain cases (stacks)
            the files do not exist, and also it is better for caching.
        """
        pass
