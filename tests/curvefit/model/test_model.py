"""Tests for kontrol.curvefit.model.Model"""
import numpy as np
import kontrol.curvefit.model


def test_model():
    x = np.linspace(0, 1)
    model = kontrol.curvefit.model.Model()
    #
    ## Catch no model parameters error.
    try:
        y = model(x)
        raise
    except ValueError:
        pass
    model.args = [1]
    y = model(x)
    assert np.array_equal(x, y)
