import numpy as np

def quad_sum(*spectra):
    """Takes any number of same length spectrum and returns the quadrature sum
    """
    qs=np.zeros_like(spectra[0])
#     print(args[0])
    for i in spectra:
        for j in range(len(i)):
            qs[j]=np.sqrt(qs[j]**2+i[j]**2)
    return(qs)

def norm2(spectrum):
    """Takes a spectrum and returns the 2-norm of the spectrum.
    """
#     if isinstance(spectrum.np.array)
    spectrum_array = np.array(spectrum)
    norm = np.sqrt(sum(spectrum_array**2))
    return(norm)
