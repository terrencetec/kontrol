"""Test for complementary filter class
"""
import control
import numpy as np

import kontrol
import kontrol.core.controlutils
import kontrol.frequency_series.noise_models


def test_complementary_filter():
    omega = np.logspace(-2,2,1000)
    f = omega/2/np.pi
    tf_noise1 = control.tf([1/10, 1], [1/0.1, 1]) *10
    tf_noise2 = control.tf([1/0.1, 1], [1/10, 1])

    comp = kontrol.ComplementaryFilter(noise1=tf_noise1, noise2=tf_noise2)
    comp.hinfsynthesis()
    tf_correct = control.tf([1, 2.08392466e+04, 1.58200377e+04, 2.53883414e+03, 1.16522184e+02], [1, 2.08679038e+04, 1.64005175e+04, 5.55127674e+03, 8.50146586e+02])


    assert kontrol.core.controlutils.check_tf_equal(
        tf_correct, comp[0, 0], allclose_kwargs={"rtol":1e-4})
