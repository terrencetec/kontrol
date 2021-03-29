"""Test Kontrol's transfer function class. [Not really testing]
"""
import control

import kontrol.core.transfer_function


def test_transfer_function_foton():
    tf = control.tf([1], [2, 3])
    kontrol_tf = kontrol.core.transfer_function.TransferFunction(tf)
    n_correct = "zpk([],[0.238732414637843],0.3333333333333333,\"n\")"
    kontrol_tf_foton_n = kontrol_tf.foton
    kontrol_tf.foton = "f"
    f_correct = "zpk([],[-0.238732414637843],-0.5,\"f\")"
    kontrol_tf_foton_f = kontrol_tf.foton
    kontrol_tf.foton = "s"
    s_correct = "zpk([],[-1.5],-0.5,\"s\")"
    kontrol_tf_foton_s = kontrol_tf.foton
    assert all([
        kontrol_tf_foton_n==n_correct,
        kontrol_tf_foton_f==f_correct,
        kontrol_tf_foton_s==s_correct])
