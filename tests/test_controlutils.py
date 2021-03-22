"""Tests for control utility functions.
"""
import control
import numpy as np

import kontrol.controlutils


def test_tfmatrix2tf():
    tf1 = control.tf([1, 2], [3, 4, 5])
    tf2 = control.tf([6, 7], [8, 9, 10])
    tf3 = control.tf([11, 12], [13, 14, 15])
    tf4 = control.tf([1], [2, 3])
    tf5 = control.tf([3], [4, 5])
    tf6 = control.tf([5], [6, 7])
    tfmatrix = [
        [tf1, tf2, tf3],
        [tf4, tf5, tf6]
    ]
    tf = kontrol.controlutils.tfmatrix2tf(tfmatrix)
    assert all([
        check_tf_equal(tf[0, 0], tf1), check_tf_equal(tf[0, 1], tf2),
        check_tf_equal(tf[0, 2], tf3), check_tf_equal(tf[1, 0], tf4),
        check_tf_equal(tf[1, 1], tf5), check_tf_equal(tf[1, 2], tf6)
    ])


def test_zpk():
    kontrol_zpk = kontrol.controlutils.zpk(
        zeros=[1, 2, 3], poles=[4, 5, 6], gain=7, unit="omega")
    s = control.tf("s")
    zpk = 7 * (s/1 + 1)*(s/2 + 1)*(s/3 + 1) / ((s/4 + 1)*(s/5 + 1)*(s/6 + 1))
    assert check_tf_equal(kontrol_zpk, zpk)


def test_convert_unstable_tf():
    unstable_tf = kontrol.controlutils.zpk(
        zeros=[1, 2, -3], poles=[4, 5, -6], gain=7, unit="omega")
    stable_tf = kontrol.controlutils.zpk(
        zeros=[1, 2, 3], poles=[4, 5, 6], gain=7, unit="omega")
    converted_tf = kontrol.controlutils.convert_unstable_tf(unstable_tf)
    assert check_tf_equal(converted_tf, stable_tf)


def check_tf_equal(tf1, tf2):
    zeros_close = np.allclose(tf1.zero(), tf2.zero())
    poles_close = np.allclose(tf1.pole(), tf2.pole())
    gain_close = np.allclose(tf1.dcgain(), tf2.dcgain())
    return all([zeros_close, poles_close, gain_close])