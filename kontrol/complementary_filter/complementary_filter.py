"""Complementary filter class for sythesis
"""
import numpy as np


import kontrol.core.math
import kontrol.core.controlutils
import kontrol.complementary_filter.synthesis
import kontrol.transfer_function


class ComplementaryFilter():
    r"""Complementary filter synthesis class.

    Parameters
    ----------
    noise1 : TransferFunction
        Sensor noise 1 transfer function model.
        A transfer function that has magnitude response matching the
        amplitude spectral density of noise 1.
    noise2 : TransferFunction
        Sensor noise 2 transfer function model.
        A transfer function that has magnitude response matching the
        amplitude spectral density of noise 2.
    weight1 : TransferFunction, optional
        Weighting function 1.
        Frequency dependent specification for noise 1.
        Defaults None.
    weight2 : TransferFunction, optional
        Weighting function 2.
        Frequency dependent specification for noise 2.
        Defaults None.
    filter1 : TransferFunction, optional
        The complementary filter for noise 1.
        Defaults None.
    filter2 : TransferFunction, optional
        The complementary filter for noise 2.
        Defaults None.
    f : array, optional
        The frequency axis in Hz for evaluating the super sensor noise.
        Defaults None.

    Methods
    -------
    h2synthesis()
        Complementary filter synthesis that minimizes the
        :math:`\mathcal{H}_2`-norm
        of the super sensor noise. The noise must be specified
        before using this method.
    hinfsynthesis()
        Complementary filter synthesis that minimizes the
        :math:`\mathcal{H}_\infty`-norm
        of the super sensor noise. The noise must be specified
        before using this method.

    Notes
    -----
    This is a utility class for complementary filter synthesis,
    sensor noise estimation and analysis.
    To use synthesis methods, specify ``noise1`` and ``noise2`` as
    the transfer function models for the sensor noises, and
    specify ``weight1`` and ``weight2`` as the frequency-dependent
    specifications for the two sensor noises.

    References
    ----------
    .. [1]
        T. T. L. Tsang, T. G. F. Li, T. Dehaeze, C. Collette.
        Optimal Sensor Fusion Method for Active Vibration Isolation Systems in
        Ground-Based Gravitational-Wave Detectors.
        https://arxiv.org/pdf/2111.14355.pdf
    """
    def __init__(self, noise1=None, noise2=None, weight1=None, weight2=None,
                 filter1=None, filter2=None, f=None):
        """Constructor

        Parameters
        ----------
        noise1 : TransferFunction
            Sensor noise 1 transfer function model.
            A transfer function that has magnitude response matching the
            amplitude spectral density of noise 1.
        noise2 : TransferFunction
            Sensor noise 2 transfer function model.
            A transfer function that has magnitude response matching the
            amplitude spectral density of noise 2.
        weight1 : TransferFunction, optional
            Weighting function 1.
            Frequency dependent specification for noise 1.
            Defaults None.
        weight2 : TransferFunction, optional
            Weighting function 2.
            Frequency dependent specification for noise 2.
            Defaults None.
        filter1 : TransferFunction, optional
            The complementary filter for noise 1.
            Defaults None.
        filter2 : TransferFunction, optional
            The complementary filter for noise 2.
            Defaults None.
        f : array, optional
            The frequency axis in Hz for evaluating the super sensor noise.
            Defaults None.
        """
        self._noise1 = None
        self._noise2 = None
        self._weight1 = None
        self._weight2 = None
        self._filter1 = None
        self._filter2 = None
        self._f = None
        self.noise1 = noise1
        self.noise2 = noise2
        self.weight1 = weight1
        self.weight2 = weight2
        self.filter1 = filter1
        self.filter2 = filter2
        self._f = f

    def h2synthesis(self, clean_filter=True, **kwargs):
        """Synthesize complementary filters using H2 synthesis.

        Returns
        -------
        filter1 : TransferFunction
            The complementary filter filtering noise 1.
        filter2 : TransferFunction
            The complementary filter filtering noise 2.
        clean_filter : boolean, optional
            Remove small outlier coefficients from filters.
            Defaults True.
        **kwargs
            Keyword arguments passed to kontrol.TransferFunction.clean()
        """
        func = kontrol.complementary_filter.synthesis.h2complementary
        return self._synthesis(func=func, clean_filter=clean_filter, **kwargs)

    def hinfsynthesis(self, clean_filter=True, **kwargs):
        """Synthesize complementary filters using H-inifinity synthesis.

        Returns
        -------
        filter1 : TransferFunction
            The complementary filter filtering noise 1.
        filter2 : TransferFunction
            The complementary filter filtering noise 2.
        clean_filter : boolean, optional
            Remove small outlier coefficients from filters.
            Defaults True.
        **kwargs
            Keyword arguments passed to kontrol.TransferFunction.clean()
        """
        func = kontrol.complementary_filter.synthesis.hinfcomplementary
        return self._synthesis(func=func, clean_filter=clean_filter, **kwargs)

    def _synthesis(self, func, clean_filter=True, **kwargs):
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
        clean_filter : boolean, optional
            Remove small outlier coefficients from filters.
            Defaults True.
        **kwargs
            Keyword arguments passed to kontrol.TransferFunction.clean()
        """
        filter1, filter2 = func(
            self.noise1, self.noise2, self.weight1, self.weight2, **kwargs)
        self.filter1 = filter1
        self.filter2 = filter2
        if clean_filter:
            self.filter1.clean(**kwargs)
            self.filter2 = 1 - self.filter1
        return self.filter1, self.filter2

    @property
    def noise1(self):
        """Transfer function model of sensor noise 1.
        """
        return self._noise1

    @noise1.setter
    def noise1(self, _noise1):
        """noise1 setter

        Parameters
        ----------
        noise1 : TransferFunction
        """
        self._noise1 = _noise1

    @property
    def noise2(self):
        """Transfer function model of sensor noise 2.
        """
        return self._noise2

    @noise2.setter
    def noise2(self, _noise2):
        """noise2 setter

        Parameters
        ----------
        noise2 : TransferFunction
        """
        self._noise2 = _noise2

    def noise_super(self, f=None, noise1=None, noise2=None,
                    filter1=None, filter2=None):
        """Compute and return predicted the ASD of the super sensor noise

        Parameter
        ---------
        f : array, optional
            The frequency axis in Hz.
            Use self.f if None.
            Defaults None.
        noise1 : array, optional
            The amplitude spectral density of noise 1.
            Use self.noise1 and self.f to estimate if None.
            Defaults None.
        noise2 : array, optional
            The amplitude spectral density of noise 2.
            Use self.noise1 and self.f to estimate if None.
            Defaults None.
        filter1 : TransferFunction, optional
            The complementary filter for filtering noise1
            Use self.filter1 if not specified.
            Defaults None
        filter2 : TransferFunction, optional
            The complementary filter for filtering noise1
            Use self.filter2 if not specified.
            Defaults None

        Returns
        -------
        array
            The amplitude spectral density of the super sensor noise.
        """
        if f is None:
            if self.f is None:
                raise ValueError("self.f is not specified.")
            f = self.f
        if filter1 is None:
            if self.filter1 is None:
                raise ValueError("self.filter1 is not specified. "
                                 "Please specify self.filter1 or synthesize.")
            filter1 = self.filter1
        if filter2 is None:
            if self.filter2 is None:
                raise ValueError("self.filter2 is not specified. "
                                 "Please specify self.filter2 or synthesize.")
            filter2 = self.filter2
        if noise1 is None:
            if self.noise1 is None:
                raise ValueError("noise1 is not specified. "
                                 "Please specify noise1 or self.noise1.")
            noise1 = abs(self.noise1(1j*2*np.pi*f))
        if noise2 is None:
            if self.noise2 is None:
                raise ValueError("noise2 is not specified. "
                                 "Please specify noise2 or self.noise2.")
            noise2 = abs(self.noise2(1j*2*np.pi*f))
        noise1_filtered = abs(filter1(1j*2*np.pi*f)) * noise1
        noise2_filtered = abs(filter2(1j*2*np.pi*f)) * noise2
        return kontrol.core.math.quad_sum(noise1_filtered, noise2_filtered)

    @property
    def filter1(self):
        """First complementary filter.
        """
        return self._filter1

    @filter1.setter
    def filter1(self, _filter1):
        """filter1 setter.

        Parameters
        ----------
        _filter1 : TransferFunction
        """
        if _filter1 is None:
            self._filter1 = _filter1
        else:
            self._filter1 = kontrol.transfer_function.TransferFunction(
                _filter1)

    @property
    def filter2(self):
        """Second complementary filter.
        """
        return self._filter2

    @filter2.setter
    def filter2(self, _filter2):
        """filter2 setter.

        Parameters
        ----------
        _filter2 : TransferFunction
        """
        if _filter2 is None:
            self._filter2 = _filter2
        else:
            self._filter2 = kontrol.transfer_function.TransferFunction(
                _filter2)

    @property
    def f(self):
        """The frequency axis in Hz.
        """
        return self._f

    @f.setter
    def f(self, _f):
        """Frequency axis setter.

        Parameters
        ----------
        _f: array
            The frequency axis.
        """
        self._f = _f
