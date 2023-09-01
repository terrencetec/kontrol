"""Ad Hoc class for Easy channel access (EZCA).
"""
import ezca
import numpy as np


class Ezca(ezca.Ezca):
    """Ezca class for access channel variables
    """
    def __init__(self, prefix, timeout=0.1):
        """Constructor

        Parameters
        ----------
        prefix : str
            Channel prefix. E.g. "K1:VIS-BS".
            "K1:" is implied in KAGRA DGS so "VIS-BS" is equivalent to
            "K1:VIS-BS".
        timeout : int, optional
            Timeout in seconds. Defaults to 0.1.
        """
        super().__init__(prefix, timeout=timeout)

    def get_matrix(self, matrix, row_slicers=None, column_slicers=None):
        """Returns a matrix from the EPICS record using Ezca.

        Parameters
        ----------
        matrix : str
            The matrix to be accessed.
        row_slicers : int, (int, int) or None, optional
            Row slicers, the rows to be accessed. Counting from 1.
            If an int is specified, then the number of rows to be accessed
            will be this number, starting from the [1, 1] element.
            If a submatrix is to be accessed, then specify as a tuple.
            Defaults None. If None, sets to full matrix.
        column_slicers : int, (int, int) or None, optional
            Column slicers, the columns to be accessed. Counting from 1.
            If an int is specified, then the number of columns to be accessed
            will be this number, starting from the [1, 1] element.
            If a submatrix is to be accessed, then specify as a tuple.
            Defaults None. If None, sets to full matrix.

        Returns
        -------
        numpy.array
            The accessed matrix.
        """
        # Read the matrix until error to get the number of rows and columns.
        nrow, ncol = self._get_row_column(matrix)
        if isinstance(row_slicers, int):
            row_slicers = (1, row_slicers)
        elif row_slicers is None:
            row_slicers = (1, nrow)
        if isinstance(column_slicers, int):
            column_slicers = (1, column_slicers)
        elif column_slicers is None:
            column_slicers = (1, ncol)

        ezca_matrix = np.zeros((nrow, ncol))  # Initialize matrix placeholder
        for i in range(len(ezca_matrix)):
            for j in range(len(ezca_matrix)):
                ezca_matrix[i, j] = self.read(
                    "{}_{}_{}".format(matrix, i+1, j+1))

        return ezca_matrix[row_slicers[0]-1:row_slicers[1],
                           column_slicers[0]-1:column_slicers[1]]

    def put_matrix(self, numpy_array, matrix,
                   row_slicers=None, column_slicers=None):
        """Put a matrix into the EPICS record using Ezca.

        Parameters
        ----------
        numpy_array : array
            The matrix values to be put.
        matrix : str
            The matrix in EPICS record.
        row_slicers : (int, int) or None, optional
            Row slicers, the rows to be accessed. Counting from 1.
            The size determined by the tuple must match the size of
            `numpy_array`
            Defaults None. If None, sets to full matrix.
        column_slicers : (int, int) or None, optional
            Column slicers, the columns to be accessed. Counting from 1.
            The size determined by the tuple must match the size of
            `numpy_array`
            Defaults None. If None, sets to full matrix.
        """
        # Read the matrix until error to get the number of rows and columns.
        nrow, ncol = self._get_row_column(matrix)
        if row_slicers is None:
            row_slicers = (1, nrow)
        if column_slicers is None:
            column_slicers = (1, ncol)

        if row_slicers[1] - row_slicers[0] + 1 != len(numpy_array):
            raise ValueError("Slicers must match the size of numpy_array.")
        elif column_slicers[1] - column_slicers[0] + 1 != len(numpy_array[0]):
            raise ValueError("Slicers must match the size of numpy_array.")

        epics_matrix = self.get_matrix(matrix)
        epics_matrix[row_slicers[0]-1:row_slicers[1],
                     column_slicers[0]-1: column_slicers[1]] = numpy_array

        self._put_matrix(numpy_array=epics_matrix, matrix=matrix)

    def _put_matrix(self, numpy_array, matrix):
        """Put a matrix into the EPICS record using Ezca, (low level function).

        Parameters
        ----------
        numpy_array : array
            The matrix values to be put.
            Matrix size must match that in the EPICS record.
        matrix : str
            The matrix in EPICS record.
        """
        nrow, ncol = self._get_row_column(matrix)
        if len(numpy_array) != nrow or len(numpy_array[0]) != ncol:
            raise ValueError("Size of numpy_array not equal to that in the"
                             " EPICS record.")

        for i in range(len(numpy_array)):
            for j in range(len(numpy_array[i])):
                self.write("{}_{}_{}".format(matrix, i+1, j+1),
                           numpy_array[i, j])

    def _get_row_column(self, matrix):
        """Get the number of rows and columns of a matrix.

        Parameters
        ==========
        matrix : str
            The matrix to be accessed.

        Returns
        =======
        int, int
            The number of rows and columns of the matrix.
        """
        # Try increasing the number of row and columns numbers.
        i = 1
        j = 1
        while 1:
            try:
                self.read("{}_{}_1".format(matrix, i))
                i += 1
            except ezca.errors.EzcaConnectError:
                if i > 0:
                    i -= 1
                break
        while 1:
            try:
                self.read("{}_1_{}".format(matrix, j))
                j += 1
            except ezca.errors.EzcaConnectError:
                if j > 0:
                    j -= 1
                break
        return i, j
