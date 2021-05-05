"""Tests for sensors/actuators related utilities (kontrol.sensact)
"""
import numpy as np

import kontrol


def test_matrix():
    matrix = np.array([[1,2,3], [2,3,4], [3,4,5]])
    kontrol_matrix = kontrol.Matrix([[1,2,3], [2,3,4], [3,4,5]])
    assert np.array_equal(kontrol_matrix, matrix)


def test_sensing_matrix():
    ## MCo work Klog 16562 https://klog.icrr.u-tokyo.ac.jp/osl/?r=16562
    coupling_matrix = [[1, 0, 0], [0, 1, 0.07615], [0, -0.0300588, 1]]
    oplev2eul = kontrol.SensingMatrix(
        matrix=[
            [0, 0, 0, 1],
            [0.147059, 0, 0, 0],
            [0, 0.154453, 0, 0]
        ],
        coupling_matrix=coupling_matrix)
    oplev2eul_diagonalized = oplev2eul.diagonalize()
    correct_matrix = [
        [0, 0, 0, 1],
        [0.14672315, -0.01173474, 0, 0],
        [0.00441032, 0.15410027, 0, 0]
    ]  # This is not the one used finally. Just used here for testing.
    test_1 = np.allclose(oplev2eul_diagonalized, correct_matrix)
    oplev2eul_diagonalized = oplev2eul.diagonalize(coupling_matrix)
    test_2 = np.allclose(oplev2eul_diagonalized, correct_matrix)
    assert np.all([test_1, test_2])
