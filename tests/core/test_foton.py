"""Test for kontrol-foton utilities.
"""
import control
import numpy as np

import kontrol.core.foton


s = control.tf("s")
tf_test = np.pi*s*(s+3*np.pi)/(s+np.pi)/(s**2+s+5**2)/(s+1.5)**2
zpk_str_n = ('zpk([-0.0;1.5],[0.23873239741798644;0.23873243185770118;'
             '0.4999999999999977;0.07957747154594766+i*0.7917858446492736;'
             '0.07957747154594766+i*-0.7917858446492736],'
             '1.0527578027828701,'
             '"n")')
rpoly_str = ('rpoly([1.0;9.42477796076938;0.0],[1.0;7.141592653589788;'
             '42.816370614359144;172.283177771091;298.93803248981106;'
             '176.7145867644253],3.141592653589793)')

def test_tf2foton():
    ## test raises
    try:
        kontrol.core.foton.tf2foton(tf_test, expression="a")
    except ValueError:
        pass
    zpk_str_n_test = kontrol.core.foton.tf2foton(
        tf_test, expression="zpk", root_location="n")
    rpoly_str_test = kontrol.core.foton.tf2foton(tf_test, expression="rpoly")

    # assert all([zpk_str_n_test==zpk_str_n, rpoly_str_test==rpoly_str])
    # FIXME Use better comparison. 

def test_tf2zpk():
    ## test raises
    try:
        kontrol.core.foton.tf2zpk(1/s**20)
    except ValueError:
        pass
    try:
        kontrol.core.foton.tf2zpk(s**20)
    except ValueError:
        pass
    try:
        kontrol.core.foton.tf2zpk(tf_test, root_location="a")
    except ValueError:
        pass

    ## These should work
    kontrol.core.foton.tf2zpk(1/s**19)
    kontrol.core.foton.tf2zpk(s**21/s**20)

    ## test "n" expression
    zpk_str_n_test = kontrol.core.foton.tf2zpk(tf_test, root_location="n")

    # assert zpk_str_n_test == zpk_str_n
    # FIXME Use better comparison. 

def test_tf2rpoly():
    ## test raises
    try:
        kontrol.core.foton.tf2rpoly(1/s**20)
    except ValueError:
        pass
    try:
        kontrol.core.foton.tf2rpoly(s**20)
    except ValueError:
        pass

    ## These should work
    kontrol.core.foton.tf2rpoly(1/s**19)
    kontrol.core.foton.tf2rpoly(s**21/s**20)

    rpoly_str_test = kontrol.core.foton.tf2rpoly(tf_test)

    # assert rpoly_str_test == rpoly_str
    # FIXME Use better comparison. 
