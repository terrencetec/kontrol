from .complementary_filter.complementary_filter import ComplementaryFilter
from .transfer_function import *
from .sensact.matrix import Matrix, SensingMatrix
from .sensact.optical_lever import (
    OpticalLeverSensingMatrix, HorizontalOpticalLeverSensingMatrix,
    VerticalOpticalLeverSensingMatrix)
from .core import spectral, foton
from . import dmd


# for ad hoc/optional packages
import importlib
ezca_spec = importlib.util.find_spec("ezca")
ezca_exist = ezca_spec is not None
if ezca_exist:
    from .ezca import Ezca
