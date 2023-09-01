"""Model base class for curve fitting.
"""


class Model:
    """Model base class for curve fitting"""
    def __init__(self, args=None, nargs=None, log_args=False):
        """Constructor

        Parameters
        ----------
        args : array or None, optional
            The model parameters.
            Defaults to None.
        nargs : int, optional
            The number of model parameters needed to define the model.
            Defaults to None.
        log_args : boolean, optional
            If true,
            model parameters passed to the model are assumed to be passed
            through a log10() function.
            So, when the real parameters will be assumed to be
            10**args instead.
            Defaults to False.
        """
        self.log_args = log_args
        self._args = None
        self._nargs = None
        self.args = args
        self.nargs = nargs

    def __call__(self, x, args=None, **kwargs):
        """Use self._x2y(x, **kwargs) to give y values from x.

        This is a low level function that shouldn't be used by users.

        Parameters
        ----------
        x : array
            Independent variables
        args : array or None, optional
            Model parameters.
            Defaults to None.
            If not specified, use self.args.
            If specified, set self.args to args.
        **kwargs
            Keyword arguments passed to self._x2y().

        Returns
        -------
        y : array
            f(x) = y values.
        """
        if args is None:
            args = self.args
        else:
            self.args = args
        if self.args is None:
            raise ValueError("Please specify model parameters by the "
                             "arg argument or by setting self.arg.")
        return self._x2y(x, **kwargs)

    def _x2y(self, x, **kwargs):
        """Convert independent variables to dependent variables.

        This should be defined independent in child classes.
        This by default returns ``x`` itself, i.e. f(x) = x.

        Parameters
        ----------
        x : array
            The independent variables.
        **kwargs
            Keyword arguments.

        Returns
        -------
        y : array
            f(x) = x.
        """
        y = x
        return y

    @property
    def args(self):
        """Model parameters"""
        return self._args

    @args.setter
    def args(self, _args):
        """args.setter"""
        if self.log_args and _args is not None:
            _args = 10**_args
        self._args = _args
        # self.nargs = len(_args)

    @property
    def nargs(self):
        """Number of model parameters"""
        return self._nargs

    @nargs.setter
    def nargs(self, _nargs):
        """nargs.setter"""
        self._nargs = _nargs
