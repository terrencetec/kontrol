"""Test Kontrol's transfer function class. [Not really testing]
"""
import control

import kontrol.core.transfer_function


def test_transfer_function_foton():
    tf = control.tf([1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11])
    kontrol_tf = kontrol.core.transfer_function.TransferFunction(tf)
    kontrol_tf.foton
