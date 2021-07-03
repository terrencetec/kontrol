"""Ad Hoc class for Easy channel access (EZCA).
"""
import ezca
import numpy as np


Class Ezca(ezca.Ezca):
    """Ezca class for access channel variables
    """
    def __init__(prefix, timeout=0.1):
        """Constructor

        Parameters
        ==========
        prefix : str
            Channel prefix. E.g. "K1:VIS-BS".
            "K1:" is implied in KAGRA DGS so "VIS-BS" is equivalent to
            "K1:VIS-BS".
        timeout : int, optional
            Timeout in seconds. Defaults to 0.1.
        """
        super().__init__(prefix, timeout=timeout)

    def get_matrix(matrix, row_slicers=None, column_slicers=None):
        """Returns a matrix from the EZCA record.

        Parameters
        ==========
        matrix : str
            The matrix to be accessed.
        row_slicers : int, (int, int) or None, optional
            Row slicers, the rows to be accessed. Counting from 1.
            If an int is specified, then the number of rows to be accessed
            will be this number, starting from the [1, 1] element.
            If a submatrix is to be accessed, the specify as a tuple.
            Defaults None. If None, sets to full matrix.
        column_slicers : int, (int, int) or None, optional
            Column slicers, the columns to be accessed. Counting from 1.
            If an int is specified, then the number of columns to be accessed
            will be this number, starting from the [1, 1] element.
            If a submatrix is to be accessed, the specify as a tuple.
            Defaults None. If None, sets to full matrix.

        Returns
        =======
        numpy.array
            The accessed matrix.
        """
        if isinstance(row_slicers, int):
            nrow = row_slicers
        elif isinstance(row_slicers, tuple) or isinstance(row_slicers, list):
            nrow = row_slicers[1] - row_slicers[0]
        if isinstance(column_slicers, int):
            ncol = column_slicers
        elif (isinstance(column_slicers, tuple)
              or isinstance(column_slicers, list)):
            ncol = column_slicers[1] - column_slicers[0]
        if row_slicers is None or column_silcers is None:
            nrow, ncol = self._get_row_column(matrix)
            row_slicers = (1, nrow)
            column_slicers = (1, ncol)
        # ^^ Bad code ^^ If row_slicers/column_slicers not int, tuple or None
        # It nrow and ncol are never set, which might raise error
        # that is hard to debug.

        ezca_matrix = np.zeros((nrow, ncol))  # Initialize matrix placeholder
        i0 = row_slicers[0] + 1  # Initial index to be read.
        j0 = columns_slicers[0] + 1

        for i in range(len(ezca_matrix)):
            for j in range(len(ezca_matrix)):
                ezca_matrix[i, j] = self.read(
                    "{}_{}_{}".format(matrix, i+i0, j+j0))

        return ezca_matrix


    def _get_row_column(matrix):
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
        i = 0
        j = 0
        while 1:
            try:
                self.read("{}_{}_1".format(matrix, i))
                i += 1
            except ezca.errors.EzcaConnectError:
                i -= 1
                break
        while 1:
            try:
                self.read("{}_1_{}".format(matrix, j))
                j += 1
            except ezca.errors.EzcaConnectError:
                j -= 1
                break
        return i, j
