"""KAGRA/LIGO Foton related utilities.
"""
import control
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
    # Divide tf into tfs with less than 20 order.
    # Do tf conversion.
    # Stack the string
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

    zeros = tf.zeros()
    poles = tf.poles()
    str_zeros = ""  # String of list of zeros (placeholder)
    str_poles = ""  # String of list of poles (placeholder)

    # get zeros and poles.
    if root_location in ["f", "n"]:
        zeros /= 2*np.pi
        poles /= 2*np.pi
    if root_location == "n":
        zeros = -zeros.conjugate()
        poles = -poles.conjugate()

    # get zeros and poles list, and sort.
    z_wn = np.sqrt(tf.zeros().real**2 + tf.zeros().imag**2)
    p_wn = np.sqrt(tf.poles().real**2 + tf.poles().imag**2)
    z_sort_arg = z_wn.argsort()
    p_sort_arg = p_wn.argsort()
    z_wn.sort()
    p_wn.sort()

    # get gain
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

    # Convert to zpk expressing string
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
    str_num = ""  # String of numerator coefficients
    str_den = ""  # String of numerator coefficients
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


def foton2tf(foton_string):
    """Convert a Foton string to TransferFunction

    Parameters
    ----------
    foton_string : str
        The Foton string, e.g. zpk([0], [1; 1], 1, "n").

    Returns
    -------
    tf : TransferFunction
        The transfer function.
    """
    # Categorize the string and call the relevant function.
    if "zpk" in foton_string:
        return zpk2tf(foton_string)
    elif "rpoly" in foton_string:
        return rpoly2tf(foton_string)
    else:
        raise ValueError("Foton string not recognized. "
                         "Only zpk and rpoly strings are supported.")


def zpk2tf(foton_string):
    """Convert a Foton ZPK string to TransferFunction

    Paramters
    ---------
    foton_string : str
        The Foton ZPK string, e.g. zpk([0], [1; 1], 1, "n").

    Returns
    -------
    tf : TransferFunction
        The transfer function.
    """
    foton_string = foton_string.replace(" ", "")
    foton_string = foton_string.lstrip("zpk(")
    foton_string = foton_string.rstrip(")")
    split = foton_string.split(",")
    if len(split) == 3:
        z_string, p_string, gain_string = split
        root_location = "s"
    else:
        z_string, p_string, gain_string, root_location = split

    def process_zp_string(zp_string):
        zp_string = zp_string.replace("[", "")
        zp_string = zp_string.replace("]", "")
        zp_string = zp_string.split(";")
        zp = []
        if zp_string == [""]:
            return np.array(zp)
        for string in zp_string:
            # split real and imaginary
            split = string.split("i*")
            if len(split) == 2:
                real_string, imag_string = split
                sign = real_string[-1]
            else:
                real_string, = split
                imag_string = "0"
                sign = "+"
            real_string = real_string.rstrip("+")
            real_string = real_string.rstrip("-")

            zp_complex = f"{real_string}{sign}{imag_string}j"
            zp.append(complex(zp_complex))
        zp = np.array(zp)
        return zp

    zeros = process_zp_string(z_string)
    poles = process_zp_string(p_string)
    gain = float(gain_string)

    root_location = root_location.replace("'", "")
    root_location = root_location.replace('"', "")

    if root_location in "nf":
        # zeros poles are in Hz. Gain is DC.
        zeros *= 2*np.pi  # Convert to rad/s
        poles *= 2*np.pi
    #     print("nf")

    if root_location in "sf":
        # Negate for (s+z), (s+p) convention.
        zeros = -zeros
        poles = -poles

    tf = get_zpk2tf((zeros, poles, gain))
    # print(root_location)

    # tf = control.tf([1], [1])
    # s = control.tf("s")

    # for zero in zeros:
    #     if zero == 0:
    #         tf *= (s+zero)/(2*np.pi)
    #     elif zero.imag > 0 and zero.real != 0:
    #         wn = np.sqrt(zero.real**2 + zero.imag**2)
    #         q = wn / (2*zero.real)
    #         tf *= (s**2 + wn/q*s + wn**2) / wn**2
    #     elif zero.imag > 0 and zero.real == 0:
    #         wn = zero.imag
    #         tf *= (s**2 + wn**2)/wn**2
    #     elif zero.imag == 0 and zero.real != 0:
    #         tf *= (s+zero.real)/zero.real

    # for pole in poles:
    #     if pole == 0:
    #         tf /= (s+pole)/(2*np.pi)
    #     elif pole.imag > 0 and pole.real != 0:
    #         wn = np.sqrt(pole.real**2 + pole.imag**2)
    #         q = wn / (2*pole.real)
    #         tf /= (s**2 + wn/q*s + wn**2) / wn**2
    #     elif pole.imag > 0 and pole.real == 0:
    #         wn = pole.imag
    #         tf /= (s**2 + wn**2)/wn**2
    #     elif pole.imag == 0 and pole.real != 0:
    #         tf /= (s+pole.real)/pole.real

    # if root_location == "n":
    #     tf *= gain
    # elif root_location in "sf":
    #     tf *= gain / (tf.num[0][0][0]/tf.den[0][0][0])

    return kontrol.TransferFunction(tf)


