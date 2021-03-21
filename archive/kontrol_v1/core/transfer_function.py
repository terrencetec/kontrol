"""Transfer function class.
Wrapper around control.TransferFunction
to provide custom functionality related to KAGRA.
"""

import control
import numpy as np


class TransferFunction(control.TransferFunction):
    """Transfer function class

    Attributes
    ----------
    foton: string
        The foton zpk expression of this transfer function object.
    expression: string, optional
        Foton zpk expression type: Hz/norm 'n', Hz 'f', or rad/s 's'.
        Defaults to 'n'.
    """
    def __init__(self, *args, expression='n'):
        """Initialize with a transfer function object

        Parameters
        ----------
        expression: string, optional
            Foton zpk expression type: Hz/norm 'n', Hz 'f', or rad/s 's'.
            Defaults to 'n'.
        *args:
            Arguments passed to control.TransferFunction class.
        """
        super().__init__(*args)
        self.expression = expression

    @property
    def foton(self):
        """Foton expression

        Parameters
        ----------
        expression: string, optional
            The foton expression type: 'n', 'f', or 's'.

        Returns
        -------
        string
            The foton zpk expression
        """
        if self.expression == 'n':
            zeros = -1*self.zero().real + 1j*self.zero().imag
            poles = -1*self.pole().real + 1j*self.pole().imag
            gain = float(self.dcgain())
            gain = gain.real
            zeros /= 2*np.pi
            poles /= 2*np.pi
        elif self.expression == 'f':
            zeros = 1*self.zero().real + 1j*self.zero().imag
            poles = 1*self.pole().real + 1j*self.pole().imag
            gain = float(self.dcgain())
            for zero in zeros:
                gain /= zero
            for pole in poles:
                gain *= pole
            gain = gain.real
            zeros /= 2*np.pi
            poles /= 2*np.pi
        elif self.expression == 's':
            zeros = self.zero()
            poles = self.pole()
            gain = float(self.dcgain())
            for zero in zeros:
                gain /= zero
            for pole in poles:
                gain *= pole
            gain = gain.real
        else:
            raise ValueError("expression: {} not valid."
                             "expression can only be 'n', 'f' or 's'."
                             "".format(self.expression))

        self._foton = 'zpk(['
        for zero in zeros:
            string = '{}'.format(
                zero.real if abs(zero.imag/zero.real) < 1e-10 else zero)
            string = string.lstrip('(')
            string = string.rstrip(')')
            self._foton += string
            self._foton += ';'
        self._foton = self._foton.rstrip(';')
        self._foton += '],['
        for pole in poles:
            string = '{}'.format(
                pole.real if abs(pole.imag/pole.real) < 1e-10 else pole)
            string = string.lstrip('(')
            string = string.rstrip(')')
            self._foton += string
            self._foton += ';'
        self._foton = self._foton.rstrip(';')
        self._foton += ('],{gain},"{expression}")'
                        ''.format(gain=gain, expression=self.expression))
        return self._foton
