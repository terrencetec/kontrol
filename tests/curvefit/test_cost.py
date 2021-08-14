"""Tests for kontrol.curvefit.cost
"""
import numpy as np
import kontrol.curvefit
from kontrol.core.math import mse

def test_cost():
    def model(x, args):
        return args[0]*x**2
    xdata = np.linspace(-1, 1, 1024)
    args = [1]
    ydata = model(xdata, args)
    error_func = mse
    cost = kontrol.curvefit.Cost(error_func=error_func)
    kwargs = {"weight": np.ones_like(ydata)}
    cost.error_func_kwargs = kwargs
    _cost = cost(args, model=model, xdata=xdata, ydata=ydata)
    assert not _cost
