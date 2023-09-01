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

    zpk_tf = control.tf([gain], [1])
    for z in zeros:
        zpk_tf *= control.tf([1/z, 1], [1])
    for p in poles:
        zpk_tf *= control.tf([1], [1/p, 1])

    return zpk_tf


def sos(natural_frequencies=None, quality_factors=None, gain=1., unit="f"):
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
    if natural_frequencies is None:
        natural_frequencies = []
    if quality_factors is None:
        quality_factors = []
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
    zeros_unstable = control_tf.zeros()
    poles_unstable = control_tf.poles()
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


def check_tf_equal(tf1, tf2, allclose_kwargs={}, minreal=True):
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
    minreal: boolean
        Use control.minreal to remove canceling zeros and poles before
        comparison.

    Returns
    -------
    boolean
    """
    if minreal:
        tf1 = control.minreal(tf1, verbose=False)
        tf2 = control.minreal(tf2, verbose=False)
    zeros_close = np.allclose(tf1.zeros(), tf2.zeros(), **allclose_kwargs)
    poles_close = np.allclose(tf1.poles(), tf2.poles(), **allclose_kwargs)
    gain_close = np.allclose(tf1.dcgain(), tf2.dcgain(), **allclose_kwargs)
    return all([zeros_close, poles_close, gain_close])


def generic_tf(zeros=None, poles=None,
               zeros_wn=None, zeros_q=None,
               poles_wn=None, poles_q=None,
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
    if zeros is None:
        zeros = []
    if poles is None:
        poles = []
    if zeros_wn is None:
        zeros_wn = []
    if zeros_q is None:
        zeros_q = []
    if poles_wn is None:
        poles_wn = []
    if poles_q is None:
        poles_q = []

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


def outliers(tf, f, unit="f"):
    """Returns a list of zeros and poles outside the frequency range.

    Parameters
    ----------
    tf: control.xferfcn.TransferFunction
        The transfer function.
    f: array
        The frequency axis of interest.
    unit: str, optional
        The unit of the zeros, poles and the natural frequencies.
        Choose from ["f", "s", "Hz", "omega"].
        Defaults "f".

    Returns
    -------
    outlier_zeros: array
        Zeros outside the frequency range.
    outlier_poles: array
        Poles outside the frequency range.

    Note
    ----
    We use the python-control package convention for
    the returned zeros and poles, so to preserve the type and format
    as much as possible for further processes.
    """
    outlier_zeros = []
    outlier_poles = []
    zeros = tf.zeros()
    poles = tf.poles()
    f = np.array(f)
    if unit in ["f", "Hz"]:
        f = f*2*np.pi
    f_min = min(f)
    f_max = max(f)

    for zero in zeros:
        fn = np.sqrt(zero.real**2 + zero.imag**2)
        if fn < f_min or fn > f_max:
            outlier_zeros.append(zero)
    for pole in poles:
        fn = np.sqrt(pole.real**2 + pole.imag**2)
        if fn < f_min or fn > f_max:
            outlier_poles.append(pole)
    outlier_zeros = np.array(outlier_zeros)
    outlier_poles = np.array(outlier_poles)
    return outlier_zeros, outlier_poles


def outlier_exists(tf, f, unit="f"):
    """Checks for zeros and poles outside the frequency range.

    Parameters
    ----------
    tf: control.xferfcn.TransferFunction
        The transfer function.
    f: array
        The frequency axis of interest.
    unit: str, optional
        The unit of the zeros, poles and the natural frequencies.
        Choose from ["f", "s", "Hz", "omega"].
        Defaults "f".

    Returns
    -------
    boolean
        If there's any zero or pole outside the frequency range.
    """
    outlier_zeros, outlier_poles = outliers(tf=tf, f=f, unit=unit)
    if len(outlier_zeros) + len(outlier_poles) > 0:
        return True
    else:
        return False


def tf_order_split(tf, max_order=20):
    """Split TransferFunction objects into multiple ones with fewer order.

    Parameters
    ----------
    tf : TransferFunction
        The transfer function
    max_order : int, optional
        The maxmium order of the split transfer functions.
        Defaults to 20 (the foton limit).

    Returns
    -------
    list of TransferFunction.
        The list of splitted transfer functions.
    """
    zeros = tf.zeros()
    poles = tf.poles()
    gain = tf.minreal().num[0][0][0]

    global order_running
    global zero_running
    global tf_zero_list
    global pole_running
    global tf_pole_list
    order_running = 0
    zero_running = []
    tf_zero_list = []
    pole_running = []
    tf_pole_list = []

    def put_tf_zeros_into_list():
        """Use zeros in zero_running to create an all zero transfer function
        and put store them into tf_zero_list, and reset order_running to 0.
        """
        s = control.tf("s")
        global order_running
        global zero_running
        global tf_zero_list
        simple_zeros = []
        zeros_wn = []
        zeros_q = []
        differentiator = 0
        gain = 1
        for z in zero_running:
            if z.imag == 0:
                if z.real == 0:
                    differentiator += 1
                    # gain *= 2*np.pi
                else:
                    gain *= -z.real
                    simple_zeros += [-z.real]
            else:
                wn = abs(z)
                q = wn / (-2*z.real)
                gain *= wn**2
                zeros_wn += [abs(z)]
                zeros_q += [q]
        tf = generic_tf(zeros=simple_zeros,
                        zeros_wn=zeros_wn, zeros_q=zeros_q,
                        dcgain=gain, unit="s")
        for i in range(differentiator):
            tf *= s
        tf_zero_list += [tf]
        order_running = 0
        zero_running = []

    def put_tf_poles_into_list():
        """Use poles in pole_running to create an all pole transfer function
        and put store them into tf_pole_list, and reset order_running to 0.
        """
        s = control.tf("s")
        global order_running
        global pole_running
        global tf_pole_list
        simple_poles = []
        poles_wn = []
        poles_q = []
        integrator = 0
        gain = 1
        for p in pole_running:
            if p.imag == 0:
                if p.real == 0:
                    integrator += 1
                    # gain /= 2*np.pi
                else:
                    gain /= -p.real
                    simple_poles += [-p.real]
            else:
                wn = abs(p)
                q = wn / (-2*p.real)
                gain /= wn**2
                poles_wn += [abs(p)]
                poles_q += [q]
        tf = generic_tf(poles=simple_poles,
                        poles_wn=poles_wn, poles_q=poles_q,
                        dcgain=gain, unit="s")
        for _ in range(integrator):
            tf *= 1/s
        tf_pole_list += [tf]
        order_running = 0
        pole_running = []

    # Put zeros into list until order reaches max_order.
    # And then make a transfer function out of the list,
    # and finally resets.
    for i in range(len(zeros)):
        if zeros[i].imag == 0:
            if order_running+1 > max_order:
                put_tf_zeros_into_list()
            order_running += 1
            zero_running += [zeros[i]]
        elif zeros[i].imag > 0:
            if order_running+2 > max_order:
                put_tf_zeros_into_list()
            order_running += 2
            zero_running += [zeros[i]]
        else:
            pass  # Ignore negative part of the complex pair.

    # Add the reminders
    put_tf_zeros_into_list()

    for i in range(len(poles)):
        if poles[i].imag == 0:
            if order_running+1 > max_order:
                put_tf_poles_into_list()
            order_running += 1
            pole_running += [poles[i]]
        elif poles[i].imag > 0:
            if order_running + 2 > max_order:
                put_tf_poles_into_list()
            order_running += 2
            pole_running += [poles[i]]
        else:
            pass  # Ignore negative part of the complex pair.

    put_tf_poles_into_list()

    n_tf = max(len(tf_pole_list), len(tf_zero_list))
    tf_list = []
    for i in range(n_tf):
        # print(i)
        if i+1 > len(tf_pole_list):
            tf_list += [tf_zero_list[i]]
        elif i+1 > len(tf_zero_list):
            tf_list += [tf_pole_list[i]]
        else:
            tf_list += [tf_zero_list[i]*tf_pole_list[i]]
    tf_list[0] *= gain
    return tf_list


def clean_tf(tf, tol_order=5, small_number=1e-25):
    """Remove numerator/denominator coefficients that are small outliers

    Parameters
    ----------
    tf : TransferFunction
        The transfer function to be cleaned
    tol_order : float, optional
        If the coefficient is ``tol_order`` order smaller than
        the rest of the coefficients, then this coefficient is an outlier.
        Defaults 5.
    small_number : float, optional
        A small number to be added to the log10 in case 0 is encountered.

    Returns
    -------
    tf_cleaned : TransferFunction
        The cleaned transfer function.
    """
    num = tf.num[0][0].copy()
    den = tf.den[0][0].copy()
    log_num = np.log10(num+small_number)
    log_den = np.log10(den+small_number)
    num_mask = log_num.mean() - log_num > tol_order
    den_mask = log_den.mean() - log_den > tol_order
    num[num_mask] = 0
    den[den_mask] = 0
    tf_cleaned = control.tf(num, den)
    # tf_cleaned = tf_cleaned.minreal()
    return tf_cleaned


def clean_tf2(tf, tol_order=5, small_number=1e-25):
    """Remove zeros/poles that are outliers.

    Parameters
    ----------
    tf : TransferFunction
        The transfer function to be cleaned.
    tol_order : float, optional
        If the frequency of the zero/pole is ``tol_order'' order away from the
        mean order, then this zero/pole is an outlier.
        Defaults 5.
    small_number : float, optional
        A small number to be added to the log10() in case 0 is encountered

    Returns
    -------
    tf_cleaned : TransferFunction
        The cleaned transfer function.
    """
    zeros = tf.zeros().copy()
    poles = tf.poles().copy()
    wn_zeros = abs(zeros)
    wn_poles = abs(poles)
    log_wn_zeros = np.log10(wn_zeros+small_number)
    log_wn_poles = np.log10(wn_poles+small_number)
    mean_wn_zeros = np.mean(log_wn_zeros)
    mean_wn_poles = np.mean(log_wn_poles)
    mask_zeros = abs(log_wn_zeros-mean_wn_zeros) > tol_order
    mask_poles = abs(log_wn_poles-mean_wn_poles) > tol_order
    zeros[mask_zeros] = None
    poles[mask_poles] = None

    s = control.tf("s")
    tf_cleaned = control.tf([1], [1])
    for i, zero in enumerate(zeros):
        if mask_zeros[i]:  # Remove outliers
            continue
        if zero.imag < 0:  # Only treat positive imag part.
            continue
        elif zero.imag != 0 and zero.real != 0:
            wn, q = complex2wq(zero)
            tf_cleaned *= (s**2 + wn/q*s + wn**2) / wn**2
        elif zero.real == 0 and zero.imag != 0:
            wn = abs(zero)
            tf_cleaned *= (s**2 + wn**2) / wn**2
        elif zero.real != 0 and zero.imag == 0:
            tf_cleaned *= (s+abs(zero))/abs(zero)
        elif zero == 0:
            tf_cleaned *= s

    for i, pole in enumerate(poles):
        if mask_poles[i]:  # Remove outliers
            continue
        if pole.imag < 0:  # Only treat positive imag part.
            continue
        elif pole.imag != 0 and pole.real != 0:
            wn, q = complex2wq(pole)
            tf_cleaned /= (s**2 + wn/q*s + wn**2) / wn**2
        elif pole.real == 0 and pole.imag != 0:
            wn = abs(pole)
            tf_cleaned /= (s**2 + wn**2) / wn**2
        elif pole.real != 0 and pole.imag == 0:
            tf_cleaned /= (s+abs(pole))/abs(pole)
        elif pole == 0:
            tf_cleaned /= s

    # Match gain at 1 Hz
    gain_1hz = abs(tf(1j*2*np.pi*1))
    tf_cleaned *= gain_1hz / abs(tf_cleaned(1j*2*np.pi*1))
    # tf_cleaned = tf_cleaned.minreal()
    return tf_cleaned


def clean_tf3(tf, tol_order=5, small_number=1e-25):
    """Remove first coefficient if it is much smaller than the second

    Parameters
    ----------
    tf : TransferFunction
        Transfer function to be cleaned
    tol_order : float, optional
        First coefficient is removed if it is ``tol_order'' order
        smaller than the second coefficient.
        Remove only if there exists such coefficient in both
        numerator and denominator.
    small_number : float, optional
        A small number to be added to the log10() in case 0 is encountered.

    Returns
    -------
    tf_cleaned : TransferFunction
        The cleaned TransferFunction
    """
    num = tf.num[0][0].copy()
    den = tf.den[0][0].copy()
    if (abs(np.log10(num[0]) - np.log10(num[1])) > tol_order
       and abs(np.log10(den[0]) - np.log10(den[1])) > tol_order):
        #
        tf_cleaned = control.tf(tf.num[0][0][1:], tf.den[0][0][1:])
    else:
        tf_cleaned = tf
    return tf_cleaned


def complex2wq(complex_frequency):
    """Convert a complex frequency to frequency and Q-factor.

    Parameters
    ----------
    complex_frequency : complex
        Complex frequency in rad/s.

    Returns
    -------
    wn : float
        The frequency in rad/s
    q : float
        The Q factor.
    """
    wn = abs(complex_frequency)
    q = -wn / (2*complex_frequency.real)
    q = abs(q)
    return wn, q
