"""Tests for kontrol.curvefit.error_func
"""
import numpy as np

import kontrol.curvefit.error_func


def test_mse():
    correct = 1
    a = np.array([1, 2, 3, 4, 5])
    b = np.array([2, 3, 4, 5, 6])
    test = kontrol.curvefit.error_func.mse(a, b)
    assert correct == test


def test_log_mse():
    correct = 1
    a = np.array([1, 10, 100, 1000, 10000])
    b = np.array([10, 100, 1000, 10000, 100000])
    test = kontrol.curvefit.error_func.log_mse(a, b)
    test_cal = correct==test

    # Test handling of zero value array
    correct=0
    a = np.zeros(10)
    b = np.ones(10)
    test_zero_value_array_ab = kontrol.curvefit.error_func.log_mse(
        a, b, small_multiplier=1)
    test_zero_value_array_ba = kontrol.curvefit.error_func.log_mse(
        b, a, small_multiplier=1)
    test_zero_handle = (correct==test_zero_value_array_ab and
                        correct==test_zero_value_array_ba)

    assert np.all([test_cal, test_zero_handle])


def test_noise_error():
    correct = 1
    a = np.array([1, 10, 100, 1000, 10000])
    b = np.array([10+0j, 100+0j, 1000+0j, 10000+0j, 100000+0j])
    test = kontrol.curvefit.error_func.noise_error(a, b)
    test_cal = correct==test
    assert test_cal


def test_spectrum_error():
    correct = 1
    a = np.array([1, 10, 100, 1000, 10000])
    b = np.array([10+0j, 100+0j, 1000+0j, 10000+0j, 100000+0j])
    test = kontrol.curvefit.error_func.spectrum_error(a, b)
    test_cal = correct==test
    assert test_cal
