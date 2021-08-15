"""Transfer function models for transfer function fitting."""
import numpy as np

from .model import Model
import kontrol.core.math as math
import kontrol


class TransferFunctionModel(Model):
    r"""Transfer function model class defined by numerator and denominator

    Parameters
    ----------
    nzero : int
        Number of zeros.
    npole : int
        Number of poles.
    args : array or None, optional.
        The model parameters.
        Structured as follows:
        [b_n, b_n-1,..., b_1, b_0, a_m, a_m-1,..., a_1, a_0],
        where b and a are the coefficients of the numerator and denominator
        respectively, ordered from higher-order to lower-order.
        Defaults to None.

    Attributes
    ----------
    tf : kontrol.TransferFunction
        The last evaluted transfer function.

    Notes
    -----
    The transfer function model is defined as

    .. math::

       G(s, b_n, b_{n-1},..., b_1, b_0, a_m, a_{m-1},..., a_1, a_0)
       = \frac{\sum_{i=0}^{n} b_i s^i}{\sum_{j=0}^{m} a_j s^j}
    """
    def __init__(self, nzero, npole, args=None):
        """Constructor

        Parameters
        ----------
        nzero : int
            Number of zeros.
        npole : int
            Number of poles.
        args : array or None, optional.
            The model parameters.
            Structured as follows:
            [b_n, b_n-1,..., b_1, b_0, a_m, a_m-1,..., a_1, a_0],
            where b and a are the coefficients of the numerator and denominator
            respectively, ordered from higher-order to lower-order.
            Defaults to None.
        """
        super().__init__(args)
        self._nzero = None
        self._npole = None
        self.nzero = nzero
        self.npole = npole

    def _x2y(self, x, xunit="Hz"):
        """Transfer function frequency response.

        Parameters
        ----------
        x : array
            Independent variable in units specified by ``xunit``.
        xunit : str, optional.
            Unit of ``x``.
            Choose from ["Hz", "rad/s", "s"].
            Defaults to "Hz".

        Returns
        -------
        y : array
            Frequency response of the transfer function in complex values.
        """
        if len(self.num) + len(self.den) != self.nzero + self.npole + 2:
            raise ValueError("len(args) must be nzero+npole+2")
        num = self.num
        den = self.den
        s = self._x2s(x, xunit)
        num_poly = math.polyval(num, s)
        den_poly = math.polyval(den, s)
        y = num_poly/den_poly
        return y

    def _x2s(self, x, xunit):
        """Returns the complex variable s.

        Parameters
        ----------
        x : array
            Independent variable in units specified by ``xunit``.
        xunit : str,
            Unit of ``x``.
            Choose from ["Hz", "rad/s", "s"].

        Returns
        -------
        s : array
            The complex variable.
        """
        if xunit == "Hz":
            s = 1j*2*np.pi*x
        elif xunit == "rad/s":
            s = 1j*x
        elif xunit == "s":
            s = x
        else:
            raise ValueError("Invalid specification for xunit."
                             "Please choose xunit from 'Hz', 'rad/s', or 's'.")
        return s

    @property
    def nzero(self):
        """Number of zeros"""
        return self._nzero

    @nzero.setter
    def nzero(self, _nzero):
        """nzero.setter"""
        self._nzero = _nzero

    @property
    def npole(self):
        """Number of zeros"""
        return self._npole

    @npole.setter
    def npole(self, _npole):
        """npole.setter"""
        self._npole = _npole

    @property
    def num(self):
        """Numerator array"""
        return self.args[:self.nzero+1]

    @property
    def den(self):
        """Denominator array"""
        return self.args[self.nzero+1:]

    @property
    def tf(self):
        """The Transfer Function object."""
        return kontrol.TransferFunction(self.num, self.den)


class DampedOscillator(TransferFunctionModel):
    r"""Transfer function model for a damped oscillator.

    Parameters
    ----------
    args : array or None, optional.
        The model parameters with three numbers.
        Structured as follows:
        ``args = [k, fn, q]``,
        where ``k`` is the DC gain of the transfer function,
        ``fn`` is the resonance frequency in Hz, and ``q`` is the Q-factor.
        Defaults to None.

    Notes
    -----
    The model is definded as

    .. math::

       G(s; k, \omega_n, q) =
       k\frac{\omega_n^2}{s^2 + \frac{\omega_n}{q}s + \omega_n^2}

    where :math:`k` is the DC gain of the transfer function, :math:`\omega_n`
    is the resonance frequency of the oscillator, and :math:`q` is the
    Q-factor if the damped oscillator.
    """
    def __init__(self, args=None):
        """Constructor

        Parameters
        ----------
        args : array or None, optional.
            The model parameters with three numbers.
            Structured as follows:
            ``args = [k, fn, q]``,
            where ``k`` is the DC gain of the transfer function,
            ``fn`` is the resonance frequency in Hz, and ``q`` is the Q-factor.
            Defaults to None.
        """
        super().__init__(nzero=0, npole=2)
        self._args = None
        self.args = args

    @property
    def damped_oscillator_args(self):
        """The model parameters with three numbers [k, fn, q]"""
        return self._damped_oscillator_args

    @damped_oscillator_args.setter
    def damped_oscillator_args(self, _damped_oscillator_args):
        """damped_oscillator_args.setter"""
        self._damped_oscillator_args = _damped_oscillator_args

    # Overriding self.args in kontrol.curvefit.model.Model()
    @property
    def args(self):
        """Model parameters"""
        return self._args

    @args.setter
    def args(self, _args):
        """args.setter"""
        if _args is None:
            self._args = None
        else:
            if len(_args) != 3:
                raise ValueError("args must be in the format [k, wn, q].")
            self.damped_oscillator_args = _args
            k = self.k
            fn = self.fn
            q = self.q
            wn = 2*np.pi*fn
            args = np.array([k*wn**2, 1, wn/q, wn**2])  # Convert to num, den.
            self._args = args

    @property
    def k(self):
        """DC gain"""
        return self.damped_oscillator_args[0]

    @property
    def fn(self):
        """Resonance frequency"""
        return self.damped_oscillator_args[1]

    @property
    def q(self):
        """Q factor"""
        return self.damped_oscillator_args[2]


class CoupledOscillator(TransferFunctionModel):
    """"""
    def __init__(self):
        """"""
        pass
        # Taking a break.
