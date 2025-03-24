"""Analysis on data series"""

"""Analysis of data series (base class)"""

# Standard library imports
from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor, as_completed

# Nonstandard
from tqdm import tqdm


class AnalysisBase(ABC):
    """Base class for analysis subclasses (GreyLevel, ContourTracking, etc.)."""

    def __init__(self, data_series):
        """Initialize Analysis object

        Parameters
        ----------
        data_series : ImgSeries or ImgStack object
            data series on which the analysis will be run
        """
        self.data_series = data_series

    # ============================ Public methods ============================

    def run(
        self,
        start=0,
        end=None,
        skip=1,
        parallel=False,
        nprocess=None,
    ):
        """Start analysis of data sequence.

        Parameters
        ----------
        start : int
        end : int
        skip : int
            data nums to consider. These numbers refer to 'num' identifier which
            starts at 0 in the first folder and can thus be different from the
            actual number in the data filename

        parallel : bool
            if True, distribute computation across different processes.
            (only available if calculations on each data is independent of
            calculations on the other datas)

        nprocess : int
            number of process workers; if None (default), use default
            in ProcessPoolExecutor, depends on the number of cores of computer)

        Returns
        -------
        None
            but stores results in the results object

        Warning
        -------
            If running on a Windows machine and using the parallel option,
            the function call must not be run during import of the file
            containing the script (i.e. the function must be in a
            `if __name__ == '__main__'` block).
            This is because apparently multiprocessing imports the main
            program initially, which causes recursive problems.
        """
        self._initialize()
        nums = self.data_series.nums[start:end:skip]  # Required nums

        if parallel:  # ================================= Multiprocessing mode

            futures = {}

            with ProcessPoolExecutor(max_workers=nprocess) as executor:

                for num in nums:
                    future = executor.submit(self.analyze, num)
                    futures[num] = future

                # Waitbar ----------------------------------------------------
                futures_list = list(futures.values())
                for future in tqdm(as_completed(futures_list), total=len(nums)):
                    pass

                # Get results ------------------------------------------------
                for num, future in futures.items():
                    data = future.result()
                    self._store_data(data)

        else:  # ============================================= Sequential mode

            for num in tqdm(nums):
                data = self.analyze(num=num)
                self._store_data(data)

        # Finalize -----------------------------------------------------------

        self._finalize()

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
        live=False,
        **kwargs,
    ):
        """Interactively inspect data series.

        Parameters
        ----------
        start : int
        end : int
        skip : int
            data nums to consider. These numbers refer to 'num' identifier which
            starts at 0 in the first folder and can thus be different from the
            actual number in the data filename

        transform : bool
            if True (default), apply active transforms
            if False, load raw data.

        live : bool
            if True, run analysis (and store data) during the inspection
            if False, inspect from existing results (analysis already made)

        **kwargs
            any keyword-argument to pass to the viewer.
        """
        nums = self.data_series.nums[start:end:skip]

        self.viewer.transform = transform
        self.viewer.kwargs = kwargs
        self.viewer.live = live

        return self.viewer.inspect(nums=nums)

    def animate(
        self,
        start=0,
        end=None,
        skip=1,
        transform=True,
        live=False,
        blit=False,
        **kwargs,
    ):
        """Interactively inspect data stack.

        Parameters
        ----------
        start : int
        end : int
        skip : int
            data nums to consider. These numbers refer to 'num' identifier which
            starts at 0 in the first folder and can thus be different from the
            actual number in the data filename

        transform : bool
            if True (default), apply active transforms
            if False, load raw data.

        live : bool
            if True, run analysis (and store data) during the inspection
            if False, inspect from existing results (analysis already made)

        blit : bool
            if True, use blitting for faster animation.

        **kwargs
            any keyword-argument to pass to the viewer.
        """
        nums = self.data_series.nums[start:end:skip]

        self.viewer.transform = transform
        self.viewer.kwargs = kwargs
        self.viewer.live = live

        return self.viewer.animate(nums=nums, blit=blit)

    # =================== Methods to define in subclasses ====================

    def _initialize(self):
        """Check everything OK before starting analysis & initialize params.

        Define in subclasses (optional)
        """
        print('hello')

    def _store_data(self, data):
        """How to handle data output by analyze()"""
        pass

    def _finalize(self):
        """What to do at the end of the analysis.

        Define in subclasses (optional)
        """
        pass

    @abstractmethod
    def analyze(self, num, details=False):
        """Same as _analyze, but with num as input instead of img.

        Parameters
        ----------
        num : int
            number identifier across the data series

        details : bool
            whether to include more details (e.g. for debugging or live view)

        Returns
        -------
        Any
            data that can be used by ._store_data()"""
        pass
