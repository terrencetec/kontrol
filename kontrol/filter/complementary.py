"""Complementary filter references.
"""

from control import tf

def complementary_sekiguchi(coefs):
    r"""4th-order complementary filters specified by the blending frequencies.

    Parameters
    ----------
        coefs: float
            Blending frequency of the filter in [rad/s]

    Returns
    -------
        lpf: control.xferfcn.TransferFunction
            Complementary low pass-filter
        hpf: control.xferfcn.Transferfunction
            Complementary high pass-filter

    Notes
    -----
    4th-order complemetary filter used in Sekiguchi's
    thesis [1]_ whose high-pass is structured as:

    .. math::
        H = \frac{s^7 + 7w_bs^6 + 21w_b^2s^5 + 35w_b^3s^4}{(s+w_b)^7}

    where :math:`w_b` is the blending frequency in [rad/s].

    References
    ----------
    .. [1]
        T. Sekiguchi, A Study of Low Frequency Vibration Isolation System
        for Large Scale Gravitational Wave Detectors

    """

    blend_freq = coefs[0]
    _coefs = [blend_freq]*4
    # hpf_numerator = [
    #     1,
    #     7*blend_freq,
    #     21*blend_freq**2,
    #     35*blend_freq**3,
    #     0, 0, 0, 0,
    # ]
    # hpf = tf(hpf_numerator, [1]) * tf([1], [1, blend_freq])**7
    # lpf = 1 - hpf
    return(complementary_modified_sekiguchi(_coefs))

def complementary_modified_sekiguchi(coefs):
    r"""Modified Sekiguchi Filter with guaranteed 4th-order high-pass.

    Parameters
    ----------
        coefs: list of (int or float) or numpy.ndarray
            4 coefficients defining the modified Sekiguchi filter.

    Returns
    -------
        lpf: control.xferfcn.TransferFunction
            Complementary low-pass filter
        hpf: control.xferfcn.Transferfunction
            Complementary high-pass filter

    Notes
    -----
        The modified Sekiguchi complemetary filter is structured as:

        .. math::
            H = \frac{s^7 + 7a_1s^6 + 21a_2^2s^5 + 35a_3^3s^4}{(s+a_4)^7}

        where :math:`a_1`, :math:`a_2`, :math:`a_3`, :math:`a_4` are some
        parameters that defines the filter.
    """

    a1, a2, a3, a4 = coefs
    hpf_numerator = [
        1,
        7 * a1,
        21 * a2**2,
        35 * a3**3,
        0, 0, 0, 0,
    ]
    hpf = tf(hpf_numerator, [1]) * tf([1], [1, a4])**7
    lpf = 1 - hpf
    return(lpf, hpf)

def complementary_lucia(coefs):
    r"""Lucia Trozzo's complementary filter

    Parameters
    ----------
        coefs: list of float or numpy.ndarray of floats
            Takes 7 parameters, in specification order: :math:`p_1`, :math:`p_
            2`, :math:`z_1`, :math:`w_1`, :math:`q_1`, :math:`w_2`, :math:`q_2`
            . See notes for the meaning of the parameters.

    Returns
    -------
        lpf: control.xferfcn.TransferFunction
            Complementary low-pass filter
        hpf: control.xferfcn.Transferfunction
            Complementary high-pass filter
    Notes
    -----
        The modified Sekiguchi complemetary filter is structured as:

        .. math::
            H = K\frac{s^3(s+z_1)(s^2+w_1/q_1\,s+w_1^2)(s^2+w_2/q_2\,s+w_2^2)}
            {(s+p_1)^5(s+p_2)^3}

        where :math:`K` is a constant normalizing the filter at high frequency.
    """
    p1, p2, z1, w1, q1, w2, q2 = coefs
    hpf = tf([1], [1/p1, 1])**5 * tf([1], [1/p2, 1])**3
    hpf *= tf([1/z1, 1], [1])
    hpf *= tf([1, w1/q1, w1**2], [w1**2]) * tf([1, w2/q2, w2**2], [w2**2])
    hpf *= tf([1, 0],[1])**3
    hpf *= hpf.den[0][0][0]/hpf.num[0][0][0]
    lpf = 1 - hpf
    return(lpf, hpf)

# def your_custom_filter(coefs,):
#     """Define any filter using this suggested format.
#     """
#
#     # Polynomials. Use _aN for the coefficient of
#     # the Nth-order Laplace variable of the denominator.
#     a0, a1, a2, a3, b0, b1, b2 = coefs
#     A = [a3, a2, a1, a0]
#     B = [b0, b1, b2]
#     return(tf(B, A),)  # Return H(s) = B(s)/A(s).
