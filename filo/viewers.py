"""Viewers to inspect data stored in file series"""

# Nonstandard
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider


class KeyPressSlider(Slider):
    """Slider to inspect images, with keypress response"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._connect_events()
        if self.valstep is None:
            self.keystep = (self.valmax - self.valmin) * 0.01
        else:
            self.keystep = self.valstep

    def _increase_val(self, nstep=1):
        """Increase value by a nstep steps; got to beginning if > valmax"""
        new_val = self.val + nstep * self.keystep
        if new_val > self.valmax:
            new_val = self.valmin
        self.set_val(new_val)

    def _decrease_val(self, nstep=1):
        """Increase value by a nstep steps; got to beginning if > valmax"""
        new_val = self.val - nstep * self.keystep
        if new_val < self.valmin:
            new_val = self.valmax
        self.set_val(new_val)

    def _connect_events(self):
        self.cid_keypressk = self.ax.figure.canvas.mpl_connect(
            'key_press_event',
            self._on_key_press,
        )

    def _on_key_press(self, event):
        if event.key == 'right':
            self._increase_val()
        if event.key == 'left':
            self._decrease_val()
        if event.key == 'up':
            self._increase_val(nstep=10)
        if event.key == 'down':
            self._decrease_val(nstep=10)


class DataViewerBase:
    """Base class for data inspection from file series with matplotlib"""

    def __init__(self):
        """Init Image Viewer"""
        self.plot_init_done = False

        # The parameters below are changed if necessary when methods are called
        self.kwargs = {}
        self.transform = True

    def _create_figure(self):
        """Define in subclass, has to define at least self.fig., and self.axs
        if self.axs is not defined in self._first_plot()
        """
        pass

    def _initialize(self):
        """Anything else to do before first plots"""

    def _get_data(self, num):
        """How to get image / analysis and other data to _plot for each frame.

        Input: image number (int)
        Output: data (arbitrary data format usable by _first_plot() and _update_plot())
        """
        pass

    def _first_plot(self, data):
        """What to do the first time data arrives on the _plot.

        self.updated_artists must be defined here.
        self.axs must be defined here, except if done in self._create_figure()

        Input: data
        """
        pass

    def _update_plot(self, data):
        """What to do upon iterations of the _plot after the first time.

        Input: data
        """
        pass

    @staticmethod
    def _autoscale(ax):
        ax.relim()  # without this, axes limits change don't work
        ax.autoscale(axis='both')

    def _plot(self, num):
        """How to plot data"""
        data = self._get_data(num)

        if not self.plot_init_done:
            self._first_plot(data)
            self.plot_init_done = True
        else:
            self._update_plot(data)

        return self.updated_artists

    def show(self, num=0):
        """Show a single, non-animated image (num: image number)."""
        self._create_figure()
        self._initialize()
        self.plot_init_done = False
        self._plot(num=num)
        return self.axs

    def animate(self, nums, blit=False):
        """Animate an image _plot with a FuncAnimation

        Parameters
        ----------
        nums : iterable of ints
            frames to consider for the animation

        blit : bool
            if True, use blitting for fast rendering
        """
        self._create_figure()
        self._initialize()
        self.plot_init_done = False

        animation = FuncAnimation(
            fig=self.fig,
            func=self._plot,
            frames=nums,
            cache_frame_data=False,
            repeat=False,
            blit=blit,
            init_func=lambda: None,  # prevents calling twice the first num
        )

        return animation

    def inspect(self, nums):
        """Inspect image series with a slider.

        Parameters
        ----------
        nums : iterable of ints
            frames to consider for the animation
        """
        num_min = min(nums)
        num_max = max(nums)

        if num_max > num_min:  # avoids division by 0 error when just 1 image
            num_step = (num_max - num_min) // (len(nums) - 1)
        else:
            num_step = 1

        self._create_figure()
        self._initialize()
        self.plot_init_done = False

        self._plot(num=num_min)

        self.fig.subplots_adjust(bottom=0.1)
        ax_slider = self.fig.add_axes([0.1, 0.01, 0.8, 0.03])

        slider = KeyPressSlider(
            ax=ax_slider,
            label='#',
            valmin=num_min,
            valmax=num_max,
            valinit=num_min,
            valstep=num_step,
            color='steelblue',
            alpha=0.5,
        )

        slider.on_changed(self._plot)

        return slider


class AnalysisViewerBase(DataViewerBase):
    """Matplotlib viewer to display analysis results alongside data"""

    def __init__(self, analysis):
        """Init analysis viewer

        Parameters
        ----------
        analysis : Analysis object
        """
        self.analysis = analysis

        # live = True when viewing actual analysis being made
        # live = False when viewing from results (analysis already performed)
        self.live = False

        super().__init__()

    def _get_data(self, num):
        """Analyses classes should define adequate methods if needed"""
        # Actual anlysis being made, with a live view
        if self.live:
            data = self.analysis.analyze(num, details=True)
            self.analysis._store_data(data)
            return data
        # Post-analysis inspection of results
        else:
            return self._generate_data_from_results(num)

    def _initialize(self):
        """What to do before first plot"""
        if self.live:
            self.cid_close = self.fig.canvas.mpl_connect(
                'close_event',
                self._on_fig_close,
            )
            self.analysis.nums = []
            self.analysis._initialize()

    def _on_fig_close(self, event):
        """This is because we want the analysis (i.e. animation) to finish
        before saving the data in live mode."""
        # if live, it's the _on_fig_close() method of the viewer which takes
        # care of saving the data, because if not, save_results() is called
        # at the beginning of the FuncAnimation (i.e., analysis in this case,
        # and no data is saved)
        if self.live:
            self.analysis._finalize()
            self.live = False

    def _generate_data_from_results(self, num):
        """To subclass"""
        pass


class FormattedAnalysisViewerBase(AnalysisViewerBase):
    """AnalysisViewer for FormattedAnalysis."""

    def _generate_data_from_results(self, num):
        return self.analysis.formatter._generate_data_from_results(num)
