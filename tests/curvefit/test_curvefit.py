"""Test for kontrol.curvefit.CurveFit
"""
import numpy as np
import kontrol.curvefit
import scipy.optimize

def polynomial(x, args, **kwargs):
    """
    Parameters
    ----------
    x : array
        x axis
    args : array
        A list of coefficients of the polynomial

    Returns
    -------
    array
        args[0]*x**0 + args[1]*x**1 ... args[len(args)-1]*x**(len(args)-1).
    """
    poly = np.sum([args[i]*x**i for i in range(len(args))], axis=0)
    return poly

def test_curvefit():
    xdata = np.linspace(-1, 1, 1024)
    np.random.seed(123)
    random = np.random.random(3)

    ydata = polynomial(xdata, random)

    a = kontrol.curvefit.CurveFit()

    ## Catch exception
    try:
        a.fit()
    except TypeError():
        pass

    a.xdata = xdata
    a.ydata = ydata
    a.model = polynomial
    a.model_kwargs = {}
    a.cost = kontrol.curvefit.Cost(error_func=kontrol.curvefit.error_func.mse)
    a.optimizer = scipy.optimize.differential_evolution
    a.optimizer_kwargs = {
        "bounds": [(0, 1)]*len(random),
        "workers": -1,
        "maxiter": 10000,
        "updating": "deferred",}
    a.fit()
    assert np.allclose(a.optimized_args, random)
