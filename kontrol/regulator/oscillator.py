"""Control regulators designs for oscillator-like systems"""
import control
import numpy as np

import kontrol.regulator.feedback
import kontrol.regulator.predefined


#FIXME find a better name
def pid(
    plant, regulator_type="PID", dcgain=None,
    integrator_ugf=None, integrator_time_constant=None,
    low_pass=None, low_pass_cutoff=None,
    max_ugf=None,  min_gain_margin=2,
    **kwargs):
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
        The integration time constant i(s) for integral control.
        Setting this will override the ``integrator_ugf`` argument.
        Defaults to None.
    max_ugf : float, optional
        The maxmimum tolerable UGF (Hz).
        Set this between the dominate mode and the residual modes that
        don't need to be damped.
        If set to None, this will be set to 1 decade higher than
        the dominant mode.
    
    Returns
    -------
    regulator : TransferFunction
        The regulator.
    """
    s = control.tf("s")
    kp = 0
    ki = 0
    kd = 0

    if regulator_type == "PID":
        kd = kontrol.regulator.feedback.critical_damping(plant, **kwargs)
        regulator = kontrol.regulator.predefined.pid(kd=kd)
        kp = kontrol.regulator.feedback.add_proportional_control(
            plant, regulator=regulator, dcgain=dcgain, **kwargs)
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

    regulator = kontrol.regulator.predefined.pid(kp=kp, ki=ki, kd=kd)
    return regulator


def post_filtering(
        plant, regulator, max_ugf=None, decades_after_ugf=1, phase_margin=45,
        low_pass=None, mtol=1e-6, small_number=1e-6, **kwargs):
    """Add low-pass filter  after regulator.

    This function lowers the the cutoff frequency of a low-pass filter
    until the phase margin at a dedicated ugf reaches the maximum
    tolerable phase margin.

    Parameters
    ----------
    plant : TransferFunction
        The transfer function of the system that needs to be controlled.
    regulator : TransferFunction
        The regulator.
    max_ugf : float, optional
        The maximum ugf.
        If not specified, defaults to 1 decade higher than the last UGF.
        This value can be overrided by the argument ``decades_after_ugf``
        Note that there's no guarantee that the UGF will be lower than this.
        The priority is to match the target phase margin.
        Defaults to None.
    decades_after_ugf : float, optional
        Set max_ugf some decades higher than the UGF of the OLTF
        max_ugf is None.
        Defaults to 1.
    phase_margin : float, optional,
        The target phase margin (Degrees).
        Defaults to 45.
    low-pass : func(cutoff, order) -> TransferFunction, optional
        The low-pass filter.
        If not specified, ``kontrol.regulator.predefined.lowpass()``
        with order 2 will be used.
        Defaults to None.
    mtol : float, optional
        Tolerance for convergence of phase margin.
        Defaults to 1e-6.
    small_number : float, optional
        A small number as a delta f to detect whether the gain is a rising or
        lowering edge at the unity gain frequency.
        Defaults to 1e-6.
    **kwargs
        Keyword arguments passed to ``low_pass``.
    """
    if low_pass is None:
        low_pass = kontrol.regulator.predefined.low_pass
    if "order" not in kwargs.keys():
        kwargs["order"] = 2
    oltf = regulator * plant
    _, _, _, _, ugfs, _ = control.stability_margins(oltf, returnall=True)
    
    if max_ugf is None:
        max_ugf = max(ugfs)/2/np.pi * 10**decades_after_ugf

    ## Make initial guesses for the low-pass filter cutoff frequency.
    lower_edge_mask = (
        (abs(oltf(1j*(ugfs+ugfs*small_number)))
         < abs(oltf(1j*(ugfs-ugfs*small_number))))
    )  # Ignore UGFs with raising gain
    max_ugf_mask = ugfs/2/np.pi < max_ugf  # Ignore UGFs higher than max)ugf.
    mask = lower_edge_mask * max_ugf_mask  #
    ugfs = ugfs[mask]
    
    ## Set two points and use linear approximation to shoot
    ## until reaching the target.
    
    f1 = max(ugfs)/2/np.pi
    f2 = max_ugf

    ## Set a minimum cutoff frequency.
    min_cutoff = f1

    while 1:
        # Makes a low pass with f1 and f2
        # and calculate the phase margins. Use these
        # to linearly approximate the correct point and repeat
        # until converges.
        low_pass1 = low_pass(f1, **kwargs)
        low_pass2 = low_pass(f2, **kwargs)
        oltf1 = regulator * plant * low_pass1
        oltf2 = regulator * plant * low_pass2
        _, pms1, _, _, ugfs1, _ = control.stability_margins(
            oltf1, returnall=True)
        _, pms2, _, _, ugfs2, _ = control.stability_margins(
            oltf2, returnall=True)

        lower_edge_mask1 = (
            (abs(oltf1(1j*(ugfs1+ugfs1*small_number)))
             < abs(oltf1(1j*(ugfs1-ugfs1*small_number))))
        )  # Ignore UGFs with raising gain
        lower_edge_mask2 = (
            (abs(oltf2(1j*(ugfs2+ugfs2*small_number)))
             < abs(oltf2(1j*(ugfs2-ugfs2*small_number))))
        )  # Ignore UGFs with raising gain
        max_ugf_mask1 = ugfs1/2/np.pi < max_ugf
        max_ugf_mask2 = ugfs2/2/np.pi < max_ugf
        mask1 = lower_edge_mask1 * max_ugf_mask1
        mask2 = lower_edge_mask2 * max_ugf_mask2
        pm1 = min(pms1[mask1])
        pm2 = min(pms2[mask2])

        if (abs((pm2-pm1)) / abs(pm1) < mtol and 
            abs(pm1-phase_margin)/abs(phase_margin) < mtol):
            ## If phase margins bounds are closed enough and if they
            ## are close to the target phase margin, terminate.
            break

        ## Linear approximate the correct value.
        dx = f2 - f1
        dy = pm2 - pm1
        slope = dy / dx
        if abs(phase_margin - pm1) > abs(phase_margin - pm2):
            f1 = (phase_margin - pm1) / slope + f1
        else:
            f2 = (phase_margin - pm2) / slope + f2
        if f1 < min_cutoff:
            f1 = min_cutoff
        if f2 < min_cutoff+min_cutoff*small_number:
            f2 = min_cutoff+min_cutoff*small_number 
            # So f1 and f2 are not same or else it could explode.

    return low_pass(f1, **kwargs)


def post_notches():
    """ 
    notch : func(frequency, q, depth) -> TransferFunction, optional
        The notch filter.
        If not specified, ``kontrol.regulator.predefined.notch()``
        will be used.
        Defaults to None.
    """
    pass
