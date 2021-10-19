"""Tests for kontrol.curvefit.model.transfer_function_model"""
import control
import numpy as np

import kontrol.curvefit.model


def test_transfer_function_model():
    tf = kontrol.curvefit.model.TransferFunctionModel(1, 2)
    f = np.logspace(-2, 2)
    w = 2*np.pi*f
    s = 1j*w
    ## Catch wrong xunit specification
    try:
        tf(f, xunit="abc")
    except ValueError:
        pass
    tf.args = [1, 2, 3, 4, 5, 6]
    ## Catch wrong args specification
    try:
        tf(f)
    except ValueError:
        pass
    
    tf.args = [1, 2, 3, 4, 5]
    tf_f = tf(f, xunit="Hz")
    tf_w = tf(w, xunit="rad/s")
    tf_s = tf(s, xunit="s")
    control_tf = control.tf([1, 2], [3, 4, 5])

    correct = control_tf(1j*2*np.pi*f)

    f_test = np.allclose(tf_f, correct)
    w_test = np.allclose(tf_w, correct)
    s_test = np.allclose(tf_s, correct)

    tf_test = isinstance(tf.tf, control.TransferFunction)
    tf_num_test = np.allclose(tf.tf.num[0][0], control_tf.num[0][0])
    tf_den_test = np.allclose(tf.tf.den[0][0], control_tf.den[0][0])
    assert all([f_test, w_test, s_test, tf_test, tf_num_test, tf_den_test])


def test_simple_zpk_model():
    """Tests for kontrol.curvefit.model.transfer_function_model.SimpleZPK"""
    s = control.tf("s")
    tf = 6 * ((s/(1*2*np.pi) + 1)*(s/(2*2*np.pi) + 1)
          / ((s/(3*2*np.pi) + 1) * (s/(4*2*np.pi) + 1) * (s/(5*2*np.pi)+1)))

    args = [1, 2, 3, 4, 5, 6]
    f = np.linspace(0.1, 10, 1000)
    tf_val = tf(2*np.pi*1j*f)

    kontrol_zpk = kontrol.curvefit.model.SimpleZPK(nzero=2, npole=3)

    # Catch exception
    args_wrong = [1, 2, 3, 4]
    try:
        kontrol_zpk(f, args_wrong)
        raise
    except ValueError:
        pass

    kontrol_zpk_val = kontrol_zpk(f, args)
    kontrol_zpk_tf_val = kontrol_zpk.tf(1j*2*np.pi*f)
    test1 = np.allclose(tf_val, kontrol_zpk_val)
    test2 = np.allclose(tf_val, kontrol_zpk_tf_val)
    assert all([test1, test2])


def test_complex_zpk_model():
    """Tests for kontrol.curvefit.model.transfer_function_model.ComplexZPK"""
    s = control.tf("s")
    tf = (7 * (s**2/(1*2*np.pi)**2 + 1/(1*2*np.pi*2)*s + 1)
          / (s**2/(3*2*np.pi)**2 + 1/(3*2*np.pi*4)*s + 1)
          / (s**2/(5*2*np.pi)**2 + 1/(5*2*np.pi*6)*s + 1))
    args = [1,2,  ## Zero
            3,4,  ## Poles
            5,6,
            7]  ## Gain
    f = np.linspace(0.1, 10, 1000)
    tf_val = tf(2*np.pi*1j*f)
    kontrol_zpk = kontrol.curvefit.model.ComplexZPK(
        nzero_pairs=1, npole_pairs=2)

    # Catch wrong arugment length
    args_wrong = [1, 2]
    try:
        kontrol_zpk(f, args_wrong)
        raise
    except ValueError:
        pass
    kontrol_zpk_val = kontrol_zpk(f, args)
    test1 = np.allclose(tf_val, kontrol_zpk_val)
    test2 = np.allclose(tf_val, kontrol_zpk.tf(1j*2*np.pi*f))
    assert all([test1, test2])
