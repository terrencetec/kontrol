"""Frequency series class.
"""
import inspect

import numpy as np
import scipy.optimize

import kontrol.core.math
import kontrol.frequency_series.costs
import kontrol.frequency_series.conversion


class FrequencySeries:
    """ Frequency series class

    Attributes
    ----------
    f: array
        Frequency axis
    x: array
        Frequency series data.
    x_empirical: array or None
        Frequency series of the empirical model.
    model_empirical: func(f, a, b, c, ...) -> array or None
        The model function whose first argument is the frequency axis and
        the rest being an arbitrary number of model parameters to be fit.
    args_empirical_model: array or None
        The optimized arguments passed to the model_empirical.
    f_zpk: array or None
        The frequency axis used during ZPK fitting.
    x_zpk: array or None
        The frequency series data used during ZPK fitting.
        Note: this is a complex array.
    tf_zpk: control.xferfcn.TransferFunction or None
        The transfer function the best fit the data using ZPK model.
    args_zpk_model: array or None
        A 1-D list of zeros, poles, and gain.
        Zeros and poles are in unit of Hz.
    f_tf: array or None
        The frequency series data used during transfer function fitting.
    x_tf: array or None
        The frequency series data used during transfer function fitting.
        Note: this is a complex array.
    tf: control.xferfcn.TransferFunction or None
        The modeled transfer function.
    args_tf_model: array or None
        A 1-D list of numerator and denominator coefficients,
        from higher order to lower order.
    """
    def __init__(self, f, x):
        """Constructor

        Parameters
        ----------
        f: array
            Frequency axis
        x: array
            Frequency series data.
        """
        self.f = f
        self.x = x
        self.x_empirical = None
        self.model_empirical = None
        self.args_empirical_model = None
        self.f_zpk = None
        self.x_zpk = None
        self.tf_zpk = None
        self.args_zpk_model = None
        self._f_processed = None
        self._x_processed = None
        self.f_tf = None
        self.x_tf = None
        self.tf = None
        self.args_tf_model = None

    def fit_empirical(self, model, x0=None,
                      error_func=kontrol.core.math.log_mse,
                      error_func_kwargs={},
                      optimizer=scipy.optimize.minimize,
                      optimizer_kwargs={}):
        """Fit frequency series data with an empirical model. (Local optimize)

        Parameters
        ----------
        model: func(f, a, b, c, ...) -> array
            The model function whose first argument is the frequency axis and
            the rest being an arbitrary number of model parameters to be fit.
        x0: array, optional
            The initial parameters for fitting.
            Defaults None. If None, defaults to np.ones()
        error_func: func(x1: array, x2: array) -> float
            The function that evaluate the error between arrays x1 and x2.
            Defaults to kontrol.core.math.log_mse, which evaluates the
            logarithmic mean square error.
        error_func_kwargs: dict, optional
            Keyword arguments passed to the error function.
            Use this to specify weighting function {"weight": weight_func}.
            Defaults to {}.
        optimizer: func, optional
            The optimization function which has the signature
            func(func, args, bounds, **kw) -> scipy.optimize.OptimizeResult.
            Defaults to scipy.optimize.minimize.
        optimizer_kwargs: dict, optional
            Keyword arguments passed to the optimization function.
            Defaults {} but will set to
            {"method": "Powell", "x0"=x0} if optimizer is default.

        Returns
        -------
        res: scipy.optimize.OptimizeResult
            The result of the fitting (optimization)
        """
        self.model_empirical = model
        if x0 is None:
            str_sig_model = str(inspect.signature(model))
            nargs = len(str_sig_model.split(",")) - 1
            x0 = np.ones(nargs)

        if "method" not in optimizer_kwargs.keys():
            if "method" in inspect.signature(optimizer).parameters:
                optimizer_kwargs["method"] = "Powell"
        if "x0" not in optimizer_kwargs.keys():
            if "method" in inspect.signature(optimizer).parameters:
                optimizer_kwargs["x0"] = x0

        res = optimizer(
            kontrol.frequency_series.costs.cost_empirical_fit,
            args=(self.f, self.x, model, error_func, error_func_kwargs),
            **optimizer_kwargs)
        self.args_empirical_model = res.x
        self.x_empirical = model(self.f, *res.x)
        return res

    def fit_zpk(self, order, fit="x_empirical",
                padding=False, padding_order=1.,
                error_func=kontrol.core.math.log_mse,
                error_func_kwargs={},
                optimizer=scipy.optimize.differential_evolution,
                optimizer_kwargs={}):
        """Fit frequency series with a zpk model.

        Parameters
        ----------
        order: int
            The order of the ZPK model to be used.
        fit: str, optional
            Choose the data to be fit,
            choose from ["x", "x_empirical"].
        padding: boolean, optional
            Pad the data by continuous white noise.
            Defaults False.
        padding_order: float, optional
            The number of decades to be padded on both sides of the series.
            Defaults to 1.
        error_func: func(x1: array, x2: array) -> float
            The function that evaluate the error between arrays x1 and x2.
            Defaults to kontrol.core.math.log_mse, which evaluates the
            logarithmic mean square error.
        error_func_kwargs: dict, optional
            Keyword arguments passed to the error function.
            Use this to specify weighting function {"weight": weight_func}.
            Defaults to {}.
        optimizer: func, optional
            The optimization function which has the signature
            func(func, args, bounds, **kw) -> scipy.optimize.OptimizeResult.
            Defaults to scipy.optimize.differential_evolution.
        optimizer_kwargs: dict, optional
            Keyword arguments passed to the optimization function.
            Defaults {} but will set to
            {"workers": -1, "updating":"deferred"} if optimizer is default.

        Returns
        -------
        res: scipy.optimize.OptimizerResult
            The result of the optimization.

        Note
        ----
        For now, we support models with equal number of zeros and poles only.

        Best use with log-space frequency series or after using
        `fit_empirical()`.
        """
        if self._f_processed is None or self._x_processed is None:
            if fit == "x":
                f = self.f
                x = self.x
                if np.isclose(f[1]-f[0], f[2]-f[1]):
                    spacing = "linear"
                else:
                    spacing = "log"
            elif fit == "x_empirical":
                f = np.logspace(
                    np.log10(min(self.f)), np.log10(max(self.f)), len(self.f))
                x = self.model_empirical(f, *self.args_empirical_model)
                spacing = "log"
            else:
                raise ValueError("Choose fit from [\"x\" or \"x_empirical\"]")
            if padding:
                f, x = self._get_padded_data(f, x, padding_order, spacing)
            # Use these for zpk and tf fit.
            self._f_processed = f
            self._x_processed = x

        _optimizer_kwargs = dict(optimizer_kwargs)

        # Set defaults for the default optimizer
        if "workers" not in _optimizer_kwargs.keys():
            if "workers" in inspect.signature(optimizer).parameters:
                _optimizer_kwargs["workers"] = -1
        if "updating" not in _optimizer_kwargs.keys():
            if "updating" in inspect.signature(optimizer).parameters:
                _optimizer_kwargs["updating"] = "deferred"

        frequency_bounds = [(min(f), max(f))]*2*order  # FIXME
        gain_bound = [(min(x)*1e-1, max(x)*1e1)]    # FIXME
        bounds = frequency_bounds + gain_bound

        if "bounds" not in _optimizer_kwargs.keys():
            if "bounds" in inspect.signature(optimizer).parameters:
                _optimizer_kwargs["bounds"] = bounds

        res = optimizer(
            kontrol.frequency_series.costs.cost_zpk_fit,
            args=(f, x, error_func, error_func_kwargs),
            **_optimizer_kwargs)
        self.f_zpk = f
        self.x_zpk = kontrol.frequency_series.conversion.args2zpk(f=f, zpk_args=res.x)
        self.tf_zpk = kontrol.frequency_series.conversion.args2controltf(zpk_args=res.x)
        self.args_zpk_model = res.x
        return res

    def fit_tf(self, x0=None, log_var=True,
               error_func=kontrol.core.math.log_mse,
               error_func_kwargs={},
               optimizer=scipy.optimize.minimize,
               optimizer_kwargs={}):
        """Fit frequency series with a transfer function model

        Parameters
        ----------
        x0: array or None, optional
            The initial parameters defining the initial transfer function.
            A 1-D list of numerator and denominator coefficients,
            from higher order to lower order.
            Defaults None.
            If None, will use the result from the ZPK fitting.
        log_var: boolean, optional
            Optimize the log of variables instead.
            Useful for variables that have very large dynamic range
            Defaults True.
        error_func: func(x1: array, x2: array) -> float, optional
            The function that evaluate the error between arrays x1 and x2.
            Defaults to kontrol.core.math.log_mse, which evaluates the
            logarithmic mean square error.
        error_func_kwargs: dict, optional
            Keyword arguments passed to the error function.
            Use this to specify weighting function {"weight": weight_func}.
            Defaults to {}.
        optimizer: func, optional
            The optimization function which has the signature
            func(func, args, bounds, **kw) -> scipy.optimize.OptimizeResult.
            Defaults to scipy.optimize.minimize.
        optimizer_kwargs: dict, optional
            Keyword arguments passed to the optimization function.
            Defaults {} but will set to
            {"method": "Powell", "x0": x0} if optimizer is default.

        Returns
        -------
        res: scipy.optimize.OptimizerResult
            The result of the optimization.

        Note
        ----
        Only use this after using `fit_zpk()`.
        """
        if x0 is None:
            x0 = kontrol.frequency_series.conversion.tf2tf_args(tf=self.tf_zpk)
        if log_var:
            x0 = np.log(x0)

        _optimizer_kwargs = dict(optimizer_kwargs)
        if "method" not in _optimizer_kwargs.keys():
            if "method" in inspect.signature(optimizer).parameters:
                _optimizer_kwargs["method"] = "Powell"
        if "x0" not in _optimizer_kwargs.keys():
            if "method" in inspect.signature(optimizer).parameters:
                _optimizer_kwargs["x0"] = x0

        f = self._f_processed
        x = self._x_processed

        res = optimizer(
            kontrol.frequency_series.costs.cost_tf_fit,
            args=(f, x, error_func, error_func_kwargs, log_var),
            **_optimizer_kwargs)

        self.f_tf = f
        args_opt = res.x
        if log_var:
            args_opt = np.exp(args_opt)
        self.x_tf = kontrol.frequency_series.conversion.args2tf(f, args_opt)  # Frequency series
        self.tf = kontrol.frequency_series.conversion.tf_args2tf(args_opt)  # Transfer function
        self.args_tf_model = args_opt

        return res

    def _get_padded_data(self, f, x, padding_order, spacing="log"):
        """Calculate padded frequency axis.

        Parameters
        ----------
        f: array
            Frequency axis
        x: array
            Frequency series data.
        padding_order: float
            The number of decades to be padded on both sides of the series.
        spacing: str, optional
            The spacing of the specified data.
            Choose from ["log", "linear"].

        Returns
        -------
        f_pad: array
            Padded frequency axis.
        x_pad: array
            Padded frequency series data
        """
        len_new_f = ((np.log10(max(f)) + padding_order
                    - np.log10(min(f)) + padding_order)
                    / (np.log10(max(f)) - np.log10(min(f)))
                    * len(f))
        len_new_f = int(len_new_f)
        pad_width = int(((len_new_f)-len(f))/2)
        if spacing == "log":
            upper = np.log10(max(f)) + padding_order
            lower  = np.log10(min(f)) - padding_order
            f = np.logspace(
                np.log10(min(f)), np.log10(max(f)), len(f))
            log_f = np.log10(f)
            log_f_pad = np.pad(log_f, pad_width, "linear_ramp",
                end_values=(lower, upper))
            f_pad = 10**log_f_pad
        elif spacing == "linear":
            upper = max(f)*10**padding_order
            lower = min(f)/10**padding_order
            f_pad = np.pad(f, pad_width, "linear_ramp",
                end_values=(lower, upper))
        x_pad = np.pad(x, pad_width, "edge")
        return f_pad, x_pad
