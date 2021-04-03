"""Filter synthesis functions.
"""
import control

import kontrol.core.controlutils


def h2complementary(n1, n2):
    """H2 optimal complementary filter synthesis

    Parameters
    ----------
    n1: control.xferfcn.TransferFunction
        The transfer function representing the noise content of a
        particular sensor to be fused.
    n2: control.xferfcn.TransferFunction
        The trasnfer function representing the noise content of another
        sensor to be fused.

    Returns
    -------
    h1: control.xferfcn.TransferFunction
        The complementary filter filtering n1.
    h2: control.xferfcn.TransferFunction
        The complementary filter filtering n2.

    Notes
    -----
    This function ultilizes control.robust.h2syn which depends on the slycot
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
        https://tdehaeze.github.io/dehaeze20_optim_robus_compl_filte/matlab/index.html
    """
    p = [[control.tf([0],[1]), n2, control.tf([1],[1])],
         [n1, -n2, control.tf([0],[1])]]
#     p = [[n1, -n1],
#          [tf([0],[1]), n2],
#          [tf([1],[1]), tf([0],[1])]]
    p = kontrol.core.controlutils.tfmatrix2tf(p)
    h1 = control.tf(control.h2syn(control.ss(p), 1, 1))
    h2 = 1 - h1
    return h1, h2


def hinfcomplementary(n1, n2):
    """H-infinity optimal complementary filter synthesis

    Parameters
    ----------
    n1: control.xferfcn.TransferFunction
        The transfer function representing the noise content of a
        particular sensor to be fused.
    n2: control.xferfcn.TransferFunction
        The trasnfer function representing the noise content of another
        sensor to be fused.

    Returns
    -------
    h1: control.xferfcn.TransferFunction
        The complementary filter filtering n1.
    h2: control.xferfcn.TransferFunction
        The complementary filter filtering n2.

    Notes
    -----
    This function ultilizes control.robust.hinfsyn which depends on the slycot
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
        https://tdehaeze.github.io/dehaeze20_optim_robus_compl_filte/matlab/index.html
    """
    p = [[control.tf([0],[1]), n2, control.tf([1],[1])],
         [n1, -n2, control.tf([0],[1])]]
#     p = [[n1, -n1],
#          [tf([0],[1]), n2],
#          [tf([1],[1]), tf([0],[1])]]
    p = kontrol.core.controlutils.tfmatrix2tf(p)
    K, _, _, _ = control.hinfsyn(control.ss(p), 1, 1)
    h1 = control.tf(K)
    h2 = 1 - h1
    return h1, h2
