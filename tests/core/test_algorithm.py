"""Tests for kontrol.core.algorithm module"""
import numpy as np
import kontrol.core.algorithm


def test_bisection_method():
    """Tests for kontrol.core.algorithm.bisection_method()"""
    func = lambda x: x**2 - 1
    x1 = 0
    x2 = 3
    val = 0
    xm = kontrol.core.algorithm.bisection_method(func, x1, x2, val)
    assert np.isclose(func(xm), val, atol=1e-5)

    # test log_center
    x1 = 1e-6  # logarithmic center doesn't work with 0 or negative numbers
    xm = kontrol.core.algorithm.bisection_method(
        func, x1, x2, val, log_center=True)
    assert np.isclose(func(xm), val, atol=1e-5)

    # test maxiter
    maxiter = 1
    xm = kontrol.core.algorithm.bisection_method(
        func, x1, x2, val, maxiter=maxiter)
    assert xm is None
