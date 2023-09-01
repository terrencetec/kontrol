"""Transfer function class.
Wrapper around control.TransferFunction
to provide custom functionality related to KAGRA.
"""
import os
import pickle

import control

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

    def clean(self, tol_order=5):
        """Remove numerator/denominator coefficients that are small outliers

        Parameters
        ----------
        tol_order : int, optional
            If the coefficient is ``tol_order`` order smaller than
            the rest of the coefficients, then this coefficient is an outlier.
            Defaults 5.
        """
        tf_cleaned = kontrol.core.controlutils.clean_tf3(
            self, tol_order=tol_order)
        super().__init__(tf_cleaned)

    def stabilize(self):
        """Convert unstable zeros and poles to stable ones.
        """
        stable_tf = kontrol.core.controlutils.convert_unstable_tf(self)
        super().__init__(stable_tf)

    def foton(
            self, expression="zpk", root_location="s", significant_figures=6,
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
        significant_figures : int, optional
            Number of significant figures to print out.
            Defaults to 6.
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
        """
        # TODO add MIMO support
        return kontrol.core.foton.tf2foton(
            tf=self, expression=expression, root_location=root_location,
            significant_figures=significant_figures,
            itol=itol, epsilon=epsilon)

    def save(self, path, overwrite=True):
        """Save the transfer function to a specified path.

        This functions extracts the numerator and denominator coefficients
        and puts it into a pandas DataFrame with keys {"num" and "den"}.
        Then it outputs to the specified path with a pickle format.

        Parameters
        ----------
        path : str
            The string of the path.
        overwrite : boolean, optional
            Overwrite if the file exists.
        """
        if not overwrite and os.path.exists(path):
            raise FileExistsError("File {} exists. "
                                  "Set overwrite option to True if you "
                                  "want to overwrite the file."
                                  "".format(path))
        with open(path, "wb") as f:
            pickle.dump(self, f)


def load_transfer_function(path):
    """Load a kontrol TransferFunction object from path.

    Parameters
    ----------
    path : str
        The path of the saved transfer function

    Returns
    -------
    TransferFunction
        The loaded TransferFunction object.
    """
    if not os.path.exists(path):
        raise FileNotFoundError("{} does not exist.".format(path))
    with open(path, "rb") as f:
        tf = pickle.load(f)
    return tf
