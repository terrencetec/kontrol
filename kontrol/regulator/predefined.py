"""Predefined regulator library. """
import control
import numpy as np

import kontrol


def proportional_integral_derivative(kp=0, ki=0, kd=0):
    r"""PID control build on proportional_derivative().
    
    Parameters
    ----------
    kp : float, optional
        The proportional control gain.
        Defaults to 0.
    ki : float, optional
        The integral control gain.
        Defaults to 0.
    kd : float, optional
        Defaults to 0.

    Returns
    -------
    TransferFunction
        The PID controller.
        
    Notes
    -----
    The PID controller is defined as

    .. math::
       
       K_\mathrm{PID}(s) = K_p + K_i/s + K_d s\,.
    """
    s = control.tf("s")
    return kontrol.TransferFunction(kp + ki/s + kd*s)


def pid(kp=0, ki=0, kd=0):
    """Alias of proportional_integral_derivative()"""
    return proportional_integral_derivative(kp, ki, kd)


def low_pass(cutoff, order=1, **kwargs):
    r"""Simple low-pass filter

    Parameters
    ----------
    cutoff : float
        Cutoff frequency (Hz)
    order : int, optional
        The order of the filter.
        Defaults to be 1.
    **kwargs
        Keyword arguments holder. Not passed to anywhere.
    
    Return
    ------
    TransferFunction
        The low-pass filter.

    Notes
    -----
    The low-pass filter is defined as

    .. math::
       
       L(s) = \left(\frac{2\pi f_c}/{s+2\pi f_c}\right)^n\,,

    where :math:`f_c` is the cutoff frequency (Hz), :math:`n` is the order
    of the filter.
    """
    s = control.tf("s")
    lp = ((2*np.pi*cutoff) / (s + 2*np.pi*cutoff))**order
    return kontrol.TransferFunction(lp)


def notch(frequency, q, depth, **kwargs):
    r"""Notch filter defined in Foton.

    Parameters
    ----------
    frequency : float
        The notch frequency (Hz).
    q : float
        The quality factor.
    depth : float
        The depth of the notch filter (magnitude).

    Returns
    -------
    TransferFunction
        The notch filter

    Notes
    -----
    The notch filter is defined by Foton, as
    
    .. math::
       
       N(s) = \frac{s^2 + (2\pi f_n)/(dQ/2)s + (2\pi fn)**2}
       {s^2 + (2\pi f_n)/(Q/2)s + (2\pi fn)**2}\,,

    where :math:`f_n` is the notch frequency, :math:`q` is the quality factor
    , and :math:`d` is the depth.
    """
    wn = 2*np.pi*frequency
    qp = q/2
    depth = 10**(depth_db/20)
    qz = qp*depth
    n = (s**2 + wn/qz*s + wn**2) / (s**2 + wn/qp*s + wn**2)
    return kontrol.TransferFunction(n) 
