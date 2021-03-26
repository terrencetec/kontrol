"""Tests for kontrol.core.frequency_series.frequency_series
"""
import numpy as np
import control

import kontrol.core.frequency_series.frequency_series
import kontrol.core.frequency_series.noise_models
import kontrol.controlutils


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

    fs = kontrol.core.frequency_series.frequency_series.FrequencySeries(f, x)

    fs.fit_empirical(
        model=model, optimizer_kwargs={"options":{"maxfev":100000}})
    fs.fit_zpk(order=1)
    fs.fit_tf()

    tf_correct = control.tf([1/(2*np.pi*10), 1], [1/(2*np.pi*1), 1])
    assert kontrol.controlutils.check_tf_equal(tf_correct, fs.tf)
