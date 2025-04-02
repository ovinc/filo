"""Tools for multiprocessed analysis of data"""


# Standard library imports
from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor, as_completed

# Nonstandard
from tqdm import tqdm


class Multiprocess(ABC):
    """Multiprocessing with waitbar"""

    def __init__(
        self,
        func,
        post_func=None,
        nprocess=None,
    ):
        """Start analysis of data sequence.

        Parameters
        ----------
        func : callable
            The function to be multiprocessed
            Must accept a single parameter that will be passed as a sequence
            in args in run(args), and returns data in any format.

        post_func : callable
            What to do with the output data of func()
            This function is applied on every result returned by the
            multiprocessed function and is itself not multiprocessed.
            Must accept as an argument the data returned by func()

        nprocess : int
            number of process workers; if None (default), use default
            in ProcessPoolExecutor, depends on the number of cores of computer)

        Warning
        -------
            If running on a Windows machine and using the parallel option,
            the function call must not be run during import of the file
            containing the script (i.e. the function must be in a
            `if __name__ == '__main__'` block).
            This is because apparently multiprocessing imports the main
            program initially, which causes recursive problems.
        """
        self.func = func
        self.post_func = post_func
        self.nprocess = nprocess

    def run(self, args):
        """Start multiprocessed analysis

        Parameters
        ----------
        args : array_like
            Sequence of arguments to pass to the multiprocessed func
            (e.g., list of integers corresponding to data identifiers)

        Returns
        -------
        None
            Use the post_func function to extract and store results.
        """
        futures = []

        with ProcessPoolExecutor(max_workers=self.nprocess) as executor:

            for arg in args:
                future = executor.submit(self.func, arg)
                futures.append(future)

            # Waitbar --------------------------------------------------------
            for future in tqdm(as_completed(futures), total=len(args)):
                pass

            # Process / store results ----------------------------------------
            for future in futures:
                data = future.result()
                if self.post_func is not None:
                    self.post_func(data)
