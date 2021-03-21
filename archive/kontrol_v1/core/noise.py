"""Noise instance for handling noise frequency series.
"""
import numpy as np
import kontrol.model.fit
import kontrol.utils
import tqdm.auto as tqdm
import scipy.optimize
import control

from kontrol.logger import logger

class Noise:
    """Noise spectral density class

    Attributes
    ----------
    f: array
        The frequency axis, with DC stripped away.
    asd: array
        The amplitude spectral density of the noise
    coh: array, optional
        A conherence between the noise measurement and another
        measurement measuring the same quantity by another sensor.
        This is useful for filtering out signals from the noise ASD.
    coh_threshold: float, optional
        Coherence threshold for making the coherence weighting.
        If coherence is higher than this threshold, the weight is zero.
        Otherwise, the weight is one.
    asd_fit: array
        The fitted amplitude spectral density from the amplitude of the
        fitting transfer function.
    tf: control.xferfcn.TransferFunction
        The transfer function that approximates the noise ASD.
    args: array
        An odd number length array. First half is position of the zeros,
        second half is the position of the poles, last entry is the gain of the
        fitted transfer function.
    label: string
        A label describing the sensor noise.
    fit_results: scipy.optimize.OptimizeResults
        The optimization results for fitting.
    all_tf: list of list of control.xferfcn.TransferFunction
        All fitted transfer functions.
    all_args: list of list of float
        All fitted arguments.
    all_fit_results: list of list of scipy.optimize.OptimizeResults
        All optimization results for fitting.
    weight: array
        Weighting function used during fitting.
    log_params: boolean
        Handles logarithms of the arguments instead.

    Methods
    -------
    fit(self, order_bound=(0, 10), frequency_bound=None, gain_bound=None,
            nfits=1, stop_criterion=None, tol=0., **kwargs)
    """

    def __init__(self, f, asd, coh=None, coh_threshold=0.5, label=None,
            log_params=True):
        """Initiate a Noise instance

        Parameters
        ----------
        f: array
            The frequency axis of the noise spectral density
        asd: array
            The amplitude spectral density of the noise.
        coh: array, optional
            A conherence between the noise measurement and another
            measurement measuring the same quantity by another sensor.
            This is useful for filtering out signals from the noise ASD.
        coh_threshold: float, optional
            Coherence threshold for making the coherence weighting.
            If coherence is higher than this threshold, the weight is zero.
            Otherwise, the weight is one.
        label: string, optional
            A label describing the sensor noise.
        log_params: boolean
            Handles logarithms of the arguments instead.
        """

        if len(f) != len(asd):
            raise ValueError('Length of f {} not equal to length of asd {}'\
                ''.format(len(f), len(asd)))
        mask = f>0
        self.f = np.array(f[mask])
        self.asd = np.array(asd[mask])
        if coh is None:
            self.coh = None
        elif len(coh) != len(f):
            raise ValueError('Length of coh {} not equal to length of f {}'\
                ''.format(len(coh), len(f)))
        else:
            self.coh = np.array(coh[mask])
        self.coh_threshold = coh_threshold
        self.asd_fit = None
        self.tf = None
        self.args = []
        self.label = label
        self.fit_results = None
        self.all_tf = None
        self.all_args = []
        self.all_fit_results = None
        self.weight = None
        self.log_params = log_params

    def fit(self, order_bound=(0, 10), frequency_bound=None, gain_bound=None,
            nfits=1, stop_criterion=None, tol=0., log_params=None,
            use_coh=True, **kwargs):
        """Use a transfer function to approximate the noise.

        The function will fit *ntrials* time for each system order
        with increasing order and will
        terminate according to *stop_criterion*.
        The fit is done by
        minimizing the logarithmic least mean square error.

        Parameters
        ----------
        order_bound: tuple of (int, int), optional
            The maximum number of zeros or poles. Bound inclusive.
            Defaults to (0, 10).
        frequency_bound: tuple of (float, float), optional
            The frequency bound of the zeros and poles.
            Defaults to (min(self.f) - 1 decade, max(self.f) + 1 decade).
        gain_bound: tuple of (float, float), optional
            The gain bound.
            Defaults to (min(self.asd)*1e-1, max(self.asd)*1e1).
        nfits: int, optional
            Number of fit trials for each system order.
        stop_criterion: 'min', 'mean', or None, optional
            Defaults to None.
            'min': terminate when the minimum cost of the current order
                is higher than the previous order, or if didn't improve
                by some fraction tolerance.
            'mean': terminate when then mean cost of the current order
                is higher than then previous order, or if didn't improve
                by some tolerable fraction.
            None: Do not terminate until all iteration is finished.
        tol: float, optional
            The fractional tolerance. If the new, higher order fit didn't
            improve by this tolerance, the fit will be terminated.
            Defaults to 0.
        log_params: boolean, optional
            Optimize the base-10 logarithm of the parameters instead.
            This overrides self.log_params.
            Defaults to None.
        use_coh: boolean, optional
            Use the coherence function between the two sensor readouts
            to filter coherent data.
            Defaults to True.
        **kwargs:
            Keyword arguments that will be passed to the optimization
            algorithm (scipy.optimize.differential_evolution).
            Defaults to {'workers:-1'}, this will use all available cpu cores.
        """
        if 'workers' not in kwargs:
            kwargs['workers'] = -1
        if 'maxiter' not in kwargs:
            kwargs['maxiter'] = (max(order_bound)*2+1) * 1000
        if frequency_bound is None:
            frequency_bound = [(np.min(self.f)*1e-1, np.max(self.f)*1e1)]
        if gain_bound is None:
            gain_bound = (np.min(self.asd)*1e-1, np.max(self.asd)*1e1)
        if self.weight is None:
            # self.weight = kontrol.model.fit.vinagre_weight(omega=self.f)
            self.weight = kontrol.model.fit.one_on_f_weight(f=self.f)
        if use_coh:
            self.weight *= kontrol.model.fit.coherence_weight(
                coh=self.coh, threshold=self.coh_threshold, invert=True)
        if log_params is not None:
            if isinstance(log_params, bool):
                self.log_params = log_params
            else:
                logger.Error('log_params:{} is not bool. Using default'
                             'self.log_params:{} instead.'
                             ''.format(log_params, self.log_params))

        norder = max(order_bound)-min(order_bound)+1
        self.all_tf = [[]] * norder
        self.all_args = [[]] * norder
        self.all_fit_results = [[]] * norder
        self._costs = [[]] * norder
        for i, order in tqdm.tqdm(zip(range(norder),
                range(np.min(order_bound), np.max(order_bound)+1)),
                desc='Current order'):
            bounds = frequency_bound*order*2
            bounds.append(gain_bound)
            if self.log_params:
                bounds = np.log10(bounds)

            fit_results_list = []
            args_list = []
            tf_list = []
            costs_list = []
            for n in tqdm.tqdm(range(nfits),
                    desc='{}th-order fits'.format(order)):
                res = scipy.optimize.differential_evolution(
                    func=cost,
                    bounds=bounds,
                    args=(args2tfamp,
                          kontrol.utils.lmse, self.f, self.asd,
                          self.weight, self.log_params),
                    **kwargs,)

                if self.log_params:
                    args = np.power(np.ones_like(res.x)*10, res.x)
                else:
                    args = res.x
                fit_results_list.append(res)
                args_list.append(args)
                tf_list.append(args2controltf(args))
                costs_list.append(res.fun)

                # Capture the best fit.
                if self.fit_results is None:
                    self.fit_results = res
                    self.tf = args2controltf(args)
                    self.asd_fit = args2tfamp(args, self.f)
                    self.args = args
                elif self.fit_results.fun > res.fun:
                    self.fit_results = res
                    self.tf = args2controltf(args)
                    self.asd_fit = args2tfamp(args, self.f)
                    self.args = args

            self.all_fit_results[i] = fit_results_list
            self.all_args[i] = args_list
            self.all_tf[i] = tf_list
            self._costs[i] = costs_list
            if i > 0:
                if stop_criterion == 'min':
                    current_cost = np.min(self._costs[i])
                    prev_cost = np.min(self._costs[i-1])
                    improvement = (prev_cost-current_cost)/prev_cost
                elif stop_criterion == 'mean':
                    current_cost = np.mean(self._costs[i])
                    prev_cost = np.mean(self._costs[i-1])
                    improvement = (prev_cost-current_cost)/prev_cost
                else:
                    improvement = tol
                if improvement < tol:
                    logger.info('Current {} cost {},'\
                        'previous {} cost {}, improvement is {}, tolerance'
                        'is {}, halting...'\
                        ''.format(stop_criterion, current_cost,
                            stop_criterion, prev_cost, improvement, tolerance))
                    break


