"""Core algorithm library.

And yes, I know I shouldn't use Python for computations like these.
"""
import numpy as np

import kontrol.logger


def bisection_method(
        func, x1, x2, val, tol=1e-6, maxiter=9999, log_center=False,
        **kwargs):
    """Bisection method for finding argument of a scalar function.

    This algorithm use bisection method to find
    the argument such that a scalar function ``func(x)``
    outputs a desired target value ``val``.
    Note that in a typical root finding problem, ``val``
    is just 0.
    The target function value must exist within the
    two endponts ``x1`` and ``x2``.
    In addition ``func(x1) - val`` and ``func(x2) - val``
    must have different signs (intermediate value theorem)
    or else the algorithm won't work.
    The algorithm exits when maximum iteration is reached.

    Parameters
    ----------
    func : callable(x: float) -> float
        The function.
    x1 : float
        The first endpoint.
    x2 : float
        The second endpoint.
    val : float
        The target value.
    ftol : float, optional,
        The tolerance of the function value for
        satisfying convergence condition.
        Defaults to 1e-6.
    maxiter : ``int``, optional
        Maximum number of iteration before termination.
        Defaults to 9999.
    log_center : bool, optional
        Use the logarithmic center of the endpoints to calculate
        the next endpoint instead of the using the linear center.
        Defaults to ``False``.
    **kwargs
        Keyword arguments passed to ``func(x, **kwargs)``.

    Returns
    -------
    xm : float or None
        The solutuon where ``func(xm)=val``.
        If maxiter is reached, returns ``None``

    Raises
    ------
    ValueError
        If ``func(x1) - val`` and ``func(x2) - val`` don't have
        different signs.

    Notes
    -----
    The termination condition is ``abs(func(xm)-val) < tol``.
    """
    func_x1 = func(x1, **kwargs)
    func_x2 = func(x2, **kwargs)
    if np.sign(func_x1 - val) == np.sign(func_x2 - val):
        raise ValueError("func(x1)-val and func(x2)-val must have different"
                         " signs.")

    for _ in range(maxiter):
        if log_center:
            xm = 10**((np.log10(x1) + np.log10(x2))/2)
        else:
            xm = (x1+x2)/2
        func_val = func(xm, **kwargs)
        if abs((func_val-val)) < tol:
            return xm
        else:
            func_x1 = func(x1, **kwargs)
            func_x2 = func(x2, **kwargs)
            if np.sign(func_x1 - val) == np.sign(func_val - val):
                x1 = xm
            else:
                x2 = xm
    kontrol.logger.logger.error("Maximum number of iteration reached")
    return None
