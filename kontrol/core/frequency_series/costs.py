"""Cost functions for fitting
"""
from . import conversion
import kontrol.common.math


def cost_empirical_fit(args, f, x, model,
                       error_func=kontrol.common.math.log_mse,
                       error_func_kwargs={}):
    """Cost function for frequency series empirical fitting.

    Parameters
    ----------
    args: array
        Empirical model parameters.
    f: array
        Frequency axis.
    x: array
        Frequency series data.
    model: func(f, a, b, c, ...) -> array
        The model function whose first argument is the frequency axis and
        the rest being an arbitrary number of model parameters to be fit.
    error_func: func(x1: array, x2: array) -> float
        The function that evaluate the error between arrays x1 and x2.
        Defaults to kontrol.common.math.log_mse, which evaluates the
        logarithmic mean square error.
    error_func_kwargs: dict
        Keyword arguments passed to the error function.

    Returns
    -------
    cost: float
        The cost.
    """
    x_model = model(f, *args)
    cost = error_func(x, x_model, **error_func_kwargs)
    return cost


def cost_zpk_fit(zpk_args, f, x,
                 error_func=kontrol.common.math.log_mse,
                 error_func_kwargs={}):
    """The cost function for fitting a frequency series with zero-pole-gain.

    Parameters
    ----------
    zpk_args: array
        A 1-D list of zeros, poles, and gain.
        Zeros and poles are in unit of Hz.
    f: array
        The frequency axis.
    x: array
        The frequecy series data.
    error_func: func(x1: array, x2: array) -> float
        The function that evaluate the error between arrays x1 and x2.
        Defaults to kontrol.common.math.log_mse, which evaluates the
        logarithmic mean square error.
    error_func_kwargs: dict
        Keyword arguments passed to the error function.

    Returns
    -------
    cost: float
        The cost.
    """
    x_zpk = abs(conversion.args2zpk(f=f, zpk_args=zpk_args))
    cost = error_func(x, x_zpk, **error_func_kwargs)
    return cost
