"""Error functions for curve fitting
"""
import numpy as np


def mse(x1, x2, weight=None):
    """Mean square error

    Parameters
    ----------
    x1 : array
        Array
    x2 : array
        Array
    weight: array or None, optional
        weighting function.
        If None, defaults to np.ones_like(x1)

    Returns
    -------
    float
        Mean square error between arrays x1 and x2.
    """
    if weight is None:
        weight = np.ones_like(x1)
    return np.mean(np.square(np.subtract(x2, x1)*weight))


def log_mse(x1, x2, weight=None, small_multiplier=1e-6):
    """Logarithmic mean square error/Mean square log error

    Parameters
    ----------
    x1 : array
        Array
    x2 : array
        Array
    weight: array or None, optional
        weighting function.
        If None, defaults to `np.ones_like(x1)`
    small_multiplier: float, optional
        `x1` will be modified by `x1`+`small_multiplier`*`np.min(x2)` if
        0 exists in `x1`.
        Same goes to `x2`.
        If 0 both exists in `x1` and `x2`, raise.

    Returns
    -------
    float
        Logarithmic mean square error between arrays x1 and x2.
    """
    if 0 in x1 and 0 in x2:
        raise ValueError("zero value exists in both 'x1' and 'x2'"
                         "Can't take np.log10()")
    elif 0 in x1:
        x1 += small_multiplier * np.min(x2)
    elif 0 in x2:
        x2 += small_multiplier * np.min(x1)
    return mse(x1=np.log10(x1), x2=np.log10(x2), weight=weight)
