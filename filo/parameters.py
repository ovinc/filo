"""Base classes for display / transform / analysis parameters"""

from abc import ABC, abstractmethod

class ParameterBase:
    """Base class to define common methods for different parameters."""

    def __init__(self, data_series):
        """Init parameter object.

        Parameters
        ----------
        data_series : filo.DataSeries or subclass
            object describing the data series to work with
        """
        self.data_series = data_series
        self.data = {}

    def __repr__(self):
        return f'{self.name.capitalize()} {self.data}'

    def reset(self):
        """Reset parameter data (e.g. rotation angle zero, ROI = total image, etc.)"""
        self.data = {}

    @property
    def is_empty(self):
        return not self.data

    @property
    def is_active(self):
        return not self.is_empty

    # ============================= To subclass ==============================

    @property
    @abstractmethod
    def name(self):
        """Must define a property or class attribute name (str)"""
        pass


class TransformParameterBase(ParameterBase):
    """Base class for global transorms on image series (rotation, crop etc.)

    These parameters DO impact analysis and are stored in metadata.
    """
    @property
    def order(self):
        # Order in which transform is applied if several transforms defined
        transform_list = list(self.data_series.transforms)
        return transform_list.index(self.name)

    def reset(self):
        """Reset parameter data (e.g. rotation angle zero, ROI = total image, etc.)"""
        self.data = {}
        self._update_others()

    def _update_others(self):
        """What to do to all other parameters and caches when the current
        parameter is updated"""
        self.data_series.clear_cache('transforms')
        for transform_name in self.data_series.active_transforms:
            transform = getattr(self.data_series, transform_name)
            if not transform.is_empty and self.order < transform.order:
                transform._update_parameter()

    # ============================= To subclass ==============================

    @abstractmethod
    def apply(self, data):
        """How to apply the transform on data

        To be defined in subclasses.

        Parameters
        ----------
        data : Any
            input data on which to apply the transform

        Returns
        -------
        Any
            the processed data
        """
        pass

    def _update_parameter(self):
        """What to do to current parameter if another parameter is updated.

        (only other parameters earlier in the order of transforms will be
        considered, see self._update_others())
        [optional]
        """
        pass


class CorrectionParameterBase(ParameterBase):
    """Prameter for corrections (flicker, shaking, etc.) on image series"""

    @abstractmethod
    def apply(self, data, num):
        """How to apply the correction on data

        To be defined in subclasses.

        Parameters
        ----------
        data : Any
            input data on which to apply the transform

        num : int
            the data identifier

        Returns
        -------
        Any
            the processed data
        """
        pass