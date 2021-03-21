"""Filter synthesize classes library
"""

import control
import numpy as np

from kontrol import logger


class ComplementaryFilter:
    """Complementary filter synthesis class.

    Attributes
    ----------
    noise1: kontrol.Noise
        kontrol.Noise instance that carries information about the
        first sensor noise.
    noise2: kontrol.Noise
        kontrol.Noise instance that carries information about the
        first sensor noise.
    coh: array,
        The coherence between the two sensors.
        Defaults to None. It will be used to generate a frequency
        dependent weight to filter out signals from the noise spectral
        densities.
    complementary_filter1: kontrol.Filter?
    complementary_filter2: kontrol.Filter?


    """

    def __init__(self, arg1, arg2, arg3=None, coh=None):
        """ Initiate the complementary filter with noise characteristics.

        There are two ways to initialize the Complementary Class.
        ComplementaryFilter(f: array, noise1:array, noise2: array,) with
        f being the frequency axis, noise1 being the amplitude spectral
        density of the first sensor noise and noise2 being the amplitude
        spectral density of the second sensor noise.
        Or ComplementaryFilter(noise1:kontrol.Noise, noise2:kontrol.Noise)
        where noise1 and noise2 are defined kontrol.Noise objects.

        Parameters
        ----------
        arg1:
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
