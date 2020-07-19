""" Calculating actuation and sensing diagonalization matrix
"""
import numpy as np

def rediagonalization(current_matrix, coupling_matrix, type = 'sensing'):
    """Refine existing diagonalization matrix given a coupling matrix.

    Parameters
    ----------
        current_matrix: list of (list of int/float) or 2D numpy.ndarray
            The matrix to be refined.
        coupling_matrix: list of (list of int/float) or 2D numpy.ndarray
            The measured coupling. For sensing matrix, coupling_matrix[i][j] is
            the coupling ratio between the i-th component and j-th component
            of the displacement vector. Hence, the diagonal elements should be
            1. For actuation matrix, coupling matrix[i][j] is the ratio
            between the i-th component of displacement and j-th component in
            actuation. The diagonal elements should be comparable to the
            actuation efficiency of the particular DoF.
        type: string
            Specifying what kind of matrix we are diagonalizing. Either
            'sensing' or 'actuation'

    Returns
    -------
        numpy.ndarray
            The refined diagonalziation matrix.
    """
    current_matrix = np.array(current_matrix)
    coupling_matrix = np.array(coupling_matrix)
    diagonal_coupling = np.array(np.diag(np.diag(coupling_matrix)))
    if type == 'sensing':
        new_matrix = np.matmul(np.linalg.inv(coupling_matrix), current_matrix)
        return(new_matrix)
    elif type == 'actuation':
        new_matrix = np.matmul(current_matrix,
            np.matmul(np.linalg.inv(coupling_matrix), diagonal_coupling))
        return(new_matrix)
    else:
        print("Please specify type, either 'sensing' or 'actuation'.")
        return(None)
