"""Noise model reference
Model of a generic piecewise noise, LVDT noise, and Geophone noise are avaliable.
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
            The list of exponents of each section of noise separated by the \
            corner frequencies.
        fc: list of int/float
            The list of corner frequencies in increaing order. The length of \
            fc must be 1 less then the length of exp

    Returns
    -------
        noise: numpy.ndarray
            The piecewise noise array.
    """

    list(fc)
    if fc[-1] < np.inf:
        fc.append(np.inf)

    noise = np.zeros_like(f)
    fc_index = 0
    for i in range(len(f)):
        if f[i] >= fc[fc_index]:
            fc_index += 1
            n0 = n0 * fc[fc_index-1]**(exp[fc_index-1]-exp[fc_index])
        noise[i] = n0 * f[i]**exp[fc_index]
        # print(fc_index)
    return(np.array(noise))

def lvdt_noise(f, n0, fc, exp=[-0.5, 0]):
    """LVDT noise

    Parameters
    ----------
        f: list of int/float or numpy.ndarray
            The frequency axis of the noise.
        n0: int/float
            The noise level at 1 Hz with the exponent of -0.5.
        fc: int/float
            The corner frequency at which the exponent changes from -0.5 to 0.
        exp: list of float, optional.
            The exponents of the frequency dependency before and after the
            corner frequency. Defaults [-0.5, 0]
    Returns
    -------
        noise: numpy.ndarray
            The piecewise noise array.

    Notes
    -----
        The LVDT noise noise typically has a :math:`f^{-0.5}` dependency \
        before the corner frequency and is flat after that.
    """

    return(piecewise_noise(f, n0, exp=exp, fc=[fc]))

def geophone_noise(f, n0, fc, exp = [-3.5, -1]):
    """Geophone noise

    Parameters
    ----------
        f: list of int/float or numpy.ndarray
            The frequency axis of the noise.
        n0: int/float
            The noise level at 1 Hz with the exponent of -3.5.
        fc: int/float
            The corner frequency at which the exponent changes from -3.5 to -1.
        exp: list of float, optional.
            The exponents of the frequency dependency before and after the
            corner frequency. Defaults [-3.5, -1].

    Returns
    -------
        noise: numpy.ndarray
            The piecewise noise array.

    Notes
    -----
        The geophone noise noise typically has a :math:`f^{-3.5}` dependency \
        before the corner frequency and depends on :math:`f^{-1}` after that.
    """

    return(piecewise_noise(f, n0, exp=exp, fc=[fc]))
