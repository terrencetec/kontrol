"""Frequency series class.
"""
import inspect

import numpy as np
import scipy.optimize

from . import costs
from . import conversion
import kontrol.common.math


class FrequencySeries:
    """ Frequency series class

    Parameters
    ----------
    f: array
        Frequency axis
    x: array
        Frequency series data.

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

    Methods
    -------
    fit_empirical(model, x0=None, error_func=kontrol.common.math.log_mse,
    error_func_kwargs={}, minimize_kwargs={"method": "Powell"})

    fit_zpk(self, order, fit="x_empirical",
    padding=False, padding_order=1.,
    error_func=kontrol.common.math.log_mse,
    error_func_kwargs={},
    optimizer=scipy.optimize.differential_evolution,
    optimizer_kwargs={})
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

    def fit_empirical(self, model, x0=None,
                      error_func=kontrol.common.math.log_mse,
                      error_func_kwargs={},
                      minimize_kwargs={"method": "Powell"}):
        """Fit frequency series data with an empirical model. (Local optimize)

        Parameters
        ----------
        model: func(f, a, b, c, ...) -> array
            The model function whose first argument is the frequency axis and
            the rest being an arbitrary number of model parameters to be fit.
        x0: array, optional.
            The initial parameters for fitting.
            Defaults None. If None, defaults to np.ones()
        error_func: func(x1: array, x2: array) -> float
            The function that evaluate the error between arrays x1 and x2.
            Defaults to kontrol.common.math.log_mse, which evaluates the
            logarithmic mean square error.
        error_func_kwargs: dict, optional
            Keyword arguments passed to the error function.
            Use this to specify weighting function {"weight": weight_func}.
            Defaults to {}.
        minimize_kwargs: dict, optional.
            Keyword arguments passed to scipy.optimize.minimize.
            Defaults {"method":"Powell"}

        Returns
        -------
        res: scipy.optimize.OptimizeResult
            The result of the fitting (optimization)
        """
        self.model_empirical = model
        if "method" not in minimize_kwargs.keys():
            minimize_kwargs["method"] = "Powell"
        if x0 is None:
            str_sig_model = str(inspect.signature(model))
            nargs = len(str_sig_model.split(",")) - 1
            x0 = np.ones(nargs)
        res = scipy.optimize.minimize(
            fun=costs.cost_empirical_fit, x0=x0,
            args=(self.f, self.x, model, error_func, error_func_kwargs),
            **minimize_kwargs)
        self.args_empirical_model = res.x
        self.x_empirical = model(self.f, *res.x)
        return res

    def fit_zpk(self, order, fit="x_empirical",
                padding=False, padding_order=1.,
                error_func=kontrol.common.math.log_mse,
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
        """
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

        # Set defaults for the default optimizer
        if "workers" not in optimizer_kwargs.keys():
            if "workers" in inspect.signature(optimizer).parameters:
                optimizer_kwargs["workers"] = -1
        if "updating" not in optimizer_kwargs.keys():
            if "updating" in inspect.signature(optimizer).parameters:
                optimizer_kwargs["updating"] = "deferred"

        frequency_bounds = [(min(f), max(f))]*2*order  # FIXME
        gain_bound = [(min(x)*1e-1, max(x)*1e1)]    # FIXME
        bounds = frequency_bounds + gain_bound
        if "bounds" not in optimizer_kwargs.keys():
            if "bounds" in inspect.signature(optimizer).parameters:
                optimizer_kwargs["bounds"] = bounds

        res = optimizer(
            func=costs.cost_zpk_fit,
            args=(f, x, error_func, error_func_kwargs),
            **optimizer_kwargs)
        self.f_zpk = f
        self.x_zpk = conversion.args2zpk(f=f, zpk_args=res.x)
        self.tf_zpk = conversion.args2controltf(zpk_args=res.x)
        self.args_zpk_model = res.x
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
