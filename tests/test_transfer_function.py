"""Test Kontrol's transfer function class. [Not really testing]
"""
import control

import kontrol


def test_transfer_function_stablize():
    """Tests for kontrol.TransferFunction.stablize."""
    s = control.tf("s")
    tf_unstable = (s-2) / (s-1) / (s**2-s-1)
    kontrol_tf = kontrol.TransferFunction(tf_unstable)
    kontrol_tf.stabilize()
    positive_real_pole_exist = any(kontrol_tf.pole().real > 0)
    positive_real_zero_exist = any(kontrol_tf.zero().real > 0)
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
    assert all([
        kontrol_tf_foton_n==n_correct,
        kontrol_tf_foton_f==f_correct,
        kontrol_tf_foton_s==s_correct,
        kontrol_tf_foton_rpoly==rpoly_correct,])
