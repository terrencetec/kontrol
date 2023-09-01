"""Utility functions for Dymanic Mode Decomposition."""
import numpy as np


def hankel(array, order):
    """Hankelize an array

    Parameters
    ----------
    array : array
        Array with rows as channels and columns as samples

    order : int
        The number of rows of the hankelized matrix.

    Returns
    -------
    hankel_array : array
        The hankelized array

    Examples
    --------
    .. code-block: python
        a = [1, 2, 3, 4, 5]
        hankel(a, 3)
        array([[1, 2, 3],
               [2, 3, 4],
               [3, 4, 5]])
    """
    hankel_array = np.zeros((order, len(array)-order+1))
    for i in range(order):
        hankel_array[i] = array[i:len(array)-order+1+i]
    return hankel_array


def auto_truncate(sigma, threshold=0.99):
    """Automatically get truncation value

    Parameters
    ----------
    sigma : array
        Singular values. Arranged from large to small values.
    threshold : float, optional
        Only include singular values so their sum is
        ``threshold`` of the original sum.
        Defaults 0.99.

    Returns
    -------
    truncation_value : int
        Amount of singular values that are required
        to reach the threshold sum.
    """
    sum_sigma = np.sum(sigma)
    for i in range(len(sigma)):
        truncation_value = i+1
        sum_truncated = np.sum(sigma[:truncation_value])
        if sum_truncated >= threshold*sum_sigma:
            break
    return truncation_value
