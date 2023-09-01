"""Algorithmic designs for feedback control regulators.
"""
import control
import numpy as np

import kontrol


def critical_damping(plant, method="calculated", **kwargs):
    r"""Returns the critical damping derivative control gain.

    This functions calls
    ``kontrol.regulator.feedback.critical_damp_calculated()`` or
    ``kontrol.regulator.feedback.cricical_damp_optimized()`` and
    returns the derivative control gain.

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
        of the mode to be damped, and :math:`K_{DC}` is the sum of DC gains
        of the mode and that of the other high-frequency modes.

        Both method assumes that the plant has at least one pair of complex
        poles.

        Defaults to "calculated".
    **kwargs : dict
        Method specific keyword arguments.

        See:

        - "optimized": kontrol.regulator.feedback.critical_damp_optimized
        - "calculated": kontrol.regulator.feedback.critical_damp_calculated

    Returns
    -------
    kd : float
        The derivative gain for critically damping the
        dominant mode.
    """
    if _count_complex_poles(plant) == 0:
        raise ValueError("Plant must contain at least one pair of"
                         " complex poles")

    if method == "calculated":
        kd = critical_damp_calculated(plant, **kwargs)
    elif method == "optimized":
        kd = critical_damp_optimize(plant, **kwargs)
    else:
        raise ValueError('Invalid method. '
                         'Methods avavilable from ["optimized", "calculated"]')
    return kd


def critical_damp_calculated(plant, nmode=1, **kwargs):
    r"""Find dominant mode and returns the approximate critical regulator.

    Parameters
    ----------
    plant : TransferFunction
        The transfer function representation of the system to be feedback
        controlled.
        The plant must contain at least one pair of complex poles.
    nmode : int, optional
        The ``nmode``th dominant mode to be damped.
        This number must be less than the number of modes in the plant.
        Defaults 1.

    Returns
    -------
    kd : float
        The derivative gain for critically damping the
        dominant mode.

    Notes
    -----
    The plant must contain at least one complex pole pair.
    The plant must have a non-zero DC gain.

    The critical regulator is approximated by

    .. math::
        K(s) \approx \frac{2}{\omega_n K_\mathrm{DC}}\,,

    where :math:`\omega_n` is the resonance frequency of the dominant mode
    and :math:`K_\mathrm{DC}` is the sum of DC gains of the mode
    and that of the other higher-frequency modes..
    """
    # Decompose into frequencies, quality factors, and DC gains
    wn, q, k = kontrol.regulator.feedback.mode_decomposition(plant)
    peak_gain = q*k  # Gain at the resonances.

    # indexes of the modes from most dominant to least dominant.
    dominant_indexes = np.flip(np.argsort(peak_gain))
    # The index of the mode that we want to damp
    mode_index = dominant_indexes[nmode-1]

    # Sum all the DC gains of the modes that has higher
    # or equal frequency than the mode (including the mode itself).
    dcgain = np.sum(k[:mode_index+1])
    dominant_wn = wn[mode_index]

    kd = 2/dominant_wn/dcgain  # Estimate critical damping gain.

    return kd


def critical_damp_optimize(plant, gain_step=1.1, ktol=1e-6, **kwargs):
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
    kd : float
        The derivative gain for critically damping the
        dominant mode.

    Notes
    -----
    Update on 2021-12-04: Use carefully. It only critically damps
    the mode that has the highest peak when multiplied by an differentiator.
    Note for myself: only 2 complex poles can become simple poles for
    plants with second-order rolloff.

    Only works with plants that contain at least one complex pole pair.
    Works best with plants that only contain complex zeros/poles.
    If it returns unreasonably high gain, try lowering ``gain_step``.

    The algorithm goes as follows.

    1. Find the minimum damping gain ``k_min`` such that the open-loop
    transfer function ``k_min*s*plant`` has maxmimum gain
    at unity gain frequency.

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
        raise ValueError("ktol must be greater than 0")

    s = control.tf("s")
    f_pole = abs(plant.poles())/2/np.pi
    kd_min = 1/max(abs((s*plant)(1j*2*np.pi*f_pole)))

    n_complex_pole = _count_complex_poles(plant)

    # Find overdamp gain
    # Do so by adding gain until number of complex pole modes
    # reduced by more than the number of n_overdamp_modes
    kd = kd_min
    while 1:
        kd *= gain_step
        oltf = kd * s * plant
        sensitivity = plant / (1+oltf)
        damped_complex_poles = _count_complex_poles(sensitivity.minreal())
        if n_complex_pole > damped_complex_poles:
            kd_max = kd
            break

    kd_mid = 10**((np.log10(kd_max)-np.log10(kd_min))/2 + np.log10(kd_min))

    # Keep tighting the bounds until convergence condition is met.
    while 1:
        kd_mid = 10**((np.log10(kd_max)-np.log10(kd_min))/2 + np.log10(kd_min))
        oltf_mid = kd_mid * s * plant
        sensitivity = plant / (1+oltf_mid)
        damped_complex_poles = _count_complex_poles(sensitivity.minreal())
        if n_complex_pole > damped_complex_poles:
            # Mid gain still overdamps
            kd_max = kd_mid
        else:
            # Mid gain underdamps.
            kd_min = kd_mid

        if (kd_max-kd_min)/kd_min < ktol:
            # Convergence.
            break

    kd = kd_mid

    return kd


def _count_complex_poles(plant):
    """Returns number of complex poles in a transfer function"""
    n_complex_pole = 0
    for p in plant.poles():
        if p.imag != 0:
            n_complex_pole += 1
    return n_complex_pole


