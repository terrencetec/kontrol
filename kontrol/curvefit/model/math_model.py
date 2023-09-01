"""Basic mathematical models"""
import numpy as np
import scipy.special

from .model import Model


class StraightLine(Model):
    r"""Simply a straight line.

    Parameters
    ----------
    args : array, optional
        The model parameters structued as:
        [slope, y-intercept].
        Defaults to None.

    Attributes
    ----------
    slope : float
        The slope of the line.
    intercept : float
        The y-intercept of the line.

    Notes
    -----
    The straight line is defined as

    .. math::

       y(x; m, c) = mx + c\,,

    where :math:`m` is the slope and :math:`c` is the y-intercept.
    """
    def __init__(self, args=None):
        """Constructor

        Parameters
        ----------
        args : array, optional
            The model parameters structued as:
            [slope, y-intercept].
            Defaults to None.
        """
        super().__init__(args=args)
        if self.args is None:
            self.args = np.zeros(2)

    @property
    def slope(self):
        """The slope of the line"""
        return self.args[0]

    @slope.setter
    def slope(self, _slope):
        """slope.setter"""
        self.args[0] = _slope

    @property
    def intercept(self):
        """The y-intercept of the line"""
        return self.args[1]

    @intercept.setter
    def intercept(self, _intercept):
        """intercept.setter"""
        self.args[1] = _intercept

    def _x2y(self, x, **kwargs):
        """y = mx + c"""
        y = self.slope*x + self.intercept
        return y


class Erf(Model):
    r"""The error function erf(x)

    Parameters
    ----------
    args : array, optional
        The model parameters structured as
        [amplitude, slope, x0, y0].
        Defaults to None.

    Notes
    -----
    The function is defined as

    .. math::

       f(x; a, m, x_0, y_0) = a\,\mathrm{erf}(m(x-x_0)) + y_0\,,

    where :math:`\mathrm{erf}(x)` is the error function [1]_,
    :math:`a` is the peak to peak amplitude, :math:`m` is the
    slope at the inflection point, :math:`x_0` is the :math:`x` offset
    , and :math:`y_0` is the :math:`y` offset.

    References
    ----------
    .. [1]
        https://en.wikipedia.org/wiki/Error_function
    """
    def __init__(self, args=None):
        """Constructor

        Parameters
        ----------
        args : array, optional
            The model parameters structured as
            [amplitude, slope, x0, y0].
            Defaults to None.
        """
        super().__init__(args=args)
        if self.args is None:
            self.args = np.zeros(4)

    def _x2y(self, x):
        """The error function"""
        a = self.amplitude
        m = self.slope
        x0 = self.x_offset
        y0 = self.y_offset
        return a*scipy.special.erf(m*(x-x0)) + y0

    @property
    def amplitude(self):
        """Peak to Peak amplitude of the error function."""
        return self.args[0]

    @amplitude.setter
    def amplitude(self, _amplitude):
        """amplitude.setter"""
        self.args[0] = _amplitude

    @property
    def slope(self):
        """Slope at the inflection point."""
        return self.args[1]

    @slope.setter
    def slope(self, _slope):
        """slope.setter"""
        self.args[1] = _slope

    @property
    def x_offset(self):
        """x offset"""
        return self.args[2]

    @x_offset.setter
    def x_offset(self, _x_offset):
        """x_offset.setter"""
        self.args[2] = _x_offset

    @property
    def y_offset(self):
        """y offset"""
        return self.args[3]

    @y_offset.setter
    def y_offset(self, _y_offset):
        """y_offset.setter"""
        self.args[3] = _y_offset
