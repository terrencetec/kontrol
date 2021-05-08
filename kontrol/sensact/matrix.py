"""Base class for matrices, sensing and actuation matices.
"""
import numpy as np


class Matrix(np.ndarray):
    """Base class for matrices
    """
    def __new__(cls, matrix=None, *args, **kwargs):
        """Constructor

        Parameters
        ----------
        matrix: array
            The matrix/array.

        Returns
        -------
        obj: Matrix(numpy.ndarray)
            The matrix/array.
        """
        # print("Matrix __new__")
        self = np.asarray(matrix).view(cls)
        return self

    def __init__(self, *args, **kwargs):
        """Constructor
        """
        # print("Matrix __init__")
        pass


class SensingMatrix(Matrix):
    """Base class for sensing matrices
    """
    def __init__(self, matrix, coupling_matrix=None, *args, **kwargs):
        r"""Constructor

        Parameters
        ----------
        matrix: array
            The sensing matrix.
        coupling_matrix: array, optional
            The coupling matrix.
            Default None.

        Notes
        -----
        The coupling matrix has (i, j) elements as coupling ratios x_i/x_j.
        For example, consider the 2-sensor configuration:
        I have a coupled sensing readout :math:`x_{1,\mathrm{coupled}}`
        that reads :math:`x_{1,\mathrm{coupled}}=x_1 + 0.1x_2`.
        and, I have another coupled sensing readout
        :math:`x_{2,\mathrm{coupled}}` that reads
        :math:`x_{2,\mathrm{coupled}}=-0.2x_1 + x_2`.
        Then, the coupling matrix is

        .. math::
            \begin{bmatrix}
            1 & 0.1\\
            -0.2 & 1
            \end{bmatrix}.
        """
        # print("SensingMatrix __init__")
        # super().__init__(matrix)
        if coupling_matrix is not None:
            self.coupling_matrix = np.array(coupling_matrix)
        else:
            self.coupling_matrix = None

    def diagonalize(self, coupling_matrix=None):
        r"""Diagonalize the sensing matrix, given a coupling matrix.

        Parameters
        ----------
        coupling_matrix: array, optional.
            The coupling matrix.
            If None, self.coupling_matrix will be used.
            Default None.

        Returns
        -------
        array:
            The new sensing matrix.

        Notes
        -----
        The coupling matrix has (i, j) elements as coupling ratios x_i/x_j.
        For example, consider the 2-sensor configuration:
        I have a coupled sensing readout :math:`x_{1,\mathrm{coupled}}`
        that reads :math:`x_{1,\mathrm{coupled}}=x_1 + 0.1x_2`.
        and, I have another coupled sensing readout
        :math:`x_{2,\mathrm{coupled}}` that reads
        :math:`x_{2,\mathrm{coupled}}=-0.2x_1 + x_2`.
        Then, the coupling matrix is

        .. math::
            \begin{bmatrix}
            1 & 0.1\\
            -0.2 & 1
            \end{bmatrix}.
        """
        if coupling_matrix is not None:
            coupling_matrix = np.array(coupling_matrix)
            return np.linalg.inv(coupling_matrix) @ self
        elif self.coupling_matrix is not None:
            return np.linalg.inv(self.coupling_matrix) @ self
        else:
            raise ValueError("Coupling matrix is not specified")
