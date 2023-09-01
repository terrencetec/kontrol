"""Spectral analysis related function library.
"""
import numpy as np
import scipy.signal


def two_channel_correlation(psd, coh):
    r"""Noise estimation from two identical sensors' readouts.

    Parameters
    ----------
    psd : array
        The power spectral density of the readout of the sensor
    coh : array
        The coherence between readout of the sensor and another identical
        sensor.

    Returns
    -------
    noise : array
        Power spectral density of the estimated noise.

    Notes
    -----
    The PSD of the noise is computed as

    .. math::
        P_{nn}(f) = P_{x_1x_1}(f)\left(1-C_{x_1x_2}(f)^{\frac{1}{2}}\right)\,,

    where :math:`P_{x_1x_1}(f)` is the power spectral density of the readout
    and :math:`C_{x_1x_2}(f)` is the coherence
    between the two sensor readouts.

    References
    ----------
    .. [1]
        Aaron Barzilai, Tom VanZandt, and Tom Kenny.
        Technique for measurement of the noise of a sensor in the
        presence of large background signals. Review of Scientific Instruments,
        69:2767–2772, 07 1998.
    """
    noise = psd * (1 - coh**0.5)
    return noise


def three_channel_correlation(psd1, psd2=None, psd3=None,
                              csd12=None, csd13=None,
                              csd21=None, csd23=None,
                              csd31=None, csd32=None,
                              returnall=True):
    r"""Noise estimation from three sensors' readouts.

    Parameters
    ----------
    psd1 : array
        The power spectral density of the readout of the first sensor.
    psd2 : array, optional
        The power spectral density of the readout of the second sensor.
        Defaults ``None``.
    psd3 : array, optional
        The power spectral density of the readout of the third sensor.
        Defaults ``None``.
    csd12 : array, optional
        Cross power spectral density between readout 1 and 2.
        If not specified, this will be estimated as ``psd1*psd2/csd21``.
        Default ``None``.
    csd13 : array, optional
        Cross power spectral density between readout 1 and 3.
        If not specified, this will be estimated as ``psd1*psd3/csd31``.
        Default ``None``.
    csd21 : array, optional
        Cross power spectral density between readout 2 and 1.
        If not specified, this will be estimated as ``psd2*psd1/csd12``.
        Default ``None``.
    csd23 : array, optional
        Cross power spectral density between readout 2 and 3.
        If not specified, this will be estimated as ``psd2*psd3/csd32``.
        Default ``None``.
    csd31 : array, optional
        Cross power spectral density between readout 3 and 1.
        If not specified, this will be estimated as ``psd1*psd3/csd13``.
        Default ``None``.
    csd32 : array, optional
        Cross power spectral density between readout 3 and 1.
        If not specified, this will be estimated as ``psd3*psd2/csd23``.
        Default ``None``.
    returnall : boolean, optional
        If ``True``, return all three noise estimations.
        If ``False``, return noise estimation of first sensor only.
        Defaults True.

    Returns
    -------
    noise1 : array
        Power spectral density of the estimated noise in `psd1`.
    noise2 : array, optional
        Power spectral density of the estimated noise in `psd2`.
        Returns only if ``returnall==True``
    noise3 : array, optional
        Power spectral density of the estimated noise in `psd3`.
        Returns only if ``returnall==True``

    Notes
    -----
    The PSD of the noise in `psd1` is then computed as

    .. math::
       P_{n_1n_1}(f) = \left\lvert P_{x_1x_1}(f) -
       \frac{P_{x_1x_3}(f)}{P_{x_2x_3}(f)}P_{x_2x_1}\right\vert\,,

    If ``returnall`` is ``True``, at least ``psd1``, ``psd2``, ``psd3``,
    (``csd13`` or ``csd31``), (``csd23`` or ``csd32``), and
    (``csd12`` and ``csd21``) must be provided.

    References
    ----------
    .. [2]
        R. Sleeman, A. Wettum, and J. Trampert.
        Three-channel correlation analysis: A new technique to measure
        instrumental noise of digitizers and seismic sensors.
        Bulletin of the Seismological Society of America, 96:258–271, 2006.
    """
    if csd12 is None:
        if all([csd21 is not None, psd1 is not None, psd2 is not None]):
            csd12 = psd1*psd2/csd21
    if csd13 is None:
        if all([csd31 is not None, psd1 is not None, psd3 is not None]):
            csd13 = psd1*psd3/csd31
    if csd21 is None:
        if all([csd12 is not None, psd2 is not None, psd1 is not None]):
            csd21 = psd2*psd1/csd12
    if csd23 is None:
        if all([csd32 is not None, psd2 is not None, psd3 is not None]):
            csd23 = psd2*psd3/csd32
    if csd31 is None:
        if all([csd13 is not None, psd3 is not None, psd1 is not None]):
            csd31 = psd3*psd1/csd13
    if csd32 is None:
        if all([csd23 is not None, psd3 is not None, psd2 is not None]):
            csd32 = psd3*psd2/csd23
    if returnall:
        if any([psd2 is None, psd3 is None,
                csd12 is None, csd13 is None,
                csd21 is None, csd23 is None,
                csd31 is None, csd32 is None]):
            raise ValueError("If returnall is True,"
                             " at least psd2, psd3"
                             " (csd13 or csd31),"
                             " (csd23 or csd32), and"
                             " (csd12 and csd21) must be provided.")
        noise1 = three_channel_correlation(
            psd1, csd13=csd13, csd23=csd23, csd21=csd21, returnall=False)
        noise2 = three_channel_correlation(
            psd2, csd13=csd21, csd23=csd31, csd21=csd32, returnall=False)
        noise3 = three_channel_correlation(
            psd3, csd13=csd32, csd23=csd12, csd21=csd13, returnall=False)
        return noise1, noise2, noise3
    else:
        if any([csd13 is None, csd23 is None, csd21 is None]):
            raise ValueError("(csd13 or csd31), (csd23 or csd32),"
                             " and (csd21 or csd12) must be provided")
        return abs(psd1-csd13/csd23*csd21)


