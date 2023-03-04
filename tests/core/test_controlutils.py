"""Tests for control utility functions.
"""
import control
import numpy as np

import kontrol.core.controlutils


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
    tf = kontrol.core.controlutils.tfmatrix2tf(tfmatrix)
    assert all([
        check_tf_equal(tf[0, 0], tf1), check_tf_equal(tf[0, 1], tf2),
        check_tf_equal(tf[0, 2], tf3), check_tf_equal(tf[1, 0], tf4),
        check_tf_equal(tf[1, 1], tf5), check_tf_equal(tf[1, 2], tf6)
    ])


def test_zpk():
    kontrol_zpk = kontrol.core.controlutils.zpk(
        zeros=[1, 2, 3], poles=[4, 5, 6], gain=7, unit="omega")
    s = control.tf("s")
    zpk = 7 * (s/1 + 1)*(s/2 + 1)*(s/3 + 1) / ((s/4 + 1)*(s/5 + 1)*(s/6 + 1))
    assert check_tf_equal(kontrol_zpk, zpk)


def test_convert_unstable_tf():
    unstable_tf = kontrol.core.controlutils.zpk(
        zeros=[1, 2, -3], poles=[4, 5, -6], gain=7, unit="omega")
    stable_tf = kontrol.core.controlutils.zpk(
        zeros=[1, 2, 3], poles=[4, 5, 6], gain=7, unit="omega")
    converted_tf = kontrol.core.controlutils.convert_unstable_tf(unstable_tf)
    assert check_tf_equal(converted_tf, stable_tf)


def test_check_tf_equal():
    tf1 = kontrol.core.controlutils.zpk(
        zeros=[1, 2, 3], poles=[4, 5, 6], gain=7, unit="omega")
    tf2 = kontrol.core.controlutils.zpk(
        zeros=[1, 2, 3], poles=[4, 5, 6], gain=7, unit="omega")
    assert kontrol.core.controlutils.check_tf_equal(tf1, tf2)


def test_generic_tf():
    f = np.logspace(-2, 3, 1000)
    s = 1j*2*np.pi*f
    x_correct = 2 * ((s/0.1+1)
                /(s/1+1)
                *(s**2+10/100*s+10**2) / 10**2
                /(s**2+100/1000*s+100**2) * 100**2
                /(s/5+1))
    zeros = [0.1]
    poles = [1, 5]
    zeros_wn = [10]
    zeros_q = [100]
    poles_wn = [100]
    poles_q = [1000]
    dcgain = 2
    unit = "s"
    sos = kontrol.core.controlutils.generic_tf(
        zeros, poles, zeros_wn, zeros_q, poles_wn, poles_q, dcgain, unit)
    assert np.allclose(sos(s), x_correct)


def test_outliers():
    omega = np.logspace(-1, 1)
    s = control.tf("s")
    tf = 2 * ((s/0.1+1)
                /(s/1+1)
                *(s**2+10/100*s+10**2) / 10**2
                /(s**2+100/1000*s+100**2) * 100**2
                /(s/5+1))
    outlier_zeros, outlier_poles = kontrol.core.controlutils.outliers(
        tf=tf, f=omega, unit="omega")
    outlier_zeros_correct = [-0.05+9.999875j, -0.05-9.999875j]
    outlier_poles_correct = [-0.05+99.9999875j, -0.05-99.9999875j]
    assert np.all(
        [np.allclose(outlier_zeros, outlier_zeros_correct),
         np.allclose(outlier_poles, outlier_poles_correct)])


def test_outlier_exists():
    omega=np.logspace(-1, 1)
    s = control.tf("s")
    tf = 2 * ((s/0.1+1)
                /(s/1+1)
                *(s**2+10/100*s+10**2) / 10**2
                /(s**2+100/1000*s+100**2) * 100**2
                /(s/5+1))
    first_test = kontrol.core.controlutils.outlier_exists(
        tf=tf, f=omega, unit="omega")
    omega = np.logspace(-2, 3)
    second_test = kontrol.core.controlutils.outlier_exists(
        tf=tf, f=omega, unit="omega")
    assert np.all([first_test, not second_test])


def test_tf_order_split():
    """Tests for kontrol.core.controlutils.tf_order_split()"""
    max_order = 5
    tf_order = 50
    tf = control.ss2tf(control.rss(tf_order))
    tf_split_list = kontrol.core.controlutils.tf_order_split(
        tf, max_order=max_order)
    tf_combined = np.prod(tf_split_list)
    f = np.logspace(-3, 3, 100000)
     
    assert np.allclose(tf(1j*2*np.pi*f), tf_combined(1j*2*np.pi*f))
    
    for tf_ in tf_split_list:
        if len(tf_.pole()) > max_order or len(tf_.zero()) > max_order:
            print(tf_.pole())
            print(tf_.zero())
            assert False


def test_clean_tf():
    """Tests for kontrol.core.controlutils.clean_tf()
    """
    num = [1e-9, 1, 2, 3]
    den = [1e-9, 2, 3, 4]
    tf = control.tf(num, den)
    tf_cleaned = kontrol.core.controlutils.clean_tf(tf)
    assert len(tf_cleaned.num[0][0]) == 3
    assert len(tf_cleaned.den[0][0]) == 3


def test_clean_tf2():
    """Tests for kontrol.core.controlutils.clean_tf2()"""
    tol_order = 5
    s = control.tf("s")
    tf = ((s+1)*(s**2+10/3*s+10**2)*(s+100)*(s+1e9)*s
          / (s*(s+0.1)*(s**2+30/3*s+30**2)*(s+300)*(s+2e9)))
    tf_cleaned = kontrol.core.controlutils.clean_tf2(tf)
    assert len(tf_cleaned.num[0][0]) == 5
    assert len(tf_cleaned.den[0][0]) == 5


def test_clean_tf3():
    """Tests for kontrol.core.controlutils.clean_tf3()
    """
    num = [1e-9, 1, 2, 3]
    den = [1e-9, 2, 3, 4]
    tf = control.tf(num, den)
    tf_cleaned = kontrol.core.controlutils.clean_tf3(tf)
    assert len(tf_cleaned.num[0][0]) == 3
    assert len(tf_cleaned.den[0][0]) == 3


def check_tf_equal(tf1, tf2):
    zeros_close = np.allclose(tf1.zero(), tf2.zero())
    poles_close = np.allclose(tf1.pole(), tf2.pole())
    gain_close = np.allclose(tf1.dcgain(), tf2.dcgain())
    return all([zeros_close, poles_close, gain_close])

