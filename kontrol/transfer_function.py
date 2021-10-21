"""Transfer function class.
Wrapper around control.TransferFunction
to provide custom functionality related to KAGRA.
"""
import control
import numpy as np

import kontrol.core.controlutils


class TransferFunction(control.TransferFunction):
    """Transfer function class

    Parameters
    ----------
    *args:
        Arguments passed to control.TransferFunction class.
    """
    def __init__(self, *args):
        """Initialize with a transfer function object

        Parameters
        ----------
        *args:
            Arguments passed to control.TransferFunction class.
        """
        super().__init__(*args)

    def lstrip(self, element, fc=None):
        """Remove zero or pole from the left.

        Parameters
        ----------
        element: str
            Element to be removed.
            Choose from ["any", "zero", "pole", "pair", "all"].
        fc: float or None, optional
            Cutoff frequency.
            If element is in ["any", "all"], remove any or all elements
            on the left of the cutoff.
            Defaults None.
        """
        # Work in progress
        pass

    def rstrip(self, element, fc=None):
        """Remove zero or pole from the right.

        Parameters
        ----------
        element: str
            Element to be removed.
            Choose from ["any", "zero", "pole", "pair", "all"].
        fc: float or None, optional
            Cutoff frequency.
            If element is in ["any", "all"], remove any or all elements
            on the left of the cutoff.
            Defaults None.
        """
        # Work in progress
        pass

    def stabilize(self):
        """Convert unstable zeros and poles to stable ones.
        """
        stable_tf = kontrol.core.controlutils.convert_unstable_tf(self)
        super().__init__(stable_tf)

    def foton(
            self, expression="zpk", root_location="s",
            itol=1e-25, epsilon=1e-25):
        """Foton expression of this transfer function
        
        Calls kontrol.core.foton.tf2foton and returns a foton expression
        of this transfer function

        Parameters
        ----------
        expression : str, optional
            Format of the foton expression.
            Choose from ["zpk", "rpoly"].
            Defaults to "zpk".
        root_location : str, optional
            Root location of the zeros and poles for expression=="zpk".
            Choose from ["s", "f", "n"].
            "s": roots in s-plane, i.e. zpk([...], [...], ...,  "s").
            "f": roots in frequency plane, i.e. zpk([...], [,,,], ..., "f").
            "n": roots in frequency plane but negated and gains are normalized,
            i.e. real parts are positive zpk([...], [...], ..., "n").
            Defaults to "s".
        itol : float, optional
            Treating complex roots as real roots if the ratio of
            the imaginary part and the real part is smaller than this tolerance
            Defaults to 1e-25.
        epsilon : float, optional
            Small number to add to denominator to prevent division error.
            Defaults to 1e-25.

        Returns
        -------
        foton_expression : str
            The foton expression in selected format.

        Note
        ----
        Only works for transfer functions with less than 20 orders.
        """
        ## TODO add MIMO support
        return kontrol.core.foton.tf2foton(
            tf=self, expression=expression, root_location=root_location,
            itol=itol, epsilon=epsilon)
