"""Tests for kontrol.regulator.feedback module"""
import control
import numpy as np

import kontrol.regulator


s = control.tf("s")
k = np.random.random()
q = np.random.randint(1, 100)
wn = np.random.random()
plant = k * wn**2 / (s**2 + wn/q*s + wn**2)


def test_critical_damping():
    """Tests for kontrol.regulator.feedback.critical_damping()."""
    correct_kd = 2/wn/k
    kd = kontrol.regulator.feedback.critical_damping(plant)
    kd_optimized = kontrol.regulator.feedback.critical_damping(
        plant, method="optimized")
    correct_kd_optimized = (1/0.5 - 1/q) / (k*wn)
    assert np.isclose(correct_kd, kd)
    assert np.isclose(correct_kd_optimized, kd_optimized)


def test_critical_damp_optimized():
    """Tests for kontrol.regulator.feedback.critical_damp_optimize()"""
    ## For testing exceptions only.
    # Test gain_step exceptions
    try:
        kontrol.regulator.feedback.critical_damp_optimize(plant, gain_step=0.9)
        raise
    except ValueError:
        pass
    # Test ktol exception
    try:
        kontrol.regulator.feedback.critical_damp_optimize(plant, ktol=0)
        raise
    except ValueError:
        pass


def test_add_proportional_control():
    """Tests for kontrol.regulator.feedback.add_proportional_control()."""
    kd = kontrol.regulator.feedback.critical_damping(plant)
    regulator = kontrol.regulator.predefined.pid(kd=kd)
    kp = kontrol.regulator.feedback.add_proportional_control(
        plant, regulator)
    _, _, _, _, ugf_kd, _ = control.stability_margins(
        regulator*plant, returnall=True)
    _, _, _, _, ugf_kp, _ = control.stability_margins(
        kp*plant, returnall=True)
    assert np.isclose(min(ugf_kd), min(ugf_kp)) 

    dcgain = np.random.random()
    kp = kontrol.regulator.feedback.add_proportional_control(
        plant, dcgain=dcgain)
    assert np.isclose((kp*plant).dcgain(), dcgain)

    # Test excetion
    try:
        kontrol.regulator.feedback.add_proportional_control(plant)
        raise
    except ValueError:
        pass


def test_add_integral_control():
    """Tests for kontrol.regulator.feedback.add_integral_control()."""
    kd = kontrol.regulator.feedback.critical_damping(plant)
    regulator = kontrol.regulator.predefined.pid(kd=kd)
    ki = kontrol.regulator.feedback.add_integral_control(
        plant, regulator)
    _, _, _, _, ugf_kd, _ = control.stability_margins(
        regulator*plant, returnall=True)
    _, _, _, _, ugf_ki, _ = control.stability_margins(
        ki/s*plant.dcgain(), returnall=True)
    assert np.isclose(min(ugf_kd), min(ugf_ki))

    integrator_ugf = wn/2/np.pi/10
    ki = kontrol.regulator.feedback.add_integral_control(
        plant, integrator_ugf=integrator_ugf)
    _, _, _, _, ugf_ki, _ = control.stability_margins(
        ki/s*plant, returnall=True)
    assert np.isclose(integrator_ugf, min(ugf_ki)/2/np.pi, rtol=1e-1)

    integrator_time_constant = 1/integrator_ugf
    ki = kontrol.regulator.feedback.add_integral_control(
        plant, integrator_time_constant=integrator_time_constant)
    _, _, _, _, ugf_ki, _ = control.stability_margins(
        ki/s*plant, returnall=True)

    assert np.isclose(integrator_ugf, min(ugf_ki)/2/np.pi, rtol=1e-1)

    # Test exception
    try:
        kontrol.regulator.feedback.add_integral_control(plant)
        raise
    except ValueError:
        pass


    
