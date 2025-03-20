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
        return f'{self.parameter_name.capitalize()} {self.data}'

    def reset(self):
        """Reset parameter data (e.g. rotation angle zero, ROI = total image, etc.)"""
        self.data = {}

    @property
    def is_empty(self):
        return not self.data

    # ============================= To subclass ==============================

    @property
    @abstractmethod
    def parameter_name(self):
        """Must define a property or class attribute parameter_name (str)"""
        pass


class TransformParameter(ParameterBase):
    """Base class for global transorms on image series (rotation, crop etc.)

    These parameters DO impact analysis and are stored in metadata.
    """
    @property
    def order(self):
        # Order in which transform is applied if several transforms defined
        return self.data_series.transforms.index(self.parameter_name)

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
    def apply(self, img):
        """How to apply the transform on an image array

        To be defined in subclasses.

        Parameters
        ----------
        img : array_like
            input image on which to apply the transform

        Returns
        -------
        array_like
            the processed image
        """
        pass

    def _update_parameter(self):
        """What to do to current parameter if another parameter is updated.

        (only other parameters earlier in the order of transforms will be
        considered, see self._update_others())
        [optional]
        """
        pass


class CorrectionParameter(ParameterBase):
    """Prameter for corrections (flicker, shaking, etc.) on image series"""

    def load(self, filename=None):
        """Load parameter data from .json and .tsv files (with same name).

        Redefine Parameter.load() because here stored as tsv file.
        """
        path = self.data_series.savepath
        fname = CONFIG['filenames'][self.parameter_name] if filename is None else filename
        try:  # if there is metadata, load it
            filepath = path / (fname + '.json')
            self.data = FileIO.from_json(filepath)
        except FileNotFoundError:
            self.data = {}
        self.data['correction'] = FileIO.from_tsv(filepath=path + (fname + '.tsv'))
