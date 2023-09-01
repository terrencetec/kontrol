import numpy as np

import kontrol.dmd.dmd
import kontrol.dmd.utils


def dmd_forecast(past, t_past, t_future,
                 order=None, truncation_value=None,
                 truncate_threshold=0.99, t_constant=None, i_constant=-1,
                 return_dmd=False):
    """Produce a short term forecast from past time series data using DMD.

    Parameters
    ----------
    past : array
        Past time series
    t_past : array
        Past time axis.
    t_future : array
        The time stamps of the future prediction.
        Preferably some time after t_past.
    order : int, optional
        The order of hankelization.
        Defaults to ``int(len(past)/2)``.
    truncation_value : int, optional
        The number of modes to be taken.
        If not provided, ``kontrol.dmd.auto_truncate()``
        will be used with the parameter ``truncate_threshold``
        to obtain the value.
    truncate_threshold : float, optional
        Truncate modes that has singular values less
        than this fraction of the total.
        This should within [0, 1], with 0 being all modes
        accepted and 1 being all modes truncated.
        Defaults to 0.99.
    t_constant : int, optional
        Time at which the constant vector is defined.
        Only make sense if it's a value in ``t_past``.
        Defaults t_past[-1].
    i_constant : int, optional
        The index of the column vector in the
        data matrix (snapshot) at ``t_constant``.
        Defaults -1.
    return_dmd : boolean, optional
        Return the DMD instance if True.
        Defaults to False.

    Returns
    -------
    forecast : array
        The forecast
    dmd : kontrol.dmd.DMD, optional
        The DMD instance used to produce the forecast.

    Examples
    --------

    .. code-block:: python

       t_past = np.linspace(0, 10, 1024) # Some time axis.
       t_future = np.linspace(10, 15, 512) # Forecast between t=[10, 15].
       time_series = ... # Some time series
       forecast = dmd_forecast(time_series, t_past, t_future)
    """
    if order is None:
        order = int(len(past)/2)

    # Hankelize the time series to create a data matrix.
    snapshot = kontrol.dmd.utils.hankel(array=past, order=order)

    # Create DMD instance
    dt = t_past[1]-t_past[0]
    dmd = kontrol.dmd.dmd.DMD(snapshot_1=snapshot, dt=dt)

    # Do an SVD of the snapshot and obtain a list of singular values.
    dmd.svd()

    # Obtain truncation value
    if truncation_value is None:
        truncation_value = kontrol.dmd.utils.auto_truncate(
            sigma=dmd.sigma, threshold=truncate_threshold)

    dmd.truncation_value = truncation_value

    # Run the DMD algorithm, get the DMD modes.
    dmd.run()

    # figure out how to handle t_predict and constants.
    if t_constant is None:
        t_constant = t_past[-1]
    prediction = dmd.predict(
        t=t_future, t_constant=t_constant, i_constant=i_constant)
    forecast = np.real(prediction[-1])  # Use last row for forecasting.

    if return_dmd:
        return forecast, dmd
    else:
        return forecast
