"""KAGRA/LIGO Foton related utilities.
"""
import numpy as np


def tf2foton(
    tf, expression="zpk", root_location="s", itol=1e-25, epsilon=1e-25):
    """Convert a single transfer function to foton expression.

    Parameters
    ----------
    tf : TransferFunction
        The transfer function object.
    expression: str, optional
        Format of the foton expression.
        Choose from ["zpk", "rpoly"].
        Defaults to "zpk".
    root_location : str, optional
        Root location of the zeros and poles for expression=="zpk".
        Choose from ["s", "f", "n"].
        "s": roots in s-plane, i.e. zpk([...], [...], ...,  "s").
        "f": roots in frequency plane, i.e. zpk([...], [,,,], ..., "f").
        "n": roots in frequency plane but negated and gains are normalized,
        i.e. real parts are positive zpk([...], [...], ..., "n").
        Defaults to "s".
    itol : float, optional
        Treating complex roots as real roots if the ratio of
        the imaginary part and the real part is smaller than this tolerance
        Defaults to 1e-25.
    epsilon : float, optional
        Small number to add to denominator to prevent division error.
        Defaults to 1e-25.

    Returns
    -------
    foton_expression : str
        The foton expression in selected format.

    Notes
    -----
    Only works for transfer functions with less than 20 orders.
    """
    if expression not in ["zpk", "rpoly"]:
        raise ValueError("expression {} not available."
                         "Please select expression from [\"zpk\", \"rpoly\"."
                         "".format(expression))
    if expression == "zpk":
        foton_expression = tf2zpk(
            tf, root_location=root_location, itol=itol, epsilon=epsilon)
    elif expression == "rpoly":
        foton_expression = tf2rpoly(tf)
    else:
        foton_expression = ""
        print("If you see this, contact maintainer.")

    return foton_expression


def tf2zpk(tf, root_location="s", itol=1e-25, epsilon=1e-25):
    """Convert a single transfer function to foton zpk expression.

    Parameters
    ----------
    tf : TransferFunction
        The transfer function object.
    root_location : str, optional
        Root location of the zeros and poles.
        Choose from ["s", "f", "n"].
        "s": roots in s-plane, i.e. zpk([...], [...], ...,  "s").
        "f": roots in frequency plane, i.e. zpk([...], [,,,], ..., "f").
        "n": roots in frequency plane but negated and gains are normalized,
        i.e. real parts are positive zpk([...], [...], ..., "n").
        Defaults to "s".
    itol : float, optional
        Treating complex roots as real roots if the ratio of
        the imaginary part and the real part is smaller than this tolerance
        Defaults to 1e-25.
    epsilon : float, optional
        Small number to add to denominator to prevent division error.
        Defaults to 1e-25.

    Returns
    -------
    str
        The foton zpk expression in selected format.

    Notes
    -----
    Only works for transfer functions with less than 20 orders.
    """
    if _order_gt(tf, 20):
        raise ValueError("Order of transfer function is not less than 20")
    if root_location not in ["s", "f", "n"]:
        raise ValueError("Select root_location from [\"s\", \"f\", \"n\"]")

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

    ## get zeros and poles list, and sort.
    z_wn = np.sqrt(tf.zero().real**2 + tf.zero().imag**2)
    p_wn = np.sqrt(tf.pole().real**2 + tf.pole().imag**2)
    z_sort_arg = z_wn.argsort()
    p_sort_arg = p_wn.argsort()
    z_wn.sort()
    p_wn.sort()

    ## get gain
    gain = tf.minreal().num[0][0][0]
    if root_location in ["n"]:
        for wn in p_wn:
            if wn != 0:
                gain /= wn
            else:
                gain /= 2*np.pi
        for wn in z_wn:
            if wn != 0:
                gain *= wn
            else:
                gain *= 2*np.pi

    ## Convert to zpk expressing string
    for zero in zeros[z_sort_arg]:
        if abs(zero.imag)/abs(zero.real+epsilon) < itol:
            str_zeros += "{}".format(zero.real)
        else:
            str_zeros += "{}+i*{}".format(zero.real, zero.imag)
        str_zeros += ";"
    for pole in poles[p_sort_arg]:
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


def tf2rpoly(tf):
    """Convert a transfer function to foton rpoly expression.

    Parameters
    ----------
    tf : TransferFunction
        The transfer function object

    Returns
    -------
    str :
        Foton express in foton rpoly expression.

    Notes
    -----
    Only works for transfer functions with less than 20 orders.
    """
    if _order_gt(tf, 20):
        raise ValueError("Order of transfer function is not less than 20")

    num = tf.minreal().num[0][0]
    den = tf.minreal().den[0][0]
    str_num = ""  ## String of numerator coefficients
    str_den = ""  ## String of numerator coefficients
    gain = num[0]
    num /= num[0]

    for coef in num:
        str_num += "{}".format(coef)
        str_num += ";"
    for coef in den:
        str_den += "{}".format(coef)
        str_den += ";"
    str_num = str_num.rstrip(";")
    str_den = str_den.rstrip(";")
    rpoly_expression = "rpoly([{}],[{}],{})".format(str_num, str_den, gain)

    return rpoly_expression


def _order(tf):
    """Returns the number of coefficients in numerator and denominator

    Parameters
    ----------
    tf : TransferFunction
        The transfer function object

    Returns
    -------
    nnum : int
        Number of coefficients in numerator.
    nden : int
        Number of coefficients in denominator.
    """
    nnum = len(tf.minreal().num[0][0])
    nden = len(tf.minreal().den[0][0])
    return nnum, nden


def _order_gt(tf, order):
    """Returns true if transfer function order is greater than the specified.

    Parameters
    ----------
    tf : TransferFunction
        The transfer function object.
    order : int
        Order threshold.

    Returns
    -------
    boolean
        True if order(tf) > order, False otherwise.
    """
    nnum, nden = _order(tf)
    return max(nnum, nden) > order
