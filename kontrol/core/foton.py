"""KAGRA/LIGO Foton related utilities.
"""
import numpy as np

import kontrol.core.controlutils
import kontrol.logger


def tf2foton(
        tf, expression="zpk", root_location="s", significant_figures=6,
        itol=1e-25, epsilon=1e-25):
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
    significant_figures : int, optional
        Number of significant figures to print out.
        Defaults to 6.
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
    """
    if expression not in ["zpk", "rpoly"]:
        raise ValueError("expression {} not available."
                         "Please select expression from [\"zpk\", \"rpoly\"."
                         "".format(expression))
    ## Divide tf into tfs with less than 20 order.
    ## Do tf conversion.
    ## Stack the string
    foton_expression = ""
    tf_list = kontrol.core.controlutils.tf_order_split(tf, max_order=20)
    if len(tf_list) > 1:
        kontrol.logger.logger.warning("The transfer function has "
                                      "order higher than 20. This is not "
                                      "supported by KAGRA's Foton software. "
                                      "The Foton expression is splitted into "
                                      "multiple expressions with less order.")
    for tf_ in tf_list:
        if expression == "zpk":
            foton_expression += tf2zpk(
                tf_, root_location=root_location,
                significant_figures=significant_figures,
                itol=itol, epsilon=epsilon)
        elif expression == "rpoly":
            foton_expression += tf2rpoly(
                tf_, significant_figures=significant_figures)
        else:
            foton_expression += ""
            print("If you see this, contact maintainer.")
        foton_expression += "\n\n"
    foton_expression = foton_expression.rstrip("\n\n")

    return foton_expression


def tf2zpk(tf, root_location="s", significant_figures=6,
           itol=1e-25, epsilon=1e-25):
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
    significant_figures : int, optional
        Number of significant figures to print out.
        Defaults to 6.
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
    # if _order_gt(tf, 20):
    #     raise ValueError("Order of transfer function is not less than 20")
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
            str_zeros += "{:.{}g}".format(zero.real, significant_figures)
        else:
            str_zeros += "{:.{sf}f}+i*{:.{sf}f}".format(
                zero.real, zero.imag, sf=significant_figures)
        str_zeros += ";"
    for pole in poles[p_sort_arg]:
        if abs(pole.imag)/abs(pole.real+epsilon) < itol:
            str_poles += "{:.{}g}".format(pole.real, significant_figures)
        else:
            str_poles += "{:.{sf}f}+i*{:.{sf}f}".format(
                pole.real, pole.imag, sf=significant_figures)
        str_poles += ";"
    str_zeros = str_zeros.rstrip(";")
    str_poles = str_poles.rstrip(";")
    zpk_expression = "zpk([{}],[{}],{:.{}g},\"{}\")".format(
        str_zeros, str_poles, gain, significant_figures, root_location)

    return zpk_expression


def tf2rpoly(tf, significant_figures=6):
    """Convert a transfer function to foton rpoly expression.

    Parameters
    ----------
    tf : TransferFunction
        The transfer function object
    significant_figures : int, optional
        Number of significant figures to print out.
        Defaults to 6.

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
        str_num += "{:.{}g}".format(coef, significant_figures)
        str_num += ";"
    for coef in den:
        str_den += "{:.{}g}".format(coef, significant_figures)
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


def notch(frequency, q, depth, significant_figures=6):
    """Returns the foton expression of a notch filter.
    
    Parameters
    ----------
    frequency : float
        The notch frequency (Hz).
    q : float
        The quality factor.
    depth : float
        The depth of the notch filter (magnitude).
    significant_figures : int, optional
        Number of significant figures to print out.
        Defaults to 6.

    Returns
    -------
    str
        The foton representation of this notch filter.
    """
    depth_db = 20*np.log10(depth)
    expression = "notch({:.{sf}f},{:.{sf}f},{:.{sf}f})".format(
        frequency, q, depth_db, sf=significant_figures)
    return expression
