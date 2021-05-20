# from . import frequency_series
# from .frequency_series import FrequencySeries


# from .frequency_series.frequency_series import FrequencySeries
from .frequency_series.frequency_series import FrequencySeries
from .complementary_filter.complementary_filter import ComplementaryFilter
from .transfer_function import TransferFunction
from .sensact.matrix  import Matrix, SensingMatrix
from .sensact.optical_lever import (
    OpticalLeverSensingMatrix, HorizontalOpticalLeverSensingMatrix,
    VerticalOpticalLeverSensingMatrix)
from .core import spectral
