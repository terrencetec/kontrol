"""Simple maths for complementary filter synthesis
"""
import numpy as np

from . import conversion
import kontrol.common.math


def zpk_fit_cost(zpk_args, f, noise_asd, weight=None):
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
    weight: array or None, optional
        weighting function.
        If None, defaults to np.ones_like(noise_asd)

    Returns
    -------
    The logarithmic mean square error between the noise ASD and the magnitude
    of ZPK model.
    """
    zpk = conversion.args2zpk(f=f, zpk_args=zpk_args)
    return kontrol.common.math.log_mse(
        x1=noise_asd, x2=abs(zpk), weight=weight)


def tf_fit_cost(log_tf_args, f, noise_asd, weight=None):
    """Cost for fitting transfer function to the noise ASD

    Parameters
    ----------
    log_tf_args: array
        A list of numerator and denominator coefficients, "logged".
    f: array
        The frequency axis.
    noise_asd: array
        The noise ASD.
    weight: array or None, optional
        weighting function.
        If None, defaults to np.ones_like(noise_asd)

    Returns
    -------
    The logarithmic mean square error between the noise ASD and the magnitude
    of TF model.
    """
    tf_args = np.exp(log_tf_args)
    tf = conversion.args2tf(f=f, tf_args=tf_args)
    return kontrol.common.math.log_mse(x1=noise_asd, x2=abs(tf))
