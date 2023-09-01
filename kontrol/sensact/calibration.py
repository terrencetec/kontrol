"""Calibration library for calibrating sensors from sensors measurements"""
import numpy as np
import scipy.optimize

import kontrol.curvefit


def calibrate(xdata, ydata, method="linear", **kwargs):
    """Fit the measurement data and returns the slope of the fit.

    Parameters
    ----------
    xdata : array
        The independent variable, e.g. the displacement of the sensor.
    ydata : array
        The dependent variable, e.g. the sensor readout.
    method : str, optional
        The method of the fit.
        Choose from ["linear", "erf"].
       - "linear": use ``kontrol.sensact.calibration.calibrate_linear()``
       - "erf": use ``kontrol.sensact.calibration.calibrate_erf()``
    **kwargs :
        Keyword arguments passed to the calibration methods.

    Returns
    -------
    slope : float
        The slope of the fitted straight line.
    intercept : float
        The y-intercept of the fitted straight line.
    linear_range : float, optional
        The range of y where the sensor considered linear.
    """
    if method == "linear":
        return calibrate_linear(xdata, ydata, **kwargs)
    elif method == "erf":
        return calibrate_erf(xdata, ydata, **kwargs)
    else:
        raise ValueError("Invalid method. "
                         'Please choose from ["linear", "erf"].')


def calibrate_linear(
        xdata, ydata, nonlinearity=5, full_range=None, start_index=None,
        return_linear_range=False, return_model=False):
    """Fit a straight line to the data and returns the slope and intercept

    This functions recursively fits a straight line to chosen data points and
    terminates when no linear data point remains. It starts from 3 points
    closest to the middle of the full-range. After fitting a straight line
    to the 3 points, other data points that are within the linearity
    specification will be included to the dataset and this dataset will be
    use for the next fit. The process repeats until no data points can
    be added anymore.

    Parameters
    ----------
    xdata : array
        The independent variable, e.g. the displacement of the sensor.
    ydata : array
        The dependent variable, e.g. the sensor readout.
    nonlinearity : float, optional
        The specification of non-linearity (%).
        Defined by the maximum deviation of the full_range.
        Default 5.
    full_range : float, optional
        The full output range of the sensor.
        If not specified, it will be chosen to be
        ``max(ydata) - min(ydata)``
    start_index : int, optional
        The index of the data point to start with.
        If not specified, it will be chosen to be index of the ``ydata``
        closest to ``(max(ydata) + min(ydata))/2``.
    return_linear_range : boolean, optional
        If True, return the linear range of ydata.
    return_model : boolean, optional
        Return a kontrol.curvefit.model.Model object with the fitted
        parameters.

    Returns
    -------
    slope : float
        The slope of the fitted straight line.
    intercept : float
        The y-intercept of the fitted straight line.
    linear_range : float, optional
        The range of x where the sensor considered linear.
    model : kontrol.curvefit.model.Model
        The fitted model.
    """
    xdata = np.array(xdata)
    ydata = np.array(ydata)
    # Sort data
    sort_indexes = np.argsort(xdata)
    xdata = xdata[sort_indexes]
    ydata = ydata[sort_indexes]
    if full_range is None:
        full_range = max(ydata) - min(ydata)
    if start_index is None:
        mid_range = np.mean([max(ydata), min(ydata)])
        # Find the element closest to the mid_range
        error = None
        for i in range(len(ydata)):
            if error is None:
                error = abs(ydata[i] - mid_range)
            if abs(ydata[i] - mid_range) < error:
                start_index = i
                error = abs(ydata[i] - mid_range)
    error_func = kontrol.curvefit.error_func.mse
    cost = kontrol.curvefit.Cost(error_func=error_func)
    model = kontrol.curvefit.model.StraightLine()
    optimizer = scipy.optimize.minimize
    curvefit = kontrol.curvefit.CurveFit()
    curvefit.model = model
    curvefit.cost = cost
    curvefit.optimizer = optimizer

    mask = np.zeros_like(xdata) == 1
    for i in range(len(mask)):
        if (
            i == start_index or i-1 == start_index
                or i+1 == start_index):
            # Set the mask such the the middle points are true.
            mask[i] = True
    # Starting from 3 points in the middle, fit a straight line
    # and include those data points which fall within the linearity
    # specification, and repeats.
    while 1:
        curvefit.xdata = xdata[mask]
        curvefit.ydata = ydata[mask]
        x0_slope = ((curvefit.ydata[-1] - curvefit.ydata[0])
                    / (curvefit.xdata[-1] - curvefit.xdata[0]))
        x0_intersect = ydata[start_index] - x0_slope*xdata[start_index]
        x0 = [x0_slope, x0_intersect]
        optimizer_kwargs = {"x0": x0}
        curvefit.optimizer_kwargs = optimizer_kwargs
        curvefit.fit()
        line_fit = curvefit.model(xdata)
        nonlinearity_mask = abs(line_fit-ydata)/abs(full_range) * 100
        mask |= nonlinearity_mask < nonlinearity  # Include points
        # that are within the linearity specification.
        if len(xdata[mask]) == len(curvefit.xdata):
            # terminate when dataset didn't increase
            break

    slope = curvefit.model.slope
    intercept = curvefit.model.intercept

    returns = (slope, intercept)
    if return_linear_range:
        linear_range = max(curvefit.ydata) - min(curvefit.ydata)
        returns += (linear_range,)
    if return_model:
        returns += (curvefit.model,)

    return returns


