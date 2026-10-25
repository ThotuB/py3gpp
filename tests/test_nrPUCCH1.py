import numpy as np

from py3gpp import nrPUCCH1


def test_nrPUCCH1_no_freq_hopping():
    # Reference values captured from a live MATLAB 5G Toolbox (R2026a) session.
    sym = nrPUCCH1([1, 1], [0], [0, 14], "normal", 3, 12, "enable", 5, "disabled", 0)

    assert sym.shape == (84,)
    assert np.allclose(np.abs(sym), 1.0)
    assert np.allclose(sym[:3], [-0.0 + 1.0j, -0.866025 + 0.5j, -0.866025 - 0.5j], atol=1e-6)


def test_nrPUCCH1_freq_hopping():
    sym = nrPUCCH1([1, 1], [0], [0, 14], "normal", 3, 12, "enable", 5, "enabled", 1)

    assert sym.shape == (84,)
    assert np.allclose(np.abs(sym), 1.0)
    assert np.allclose(sym[:3], [0.0 + 1.0j, -0.866025 + 0.5j, -0.866025 - 0.5j], atol=1e-6)


def test_nrPUCCH1_no_ack_no_sr_returns_empty():
    sym = nrPUCCH1([], [0], [0, 14], "normal", 0, 0, "neither", 0, "disabled", 0)
    assert sym.shape == (0,)
