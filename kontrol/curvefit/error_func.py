"""Error functions for curve fitting
"""
import numpy as np


def mse(x1, x2, weight=None):
    """Mean square error

    Parameters
    ----------
    x1 : array
        Array
    x2 : array
        Array
    weight: array or None, optional
        weighting function.
        If None, defaults to np.ones_like(x1)

    Returns
    -------
    float
        Mean square error between arrays x1 and x2.
    """
    if weight is None:
        weight = np.ones_like(x1)
    return np.mean(np.square(np.subtract(x2, x1)*weight))


def log_mse(x1, x2, weight=None, small_multiplier=1e-6):
    """Logarithmic mean square error/Mean square log error

    Parameters
    ----------
    x1 : array
        Array
    x2 : array
        Array
    weight: array or None, optional
        weighting function.
        If None, defaults to `np.ones_like(x1)`
    small_multiplier: float, optional
        `x1` will be modified by `x1`+`small_multiplier`*`np.min(x2)` if
        0 exists in `x1`.
        Same goes to `x2`.
        If 0 both exists in `x1` and `x2`, raise.

    Returns
    -------
    float
        Logarithmic mean square error between arrays x1 and x2.
    """
    if 0 in x1 and 0 in x2:
        raise ValueError("zero value exists in both 'x1' and 'x2'"
                         "Can't take np.log10()")
    elif 0 in x1:
        x1 += small_multiplier * np.min(x2)
    elif 0 in x2:
        x2 += small_multiplier * np.min(x1)
    return mse(x1=np.log10(x1), x2=np.log10(x2), weight=weight)


def tf_error(tf1, tf2, weight=None, small_number=1e-6, norm=2):
    r"""Mean log error between two transfer functions frequency response

    Parameters
    ----------
    tf1 : array
        Frequency response of transfer function 1, in complex values.
    tf2 : array
        Frequency response of transfer function 2, in complex values.
    weight : array or None, optional
        Weighting function.
        Defaults None.
    small_number : float, optional
        A small number to be added in before evaluating np.log10 to
        prevent error.
        Defaults to 1e-6.
    norm : int, optional
        The type of norm used to estimate the error.
        Choose ``1`` for $\mathcal{L}_1$ norm and
        ``2`` for $\mathcal{L}_2$ norm.
        Other norms are are possible but not encouraged unless
        there's a specifiy reason.
        Defaults 2.

    Returns
    -------
    float
        Mean log error between two transfer function.

    Notes
    -----
    $\mathcal{L}_1$ norm is more robust while
    $\mathcal{L}_2$ norm is more susceptible to outliers, but fits
    data with large dynamic range well.
    """
    if weight is None:
        weight = np.ones_like(tf1, dtype=float)
    return np.mean(np.log10(abs(tf1-tf2)**norm + small_number) * weight)


def noise_error(noise1, noise2, weight=None, small_number=1e-6, norm=2):
    r"""Mean log error between two noise spectrums.

    Parameters
    ----------
    noise1 : array
        Noise spectrum 1.
    noise2 : array
        Noise spectrum 2.
    weight : array or None, optional
        Weighting function.
        Defaults None.
    small_number : float, optional
        A small number to be added in before evaluating np.log10 to
        prevent error.
        Defaults to 1e-6.
    norm : int, optional
        The type of norm used to estimate the error.
        Choose ``1`` for $\mathcal{L}_1$ norm and
        ``2`` for $\mathcal{L}_2$ norm.
        Other norms are are possible but not encouraged unless
        there's a specifiy reason.
        Defaults 2.

    Returns
    -------
    float
        The mean log error.

    Notes
    -----
    $\mathcal{L}_1$ norm is more robust while
    $\mathcal{L}_2$ norm is more susceptible to outliers, but fits
    data with large dynamic range well.
    """
    if weight is None:
        weight = np.ones_like(noise1, dtype=float)
    return np.mean((np.log10(abs(noise1))-np.log10(abs(noise2)))**norm*weight)


def spectrum_error(spectrum1, spectrum2,
                   weight=None, small_number=1e-6, norm=2):
    r"""Mean log error between two spectrums. Alias of noise_error().

    Parameters
    ----------
    spectrum1 : array
        Spectrum 1.
    spectrum2 : array
        Spectrum 2.
    weight : array or None, optional
        Weighting function.
        Defaults None.
    small_number : float, optional
        A small number to be added in before evaluating np.log10 to
        prevent error.
        Defaults to 1e-6.
    norm : int, optional
        The type of norm used to estimate the error.
        Choose ``1`` for $\mathcal{L}_1$ norm and
        ``2`` for $\mathcal{L}_2$ norm.
        Other norms are are possible but not encouraged unless
        there's a specifiy reason.
        Defaults 2.

    Returns
    -------
    float
        The mean log error.

    Notes
    -----
    $\mathcal{L}_1$ norm is more robust while
    $\mathcal{L}_2$ norm is more susceptible to outliers, but fits
    data with large dynamic range well.
    """
    return noise_error(spectrum1, spectrum2,
                       weight=weight, small_number=small_number, norm=norm)
