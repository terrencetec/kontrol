"""Tests for kontrol.core.spectral
"""
import control
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal

import kontrol


np.random.seed(123)

# Time axis and sampling frequency
fs = 128
t0 = 0
t_end = 512
t = np.arange(t0, t_end, 1/fs)

# The coherent signal
A = 1
sigma = -.01
gamma = -0.1
omega_0 = 10*2*np.pi
x = A*np.exp((sigma + 1j*omega_0*np.exp(gamma*t)) * t).real

# The sensor dynamics.
zeta = 1
omega_n = 1*2*np.pi
omega_m = 10
s = control.tf("s")
H1 = s**2 / (s**2 + 2*zeta*omega_n*s + omega_n**2)
H2 = H1
H3 = omega_m / (s+omega_m)

# Signals sensed by the sensors.
_, x1 = control.forced_response(sys=H1, T=t, U=x)
_, x2 = control.forced_response(sys=H2, T=t, U=x)
_, x3 = control.forced_response(sys=H3, T=t, U=x)

# The noises
w1 = np.random.normal(loc=0, scale=1, size=len(t))
w2 = np.random.normal(loc=0, scale=1, size=len(t))
w3 = np.random.normal(loc=0, scale=1, size=len(t))
a1 = 0.5
a3 = 5
epsilon_1 = omega_0/100
epsilon_3 = omega_0/200
G1 = a1 / (s+epsilon_1)
G2 = G1
G3 = a3 / (s+epsilon_3)**2
_, n1 = control.forced_response(sys=G1, T=t, U=w1)
_, n2 = control.forced_response(sys=G2, T=t, U=w2)
_, n3 = control.forced_response(sys=G3, T=t, U=w3)

# The readouts
y1 = x1 + n1
y2 = x2 + n2
y3 = x3 + n3

f, P_x = scipy.signal.welch(x, fs=fs)
f, P_n1 = scipy.signal.welch(n1, fs=fs)
f, P_n2 = scipy.signal.welch(n2, fs=fs)
f, P_n3 = scipy.signal.welch(n3, fs=fs)
f, P_y1 = scipy.signal.welch(y1, fs=fs)
f, P_y2 = scipy.signal.welch(y2, fs=fs)
f, P_y3 = scipy.signal.welch(y3, fs=fs)


def test_two_channel_correlation():
    """
    Tests for `kontrol.core.spectral.two_channel_correlation()`.
    """
    P_n1_2channel = kontrol.spectral.two_channel_correlation(y1, y2, fs=fs)

    # Alternatively, use the PSD and coherence.
    _, coherence_12 = scipy.signal.coherence(y1, y2, fs=fs)
    P_n1_2channel_coh = kontrol.spectral.two_channel_correlation(
        P_y1, P_y2, fs=fs, coherence=coherence_12)

    # Alternatively, use the PSD and cross power spectral density.
    _, cpsd_12 = scipy.signal.csd(y1, y2, fs=fs)
    _, cpsd_21 = scipy.signal.csd(y2, y1, fs=fs)
    P_n1_2channel_cpsd = kontrol.spectral.two_channel_correlation(
        P_y1, P_y2, fs=fs, cpsd=cpsd_12)

    ts_equal_coh = np.allclose(P_n1_2channel, P_n1_2channel_coh)
    ts_equal_cpsd = np.allclose(P_n1_2channel, P_n1_2channel_cpsd)
    predict_equal_true = np.allclose(
        np.log10(P_n1_2channel), np.log10(P_n1), rtol=0, atol=0.1)

    assert np.all([ts_equal_coh, ts_equal_cpsd, predict_equal_true])


def test_three_channel_correlation():
    """Tests for `kontrol.core.spectral.three_channel_correlation()`.
    """
    P_n1_3channel = kontrol.spectral.three_channel_correlation(
        y1, y2, y3, fs=fs)
    P_n2_3channel = kontrol.spectral.three_channel_correlation(
        y2, y1, y3, fs=fs)
    P_n3_3channel = kontrol.spectral.three_channel_correlation(
        y3, y1, y2, fs=fs)

    # Alternatively, use PSD and coherences
    _, coherence_12 = scipy.signal.coherence(y1, y2, fs=fs)
    _, coherence_13 = scipy.signal.coherence(y1, y3, fs=fs)
    _, coherence_21 = scipy.signal.coherence(y2, y1, fs=fs)
    _, coherence_23 = scipy.signal.coherence(y2, y3, fs=fs)
    _, coherence_31 = scipy.signal.coherence(y3, y1, fs=fs)
    _, coherence_32 = scipy.signal.coherence(y3, y2, fs=fs)

    n1_kwargs = {
        "coherence_13": coherence_13,
        "coherence_23": coherence_23,
        "coherence_21": coherence_21,
    }
    # Notice the changes.
    n2_kwargs = {
        "coherence_13": coherence_23,
        "coherence_23": coherence_13,
        "coherence_21": coherence_12,
    }
    n3_kwargs = {
        "coherence_13": coherence_32,
        "coherence_23": coherence_12,
        "coherence_21": coherence_13,
    }

    P_n1_3channel_coh = kontrol.spectral.three_channel_correlation(
        P_y1, **n1_kwargs)
    P_n2_3channel_coh = kontrol.spectral.three_channel_correlation(
        P_y2, **n2_kwargs)
    P_n3_3channel_coh = kontrol.spectral.three_channel_correlation(
        P_y3, **n3_kwargs)


    # And Alternatively, use PSD and cross power spectral densities.
    _, cpsd_12 = scipy.signal.csd(y1, y2, fs=fs)
    _, cpsd_13 = scipy.signal.csd(y1, y3, fs=fs)
    _, cpsd_21 = scipy.signal.csd(y2, y1, fs=fs)
    _, cpsd_23 = scipy.signal.csd(y2, y3, fs=fs)
    _, cpsd_31 = scipy.signal.csd(y3, y1, fs=fs)
    _, cpsd_32 = scipy.signal.csd(y3, y2, fs=fs)

    n1_kwargs = {
        "cpsd_13": cpsd_13,
        "cpsd_23": cpsd_23,
        "cpsd_21": cpsd_21
    }
    n2_kwargs = {
        "cpsd_13": cpsd_23,
        "cpsd_23": cpsd_13,
        "cpsd_21": cpsd_12,
    }
    n3_kwargs = {
        "cpsd_13": cpsd_32,
        "cpsd_23": cpsd_12,
        "cpsd_21": cpsd_13
    }

    P_n1_3channel_cpsd = kontrol.spectral.three_channel_correlation(
        P_y1, **n1_kwargs)
    P_n2_3channel_cpsd = kontrol.spectral.three_channel_correlation(
        P_y2, **n2_kwargs)
    P_n3_3channel_cpsd = kontrol.spectral.three_channel_correlation(
        P_y3, **n3_kwargs)

    ts_equal_coh = np.allclose(P_n3_3channel, P_n3_3channel_coh)
    ts_equal_cpsd = np.allclose(P_n3_3channel, P_n3_3channel_coh)
    predict_equal_true = np.allclose(P_n3_3channel, P_n3, rtol=0, atol=0.5)

    assert np.all([ts_equal_coh, ts_equal_cpsd, predict_equal_true])
