"""Utility functions for Dymanic Mode Decomposition."""
import numpy as np


def hankel(array, order):
    """Hankelize an array
    
    Parameters
    ----------
    array : array
        Array with rows as channels and columns as samples
    
    order : int
        The number of rows added
    
    Returns
    -------
    hankel_array : array
        The hankelized array
    
    Examples
    --------
    .. code-block: python
        a = [1, 2, 3, 4, 5]
        hankel(a, 2)
        array([[1, 2, 3],
               [2, 3, 4],
               [3, 4, 5]])
    """
    hankel_array = np.zeros((order, len(array)-order+1))
    for i in range(order):
        hankel_array[i] = array[i:len(array)-order+1+i]
    return hankel_array
