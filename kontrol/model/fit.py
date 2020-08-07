"""Fitting tools for system models and noise.
"""
from scipy.optimize import minimize
from inspect import signature
import numpy as np

def noise_fit(noise_model, f, noise_data, weight=None, x0=None, **kwargs):
    """Noise model fit, follow the argument format of scipy.optimize.curve_fit

    The fitting is done by minimizing the mean-squared whitened error. The
    errors are whitened by the noise data.

    Parameters
    ----------
        noise_model: function
            The noise function in the form of noise_model(f, a, b, c, \.\.\.),
            where a, b, c, \.\.\. are the parameters defining the noise models.
            Example models are in kontrol.model.noise.lvdt_noise() and
            kontrol.model.noise.geophone_noise(). The number of parameters will
            be estimated by introspection (by the number of commas).
        f: array_like
            The frequency axis of the noise
        noise_data: array_like
            The noise data to be fitted. Must have same length as f.
        weight: array_like, optional
            Weightings in frequency domain that will be multiplied to the
            residues before summing. This can be used to filter unwanted data
            or to emphasize particular frequency regions.
        x0: array_like, optional
            Initial guess for of the noise model parameters. If not specified,
            it will be default to ones.
        \*\*kwargs:
            keyword arguments that will be passed to scipy.optimize.minimize.

    Returns
    -------
        args: numpy.ndarray
            The arguments of the noise_model. The fitted noise model can be
            called by noise_model(f, \*args).

    Notes
    -----
        The cost function is defined by the summation of ((noise_model(n) -
        noise data(n))/noise_data(n))^2)^1/2*weight(n)
    """
    if weight is None:
        weight = np.ones_like(noise_data)
    if x0 is None:
        no_of_params = str(signature(noise_model)).count(',')
        x0 = np.ones(no_of_params)
    def cost(args):
        return(sum(np.sqrt((noise_model(f, *args)/noise_data
            - np.ones_like(noise_data))**2)*weight))
    res = minimize(cost, x0, options={'disp':True},
        method='Nelder-Mead', **kwargs)
    args = res.x
    return(args)

def make_weight(x, *segments, default_weight=1.):
    """Make weighting functions for data fitting

    Parameters
    ----------
        x: list or np.ndarray
            The data points for evaluation
        *segments: tuples of (tuple of (float, float), float)
            Set weights values for segments of the data.
            The first entry specify the bound of the segment.
            The second entry specify the weight of the segment.
            Use np.inf for unbounded segments.
        default_weight: float, optional
            The default value of the weighting function.
            Defaults to be 1.

    Returns
    -------
        weight: np.ndarray
            The weighting function as specfied.
    """

    weight = np.ones_like(x) * default_weight

    for seg in segments:
        lower = seg[0][0]
        upper = seg[0][1]
        weight_val = seg[1]
        if lower > upper:
            _ = lower
            lower = upper
            upper = _
        mask_bool = (x >= lower) & (x <= upper)
        mask_value = mask_bool * weight_val
        weight *= np.logical_not(mask_bool)
        weight += mask_value

    return(weight)
