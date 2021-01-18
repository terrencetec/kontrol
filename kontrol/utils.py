"""Utility functions.
Functions: quad_sum, norm2, rms, tfmatrix2tf.
"""

import numpy as np
import control
from control import tf


def quad_sum(*spectra):
    """Takes any number of same length spectrum and returns the quadrature sum.

    Parameters
    ----------
        *spectra:
            Variable length argument list of the spectra.

    Returns
    -------
        qs: np.ndarray
            The quadrature sum of the spectra.

    """
    qs=np.zeros_like(spectra[0])
#     print(args[0])
    for i in spectra:
        for j in range(len(i)):
            qs[j]=np.sqrt(qs[j]**2+i[j]**2)
    return qs


def norm2(spectrum):
    """Takes a spectrum and returns the 2-norm of the spectrum.

    Parameters
    ----------
        spectrum: list of float or numpy.ndarray
            The spectrum of interest

    Returns
    -------
        norm: float
            The 2-norm of the spectrum
    """
#     if isinstance(spectrum.np.array)
    spectrum_array = np.array(spectrum)
    norm = np.sqrt(sum(spectrum_array**2))
    return norm


def rms(ts):
    """Calculate the RMS fluctuation of a given time series

    Parameters
    ----------
        ts: list of float or numpy.ndarray
            The time series to be analyzed.

    Returns
    -------
        float
            The RMS of the time series.
    """
    ts = np.array(ts)
    return np.std(ts, ddof=0)


def lmse(array1, array2, weight=None):
    """Return the logrithmic mean square error between the two arrays

    Parameters
    ----------
    array1: array
        The first array
    array2: array
        The second array
    weight: array, optional
        The weighting function.

    Returns
    -------
    float
        Logrithmic mean square error
    """
    if len(array1)!=len(array2):
        raise ValueError('array1 length {} not equal to array2 length {}'\
            ''.format(len(array1), len(array2)))
    array1 = np.array(array1)
    array2 = np.array(array2)
    if weight is None:
        weight = np.ones_like(array1)
    if len(array1)!=len(weight):
        raise ValueError('weight length {} not equal to array length {}'\
            ''.format(len(weight), len(array1)))
    weight = np.array(weight)
    _lmse = (1/len(array1)
             * np.sum((np.abs(np.log10(array1)-np.log10(array2))*weight)**2))
    return _lmse


def tfmatrix2tf(sys):
    """Convert a matrix of transfer functions to a MIMO transfer function.

    Parameters
    ----------
        sys: list of (list of control.xferfcn.TransferFunction)
            The transfer function matrix representing a MIMO system. sys[i][j]
            is the transfer function from the i+1 input port to the j+1 output
            port.
    Returns
    -------
        control.xferfcn.TransferFunction
            The transfer function of the MIMO system.
    """
    nums = list(np.zeros_like(sys))
    dens = list(np.zeros_like(sys))
    for i in range(len(sys)):
        for j in range(len(sys[i])):
            nums[i][j] = list(sys[i][j].num[0][0])
            dens[i][j] = list(sys[i][j].den[0][0])
        nums[i] = list(nums[i])
        dens[i] = list(dens[i])
    generalized_plant = control.tf(nums, dens)
    return generalized_plant


def remove_unstable(unstable_tf, remove_unstable_zeros=True):
    """Negate the positive real parts of the poles and zeros of a transfer function.

    Parameters
    ----------
        untable_tf: control.xferfcn.TransferFunction
            The transfer function which contains unstable poles or zeros.
        remove_unstable_zeros: boolean, optional
            Set True to remove unstable zeros as well.

    Returns
    -------
        stable_tf: control.xferfcn.TransferFuncion
            The modified transfer function with flipped unstable poles and zeros.
    """
    stable_tf = tf([1], [1])

    for pole in unstable_tf.pole():
#         print(pole)
        x = np.real(pole)
        y = np.imag(pole)
        if abs(y/x) < 1e-10:
            y = 0
        if x > 0:
            wn = x + 1j*y
        else:
            wn = -x + 1j*y
        stable_tf *= tf([1], [1/wn, 1])

    for zero in unstable_tf.zero():
#         print(zero)
        x = np.real(zero)
        y = np.imag(zero)
        if abs(y/x) < 1e-10:
            y = 0
        if x > 0:
            wn = x + 1j*y
        else:
            wn = -x + 1j*y
        stable_tf *= tf([1/wn, 1], [1])

    stable_tf *= float(unstable_tf.dcgain())

    return stable_tf


def zpk(zeros, poles, gain, unit='Hz', negate=True):
    """Zero-pole-gain definition of transfer function.

    Parameters
    ----------
        zeros: list of floats
            A list of the location of the zeros
        poles: list of floats
            A list of the location of the poles
        gain: float
            The static gain of the transfer function
        unit: string, optional
            The unit of the zeros and poles.
            Specify 'Hz' if zeros and poles are in Hz.
            Specify anything else if zeros and poles
            are in radian per second.
            Default by 'Hz'.
        negate: boolean, optional
            Negate zeros and poles in specification
            so negative sign is not needed for stable
            zeros and poles. Default to be True.

    Returns
    -------
        zpk_tf: control.xferfcn.TransferFunction
            The zpk defined transfer function

    Notes
    -----
        Refrain from specifying imaginary zeros and poles.
        Use kontrol.utils.sos() for second-order sections
        instead.
        The zero and poles are negated by default.
    """

    zeros = [float(z) for z in zeros]
    poles = [float(p) for p in poles]

    zeros = np.array(zeros)
    poles = np.array(poles)

    if unit == 'Hz':
        for i in range(len(zeros)):
            zeros[i] = 2*np.pi*zeros[i]
        for i in range(len(poles)):
            poles[i] = 2*np.pi*poles[i]

    if negate is False:
        for i in range(len(zeros)):
            zeros[i] = -zeros[i]
        for i in range(len(poles)):
            poles[i] = -poles[i]

    zpk_tf = tf([gain],[1])
    for z in zeros:
        zpk_tf *= tf([1/z, 1], [1])
    for p in poles:
        zpk_tf *= tf([1], [1/p, 1])

    return zpk_tf
