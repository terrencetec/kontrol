"""KAGRA/LIGO foton related utilities.
"""
import numpy as np


def tf2foton(tf, format="zpk", root_location="s", itol=1e-25, epsilon=1e-25):
    """Convert a single transfer function to foton expression.

    Parameters
    ==========
    tf: TransferFunction
        The transfer function object.
    format: str, optional
        Format of the foton expression.
        Choose from ["zpk", "Rpoly"].
        Defaults to "zpk".
    root_location: str, optional
        Root location of the zeros and poles for format=="zpk".
        Choose from ["s", "f", "n"].
        "s": roots in s-plane, i.e. zpk([...], [...], ...,  "s").
        "f": roots in frequency plane, i.e. zpk([...], [,,,], ..., "f").
        "n": roots in frequency plane but negated and gains are normalized,
            i.e. real parts are positive zpk([...], [...], ..., "n").
        Defaults to "s".
    itol: float, optional
        Treating complex roots as real roots if the ratio of
        the imaginary part and the real part is smaller than this tolerance
        Defaults to 1e-25.
    epsilon: float, optional
        Small number to add to denominator to prevent division error.
        Defaults to 1e-25.

    Returns
    =======
    foton_expression: str
        The foton expression in selected format.

    Note
    ====
    Only works for transfer functions with less than 20 orders.
    """
    pass


def tf2zpk(tf, root_location="s", itol=1e-25, epsilon=1e-25):
    """Convert a single transfer function to foton zpk expression.

    Parameters
    ==========
    tf: TransferFunction
        The transfer function object.
    root_location: str, optional
        Root location of the zeros and poles.
        Choose from ["s", "f", "n"].
        "s": roots in s-plane, i.e. zpk([...], [...], ...,  "s").
        "f": roots in frequency plane, i.e. zpk([...], [,,,], ..., "f").
        "n": roots in frequency plane but negated and gains are normalized,
            i.e. real parts are positive zpk([...], [...], ..., "n").
        Defaults to "s".
    itol: float, optional
        Treating complex roots as real roots if the ratio of
        the imaginary part and the real part is smaller than this tolerance
        Defaults to 1e-25.
    epsilon: float, optional
        Small number to add to denominator to prevent division error.
        Defaults to 1e-25.

    Returns
    =======
    str
        The foton zpk expression in selected format.

    Note
    ====
    Only works for transfer functions with less than 20 orders.
    """
    if _order_geq_than(tf, 20):
        raise valueError("Order of transfer function is greater than 20")
    if root_location not in ["s", "f", "n"]:
        raise valueError("Select root_location from [\"s\", \"f\", \"n\"]")

    zeros = tf.zero()
    poles = tf.pole()
    str_zeros = ""  # String of list of zeros (placeholder)
    str_poles = ""  # String of list of poles (placeholder)

    ## get zeros and poles.
    if root_location in ["f", "n"]:
        zeros /= 2*np.pi
        poles /= 2*np.pi
    if root_location == "n":
        zeros = -zeros.conjugate()
        poles = -poles.conjugate()

    ## get gain
    if root_location in ["s", "f"]:
        gain = tf.minreal().num[0][0][0]
    else:
        z_wn = np.sqrt(tf.zero().real**2 + tf.zero().imag**2)
        p_wn = np.sqrt(tf.pole().real**2 + tf.pole().imag**2)
        z_wn.sort()
        p_wn.sort()
        gain = 1
        dc_zero_counter = list(z_wn).count(0)
        dc_pole_counter = list(p_wn).count(0)
        for wn in p_wn:
            if dc_zero_counter >= 1:
                dc_zero_counter -= 1
                # continue
            if wn != 0:
                gain /= wn
            else:
                gain /= 2*np.pi
        for wn in z_wn:
            if dc_pole_counter >= 1:
                dc_pole_counter -= 1
                # continue
            if wn != 0:
                gain *= wn
            else:
                gain *= 2*np.pi

    for zero in zeros:
        if abs(zero.imag)/abs(zero.real+epsilon) < itol:
            str_zeros += "{}".format(zero.real)
        else:
            str_zeros += "{}+i*{}".format(zero.real, zero.imag)
        str_zeros += ";"
    for pole in poles:
        if abs(pole.imag)/abs(pole.real+epsilon) < itol:
            str_poles += "{}".format(pole.real)
        else:
            str_poles += "{}+i*{}".format(pole.real, pole.imag)
        str_poles += ";"
    str_zeros = str_zeros.rstrip(";")
    str_poles = str_poles.rstrip(";")
    zpk_expression = "zpk([{}],[{}],{},\"{}\")".format(
        str_zeros, str_poles, gain, root_location)
    return zpk_expression


def _order(tf):
    """Returns the number of coefficients in numerator and denominator

    Parameters
    ==========
    tf: TransferFunction
        The transfer function object

    Returns
    =======
    nnum: int
        Number of coefficients in numerator.
    nden: int
        Number of coefficients in denominator.
    """
    nnum = len(tf.num[0][0])
    nden = len(tf.den[0][0])
    return nnum, nden


def _order_geq_than(tf, order):
    """Returns true if transfer function order is greater than the specified.

    Parameters
    ==========
    tf: TransferFunction
        The transfer function object.
    order: int
        Order threshold.

    Returns
    =======
    bool
        True if order(tf) >= order, False otherwise.
    """
    nnum, nden = _order(tf)
    return max(nnum, nden) >= order
