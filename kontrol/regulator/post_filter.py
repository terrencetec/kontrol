"""Functions for designing post-regulator filters"""
import control
import numpy as np

import kontrol.logger
import kontrol.regulator.feedback
import kontrol.regulator.predefined


def post_low_pass(
        plant, regulator, post_filter=None,
        ignore_ugf_above=None, decades_after_ugf=1,
        phase_margin=45, f_start=None, f_step=1.1,
        low_pass=None, mtol=1e-6, small_number=1e-6,
        oscillatory=True, **kwargs):
    """Add low-pass filter after regulator.

    This function lowers/increase the the cutoff frequency
    of a low-pass filter until the phase margin at a
    dedicated ugf crosses the specified phase margin.
    Then, runs a bisection algorithm to poolish the cutoff
    frequency until the phase margin converges relative to
    the specified tolerance.

    Parameters
    ----------
    plant : TransferFunction
        The transfer function of the system that needs to be controlled.
    regulator : TransferFunction
        The regulator.
    post_filter : TransferFunction, optional
        Any post filters that will be applied on top of the regulator.
        Defaults None.
    ignore_ugf_above : float, optional
        Ignore unity gain frequencies higher than ``ignore_ugf_above`` (Hz).
        If not specified, defaults to 1 decade higher than the last UGF.
        This value can be overrided by the argument ``decades_after_ugf``
        Note that there's no guarantee that the UGF will be lower than this.
        The priority is to match the target phase margin.
        Defaults to None.
    decades_after_ugf : float, optional
        Set ignore_ugf_above some decades higher than the UGF of the OLTF
        ignore_ugf_above is None.
        Defaults to 1.
    phase_margin : float, optional,
        The target phase margin (Degrees).
        Defaults to 45.
    f_start : float, optional,
        The cutoff frequency to start iterating with.
        If not specified, defaults to some decades higher than the
        highest UGF. "Some decade" is set by ``decades_after_ugf``.
        Defaults None.
    f_step : float, optional,
        The gain that is used to multiply (or divide) the cutoff frequency
        during a coarse search.
        Defaults 1.1
    low_pass : func(cutoff, order) -> TransferFunction, optional
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
    oscillatory : boolean, optional
        Use the first mode of the oscillatory system to evaluate the phase
        margins to avoid having UGFs at steep phase slopes.
        The benefit of using this is to have a conservative phase margin
        estimate. The phase response of the first mode
        is the lower bound of the phase response.
        If False, use the plant itself to calculate phase margins.
        If the plant does not contain any complex poles, this option will be
        overridden to False.
        Defaults True.
    **kwargs
        Keyword arguments passed to ``low_pass``.

    Returns
    -------
    TransferFunction
        The low-pass filter.
    """
    if oscillatory:
        wn, q, k = kontrol.regulator.feedback.mode_decomposition(plant)
        if len(wn) == 0:
            oscillatory = False
    if low_pass is None:
        low_pass = kontrol.regulator.predefined.low_pass
    if "order" not in kwargs.keys():
        kwargs["order"] = 2
    if post_filter is None:
        post_filter = control.tf([1], [1])

    regulator *= post_filter
    oltf = plant * regulator
    _, pms, _, _, ugfs, _ = control.stability_margins(oltf, returnall=True)

    if ignore_ugf_above is None:
        ignore_ugf_above = max(ugfs)/2/np.pi * 10**decades_after_ugf
    if f_start is None:
        f_start = max(ugfs)/2/np.pi * 10**decades_after_ugf

    # Make initial guesses for the low-pass filter cutoff frequency.
    lower_edge_mask = (
        (abs(oltf(1j*(ugfs+ugfs*small_number)))
         < abs(oltf(1j*(ugfs-ugfs*small_number))))
    )  # Ignore UGFs with raising gain

    # Ignore UGFs higher than ignore_ugf_above.
    ignore_ugf_mask = ugfs/2/np.pi < ignore_ugf_above

    mask = lower_edge_mask * ignore_ugf_mask  #
    ugfs = ugfs[mask]
    if not oscillatory:
        pms = pms[mask]
    else:
        pms = []
        plant_one_mode = kontrol.regulator.feedback.mode_composition(
            wn[-1:], q[-1:], k[-1:])
        oltf_ = plant_one_mode * regulator
        # For each UGF, scale the OLTF one-mode plant such that the UGF matches
        # Then, find the phase margin using control.stability_margins.
        for ugf in ugfs:
            oltf_ *= 1/abs(oltf_(1j*ugf))  # Equalize the ugf
            _, pms_, _, _, ugfs_, _ = control.stability_margins(
                oltf_, returnall=True)
            for i, ugf_ in enumerate(ugfs_):
                if i == 0:
                    ugf_phase_eval = ugf_
                    index_phase_eval = i
                else:
                    if abs(ugf_-ugf) < abs(ugf_phase_eval-ugf):
                        ugf_phase_eval = ugf_
                        index_phase_eval = i
            pms.append(pms_[index_phase_eval])
        pms = np.array(pms)

    # Count phase margins that are already lower than
    # the specified phase margin and ignore them.
    n_pm_ignore = np.sum(pms < phase_margin)

    # Count number of phase margins
    n_pm = len(pms)

    if n_pm_ignore == n_pm:
        raise ValueError("All phase margins already below"
                         " specified phase margins."
                         " Can't implement low-pass filter.")
    if n_pm_ignore > 0:
        kontrol.logger.logger.warning(f"There are {n_pm_ignore} phase margins"
                                      " below the specified phase margin"
                                      " initially.")

    fc = f_start

    pm_was_lower = False
    pm_was_higher = False

    # Update 2022-01-17: Use the low-passed OLTF to evaluate UGF
    # but only use the first mode of the plant (if the plant is oscillatory)
    # to evaluate phase.

    # Start coarse searching
    while 1:
        oltf_lp = oltf * low_pass(fc, **kwargs)
        _, pms, _, _, ugfs, _ = control.stability_margins(
            oltf_lp, returnall=True)
        lower_edge_mask = ((abs(oltf_lp(1j*(ugfs+ugfs*small_number)))
                            < abs(oltf_lp(1j*(ugfs-ugfs*small_number)))))
        ignore_ugf_mask = ugfs/2/np.pi < ignore_ugf_above
        mask = lower_edge_mask * ignore_ugf_mask
        ugfs = ugfs[mask]
        if not oscillatory:
            pms = pms[mask]
        else:
            pms = []
            plant_one_mode = kontrol.regulator.feedback.mode_composition(
                wn[-1:], q[-1:], k[-1:])
            oltf_ = plant_one_mode * regulator * low_pass(fc, **kwargs)
            # For each UGF, scale the OLTF one-mode plant
            # such that the UGF matches.
            # Then, find the phase margin using control.stability_margins.
            for ugf in ugfs:
                oltf_ *= 1/abs(oltf_(1j*ugf))  # Equalize the ugf
                _, pms_, _, _, ugfs_, _ = control.stability_margins(
                    oltf_, returnall=True)
                for i, ugf_ in enumerate(ugfs_):
                    if i == 0:
                        ugf_phase_eval = ugf_
                        index_phase_eval = i
                    else:
                        if abs(ugf_-ugf) < abs(ugf_phase_eval-ugf):
                            ugf_phase_eval = ugf_
                            index_phase_eval = i
                pms.append(pms_[index_phase_eval])
            pms = np.array(pms)

        # Check number of phase margins and see if it changed.
        # If it changed,
        # recount the number of phase margins already lower than target.
        if len(pms) != n_pm:
            if n_pm_ignore > np.sum(pms < phase_margin):
                # In case the low-pass filter suppressed the problematic peak
                n_pm_ignore = np.sum(pms < phase_margin)
            n_pm = len(pms)

        # Find the minimum phase margin. (Don't count ignored ones.)
        pms_order = np.argsort(pms)
        min_pm_index = pms_order[n_pm_ignore]
        min_pm = pms[min_pm_index]
        if min_pm < phase_margin:
            f1 = fc
            pm_lower_bound = min_pm
            pm_was_lower = True
            fc *= f_step
        else:
            f2 = fc
            pm_upper_bound = min_pm
            pm_was_higher = True
            fc /= f_step

        # Phase margin crosses specification
        # memorize the two frequencies f1, f2 and break.
        if pm_was_lower and pm_was_higher:
            break

    # Runs bisection alogrithm using f1 and f2 as boundary.
    while 1:  # TODO Add maxiter
        fm = 10**((np.log10(f1) + np.log10(f2))/2)
        oltf_lp = oltf * low_pass(fm, **kwargs)
        _, pms, _, _, ugfs, _ = control.stability_margins(
            oltf_lp, returnall=True)
        lower_edge_mask = ((abs(oltf_lp(1j*(ugfs+ugfs*small_number)))
                           < abs(oltf_lp(1j*(ugfs-ugfs*small_number)))))
        ignore_ugf_mask = ugfs/2/np.pi < ignore_ugf_above
        mask = lower_edge_mask * ignore_ugf_mask
        ugfs = ugfs[mask]
        if not oscillatory:
            pms = pms[mask]
        else:
            pms = []
            plant_one_mode = kontrol.regulator.feedback.mode_composition(
                wn[-1:], q[-1:], k[-1:])
            oltf_ = plant_one_mode * regulator * low_pass(fm, **kwargs)

            # For each UGF, scale the OLTF one-mode plant
            # such that the UGF matches.
            # Then, find the phase margin using control.stability_margins.
            for ugf in ugfs:
                oltf_ *= 1/abs(oltf_(1j*ugf))  # Equalize the ugf
                _, pms_, _, _, ugfs_, _ = control.stability_margins(
                    oltf_, returnall=True)
                for i, ugf_ in enumerate(ugfs_):
                    if i == 0:
                        ugf_phase_eval = ugf_
                        index_phase_eval = i
                    else:
                        if abs(ugf_-ugf) < abs(ugf_phase_eval-ugf):
                            ugf_phase_eval = ugf_
                            index_phase_eval = i
                pms.append(pms_[index_phase_eval])
            #
            pms = np.array(pms)

        pms_order = np.argsort(pms)
        min_pm_index = pms_order[n_pm_ignore]
        min_pm = pms[min_pm_index]

        if (abs((min_pm - phase_margin)/phase_margin) <= mtol
                and min_pm > phase_margin):
            break
        if min_pm < phase_margin:
            f1 = fm
        else:
            f2 = fm
        if min_pm < pm_lower_bound or min_pm > pm_upper_bound:
            raise ValueError("Phase margin diverges during refinement.")

    return low_pass(fm, **kwargs)


