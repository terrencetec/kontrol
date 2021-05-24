"""Tests for core math library
"""
import numpy as np

import kontrol.core.math


def test_mse():
    correct = 1
    a = np.array([1, 2, 3, 4, 5])
    b = np.array([2, 3, 4, 5, 6])
    test = kontrol.core.math.mse(a, b)
    assert correct == test


def test_log_mse():
    correct = 1
    a = np.array([1, 10, 100, 1000, 10000])
    b = np.array([10, 100, 1000, 10000, 100000])
    test = kontrol.core.math.log_mse(a, b)
    test_cal = correct==test

    # Test handling of zero value array
    correct=0
    a = np.zeros(10)
    b = np.ones(10)
    test_zero_value_array_ab = kontrol.core.math.log_mse(
        a, b, small_multiplier=1)
    test_zero_value_array_ba = kontrol.core.math.log_mse(
        b, a, small_multiplier=1)
    test_zero_handle = (correct==test_zero_value_array_ab and
                        correct==test_zero_value_array_ba)

    assert np.all([test_cal, test_zero_handle])


def test_quad_sum():
    correct = np.array([1, 5, np.sqrt(1**2 + 4**2)]).astype(float)
    a = np.array([1, 3, 1]).astype(float)
    b = np.array([0, 4, 4]).astype(float)
    test = kontrol.core.math.quad_sum(a, b)
    assert np.allclose(correct, test)