def calibrate_erf(
        xdata, ydata, nonlinearity=5, return_linear_range=False,
        return_model=False):
    r"""Fit an error function and return the 1st-order slope and intercept.

    Parameters
    ----------
    xdata : array
        The independent variable, e.g. the displacement of the sensor.
    ydata : array
        The dependent variable, e.g. the sensor readout.
    nonlinearity : float, optional
        The specification of non-linearity (%).
        Defined by the maximum deviation of the full_range.
        Default 5.
    return_linear_range : boolean, optional
        If True, return the linear range of ydata.
    return_model : boolean, optional
        Return a kontrol.curvefit.model.Model object with the fitted
        parameters.

    Returns
    -------
    slope : float
        The slope of the fitted straight line.
    intercept : float
        The :math:`y`-intercept of the fitted straight line.
    linear_range : float, optional
        The range of x where the sensor considered linear.

    Notes
    -----
    Credits to Kouseki Miyo, the inventor of this method.

    We fit the following function

    .. math::
       f(x; a, m, x_0, y_0) = a\,\mathrm{erf}(m(x-x_0)) + y_0\,\,

    where :math:`a, m, x_0, y_0` are some parameters to be found.
    The :math:`\mathrm{erf}(x)` function is defined as

    .. math::
       \mathrm{erf}(x) = \frac{2}{\sqrt{\pi}}\int_0^x\,e^{-x^2}\,dx\,.

    If we taylor expand the exponential function and take the first-order
    approximation of the :math:`\mathrm{erf}(x)` function, we get

    .. math::
       \mathrm{erf}(x) \approx \frac{2am}{\sqrt{\pi}}(x-x_0) + y_0\,.

    So the (inverse) calibration factor is :math:`\frac{2am}{\sqrt{\pi}}`,
    and the :math:`y`-intercept is :math:`\frac{2am}{\sqrt{\pi}}x_0 + y_0`.
    """
    xdata = np.array(xdata)
    ydata = np.array(ydata)
    # Sort data
    sort_indexes = np.argsort(xdata)
    xdata = xdata[sort_indexes]
    ydata = ydata[sort_indexes]
    # Scale data for numerical stability
    xmean = np.mean(xdata)
    xdata -= xmean
    x_scale = max(abs(xdata))
    y_scale = max(abs(ydata))
    xdata /= x_scale
    ydata /= y_scale

    # Setup kontrol.curvefit
    error_func = kontrol.curvefit.error_func.mse
    cost = kontrol.curvefit.Cost(error_func=error_func)
    model = kontrol.curvefit.model.Erf()
    optimizer = scipy.optimize.minimize
    curvefit = kontrol.curvefit.CurveFit()
    curvefit.xdata = xdata
    curvefit.ydata = ydata
    curvefit.model = model
    curvefit.cost = cost
    curvefit.optimizer = optimizer

    # Guess initial parameters
    x0_amplitude = (max(ydata)-min(ydata)) / 2
    x0_slope = ((ydata[-1] - ydata[0]) / (xdata[-1] - xdata[0]))
    mid_range = np.mean([max(ydata), min(ydata)])
    # Find the element closest to the mid_range
    error = None
    for i in range(len(ydata)):
        if error is None:
            error = abs(ydata[i] - mid_range)
        if abs(ydata[i] - mid_range) < error:
            start_index = i
            error = abs(ydata[i] - mid_range)
    x0_x_offset = xdata[start_index]
    x0_y_offset = ydata[start_index]
    x0 = [x0_amplitude, x0_slope, x0_x_offset, x0_y_offset]
    optimizer_kwargs = {"x0": x0}
    
    curvefit.optimizer_kwargs = optimizer_kwargs
    res = curvefit.fit()

    # Unscaling
    curvefit.model.amplitude *= y_scale
    curvefit.model.slope /= x_scale
    curvefit.model.x_offset *= x_scale
    curvefit.model.x_offset += xmean
    curvefit.model.y_offset *= y_scale
    xdata *= x_scale
    xdata += xmean
    ydata *= y_scale

    a = curvefit.model.amplitude
    m = curvefit.model.slope
    x0 = curvefit.model.x_offset
    y0 = curvefit.model.y_offset
    slope = a*m*2/np.sqrt(np.pi)
    intercept = -slope*x0 + y0

    returns = (slope, intercept)
    if return_linear_range:
        y = kontrol.curvefit.model.StraightLine(args=[slope, intercept])
        full_range = max(curvefit.model(xdata)) - min(curvefit.model(xdata))
        nonlinearity_mask = (abs(y(xdata) - curvefit.model(xdata))
                             / full_range
                             * 100)
        mask = nonlinearity_mask < nonlinearity
        y_linear = ydata[mask]
        linear_range = max(y_linear) - min(y_linear)
        returns += (linear_range,)
    if return_model:
        returns += (curvefit.model,)

    return returns
