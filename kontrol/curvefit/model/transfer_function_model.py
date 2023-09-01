"""Transfer function models for transfer function fitting."""
import control
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
    def __init__(self, nzero, npole, args=None, log_args=False):
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
        super().__init__(args=args, log_args=log_args)
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
        s = _x2s(x, xunit)
        num_poly = math.polyval(num, s)
        den_poly = math.polyval(den, s)
        y = num_poly/den_poly
        return y

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
        # if self.log_args:
        #     num = 10**self.num
        #     den = 10**self.den
        # else:
        num = self.num
        den = self.den
        return kontrol.TransferFunction(num, den)


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
                raise ValueError("args must be in the format [k, fn, q].")
            self.damped_oscillator_args = _args
            k = self.gain
            fn = self.fn
            q = self.q
            wn = 2*np.pi*fn
            args = np.array([k*wn**2, 1, wn/q, wn**2])  # Convert to num, den.
            self._args = args

    @property
    def gain(self):
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


class SimpleZPK(Model):
    r"""ZPK model with simple poles and zeros.

    Parameters
    ----------
    nzero : int
        Number of simple zeros.
    npole : int
        Number of simple poles.
    args : array, optional
         The model parameters defined as
         ``args = [z1, z2,..., p1, p2,..., k]``
         where ``z`` are the locations of the zeros in Hz,
         ``p`` are the locations of the pole in Hz, and
         ``k`` is the static gain,
    log_args : boolean, optional
        If true,
        model parameters passed to the model are assumed to be passed
        through a log10() function.
        So, when the real parameters will be assumed to be
        10**args instead.
        Defaults to False.

    Attributes
    ----------
    zero : array
        List of zeros.
    pole : array
        List of poles.
    gain : float
        Static gain.
    tf : kontrol.TranserFunction
        The transfer function representation of this ZPK model

    Notes
    -----
    The simple ZPK model is defined as

    .. math::

       G(s; z_1, z_2,..., p_1, p_2, ..., k)
       = k\frac{\prod_i(\frac{s}{2\pi z_i}+1)}{\prod_j(\frac{s}{2\pi p_j}+1)}
    """
    def __init__(self, nzero, npole, args=None, log_args=False):
        r"""Constructor.

        Parameters
        ----------
        nzero : int
            Number of simple zeros.
        npole : int
            Number of simple poles.
        args : array, optional
             The model parameters defined as
             ``args = [z1, z2,..., p1, p2,..., k]``
             where ``z`` are the locations of the zeros in Hz,
             ``p`` are the locations of the pole in Hz, and
             ``k`` is the static gain,
        log_args : boolean, optional
            If true,
            model parameters passed to the model are assumed to be passed
            through a log10() function.
            So, when the real parameters will be assumed to be
            10**args instead.
            Defaults to False.
        """
        self._nzero = None
        self._npole = None
        self.nzero = nzero
        self.npole = npole
        super().__init__(args=args, log_args=log_args)

    def _x2y(self, x, xunit="Hz"):
        """ZPK model frequency response."""
        s = _x2s(x, xunit)
        tf = np.ones_like(s) * self.gain
        for i in range(len(self.zero)):
            tf *= s/(2*np.pi*self.zero[i]) + 1
        for i in range(len(self.pole)):
            tf /= s/(2*np.pi*self.pole[i]) + 1
        return tf

    @property
    def nzero(self):
        """Number of simple zeros"""
        return self._nzero

    @nzero.setter
    def nzero(self, _nzero):
        """nzero.setter"""
        self._nzero = _nzero

    @property
    def npole(self):
        """Number of complex pole pairs"""
        return self._npole

    @npole.setter
    def npole(self, _npole):
        """npole.setter"""
        self._npole = _npole

    @property
    def args(self):
        """Model parameters in ZPK [z1, z2,..., p1, p2,..., k] format"""
        return self._args

    @args.setter
    def args(self, _args):
        """args.setter"""
        if _args is None:
            self._args = None
        elif len(_args) != self.nzero + self.npole + 1:
            raise ValueError("Length of argument must match nzero and npole.")
        else:
            if self.log_args:
                _args = 10**_args
            self._args = _args

    # TODO Maybe I should consider setter for zero, pole and gain.
    # These can be used to change the args as well but could be tedious.
    @property
    def zero(self):
        """List of zeros"""
        return self.args[:self.nzero]

    @property
    def pole(self):
        """List of poles"""
        return self.args[self.nzero:-1]

    @property
    def gain(self):
        """Static gain"""
        return self.args[-1]

    @property
    def tf(self):
        """Returns a TransferFunction object of this ZPK model"""
        s = control.tf("s")
        tf = control.tf([self.gain], [1])
        for i in range(len(self.zero)):
            tf *= s/(2*np.pi*self.zero[i]) + 1
        for i in range(len(self.pole)):
            tf /= s/(2*np.pi*self.pole[i]) + 1
        return kontrol.TransferFunction(tf)


