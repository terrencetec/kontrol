"""Control regulators designs for oscillator-like systems"""
import kontrol.regulator.feedback
import kontrol.regulator.predefined


# FIXME find a better name
def pid(
    plant, regulator_type="PID", dcgain=None,
    integrator_ugf=None, integrator_time_constant=None,
        return_gain=False, **kwargs):
    """PID-like controller design for oscillator-like systems

    Parameters
    ----------
    plant : TransferFunction
        The transfer function of the system that needs to be controlled.
    regulator_type : str, optional
        The type of the contorl regulator.
        Choose from ``{"PID", "PD", "PI", "I", "D"}`` for
        proportional-integral-derivative, proportional-derivative,
        proportional-integral, or derivative (velocity) control respectively.
        Defaults to "PID".
    dcgain : float, optional
        The DC gain of the OLTF of the proportional control.
        If set to None, it will be set automatically
        depending on the type of the controller.
        If ``regulator_type=="PI"``, then dcgain will be set such that
        the proportional control UGF matches that of the integral control.
        If ``regulator_type=="PD" or "PID"``, then the dcgain will be set
        such that it matches the UGF of the derivative control.
        Defaults to None.
    integrator_ugf : float, optional
        The unity gain frequency (Hz) of the integral control.
        This is the inverse of the integration time constant.
        If ``integrator_time_constant is not None``, then this value will be
        ignored.
        If set to None, it'll be set to match the UGF of the
        derivative control.
        For ``regulator_type=="I"``, this must be specified.
        Defaults to None.
    integrator_time_constant : float, optional,
        The integration time constant (s) for integral control.
        Setting this will override the ``integrator_ugf`` argument.
        Defaults to None.
    return_gain : boolean, optional
        Return the PID gain instead.

    Returns
    -------
    regulator : TransferFunction, optional
        The regulator.
        Return only if return_gain is ``False``.
    kp : float, optional
        Proportional gain.
        Return only if return_gain is ``True''.
    ki : float, optional
        Integral gain.
        Return only if return_gain is ``True``.
    kd : float, optional
        Derivative gain.
        Return only if return_gain is ``True``.
    """
    kp = 0
    ki = 0
    kd = 0

    if regulator_type == "PID":
        kd = kontrol.regulator.feedback.critical_damping(plant, **kwargs)
        regulator = kontrol.regulator.predefined.pid(kd=kd)
        kp = kontrol.regulator.feedback.add_proportional_control(
            plant, regulator=regulator, dcgain=dcgain, **kwargs)
        # Commented line below so the open-loop gain don't go
        # below unity at low frequency.
        # regulator = kontrol.regulator.predefined.pid(kd=kd, kp=kp)
        ki = kontrol.regulator.feedback.add_integral_control(
            plant, regulator=regulator,
            integrator_ugf=integrator_ugf,
            integrator_time_constant=integrator_time_constant,
            **kwargs)
    elif regulator_type == "PD":
        kd = kontrol.regulator.feedback.critical_damping(plant, **kwargs)
        regulator = kontrol.regulator.predefined.pid(kd=kd)
        kp = kontrol.regulator.feedback.add_proportional_control(
            plant, regulator=regulator, dcgain=dcgain, **kwargs)
    elif regulator_type == "PI":
        kp = kontrol.regulator.feedback.add_proportional_control(
            plant, dcgain=dcgain, **kwargs)
        ki = kontrol.regulator.feedback.add_integral_control(
            plant, integrator_ugf=integrator_ugf,
            integrator_time_constant=integrator_time_constant)
    elif regulator_type == "I":
        ki = kontrol.regulator.feedback.add_integral_control(
            plant, integrator_ugf=integrator_ugf,
            integrator_time_constant=integrator_time_constant)
    elif regulator_type == "D":
        kd = kontrol.regulator.feedback.critical_damping(
            plant, **kwargs)
    else:
        raise ValueError('Invalid regulator_type. '
                         'Please select regulator_type from {"PID", "PD", '
                         '"PI", "D"}.')
    if return_gain:
        return kp, ki, kd
    else:
        regulator = kontrol.regulator.predefined.pid(kp=kp, ki=ki, kd=kd)
        return regulator
