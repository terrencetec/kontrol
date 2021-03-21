"""Algorithm module.

The module now contains two LMS algorithms, lms_update() and nlms_update.
"""

import numpy as np

def lms_update(coefs, input, error, mu=None, mu_limits=(0, np.inf), returnmu=False,
        small_number=1e-3, *args, **kwargs):
    """LMS algorithm.

    Update filter coefficients/weights that minimize the mean square
    error. See https://en.wikipedia.org/wiki/Least_mean_squares_filter for
    information.

    Parameters
    ----------
        coefs: list of float or numpy.ndarray
            Filter coefficients/weights to be updated. Its length has to be \
            equal to the length of input.
        input: list of float or numpy.ndarray
            The time series data of the input. The length should be equal to \
            the number of taps of the FIR filter that is to be optimized.
        error: float
            The error to be minimzed.
        mu: float, optional
            The step size of the steepest descent algorithm. It should be \
            larger than zero and smaller that 1/lambda_max where lambda_max \
            is the larger eigenvalue of the autocorrelation matrix of the \
            input. if not given, then it will be estimated from the given \
            input.
        mu_limits: tuple of (int or float, int of float), optional
            Lower and upper limit of the step size. Defaults to be (0, np.inf)
        returnmu: boolean, optional
            If true, then return mu as well. Defaults to False.
        small_number: float, optional
            A small number to be included in the denominator to prevent \
            spikes when calculating the step size mu. Defaults to 1e-3.

    Returns
    -------
        new_coefs: numpy.ndarray
            The updated filter coefficients/weights.
        mu: float
            The step size used in this iteration. Only returns when returnmu \
            is set to True.
    """
    coefs = np.array(coefs)
    input = np.array(input)
    if mu == None:
        R = np.matrix(input).T*np.matrix(input)  # Autocorrelation matrix
        lambda_max = max(np.linalg.eigvals(R).real)
        mu = 1/(lambda_max+small_number)
        if mu > mu_limits[1]:
            mu = mu_limits[1]
        elif mu < mu_limits[0]:
            mu = mu_limits[0]
        # mu = 2/np.trace(R)  # This guarantees the weights do not diverge.
    new_coefs = coefs + mu*error*input
    if returnmu:
        return(new_coefs, mu)
    else:
        return(new_coefs)

def nlms_update(coefs, input, error, mu=0.5, mu_limits=(0, 1), returnmu=False,
        small_number=1e-3, *args, **kwargs):
    """Normalized LMS algorithm. Very similar to lms_update()

    Parameters
    ----------
        coefs: list of float or numpy.ndarray
            Filter coefficients/weights to be updated. Its length has to be \
            equal to the length of input.
        input: list of float or numpy.ndarray
            The time series data of the input.
        error: float
            The error to be minimzed.
        mu: float, optional
            The step size of the steepest descent algorithm. It should be \
            between 0 and 1 for NLMS algorithms.
        mu_limits: tuple of (int or float, int or float), optional
            Lower and upper limit of the step size. Defaults to be (0, 1)
        returnmu: boolean, optional
            If true, then return mu as well.
        small_number: float, optional
            A small number to be included in the denominator to prevent \
            spikes when calculating the step size mu.

    Returns
    -------
        new_coefs: list or numpy.ndarray
            The updated filter coefficients/weights.
        mu: float
            The step size used in this iteration. Only returns when returnmu \
            is set to True.
    """
    coefs = np.array(coefs)
    input = np.array(input)
    if mu > mu_limits[1]:
        mu = mu_limits[1]
    elif mu < mu_limits[0]:
        mu = mu_limits[0]
    new_coefs = (coefs
                 + mu * error * input
                 / (float(np.matrix(input)*np.matrix(input).T) + small_number))
    if returnmu:
        return(new_coefs, mu)
    else:
        return(new_coefs)