class ComplexZPK(Model):
    r"""ZPK model with complex poles and zeros.

    Parameters
    ----------
    nzero_pairs : int
        Number of complex zero pairs.
    npole_pairs : int
        Number of complex pole pairs.
    args : array, optional
         The model parameters defined as
         ``args = [f1, q1, f2, q2,..., fi, qi,..., fn, qn, k]``,
         where ``f`` are resonance frequencies of the complex
         zero/pole pairs, ``q`` are the quality factors, and
         ``k`` is the static gain, ``i`` is the number of complex zero
         pairs, and ``n-i`` is the number of of complex pole pairs.
    log_args : boolean, optional
        If true,
        model parameters passed to the model are assumed to be passed
        through a log10() function.
        So, when the real parameters will be assumed to be
        10**args instead.
        Defaults to False.

    Attributes
    ----------
    fn_zero : array
        List of resonance frequencies of the complex zeros.
    fn_pole : array
        List of resonance frequencies of the complex poles.
    q_zero : array
        List of Q-factors of the complex zeros.
    q_pole : array
        List of Q-factors of the complex poles.

    Notes
    -----
    The complex ZPK model is defined by:

    .. math::

       G(s; f_i, q_i,k)
       =k\frac{\prod_i(\frac{s^2}{(2\pi f_i)^2} + \frac{1}{2\pi f_i q_i}s + 1)}
       {\prod_j(\frac{s^2}{(2\pi f_j)^2} + \frac{1}{2\pi f_j q_j}s + 1)}

    """
    def __init__(
            self, nzero_pairs, npole_pairs, args=None, log_args=False):
        r"""Constructor.

        Parameters
        ----------
        nzero_pairs : int
            Number of complex zero pairs.
        npole_pairs : int
            Number of complex pole pairs.
        args : array, optional
             The model parameters defined as
             ``args = [f1, q1, f2, q2,..., fi, qi,..., fn, qn, k]``,
             where ``f`` are resonance frequencies of the complex
             zero/pole pairs, ``q`` are the quality factors, and
             ``k`` is the static gain, ``i`` is the number of complex zero
             pairs, and ``n-i`` is the number of of complex pole pairs.
        log_args : boolean, optional
            If true,
            model parameters passed to the model are assumed to be passed
            through a log10() function.
            So, when the real parameters will be assumed to be
            10**args instead.
            Defaults to False.

        Example
        -------
        with ``nzero_pairs = 1``, ``npole_pairs = 2``,
        args = [1, 2, 3, 4, 5, 6, 7] refers to a transfer function

        .. math::

           G(s) = 7\frac{\frac{1}{(1\times 2\pi)^2}s^2
           + \frac{1}{2\times 1 \ times 2\pi}s + 1}
           {\left(\frac{1}{(3\times 2\pi)^2}s^2
           + \frac{1}{4\times 3\times 2\pi}s + 1\right)
           \left(\frac{1}{(3\times 2\pi)^2}s^2
           + \frac{1}{4\times 3\times 2\pi}s + 1\right)}
        """
        self._nzero_pairs = None
        self._npole_pairs = None
        self._fn_zero = None
        self._fn_pole = None
        self._q_zero = None
        self._q_pole = None
        self._gain = None
        self.nzero_pairs = nzero_pairs
        self.npole_pairs = npole_pairs  # self.npole_pairs is not used.
        super().__init__(args=args, log_args=log_args)

    def _x2y(self, x, xunit="Hz"):
        """ZPK model (complex) frequency response."""
        s = _x2s(x, xunit)
        fn_zero = self.fn_zero
        q_zero = self.q_zero
        fn_pole = self.fn_pole
        q_pole = self.q_pole
        num = np.ones_like(s) * self.gain
        den = np.ones_like(s)
        for i in range(len(fn_zero)):
            num *= (1 / (2*np.pi*fn_zero[i])**2 * s**2
                    + 1 / (2*np.pi*fn_zero[i]*q_zero[i]) * s
                    + 1)
        for i in range(len(fn_pole)):
            den *= (1 / (2*np.pi*fn_pole[i])**2 * s**2
                    + 1 / (2*np.pi*fn_pole[i]*q_pole[i]) * s
                    + 1)
        return num/den

    @property
    def nzero_pairs(self):
        """Number of complex zero pairs"""
        return self._nzero_pairs

    @nzero_pairs.setter
    def nzero_pairs(self, _nzero_pairs):
        """nzero_pairs.setter"""
        self._nzero_pairs = _nzero_pairs

    @property
    def npole_pairs(self):
        """Number of complex pole pairs"""
        return self._npole_pairs

    @npole_pairs.setter
    def npole_pairs(self, _npole_pairs):
        """npole_pairs.setter"""
        self._npole_pairs = _npole_pairs

    @property
    def args(self):
        """Model parameters in ZPK [f1, q1, f2, q2,..., fn, qn, k] format"""
        return self._args

    @args.setter
    def args(self, _args):
        """args.setter"""
        if _args is None:
            self._args = None
        elif np.mod(len(_args), 2) != 1:
            raise ValueError("Length of argument must be odd number "
                             "and in the format "
                             "[f1, q1, f2, q2,..., fn, qn, k]")
        elif len(_args) != self.nzero_pairs*2 + self.npole_pairs*2 + 1:
            raise ValueError("Length of argument must match the specfied "
                             "nzero_pairs and npole_pairs.")
        else:
            if self.log_args:
                _args = 10**_args
            self._args = _args

    @property
    def fn_zero(self):
        """List of resonance frequencies of complex zeros."""
        return self.args[:int(self.nzero_pairs*2):2]

    @property
    def fn_pole(self):
        """List of resonance frequencies of complex poles."""
        return self.args[int(self.nzero_pairs*2):-1:2]

    @property
    def q_zero(self):
        """List of quality factors of the complex zeros"""
        return self.args[1:int(self.nzero_pairs*2):2]

    @property
    def q_pole(self):
        """List of quality factors of the complex poles"""
        return self.args[int(self.nzero_pairs*2)+1:-1:2]

    @property
    def gain(self):
        """Static gain."""
        return self.args[-1]

    @property
    def tf(self):
        """Returns a TransferFunction object of this ZPK model"""
        s = control.tf("s")
        fn_zero = self.fn_zero
        q_zero = self.q_zero
        fn_pole = self.fn_pole
        q_pole = self.q_pole
        k = self.gain
        num = control.tf([k], [1])
        den = control.tf([1], [1])
        for i in range(len(fn_zero)):
            num *= (1 / (2*np.pi*fn_zero[i])**2 * s**2
                    + 1 / (2*np.pi*fn_zero[i]*q_zero[i]) * s
                    + 1)
        for i in range(len(fn_pole)):
            den *= (1 / (2*np.pi*fn_pole[i])**2 * s**2
                    + 1 / (2*np.pi*fn_pole[i]*q_pole[i]) * s
                    + 1)
        return kontrol.TransferFunction(num/den)


# TODO add support for a generic ZPK model

def _x2s(x, xunit):
    """Converts the independent variable to the complex variable s.

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
