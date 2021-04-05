"""Complementary filter class for sythesis
"""
import control
import numpy as np


import kontrol.core.math
import kontrol.core.controlutils
import kontrol.transfer_function
import kontrol.complementary_filter.synthesis


class ComplementaryFilter(kontrol.transfer_function.TransferFunction):
    """A set of complementary filters.

    This instances will return a TransferFunction object that
    has two inputs and one output, i.e. 2 transfer functions, which
    represents the two complementary filters.

    To use the synthesis methods, it's best to declare this class
    with two transfer functions that model the noises to be filtered.

    Attributes
    ----------
    f: array or None
        The frequency axis (Hz) of the noises to be filtered.
    omega: array or None
        The frequency axis (rad/s) of the noises to be filtered.
    noise1: array or None
        Noise amplitude spectral density of the first input.
    noise2: array or None
        Noise amplitude spectral density of the second input.
    tf_noise1: TransferFunction or None
        A transfer function that models the amplitude spectral density of
        the first input.
    tf_noise2: TransferFunction or None
        A transfer function that models the amplitude spectral density of
        the second input.
    filter1: TransferFunction or None
        The first complementary filter.
    filter2: TransferFunction or None
        The second complementary filter.

    Methods
    -------
    h2synthesis(w1=None, w2=None)
        Complementary filter synthesis that minimizes the
        :math:`\mathcal{H}_2`-norm
        of the super sensor noise. The noise must be specified
        before using this method.
    hinfsynthesis(w1=None, w2=None)
        Complementary filter synthesis that minimizes the
        :math:`\mathcal{H}_\infty`-norm
        of the super sensor noise. The noise must be specified
        before using this method.
    """
    def __init__(self, f=None, noise1=None, noise2=None,
                 filter1=None, filter2=None, unit="f"):
        """Constructor

        Parameters
        ----------
        f: array or None, optional
            The frequency axis of the noises to be filtered.
            Default None.
        noise1: array, TransferFunction, FrequencySeries or None, optional
            Noise amplitude spectral density of the first input.
            Default None.
        noise2: array, TransferFunction, FrequencySeries or None, optional
            Noise amplitude spectral density of the second input.
            Default None.
        filter1: TransferFunction or None, optional
            The first complementary filter.
            Default None.
        filter2: TransferFunction or None, optional
            The second complementary filter. This should complement
            filter 1.
            Default None.
        unit: str, optional
            The unit of the frequency axis.
            Choose from ["f", "s", "Hz", "omega"].
            Default "f".

        Raises
        ------
        ValueError
            Filter1 doesn't complement filter2.
        """
        if f is not None:
            f = np.array(f)
            if unit in ["f", "Hz"]:
                self.f = f
                self.omega = 2*np.pi*f
            else:
                self.f = f/2/np.pi
                self.omega = f
        else:
            self.f = None
            self.omega = None

        if isinstance(noise1, control.xferfcn.TransferFunction):
            self.tf_noise1 = noise1
            if self.omega is not None:
                self.noise1 = abs(noise1(1j*self.omega))
            else:
                self.noise1 = noise1
        else:
            self.tf_noise1 = None
            self.noise1 = noise1

        if isinstance(noise2, control.xferfcn.TransferFunction):
            self.tf_noise2 = noise2
            if self.omega is not None:
                self.noise2 = abs(noise2(1j*self.omega))
            else:
                self.noise2 = noise2
        else:
            self.tf_noise2 = None
            self.noise2 = noise2

        self.filter1 = filter1
        self.filter2 = filter2
        if filter1 is not None and filter2 is not None:
            tf_1 = control.tf([1], [1])
            tf_check = filter1+filter2
            if not kontrol.core.controlutils.check_tf_equal(tf_1, tf_check):
                raise ValueError("filter1 is not complementary to filter2.")
        elif filter1 is not None and filter2 is None:
            filter2 = control.tf([1], [1]) - filter1
            self.filter2 = filter2
        elif filter1 is None and filter2 is not None:
            filter1 = control.tf([1], [1]) - filter2
            self.filter1 = filter1

        if filter1 is not None and filter2 is not None:
            tf_complementary_matrix = [[filter1], [filter2]]
            tf_complementary = kontrol.core.controlutils.tfmatrix2tf(
                tf_complementary_matrix)
            super().__init__(tf_complementary)

    def h2synthesis(self, w1=None, w2=None):
        """Synthesize complementary filters using H2 synthesis.

        Parameters
        ----------
        w1: TransferFunction or None, optional
            Addition weighting function on filter 1.
            Default None.
        w2: TransferFunction or None, optional
            Additional weighting function on filter 2.
            Default None.
        """
        func = kontrol.complementary_filter.synthesis.h2complementary
        self._synthesis(func=func, w1=w1, w2=w2)

    def hinfsynthesis(self, w1=None, w2=None):
        """Synthesize complementary filters using H-inifinity synthesis.

        Parameters
        ----------
        w1: TransferFunction or None, optional
            Addition weighting function on filter 1.
            Default None.
        w2: TransferFunction or None, optional
            Additional weighting function on filter 2.
            Default None.
        """
        func = kontrol.complementary_filter.synthesis.hinfcomplementary
        self._synthesis(func=func, w1=w1, w2=w2)

    def _synthesis(self, func, w1=None, w2=None):
        """Generic complementary filter synthesis function.

        Synthesize the complementary filter using the function and
        re-initialize kontrol.transfer_function.TransferFunction
        with a 2-input-1-output control.xferfcn.TransferFunction.

        Parameters
        ----------
        func: function
            The function that takes two noise models and returns
            a pair of complementary filters.
            It should have a siguration of
            func(TransferFunction, TransferFunction) ->
            (TransferFunction, TransferFunction).
        w1: TransferFunction or None, optional
            Addition weighting function on filter 1.
            Default None.
        w2: TransferFunction or None, optional
            Additional weighting function on filter 2.
            Default None.
        """
        if w1 is None:
            w1 = control.tf([1], [1])
        if w2 is None:
            w2 = control.tf([1], [1])
        n1 = self.tf_noise1/self.tf_noise2*w1
        n2 = self.tf_noise2/self.tf_noise1*w2
        h1, h2 = func(n1, n2)
        self.filter1 = h1
        self.filter2 = h2

    @property
    def noise1(self):
        """Amplitude spectral density of sensor noise 1.
        """
        ## Calculate here.
        if self._noise1 is not None:
            return self._noise1
        elif self.tf_noise1 is not None:
            if self.omega is not None:
                return abs(self.tf_noise1(1j*self.omega))
            else:
                raise ValueError("noise1 is not specfied."
                                 "tf_nosie1 is specified but f/omega is not.")
                return None
        else:
            raise ValueError("noise1 is not specfied."
                             "tf_nosie1 is not specified")
            return None

    @noise1.setter
    def noise1(self, noise):
        """noise1 setter

        Parameters
        ----------
        noise1: array, FrequencySeries or TransferFunction
            Noise amplitude spectral density of the first input.
        """
        if isinstance(noise, control.xferfcn.TransferFunction):
            self.tf_noise1 = noise
            if self.omega is not None:
                self._noise1 = abs(self.tf_noise1(1j*self.omega))
            else:
                self._noise1 = None
        else:
            self._noise1 = noise

    @property
    def noise2(self):
        """Amplitude spectral density of sensor noise 2.
        """
        if self._noise2 is not None:
            return self._noise2
        elif self.tf_noise2 is not None:
            if self.omega is not None:
                return abs(self.tf_noise2(1j*self.omega))
            else:
                raise ValueError("noise2 is not specfied."
                                 "tf_nosie2 is specified but f/omega is not.")
                return None
        else:
            raise ValueError("noise2 is not specfied."
                             "tf_nosie2 is not specified")
            return None

    @noise2.setter
    def noise2(self, noise):
        """noise2 setter

        Parameters
        ----------
        noise1: array, FrequencySeries or TransferFunction
            Noise amplitude spectral density of the first input.
        """
        if isinstance(noise, control.xferfcn.TransferFunction):
            self.tf_noise2 = noise
            if self.omega is not None:
                self._noise2 = abs(self.tf_noise2(1j*self.omega))
            else:
                self._noise2 = None
        else:
            self._noise2 = noise

    @property
    def noise_super(self):
        """Super sensor noise amplitude spectral density
        """
        if self.f is None:
            raise ValueError("self.f is not specified.")
        elif self.filter1 is None:
            raise ValueError("self.filter1 is not specified.")
        elif self.filter2 is None:
            raise ValueError("self.filter2 is not specified.")
        elif self.noise1 is None:
            raise ValueError("self.noise1 is not specified.")
        elif self.noise2 is None:
            raise ValueError("self.noise2 is not specified.")
        noise1_filtered = abs(self.filter1(1j*self.omega)) * self.noise1
        noise2_filtered = abs(self.filter2(1j*self.omega)) * self.noise2
        return kontrol.core.math.quad_sum(noise1_filtered, noise2_filtered)

    @property
    def filter1(self):
        """First complementary filter.
        """
        return self._filter1

    @filter1.setter
    def filter1(self, tf):
        """filter1 setter.

        Parameters
        ----------
        tf: TransferFunction
        """
        self._filter1 = tf
        if self.filter1 is not None and self.filter2 is not None:
            tf_complementary_matrix = [[self.filter1], [self.filter2]]
            tf_complementary = kontrol.core.controlutils.tfmatrix2tf(
                tf_complementary_matrix)
            super().__init__(tf_complementary)

    @property
    def filter2(self):
        """Second complementary filter.
        """
        return self._filter2

    @filter2.setter
    def filter2(self, tf):
        """filter2 setter.

        Parameters
        ----------
        tf: TransferFunction
        """
        self._filter2 = tf
        if self.filter1 is not None and self.filter2 is not None:
            tf_complementary_matrix = [[self.filter1], [self.filter2]]
            tf_complementary = kontrol.core.controlutils.tfmatrix2tf(
                tf_complementary_matrix)
            super().__init__(tf_complementary)

    @property
    def f(self):
        """The frequency axis in Hz.
        """
        if self._f is not None:
            return self._f
        elif self._omega is not None:
            return self._omega/2/np.pi
        else:
            return None

    @f.setter
    def f(self, _f):
        """Frequency axis setter.

        Parameters
        ----------
        _f: array
            The frequency axis.
        """
        self._f = _f
        if _f is not None:
            self._omega = _f*2*np.pi

    @property
    def omega(self):
        """The frequency axis in rad/s.

        Parameters
        ----------
        _omega: array
            The frequency axis in rad/s.
        """
        if self._omega is not None:
            return self._omega
        elif self.f is not None:
            return self.f*2*np.pi
        else:
            return None

    @omega.setter
    def omega(self, _omega):
        """Frequency axis setter.
        """
        self._omega = _omega
        if _omega is not None:
            self._f = _omega/2/np.pi
