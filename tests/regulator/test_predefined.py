"""Tests for kontrol.regulator.predefined module"""
import control
import numpy as np

import kontrol.core.controlutils
import kontrol.regulator


def test_pid():
    """Tests for kontrol.regulator.predefined.pid()"""
    s = control.tf("s")
    kp = np.random.random()
    ki = np.random.random()
    kd = np.random.random()
    correct_pid = kp + ki/s + kd*s
    kontrol_pid = kontrol.regulator.predefined.pid(kp=kp, ki=ki, kd=kd)
    assert kontrol.core.controlutils.check_tf_equal(correct_pid, kontrol_pid)


def test_low_pass():
    """Tests for kontrol.regulator.predefined.low_pass()"""
    s = control.tf("s")
    order = np.random.randint(1, 10)
    fc = np.random.random()
    wc = 2*np.pi*fc
    correct_low_pass = (wc / (s+wc))**order
    kontrol_low_pass = kontrol.regulator.predefined.low_pass(fc, order)
    assert kontrol.core.controlutils.check_tf_equal(
        correct_low_pass, kontrol_low_pass)


def test_notch():
    """Tests for kontrol.regulator.predefined.notch()"""
    # Try exception
    try:
        kontrol.regulator.predefined.notch(1, 1)
        raise
    except ValueError:
        pass
    s = control.tf("s")
    depth = 10
    depth_db = 20*np.log10(depth)
    frequency = np.random.random()
    wn = 2*np.pi*frequency
    q = np.random.randint(1, 100)
    correct_notch = ((s**2 + wn/(q/2*depth)*s + wn**2)
                     / (s**2 + wn/(q/2)*s + wn**2))
    notch = kontrol.regulator.predefined.notch(frequency, q, depth)
    notch_db = kontrol.regulator.predefined.notch(
        frequency, q, depth_db=depth_db)
    assert kontrol.core.controlutils.check_tf_equal(
        correct_notch, notch)
    assert kontrol.core.controlutils.check_tf_equal(
        correct_notch, notch_db)

