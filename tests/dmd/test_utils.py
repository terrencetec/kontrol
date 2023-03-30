"""Tests for kontrol.dmd.utils module"""
import numpy as np

import kontrol.dmd


def test_hankel():
    """Tests for kontrol.dmd.utils.hankel()"""
    order = 3
    array = [1, 2, 3, 4, 5]
    array_correct = [
        [1, 2, 3],
        [2, 3, 4],
        [3, 4, 5]
    ]
    array_hankel = kontrol.dmd.utils.hankel(array=array, order=order)
    assert np.allclose(array_hankel, array_correct)


def test_auto_truncate():
    """Tests for kontrol.dmd.utils.auto_truncate()"""
    sigma = [5, 4, 3, 2, 1]
    truncation_value = kontrol.dmd.auto_truncate(sigma, threshold=0.9)
    assert truncation_value==4
