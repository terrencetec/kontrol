"""Base class for curve fitting
"""


class CurveFit:
    """Base class for curve fitting

    Parameters
    ----------
    xdata : array or None, optional
        The independent variable data / data on the x axis.
        Defaults to None.
    ydata : array or None, optional
        The dependent variable data / data on the y axis.
        Defaults to None.
    model : callable or None, optional
        The model used to fit the data.
        The callable has a signature of
        func(x: array, args: array, **kwargs) -> array.
        ``args`` in model is an array of parameters that
        define the model.
        Defaults to None
    model_kwargs : dict or None, optional
        Keyword arguments passed to the model.
        Defaults to None.
    cost : kontrol.curvefit.Cost or callable
        Cost function.
        The callable has a signature of
        func(args, model, xdata, ydata) -> array.
        First argument is a list of parameters that will be passed to
        the model.
        This must be pickleable if multiprocessing is to be used.
        Defaults to None.
    optimizer : func(func, **kwargs) -> OptimizeResult, or None, optional
        The optimization algorithm use for minimizing the cost function.
    optimizer_kwargs : dict or None, optional
        Keyword arguments passed to the optimizer function.
        Defaults to None.
    """
    def __init__(self, xdata=None, ydata=None,
                 model=None, model_kwargs=None,
                 cost=None, optimizer=None, optimizer_kwargs=None):
        """Constructor

        Parameters
        ----------
        xdata : array or None, optional
            The independent variable data / data on the x axis.
            Defaults to None.
        ydata : array or None, optional
            The dependent variable data / data on the y axis.
            Defaults to None.
        model : callable or None, optional
            The model used to fit the data.
            The callable has a signature of
            func(x: array, args: array, **kwargs) -> array.
            ``args`` in model is an array of parameters that
            define the model.
            Defaults to None
        model_kwargs : dict or None, optional
            Keyword arguments passed to the model.
            Defaults to None.
        cost : kontrol.curvefit.Cost or callable
            Cost function.
            The callable has a signature of
            func(args, model, xdata, ydata) -> array.
            First argument is a list of parameters that will be passed to
            the model.
            This must be pickleable if multiprocessing is to be used.
            Defaults to None.
        optimizer : func(func, **kwargs) -> OptimizeResult, or None, optional
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
        self._optimizer = None
        self._optimizer_kwargs = None
        self._optimized_args = None
        self._optimize_result = None
        self.xdata = xdata
        self.ydata = ydata
        self.model = model
        self.model_kwargs = model_kwargs
        self.cost = cost
        self.optimizer = optimizer
        self.optimizer_kwargs = optimizer_kwargs
        self.optimized_args = None
        self.optimize_result = None

    def prefit(self):
        """Something to do before fitting."""
        pass

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
        self.prefit()
        if model_kwargs is None:
            model_kwargs = self.model_kwargs
        if optimizer_kwargs is None:
            optimizer_kwargs = self.optimizer_kwargs

        cost = self.cost
        model = self.model
        xdata = self.xdata
        ydata = self.ydata
        optimizer = self.optimizer
        if (cost is None or model is None or xdata is None or ydata is None or
                optimizer is None):
            raise TypeError("Cost, model, xdata, ydata, and optimizer must"
                            " be specified before fitting.")

        res = optimizer(
            cost, args=(model, xdata, ydata, model_kwargs), **optimizer_kwargs)
        self.optimize_result = res
        self.optimized_args = res.x
        self.model.args = self.optimized_args
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
        self._model = _model

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

    @property
    def optimized_args(self):
        """The optimized arguments"""
        return self._optimized_args

    @optimized_args.setter
    def optimized_args(self, _optimized_args):
        """optimized_args setter"""
        self._optimized_args = _optimized_args

    @property
    def optimize_result(self):
        """Optimization Result"""
        return self._optimize_result

    @optimize_result.setter
    def optimize_result(self, _optimize_result):
        """optimize_result setter"""
        self._optimize_result = _optimize_result

    @property
    def yfit(self):
        """The fitted y values"""
        if self.optimized_args is None:
            return None
        else:
            return self.model(
                self.xdata, self.optimized_args, **self.model_kwargs)
