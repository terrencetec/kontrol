"""Transfer function fitting class
"""
from .curvefit import CurveFit


class TransferFunctionFit(CurveFit):
    """Transfer function fitting class
    """
    def __init__(self, xdata=None, ydata=None,
                 model=None, model_kwargs=None,
                 cost=None, optimizer=None, optimizer_kwargs=None,
                 xunit="Hz"):
        """Constructor

        Parameters
        ----------
        xdata : array or None, optional
            Independent variable data.
            Defaults to None.
        ydata : array or None, optional
            Transfer function frequency response in complex numbers.
            Defaults to None.
        model : func(x: array, args: array, **kwargs) -> array, or None, optional
            The model used to fit the data.
            ``args`` in model is an array of parameters that
            define the model.
            Defaults to None
        model_kwargs : dict or None, optional
            Keyword arguments passed to the model.
            Defaults to None.
        cost : kontrol.curvefit.Cost or func(args, model, xdata, ydata) -> array
            Cost function.
            The cost function to be used to fit the data.
            First argument is a list of parameters that will be passed to
            the model.
            This must be pickleable if multiprocessing is to be used.
            Defaults to None.
        optimizer : func(func, **kwargs) -> OptimizeResult, or None, optional
            The optimization algorithm use for minimizing the cost function.
        optimizer_kwargs : dict or None, optional
            Keyword arguments passed to the optimizer function.
            Defaults to None.
        xunit : str, optional
            The unit of the xdata.
            Choose from ["Hz", "rad/s", "s"].
            Defaults to "Hz".
        """
        super().__init__(
            xdata, ydata, model, model_kwargs,
            cost, optimizer, optimizer_kwargs)
        self._xunit = None
        self.xunit = xunit

    @property
    def xunit(self):
        """The unit of the xdata."""
        return self._xunit

    @xunit.setter
    def xunit(self, _xunit):
        """xunit setter"""
        if _xunit not in ["Hz", "rad/s", "s"]:
            raise ValueError("Invalid specification for xunit. "
                             "Please choose xunit from 'Hz', 'rad/s', or 's'.")
        self._xunit = _xunit
