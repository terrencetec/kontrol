"""This is an ad hoc premature filter optimization python package for designing
andoptimization of digital filters.

We follow PEP 8 style as much as possible.
"""

from control import tf
import numpy as np
from scipy.optimize import (
                            dual_annealing,
                            differential_evolution,
                            minimize, Bounds)
import time
from .utils import quad_sum, norm2
from .filters import complementary_sekiguchi, complementary_modified_sekiguchi

# We are using functions for filters for now, for simplicity.
# In the future we should switch to classes which are more manageable.

def optimize_complementary_filter(filter_, spectra, f,
                                  method=differential_evolution,
                                  bounds=None, x0=None,
                                  *args, **kwargs):
    """Take a filter function (returns (lpf, hpf)) and bounds of the filter
    coefficients, the spectrum contents that goes through the complementary
    filters and the frequency axis of the spectra. This function will minimize
    the 2-norm of the overall spectra and returns the coefficients of the
    filters which do that.

    Args:
        filter_: tuple
            a function that returns a tuple of the list of complementary filters
            (lpf, hpf), or even (lpf, mpf, ...), where pfs are the filter in
            TransferFunction class.
        bounds: list of tuples
            The numerical boundaries of the coefficients that defines the
            filters in the format [(lower bound, upper bound), ...]. If not
            specified, then local minimization methods will be used. In this
            case x0 must be provided. If specified with x0, then dual annealing
            will be used. Else, differential evolution will be used.
        spectra: list of array_like
            The frequency dependent contents that is filtered by the
            complementary filters with indice matching that of filter_. Each
            spectrum must have the same length as each other and must have the
            same length as the frequency axis f.
        f: array_like
            The frequency axis of the spectra.
        method: function
            2020/05/14: method is automatically selected base on the
            specifications of bounds and x0. If a custom method is desired,
            then make sure that the arguments are correctly specfied in **kwargs
            and that it takes the first argument as the cost function.
            A function of the optimization that takes the format
            optimization(cost_function, bounds, ...)
            I found two methods in scipy.optimize particularly useful,
            dual_annealing and differential_evolution. dual_annealing is slower
            for high-dimensional parameter space while differential_evolution is
            generally faster but can at times trapped in local minimum near the
            true optimum.
        x0: array_like
            The initial guess of the filter arguments. If provided, then either
            differential evolution or dual annealing will be used depending on

    Returns:
        result: scipy.optimize.OptimizeResult
            the optimization result in scipy optimization result format.
    """

    def cost(coefs):
        """Takes filter coefficients, applies them to the specfied filter_,
        and applies the filters to the spectra,
        and then returns the 2-norm of the overall spectrum.
        """
        filtered_spectra=[[]]*len(spectra)
        for i in range(len(spectra)):
            filter_val=abs(filter_(coefs)[i].horner(2*np.pi*1j*f)[0][0])
            filtered_spectra[i] = spectra[i] * filter_val
        total_spectrum = quad_sum(*filtered_spectra)
        return(norm2(total_spectrum))

    if x0 is not None:
        kwargs['x0'] = x0
    if bounds == None:
        kwargs['fun'] = cost
        method = minimize
        print('Optimizing with scipy.optimize.minimize')
        if x0 == None:
            print('x0 must be specified if bounds are not specified')
            return(None)
    else:
        kwargs['bounds'] = bounds
        kwargs['func'] = cost
        if x0 == None:
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
