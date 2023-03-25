"""Tests for kontrol.dmd.dmd module"""
import numpy as np

import kontrol.dmd


def test_dmd():
    """Tests for kontrol.dmd.DMD class"""
    t, dt = np.linspace(0, 10, 1024, retstep=True)
    y = np.sin(t)
    snapshot_1 = kontrol.dmd.hankel(y, 128)
    dmd = kontrol.dmd.DMD(snapshot_1=snapshot_1, truncation_value=2, dt=dt)
    dmd.run()
    y_predict = np.real(dmd.predict(t)[0])
    assert np.allclose(y_predict, y)
