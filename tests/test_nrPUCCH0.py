import numpy as np

from py3gpp import nrPUCCH0


def test_nrPUCCH0_sr_only():
    # Reference values captured from a live MATLAB 5G Toolbox (R2026a) session.
    sym = nrPUCCH0([], [1], [11, 2], "normal", 63, 512, "enable", 5, "disabled")

    assert sym.shape == (24,)
    assert np.allclose(np.abs(sym), 1.0)
    assert np.allclose(sym[:3], [0.707107 + 0.707107j, -0.707107 - 0.707107j, 0.707107 - 0.707107j], atol=1e-6)


def test_nrPUCCH0_2bit_ack():
    sym = nrPUCCH0([1, 1], [0], [10, 2], "extended", 3, 12, "enable", 5, "disabled")

    assert sym.shape == (24,)
    assert np.allclose(np.abs(sym), 1.0)
    assert np.allclose(sym[:3], [-0.707107 - 0.707107j, -0.965926 - 0.258819j, -0.965926 + 0.258819j], atol=1e-6)


def test_nrPUCCH0_freq_hopping_2symbol():
    sym = nrPUCCH0([1, 0], [], [0, 2], "normal", 5, 100, "disable", 3, "enabled")

    assert sym.shape == (24,)
    assert np.allclose(np.abs(sym), 1.0)
    assert np.allclose(sym[:3], [-0.707107 - 0.707107j, -0.707107 - 0.707107j, 0.707107 + 0.707107j], atol=1e-6)


def test_nrPUCCH0_no_ack_no_sr_returns_empty():
    sym = nrPUCCH0([], [0], [11, 2], "normal", 0, 0, "neither", 0, "disabled")
    assert sym.shape == (0,)

    sym = nrPUCCH0([], [], [11, 2], "normal", 0, 0, "neither", 0, "disabled")
    assert sym.shape == (0,)
