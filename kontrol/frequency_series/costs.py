"""Cost functions for fitting
"""
import numpy as np

import kontrol.core.math
import kontrol.frequency_series.conversion



def cost_empirical_fit(args, f, x, model,
                       error_func=kontrol.core.math.log_mse,
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
        Defaults to kontrol.core.math.log_mse, which evaluates the
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
                 error_func=kontrol.core.math.log_mse,
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
        Defaults to kontrol.core.math.log_mse, which evaluates the
        logarithmic mean square error.
    error_func_kwargs: dict, optional
        Keyword arguments passed to the error function.
        Defaults {}.

    Returns
    -------
    cost: float
        The cost.
    """
    x_zpk = abs(
        kontrol.frequency_series.conversion.args2zpk(f=f, zpk_args=zpk_args))
    cost = error_func(x, x_zpk, **error_func_kwargs)
    return cost


def cost_tf_fit(tf_args, f, x,
                error_func=kontrol.core.math.log_mse,
                error_func_kwargs={},
                log_var=True):
    """The cost funcion for gitting a frequency series with transfer function.

    Parameters
    ----------
    tf_args: array
        A 1-D list of numerator and denominator coefficients,
        from higher order to lower order.
    f: array
        The frequency axis.
    x: array
        The frequecy series data.
    error_func: func(x1: array, x2: array) -> float, optional
        The function that evaluate the error between arrays x1 and x2.
        Defaults to kontrol.core.math.log_mse, which evaluates the
        logarithmic mean square error.
    error_func_kwargs: dict, optional
        Keyword arguments passed to the error function.
        Defaults {}.
    log_var: boolean, optional
        Optimize the log of variables instead.
        Useful for variables that have very large dynamic range
        Defaults True.

    Returns
    -------
    cost: float
        The cost.
    """
    if log_var:
        tf_args = np.exp(tf_args)
    x_tf = abs(
        kontrol.frequency_series.conversion.args2tf(f=f, tf_args=tf_args))
    cost = error_func(x, x_tf, **error_func_kwargs)
    return cost
