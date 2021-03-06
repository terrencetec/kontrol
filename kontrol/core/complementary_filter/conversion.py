"""Conversion functions for complementary filter synthesis
"""
import control
import numpy as np


def args2zpk(f, zpk_args):
    """Returns an array of ZPK defined transfer function evaluted at frequency f.

    Parameters
    ----------
    f: array
        The frequency axis.
    zpk_args: array
        A 1-D list of zeros, poles, and gain.
        Zeros and poles are in unit of Hz.

    Returns
    -------
    zpk: array
        A complex array.
    """
    s = 1j*2*np.pi*f
    zeros = zpk_args[:int(len(zpk_args)/2)]
    poles = zpk_args[int(len(zpk_args)/2):len(zpk_args)-1]
    gain = zpk_args[-1]
    zpk = np.prod([(s/(2*np.pi*z)+1)/(s/(2*np.pi*p)+1)
                  for z,p in zip(zeros, poles)], axis=0)
    zpk *= gain
    return zpk


def args2controltf(zpk_args):
    """Convert a list of zeros, poles, and gain to control.tf

    Parameters
    ----------
    zpk_args: array
        A 1-D list of zeros, poles, and gain.
        Zeros and poles are in unit of Hz.
    """
    s = control.tf("s")
    zeros = zpk_args[:int(len(zpk_args)/2)]
    poles = zpk_args[int(len(zpk_args)/2):len(zpk_args)-1]
    gain = zpk_args[-1]
    zpk = np.prod([(s/(2*np.pi*z)+1)/(s/(2*np.pi*p)+1)
                  for z,p in zip(zeros, poles)], axis=0)
    zpk *= gain
    return zpk


def args2tf(f, tf_args):
    """Returns an array of transfer function evaluted at frequency f.

    Parameters
    ----------
    f: array
        The frequency axis.
    tf_args: array
        A 1-D list of numerator and denominator coefficients,
        from higher order to lower order.

    Returns
    -------
    array
        A complex array.
    """
    s = 1j*2*np.pi*f
    num_coef = tf_args[:int(len(tf_args)/2)]
    den_coef = tf_args[int(len(tf_args)/2):len(tf_args)]
#     print(num_coef)
#     print(den_coef)
    num = np.sum([np.flip(num_coef)[i] * s**i for i in range(len(num_coef))], axis=0)
    den = np.sum([np.flip(den_coef)[i] * s**i for i in range(len(den_coef))], axis=0)
    return num/den
