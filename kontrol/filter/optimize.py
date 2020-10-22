"""Optimization related control stuff.

This is an ad hoc premature filter optimization python package for designing
and optimization of digital filters.
"""

from control import tf, h2syn, hinfsyn, ss
import numpy as np
from scipy.optimize import (
                            dual_annealing,
                            differential_evolution,
                            minimize, Bounds)
import time
from ..utils import quad_sum, norm2, tfmatrix2tf
# from .filters import complementary_sekiguchi, complementary_modified_sekiguchi

# We are using functions for filters for now, for simplicity.
# In the future we should switch to classes which are more manageable.

def optimize_complementary_filter(complementary_filter, spectra, f, \
                                  method=differential_evolution, \
                                  bounds=None, x0=None, \
                                  *args, **kwargs):
    """Complementary filter optimization given noise spectra.

    Take a filter function (returns (lpf, hpf)) and bounds of the filter
    coefficients, the spectrum contents that goes through the complementary
    filters and the frequency axis of the spectra. This function will minimize
    the 2-norm of the overall spectra and returns the coefficients of the
    filters which do that.

    Parameters
    ----------
        complementary_filter: tuple of (control.xferfcn.TransferFunction, )
            A function that returns a tuple of the list of complementary \
            filters.
        spectra: list of [list or numpy.ndarray, ]
            The frequency dependent contents that are filtered by the \
            complementary filters with indice matching that of \
            complementary_filter. Each spectrum must have the same length as \
            each other and must have the same length as the frequency axis f.
        f: list of float or numpy.ndarray
            The frequency axis of the spectra.
        method: function, optional
            The function that takes a cost function and minimizes it. \
            Examples would be scipy.optimize.minimize(), \
            scipy.optimize.dual_annealing(), \
            and scipy.optimize.differential_evolution().
        bounds: list of tuple of (float, float), optional
            The numerical boundaries of the coefficients that define the \
            filters. E.g. [(0, 1), (0, 2), ].
        x0: list of float or numpy.ndarray, optional
            The initial guess of the filter arguments.
        \*args:
            Variable length arguments list
        \*\*kwargs:
            Keyword arguments that also goes to the method.

    Returns
    -------
        result: scipy.optimize.OptimizeResult
            The optimization result in scipy optimization result format.

    Note
    ----
    Method is automatically selected base on the
    specifications of bounds and x0. If a custom method is desired,
    then make sure that the arguments are correctly specfied in \*\*kwargs
    and that it takes the first argument as the cost function.
    A function of the optimization that takes the format
    optimization(cost_function, bounds, ...).

    I found two methods in scipy.optimize particularly useful,
    dual_annealing and differential_evolution. dual_annealing is slower
    for high-dimensional parameter space while differential_evolution is
    generally faster but can at times trapped in local minimum near the
    true optimum.

    The function automatically detemines which minimization method to be used.
    If x0 is provided, then scipy.optimize.minimize will be used if bounds are
    not provided and scipy.optimize.dual_annealing will be used if bounds are
    provided. Otherwise, scipy.optimize.differential_evolution will be used.
    """

    def cost(coefs):
        """Takes filter coefficients, applies them to the specfied
        complementary_filter, and applies the filters to the spectra,
        and then returns the 2-norm of the overall spectrum.
        """
        filtered_spectra=[[]]*len(spectra)
        for i in range(len(spectra)):
            s = 2*np.pi*1j*f
            filter_val = abs(complementary_filter(coefs)[i].horner(s)[0][0])
            filtered_spectra[i] = spectra[i] * filter_val
        total_spectrum = quad_sum(*filtered_spectra)
        return(norm2(total_spectrum))

    if x0 is not None:
        kwargs['x0'] = x0
    if bounds is None:
        kwargs['fun'] = cost
        method = minimize
        print('Optimizing with scipy.optimize.minimize')
        if x0 is None:
            print('x0 must be specified if bounds are not specified')
            return(None)
    else:
        kwargs['bounds'] = bounds
        kwargs['func'] = cost
        if x0 is None:
            method = differential_evolution
            print('Optimizing with scipy.optimize.differential_evolution')
        else:
            method = dual_annealing
            print('Optimizing with scipy.optimize.dual_annealing')
