"""Tests for common math library
"""
import numpy as np

import kontrol.common.math


def test_mse():
    correct = 1
    a = np.array([1, 2, 3, 4, 5])
    b = np.array([2, 3, 4, 5, 6])
    test = kontrol.common.math.mse(a, b)
    assert correct == test


def test_log_mse():
    correct = 1
    a = np.array([1, 10, 100, 1000, 10000])
    b = np.array([10, 100, 1000, 10000, 100000])
    test = kontrol.common.math.log_mse(a, b)
    assert correct == test


def test_quad_sum():
    correct = np.array([1, 5, np.sqrt(1**2 + 4**2)]).astype(float)
    a = np.array([1, 3, 1]).astype(float)
    b = np.array([0, 4, 4]).astype(float)
    test = kontrol.common.math.quad_sum(a, b)
    assert np.allclose(correct, test)
