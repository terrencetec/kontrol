import numpy as np

def lms_update(coefs, input, error, mu=None, mu_max=None, returnmu=False):
    """Update filter coefficients/weights that minimize the mean square
    error. See https://en.wikipedia.org/wiki/Least_mean_squares_filter for
    information. For now, this function is suppose to be used with real-time
    measurement (perhaps with Ezca).

    Args:
        coefs: list or numpy.ndarray
            Filter coefficients/weights to be updated. Its length has to be
            equal to the length of input.
        input: list or numpy.ndarray
            The time series data of the input.
        error: float
            The error to be minimzed.
        mu: float
            The step size of the steepest descent algorithm. It should be
            larger than zero and smaller that 1/lambda_max where lambda_max is
            the larger eigenvalue of the autocorrelation matrix of the input. if
            not given, then it will be estimated from the given input.
        mu_max: float
            The maximum allowable step size. To prevent divergence.
        returnmu: boolean
            If true, then return mu as well.

    Returns:
        new_coefs: list or numpy.ndarray
            The updated filter coefficients/weights.
        mu: float
            The step size used in this iteration. Only returns when returnmu
            is set to True.
    """
    coefs = np.array(coefs)
    input = np.array(input)
    if mu == None:
        R = np.matrix(input).T*np.matrix(input)  # Autocorrelation matrix
        lambda_max = max(np.linalg.eigvals(R).real)
        mu = 1/(lambda_max)
        if mu_max != None:
            if mu >= mu_max:
                mu = mu_max
        # mu = 2/np.trace(R)  # This guarantees the weights do not diverge.
    new_coefs = coefs + mu*error*input
    if returnmu:
        return(new_coefs, mu)
    else:
        return(new_coefs)

def nlms_update(coefs, input, error, mu=0.1, mu_max=1, returnmu=False):
    coefs = np.array(coefs)
    input = np.array(input)
    if mu_max != None:
        if mu >= mu_max:
            mu = mu_max
        # mu = 2/np.trace(R)  # This guarantees the weights do not diverge.
    new_coefs = coefs + mu*error*input/(float(np.matrix(input)*np.matrix(input).T)+1e-3)
    if returnmu:
        return(new_coefs, mu)
    else:
        return(new_coefs)
