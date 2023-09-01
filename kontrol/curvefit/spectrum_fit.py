"""Spectrum fitting class
"""
import numpy as np
import scipy.optimize

from .curvefit import CurveFit
import kontrol.curvefit.cost
import kontrol.curvefit.error_func
import kontrol.curvefit.model


class SpectrumZPKFit(CurveFit):
    """Spectrum ZPK fitting class

    This class is basically a ``CurveFit`` class
    with default cost functions and optimizer
    that is designed for fitting a spectrum with
    a simple ZPK model.
    By default, the error function is
    ``kontrol.curvefit.error_func.spectrum_error()``.
    The default optimizer is ``scipy.optimize.differential_evolution(), with
    ``options = {"bounds": bounds, "workers": -1, "updating"="deferred"}``,
    where ``bounds`` is [(min(xdata), max(xdata)] * (nzeros + npoles),
    and appended with [(min(ydata), max(ydata)].
    The bounds are np.log10() if log_args is true in the model.
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
    seed : int, optional
        The random seed.
        Defaults 123.
    """
    def __init__(self, xdata=None, ydata=None,
                 model=None, model_kwargs=None, npole=None, nzero=None,
                 cost=None, weight=None, error_func_kwargs=None,
                 optimizer=None, optimizer_kwargs=None, seed=123):
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
        seed : int, optional
            The random seed.
            Defaults 123.
        """
        if cost is None:
            error_func = kontrol.curvefit.error_func.spectrum_error
            default_error_func_kwargs = {"weight": weight}
            if error_func_kwargs is None:
                error_func_kwargs = default_error_func_kwargs
            else:
                error_func_kwargs = dict(
                    default_error_func_kwargs, **error_func_kwargs)
            cost = kontrol.curvefit.cost.Cost(
                error_func=error_func, error_func_kwargs=error_func_kwargs)

        if optimizer is None:
            optimizer = scipy.optimize.differential_evolution

        if (model is not None and xdata is not None and ydata is not None):
            n_zero_pole_bounds = model.nzero + model.npole
            if model.log_args:
                bound = (np.log10(min(xdata)), np.log10(max(xdata)))
                bounds = [bound] * n_zero_pole_bounds
                bounds.append((np.log10(min(ydata)), np.log10(max(ydata))))
            else:
                bound = (min(xdata), max(xdata))
                bounds = [bound] * n_zero_pole_bounds
                bounds.append((min(ydata), max(ydata)))
        else:
            bounds = None

        default_optimizer_kwargs = {
            "workers": -1, "updating": "deferred", "bounds": bounds}
        if optimizer_kwargs is None:
            optimizer_kwargs = default_optimizer_kwargs
        else:
            optimizer_kwargs = dict(
                default_optimizer_kwargs, **optimizer_kwargs)

        super().__init__(
            xdata, ydata, model, model_kwargs,
            cost, optimizer, optimizer_kwargs)
        self._weight = None
        self.weight = weight
        self._model = None
        self.model = model
        self._seed = None
        self.seed = seed

    @property
    def seed(self):
        """Random seed"""
        return self._seed

    @seed.setter
    def seed(self, _seed):
        """seed setter"""
        self._seed = _seed

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
    def xdata(self):
        """xdata"""
        return self._xdata

    @xdata.setter
    def xdata(self, _xdata):
        """xdata setter"""
        self._xdata = _xdata
        self._update_optimizer_kwargs()

    @property
    def ydata(self):
        """ydata"""
        return self._ydata

    @ydata.setter
    def ydata(self, _ydata):
        """ydata setter"""
        self._ydata = _ydata
        self._update_optimizer_kwargs()

    @property
    def model(self):
        """The ZPK model used to fit the spectrum"""
        return self._model

    @model.setter
    def model(self, _model):
        """model setter"""
        self._model = _model
        self._update_optimizer_kwargs()

    def _get_bounds(self):
        """Get bounds for scipy.optimize.differential_evolution"""
        if (self.model is not None and self.xdata is not None
           and self.ydata is not None):
            #
            n_zero_pole_bounds = self.model.nzero + self.model.npole
            if self.model.log_args:
                bound = (np.log10(min(self.xdata)), np.log10(max(self.xdata)))
                bounds = [bound] * n_zero_pole_bounds
                bounds.append(
                    (np.log10(min(self.ydata)), np.log10(max(self.ydata))))
            else:
                bound = (min(self.xdata), max(self.xdata))
                bounds = [bound] * n_zero_pole_bounds
                bounds.append((min(self.ydata), max(self.ydata)))
        else:
            bounds = None
        return bounds

    def _update_optimizer_kwargs(self):
        """Set optimizer_kwargs"""
        bounds = self._get_bounds()
        if bounds is not None:
            update_optimizer_kwargs = {"bounds": bounds}
            self.optimizer_kwargs = dict(
                self.optimizer_kwargs, **update_optimizer_kwargs)

    def prefit(self):
        """Something to do before fitting"""
        np.random.seed(self.seed)


class SpectrumTFFit(CurveFit):
    """Spectrum Transfer function fitting class

    This class is basically a ``CurveFit`` class
    with default cost functions and optimizer
    that is designed for fitting a spectrum with a transfer function
    By default, the error function is
    ``kontrol.curvefit.error_func.spectrum_error()``.
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
    optimizer : ``func(func, **kwargs)`` -> ``OptimizeResult``, or ``None``,\
                optional
        The optimization algorithm use for minimizing the cost function.
    optimizer_kwargs : ``dict`` or ``None``, optional
        Keyword arguments passed to the optimizer function.
        Defaults to ``None``.
    options : ``dict`` or ``None``, optional
        The option arguments passed to the ``optimizer``
    num0 : ``array``, optional
        Inital guess of the numerator.
        Defaults to None.
    den0 : ``array``, optional
        Inital guess of the denominator.
        Defaults to None.
    """
    def __init__(self, xdata=None, ydata=None,
                 model=None, model_kwargs=None,
                 cost=None, weight=None, error_func_kwargs=None,
                 optimizer=None, optimizer_kwargs=None, options=None,
                 num0=None, den0=None):
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
        num0 : ``array``, optional
            Inital guess of the numerator.
            Defaults to None.
        den0 : ``array``, optional
            Inital guess of the denominator.
            Defaults to None.
        """
        if cost is None:
            error_func = kontrol.curvefit.error_func.spectrum_error
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

        if num0 is None or den0 is None:
            x0 = None
            maxiter = None
        else:
            x0 = np.append(num0, den0)
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
        self._num0 = None
        self._den0 = None
        self.weight = weight
        self.options = options
        self.x0 = x0
        self.num0 = num0
        self.den0 = den0

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
    def num0(self):
        """Initial numerator guess"""
        return self._num0

    @num0.setter
    def num0(self, _num0):
        """num0 setter"""
        self._num0 = _num0
        if self.num0 is not None and self.den0 is not None:
            self.x0 = np.append(self.num0, self.den0)

    @property
    def den0(self):
        """Initial denominator guess"""
        return self._den0

    @den0.setter
    def den0(self, _den0):
        """den0 setter"""
        self._den0 = _den0
        if self.num0 is not None and self.den0 is not None:
            self.x0 = np.append(self.num0, self.den0)

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


