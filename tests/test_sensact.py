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

def test_optical_lever_sensing_matrix():
    # Old SRM optical lever sensing matrix from my old scripts
    correct_matrix = np.array([
        [-0.08378354, 0.01293162, -3.27137886, 0.07679314],
        [2.2622183, 0.01609096, 1.33690529, -0.03138284],
        [-0.01851529, 3.07431463, 0, 0]
    ])
    r = (990+300+157)/1000
    alpha_v = 36.9*np.pi/180
    alpha_h = 0*np.pi/180
    r_v = r
    r_h = r*np.cos(alpha_v)
    r_lens_v = (990+300+50+40)/1000
    f = 300/1000
    d_v = r_lens_v*f/(r_lens_v-f)
    phi_tilt = -0.375*np.pi/180
    phi_len = 1.3*np.pi/180
    delta_y = 0.037
    delta_x = -0.0044
    kontrol_ol2eul = kontrol.OpticalLeverSensingMatrix(
        r_h=r_h, r_v=r_v, alpha_h=alpha_h, alpha_v=alpha_v,
        r_lens_v=r_lens_v, d_v=d_v, f=f, phi_tilt=phi_tilt, phi_len=phi_len,
        delta_y=delta_y, delta_x=delta_x
    )
    calibration = np.array([0.006547, 0.007115, 0.001075, 0.001112]) # mm/count
    calibration = np.diag(calibration)*1000
    assert np.allclose(kontrol_ol2eul@calibration, correct_matrix)
