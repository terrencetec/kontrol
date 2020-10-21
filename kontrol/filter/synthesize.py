"""Filter synthesize classes library
"""
import control
import kontrol.series.FrequencySeries
import numpy as np

from kontrol import logger

class ComplementaryFilter:
    """Complementary filter synthesis class.

    Attributes
    ----------
    noise1: array
        The amplitude spectral density of the sensor noise of the
        first sensor to be blended.
    noise2: array
        The amplitude spectral density of the sensor noise of the
        second sensor to be blended.
    coh: array,
        The coherence between the two sensors.
        Defaults to None. It will be used to generate a frequency
        dependent weight to filter out signals from the noise spectral
        densities.
    weight: array,
        Additional frequency dependent weighting functions that will
        be use when fitting the noises.

    """

    def __init__(self, f, noise1, noise2, coh=None, weight=None):
        """ Initiate the complementary filter with noise characteristics.

        Parameters
        ----------
        f: array
            The frequency axis of the noise amplitude spectral density.
        noise1: array
            The amplitude spectral density of the sensor noise of the
            first sensor to be blended.
        noise2: array
            The amplitude spectral density of the sensor noise of the
            second sensor to be blended.
        coh: array, optional
            The coherence between the two sensors.
            Defaults to None. It will be used to generate a frequency
            dependent weight to filter out signals from the noise spectral
            densities. If None, it will be set to zeros.
        weight: array, optional
            Additional frequency dependent weighting functions that will
            be use when fitting the noises.
            By default, it will use the log, normalized Vinagre's weight [1]_.

        References
        ----------
        .. [1]
            Valério, Duarte & Ortigueira, Manuel & Costa, José. (2008).
            Identifying a Transfer Function From a Frequency Response.
            Journal of Computational and Nonlinear Dynamics -
            J COMPUT NONLINEAR DYN. 3. 7-1077. 10.1115/1.2833906.
        """

        self.f = np.array(f)
        self.noise1 = np.array(noise1)
        self.noise2 = np.array(noise2)
        if len(self.noise1) != len(self.noise2):
            raise ValueError('Length of noise1 {} is not equal to that of'\
                'noise2 {}'.format(len(self.noise1), len(self.noise2)))
        if len(self.f) != len(self.noise1):
            raise ValueError('Length of f {} is not equal to that of'\
                'noise2 {}'.format(len(self.f), len(self.noise1)))
        if coh is None:
            self.coh = np.zeros_like(self.noise1)
        if len(coh) != len(noise1):
            raise ValueError('Length of coh {} is not equal that of noise1'\
                'and noise2 {}'.format(len(coh), len(noise1)))
        if weight is None:
            self.weight = np.ones_like(noise1)
