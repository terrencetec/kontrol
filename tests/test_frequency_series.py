"""Tests for kontrol.frequency_series.frequency_series
"""
import numpy as np
import control

import kontrol
import kontrol.core.controlutils
import kontrol.frequency_series.noise_models


def test_frequency_series():
    np.random.seed(123)

    f = np.linspace(1e-1, 1e2, 100)
    s = 1j*2*np.pi*f

    ##  Lag filter at 1 & 10 Hz.
    def model(f, f1, f2):
        s = 1j*2*np.pi*f
        tf = (s/(2*np.pi*f2) + 1)/(s/(2*np.pi*f1) + 1)
        x = abs(tf)
        return x

    x = model(f, 1, 10)

    fs = kontrol.FrequencySeries(f=f, x=x)

    fs.fit_empirical(
        model=model, optimizer_kwargs={"options":{"maxfev":100000}})
    fs.fit_zpk(order=1, padding=True)
    fs.fit_tf()

    tf_correct = control.tf([1/(2*np.pi*10), 1], [1/(2*np.pi*1), 1])
    assert kontrol.core.controlutils.check_tf_equal(
        tf_correct, fs.tf, allclose_kwargs={"rtol":1e-2})


def test_noise_models():
    f = np.logspace(-2, 2, 1000)
    lvdt_noise = kontrol.frequency_series.noise_models.lvdt_noise(f=f)
    geophone_noise = kontrol.frequency_series.noise_models.geophone_noise(f=f)
    lvdt_noise_ = kontrol.frequency_series.noise_models.piecewise_noise(
        f=f, n0=8e-3, exp=[-0.5, 0], fc=[4.5])
    geophone_noise_ = kontrol.frequency_series.noise_models.piecewise_noise(
        f=f, n0=2e-6, exp=[-3.5, -1], fc=[0.9])
    assert all([
        np.allclose(lvdt_noise, lvdt_noise_),
        np.allclose(geophone_noise, geophone_noise_)])
