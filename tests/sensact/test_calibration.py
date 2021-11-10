"""Tests for kontrol.sensact.calibration submodule"""
import numpy as np
import scipy.special

import kontrol.sensact


def test_calibrate():
    """Tests for kontrol.sensact.calibration.calibrate"""
    # Test method="linear"
    xdata = np.linspace(-1, 1, 1000)
    m = np.random.random()
    c = np.random.random()
    ydata = m*xdata + c

    ## Tests exception
    try:
        kontrol.sensact.calibrate(xdata=xdata, ydata=ydata, method="abc")
        raise
    except ValueError:
        pass

    slope, intercept, linear_range, model = kontrol.sensact.calibrate(
        xdata=xdata, ydata=ydata, method="linear", return_linear_range=True,
        return_model=True)
    
    assert np.allclose([m, c], [slope, intercept])
    assert np.allclose(ydata, model(xdata))

    # Test methor="erf"
    xdata = np.linspace(-3, 3, 1000)
    a = 1
    b = 1
    c = 0
    d = 0
    ydata = a*scipy.special.erf(b*(xdata-c)) + d
    slope, intercept, linear_range, model = kontrol.sensact.calibrate(
        xdata=xdata, ydata=ydata, method="erf", return_linear_range=True,
        return_model=True)

    assert np.allclose(
        [model.amplitude, model.slope, model.x_offset, model.y_offset],
        [a, b, c, d], rtol=1e-3, atol=1e-3)
    assert np.allclose(model(xdata), ydata, rtol=1e-3, atol=1e-3)
    
