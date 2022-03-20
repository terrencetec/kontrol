"""Tests for kontrol.core.spectral
"""
import control
import numpy as np
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
    _, coh = scipy.signal.coherence(y1, y2, fs=fs)
    P_n1 = kontrol.spectral.two_channel_correlation(psd=P_y1, coh=coh)


def test_three_channel_correlation():
    """Tests for `kontrol.core.spectral.three_channel_correlation()`.
    """
    _, csd12 = scipy.signal.csd(y1, y2, fs=fs)
    _, csd13 = scipy.signal.csd(y1, y3, fs=fs)
    _, csd21 = scipy.signal.csd(y2, y1, fs=fs)
    _, csd23 = scipy.signal.csd(y2, y3, fs=fs)
    _, csd31 = scipy.signal.csd(y3, y1, fs=fs)
    _, csd32 = scipy.signal.csd(y3, y2, fs=fs)

    n1_kwargs = {
        "csd13": csd13,
        "csd23": csd23,
        "csd21": csd21,
        "returnall": False,
    }
    n2_kwargs = {
        "csd13": csd23,
        "csd23": csd13,
        "csd21": csd12,
        "returnall": False,
    }
    n3_kwargs = {
        "csd13": csd32,
        "csd23": csd12,
        "csd21": csd13,
        "returnall": False,
    }
    
    # Test functionality only, not testing correctness.
    P_n1 = kontrol.spectral.three_channel_correlation(P_y1, **n1_kwargs)
    P_n2 = kontrol.spectral.three_channel_correlation(P_y2, **n2_kwargs)
    P_n3 = kontrol.spectral.three_channel_correlation(P_y3, **n3_kwargs)
    P_n1, P_n2, P_n3 = kontrol.spectral.three_channel_correlation(
        P_n1, P_n2, P_n3, csd13=csd13, csd23=csd23, csd21=csd21)
    P_n1, P_n2, P_n3 = kontrol.spectral.three_channel_correlation(
        P_n1, P_n2, P_n3, csd31=csd31, csd32=csd32, csd12=csd12)
    
    # Test raises
    try:
        kontrol.spectral.three_channel_correlation(P_y1)
        raise
    except ValueError:
        pass

    try:
        kontrol.spectral.three_channel_correlation(P_y1, returnall=False)
        raise
    except ValueError:
        pass


def test_asd2ts():
    """Tests for kontrol.spectral.asd2ts"""
    f = np.linspace(0, 128, 4096)
    f = f[f>0]
    s = control.tf("s")
    color = (s+1)**2 / (s**2 * (s+10))
    colored_noise_asd = abs(color(1j*2*np.pi*f))

    fs = f[-1]*2
    averages = 10
    t = np.arange(0, len(f)*2*1/fs*averages, 1/fs)
    t_sim, time_series = kontrol.spectral.asd2ts(colored_noise_asd, f=f, t=t)
    fs_sim = 1/(t_sim[1]-t_sim[0])
    window = np.hanning(int(len(time_series)/averages))
    f_sim, psd_sim = scipy.signal.welch(time_series, fs=fs_sim, window=window)
    asd_sim = psd_sim[f_sim>0]**0.5
    f_sim = f_sim[f_sim>0]
    log_mse = np.mean((np.log10(asd_sim) - np.log10(colored_noise_asd))**2)
    assert log_mse < 0.1

    # Test raise
    try:
        kontrol.spectral.asd2ts(colored_noise_asd)
        raise
    except ValueError:
        pass
    # Try without specifying time
    t_sim, time_series = kontrol.spectral.asd2ts(colored_noise_asd, f=f)


def test_asd2rms():
    """Tests for kontrol.spectral.asd2rms()"""
    t = np.linspace(0, 10, 32768)
    y = np.random.normal(loc=0, scale=1, size=len(t))

    fs = 1/(t[1]-t[0])

    f, pyy = scipy.signal.welch(y, fs=fs, nfft=len(y)/16)

    asd = pyy**0.5
    rms = kontrol.spectral.asd2rms(asd=asd, f=f)
    assert np.isclose(1, rms[0], rtol=1e-2)

    rms = kontrol.spectral.asd2rms(asd=asd, f=f, return_series=False)
    assert np.isclose(1, rms, rtol=1e-2)

    rms = kontrol.spectral.asd2rms(asd=asd, df=f[1]-f[0])
    assert np.isclose(1, rms[0], rtol=1e-2)

    rms = kontrol.spectral.asd2rms(asd=asd, df=f[1]-f[0], return_series=False)
    assert np.isclose(1, rms, rtol=1e-2)

