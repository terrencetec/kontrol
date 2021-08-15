"""Model base class for curve fitting.
"""
class Model:
    """Model base class for curve fitting"""
    def __init__(self, args=None):
        """Constructor

        Parameters
        ----------
        args : array or None, optional.
            The model parameters.
            Defaults to None.
        """
        self._args = None
        self.args = args

    def __call__(self, x, args=None, **kwargs):
        """Use self._x2y(x, args, **kwargs) to give y values from x.

        This is a low level function that shouldn't be used by users.

        Parameters
        ----------
        x : array
            Independent variables
        args : array or None, optional
            Model parameters.
            Defaults to None.
            If not specified, use self.args.
        **kwargs
            Keyword arguments passed to self._x2y().

        Returns
        -------
        y : array
            f(x) = y values.
        """
        return self._x2y(x, args, **kwargs)

    def _x2y(self, x, args=None, **kwargs):
        """Convert independent variables to dependent variables.

        This should be defined independent in child classes.
        This by default returns ``x`` itself, i.e. f(x) = x.

        Parameters
        ----------
        x : array
            The independent variables.
        args : array or None, optional
            Model parameters.
            Defaults to None.
            If not specified, use self.args.
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
        self._args = _args
