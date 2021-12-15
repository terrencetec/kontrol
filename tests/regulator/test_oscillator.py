"""Tests for kontrol.regulator.oscillator module"""
import control
import numpy as np

import kontrol.regulator


s = control.tf("s")
k = np.random.random()
q = np.random.randint(1, 100)
wn = np.random.random()
plant = k * wn**2 / (s**2 + wn/q*s + wn**2)


def test_pid():
    """Tests for kontrol.regulator.oscillator.pid()"""
    # Tests for errors only. This function is 
    # highly dependent on kontrol.regulator.feedback module.
    kp, ki, kd = kontrol.regulator.oscillator.pid(
        plant, regulator_type="PID", return_gain=True)
    pid = kontrol.regulator.oscillator.pid(plant, regulator_type="PID")
    pd = kontrol.regulator.oscillator.pid(
        plant, regulator_type="PD")
    pi = kontrol.regulator.oscillator.pid(
        plant, regulator_type="PI", dcgain=k, integrator_ugf=wn/2/np.pi/10)
    i = kontrol.regulator.oscillator.pid(
        plant, regulator_type="I", integrator_ugf=wn/2/np.pi/10)
    d = kontrol.regulator.oscillator.pid(plant, regulator_type="D")

    # Test exceptions
    try:
        kontrol.regulator.oscillator.pid(plant, regulator_type="abc")
        raise
    except ValueError:
        pass
