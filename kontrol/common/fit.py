"""Common functions for curve fitting.
"""
import scipy.optimize


def zpk_fit(self, f, x, order,
            optmizer=scipy.optimize.differential_evolution,
            optimizer_kwargs={}):
    """Fit frequency series with a given model order using global optimization

    Parameters
    ----------
    f: array
        The frequency axis.
    x: array
        The frequency series data
    order: int
        The order of the ZPK model to be used.
    optimizer: func, optional
        The optimization function which has the signature
        func(func, args, bounds, **kw) -> scipy.optimize.OptimizeResult.
        Defaults to scipy.optimize.differential_evolution.
    optimizer_kwargs: dict, optional
        Keyword arguments passed to the optimization function.
        Defaults {} but will set to
        {"workers": -1, "updating":"deferred"} if optimizer is default.

    Returns
    -------
    res: scipy.optimize.OptimizeResult or whatever the optimizer func returns.
        The result of the optimization.
    """
    # Set defaults for the default optimizer
    if "workers" not in optimizer_kwargs.keys():
        if "workers" in inspect.signature(optimizer).parameters:
            optimizer_kwargs["workers"] = -1
    if "updating" not in optimizer_kwargs.keys():
        if "updating" in inspect.signature(optimizer).parameters:
            optimizer_kwargs["updating"] = "deferred"

    frequency_bounds = [(min(f), max(f))]*2*order
    gain_bound = [(min(noise_asd)*1e-1, max(noise_asd)*1e1)]
    bounds = frequency_bounds + gain_bound
    res = scipy.optimize.differential_evolution(
        func=costs.zpk_fit_cost, args=(f, noise_asd), bounds=bounds,
        **differential_evolution_kwargs)
    return res
