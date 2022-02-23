"""Spectral analysis related function library.
"""
import numpy as np
import scipy.signal


def two_channel_correlation(x1, x2, fs=None, cpsd=None, coherence=None,
                            **welch_kwargs):
    r"""Noise estimation from two identical sensors' readouts.

    Parameters
    ----------
    x1 : array
        Sensor readout 1. Time series or Power spectral density.
        The signal should contain a superposition of a
        signal that is correlated with that in `x2` and a self noise
        that is uncorrelated.
        If this is specified as time series,
        `fs` must be specified.
        If this is specified as a power spectral density,
        either `cpsd` or `coherence` must be specified.
    x2 : array
        Sensor readout 2. Time series or Power spectral density.
        The signal should contain a superposition of a
        signal that is correlated with that in `x1` and a self noise
        that is uncorrelated.
        If this is specified as time series,
        `fs` must be specified.
        If this is specified as a power spectral density,
        either `cpsd` or `coherence` must be specified.
    fs : float, optional
        Sampling frequency.
        This must be specified if `x1` and `x2` are time series.
        If this is specified, this will override the value in **welch_kwargs.
        Default None.
    x_type : str, optional
        Type of `x1` and `x2`.
        Choose from ["time series", "ts", "power spectral density", "psd"]
        If `x1` and `x2` are time series, then select "time series" or "ts".
        If `x1` and `x2` are power spectral densities, then select
        "power spectral density" or "psd".
    cpsd : array, optional
        Cross power spectral density bewween `x1` and `x2`.
        If `cpsd` is specified, `x1` and `x2` will be treated as a
        power spectral density.
        Otherwise, `x1` and `x2` will be treated as time series.
        If `coherence` is specified, `cpsd` will be ignored.
        Default None.
    coherence : array, optional
        Coherence between `x1` and `x2`.
        If coherence is specified, `x1` and `x2` will be treated as a power
        spectral density.
        Otherwise, `x1` and `x2` will be treated as time series.
        If coherence is specified, cpsd will be ignored.
        Default None.
    **welch_kwargs :
        Keyword arguments passed to `scipy.signal.welch` and
        `scipy.signal.coherence`
        to compute power spectral density and coherence
        of `x1` and `x2`, if they are time series.

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
    :math:`x_1` and :math:`C_{x_1x_2}(f)` is the coherence
    betwwen the readout :math:`x_1` and :math:`x_2`

    References
    ----------
    .. [1]
        Aaron Barzilai, Tom VanZandt, and Tom Kenny.
        Technique for measurement of the noise of a sensor in the
        presence of large background signals. Review of Scientific Instruments,
        69:2767–2772, 07 1998.
    """
    if fs is not None:
        welch_kwargs["fs"] = fs
    if cpsd is None and coherence is None and "fs" in welch_kwargs.keys():
        ## x1 and x2 are time series, compute the PSD and coherence.
        _, psd1 = scipy.signal.welch(x1, **welch_kwargs)
        _, coherence = scipy.signal.coherence(x1, x2, **welch_kwargs)
    elif coherence is not None:
        psd1 = x1
    elif cpsd is not None:
        ## x1 and x2 are PSDs but coherence is not given.
        psd1 = x1
        psd2 = x2
        coherence = np.abs(cpsd)**2 / (psd1*psd2)
    else:
        raise ValueError("The following must be specified:\n"
                         "If 'x1', and 'x2' are time series, specify:\n"
                         "'x1', 'x2', and 'fs'.\n"
                         "If 'x1, and 'x2' are power spectral densities,"
                         "specify:\n"
                         "'x1', 'x2' and 'coherence' or\n"
                         "'x1', 'x2' and 'cpsd'.")
    noise = psd1 * (1 - coherence**(1/2))
    return noise


