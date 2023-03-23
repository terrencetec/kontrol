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
