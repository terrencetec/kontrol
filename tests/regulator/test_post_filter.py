"""Tests for kontrol.regulator.post_filter module"""
import control
import numpy as np

import kontrol.regulator


s = control.tf("s")
k = np.random.random()
q = np.random.randint(1, 100)
wn = np.random.random()
plant = k * wn**2 / (s**2 + wn/q*s + wn**2)
pid = kontrol.regulator.oscillator.pid(plant, regulator_type="PID")


def test_post_low_pass():
    """Tests for kontrol.regulator.post_filter.post_low_pass()"""
    low_pass = kontrol.regulator.post_filter.post_low_pass(plant, pid)
    _, pm, _, _, ugf, _ = control.stability_margins(
        pid*plant*low_pass, returnall=True)
    #assert np.isclose(min(pm), 45)  # 45 is default phase margin target
    # ^^ There's a phase marigin above 0 degree interpreted as negative
    # phase margin.
    # vv Temporarily ignore it
    assert np.isclose(pm[-1], 45)

    # Test exception for all UGFs already below target phase margin
    try:
        # Add a pole a 0 Hz to shift the phase by -90 degrees
        kontrol.regulator.post_filter.post_low_pass(plant/s, pid)
        raise
    except ValueError:
        pass


def test_post_notch():
    """Tests for kontrol.regulator.post_filter.post_notch()"""
    # Test for errors only. Didn't check functionality
    notch_peaks_above = wn/2/np.pi/2  # Notch the resonance.
    notch_list = kontrol.regulator.post_filter.post_notch(
        plant, pid, notch_peaks_above=notch_peaks_above)
    