def get_zpk2tf(get_zpk, plane="s"):
    """Converts Foton's get_zpk() output to TransferFunction
    
    Parameters
    ----------
    get_zpk : tuple(array, array, float)
        The output from Foton's get_zpk() method of a filter instance.
    plane : str, optional
        "s", "f", or "n".
        Default "s".

    Returns
    -------
    tf : TransferFunction
        The converted transfer function.
    """
    zeros = get_zpk[0]
    poles = get_zpk[1]
    gain = get_zpk[2]

    if plane in "nf":
        # zeros poles are in Hz. Gain is DC.
        zeros *= 2*np.pi  # Convert to rad/s
        poles *= 2*np.pi
        raise ValueError('plane="n" or "f" not supported in this version.')
    #     print("nf")

    if plane in "sf":
        # Negate for (s+z), (s+p) convention.
        zeros = -zeros
        poles = -poles

    tf = control.tf([1], [1])
    s = control.tf("s")

    for zero in zeros:
        if zero == 0:
            tf *= (s+zero)/(2*np.pi)
        elif zero.imag > 0 and zero.real != 0:
            wn = np.sqrt(zero.real**2 + zero.imag**2)
            q = wn / (2*zero.real)
            tf *= (s**2 + wn/q*s + wn**2) / wn**2
        elif zero.imag > 0 and zero.real == 0:
            wn = zero.imag
            tf *= (s**2 + wn**2)/wn**2
        elif zero.imag == 0 and zero.real != 0:
            tf *= (s+zero.real)/zero.real

    for pole in poles:
        if pole == 0:
            tf /= (s+pole)/(2*np.pi)
        elif pole.imag > 0 and pole.real != 0:
            wn = np.sqrt(pole.real**2 + pole.imag**2)
            q = wn / (2*pole.real)
            tf /= (s**2 + wn/q*s + wn**2) / wn**2
        elif pole.imag > 0 and pole.real == 0:
            wn = pole.imag
            tf /= (s**2 + wn**2)/wn**2
        elif pole.imag == 0 and pole.real != 0:
            tf /= (s+pole.real)/pole.real

    if plane == "n":
        tf *= gain
    elif plane in "sf":
        tf *= gain / (tf.num[0][0][0]/tf.den[0][0][0])

    return kontrol.TransferFunction(tf)


def rpoly2tf(foton_string):
    """Converts rpoly Foton strings to TransferFunction

    Parameters
    ----------
    foton_string : str
        The rpoly Foton string. E.g. rpoly([1; 2; 3], [2; 3; 4], 5)
    """
    foton_string = foton_string.lstrip("rpoly")
    foton_string = foton_string.replace(" ", "")
    foton_string = foton_string.replace("(", "")
    foton_string = foton_string.replace(")", "")
    num_string, den_string, gain_string = foton_string.split(",")

    def string2floatarray(string):
        """Convert a string of float array to array"""
        string = string.replace("[", "")
        string = string.replace("]", "")
        string = string.split(";")
        float_array = []
        if string == [""]:
            return np.array(float_array)
        for value in string:
            float_array.append(float(value))
        return np.array(float_array)
    num = string2floatarray(num_string)
    den = string2floatarray(den_string)
    gain = float(gain_string)
    tf = control.tf(num, den)
    tf *= gain
    return kontrol.TransferFunction(tf)


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
