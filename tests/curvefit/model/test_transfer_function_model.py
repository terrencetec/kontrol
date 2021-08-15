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
