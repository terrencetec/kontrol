"""Predefined regulator library. """
import control

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
    """Alias kontrol.regulator.predefined.proportional_integral_derivative()"""
    return proportional_integral_derivative(kp, ki, kd)
