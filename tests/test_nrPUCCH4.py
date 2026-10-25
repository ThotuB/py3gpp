import numpy as np

from py3gpp import nrPUCCH4


def test_nrPUCCH4_sf2_matches_matlab():
    # Reference values captured from a live MATLAB 5G Toolbox (R2026a) session.
    uciCW = [
        0,
        1,
        0,
        1,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        0,
        1,
        1,
        0,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        0,
        0,
        0,
        1,
        0,
        0,
        1,
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        0,
        0,
        0,
        1,
        0,
        0,
        0,
        1,
        1,
        1,
        0,
        1,
        0,
        1,
        0,
        1,
        0,
        0,
        1,
        1,
        0,
        1,
        1,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        1,
        0,
        1,
        1,
        0,
        1,
        1,
        1,
        1,
        1,
        0,
        0,
        0,
        0,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        0,
        0,
    ]
    sym = nrPUCCH4(uciCW, "QPSK", 148, 160, 2, 1)

    assert sym.shape == (96,)
    assert np.allclose(sym[:3], [0.0 + 0.0j, 0.10939 + 0.408248j, 0.0 + 0.0j], atol=1e-6)


def test_nrPUCCH4_sf4_matches_matlab():
    uciCW = [1, 1, 0, 1, 1, 0, 0, 1, 1, 1] + [0] * 182
    sym = nrPUCCH4(uciCW, "pi/2-BPSK", 285, 897, 4, 3)

    assert sym.shape == (768,)
    assert np.allclose(sym[:3], [0.0 + 0.0j, -1.632993 - 1.632993j, 0.0 + 0.0j], atol=1e-6)


def test_nrPUCCH4_occi_out_of_range_raises():
    import pytest

    uciCW = np.zeros(48, dtype=int)
    with pytest.raises(AssertionError):
        nrPUCCH4(uciCW, "QPSK", 1, 1, 2, 2)