def cost(args, args2array, criterion, f, asd, weight=None, log_params=True):
    """ Cost function for curve fitting

    Parameters
    ----------
    args: array
        The parameters.
    args2array: func(args:array, f:array) -> array
        A function the converts the args parameters to
        amplitude frequency response of a transfer function.
    criterion: func(array1:array, array2:array, weight:array) -> float
        A function that computes the cost of given two data arrays.
    asd: array
        The amplitude spectral density to be fitted.
    weight: array, optional
        The weighting function
    log_params: boolean, optional
        Optimize the logarithm of the parameters instead.
        Defaults to True

    Returns
    -------
    float
        The cost.
    """
    if len(f) != len(asd):
        raise ValueError('Length of f {} not equal to length of asd {}'\
            ''.format(len(f), len(asd)))
    f = np.array(f)
    asd = np.array(asd)
    if weight is None:
        weight = np.ones_like(asd)
    elif len(weight) != len(asd):
        raise ValueError('Length of weight {} not equal to length of asd {}'\
            ''.format(len(weight), len(asd)))
    else:
        weight = np.array(weight)
    if log_params:
        args = np.power(np.ones_like(args)*10, args)
    array1 = args2array(args=args, f=f)
    array2 = asd
    loss = criterion(array1=array1, array2=array2, weight=weight)
    return loss