#         method = minimize
#         kwargs['fun'] = _cost
#         kwargs['x0'] = x0
#     kwargs['args'] = args
    t0 = time.clock()
    result = method(**kwargs)
    print('Done. Time taken: %.2f s The 2-norm is %.2f unit'
    %(time.clock()-t0, result.fun))
    return(result)

def h2complementary(n1, n2):
    """H2 optimal complementary filter synthesis

    Parameters
    ----------
    n1: control.xferfcn.TransferFunction
        The transfer function representing the noise content of a
        particular sensor to be fused.
    n2: control.xferfcn.TransferFunction
        The trasnfer function representing the noise content of another
        sensor to be fused.

    Returns
    -------
    h1: control.xferfcn.TransferFunction
        The complementary filter filtering n1.
    h2: control.xferfcn.TransferFunction
        The complementary filter filtering n2.

    Notes
    -----
    This function ultilizes control.robust.h2syn which depends on the slycot
    module. If you are using under a conda virtual environment, the slycot
    module can be installed easily from conda-forge. Using pip to install
    slycot is a bit more involved (I have yet to suceed installing slycot in
    my Windows machine). Please refer to the python-control package for further
    instructions.

    It is possible that h2syn yields no solution for some tricky noise profiles
    . Try adjusting the noise profiles at some irrelevant frequencies.

    Thomas Dehaeze [1]_ had the idea first so credits goes to him. (Properly
    cite when the paper is published.)

    References
    ----------
    .. [1]
        Dehaeze, T.
        https://tdehaeze.github.io/dehaeze20_optim_robus_compl_filte/matlab/index.html
    """
    p = [[tf([0],[1]), n2, tf([1],[1])],
         [n1, -n2, tf([0],[1])]]
#     p = [[n1, -n1],
#          [tf([0],[1]), n2],
#          [tf([1],[1]), tf([0],[1])]]
    p = tfmatrix2tf(p)
    h1 = tf(h2syn(ss(p), 1, 1))
    h2 = 1 - h1
    return(h1, h2)

def hinfcomplementary(n1, n2):
    """H-infinity optimal complementary filter synthesis

    Parameters
    ----------
    n1: control.xferfcn.TransferFunction
        The transfer function representing the noise content of a
        particular sensor to be fused.
    n2: control.xferfcn.TransferFunction
        The trasnfer function representing the noise content of another
        sensor to be fused.

    Returns
    -------
    h1: control.xferfcn.TransferFunction
        The complementary filter filtering n1.
    h2: control.xferfcn.TransferFunction
        The complementary filter filtering n2.

    Notes
    -----
    This function ultilizes control.robust.hinfsyn which depends on the slycot
    module. If you are using under a conda virtual environment, the slycot
    module can be installed easily from conda-forge. Using pip to install
    slycot is a bit more involved (I have yet to suceed installing slycot in
    my Windows machine). Please refer to the python-control package for further
    instructions.

    It is possible that h2syn yields no solution for some tricky noise profiles
    . Try adjusting the noise profiles at some irrelevant frequencies.

    Thomas Dehaeze [1]_ had the idea first so credits goes to him. (Properly
    cite when the paper is published.)

    References
    ----------
    .. [1]
        Dehaeze, T.
        https://tdehaeze.github.io/dehaeze20_optim_robus_compl_filte/matlab/index.html
    """
    p = [[tf([0],[1]), n2, tf([1],[1])],
         [n1, -n2, tf([0],[1])]]
#     p = [[n1, -n1],
#          [tf([0],[1]), n2],
#          [tf([1],[1]), tf([0],[1])]]
    p = tfmatrix2tf(p)
    K, _, _, _ = hinfsyn(ss(p), 1, 1)
    h1 = tf(K)
    h2 = 1 - h1
    return(h1, h2)
