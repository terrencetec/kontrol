"""Filter synthesis functions.
"""
import control

import kontrol.core.controlutils


def generalized_plant(noise1, noise2, weight1, weight2):
    """Return the generalized plant of a 2 complementary filter system

    Parameters
    ----------
    noise1 : TransferFunction
        Sensor noise 1 transfer function model.
        A transfer function that has magnitude response matching the
        amplitude spectral density of noise 1.
    noise2 : TransferFunction
        Sensor noise 2 transfer function model.
        A transfer function that has magnitude response matching the
        amplitude spectral density of noise 2.
    weight1 : TransferFunction
        Weighting function 1.
        Frequency dependent specification for noise 1.
    weight2 : TransferFunction
        Weighting function 2.
        Frequency dependent specification for noise 2.

    Returns
    -------
    control.xferfcn.TransferFunction
        The plant.
    """
    zero = control.tf([0], [1])
    one = control.tf([1], [1])
    if weight1 is None:
        weight1 = one
    if weight2 is None:
        weight2 = one

    p = [[zero, weight2*noise2, one],
         [weight1*noise1, -weight2*noise2, zero]]
    # Tall matrix version here, not used.
#     p = [[noise1, -noise1],
#          [tf([0],[1]), noise2],
#          [tf([1],[1]), tf([0],[1])]]
    p = kontrol.core.controlutils.tfmatrix2tf(p)
    return p


def h2complementary(noise1, noise2, weight1=None, weight2=None):
    """H2 optimal complementary filter synthesis

    Parameters
    ----------
    noise1 : TransferFunction
        Sensor noise 1 transfer function model.
        A transfer function that has magnitude response matching the
        amplitude spectral density of noise 1.
    noise2 : TransferFunction
        Sensor noise 2 transfer function model.
        A transfer function that has magnitude response matching the
        amplitude spectral density of noise 2.
    weight1 : TransferFunction, optional
        Weighting function 1.
        Frequency dependent specification for noise 1.
        Defaults None.
    weight2 : TransferFunction, optional
        Weighting function 2.
        Frequency dependent specification for noise 2.

    Returns
    -------
    filter1 : TransferFunction
        The complementary filter filtering noise1.
    filter2 : TransferFunction
        The complementary filter filtering noise2.

    Notes
    -----
    This function ultilizes control.robust.h2syn() which depends on the slycot
    module. If you are using under a conda virtual environment, the slycot
    module can be installed easily from conda-forge. Using pip to install
    slycot is a bit more involved (I have yet to suceed installing slycot in
    my Windows machine). Please refer to the python-control package for further
    instructions.

    It is possible that h2syn yields no solution for some tricky noise profiles
    . Try adjusting the noise profiles at some irrelevant frequencies.

    Thomas Dehaeze [1]_ had the idea first so credits goes to him. (Properly
    cite when the paper is published.)

    References
    ----------
    .. [1]
        Dehaeze, T.
        https://tdehaeze.github.io/dehaeze20_optim_robus_compl_filte/matlab/\
index.html
    .. [2]
        T. T. L. Tsang, T. G. F. Li, T. Dehaeze, C. Collette.
        Optimal Sensor Fusion Method for Active Vibration Isolation Systems in
        Ground-Based Gravitational-Wave Detectors.
        https://arxiv.org/pdf/2111.14355.pdf
    """
    p = generalized_plant(noise1, noise2, weight1, weight2)
    p = control.ss(p)
    filter1 = control.h2syn(p, 1, 1)
    filter1 = control.tf(filter1)
    filter2 = 1 - filter1
    return filter1, filter2


def hinfcomplementary(noise1, noise2, weight1=None, weight2=None):
    """H-infinity optimal complementary filter synthesis

    Parameters
    ----------
    noise1 : TransferFunction
        Sensor noise 1 transfer function model.
        A transfer function that has magnitude response matching the
        amplitude spectral density of noise 1.
    noise2 : TransferFunction
        Sensor noise 2 transfer function model.
        A transfer function that has magnitude response matching the
        amplitude spectral density of noise 2.
    weight1 : TransferFunction, optional
        Weighting function 1.
        Frequency dependent specification for noise 1.
        Defaults None.
    weight2 : TransferFunction, optional
        Weighting function 2.
        Frequency dependent specification for noise 2.

    Returns
    -------
    filter1 : TransferFunction
        The complementary filter filtering noise1.
    filter2 : TransferFunction
        The complementary filter filtering noise2.

    Notes
    -----
    This function ultilizes control.robust.hinfsyn() which depends on the
    slycot module. If you are using under a conda virtual environment,
    the slycot module can be installed easily from conda-forge.
    Using pip to install slycot is a bit more involved
    (I have yet to suceed installing slycot in
    my Windows machine).
    Please refer to the python-control package for further instructions.

    Thomas Dehaeze [1]_ had the idea first so credits goes to him. (Properly
    cite when the paper is published.)

    References
    ----------
    .. [1]
        Dehaeze, T.
        https://tdehaeze.github.io/dehaeze20_optim_robus_compl_filte/matlab/\
index.html
    .. [2]
        T. T. L. Tsang, T. G. F. Li, T. Dehaeze, C. Collette.
        Optimal Sensor Fusion Method for Active Vibration Isolation Systems in
        Ground-Based Gravitational-Wave Detectors.
        https://arxiv.org/pdf/2111.14355.pdf
    """
    p = generalized_plant(noise1, noise2, weight1, weight2)
    p = control.ss(p)
    filter1, _, gamma, _ = control.hinfsyn(p, 1, 1)
    # print(gamma)
    filter1 = control.tf(filter1)
    filter2 = 1 - filter1
    return filter1, filter2
