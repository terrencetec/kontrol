"""Utility functions.
Functions: quad_sum, norm2, rms, tfmatrix2tf.
"""

import numpy as np
import control

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
    return(qs)

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
    return(norm)

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
    return(np.std(ts, ddof=0))

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
    generalize_plant = control.tf(aug_P_num, aug_P_den)
    return(generalized_plant)
