"""Frequency series instance
"""
import control
import numpy as np

class FrequencySeries:
    """Generic frequency series instance
    """
    def __init__(self, f, series):
        """Initiate the series with the frequency and series data.

        Parameters
        ----------
        f: array
            The frequency axis
        series: array or control.xferfcn.TransferFunction
            The frequency series, can be an array or a transfer function that
            has amplitude representing the content of the series.
        """

        self.f = np.array(f)
        if isinstance(series, control.xferfcn.TransferFunction):
            self.series = abs(series.horner(2*np.pi*1j*f)[0][0])
            self.tf = control.tf(series)
        elif isinstance(series, (np.ndarray, list)):
            self.series = np.array(series)
            self.tf = None

    def to_tf(self, **kwargs):
        """Fit the series
        """
        pass
