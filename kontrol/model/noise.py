"""Noise model reference"""

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
