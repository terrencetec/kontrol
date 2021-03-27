"""Utility function related to python-control library.
"""
import control
import numpy as np


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


def zpk(zeros, poles, gain, unit='f', negate=True):
    """Zero-pole-gain definition of transfer function.

    Parameters
    ----------
    zeros: list of floats
        A list of the location of the zeros
    poles: list of floats
        A list of the location of the poles
    gain: float
        The static gain of the transfer function
    unit: str, optional
        The unit of the zeros, poles and the natural frequencies.
        Choose from ["f", "s", "Hz", "omega"].
        Defaults "f".
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

    if unit in ["f", "Hz"]:
        for i in range(len(zeros)):
            zeros[i] = 2*np.pi*zeros[i]
        for i in range(len(poles)):
            poles[i] = 2*np.pi*poles[i]

    if negate is False:
        for i in range(len(zeros)):
            zeros[i] = -zeros[i]
        for i in range(len(poles)):
            poles[i] = -poles[i]

    zpk_tf = control.tf([gain],[1])
    for z in zeros:
        zpk_tf *= control.tf([1/z, 1], [1])
    for p in poles:
        zpk_tf *= control.tf([1], [1/p, 1])

    return zpk_tf


def sos(natural_frequencies=[], quality_factors=[], gain=1., unit="f"):
    r"""Second-order sections transfer fucntion.

    Parameters
    ----------
    natural_freuqnecies: array, optional
        List of natural frequencies.
        Defaults [].
    quality_factors: list, optional
        List of quality factors.
        Defaults [].
    gain: float, optional
        The gain of the transfer function.
        Defaults 1.
    unit: str, optional
        The unit of the zeros, poles and the natural frequencies.
        Choose from ["f", "s", "Hz", "omega"].
        Defaults "f".

    Returns
    -------
    sos: control.xferfcn.TransferFunction
        The product of all second-order sections.

    Note
    ----
    :math:`K\prod\left(s^2+\omega_n/Q\,s+\omega_n^2\right)`.
    """
    if len(natural_frequencies) != len(quality_factors):
        raise ValueError("Lenght of natural frequencies must match length of "
                         "quality factors.")

    natural_frequencies = np.array(natural_frequencies)
    quality_factors = np.array(quality_factors)
    if unit in ["f", "Hz"]:
        natural_frequencies = 2*np.pi*natural_frequencies

    s = control.tf("s")
    sos = control.tf([gain], [1])
    for wn, q in zip(natural_frequencies, quality_factors):
        sos *= (s**2 + wn/q*s + wn**2)/wn**2
    return sos


def convert_unstable_tf(control_tf):
    """Convert transfer function with unstable zeros and poles to tf without.

    Parameters
    ----------
    control_tf: control.xferfcn.TransferFunction
        The transfer function to be converted.

    Returns
    -------
    tf_new: control.xferfcn.TransferFunction
        control_tf with unstable zeros and poles flipped.

    Note
    ----
    Warning can occur when the order gets high, e.g. 100.
    This happens due to numerical accuracy,
    i.e. coefficients get astronomically high when order gets high.
    """
    zeros_unstable = control_tf.zero()
    poles_unstable = control_tf.pole()
    zeros_stable = []
    poles_stable = []
    for zero in zeros_unstable:
        # Ignore zeros/poles that have negative imaginary part.
        if zero.imag != 0 and zero.imag < 0:
            pass
        elif zero.real > 0:
            zeros_stable.append(-zero.real + 1j*zero.imag)
        else:
            zeros_stable.append(zero.real + 1j*zero.imag)
    for pole in poles_unstable:
        # Ignore zeros/poles that have negative imaginary part.
        if pole.imag != 0 and pole.imag < 0:
            pass
        elif pole.real > 0:
            poles_stable.append(-pole.real + 1j*pole.imag)
        else:
            poles_stable.append(pole.real + 1j*pole.imag)

    tf_new = control.tf([1], [1])
    s = control.tf("s")
    for zero in zeros_stable:
        if zero.imag != 0:
            wn = np.sqrt(zero.real**2 + zero.imag**2)
            zeta = -zero.real/wn
            tf_new /= wn**2 / (s**2+2*zeta*wn*s+wn**2)
        else:
            tf_new *= s-zero.real
    for pole in poles_stable:
        if pole.imag != 0:
            wn = np.sqrt(pole.real**2 + pole.imag**2)
            zeta = -pole.real/wn
            tf_new *= wn**2 / (s**2+2*zeta*wn*s+wn**2)
        else:
            tf_new /= s-pole.real

    tf_new *= float(control_tf.dcgain())/float(tf_new.dcgain())

    return tf_new


def check_tf_equal(tf1, tf2, allclose_kwargs={}):
    """Check if two transfer functions are approximatedly equal by np.allclose.

    Parameters
    ----------
    tf1: control.xferfcn.TransferFunction
        Transfer function 1.
    tf2: control.xferfcn.TrasnferFunction
        Transfer function 2.
    allclose_kwargs: dict, optional
        Keyword arguments passed to np.allclose(), which is used to compare
        the list of poles and zeros and dcgain.
        Defaults {}.

    Returns
    -------
    boolean
    """
    zeros_close = np.allclose(tf1.zero(), tf2.zero(), **allclose_kwargs)
    poles_close = np.allclose(tf1.pole(), tf2.pole(), **allclose_kwargs)
    gain_close = np.allclose(tf1.dcgain(), tf2.dcgain(), **allclose_kwargs)
    return all([zeros_close, poles_close, gain_close])


def generic_tf(zeros=[], poles=[],
               zeros_wn=[], zeros_q=[],
               poles_wn=[], poles_q=[],
               dcgain=1., unit="f"):
    r"""Construct a generic transfer function object.

    Parameters
    ----------
    zeros: array, optional
        List of zeros in frequencies.
        Defaults [].
    poles: array, optional
        List of poles.
        Defaults [].
    zeros_wn: array, optional
        List of natural frequencies of numerator second-order sections.
    zeros_q: array, optional.
        List of Q-value of numerator second-order sections.
    poles_wn: array, optional
        List of natural frequencies of denominator second-order sections.
    poles_q: array, optional.
        List of Q-value of denominator second-order sections.
    dcgain: float, optional
        The DC gain of the transfer function.
        Defaults 1.
    unit: str, optional
        The unit of the zeros, poles and the natural frequencies.
        Choose from ["f", "s", "Hz", "omega"].
        Defaults "f".

    Returns
    -------
    tf: control.xferfcn.TransferFunction
        The transfer function.

    Note
    ----
    No negative sign is needed for negative zeros and poles.
    For instance, `generic_tf(poles=[1], unit="s")` means
    :math:`\frac{1}{s+1}`.
    """
    zeros = np.array(zeros)
    poles = np.array(poles)
    zeros_wn = np.array(zeros_wn)
    zeros_q = np.array(zeros_q)
    poles_wn = np.array(poles_wn)
    poles_q = np.array(poles_q)

    tf = zpk(zeros=zeros, poles=poles, gain=dcgain, unit=unit)
    tf *= sos(natural_frequencies=zeros_wn, quality_factors=zeros_q, unit=unit)
    tf /= sos(natural_frequencies=poles_wn, quality_factors=poles_q, unit=unit)
    return tf