def args2zpk(args):
    """Convert ZPK parameters to ZPK list

    Parameters
    ----------
    args: array
        An odd number length array. First half is position of the zeros,
        second half is the position of the poles, last entry is the gain of the
        transfer function.

    Returns
    -------
    zeros: array
        list of zeros.
    poles: array
        list of poles
    gain: float
        gain
    """
    if np.mod(len(args), 2) == 0:
        raise ValueError('Number of arguments must be odd')
    zeros = args[0:np.int(np.floor(len(args)/2))]
    poles = args[np.int(np.floor(len(args)/2)):len(args)-1]
    gain = args[-1]
    return zeros, poles, gain


def args2tfcomplex(args, f):
    """Convert ZPK parameters to complex-valued frequency response.

    Parameters
    ----------
    args: array
        An odd number length array. First half is position of the zeros,
        second half is the position of the poles, last entry is the gain of the
        transfer function.

    f: array
        Frequency axis of the frequency response in Hz.

    Returns
    -------
    tf: array
        The complex-valued frequency response
    """
    f = np.array(f)
    s = 1j*2*np.pi*f
    zeros, poles, gain = args2zpk(args)
    tf = np.ones_like(f) + 0j*np.ones_like(f)
    for z in zeros:
        tf *= (s/(2*np.pi*z) + 1)
    for p in poles:
        tf /= (s/(2*np.pi*p) + 1)
    tf *= gain
    return tf


def args2controltf(args):
    """Convert ZPK parameters to TransferFunction instance.

    Parameters
    ----------
    args: array
        An odd number length array. First half is position of the zeros,
        second half is the position of the poles, last entry is the gain of the
        transfer function.

    Returns
    -------
    control.xferfcn.TransferFunction
        The trasnfer function
    """
    s = control.tf('s')
    zeros, poles, gain = args2zpk(args)
    tf = control.tf([1], [1])
    for z in zeros:
        tf *= (s/(2*np.pi*z) + 1)
    for p in poles:
        tf /= (s/(2*np.pi*p) + 1)
    tf *= gain
    return tf


def args2tfamp(args, f):
    """Convert ZPK parameters to amplitude frequency response.

    Parameters
    ----------
    args: array
        An odd number length array. First half is position of the zeros,
        second half is the position of the poles, last entry is the gain of the
        transfer function.

    f: array
        Frequency axis of the frequency response in Hz.

    Returns
    -------
    array
        The amplitude frequency response
    """
    return abs(args2tfcomplex(args=args, f=f))
