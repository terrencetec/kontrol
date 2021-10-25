"""Algorithmic designs for control regulators.

This sub-module contains functions for algorithmic design for
controllers, filters, and the like.
The functions has the following signature
func(plant: TransferFunction, **kwargs)->TransferFunction
For example, it takes a can take a transfer function and make a
feedback regulator that critically damps the system.
"""


def critical_damping(plant):
    r"""Derivative control for critically damping the dominant mode
    
    Parameters
    ----------
    plant : TransferFunction
        The transfer function representation of the system to be feedback
        controlled.
    method : str, optional
        The method to be used for setting the gain.
        Choose from ["optimized", "calculated"].

        * ``optimized``: the gain is optimized until the dominant complex
        pole pairs become two simple poles.
        * ``calculated``: the gain is set to :math:`\omega_n/K_{DC}`,
        where :math:`\omega_n` is the resonance frequency in rad/s
        of the dominant mode, and :math:`K_{DC}` is the DC gain
        of the plant.
        Both method assumes that the plant has at least one pair of complex
        poles.

    Returns
    -------
    kontrol.TransferFunction
        The derivative control regulator for critically damping the
        dominant mode.

    Notes
    -----
    The control regulator is simply

    .. math::

       K(s) = K_d s.

    The gain :math:`K_d` is optimized such that  
    """
    dcgain = plant.dcgain()
    pass