def spectrum_fit(f, spectrum, nzero, npole, log_args=True,
                 seed=123, minreal=True, clean=True, stabilize=True,
                 return_zpk_fit=False, return_tf_fit=False):
    """Fit a spectrum with a zpk model intermediately and then with a tf model.

    Parameters
    ----------
    f : array
        Frequency axis.
    spectrum : array
        The frequency spectrum.
    nzero : int
        Number of zeros in the transfer function.
    npole : int
        Number of poles in the transfer function.
    log_args : boolean, optional
        Fit the log10 of the arguments instead.
        Defaults True.
    seed : int, optional
        Random seed.
    minreal : boolean, optional
        Return the minreal version of the transfer function.
        Defaults True.
    clean : boolean, optional
        Clean the transfer function before returning.
        This uses kontrol.TransferFunction.clean() to remove outlier
        coefficients.
        Defaults True.
    stabilize : boolean, optional
        Negate the real parts of unstable zeros and poles.
        Defaults True.
    return_zpk_fit : boolean, optional
        Return the kontrol.curvefit.SpectrumZPKFit object.
        Defaults False.
    return_tf_fit : boolean, optional
        Return the kontrol.curvefit.SpectrumTFFit object.
        Defaults False.

    Returns
    -------
    tf : Kontrol.TransferFunction
        The fitted transfer function
    zpk_fit : Kontrol.curvefit.SpectrumZPKFit, optional
        The CurveFit object used to fit intermediately.
        Return only if ``return_zpk_fit`` is ``True``.
    tf_fit : Kontrol.curvefit.SpectrumTFFit, optional
        The CurveFit object used to fit the final transfer function
        Return only if ``return_tf_fit`` is ``True``.
    """
    # Fit a ZPK model.
    zpk_model = kontrol.curvefit.model.SimpleZPK(
        nzero=nzero, npole=npole, log_args=log_args)
    zpk_fit = SpectrumZPKFit(seed=seed)
    zpk_fit.xdata = f
    zpk_fit.ydata = spectrum
    zpk_fit.model = zpk_model
    zpk_fit.fit()

    # Extract the fitted zpk model's numerator and denominator
    tf_zpk_fit = zpk_fit.model.tf
    tf_zpk_fit = tf_zpk_fit.minreal()
    num0 = tf_zpk_fit.num[0][0]
    den0 = tf_zpk_fit.den[0][0]
    if log_args:
        num0 = np.log10(num0)
        den0 = np.log10(den0)

    # Fit a transfer function model using the fitted ZPK as an initial guess
    tf_model = kontrol.curvefit.model.TransferFunctionModel(
        nzero=nzero, npole=npole, log_args=log_args)
    tf_fit = SpectrumTFFit()
    tf_fit.xdata = f
    tf_fit.ydata = spectrum
    tf_fit.model = tf_model
    tf_fit.num0 = num0
    tf_fit.den0 = den0
    tf_fit.fit()

    # Post processing
    tf = tf_fit.model.tf
    if stabilize:
        tf.stabilize()
    if clean:
        tf.clean()  # This actually does minreal already.
    if minreal:
        # minreal returns a control.TransferFunction object...
        tf = kontrol.TransferFunction(tf.minreal())

    # Return
    if return_zpk_fit and return_tf_fit:
        return tf, zpk_fit, tf_fit
    elif return_zpk_fit:
        return tf, zpk_fit
    elif return_tf_fit:
        return tf, tf_fit
    else:
        return tf
