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

    zpk_tf = control.tf([gain],[1])
    for z in zeros:
        zpk_tf *= control.tf([1/z, 1], [1])
    for p in poles:
        zpk_tf *= control.tf([1], [1/p, 1])

    return zpk_tf


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
