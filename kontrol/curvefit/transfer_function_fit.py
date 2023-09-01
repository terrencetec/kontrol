"""Transfer function fitting class
"""
import scipy.optimize

from .curvefit import CurveFit
import kontrol.curvefit.cost
import kontrol.curvefit.error_func


class TransferFunctionFit(CurveFit):
    """Transfer function fitting class

    This class is basically a ``CurveFit`` class
    with default cost functions and optimizer
    that is designed for fitting a transfer
    function.
    By default, the error function is
    ``kontrol.curvefit.error_func.tf_error()``.
    The default optimizer is ``scipy.optimize.minimize(
    ...,method="Nelder-Mead",...)``, with
    ``options = {"adaptive": True, "maxiter": N*1000}``,
    where ``N`` is the number of variables.
    All of these can be overridden if specified.

    Parameters
    ----------
    xdata : ``array`` or ``None``, optional
        Independent variable data.
        Defaults to ``None``.
    ydata : ``array`` or ``None``, optional
        Transfer function frequency response in complex numbers.
        Defaults to ``None``.
    model : ``func(x: ``array``, args: ``array``, **kwargs)`` ->\
            ``array``, or ``None``, optional
        The model used to fit the data.
        ``args`` in model is an ``array`` of parameters that
        define the model.
        Defaults to ``None``
    model_kwargs : ``dict`` or ``None``, optional
        Keyword arguments passed to the model.
        Defaults to ``None``.
    cost : kontrol.curvefit.Cost or callable
        Cost function.
        The callable has a signature of
        func(args, model, xdata, ydata) -> array.
        First argument is a list of parameters that will be passed to
        the model.
        This must be pickleable if multiprocessing is to be used.
        Defaults to None.
    weight : ``array`` or ``None``, optional
        Weighting function.
        Defaults ``None``.
    error_func_kwargs : ``dict`` or ``None``, optional
        Keyword arguments the will be passed to ``error_func``,
        which is passed to the construct the cost function.
        Defaults to ``None``.
    optimizer : ``func(func, **kwargs)`` -> ``OptimizeResult``, or ``None``,\
                optional
        The optimization algorithm use for minimizing the cost function.
    optimizer_kwargs : ``dict`` or ``None``, optional
        Keyword arguments passed to the optimizer function.
        Defaults to ``None``.
    options : ``dict`` or ``None``, optional
        The option arguments passed to the ``optimizer``
    x0 : ``array``, optional
        Inital guess.
        Defaults to None.
    """
    def __init__(self, xdata=None, ydata=None,
                 model=None, model_kwargs=None,
                 cost=None, weight=None, error_func_kwargs=None,
                 optimizer=None, optimizer_kwargs=None, options=None,
                 x0=None,):
        """Constructor

        Parameters
        ----------
        xdata : ``array`` or ``None``, optional
            Independent variable data.
            Defaults to ``None``.
        ydata : ``array`` or ``None``, optional
            Transfer function frequency response in complex numbers.
            Defaults to ``None``.
        model : callable or None, optional
            The model used to fit the data.
            The callable has a signature of
            func(x: array, args: array, **kwargs) -> array.
            ``args`` in model is an array of parameters that
            define the model.
            Defaults to None
        model_kwargs : ``dict`` or ``None``, optional
            Keyword arguments passed to the model.
            Defaults to ``None``.
        cost : kontrol.curvefit.Cost or callable
            Cost function.
            The callable has a signature of
            func(args, model, xdata, ydata) -> array.
            First argument is a list of parameters that will be passed to
            the model.
            This must be pickleable if multiprocessing is to be used.
            Defaults to None.
        weight : ``array`` or ``None``, optional
            Weighting function.
            Defaults ``None``.
        error_func_kwargs : ``dict`` or ``None``, optional
            Keyword arguments the will be passed to ``error_func``,
            which is passed to the construct the cost function.
            Defaults to ``None``.
        optimizer : func(func, **kwargs) -> OptimizeResult, or None, optional
            The optimization algorithm use for minimizing the cost function.
        optimizer_kwargs : ``dict`` or ``None``, optional
            Keyword arguments passed to the optimizer function.
            Defaults to ``None``.
        options : ``dict`` or ``None``, optional
            The option arguments passed to the ``optimizer``
        x0 : ``array``, optional
            Inital guess.
            Defaults to None.
        """
        if cost is None:
            error_func = kontrol.curvefit.error_func.tf_error
            default_error_func_kwargs = {"weight": weight}
            if error_func_kwargs is None:
                error_func_kwargs = default_error_func_kwargs
            else:
                error_func_kwargs = dict(
                    default_error_func_kwargs, **error_func_kwargs)
            cost = kontrol.curvefit.cost.Cost(
                error_func=error_func, error_func_kwargs=error_func_kwargs)

        if optimizer is None:
            optimizer = scipy.optimize.minimize

        if x0 is None:
            maxiter = None
        else:
            maxiter = len(x0)*1000
        default_options = {"adaptive": True, "maxiter": maxiter}
        if options is None:
            options = default_options
        else:
            options = dict(default_options, **options)

        default_optimizer_kwargs = {
            "x0": x0, "method": "Nelder-Mead", "options": options}
        if optimizer_kwargs is None:
            optimizer_kwargs = default_optimizer_kwargs
        else:
            if "options" in optimizer_kwargs:
                options = dict(default_options, **optimizer_kwargs["options"])
                optimizer_kwargs["options"] = options
            optimizer_kwargs = dict(
                default_optimizer_kwargs, **optimizer_kwargs)

        super().__init__(
            xdata, ydata, model, model_kwargs,
            cost, optimizer, optimizer_kwargs)

        self._weight = None
        self._options = None
        self._x0 = None
        self.weight = weight
        self.options = options
        self.x0 = x0

    @property
    def weight(self):
        """Weighting function"""
        return self._weight

    @weight.setter
    def weight(self, _weight):
        """weight.setter"""
        self._weight = _weight
        error_func_kwargs = {"weight": self.weight}
        self.cost.error_func_kwargs = dict(
            self.cost.error_func_kwargs, **error_func_kwargs)

    @property
    def options(self):
        """Option arguments passed to optimizer"""
        return self._options

    @options.setter
    def options(self, _options):
        """options.setter"""
        if _options is None:
            self._options = {}
        else:
            self._options = _options
        self._update_optimizer_kwargs()

    @property
    def x0(self):
        """Initial guess"""
        return self._x0

    @x0.setter
    def x0(self, _x0):
        """x0.setter"""
        self._x0 = _x0
        self._update_optimizer_kwargs()

    def _get_maxiter(self):
        """Get `maxiter` option from the initial guess `x0`"""
        # Added this method so we can change the multiplier here.
        if self.x0 is None:
            return None
        else:
            return len(self.x0)*1000

    def _update_optimizer_kwargs(self):
        """Set optimizer_kwargs"""
        if self.x0 is not None:
            update_optimizer_kwargs = {"x0": self.x0}
            self.optimizer_kwargs = dict(
                self.optimizer_kwargs, **update_optimizer_kwargs)
        self._update_options()

    def _update_options(self):
        """Update optimizer options"""
        maxiter = self._get_maxiter()
        update_options = {"maxiter": maxiter}
        if "options" not in self.optimizer_kwargs:
            options = update_options
        else:
            options = dict(self.optimizer_kwargs["options"], **update_options)
        options = dict(options, **self.options)  # self.options have priority
        self.optimizer_kwargs["options"] = options
