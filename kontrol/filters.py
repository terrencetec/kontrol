"""Standard filter references.
"""

from control import tf

def complementary_sekiguchi(coefs):
    """Sekiguchi filter.

    4th-order complemetary filter used in Sekiguchi's
    thesis whose high-pass is structured as:
    hpf = (s^7 + 7*w_b*s^6 + 21*w_b^2*s^5 + 35*w_b^3*s^4) / (s+w_b)^7,
    where w_b is the blending frequency in [rad/s]

    Args:
        blend_freq: float
            Blending frequency of the filter in [rad/s]

    Returns:
        lpf: control.xferfcn.TransferFunction
            Complementary low pass-filter
        hpf: control.xferfcn.Transferfunction
            Complementary high pass-filter
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
    """Modified Sekiguchi Filter.

    Takes an array of 4 coefficients and return a 4th-order complemetary
    high-pass filter and a corresponding complementary low-pass
    filter. The filter follows Sekiguchi's complemetary filter
    but is modified for flexibility. The high-pass filter takes
    from of:
    hpf = (s^7 + 7*a_1*s^6 + 21*a_2^2*s^5 + 35*a_3^3*s^4) / (s+a_4)^7,
    where a_1, a_2, a_3 and a_4 are arbitrary coefficients replacing
    the roles of the blending frequency in Sekiguchi's filter.

    Parameters
    ----------
        coefs: numpy.ndarray
            4 coefficients defining the modified Sekiguchi filter.

    Returns
    -------
        lpf: control.xferfcn.TransferFunction
            Complementary low-pass filter
        hpf: control.xferfcn.Transferfunction
            Complementary high-pass filter
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

def your_custom_filter(coefs,):
    """Define any filter using this suggested format.
    """

    # Polynomials. Use _aN for the coefficient of
    # the Nth-order Laplace variable of the denominator.
    a0, a1, a2, a3, b0, b1, b2 = coefs
    A = [a3, a2, a1, a0]
    B = [b0, b1, b2]
    return(tf(B, A),)  # Return H(s) = B(s)/A(s).