def _find_dominant_mode(plant):
    """Returns the frequency (rad/s) of the dominant mode."""
    poles = plant.poles()
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
    return dominant_wn


def _count_overdamp_modes(plant):
    """Count overdamped modes for critically damped dominant modes"""
    s = control.tf("s")
    n_overdamp_modes = 0
    dominant_wn = _find_dominant_mode(plant)
    spoles = (s*plant).pole()
    for p in spoles:
        if p.imag != 0:
            wn = abs(p)
            amp = abs((s*plant)(1j*wn))
            if amp > abs((s*plant)(1j*dominant_wn)):
                n_overdamp_modes += 1
    return n_overdamp_modes


# IDK where to put this function
# FIXME Put this function in a proper module.
def mode_decomposition(plant):
    """Returns a list of single mode transfer functions

    Parameters
    ----------
    plant : TransferFunction
        The transfer function with at list one pair of complex poles.

    Returns
    -------
    wn : array
        Frequencies (rad/s).
    q : array
        Q factors.
    k : array
        Dcgains of the modes.
    """
    poles = plant.poles()
    complex_mask = poles.imag > 0  # Avoid duplication
    wn = abs(poles[complex_mask])  # Frequencies
    q = wn/(-2*poles[complex_mask].real)  # Q factors of the modes
    k = 1j * (plant(1j*wn)/q)  # DC gain of the modes
    # clean complex number
    sign = np.sign(k.real)
    k = sign * abs(k)
    return wn, q, k


def mode_composition(wn, q, k):
    """Create a plant composed of many modes.

    Parameters
    ----------
    wn : array
    Frequencies (rad/s).
    q : array
        Q factors.
    k : array
        Dcgains of the modes.

    Returns
    -------
    TransferFunction
        The composed plant.
    """
    if len(wn) != len(q) or len(wn) != len(k):
        raise ValueError("wn, q, k must have same length.")
    plant = kontrol.TransferFunction([0], [1])
    s = control.tf("s")
    for wn_, q_, k_ in zip(wn, q, k):
        plant = plant + k_ * wn_**2 / (s**2 + wn_/q_*s + wn_**2)
    return plant


def add_proportional_control(plant, regulator=None, dcgain=None, **kwargs):
    """Match and returns proportional gain.

    This function finds a proportional gain such that
    the proportional control UGF matches the first UGF
    of the specified regulator (typically a derivative control regulator).
    If ``dcgain`` is specified, the DC gain is matched instead.

    Parameters
    ----------
    plant : TransferFunction
        The transfer function representation of the system to be feedback
        controlled.
        The plant must contain at least one pair of complex poles.
    regulator : TransferFunction, optional
        The pre-regulator.
        If not specified, then ``dcgain`` must be specified.
        Defaults to None.
    dcgain : float, optional
        The desired DC gain of the open-loop transfer function.
        If not specified, the portional gain is tuned
        such that the portional control's first UGF matches that
        of the derivative control.
        Defaults to None.

    Returns
    -------
    kp : float
        The proportional control gain.
    """
    if dcgain is not None:
        kp = dcgain / plant.dcgain()
    elif regulator is not None:
        oltf = plant * regulator
        _, _, _, _, ugf, _ = control.stability_margins(
            oltf, returnall=True)
        kp = 1 / abs(plant(1j*min(ugf)))
    else:
        raise ValueError("At least one of regulator or dcgain must be "
                         "specified.")
    return kp


def add_integral_control(
        plant, regulator=None, integrator_ugf=None,
        integrator_time_constant=None, **kwargs):
    """Match and returns an integral gain.

    This function finds an integral gain such that
    the UGF of the integral control matches that of the specified
    regulator.
    If ``integrator_ugf`` or ``integrator_time_constant`` is specified
    instead, these will be matched instead.

    Parameters
    ----------
    plant : TransferFunction
        The transfer function representation of the system to be feedback
        controlled.
    regulator : TransferFunction, optional
        The pre-regulator
        Use ``kontrol.regulator.feedback.proportional_derivative()`` or
        ``kontrol.regulator.feedback.critical_damping()`` to make one
        for oscillator-like systems.
    integrator_ugf : float, optional
        The unity gain frequency (Hz) of the integral control.
        This is the inverse of the integration time constant.
        If ``integrator_time_constant is not None``, then this value will be
        ignored.
        If set to None, it'll be set to match the first UGF of the
        derivative control.
        Defaults to None.
    integrator_time_constant : float, optional,
        The integration time constant (s) for integral control.
        Setting this will override the ``integrator_ugf`` argument.
        Defaults to None.

    Returns
    -------
    ki : float
        The integral control gain.
    """
    s = control.tf("s")
    oltf_int = 1/s * plant.dcgain()
    if integrator_time_constant is not None:
        integrator_ugf = 1/integrator_time_constant
        ki = 1 / abs(oltf_int(1j*2*np.pi*integrator_ugf))
    elif integrator_ugf is not None:
        ki = 1 / abs(oltf_int(1j*2*np.pi*integrator_ugf))
    elif regulator is not None:
        oltf = plant * regulator
        _, _, _, _, ugf, _ = control.stability_margins(
                    oltf, returnall=True)
        ki = 1 / abs(oltf_int(1j*min(ugf)))
    else:
        raise ValueError("At least one of regulator, integrator_ugf, or "
                         "integrator_time_constant must be specified.")
    return ki