def asd2ts(asd, f=None, fs=None, t=None, window=None, zero_mean=True):
    """Simulate time series from amplitude spectral density

    Parameters
    ----------
    asd : array
        The amplitude spectral density.
    f : array, optional
        The frequency axis of the amplitude spectral density.
        This is used to calculate the sampling frequency.
        If ``fs`` is not specified, ``f`` must be specified.
        Defaults ``None``.
    fs : float, optional
        The sampling frequency in Hz.
        If ``f`` is specified, the last element of ``f`` will
        be treated as the Nyquist frequency so the double of
        it would be the sampling frequency.
        Defaults ``None``.
    t : array, optional
        The desired time axis for the time series.
        If ``t`` is specified, then the time series will
        be interpolated using ``numpy.interp()`` assuming
        that the time series is periodic.
        Default ``None``.
    window : array, optional
        The FFT window used to compute the amplitude spectral density.
        Defaults ``None``.
    zero_mean : boolean, optional
        Returns a time series with zero mean.
        Defaults ``True``.

    Returns
    -------
    t : array
        Time axis.
    time_series : array
        The time series

    Notes
    -----
    Using a custom time axis is not recommended as interpolation leads
    to distortion of the signal.
    To extend the signal in time, it's recommended to repeat the
    original time series instead.
    """
    if f is not None:
        fs = f[-1]*2  # Double the Nyquist frequency.
    elif fs is None:
        raise ValueError("Either f or fs must be specified.")

    if window is None:
        window = np.ones_like(asd)

    s2 = np.sum(window**2)  # One of the normalization factor.
    # Compute absolute value of the FFT
    abs_ym = asd*np.sqrt(fs*s2)
    # Assume ASD is noise and generate random phase for the FFT
    random_phase = np.random.random(len(abs_ym))*360-180
    # Convert abs(FFT) to FFT by adding random phase
    ym = abs_ym * np.exp(1j*random_phase)
    ts = np.fft.irfft(ym)

    if zero_mean:
        ts -= np.mean(ts)

    t_original = np.linspace(0, (len(ts)-1)/fs, len(ts))
    if t is None:
        t = t_original
    else:
        period = t_original[-1] - t_original[0]
        ts = np.interp(t, xp=t_original, fp=ts, period=period)
    return t, ts


