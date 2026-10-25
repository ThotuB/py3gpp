import numpy as np

from py3gpp import nrPUCCH2


def test_nrPUCCH2_matches_matlab():
    # Reference values captured from a live MATLAB 5G Toolbox (R2026a) session.
    uciCW = [1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0]
    sym = nrPUCCH2(uciCW, 148, 160)

    assert sym.shape == (16,)
    assert np.allclose(np.abs(sym), 1.0)
    assert np.allclose(sym[:3], [-0.707107 + 0.707107j, 0.707107 - 0.707107j, -0.707107 - 0.707107j], atol=1e-6)


def test_nrPUCCH2_length_is_half_codeword():
    uciCW = np.zeros(48, dtype=int)
    sym = nrPUCCH2(uciCW, 1, 1)
    assert sym.shape == (24,)
