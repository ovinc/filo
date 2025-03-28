"""Analysis on data series"""

"""Analysis of data series (base class)"""

# Standard library imports
from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor, as_completed

# Nonstandard
from tqdm import tqdm


class AnalysisBase(ABC):
    """Base class for analysis subclasses (GreyLevel, ContourTracking, etc.)."""

    # If results are independent (results from one num do not depend from
    # analysis on other nums), one do not need to re-do the analysis when
    # asking for the same num twice, and parallel computing is possible
    independent_results = False

    def __init__(self, data_series, viewer=None):
        """Initialize Analysis object

        Parameters
        ----------
        data_series : DataSeries
            data series on which the analysis will be run

        viewer : Viewer, optional
            data viewer to do show(), inspect(), animate() etc.
        """
        self.data_series = data_series
        self.viewer = viewer

    def __repr__(self):
        return f"{self.__class__.__name__} analysis on {self.data_series}"

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

            if not self.independent_results:
                raise ValueError(
                    "Parallel computing not available for "
                    f"{self.__class__.__name} because analysis results are"
                    "not independent of each other."
                )

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
        self._save()

    # ==================== Interactive inspection methods ====================

    def _prepare_viewer(self, transform, live, save, **kwargs):
        self.viewer.transform = transform
        self.viewer.kwargs = kwargs
        self.viewer.live = live
        self.viewer.save = save

    def show(
        self,
        num=0,
        transform=True,
        live=False,
        save=False,
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

        live : bool
            if True, run analysis (and store data) during the inspection
            if False, inspect from existing results (analysis already made)

        save : bool
            if True (and live=True), live analyzed data will be saved to
            results in the end ; if not, live analysis is not kept.

        **kwargs
            any keyword-argument to pass to the viewer.
        """
        self._prepare_viewer(transform=transform, live=live, save=save, **kwargs)
        return self.viewer.show(num=num)

    def inspect(
        self,
        start=0,
        end=None,
        skip=1,
        transform=True,
        live=False,
        save=False,
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

        save : bool
            if True (and live=True), live analyzed data will be saved to
            results in the end ; if not, live analysis is not kept.

        **kwargs
            any keyword-argument to pass to the viewer.
        """
        self._prepare_viewer(transform=transform, live=live, save=save, **kwargs)
        return self.viewer.inspect(nums=self.data_series.nums[start:end:skip])

    def animate(
        self,
        start=0,
        end=None,
        skip=1,
        transform=True,
        live=False,
        save=False,
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

        save : bool
            if True (and live=True), live analyzed data will be saved to
            results in the end ; if not, live analysis is not kept.

        blit : bool
            if True, use blitting for faster animation.

        **kwargs
            any keyword-argument to pass to the viewer.
        """
        self._prepare_viewer(transform=transform, live=live, save=save, **kwargs)
        return self.viewer.animate(
            nums=self.data_series.nums[start:end:skip],
            blit=blit,
        )

    # =================== Methods to define in subclasses ====================

    def _initialize(self):
        """Check everything OK before starting analysis & initialize params.

        Define in subclasses (optional)
        """
        pass

    def _store_data(self, data):
        """How to handle data output by analyze()"""
        pass

    def _finalize(self):
        """What to do at the end of the analysis.

        Define in subclasses (optional)
        """
        pass

    def _save(self):
        """How to save results in a data container after _finalize()

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


class FormattedAnalysisBase(AnalysisBase):
    """Analysis that uses Results / Formatter classes to manage generated data

    The Formatter is an interface between the raw results provided by analyze()
    and the Results class.
    """

    def __init__(self, data_series, results, formatter, viewer=None):
        """Init FormattedAnalysis object.

        Parameters
        ----------
        data_series : DataSeries
            data series on which the analysis will be run

        formatter : Formatter
            interface between raw analysis and results class

        viewer : Viewer, optional
            data viewer to do show(), inspect(), animate() etc.
        """
        super().__init__(data_series=data_series, viewer=viewer)
        self.results = results
        self.formatter = formatter

    # ============ Redefinition of AnalysisBase abstract methods =============

    def _initialize(self):
        """Check everything OK before starting analysis & initialize params."""
        self._init_analysis()
        self.formatter._prepare_data_storage()

    def _store_data(self, data):
        """How to handle results spit out by analysis"""
        self.formatter._store_data(data)

    def _save(self):
        """How to save results in a data container"""
        self.formatter._to_results()

    # ================== Abstract methods from AnalysisBase ==================

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
        dict
            data that can be used by formatter._store_data(), with at least
            the key 'num' indicating the data series identifier
        """
        pass

    def _finalize(self):
        """What to do at the end of the analysis.

        Define in subclasses (optional)
        """
        pass

    # ========================= New abstract methods =========================

    def _init_analysis(self):
        """Any necessary initialization outside of data storage preparation

        [OPTIONAL]
        """
        pass

    def _end_analysis(self):
        """Any necessary initialization outside of data storage preparation

        [OPTIONAL]
        """
        pass
