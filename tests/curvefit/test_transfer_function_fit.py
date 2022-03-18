"""Tests for kontrol.curvefit.transfer_function_fit module."""
import control
import numpy as np

import kontrol.curvefit


def test_transfer_function_fit():
    # Prepare data
    s = control.tf("s")
    tf = 1 / (s/(2*np.pi*1) + 1)
    xdata = np.linspace(0.01, 10, 10000)
    f = xdata
    ydata = tf(1j*2*np.pi*f)

    # Prepare model
    nzero = 0
    npole = 1
    model = kontrol.curvefit.model.SimpleZPK(nzero, npole)

    # Prepare initial guess
    x0 = [2, 2]  # Can't be zero....

    # Fit
    tf_fit = kontrol.curvefit.TransferFunctionFit()
    tf_fit.xdata = xdata
    tf_fit.ydata = ydata
    tf_fit.model = model
    tf_fit.x0 = x0
    tf_fit.fit()
    assert np.allclose(tf_fit.optimized_args, [1, 1], rtol=1e-3)

    options = {"maxiter": 1000, "maxfev": 1000, "adaptive": False}
    optimizer_kwargs = {"x0": x0}
    tf_fit = kontrol.curvefit.TransferFunctionFit(
        optimizer_kwargs=optimizer_kwargs, options=options)
    tf_fit.xdata = xdata
    tf_fit.ydata = ydata
    tf_fit.model = model
    tf_fit.fit()
    assert np.allclose(tf_fit.optimized_args, [1, 1], rtol=1e-3)