def three_channel_correlation(x1, x2=None, x3=None, fs=None,
                              cpsd_13=None, cpsd_23=None, cpsd_21=None,
                              coherence_13=None, coherence_23=None,
                              coherence_21=None, **welch_kwargs):
    r"""Noise estimation from three sensors' readouts.

    If `x1`, `x2`, and `x3` are time series:
    `three_channel_correlation(x1, x2, x3, fs,...)`
    If `x1`, `x2` and `x3` are power spectral densities,
    `three_channel_correlation(x1, coherence_13, coherence_23,
    coherence_21,...)`
    or
    `three_channel_correlation(x1, cpsd_13, cpsd_23, cpsd_21,...)`

    Parameters
    ----------
    x1 : array
        Sensor readout 1. Time series or Power spectral density.
        The signal should contain a superposition of a
        signal that is correlated with that in `x2` and a self noise
        that is uncorrelated.
        If this is specified as time series,
        `fs` must be specified.
        If this is specified as a power spectral density,
        either `cpsd` or `coherence` must be specified.
    x2 : array, optional
        Sensor readout 2. Time series or Power spectral density.
        The signal should contain a superposition of a
        signal that is correlated with that in `x1` and `x3` and a self noise
        that is uncorrelated.
        This must be specified if `x1` is time series.
        Default None
    x3 : array, optional
        Sensor readout 3. Time series or Power spectral density.
        The signal should contain a superposition of a
        signal that is correlated with that in `x1` and `x2` and a self noise
        that is uncorrelated.
        This must be specified if `x1` is time series.
        Default None
    fs : float, optional
        Sampling frequency.
        This must be specified if `x1`, `x2`, and `x3` are time series.
        If this is specified, this will override the value in **welch_kwargs.
    x_type : str, optional
        Type of `x1` and `x2`.
        Choose from ["time series", "ts", "power spectral density", "psd"]
        If `x1` and `x2` are time series, then select "time series" or "ts".
        If `x1` and `x2` are power spectral densities, then select
        "power spectral density" or "psd".
    cpsd_13 : array, optional
        Cross power spectral density bewween `x1` and `x3`.
        If `coherence` is specified, `cpsd` will be ignored.
        Default None.
    cpsd_23 : array, optional
        Cross power spectral density bewween `x2` and `x3`.
        If `coherence` is specified, `cpsd` will be ignored.
        Default None.
    cpsd_21 : array, optional
        Cross power spectral density bewween `x2` and `x1`.
        If `coherence` is specified, `cpsd` will be ignored.
        Default None.
    coherence_13 : array, optional
        Coherence between `x1` and `x3`.
        If coherence is specified, `x1`, `x2`m and `x3` will be treated as
        power spectral densities.
        Otherwise, `x1`, `x2`, and `x3` will be treated as time series.
        If coherence is specified, cpsd will be ignored.
        Default None.
    coherence_23 : array, optional
        Coherence between `x2` and `x3`.
        If coherence is specified, `x1`, `x2`m and `x3` will be treated as
        power spectral densities.
        Otherwise, `x1`, `x2`, and `x3` will be treated as time series.
        If coherence is specified, cpsd will be ignored.
        Default None.
    coherence_21 : array, optional
        Coherence between `x2` and `x1`.
        If coherence is specified, `x1`, `x2`, and `x3` will be treated as
        power spectral densities.
        Otherwise, `x1`, `x2`, and `x3` will be treated as time series.
        If coherence is specified, cpsd will be ignored.
        Default None.
    **welch_kwargs :
        Keyword arguments passed to `scipy.signal.welch` and
        `scipy.signal.coherence`
        to compute power spectral density and coherence
        of `x1` and `x2`, if they are time series.

    Returns
    -------
    noise : array
        Power spectral density of the estimated noise in `x1`.

    Notes
    -----
    If coherences `coherence_13`, `coherence_23`, and `coherence_21`
    are specified,
    the PSD of the noise in `x1` is computed as

    .. math::
        P_{n_1n_1}(f) = P_{x_1x_1}(f)\left[1-
        \left(\frac{C_{x_1x_3}(f)}{C_{x_2x_3}(f)}C_{x_2x_1}\right)
        ^{\frac{1}{2}}\right]\,,

    where :math:`P_{x_1x_1}(f)` is the power spectral density of the readout
    :math:`x_1` and :math:`C_{x_ix_j}(f)` is the coherence
    betwwen the readout :math:`x_i` and :math:`x_j`.

    If cross power spectral densities `cpsd_13`, `cpsd_23`, and `cpsd_21` are
    specified instead, the PSD of the noise in `x1` is then computed as

    .. math::
       P_{n_1n_1}(f) = P_{x_1x_1}(f) -
       \left\vert\frac{P_{x_1x_3}(f)}{P_{x_2x_3}(f)}P_{x_2x_1}\right\vert\,,

    If none of the above is specified, then `x1`, `x2`, and `x3` will be
    treated as time series and their coherence will be computed and
    used to to calculate the PSD of noise in `x1` using the first equation.

    References
    ----------
    .. [2]
        R. Sleeman, A. Wettum, and J. Trampert.
        Three-channel correlation analysis: A new technique to measure
        instrumental noise of digitizers and seismic sensors.
        Bulletin of the Seismological Society of America, 96:258–271, 2006.
    """
    if fs is not None:
        welch_kwargs["fs"] = fs
    if ((cpsd_13 is None or cpsd_23 is None or cpsd_21 is None) and
       (coherence_13 is None or coherence_23 is None or coherence_21 is None)
       and (x2 is not None and x3 is not None)
       and "fs" in welch_kwargs.keys()):
        ## x1, x2, and x3 are time series, compute the PSD and coherence.
        _, psd1 = scipy.signal.welch(x1, **welch_kwargs)
        _, coherence_13 = scipy.signal.coherence(x1, x3, **welch_kwargs)
        _, coherence_23 = scipy.signal.coherence(x2, x3, **welch_kwargs)
        _, coherence_21 = scipy.signal.coherence(x2, x1, **welch_kwargs)
    elif (coherence_13 is not None and coherence_23 is not None
         and coherence_21 is not None):
        psd1 = x1
    elif cpsd_13 is not None and cpsd_23 is not None and cpsd_21 is not None:
        ## x1, x2 and x2 are PSDs but coherence is not given.
        psd1 = x1
        noise = psd1 - np.abs(cpsd_13/cpsd_23*cpsd_21)
        return noise
    else:
        raise ValueError("The following must be specified:\n"
                         "If 'x1', 'x2', and 'x3' are time series, specify:\n"
                         "'x1', 'x2', 'x3', and 'fs'.\n"
                         "If 'x1, 'x2', 'x3' are power spectral densities,"
                         "specify:\n"
                         "'x1', 'coherence_13', 'coherence_23',and"
                         "'coherence_21'. or\n"
                         "'x1', 'cpsd_13', 'cpsd_23', and 'cpsd_21'.")
    noise = psd1 * (1 - (coherence_13/coherence_23*coherence_21)**0.5)
    return noise


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
