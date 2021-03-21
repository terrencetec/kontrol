"""Simple maths for complementary filter synthesis
"""
import numpy as np

from . import conversion


def log_mse(x1, x2):
    """Returns the logarithmic mean square error between x1 and x2.

    Parameters
    ----------
    x1: array
        Array 1
    x2: array
        Array 2

    Returns
    -------
    float
        The logarithmic mean square error between x1 and x2.
    """
    return np.mean((np.log(x1)-np.log(x2))**2)


def zpk_fit_cost(zpk_args, f, noise_asd):
    """The cost function for fitting a noise ASD with zpk.

    Parameters
    ----------
    zpk_args: array
        A 1-D list of zeros, poles, and gain.
        Zeros and poles are in unit of Hz.
    f: array
        The frequency axis.
    noise_asd: array
        The noise ASD.

    Returns
    -------
    The logarithmic mean square error between the noise ASD and the magnitude
    of ZPK model.
    """
    zpk = conversion.args2zpk(f=f, zpk_args=zpk_args)
    return log_mse(x1=noise_asd, x2=abs(zpk))


def tf_fit_cost(log_tf_args, f, noise_asd):
    """Cost for fitting transfer function to the noise ASD

    Parameters
    ----------
    log_tf_args: array
        A list of numerator and denominator coefficients, "logged".
    f: array
        The frequency axis.
    noise_asd: array
        The noise ASD.

    Returns
    -------
    The logarithmic mean square error between the noise ASD and the magnitude
    of TF model.
    """
    tf_args = np.exp(log_tf_args)
    tf = conversion.args2tf(f=f, tf_args=tf_args)
    return log_mse(x1=noise_asd, x2=abs(tf))
