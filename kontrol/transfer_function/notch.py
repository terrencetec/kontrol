"""Foton defined Notch filter.
"""
import kontrol.core.foton
import kontrol.regulator.predefined

from .transfer_function import TransferFunction


class Notch(TransferFunction):
    r"""Notch Filter Object

    Parameters
    ----------
    frequency : float
        The notch frequency (Hz).
    q : float
        The quality factor.
    depth : float, optional
        The depth of the notch filter (magnitude).
        If not specified, ``depth_db`` will be used.
        Defaults None.
    depth_db : float, optional
        The depth of the notch filter (decibel).
        If not specified, ``depth`` will be used instead.
        Defaults None.

    Attritubes
    ----------
    frequency : float
        The notch frequency (Hz).
    q : float
        The quality factor.
    depth : float
        The depth of the notch filter (magnitude).

    Notes
    -----
    The notch filter is defined by Foton, as

    .. math::

       N(s) = \frac{s^2 + (2\pi f_n)/(dQ/2)s + (2\pi f_n)^2}
       {s^2 + (2\pi f_n)/(Q/2)s + (2\pi f_n)^2}\,,

    where :math:`f_n` is the notch frequency, :math:`q` is the quality factor
    , and :math:`d` is the depth.
    """
    def __init__(self, frequency, q, depth=None, depth_db=None):
        """Constructor

        Parameters
        ----------
        frequency : float
            The notch frequency (Hz).
        q : float
            The quality factor.
        depth : float, optional
            The depth of the notch filter (magnitude).
            If not specified, ``depth_db`` will be used.
            Defaults None.
        depth_db : float, optional
            The depth of the notch filter (decibel).
            If not specified, ``depth`` will be used instead.
            Defaults None.
        """
        if depth is None and depth_db is None:
            raise ValueError("Either depth or depth_db must be specified")
        if depth is None:
            depth = 10**(depth_db/20)
        _notch = kontrol.regulator.predefined.notch(
            frequency, q, depth, depth_db)
        super().__init__(_notch)
        self._frequency = None
        self._q = None
        self._depth = None
        self.frequency = frequency
        self.q = q
        self.depth = depth
        self.depth_db = depth_db

    @property
    def frequency(self):
        """The notch frequency (Hz)."""
        return self._frequency

    @frequency.setter
    def frequency(self, _frequency):
        """frequency.setter"""
        if _frequency < 0:
            raise ValueError("Frequency must be greater than 0 Hz")
        self._frequency = _frequency
        self._update_tf()

    @property
    def q(self):
        """The quality factor"""
        return self._q

    @q.setter
    def q(self, _q):
        """q.setter"""
        if _q < 0.5:
            raise ValueError("Q factor must be greater than 0.5")
        self._q = _q
        self._update_tf()

    @property
    def depth(self):
        """The depth of the notch filter (magnitude)."""
        return self._depth

    @depth.setter
    def depth(self, _depth):
        """depth.setter"""
        if _depth < 0:
            raise ValueError("Depth must be greater than zero")
        self._depth = _depth
        self._update_tf()

    def _update_tf(self):
        """Update the TransferFunction object"""
        if (self.frequency is not None
                and self.q is not None
                and self.depth is not None):
            frequency = self.frequency
            q = self.q
            depth = self.depth
            _notch = kontrol.regulator.predefined.notch(frequency, q, depth)
            super().__init__(_notch)

    def foton(self):
        """Foton expression of this notch filter."""
        return kontrol.core.foton.notch(self.frequency, self.q, self.depth)