def post_notch(
        plant, regulator=None, post_filter=None, target_gain=None,
        notch_peaks_above=None, phase_margin=45, notch=None, **kwargs):
    """Returns a list of notch filters that suppress resonance peaks.

    This functions finds the resonances peak of the plant/OLTF
    above certain frequencies and
    returns a list of notch filters that suppress
    these peaks to the target gains.

    Parameters
    ----------
    plant : TransferFunction
        The transfer function of the system that needs to be controlled.
    regulator : TransferFunction, optional
        The regulator.
        Defaults to None.
    post_filter : TransferFunction, optional
        Any post filters that will be applied on top of the regulator.
        Defaults None.
    target_gain : float, optional
        The target open-loop gain for the suppressed peak.
        To ensure a stable system, a value of less than 1 is recommended.
        If not specified, the notch will fully suppress the peak.
        Default None.
    phase_margin : float, optional
        The target phase margin.
        Defaults to 45.
    notch_peaks_above : float, optional
        Notch modes that has freqeuncies above ``notch_peaks_above``.
        If not specified, defaults to the highest unity gain frequency that
        is above ``phase_margin``
        Defaults to None.
    notch : func(frequency, q, depth) -> TransferFunction, optional
        The notch filter.
        If not specified, ``kontrol.Notch()`` will be used.
        Defaults to None.
    **kwargs
        Keyword arguments passed to notch().

    Returns
    -------
    list of TransferFunction
        A list of notch filters.

    Notes
    -----
    This operation does not guarantee stability.
    It only finds resonances peaking out of the unity gain above some
    unity gain frequency and make notch filters to suppress them to
    a target gain level lower than the unity gain.
    The stability of the notched OLTF is not checked whatsoever.
    """
    if notch is None:
        notch = kontrol.Notch
    if regulator is None:
        regulator = control.tf([1], [1])
    if post_filter is None:
        post_filter = control.tf([1], [1])

    oltf = regulator * plant * post_filter
    oltf = oltf.minreal()
    _, pms, _, _, ugfs, _ = control.stability_margins(oltf, returnall=True)
    # mask out acceptable ugfs
    ufg_mask = pms <= phase_margin
    # Set the maximum one (masked) to be the target ugf.
    if notch_peaks_above is None:
        notch_peaks_above = max(ugfs[ufg_mask]/2/np.pi)

    wn, q, k = kontrol.regulator.feedback.mode_decomposition(oltf)
    # All poles in oltf above target frequency should be notched.
    fn = wn/2/np.pi
    notch_mask = fn > notch_peaks_above
    fn = fn[notch_mask]  # Resonance frequencies ordered from high to low.
    q = q[notch_mask]  # Quality factors
    k = k[notch_mask]  # DC gains
    gain_peak = q*k  # magnitude at the resonance

    # Choose modes that have peak higher than the DC gain.
    gain_mask = abs(gain_peak) > abs(k)
    fn = fn[gain_mask]
    q = q[gain_mask]
    k = k[gain_mask]
    gain_peak = gain_peak[gain_mask]

    # Notch peaks to the target gain or to their DC gain.
    notch_depth = np.zeros_like(fn)
    notch_q = np.zeros_like(fn)
    for i in range(len(notch_depth)):
        if target_gain is None:
            # Defaults to notch the peaks to the DC gain.
            notch_depth[i] = gain_peak[i]/k[i]
            notch_q[i] = 2*q[i]/notch_depth[i]
        elif target_gain < k[i]:
            # If the target gain is lower than the DC gain
            # Set target gain to DC gain instead.
            notch_depth[i] = gain_peak[i]/k[i]
            notch_q[i] = 2*q[i]/notch_depth[i]
        else:
            notch_depth[i] = gain_peak[i]/target_gain
            notch_q[i] = 2*target_gain/(k[i])

    notch_list = []
    for frequency, q, depth in zip(fn, notch_q, notch_depth):
        notch_list += [notch(frequency, q, depth)]

    return notch_list
