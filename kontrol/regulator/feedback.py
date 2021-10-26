"""Algorithmic designs for control regulators.

This sub-module contains functions for algorithmic design for
controllers, filters, and the like.
The functions has the following signature
func(plant: TransferFunction, **kwargs)->TransferFunction
For example, it takes a can take a transfer function and make a
feedback regulator that critically damps the system.
"""
import control
import numpy as np

import kontrol


def critical_damping(plant, method="optimized", **kwargs):
    r"""Derivative control for critically damping the dominant mode
    
    Parameters
    ----------
    plant : TransferFunction
        The transfer function representation of the system to be feedback
        controlled.
        The plant must contain at least one pair of complex poles.
    method : str, optional
        The method to be used for setting the gain.
        Choose from ["optimized", "calculated"].

        "optimized": the gain is optimized until the dominant complex
        pole pairs become two simple poles.

        "calculated": the gain is set to :math:`2/\omega_n/K_{DC}`,
        where :math:`\omega_n` is the resonance frequency in rad/s
        of the dominant mode, and :math:`K_{DC}` is the DC gain
        of the plant.
        
        Both method assumes that the plant has at least one pair of complex
        poles.

        Defaults to "optimized".
    **kwargs : keyword arugments
        Method specific keyword arguments.
        See:

        - 'optimized' :ref:`<kontrol.regulator.feedback.critical_damp_optimized>`
        - 'calculated' :ref:`<kontrol.regulator.feedback.critical_damp_calculated>``

    Returns
    -------
    TransferFunction
        The derivative control regulator for critically damping the
        dominant mode.

    Notes
    -----
    The control regulator is simply

    .. math::

       K(s) = K_d s.

    The gain :math:`K_d` is optimized such that  
    """
    if _count_complex_poles(plant) == 0:
        raise ValueError("Plant must contain at least one pair of"
                         "complex poles")

    if method == "calculated":
        regulator = critical_damp_calculated(plant, **kwargs)
    elif method == "optimized":
        regulator = critical_damp_optimize(plant, **kwargs)
    else:
        raise ValueError('Invalid method. '
                         'Methods avavilable from ["optimized", "calculated"]')
    return regulator


def critical_damp_calculated(plant):
    r"""Find dominant mode and returns the approximate critical regulator.

    Parameters
    ----------
    plant : TransferFunction
        The transfer function representation of the system to be feedback
        controlled.
        The plant must contain at least one pair of complex poles.

    Returns
    -------
    TransferFunction
        The critical regulator.

    Notes
    -----
    The plant must contain at least one complex pole pair.
    The plant must have a non-zero DC gain.

    The critical regulator is approximated by

    .. math::
        K(s) \approx \frac{2}{\omega_n K_\mathrm{DC}}\,,

    where :math:`\omega_n` is the resonance frequency of the dominant mode
    and :math:`K_\mathrm{DC}` is the DC gain of the plant.
    """
    poles = plant.pole()
    dominant_wn = None
    for p in poles:
        if p.imag != 0:
            wn = abs(p)
            amp = abs(plant(1j*wn))
            if dominant_wn is None:
                dominant_wn = wn
            if dominant_wn is not None:
                if amp > abs(plant(1j*dominant_wn)):
                    dominant_wn = wn
    dcgain = plant.dcgain()
    kd = 2/dominant_wn/dcgain
    s = control.tf("s")
    regulator = kd*s
    return kontrol.TransferFunction(regulator)


def critical_damp_optimize(plant, gain_step=1.1, ktol=1e-6):
    r"""Optimize derivative damping gain and returns the critical regulator
    
    Parameters
    ---------- 
    plant : TransferFunction
        The transfer function representation of the system to be feedback
        controlled.
        The plant must contain at least one pair of complex poles.
    gain_step : float, optional
        The multiplicative factor of the gain for finding the gain
        upper bound.
        It must be greater than 1.
        Defaults to 1.1.
    ktol : float, optional
        The tolerance for the convergence condition.
        The convergence condition is (kd_max-kd_min)/kd_min > ktol.
        It must be greater than 0.
        Defaults to 1e-6.

    Returns
    -------
    TransferFunction
        The critical regulator.

    Notes
    -----
    Only works with plants that contain at least one complex pole pair.
    Works best with plants that only contain complex zeros/poles.
    If it returns unreasonable high gain, try lowering ``gain_step``.

    The algorithm goes as follows.

    1. Find the minimum damping gain ``k_min`` such that the open-loop
    transfer function ``k_min*s*plant`` has maxmimum gain
    at unity gain frequency

    2. Iterate ``i``: ``k_i=k_min*i*gain_step`` for i=1,2,3...
    
    3. Terminate when ``1/(1+k_i*s*plant)`` has less complex pole pairs than
    the ``plant`` itself, i.e. one mode has been overdamped. Then, define
    ``k_max=k_i``.

    4. Iterate: Define ``k_mid`` as the logarithmic mean of
    ``k_max`` and ``k_min``. If ``1/(1+k_mid*s*plant)`` has less complex
    pole pairs than ``plant``, i.e. overdamps, then set ``k_max=k_mid``.
    Otherwise, set ``k_min=k_mid``.

    5. Terminate when ``(k_max - k_min)/k_min < ktol``, i.e. converges.
    
    """
    if gain_step <= 1:
        raise ValueError("gain_step must be greater than 1")
    if ktol <= 0:
        raise ValueError("ktol must be greater than 1")

    s = control.tf("s")
    f_pole = abs(plant.pole())/2/np.pi
    kd_min = 1/max(abs((s*plant)(1j*2*np.pi*f_pole)))

    k_min = kd_min * s
    oltf_min = k_min * plant

    n_complex_pole = _count_complex_poles(plant)

    # Find overdamp gain
    # Do so by adding gain until number of complex poles of
    # the closed-loop plant changes.
    kd = kd_min
    while 1:
        kd *= gain_step
        oltf = kd * s * plant
        sensitivity = plant / (1+oltf)
        if n_complex_pole > _count_complex_poles(sensitivity.minreal()):
            kd_max = kd
            break

    kd_mid = 10**((np.log10(kd_max)-np.log10(kd_min))/2 + np.log10(kd_min))

    # Keep tighting the bounds until convergence condition is met.
    while 1:
        kd_mid = 10**((np.log10(kd_max)-np.log10(kd_min))/2 + np.log10(kd_min))
        oltf_mid = kd_mid * s *plant
        sensitivity = plant / (1+oltf_mid)
        if n_complex_pole > _count_complex_poles(sensitivity.minreal()):
            # Mid gain still overdamps
            kd_max = kd_mid
        else:
            # Mid gain underdamps.
            kd_min = kd_mid
        
        if (kd_max-kd_min)/kd_min < ktol:
            # Convergence.
            kd_critical = kd_mid
            break

    regulator = kd_mid * s

    return kontrol.TransferFunction(regulator)
                         
def _count_complex_poles(plant):
    """Returns number of complex poles in a transfer function"""
    n_complex_pole = 0
    for p in plant.pole():
        if p.imag != 0:
            n_complex_pole += 1
    return n_complex_pole
    

    
