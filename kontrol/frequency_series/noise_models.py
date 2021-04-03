"""Noise models for empirical fitting.
"""
import numpy as np


def piecewise_noise(f, n0, exp=[0], fc=[0]):
    """Piecewise noise specified corner frequencies and exponents

    Parameters
    ----------
    f: list of int/float or numpy.ndarray
        The frequency axis of the noise.
    n0: int/float
        The noise level at 1 Hz with the first exponent.
    exp: list of int/float
        The list of exponents of each section of noise separated by the
        corner frequencies.
    fc: list of int/float
        The list of corner frequencies in increaing order. The length of
        fc must be 1 less then the length of exp

    Returns
    -------
    noise: numpy.ndarray
        The piecewise noise array.
    """
    if n0<0:
        n0 = -n0
    list(fc)
    if fc[-1] < np.inf:
        fc.append(np.inf)
    for i in range(len(fc)):
        if fc[i]<0:
            fc[i] = -fc[i]
    noise = np.zeros_like(f)
    fc_index = 0
    for i in range(len(f)):
        if f[i] >= fc[fc_index]:
            fc_index += 1
            n0 = n0 * fc[fc_index-1]**(exp[fc_index-1]-exp[fc_index])

        noise[i] = n0 * f[i]**exp[fc_index]
        # print(fc_index)
    return np.array(noise)


def lvdt_noise(f, n0=8e-3, fc=4.5, exp1=-0.5, exp2=0.):
    """LVDT noise model.

    Parameters
    ----------
    f: array
        Frequency axis.
    n0: float, optional.
        The noise level at 1 Hz with the first exponent. In um/rtHz.
        Defaults to the typical value 8e-3.
    fc: float, optional.
        Defaults to the typical value 4.5 Hz.
        The corner frequency at which the exponent changes.
    exp1: float, optional
        The exponent of the frequency dependency before the corner frequency.
        Defaults -0.5.
    exp2: float, optional
        The exponent of the frequency dependency after the corner frequency.
        Defaults 0.

    Returns
    -------
    noise: numpy.ndarray
        The LVDT noise frequency series.

    Notes
    -----
    The LVDT noise noise typically has a :math:`f^{-0.5}` dependency
    before the corner frequency and is flat after that.
    """
    return piecewise_noise(f, n0, exp=[exp1, exp2], fc=[fc])


def geophone_noise(f, n0=2e-6, fc=0.9, exp1=-3.5, exp2=-1.):
    """Geophone noise model.

    Parameters
    ----------
    f: array
        Frequency axis
    n0: float, optional
        The noise level at 1 Hz with the first exponent. In um/rtHz.
        Defaults to the typical value 2e-6.
    fc: float, optional
        The corner frequency at which the exponent changes.
        Defaults to the typical value 0.9.
    exp1: float, optional
        The exponent of the frequency dependency before the corner frequency.
        Defaults -3.5.
    exp2: float, optional
        The exponent of the frequency dependency after the corner frequency.
        Defaults -1.

    Returns
    -------
    noise: numpy.ndarray
        The geophone noise frequency series.

    Notes
    -----
    The geophone noise noise typically has a :math:`f^{-3.5}` dependency
    before the corner frequency and has a :math:`f^{-1}` dependency after that.
    """
    return piecewise_noise(f, n0, exp=[exp1, exp2], fc=[fc])
