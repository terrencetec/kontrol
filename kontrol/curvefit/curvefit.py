"""Base class for curve fitting
"""
import numpy as np


class CurveFit:
    """Base class for curve fitting
    """
    def __init__(self, xdata=None, ydata=None,
                 model=None, model_kwargs=None,
                 cost=None, cost_kwargs=None,
                 optimizer=None, ):
        """Constructor

        Parameters
        ----------
        xdata : array or None, optional
            The independent variable data / data on the x axis.
            Defaults to None.
        ydata : array or None, optional
            The dependent variable data / data on the y axis.
            Defaults to None.
        model : func(x: array, args: array, **kwargs) -> array,
        or None, optional
            The model used to fit the data.
            ``args`` in model are an array of parameters that
            define the model.
            Defaults to None
        model_kwargs : dict or None, optional
            Keyword arguments passed to the model.
            Defaults to None.
        cost : kontrol.curvefit.Cost
        or func(args, model, xdata, ydata) -> array
            Cost function.
        xdata: array, ydata: array) -> float
            The cost function to be used to fit the data.
            First argument is a list of parameters that will be passed to
            the model.
            This must be pickleable if multiprocessing is to be used.
            Defaults to None.
        cost_kwargs : dict or None, optional
            Keyword arguments passed to the cost function.
            Defaults to None.
        optimizer : func(func, **kwargs) -> scipy.optimize.OptimizeResult,
        or None optional
            The optimization algorithm use for minimizing the cost function.
        optimizer_kwargs : dict or None, optional
            Keyword arguments passed to the optimizer function.
            Defaults to None.
        """
        self._xdata = None
        self._ydata = None
        self._model = None
        self._model_kwargs = None
        self._cost = None
        self._cost_kwargs = None
        self._optimizer = None
        self._optimizer_kwargs = None
        self.xdata = xdata
        self.ydata = ydata
        self.model = model
        self.model_kwargs = model_kwargs
        self.cost = cost
        self.cost_kwargs = cost_kwargs
        self.optimizer = optimizer
        self.optimizer_kwargs = optimizer_kwargs
        self.optimized_args = None
        self.optimize_result = None

    def fit(self, model_kwargs=None, cost_kwargs=None, optimizer_kwargs=None):
        """Fit the data

        Sets self.optimized_args and self.optimize_result.

        Parameters
        ----------
        model_kwargs : dict or None, optional
            Overriding keyword arguments in self.model_kwargs.
            Defaults to None.
        cost_kwargs : dict or None, optional
            Overriding keyword arguments in self.cost_kwargs.
            Defaults to None.
        optimizer_kwargs : dict or None, optional
            Overriding keyword argumetns in self.optimizer_kwargs.
            Defaults to None.

        Returns
        -------
        scipy.optimizer.OptimizeResult
        """
        if model_kwargs is None:
            model_kwargs = self.model_kwargs
        if cost_kwargs is None:
            cost_kwargs = self.cost_kwargs
        if optimizer_kwargs is None:
            optimizer_kwargs = self.optimizer_kwargs

        cost = self.cost
        model = self.model
        xdata = self.xdata
        ydata = self.ydata
        kwargs = optimizer_kwargs
        res = self.optimizer(
            cost, args=(model, model_kwargs, xdata, ydata), **optimizer_kwargs)

        self.optimize_result = res
        self.optimized_args = res.x
        return res

    @property
    def xdata(self):
        """The independent variable data."""
        return self._xdata

    @xdata.setter
    def xdata(self, _xdata):
        """xdata setter"""
        self._xdata = _xdata

    @property
    def ydata(self):
        """The dependent variable data"""
        return self._ydata

    @ydata.setter
    def ydata(self, _ydata):
        """ydata setter"""
        self._ydata = _ydata

    @property
    def model(self):
        """The model used to fit the data."""
        return self._model

    @model.setter
    def model(self, _model):
        """model setter"""
        self._model = model

    @property
    def model_kwargs(self):
        """Keyword arguments passed to the model."""
        return self._model_kwargs

    @model_kwargs.setter
    def model_kwargs(self, _model_kwargs):
        """model_kwargs setter"""
        if _model_kwargs is None:
            self._model_kwargs = {}
        else:
            self._model_kwargs = _model_kwargs

    @property
    def cost(self):
        """The cost function to be used to fit the data."""
        return self._cost

    @cost.setter
    def cost(self, _cost):
        """cost setter"""
        self._cost = _cost

    @property
    def cost_kwargs(self):
        """Keyword arguments passed to the cost function."""
        return self._cost_kwargs

    @cost_kwargs.setter
    def cost_kwargs(self, _cost_kwargs):
        """cost_kwargs setter"""
        if _cost_kwargs is None:
            self._cost_kwargs = {}
        else:
            self._cost_kwargs = _cost_kwargs

    @property
    def optimizer(self):
        """The optimizer function to be used to fit the data."""
        return self._optimizer

    @optimizer.setter
    def optimizer(self, _optimizer):
        """optimizer setter"""
        self._optimizer = _optimizer

    @property
    def optimizer_kwargs(self):
        """Keyword arguments passed to the optimizer function."""
        return self._optimizer_kwargs

    @optimizer_kwargs.setter
    def optimizer_kwargs(self, _optimizer_kwargs):
        """optimizer_kwargs setter"""
        if _optimizer_kwargs is None:
            self._optimizer_kwargs = {}
        else:
            self._optimizer_kwargs = _optimizer_kwargs
