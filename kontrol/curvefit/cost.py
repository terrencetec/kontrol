"""Cost function base class
"""


class Cost:
    """Cost function base class.
    """
    def __init__(self, error_func, error_func_kwargs=None):
        """Constructor

        Parameters
        ----------
        error_func : func(array, array, **error_func_kwargs) -> float.
            The error function.
            It takes two arrays and evaluate the error.
        error_func_kwargs : dict or None, optional
            Keyword arguments the will be passed to ``error_func``
            Defaults to None.
        """
        self._error_func = None
        self._error_func_kwargs = None
        self.error_func = error_func
        self.error_func_kwargs = error_func_kwargs

    def __call__(self, args, model, xdata, ydata, model_kwargs=None):
        """Evaluate the cost function.

        Parameters
        ----------
        args : array
            Arguments passed to the model
        model : func(xdata: array, args: array, **model_kwargs) -> array
            Model used to fit the data.
        x_data : array
            Independent variable data.
        y_data : array
            Dependent variable data.
        model_kwargs : dict or None, optional
            Keyword arguments passed to the ``model``.

        Returns
        -------
        float
            Evaluated error function.
        """
        if model_kwargs is None:
            model_kwargs = {}
        y_model = model(xdata, args, **model_kwargs)
        error_func = self.error_func
        error_func_kwargs = self.error_func_kwargs
        error = error_func(ydata, y_model, **error_func_kwargs)
        return error

    @property
    def error_func(self):
        """The error function."""
        return self._error_func

    @error_func.setter
    def error_func(self, _error_func):
        """error_func setter"""
        self._error_func = _error_func

    @property
    def error_func_kwargs(self):
        """Keyword arguments passed to error_func"""
        return self._error_func_kwargs

    @error_func_kwargs.setter
    def error_func_kwargs(self, _error_func_kwargs):
        """error_func_kwargs setter"""
        if _error_func_kwargs is None:
            self._error_func_kwargs = {}
        else:
            self._error_func_kwargs = _error_func_kwargs
