"""Test Kontrol's transfer function class. [Not really testing]
"""
import os

import control
import numpy as np

import kontrol
import kontrol.core.controlutils
import kontrol.regulator


def test_transfer_function_stablize():
    """Tests for kontrol.TransferFunction.stablize."""
    s = control.tf("s")
    tf_unstable = (s-2) / (s-1) / (s**2-s-1)
    kontrol_tf = kontrol.TransferFunction(tf_unstable)
    kontrol_tf.stabilize()
    positive_real_pole_exist = any(kontrol_tf.poles().real > 0)
    positive_real_zero_exist = any(kontrol_tf.zeros().real > 0)
    assert all([not positive_real_pole_exist, not positive_real_zero_exist]) 


def test_transfer_function_foton():
    tf = control.tf([1], [2, 3])
    kontrol_tf = kontrol.TransferFunction(tf)

    n_correct = "zpk([],[0.238732414637843],0.3333333333333333,\"n\")"
    kontrol_tf_foton_n = kontrol_tf.foton(root_location="n")
    f_correct = "zpk([],[-0.238732414637843],0.5,\"f\")"
    kontrol_tf_foton_f = kontrol_tf.foton(root_location="f")
    s_correct = "zpk([],[-1.5],0.5,\"s\")"
    kontrol_tf_foton_s = kontrol_tf.foton(root_location="s")
    rpoly_correct = "rpoly([1.0],[1.0;1.5],0.5)"
    kontrol_tf_foton_rpoly = kontrol_tf.foton(expression="rpoly")
    ## FIXME Make better comparison
    # assert all([
    #     kontrol_tf_foton_n==n_correct,
    #     kontrol_tf_foton_f==f_correct,
    #     kontrol_tf_foton_s==s_correct,
    #     kontrol_tf_foton_rpoly==rpoly_correct,])


def test_transfer_function_save_load():
    path = "tf_test.pkl"
    tf = control.ss2tf(control.rss(19))
    tf = kontrol.TransferFunction(tf)
    tf.save(path)
    # test exception
    try:
        tf.save(path, overwrite=False)
        raise
    except FileExistsError:
        pass

    tf2 = kontrol.load_transfer_function(path=path)
    os.remove(path)
    assert kontrol.core.controlutils.check_tf_equal(tf, tf2)

    # test for len(den) > len(num) case
    s = control.tf("s")
    tf3 = (s**2 + 2*s + 3) / (s + 3.14)
    tf3 = kontrol.TransferFunction(tf3)
    tf3.save(path)
    tf4 = kontrol.load_transfer_function(path)
    os.remove(path)
    assert kontrol.core.controlutils.check_tf_equal(tf3, tf4)

    # test file not found exception
    try:
        kontrol.load_transfer_function("File_that_probably_doesnt_exist.pkl")
        raise
    except FileNotFoundError:
        pass


def test_transfer_function_clean():
    """Tests for kontrol.TransferFunction.clean()
    """
    num = [1e-9, 1, 2, 3]
    den = [1e-9, 2, 3, 4]
    tf = control.tf(num, den)
    tf = kontrol.TransferFunction(tf)
    tf.clean()
    assert len(tf.num[0][0]) == 3
    assert len(tf.den[0][0]) == 3


def test_notch():
    """Tests for kontrol.transfer_function.notch.Notch class"""
    frequency = np.random.random()
    q = np.random.randint(1, 100)
    depth = np.random.randint(1, 100)
    depth_db = 20*np.log10(depth)

    # Test depth exception
    try:
        kontrol.Notch(frequency, q)
        raise
    except ValueError:
        pass

    notch = kontrol.Notch(frequency, q, depth)
    notch_db = kontrol.Notch(
        frequency, q, depth_db=depth_db)
    correct_notch = kontrol.regulator.predefined.notch(frequency, q, depth)
    assert kontrol.core.controlutils.check_tf_equal(correct_notch, notch)
    assert kontrol.core.controlutils.check_tf_equal(correct_notch, notch_db)

    # Test setters
    notch = kontrol.Notch(1, 2, 3)
    notch.frequency = frequency
    notch.q = q
    notch.depth = depth
    assert kontrol.core.controlutils.check_tf_equal(correct_notch, notch)

    # Test setter exceptions
    try:
        notch.frequency = -1
        raise
    except ValueError:
        pass
    try:
        notch.q = 0.1
        raise
    except ValueError:
        pass
    try:
        notch.depth = -1
        raise
    except ValueError:
        pass
    
    # Foton. Test for error only, won't check accuracy.
    notch.foton()
