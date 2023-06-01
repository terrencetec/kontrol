"""Tests for kontrol.dmd.forecast module."""
import numpy as np

import kontrol.dmd


def test_dmd_forecast():
    """Tests for kontrol.dmd.forecast.forecast()."""
    t_past = np.linspace(0, 10, 1024)
    t_future = t_past  # Use t_past to check if the forecast matches the past.
    time_series = np.sin(t_past)

    forecast, dmd = kontrol.dmd.dmd_forecast(
        past=time_series, t_past=t_past, t_future=t_future, return_dmd=True)
    
    assert np.allclose(time_series, forecast, atol=1e-2)
