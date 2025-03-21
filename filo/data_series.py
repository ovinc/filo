"""Manage FileSeries of experimental data in potentially several folders."""


from pathlib import Path
from collections import OrderedDict

from .fileio import to_json, load_json


class DataSeries:
    """Class to manage series of experimental data but not necessarily
    connected to actual files.

    It offers the possibility to define transforms and corrections,
    and to use caching when loading the data.
    It also offers the opportunity to define viewers and data readers.
    """

    def __init__(
        self,
        savepath='.',
        corrections=(),
        transforms=(),
        reader=None,
        viewer=None,
    ):
        """Init data series object.

        Parameters
        ----------
        savepath : {str, pathlib.Path}, optional

        corrections : iterable
            Iterable of correction objects
            (their order indicates the order in which they are applied),

        transforms : iterable
            Iterable of transform objects
            (their order indicates the order in which they are applied)

        reader : subclass of ReaderBase
            object that defines how to read data

        viewer : subclass of ViewerBase
            which viewer to use for show(), inspect() etc.
        """
        self.savepath = Path(savepath)

        self.corrections = OrderedDict()
        self.transforms = OrderedDict()

        for correction in corrections:
            self.corrections[correction.name] = correction
            setattr(self, correction.name, correction)

        for transform in transforms:
            self.transforms[transform.name] = transform
            setattr(self, transform.name, transform)

        self.reader = reader
        self.viewer = viewer

    def __repr__(self):
        return (
            f"{self.__class__.__name__}, data length [{self.ntot}]\n"
            f"-- corrections: {self.active_corrections}\n"
            f"-- transforms: {self.active_transforms}"
        )

    # ===================== Corrections and  Transforms ======================

    @property
    def active_corrections(self):
        active_corrs = []
        for correction_name, correction in self.corrections.items():
            if not correction.is_empty:
                active_corrs.append(correction_name)
        return active_corrs

    def reset_corrections(self):
        """Reset all active corrections."""
        for correction in self.corrections:
            correction.reset()

    @property
    def active_transforms(self):
        active_corrs = []
        for transform_name, transform in self.transforms.items():
            if not transform.is_empty:
                active_corrs.append(transform_name)
        return active_corrs

    def reset_transforms(self):
        """Reset all active transforms."""
        for transform in self.transforms:
            transform.reset()

    def load_transforms(self, filepath):
        """Load transform parameters (crop, rotation, etc.) from json file.

        Parameters
        ----------
        filepath : {str, pathlib.Path}

        Returns
        -------
        None
            But transforms are applied and stored in attributes, e.g.
            self.rotation, self.crop, etc.
        """
        transform_data = load_json(filepath=filepath)
        for name, transform in self.transforms.items():
            transform.data = transform_data.get(name, {})
            transform._update_parameter()  # if not, subtraction reference is not updated
            transform._update_others()

    def save_transforms(self, filepath):
        """Save transform parameters (crop, rotation etc.) into json file.

        Parameters
        ----------
        filepath : {str, pathlib.Path}

        Returns
        -------
        None
        """
        transform_data = {}
        for transform_name in self.active_transforms:
            transform = getattr(self, transform_name)
            transform_data[transform_name] = transform.data
        to_json(data=transform_data, filepath=filepath)

    # =========================== Cache management ===========================

    def cache_info(self):
        """cache info of the various caches in place.

        Returns
        -------
        dict
            with the cache info corresponding to 'files' and 'transforms'
        """
        if not self.reader.cache:
            return None
        return {
            name: method.cache_info()
            for name, method in self.reader.cached_methods.items()
        }

    def clear_cache(self, which=None):
        """Clear specified cache.

        Parameters
        ----------
        which : str or None
            can be 'files' or 'transforms'
            (default: None, i.e. clear both)

        Returns
        -------
        None
        """
        if not self.reader.cache:
            return

        if which in ('files', 'transforms'):
            self.reader.cached_methods[which].cache_clear()
        elif which is None:
            for method in self.reader.cached_methods.values():
                method.cache_clear()
        else:
            raise ValueError(f'{which} not a valid cache name.')

    # ============================= Main methods =============================

    def read(self, num=0, correction=True, transform=True, **kwargs):
        """Read and return data of identifier num

        Parameters
        ----------
        num : int
            data identifier

        correction : bool
            By default, if corrections are defined on the data
            (flicker, shaking etc.), then they are applied here.
            Put correction=False to only load the raw data in the stack.

        transform : bool
            By default, if transforms are defined on the data
            (rotation, crop etc.), then they are applied here.
            Put transform=False to only load the raw data in the stack.

        **kwargs
            by default if transform=True, all active transforms are applied.
            Set any transform name to False to not apply this transform.
            e.g. data.read(subtraction=False).

        Returns
        -------
        array_like
            Image data as an array
        """
        return self.reader.read(
            num=num,
            correction=correction,
            transform=transform,
            **kwargs,
        )

    # ==================== Interactive inspection methods ====================

    def show(
        self,
        num=0,
        transform=True,
        **kwargs,
    ):
        """Show data in a matplotlib window.

        Parameters
        ----------
        num : int
            data identifier in the file series

        transform : bool
            if True (default), apply active transforms
            if False, load raw data.

        **kwargs
            any keyword-argument to pass to the viewer.
        """
        self.viewer.transform = transform
        self.viewer.kwargs = kwargs
        return self.viewer.show(num=num)

    def inspect(
        self,
        start=0,
        end=None,
        skip=1,
        transform=True,
        **kwargs,
    ):
        """Interactively inspect data series.

        Parameters
        ----------
        start : int
        end : int
        skip : int
            data to consider. These numbers refer to 'num' identifier which
            starts at 0 in the first folder and can thus be different from the
            actual number in the data filename

        transform : bool
            if True (default), apply active transforms
            if False, use raw data.

        **kwargs
            any keyword-argument to pass to the viewer.
        """
        self.viewer.transform = transform
        self.viewer.kwargs = kwargs
        return self.viewer.inspect(nums=self.nums[start:end:skip])

    def animate(self, start=0, end=None, skip=1, transform=True, blit=False, **kwargs):
        """Interactively inspect data stack.

        Parameters
        ----------
        start : int
        end : int
        skip : int
            data to consider. These numbers refer to 'num' identifier which
            starts at 0 in the first folder and can thus be different from the
            actual number in the data filename

        transform : bool
            if True (default), apply active transforms
            if False, use raw data.

        blit : bool
            use blitting for faster rendering (default False)

        **kwargs
            any keyword-argument to pass to the viewer.
        """
        self.viewer.transform = transform
        self.viewer.kwargs = kwargs
        return self.viewer.animate(
            nums=self.nums[start:end:skip],
            blit=blit,
        )

    # =========================== Iteration tools ============================

    @property
    def nums(self):
        """Iterator (sliceable) of data identifiers.

        Define in subclasses

        Examples
        --------
        Allows the user to do e.g.
        >>> for num in data_series.nums[::3]:
        >>>     ...
        """
        pass

    @property
    def ntot(self):
        """Total number of data in the series

        Returns
        -------
        int
        """
        pass
