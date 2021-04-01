"""Complementary filter class for sythesis
"""
import control
import numpy as np
# import scipy.optimize

# from . import conversion
# from . import costs
from . import synthesis
import kontrol.common.math
import kontrol.controlutils
import kontrol.core.transfer_function
import kontrol.core.complementary_filter.synthesis


class ComplementaryFilter(kontrol.core.transfer_function.TransferFunction):
    """A set of complementary filters.

    Attributes
    ----------
    f:
    omega:
    noise1:
    noise2:
    tf_noise1:
    tf_noise2:
    filter1:
    filter2:
    """
    def __init__(self, f=None, noise1=None, noise2=None,
                 filter1=None, filter2=None, unit="f"):
        """Constructor

        Parameters
        ----------
        f: array or None, optional
            The frequency axis.
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
                self.noise1 = abs(noise1(1j*omega))
            else:
                self.noise1 = noise1
        else:
            self.tf_noise1 = None
            self.noise1 = noise1

        if isinstance(noise2, control.xferfcn.TransferFunction):
            self.tf_noise2 = noise2
            if self.omega is not None:
                self.noise2 = abs(noise2(1j*omega))
            else:
                self.noise2 = noise2
        else:
            self.tf_noise2 = None
            self.noise2 = noise2

        self.filter1 = filter1
        self.filter2 = filter2
        if filter1 is not None and filter2 is not None:
            tf_1 = control.tf([1], [1])
            if not kontrol.controlutils.check_tf_equal(tf_1, filter1+filter2):
                raise ValueError("filter1 is not complementary to filter2.")
        elif filter1 is not None and filter2 is None:
            filter2 = control.tf([1], [1]) - filter1
            self.filter2 = filter2
        elif filter1 is None and filter2 is not None:
            filter1 = control.tf([1], [1]) - filter2
            self.filter1 = filter1

        if filter1 is not None and filter2 is not None:
            tf_complementary_matrix = [[filter1], [filter2]]
            tf_complementary = kontrol.controlutils.tfmatrix2tf(
                tf_complementary_matrix)
            super().__init__(tf_complementary)

    ## Make filter1 and filter2 a property.
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
        return kontrol.common.math.quad_sum(noise1_filtered, noise2_filtered)

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
            tf_complementary = kontrol.controlutils.tfmatrix2tf(
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
            tf_complementary = kontrol.controlutils.tfmatrix2tf(
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
        func = kontrol.core.complementary_filter.synthesis.h2complementary
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
        func = kontrol.core.complementary_filter.synthesis.hinfcomplementary
        self._synthesis(func=func, w1=w1, w2=w2)

    def _synthesis(self, func, w1=None, w2=None):
        """Generic complementary filter synthesis function.

        Synthesize the complementary filter using the function and
        re-initialize kontrol.core.transfer_function.TransferFunction
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


    #
    # Parameters
    # ----------
    # f: array
    #     Frequency axis.
    # noise1: array
    #     Sensor noise amplitude spectral density.
    # noise2: array
    #     Sensor noise amplitude spectral density of the other sensor.
    # f2: array, optional
    #     Frequency axis of the second noise amplitude spectral density.
    #
    # Attributes
    # ----------
    # f: array
    #     Frequency axis.
    # noise1: array
    #     Sensor noise amplitude spectral density.
    # noise2: array
    #     Sensor noise amplitude spectral density of the other sensor.
    # f2: array, optional
    #     Frequency axis of the second noise amplitude spectral density.
    # noise1_zpk_fit: array or None
    #     The zero-pole-gain fit of the first noise ASD.
    # noise2_zpk_fit: array or None
    #     The zero-pole-gain fit of the second noise ASD.
    # f_zpk_fit: array or None
    #     Frequency axis for the ZPK fit.
    # noise1_zpk_control_tf: control.xferfcn.TransferFunction
    #     The transfer function object of the noise 1 ZPK fit.
    # noise2_zpk_control_tf: control.xferfcn.TransferFunction
    #     The transfer function object of the noise 2 ZPK fit.
    # noise1_tf_fit: array or None
    #     The transfer function fit of the first noise ASD.
    # noise2_tf_fit: array or None
    #     The transfer function fit of the second noise ASD.
    # f_tf_fit: array or None
    #     Frequency axis for the trasnfer function fit.
    # noise1_tf: control.xferfcn.TransferFunction or None
    #     The transfer function object of the noise 1 TF fit.
    # noise2_tf: control.xferfcn.TransferFunction or None
    #     The transfer function object of the noise 2 TF fit.
    # filter1: control.xferfcn.TrasnferFunction or None
    #     The first complementary filter.
    # filter2: control.xferfcn.TransferFunction or None
    #     The second complementary filter.
    # noise_super: array
    #     The ampitude spectral density of the super sensor noise.
    # """
    #
    # def __init__(self, f, noise1, noise2, f2=None):
    #     """Constructor
    #
    #     Parameters
    #     ----------
    #     f: array
    #         Frequency axis.
    #     noise1: array
    #         Sensor noise amplitude spectral density.
    #     noise2: array
    #         Sensor noise amplitude spectral density of the other sensor.
    #     f2: array, optional
    #         Frequency axis of the second noise amplitude spectral density.
    #     """
    #     if f2 is None:
    #         f2 = f
    #     self.f = f
    #     self.noise1 = noise1
    #     self.noise2 = noise2
    #     self.f2 = f2
    #     self.noise1_zpk_fit = None
    #     self.noise2_zpk_fit = None
    #     self.f_zpk_fit = None
    #     self.noise1_zpk_control_tf = None
    #     self.noise2_zpk_control_tf = None
    #     self.noise1_tf_fit = None
    #     self.noise2_tf_fit = None
    #     self.f_tf_fit = None
    #     self.noise1_tf = None
    #     self.noise2_tf = None
    #     self.filter1 = None
    #     self.filter2 = None
    #
    # def zpk_fit_noise1(self, order,
    #         differential_evolution_kwargs={"workers":-1,
    #                                        "updating":"deferred"}):
    #     """Fit noise1 with a ZPK model, set self.noise1.zpk_fit.
    #
    #     Paramters
    #     ---------
    #     order: int
    #         The order of the ZPK model
    #     differential_evolution_kwargs: dict, optional
    #         The keyword arguments passed to
    #         scipy.optimize.differential_evolution during fitting.
    #
    #     Returns
    #     -------
    #     scipy.optimize.OptimizeResult
    #         The result of the optimization
    #     """
    #     res = self.zpk_fit(
    #         f=self.f, noise_asd=self.noise1, order=order,
    #         differential_evolution_kwargs=differential_evolution_kwargs)
    #     self.f_zpk_fit = self.f
    #     zpk_args = res.x
    #     self.noise1_zpk_fit = conversion.args2zpk(
    #         f=self.f_zpk_fit, zpk_args=zpk_args)
    #     self.noise1_zpk_fit = abs(self.noise1_zpk_fit)
    #     self.noise1_zpk_control_tf = conversion.args2controltf(
    #         zpk_args=zpk_args)
    #     return res
    #
    # def zpk_fit_noise2(self, order,
    #         differential_evolution_kwargs={"workers":-1,
    #                                        "updating":"deferred"}):
    #     """Fit noise2 with a ZPK model, set self.noise1.zpk_fit.
    #
    #     Paramters
    #     ---------
    #     order: int
    #         The order of the ZPK model
    #     differential_evolution_kwargs: dict, optional
    #         The keyword arguments passed to
    #         scipy.optimize.differential_evolution during fitting.
    #
    #     Returns
    #     -------
    #     scipy.optimize.OptimizeResult
    #         The result of the optimization
    #     """
    #     res = self.zpk_fit(
    #         f=self.f, noise_asd=self.noise2, order=order,
    #         differential_evolution_kwargs=differential_evolution_kwargs)
    #     self.f_zpk_fit = self.f
    #     zpk_args = res.x
    #     self.noise2_zpk_fit = conversion.args2zpk(
    #         f=self.f_zpk_fit, zpk_args=zpk_args)
    #     self.noise2_zpk_fit = abs(self.noise2_zpk_fit)
    #     self.noise2_zpk_control_tf = conversion.args2controltf(
    #         zpk_args=zpk_args)
    #     return res
    #
    # def zpk_fit(self, f, noise_asd, order, differential_evolution_kwargs={}):
    #     """Fit a noise ASD with a given model order using global optimization
    #
    #     Parameters
    #     ----------
    #     f: array
    #         The frequency axis.
    #     noise_asd: array
    #         The noise ASD.
    #     order: int
    #         The order of the ZPK model to be used.
    #     differential_evolution_kwargs: dict
    #         Keyword arguments passed to the differential evolution algorithm
    #         scipy.optimize.differential_evolution().
    #
    #     Returns
    #     -------
    #     res: scipy.optimize.OptimizeResult
    #         The result of the optimization.
    #     """
    #     frequency_bounds = [(min(f), max(f))]*2*order
    #     gain_bound = [(min(noise_asd)*1e-1, max(noise_asd)*1e1)]
    #     bounds = frequency_bounds + gain_bound
    #     res = scipy.optimize.differential_evolution(
    #         func=costs.zpk_fit_cost, args=(f, noise_asd), bounds=bounds,
    #         **differential_evolution_kwargs)
    #     return res
    #
    # def tf_fit_noise1(self, minimize_kwargs={"method":"Powell"}):
    #     """Fit noise1 with a transfer function, using the ZPK fit as initial.
    #
    #     Parameters
    #     ----------
    #     minimize_kwargs: dict, optional
    #         keyword arguments passed to the scipy.optimize.minimize() method.
    #
    #     Returns
    #     -------
    #     res: scipy.optimize.OptimizeResult
    #         The result of optimization.
    #     """
    #     num = self.noise1_zpk_control_tf.num[0][0]
    #     den = self.noise1_zpk_control_tf.den[0][0]
    #     tf_args_0 = np.concatenate((num, den))
    #     log_tf_args_0 = np.log(tf_args_0)
    #     res = self.tf_fit(
    #         f=self.f, noise_asd=self.noise1, x0=log_tf_args_0,
    #         minimize_kwargs=minimize_kwargs)
    #     self.f_tf_fit = self.f
    #     tf_args = np.exp(res.x)
    #     self.noise1_tf_fit = conversion.args2tf(
    #         f=self.f_tf_fit, tf_args=tf_args)
    #     self.noise1_tf_fit = abs(self.noise1_tf_fit)
    #     num = tf_args[:int(len(tf_args)/2)]
    #     den = tf_args[int(len(tf_args)/2):]
    #     self.noise1_tf = control.tf(num, den)
    #     return res
    #
    # def tf_fit_noise2(self, minimize_kwargs={"method":"Powell"}):
    #     """Fit noise1 with a transfer function, using the ZPK fit as initial.
    #
    #     Parameters
    #     ----------
    #     minimize_kwargs: dict, optional
    #         keyword arguments passed to the scipy.optimize.minimize() method.
    #
    #     Returns
    #     -------
    #     res: scipy.optimize.OptimizeResult
    #         The result of optimization.
    #     """
    #     num = self.noise2_zpk_control_tf.num[0][0]
    #     den = self.noise2_zpk_control_tf.den[0][0]
    #     tf_args_0 = np.concatenate((num, den))
    #     log_tf_args_0 = np.log(tf_args_0)
    #     res = self.tf_fit(
    #         f=self.f, noise_asd=self.noise2, x0=log_tf_args_0,
    #         minimize_kwargs=minimize_kwargs)
    #     self.f_tf_fit = self.f
    #     tf_args = np.exp(res.x)
    #     self.noise2_tf_fit = conversion.args2tf(
    #         f=self.f_tf_fit, tf_args=tf_args)
    #     self.noise2_tf_fit = abs(self.noise2_tf_fit)
    #     num = tf_args[:int(len(tf_args)/2)]
    #     den = tf_args[int(len(tf_args)/2):]
    #     self.noise2_tf = control.tf(num, den)
    #     return res
    #
    # def tf_fit(self, f, noise_asd, x0, minimize_kwargs={}):
    #     """Fit a noise ASD with a given model order using global optimization
    #
    #     Parameters
    #     ----------
    #     f: array
    #         The frequency axis.
    #     noise_asd: array
    #         The noise ASD.
    #     x0: array
    #         Initial guess of the numerator and denominators
    #     minimize_kwargs: dict
    #         Keyword arguments passed to the minimize algorithm
    #         scipy.optimize.minimize().
    #
    #     Returns
    #     -------
    #     res: scipy.optimize.OptimizeResult
    #         The result of the optimization.
    #     """
    #     res = scipy.optimize.minimize(
    #         fun=costs.tf_fit_cost, args=(f, noise_asd), x0=x0,
    #         **minimize_kwargs)
    #     return res

    # def synthesis(self):
    #     """Make complementary filter using H-infinity synthesis.
    #     """
    #     w1 = self.noise1_tf/self.noise2_tf
    #     w2 = self.noise2_tf/self.noise1_tf
    #     self.filter1, self.filter2 = synthesis.hinfcomplementary(
    #         n1=w1, n2=w2)
    #
    #     s = 1j*2*np.pi*self.f_tf_fit
    #     noise1_filtered = (abs(self.filter1.horner(s)[0][0])
    #                        * abs(self.noise1_tf.horner(s)[0][0]))
    #     noise2_filtered = (abs(self.filter2.horner(s)[0][0])
    #                        * abs(self.noise2_tf.horner(s)[0][0]))
    #     self.noise_super = kontrol.common.math.quad_sum(
    #         noise1_filtered, noise2_filtered)