def asd2rms(asd, f=None, df=1., return_series=True):
    r"""Calculate root-mean-squared value from amplitude spectral density

    Parameters
    ----------
    asd : array
        The amplitude spectral density
    f : array, optional
        The frequency axis.
        Defaults ``None``.
    df : float, optional
        The frequency spacing.
        Defaults 1.
    return_series : bool, optional
        Returns the RMS as a frequency series,
        where each value is the integrated RMS from highest frequency.
        If False, returns a single RMS value for the whole spectrum.
        Defaults True.

    Returns
    -------
    array
        The integrated RMS series, if ``return_series==True``.
    float
        The integrated RMS value, if ``return_series==False``.

    Notes
    -----
    The integrated RMS series is defined as

    .. math::

       x_\mathrm{RMS}(f) = \int_\infty^{f}\,x(f')^2\,df'\,,

    where :math:`x(f)` is the amplitude spectral density.

    When ``return_series`` is False, only :math:`x_\mathrm{RMS}(0)` is
    returned.
    """
    # Flip the ASD to integrate from high frequency to low.
    # if f is not None:
    #     f_inv = -np.flip(f)  # Minus sign necessary as integration limits
    #                          # are flipped
    # else:
    #     f_inv = None
    # asd_inv = np.flip(asd)
    if not return_series:
        rms = np.sqrt(np.trapz(y=asd**2, x=f, dx=df))
    else:
        rms = np.zeros_like(asd)
        for i in range(len(rms)):
            if f is None:
                rms[i] = np.sqrt(np.trapz(y=asd[i:]**2, dx=df))
            else:
                rms[i] = np.sqrt(np.trapz(y=asd[i:]**2, x=f[i:]))
        # rms = np.flip(rms)
    return rms


def pad_below_minima(series, pad_index=0, **kwargs):
    """Pad series below local minima

    Parameters
    ----------
    series : array
        The series to be padded.
    pad_index : int, optional
        The index of the local minima.
        Defaults to 0.
    **kwargs
        Keyword arguments passed to scipy.signal.argrelmin()

    Returns
    -------
    series_padded : array
        The padded series
    """
    i_min_list = scipy.signal.argrelmin(series, **kwargs)
    i_min = i_min_list[0][pad_index]
    series_padded = series.copy()
    series_padded[:i_min+1] = series[i_min]
    return series_padded


def pad_above_minima(series, pad_index=-1, **kwargs):
    """Pad series above local minima

    Parameters
    ----------
    series : array
        The series to be padded.
    pad_index : int, optional
        The index of the local minima.
        Defaults to -1.
    **kwargs
        Keyword arguments passed to scipy.signal.argrelmin()

    Returns
    -------
    series_padded : array
        The padded series
    """
    i_min_list = scipy.signal.argrelmin(series, **kwargs)
    i_min = i_min_list[0][pad_index]
    series_padded = series.copy()
    series_padded[i_min:] = series[i_min]
    return series_padded


def pad_below_maxima(series, pad_index=0, **kwargs):
    """Pad series below local maxima

    Parameters
    ----------
    series : array
        The series to be padded.
    pad_index : int, optional
        The index of the local maxima.
        Defaults to 0.
    **kwargs
        Keyword arguments passed to scipy.signal.argrelmin()

    Returns
    -------
    series_padded : array
        The padded series
    """
    i_max_list = scipy.signal.argrelmax(series, **kwargs)
    i_max = i_max_list[0][pad_index]
    series_padded = series.copy()
    series_padded[:i_max+1] = series[i_max]
    return series_padded


def pad_above_maxima(series, pad_index=-1, **kwargs):
    """Pad series above local maxima

    Parameters
    ----------
    series : array
        The series to be padded.
    pad_index : int, optional
        The index of the local maxima.
        Defaults to -1.
    **kwargs
        Keyword arguments passed to scipy.signal.argrelmin()

    Returns
    -------
    series_padded : array
        The padded series
    """
    i_max_list = scipy.signal.argrelmax(series, **kwargs)
    i_max = i_max_list[0][pad_index]
    series_padded = series.copy()
    series_padded[i_max:] = series[i_max]
    return series_padded
