"""Spectral analysis related function library.
"""
import numpy as np
import scipy.signal


def two_channel_correlation(x1, x2, fs=1, cpsd=None, coherence=None,
                            **welch_kwargs):
    r"""Noise estimation from two identical sensors' readout.

    Parameter
    ---------
    x1: array
        Sensor readout 1. Time series or Power spectral density.
        The signal should contain a superposition of a
        signal that is correlated with that in `x2` and a self noise
        that is uncorrelated.
        If this is specified as a power spectral density,
        either `cpsd` or `coherence` must be specified.
    x2: array
        Sensor readout 2. Time series or Power spectral density.
        The signal should contain a superposition of a
        signal that is correlated with that in `x1` and a self noise
        that is uncorrelated.
        If this is specified as a power spectral density,
        either `cpsd` or `coherence` must be specified.
    fs: float, optional
        Sampling frequency. Specify only if x1 and x2 are time series.
        If this is specified, this will override the value in **welch_kwargs.
    x_type: str, optional
        Type of `x1` and `x2`.
        Choose from ["time series", "ts", "power spectral density", "psd"]
        If `x1` and `x2` are time series, then select "time series" or "ts".
        If `x1` and `x2` are power spectral densities, then select
        "power spectral density" or "psd".
    cpsd: array, optional
        Cross power spectral density bewween `x1` and `x2`.
        If `cpsd` is specified, `x1` and `x2` will be treated as a
        power spectral density.
        Otherwise, `x1` and `x2` will be treated as time series.
        If `coherence` is specified, `cpsd` will be ignored.
        Default None.
    coherence: array, optional
        Coherence between `x1` and `x2`.
        If coherence is specified, `x1` and `x2` will be treated as a power
        spectral density.
        Otherwise, `x1` and `x2` will be treated as time series.
        If coherence is specified, cpsd will be ignored.
        Default None.
    **welch_kwargs:
        Keyword arguments passed to `scipy.signal.welch` and
        `scipy.signal.coherence`
        to compute power spectral density and coherence
        of `x1` and `x2`, if they are time series.

    Returns
    -------
    noise: array
        Power spectral density of the estimated noise.

    Notes
    -----
    The PSD of the noise is computed as
    .. math::
        P_{nn}(f) = P_{x_1x_1}(f)\left(1-C_{x_1x_2}(f)^{\frac{1}{2}}\right)\,,
    where $P_{x_1x_1}(f)$ is the power spectral density of the readout $x_1$
    and $C_{x_1x_2}(f)$ is the coherence betwwen the readout $x_1$ and $x_2$

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
    if cpsd is None and coherence is None:
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
    noise = psd1 * (1 - coherence**(1/2))
    return noise
