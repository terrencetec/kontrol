"""Tests for kontrol.curvefit.transfer_function_fit module."""
import control
import numpy as np

import kontrol.curvefit


def test_spectrum_zpk_fit():
    # Prepare data
    s = control.tf("s")
    tf = 1 / (s/(2*np.pi*1) + 1)
    xdata = np.linspace(0.01, 10, 10000)
    f = xdata
    ydata = abs(tf(1j*2*np.pi*f))

    # Prepare model
    nzero = 0
    npole = 1
    model = kontrol.curvefit.model.SimpleZPK(nzero, npole)

    # Fit
    tf_fit = kontrol.curvefit.SpectrumZPKFit()
    tf_fit.xdata = xdata
    tf_fit.ydata = ydata
    tf_fit.model = model
    tf_fit.fit()
    assert np.allclose(tf_fit.optimized_args, [1, 1], rtol=1e-3)

    model = kontrol.curvefit.model.SimpleZPK(nzero, npole, log_args=True)
    tf_fit.model = model
    tf_fit.fit()
    assert np.allclose(10**tf_fit.optimized_args, [1, 1], rtol=1e-3)

def test_spectrum_tf_fit():
    # Prepare data
    s = control.tf("s")
    tf = 1 / (s/(2*np.pi*1) + 1)
    xdata = np.linspace(0.01, 10, 10000)
    f = xdata
    ydata = abs(tf(1j*2*np.pi*f))

    # Prepare model
    nzero = 0
    npole = 1
    model = kontrol.curvefit.model.TransferFunctionModel(nzero, npole)

    # Fit
    tf_fit = kontrol.curvefit.SpectrumTFFit()
    tf_fit.xdata = xdata
    tf_fit.ydata = ydata
    tf_fit.model = model
    tf_fit.num0 = [1]
    tf_fit.den0 = [1, 1]
    tf_fit.fit()
    tf_fitted = tf_fit.model.tf.minreal()
    tf_fitted_args = np.append(tf_fitted.num[0][0], tf_fitted.den[0][0])
    correct_args = np.append(tf.minreal().num[0][0], tf.minreal().den[0][0])
    assert np.allclose(tf_fitted_args, correct_args, rtol=1e-3)

    model = kontrol.curvefit.model.TransferFunctionModel(
        nzero, npole, log_args=True)
    tf_fit.model = model
    tf_fit.fit()
    tf_fitted = tf_fit.model.tf.minreal()
    tf_fitted_args = np.append(tf_fitted.num[0][0], tf_fitted.den[0][0])
    assert np.allclose(tf_fitted_args, correct_args, rtol=1e-3)


def test_spectrum_fit():
    """Test for kontrol.curvifit.spectrum_fit.spectrum_fit()"""
    s = control.tf("s")
    tf = (s**2+2*s+3)/(s**2+4*s+5)
    xdata = np.logspace(-3, 3, 1024)
    ydata = abs(tf(1j*2*np.pi*xdata))
    order = 2
    # fit = kontrol.curvefit.spectrum_fit(
    #     xdata, ydata, nzero=order, npole=order)
    # fit, zpk_fit = kontrol.curvefit.spectrum_fit(
    #     xdata, ydata, nzero=order, npole=order, return_zpk_fit=True)
    # assert isinstance(zpk_fit, kontrol.curvefit.SpectrumZPKFit)
    # fit, tf_fit = kontrol.curvefit.spectrum_fit(
    #     xdata, ydata, nzero=order, npole=order, return_tf_fit=True)
    # assert isinstance(tf_fit, kontrol.curvefit.SpectrumTFFit)
    fit, zpk_fit, tf_fit = kontrol.curvefit.spectrum_fit(
        xdata, ydata, nzero=order, npole=order,
        return_zpk_fit=True, return_tf_fit=True)
    print(fit)
    assert isinstance(tf_fit, kontrol.curvefit.SpectrumTFFit)
    assert isinstance(zpk_fit, kontrol.curvefit.SpectrumZPKFit)
    assert np.allclose(fit.num[0][0], [1, 2, 3], rtol=1e-3)
    assert np.allclose(fit.den[0][0], [1, 4, 5], rtol=1e-3)
