"""Complementary filter class for sythesis
"""
import control
import numpy as np
import scipy.optimize

import kontrol.core.complementary_filter.conversion as conversion
import kontrol.core.complementary_filter.math as math

class ComplementaryFilter:
    """Complementary Filter synthesis class

    Parameters
    ----------
    f: array
        Frequency axis.
    noise1: array
        Sensor noise amplitude spectral density.
    noise2: array
        Sensor noise amplitude spectral density of the other sensor.
    f2: array, optional
        Frequency axis of the second noise amplitude spectral density.

    Attributes
    ----------
    f: array
        Frequency axis.
    noise1: array
        Sensor noise amplitude spectral density.
    noise2: array
        Sensor noise amplitude spectral density of the other sensor.
    f2: array, optional
        Frequency axis of the second noise amplitude spectral density.
    noise1_zpk_fit: array or None
        The zero-pole-gain fit of the first noise ASD.
    noise2_zpk_fit: array or None
        The zero-pole-gain fit of the second noise ASD.
    f_zpk_fit: array or None
        Frequency axis for the ZPK fit.
    noise1_zpk_control_tf: control.xferfcn.TransferFunction
        The transfer function object of the noise 1 ZPK fit.
    noise2_zpk_control_tf: control.xferfcn.TransferFunction
        The transfer function object of the noise 2 ZPK fit.
    noise1_tf_fit: array or None
        The transfer function fit of the first noise ASD.
    noise2_tf_fit: array or None
        The transfer function fit of the second noise ASD.
    f_tf_fit: array or None
        Frequency axis for the trasnfer function fit.
    noise1_tf: control.xferfcn.TransferFunction or None
        The transfer function object of the noise 1 TF fit.
    noise2_tf: control.xferfcn.TransferFunction or None
        The transfer function object of the noise 2 TF fit.
    filter1: control.xferfcn.TrasnferFunction or None
        The first complementary filter.
    filter2: control.xferfcn.TransferFunction or None
        The second complementary filter.
    """

    def __init__(self, f, noise1, noise2, f2=None):
        """Constructor

        Parameters
        ----------
        f: array
            Frequency axis.
        noise1: array
            Sensor noise amplitude spectral density.
        noise2: array
            Sensor noise amplitude spectral density of the other sensor.
        f2: array, optional
            Frequency axis of the second noise amplitude spectral density.
        """
        if f2 is None:
            f2 = f
        self.f = f
        self.noise1 = noise1
        self.noise2 = noise2
        self.f2 = f2
        self.noise1_zpk_fit = None
        self.noise2_zpk_fit = None
        self.f_zpk_fit = None
        self.noise1_zpk_control_tf = None
        self.noise2_zpk_control_tf = None
        self.noise1_tf_fit = None
        self.noise2_tf_fit = None
        self.f_tf_fit = None
        self.noise1_tf = None
        self.noise2_tf = None
        self.filter1 = None
        self.filter2 = None

    def zpk_fit_noise1(self, order,
            differential_evolution_kwargs={"workers":-1,
                                           "updating":"deferred"}):
        """Fit noise1 with a ZPK model, set self.noise1.zpk_fit.

        Paramters
        ---------
        order: int
            The order of the ZPK model
        differential_evolution_kwargs: dict, optional
            The keyword arguments passed to
            scipy.optimize.differential_evolution during fitting.

        Returns
        -------
        scipy.optimize.OptimizeResult
            The result of the optimization
        """
        res = self.zpk_fit(
            f=self.f, noise_asd=self.noise1, order=order,
            differential_evolution_kwargs=differential_evolution_kwargs)
        self.f_zpk_fit = self.f
        zpk_args = res.x
        self.noise1_zpk_fit = conversion.args2zpk(
            f=self.f_zpk_fit, zpk_args=zpk_args)
        self.noise1_zpk_fit = abs(self.noise1_zpk_fit)
        self.noise1_zpk_control_tf = conversion.args2controltf(
            zpk_args=zpk_args)
        return res

    def zpk_fit_noise2(self, order,
            differential_evolution_kwargs={"workers":-1,
                                           "updating":"deferred"}):
        """Fit noise2 with a ZPK model, set self.noise1.zpk_fit.

        Paramters
        ---------
        order: int
            The order of the ZPK model
        differential_evolution_kwargs: dict, optional
            The keyword arguments passed to
            scipy.optimize.differential_evolution during fitting.

        Returns
        -------
        scipy.optimize.OptimizeResult
            The result of the optimization
        """
        res = self.zpk_fit(
            f=self.f, noise_asd=self.noise2, order=order,
            differential_evolution_kwargs=differential_evolution_kwargs)
        self.f_zpk_fit = self.f
        zpk_args = res.x
        self.noise2_zpk_fit = conversion.args2zpk(
            f=self.f_zpk_fit, zpk_args=zpk_args)
        self.noise2_zpk_fit = abs(self.noise2_zpk_fit)
        self.noise2_zpk_control_tf = conversion.args2controltf(
            zpk_args=zpk_args)
        return res

    def zpk_fit(self, f, noise_asd, order, differential_evolution_kwargs={}):
        """Fit a noise ASD with a given model order using global optimization

        Parameters
        ----------
        f: array
            The frequency axis.
        noise_asd: array
            The noise ASD.
        order: int
            The order of the ZPK model to be used.
        differential_evolution_kwargs: dict
            Keyword arguments passed to the differential evolution algorithm
            scipy.optimize.differential_evolution().

        Returns
        -------
        res: scipy.optimize.OptimizeResult
            The result of the optimization.
        """
        frequency_bounds = [(min(f), max(f))]*2*order
        gain_bound = [(min(noise_asd)*1e-1, max(noise_asd)*1e1)]
        bounds = frequency_bounds + gain_bound
        res = scipy.optimize.differential_evolution(
            func=math.zpk_fit_cost, args=(f, noise_asd), bounds=bounds,
            **differential_evolution_kwargs)
        return res

    def tf_fit_noise1(self, minimize_kwargs={"method":"Powell"}):
        """Fit noise1 with a transfer function, using the ZPK fit as initial.

        Parameters
        ----------
        minimize_kwargs: dict, optional
            keyword arguments passed to the scipy.optimize.minimize() method.

        Returns
        -------
        res: scipy.optimize.OptimizeResult
            The result of optimization.
        """
        num = self.noise1_zpk_control_tf.num[0][0]
        den = self.noise1_zpk_control_tf.den[0][0]
        tf_args_0 = np.concatenate((num, den))
        log_tf_args_0 = np.log(tf_args_0)
        res = self.tf_fit(
            f=self.f, noise_asd=self.noise1, x0=log_tf_args_0,
            minimize_kwargs=minimize_kwargs)
        self.f_tf_fit = self.f
        tf_args = np.exp(res.x)
        self.noise1_tf_fit = conversion.args2tf(
            f=self.f_tf_fit, tf_args=tf_args)
        self.noise1_tf_fit = abs(self.noise1_tf_fit)
        num = tf_args[:int(len(tf_args)/2)]
        den = tf_args[int(len(tf_args)/2):]
        self.noise1_tf = control.tf(num, den)
        return res

    def tf_fit_noise2(self, minimize_kwargs={"method":"Powell"}):
        """Fit noise1 with a transfer function, using the ZPK fit as initial.

        Parameters
        ----------
        minimize_kwargs: dict, optional
            keyword arguments passed to the scipy.optimize.minimize() method.

        Returns
        -------
        res: scipy.optimize.OptimizeResult
            The result of optimization.
        """
        num = self.noise2_zpk_control_tf.num[0][0]
        den = self.noise2_zpk_control_tf.den[0][0]
        tf_args_0 = np.concatenate((num, den))
        log_tf_args_0 = np.log(tf_args_0)
        res = self.tf_fit(
            f=self.f, noise_asd=self.noise2, x0=log_tf_args_0,
            minimize_kwargs=minimize_kwargs)
        self.f_tf_fit = self.f
        tf_args = np.exp(res.x)
        self.noise2_tf_fit = conversion.args2tf(
            f=self.f_tf_fit, tf_args=tf_args)
        self.noise2_tf_fit = abs(self.noise2_tf_fit)
        num = tf_args[:int(len(tf_args)/2)]
        den = tf_args[int(len(tf_args)/2):]
        self.noise2_tf = control.tf(num, den)
        return res

    def tf_fit(self, f, noise_asd, x0, minimize_kwargs={}):
        """Fit a noise ASD with a given model order using global optimization

        Parameters
        ----------
        f: array
            The frequency axis.
        noise_asd: array
            The noise ASD.
        x0: array
            Initial guess of the numerator and denominators
        minimize_kwargs: dict
            Keyword arguments passed to the minimize algorithm
            scipy.optimize.minimize().

        Returns
        -------
        res: scipy.optimize.OptimizeResult
            The result of the optimization.
        """
        res = scipy.optimize.minimize(
            fun=math.tf_fit_cost, args=(f, noise_asd), x0=x0,
            **minimize_kwargs)
        return res
