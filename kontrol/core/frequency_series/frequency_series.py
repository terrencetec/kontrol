"""Frequency series class.
"""
import inspect

import numpy as np
import scipy.optimize

from . import costs
import kontrol.common.math


class FrequencySeries:
    """ Frequency series class
    """
    def __init__(self, f, x):
        """Constructor

        Parameters
        f: array
            Frequency axis
        x: array
            Frequency series data.
        """
        self.f = f
        self.x = x

    def fit_empirical(self, model, x0=None,
                      error_func=kontrol.common.math.log_mse,
                      error_func_kwargs={},
                      minimize_kwargs={"method":"Powell"}):
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
            fun=costs.empirical_fit_cost, x0=x0,
            args=(self.f, self.x, model, error_func, error_func_kwargs),
            **minimize_kwargs)
        self.x_empirical = model(self.f, *res.x)
        return res
